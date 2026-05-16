import os
import requests
import re
from bs4 import BeautifulSoup
from autogen import ConversableAgent
from config.logger_util import logger
from config.ai_config import llm  # Assuming this is your Ollama configurations list/dict

autogen_llm_config = {
    "config_list": [
        {
            "model": "mistral",
            "base_url": "http://localhost:11434/v1",  # Standard Ollama OpenAI-compatible port
            "api_key": "ollama",                     # Dummy string value required by AutoGen wrapper
        }
    ],
    "cache_seed": None,  # Set to None to ensure fresh processing on every single run
}

# 2. Setup the Master Brain Assistant
analyst_agent = ConversableAgent(
    name="Technical_Stock_Analyst",
    system_message=(
        "You are a strict, precision-oriented National Stock Exchange (NSE) analyst. "
        "Your only job is to process raw text data or tickers provided by the user. "
        "Extract the necessary info and format it into the exact requested Markdown table layout. "
        "Do not include conversational introductions, explanations, or filler words. "
        "End your exact response by writing the word: TERMINATE"
    ),
    llm_config=autogen_llm_config,
    human_input_mode="NEVER",
)

user_proxy = ConversableAgent(
    name="User_Proxy",
    llm_config=False,  # No LLM parsing needed for the sender pipeline proxy
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "").upper(),
    max_consecutive_auto_reply=1,  # Strict breaker limit switch for local hardware execution stability
)



def find_top_stocks(ticker_list, stock_count):
    logger.info("inside find_top_stocks helper function via AutoGen (Ultra-Cleaned)")
    url = "https://www.screener.in/screens/209239/breakout-stocks/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        raw_html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        target_table = soup.find("table", class_="data-table text-nowrap striped mark-visited no-scroll-right highlight-on-hover")
        
        if target_table:
            logger.info("✅ Targeted stock data table found successfully. Cleaning contents...")
            
            cleaned_rows = []
            # Find all content data rows inside the body element
            rows = target_table.find_all("tr")
            
            for row in rows:
                # Look for data cells inside the row
                tds = row.find_all("td")
                if not tds:
                    continue  # Skip header rows
                
                # Screener Structure columns:
                # Column index 1 usually maps to Name link text, Column index 2 maps to CMP (Current Price)
                try:
                    name = tds[1].get_text(strip=True)
                    current_price = tds[2].get_text(strip=True)
                    
                    # Store cleanly formatted information strips
                    cleaned_rows.append(f"Company: {name} | Price: Rs. {current_price}")
                except IndexError:
                    continue
            
            # Combine the precise text strings line-by-line
            table_text = "\n".join(cleaned_rows[:25]) # Fetch first 25 items as a buffer pool
        else:
            logger.warning("⚠️ Target table class not found! Falling back to raw text layout truncation.")
            table_text = soup.get_text()[:2000]
            
    except Exception as e:
        logger.error(f"❌ Error during HTML parsing operation: {str(e)}")
        return "Error: Unable to fetch live stock table data."

    # Instruct the AI with the cleaned text pool
    mission = (
        f"Analyze this clean stock list gathered from live market metrics:\n"
        f"--- REVENUE METRICS START ---\n{table_text}\n--- REVENUE METRICS END ---\n\n"
        f"CRITICAL TASK: Select exactly the top {stock_count} stocks from the list above.\n"
        f"Format your output strictly into a clear Markdown table containing the columns: Name and Current Price.\n"
        f"Return ONLY the table data with exactly {stock_count} items. Do not append conversations or explanation blocks."
    )

    logger.info("Starting AutoGen chat session using high-density clean values...")
    
    chat_result = user_proxy.initiate_chat(
        recipient=analyst_agent,
        message=mission,
        clear_history=True,
        summary_method="last_msg"
    )
    
    clean_output = chat_result.summary.replace("TERMINATE", "").strip()
    return clean_output


def analyze_specific_stocks(ticker_list):
    """Used by analysis_node for deep sentiment on user-provided stocks."""
    logger.info("inside analyze_specific_stocks helper function via AutoGen")
    
    clean_tickers = str(ticker_list).replace("[", "").replace("]", "").replace("'", "").strip()
    if ":" in clean_tickers:
        clean_tickers = clean_tickers.split(":")[-1].strip()

    logger.info(f"🚀 clean_tickers parsed: {clean_tickers}")

    mission = (
        f"Perform a deep sentiment and technical analysis on these tickers: {clean_tickers}.\n"
        f"Search for recent news and volume patterns to determine the trend.\n\n"
        f"Expected Output Format:\n"
        f"A clean Markdown Table with these exact columns:\n"
        f"| Share | Current Trend | Recommendation |\n"
        f"Note: Recommendation must be 'Strong Buy', 'Hold', or 'Avoid'.\n"
        f"Return ONLY the table data."
    )

    chat_result = user_proxy.initiate_chat(
        recipient=analyst_agent,
        message=mission,
        clear_history=True,
        summary_method="last_msg"
    )

    logger.info(f"✅ AGENT SUCCESS: Analysis for {clean_tickers} complete.")
    return chat_result.summary.replace("TERMINATE", "").strip()


def audit_my_portfolio(ticker_list):
    """Used by portfolio_manager_node to audit existing holdings."""
    logger.info("inside audit_my_portfolio helper function via AutoGen")

    clean_tickers = str(ticker_list).replace("[", "").replace("]", "").replace("'", "").strip()
    if ":" in clean_tickers:
        clean_tickers = clean_tickers.split(":")[-1].strip()

    logger.info(f"🚀 clean_tickers parsed: {clean_tickers}")

    mission = (
        f"Review the user's current holdings: {clean_tickers}.\n"
        f"Analyze the fundamental outlook and current technical trend for each stock "
        f"to determine if they should be held or sold.\n\n"
        f"Expected Output Format:\n"
        f"Output ONLY a clean Markdown Table with these exact columns:\n"
        f"| Share | Sentiment | Result |\n"
        f"Note: Result must be 'Keep' (for Positive/Neutral) or 'Sell' (for Negative).\n"
        f"Do NOT include raw code blocks, JSON structures, or framing chat filler."
    )

    chat_result = user_proxy.initiate_chat(
        recipient=analyst_agent,
        message=mission,
        clear_history=True,
        summary_method="last_msg"
    )

    logger.info(f"✅ AGENT SUCCESS: Portfolio audit for {clean_tickers} complete.")
    return chat_result.summary.replace("TERMINATE", "").strip()