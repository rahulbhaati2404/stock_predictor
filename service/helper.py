
from crewai import Task,Crew
import requests
from bs4 import BeautifulSoup
from config.logger_util import logger
from config.ai_config import llm
from crew_agent.agents import analyst, manager

def find_top_stocks(ticker_list, stock_count):
    logger.info("inside find_top_stocks helper function")
    url = "https://www.screener.in/screens/209239/breakout-stocks/"
    headers = {"User-Agent": "Mozilla/5.0"}
    raw_html = requests.get(url, headers=headers).text
    clean_text = BeautifulSoup(raw_html, 'html.parser').get_text()

    mission = (
        f"I am providing you with the raw text from a stock screening website.\n"
        f"--- RAW DATA START ---\n{clean_text[:5000]}\n--- RAW DATA END ---\n\n"
        f"CRITICAL TASK: From the data above, find and extract the TOP {stock_count} breakout stocks.\n"
        f"For each stock, extract: Name, Current Price, and % Change.\n"
        f"Return ONLY a Markdown table with EXACTLY {stock_count} rows."
    )

    task1 = Task(
        description=mission,
        expected_output="A perfectly formatted Markdown table.",
        agent=analyst
    )

    crew = Crew(agents=[analyst], tasks=[task1], verbose=False)
    logger.info("inside find_top_stocks Crew kickoff")
    return str(crew.kickoff())


def analyze_specific_stocks(ticker_list):
    """Used by analysis_node for deep sentiment on user-provided stocks."""
    logger.info("inside analyze_specific_stocks helper function")
    logger.info(f"inside analyze_specific_stocks helper function: {ticker_list}")
    
    clean_tickers = str(ticker_list).replace("[", "").replace("]", "").replace("'", "").strip()
    if ":" in clean_tickers:
        clean_tickers = clean_tickers.split(":")[-1].strip()

    logger.info(f"🚀 clean_tickers: {clean_tickers}")

    task_analysis = Task(
        description=(
            f"Perform a deep sentiment and technical analysis on these tickers: {clean_tickers}.\n"
            "Search for recent news and volume patterns to determine the trend."
        ),
        expected_output=(
            "A clean Markdown Table with these exact columns:\n"
            "| Share | Current Trend | Recommendation |\n"
            "Note: Recommendation must be 'Strong Buy', 'Hold', or 'Avoid'.\n"
            "Return ONLY the table, no introductory text."
        ),
        agent=analyst
    )
    
    crew = Crew(agents=[analyst], tasks=[task_analysis], verbose=False)
    logger.info("inside analyze_specific_stocks Crew kickoff")
    result = crew.kickoff()

    logger.info(f"✅ AGENT SUCCESS: Analysis for {clean_tickers} complete.")
    return str(result)

def audit_my_portfolio(ticker_list):
    """Used by portfolio_manager_node to audit existing holdings."""

    logger.info("inside audit_my_portfolio helper function")
    logger.info(f"inside audit_my_portfolio helper function: {ticker_list}")

    clean_tickers = str(ticker_list).replace("[", "").replace("]", "").replace("'", "").strip()
    if ":" in clean_tickers:
        clean_tickers = clean_tickers.split(":")[-1].strip()

    logger.info(f"🚀 clean_tickers: {clean_tickers}")

    task_audit = Task(
        description=(
            f"Review the user's current holdings: {clean_tickers}.\n"
            "Analyze the fundamental outlook and current technical trend for each stock "
            "to determine if they should be held or sold."
        ),
        expected_output=(
            "Output ONLY a clean Markdown Table with these exact columns:\n"
            "| Share | Sentiment | Result |\n"
            "Note: Result must be 'Keep' (for Positive/Neutral) or 'Sell' (for Negative).\n"
            "Do NOT include raw code, JSON, or any conversational text before or after the table."
        ),
        agent=manager
    )

    logger.info("inside audit_my_portfolio Crew kickoff")
    crew = Crew(agents=[manager], tasks=[task_audit], verbose=False)
    result = crew.kickoff()

    logger.info(f"✅ AGENT SUCCESS: Portfolio audit for {clean_tickers} complete.")
    return str(result)