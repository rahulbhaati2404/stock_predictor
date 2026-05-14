import yfinance as yf
import logging
from crewai.tools import tool
from utils.ticker_utils import format_ticker

logger = logging.getLogger("StockTools")


@tool
def get_detailed_info(ticker: str):
    try:
        ticker = format_ticker(ticker)

        logger.info(f"Fetching info for {ticker}")

        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or 'longName' not in info:
            return f"No data found for ticker {ticker}"

        name = info.get('longName', 'N/A')
        sector = info.get('sector', 'N/A')
        cap = info.get('marketCap', 'N/A')
        summary = info.get('longBusinessSummary', '')[:300]

        return (
            f"Company: {name}\n"
            f"Sector: {sector}\n"
            f"Market Cap: {cap}\n"
            f"Summary: {summary}"
        )

    except Exception as e:
        return str(e)