import logging
import requests
import pandas as pd
from datetime import date, timedelta
from bs4 import BeautifulSoup
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from jugaad_data.nse import stock_df

# Professional Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="\033[94m%(asctime)s\033[0m [\033[92m%(levelname)s\033[0m] 🛠️ %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MarketTools")

@tool
def scrape_breakout_scanner(stock_count: int):
    """Extracts the top N breakout stocks from Screener.in breakout scan."""
    logger.info(f"🔍 SCRAPER: Hunting for Top {stock_count} Breakouts...")
    url = "https://www.screener.in/screens/209239/breakout-stocks/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {'class': 'data-table'})

        if not table: 
            return "Could not find breakout table on page."

        stocks = []
        rows = table.find_all('tr')[1:] 
        for row in rows[:int(stock_count)]:
            cols = row.find_all('td')
            name = cols[1].text.strip().split('\n')[0]
            price = cols[2].text.strip()
            stocks.append(f"{name} (₹{price})")

        return " | ".join(stocks)
    except Exception as e:
        return f"Scrape failed: {str(e)}"

@tool
def analyze_breakout_potential(tickers_string: str):
    """Analyzes NSE stocks for breakouts based on 30-day volatility."""
    logger.info(f"📊 ANALYSIS: Checking NSE Data for: {tickers_string}")
    clean_input = str(tickers_string).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
    tickers = [t.strip().upper().replace('.NS', '') for t in clean_input.split(',')]

    results = []
    for ticker in tickers:
        try:
            df = stock_df(symbol=ticker, from_date=date.today()-timedelta(days=30), to_date=date.today(), series="EQ")
            if not df.empty and len(df) > 1:
                df = df.sort_values('DATE', ascending=False)
                current_price = df.iloc[0]['CLOSE']
                prev_price = df.iloc[1]['CLOSE']
                pct_change = ((current_price - prev_price) / prev_price) * 100
                status = "🚀 BULLISH BREAKOUT" if pct_change > 2.5 else "⚖️ NEUTRAL/STABLE"
                results.append(f"{ticker}: ₹{current_price:.2f} ({status}, Change: {pct_change:.2f}%)")
            else:
                results.append(f"{ticker}: Symbol not found on NSE or No Data")
        except Exception as e:
            results.append(f"{ticker}: DATA_ERROR")
    return " | ".join(results)

@tool
def search_web_for_stocks(query: str):
    """Searches web for stock news, quarterly results, and market sentiment."""
    logger.info(f"🌐 WEB SEARCH: {query}")
    try:
        search = DuckDuckGoSearchRun()
        return search.run(f"NSE India stock news: {query}")
    except Exception as e:
        return f"Search currently unavailable: {str(e)}"

@tool
def audit_stock_performance(ticker: str):
    """Evaluates current volume vs 30-day average for portfolio risk assessment."""
    logger.info(f"🛡️ AUDIT: Analyzing Risk for {ticker}")
    ticker = ticker.strip().upper().replace('.NS', '')
    try:
        df = stock_df(symbol=ticker, from_date=date.today()-timedelta(days=45), to_date=date.today(), series="EQ")
        if df.empty: return f"{ticker}: No data available for audit."

        df = df.sort_values('DATE', ascending=False)
        current_vol = df.iloc[0]['VOLUME']
        avg_vol = df['VOLUME'].mean()
        price_change = df.iloc[0]['CLOSE'] - df.iloc[1]['CLOSE']

        if current_vol > (avg_vol * 1.5) and price_change < 0:
            risk = "⚠️ HIGH RISK (Heavy Selling)"
        elif current_vol > (avg_vol * 1.5) and price_change > 0:
            risk = "✅ STRONG ACCUMULATION"
        else:
            risk = "⚖️ STABLE"

        return f"{ticker}: Volume is {((current_vol/avg_vol)*100):.1f}% of 30-day avg. Status: {risk}"
    except Exception as e:
        return f"Audit Error for {ticker}: {str(e)}"