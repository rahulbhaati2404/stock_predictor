import logging
            cols = row.find_all('td')

            name = cols[1].text.strip().split('\n')[0]
            price = cols[2].text.strip()

            stocks.append(f"{name} (₹{price})")

        logger.info(f"✅ Extracted {len(stocks)} stocks")

        return " | ".join(stocks)

    except Exception as e:
        return f"Scrape failed: {str(e)}"


@tool
def analyze_breakout_potential(tickers_string: str):
    logger.info(f"📊 ANALYSIS: {tickers_string}")

    clean_input = str(tickers_string).replace('[', '').replace(']', '').replace("'", '').replace('"', '')

    tickers = [
        t.strip().upper().replace('.NS', '')
        for t in clean_input.split(',')
    ]

    results = []

    for ticker in tickers:
        try:
            df = stock_df(
                symbol=ticker,
                from_date=date.today()-timedelta(days=30),
                to_date=date.today(),
                series="EQ"
            )

            if not df.empty and len(df) > 1:
                df = df.sort_values('DATE', ascending=False)

                current_price = df.iloc[0]['CLOSE']
                prev_price = df.iloc[1]['CLOSE']

                pct_change = ((current_price - prev_price) / prev_price) * 100

                status = (
                    "🚀 BULLISH BREAKOUT"
                    if pct_change > 2.5
                    else "⚖️ NEUTRAL/STABLE"
                )

                results.append(
                    f"{ticker}: ₹{current_price:.2f} ({status}, Change: {pct_change:.2f}%)"
                )

            else:
                results.append(f"{ticker}: No Data")

        except Exception:
            results.append(f"{ticker}: DATA_ERROR")

    return " | ".join(results)