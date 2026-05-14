def format_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()

    if "." not in ticker:
        return f"{ticker}.NS"

    return ticker