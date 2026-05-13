from crewai import Agent
from core.llm_setup import get_crewai_llm
from tools.market_tools import (
    analyze_breakout_potential, 
    search_web_for_stocks, 
    scrape_breakout_scanner,
    audit_stock_performance
)

# Initialize the 'Brain' once
llm_brain = get_crewai_llm()

# --- Technical Stock Analyst Agent ---
analyst = Agent(
    role='Technical Stock Analyst',
    goal='Extract and analyze breakout stocks using real-time data.',
    backstory=(
        "You are a precision-oriented NSE analyst. You follow instructions exactly. "
        "You ONLY use data returned by your tools to avoid hallucinations."
    ),
    tools=[analyze_breakout_potential, search_web_for_stocks, scrape_breakout_scanner],
    llm=llm_brain,
    verbose=True,
    allow_delegation=False
)

# --- Portfolio Risk Manager Agent ---
manager = Agent(
    role='Portfolio Risk Manager',
    goal='Audit holdings by comparing market data against risk-reward ratios.',
    backstory=(
        "You are a calculated risk manager. You provide 'Keep' or 'Sell' "
        "recommendations based strictly on volume and price action data."
    ),
    tools=[audit_stock_performance, search_web_for_stocks],
    llm=llm_brain,
    verbose=True,
    allow_delegation=False
)