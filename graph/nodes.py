import logging
import re
from crewai import Crew, Task
from agents.analyst_agent import analyst
from agents.manager_agent import manager

logger = logging.getLogger("Nodes")


def search_web_node(state):
    logger.info("🌐 Search web node")

    ticker_data = state.get("ticker", "COUNT_3")

    match = re.search(r'\d+', ticker_data)
    count = int(match.group()) if match else 3

    task = Task(
        description=f"Find top {count} breakout stocks",
        expected_output="Markdown table",
        agent=analyst
    )

    crew = Crew(
        agents=[analyst],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()

    return {"output": str(result)}



def analysis_node(state):
    logger.info("📊 Analysis node")

    tickers = state.get("ticker", "NONE")

    task = Task(
        description=f"Analyze these stocks: {tickers}",
        expected_output="Markdown Table",
        agent=analyst
    )

    crew = Crew(
        agents=[analyst],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()

    return {"output": str(result)}



def portfolio_manager_node(state):
    logger.info("💼 Portfolio node")

    tickers = state.get("ticker", "NONE")

    task = Task(
        description=f"Audit holdings: {tickers}",
        expected_output="Markdown Table",
        agent=manager
    )

    crew = Crew(
    }