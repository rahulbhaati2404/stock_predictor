from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import logging

logger = logging.getLogger("WebTools")


@tool
def search_web_for_stocks(query: str):
    """Searches web for stock news and market sentiment."""

    logger.info(f"🌐 WEB SEARCH: {query}")

    try:
        search = DuckDuckGoSearchRun()
        return search.run(f"NSE India stock news: {query}")

    except Exception as e:
        return f"Search currently unavailable: {str(e)}"