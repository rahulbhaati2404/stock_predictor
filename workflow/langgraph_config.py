import re
import langchain
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from yfinance import tickers
from config.logger_util import logger
from config.ai_config import llm
from service.helper import find_top_stocks, analyze_specific_stocks, audit_my_portfolio

langchain.debug = True


class AgentState(TypedDict):
    input: str
    decision: str
    ticker: str
    output: str

def router_node(state: AgentState):
    logger.info("--- LANGGRAPH STAGE: ANALYZING USER INTENT ---")
    user_msg = state["input"]

    classification_prompt = (
        f"You are a strict text classification tool. Analyze the user message and output exactly the classification format required.\n\n"
        f"User Message: '{user_msg}'\n\n"
        
        "Allowed Outputs:\n"
        "- SEARCH_WEB | [Number] (Use if searching for top stocks/breakouts. Default number to 3 if missing.)\n"
        "- ANALYSIS | [Tickers] (Use if asking to analyze specific stock names.)\n"
        "- MANAGER | [Tickers] (Use if asking about portfolio or owned stocks.)\n"
        "- INVALID_DATA (Use ONLY if completely off-topic like weather or jokes.)\n\n"
        
        "Examples:\n"
        "- 'Find 5 breakout stocks' -> SEARCH_WEB | 5\n"
        "- 'Top 10 stocks' -> SEARCH_WEB | 10\n"
        "- 'Analyze TCS' -> ANALYSIS | TCS\n\n"
        
        "Rule: Reply with ONLY the category string. Do not write explanations or intro text."
    )

    try:
            logger.info(f"Calling LLM From Router Node")
            response = llm.invoke(classification_prompt).strip()
            logger.info(f"DEBUG: LLM Router Response: {response}")

            upper_res = response.upper()

            if "SEARCH_WEB" in upper_res:
                decision = "SEARCH_WEB"
                # Extract the first number found in the response
                nums = re.findall(r'\d+', response)
                # Prioritize the extracted number, otherwise default to 3
                count = nums[0] if nums else "3"
                final_data = f"COUNT_{count}"

            elif "ANALYSIS" in upper_res:
                decision = "ANALYSIS"
                # Split by pipe and take the last part; fallback to 'NONE' if extraction fails
                final_data = response.split("|")[-1].strip() if "|" in response else "NONE"

            elif "MANAGER" in upper_res:
                decision = "MANAGER"
                final_data = response.split("|")[-1].strip() if "|" in response else "NONE"

            else:
                # Safe fallback prevents KeyError in LangGraph conditional edges
                logger.warning("Router could not classify intent.")
                decision = "INVALID_DATA"
                final_data = "NA"

            return {
                "decision": decision,
                "ticker": final_data
            }

    except Exception as e:
        logger.info(f"Router Exception: {str(e)}")
        return {"decision": "INVALID_DATA", "ticker": "NA"}

def search_web_node(state: AgentState):
    logger.info("Calling LLM From Search Web Node")
    ticker_data = state.get("ticker")
    
    if not ticker_data:
        logger.error("❌ Crucial Error: 'ticker' was not found in the incoming AgentState!")
        return {"output": "Error: Ticker missing from request."}
        
    logger.info(f"✅ Successfully retrieved ticker: {ticker_data}")

    try:
        # Search for any digits in the string
        match = re.search(r'\d+', ticker_data)
        if match:
            count = int(match.group())
        else:
            count = 2
    except Exception as e:
        logger.warning(f"⚠️ Extraction failed for '{ticker_data}': {e}. Defaulting to 2.")
        count = 2

    logger.info(f"Workflow Calling find_top_stocks")
    result = find_top_stocks("SEARCH_WEB", count)
    logger.info(f"Workflow Calling find_top_stocks: Result: {result}")

    return {"output": result}

def analysis_node(state: AgentState):
    logger.info("Calling LLM From analysis_node")
    ticker_data = state.get("ticker")
    
    if not ticker_data:
        logger.error("❌ Crucial Error: 'ticker' was not found in the incoming AgentState!")
        return {"output": "Error: Ticker missing from request."}
        
    logger.info(f"✅ Successfully retrieved ticker: {ticker_data}")

    if ticker_data == "NONE" or not ticker_data or len(ticker_data.strip()) < 2:
        result = "⚠️ No specific stocks identified. Please provide ticker symbols (e.g., 'Analyze SBIN, TCS')."
    else:
        clean_tickers = ticker_data.replace("[", "").replace("]", "").replace("'", "").strip()
        logger.info(f"✅ Successfully clean_tickers: {clean_tickers}")
        result = analyze_specific_stocks(clean_tickers)

    return {"output": result}

def portfolio_manager_node(state: AgentState):
    logger.info("Calling LLM From portfolio_manager_node")
    ticker_data = state.get("ticker")
    
    if not ticker_data:
        logger.error("❌ Crucial Error: 'ticker' was not found in the incoming AgentState!")
        return {"output": "Error: Ticker missing from request."}
        
    logger.info(f"✅ Successfully retrieved ticker: {ticker_data}")

    # 2. Validation & Cleanup
    if ticker_data == "NONE" or not ticker_data or len(ticker_data.strip()) < 2:
        result = "⚠️ Please provide the stocks in your portfolio to begin the audit (e.g., 'Audit my SBIN and RELIANCE')."
    else:
        clean_tickers = ticker_data.replace("[", "").replace("]", "").replace("'", "").strip()
        result = audit_my_portfolio(clean_tickers)

    return {"output": result}

def off_topic_node(state: AgentState):
    """
    Handles non-financial queries gracefully.
    Triggered when the Router returns 'OFF_TOPIC'.
    """
    logger.info("🛑 NODE: Handling Off-Topic Query")

    response = (
        "👋 **I am your specialized Indian Stock Market AI.**\n\n"
        "Currently, I can only assist with:\n"
        "* **Finding Breakout Stocks** (e.g., 'Find 5 breakout stocks')\n"
        "* **Technical Analysis** (e.g., 'Analyze RELIANCE')\n"
        "* **Portfolio Audits** (e.g., 'Audit my holdings: SBIN, TCS')\n\n"
        "Please ask a question related to the NSE or your portfolio!"
    )

    return {"output": response}


workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("search_web_node", search_web_node)
workflow.add_node("analysis_node", analysis_node)
workflow.add_node("portfolio_manager_node", portfolio_manager_node)
workflow.add_node("off_topic_node", off_topic_node)

workflow.set_entry_point("router")


workflow.add_conditional_edges(
    "router",
    lambda x: x["decision"],
    {
        "SEARCH_WEB": "search_web_node",
        "ANALYSIS": "analysis_node",
        "MANAGER": "portfolio_manager_node",
        "INVALID_DATA": "off_topic_node" 
    }
)

for node in ["search_web_node", "analysis_node", "portfolio_manager_node", "off_topic_node"]:
    workflow.add_edge(node, END)

stocks_app = workflow.compile()
logger.info("✅ LangGraph Blueprint compiled and ready.")