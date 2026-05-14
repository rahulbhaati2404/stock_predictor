from crewai import Agent
from services.ollama_service import get_llm_with_reconnect
from tools.market_tools import (
    analyze_breakout_potential,
    scrape_breakout_scanner
)
from tools.web_tools import search_web_for_stocks

llm_brain = get_llm_with_reconnect()

analyst = Agent(
    role='Technical Stock Analyst',
    goal='Analyze stocks using provided tools.',
    backstory='Precision oriented NSE analyst.',
    tools=[
        analyze_breakout_potential,
        search_web_for_stocks,
        scrape_breakout_scanner
    ],
    llm=llm_brain,
    verbose=True,
    allow_delegation=False,
    memory=False
)