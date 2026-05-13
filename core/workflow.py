import logging
import re
from typing import TypedDict
from langgraph.graph import StateGraph, END
from core.llm_setup import get_langchain_llm
from core.agents import analyst, manager
from crewai import Task, Crew
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("Workflow")

# 1. Define the state of our graph
class AgentState(TypedDict):
    input: str
    decision: str
    ticker: str
    output: str

llm = get_langchain_llm()

# --- HELPER FUNCTIONS (Task Logic) ---

def run_breakout_task(count):
    """Executes the breakout discovery task."""
    url = "https://www.screener.in/screens/209239/breakout-stocks/"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw_html = requests.get(url, headers=headers).text
    clean_text = BeautifulSoup(raw_html, 'html.parser').get_text()

    task = Task(
        description=f"Extract the TOP {count} breakout stocks from this data:\n{clean_text[:5000]}",
        expected_output="A Markdown table with Name, Price, and % Change.",
        agent=analyst
    )
    return str(Crew(agents=[analyst], tasks=[task]).kickoff())

def run_analysis_task(tickers):
    """Executes the deep analysis task."""
    task = Task(
        description=f"Perform deep sentiment and technical analysis on: {tickers}.",
        expected_output="A Markdown table with Trend and Recommendation (Strong Buy/Hold/Avoid).",
        agent=analyst
    )
    return str(Crew(agents=[analyst], tasks=[task]).kickoff())

def run_audit_task(tickers):
    """Executes the portfolio audit task."""
    task = Task(
        description=f"Review these holdings: {tickers}. Determine if they should be held or sold.",
        expected_output="A Markdown table with Sentiment and Result (Keep/Sell).",
        agent=manager
    )
    return str(Crew(agents=[manager], tasks=[task]).kickoff())

# --- GRAPH NODES ---

def router_node(state: AgentState):
    """Classifies user intent."""
    logger.info("📡 STAGE: Analyzing Intent...")
    user_msg = state["input"]
    
    prompt = (
        f"Identify intent: 'SEARCH_WEB | [Count]', 'ANALYSIS | [Tickers]', 'MANAGER | [Tickers]', or 'NONE'.\n"
        f"User: {user_msg}"
    )
    
    response = llm.invoke(prompt).strip().upper()
    
    if "SEARCH_WEB" in response:
        decision, data = "SEARCH_WEB", re.findall(r'\d+', response)[0] if re.findall(r'\d+', response) else "3"
    elif "ANALYSIS" in response:
        decision, data = "ANALYSIS", response.split("|")[-1].strip()
    elif "MANAGER" in response:
        decision, data = "MANAGER", response.split("|")[-1].strip()
    else:
        decision, data = "OFF_TOPIC", "NONE"

    return {"decision": decision, "ticker": data}

def search_web_node(state: AgentState):
    logger.info("🔍 STAGE: Searching for Breakouts...")
    count = int(state["ticker"]) if state["ticker"].isdigit() else 3
    return {"output": run_breakout_task(count)}

def analysis_node(state: AgentState):
    logger.info("📊 STAGE: Analyzing Tickers...")
    return {"output": run_analysis_task(state["ticker"])}

def portfolio_manager_node(state: AgentState):
    logger.info("🛡️ STAGE: Auditing Portfolio...")
    return {"output": run_audit_task(state["ticker"])}

def off_topic_node(state: AgentState):
    return {"output": "👋 I am your Stock Market AI. Please ask about breakouts, analysis, or audits!"}

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("search_web_node", search_web_node)
workflow.add_node("analysis_node", analysis_node)
workflow.add_node("portfolio_manager_node", portfolio_manager_node)
workflow.add_node("off_topic_node", off_topic_node)

workflow.set_entry_point("router")

workflow.add_conditional_