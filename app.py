import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 Options Income Screener")
st.write("Find the best covered call and cash secured put opportunities across your watchlist.")

# --- USER INPUTS ---
tickers_input = st.text_input("Enter tickers separated by commas", "AAPL, MSFT, GOOGL, AMZN, META")
min_volume = st.number_input("Minimum volume", value=500, step=100)
expiry_index = st.selectbox("Expiry", options=[1, 2, 3], format_func=lambda x: f"Expiry #{x} (nearest first)")

run = st.button("Run Screener")

if run:
    watchlist = [t.strip() for t in tickers_input.split(",")]
    results = []

    with st.spinner("Pulling live options data..."):
        for symbol in watchlist:
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.info["currentPrice"]
                expiry = ticker.options[expiry_index]

                # days to expiry
                from datetime import datetime
                days_to_expiry = (datetime.strptime(expiry, "%Y-%m-%d") - datetime.today()).days + 1
                if days_to_expiry < 1:
                    days_to_expiry = 1

                chain = ticker.option_chain(expiry)

                # Covered calls
                calls = chain.calls
                otm_calls = calls[calls["strike"] > price].copy()
                otm_calls = otm_calls[otm_calls["bid"] > 0]
                otm_calls = otm_calls[otm_calls["volume"] >= min_volume]

                if not otm_calls.empty:
                    best = otm_calls.iloc[0]
                    results.append({
                        "Ticker": symbol,
                        "Strategy": "Covered Call",
                        "Price": round(price, 2),
                        "Strike": best["strike"],
                        "Premium": best["bid"],
                        "Expiry": expiry,
                        "Annual Return %": round((best["bid"] / price) * (365 / days_to_expiry) * 100, 1),
                        "Volume": int(best["volume"]) if not pd.isna(best["volume"]) else 0
                    })

                # Cash secured puts
                puts = chain.puts
                otm_puts = puts[puts["strike"] < price].copy()
                otm_puts = otm_puts[otm_puts["bid"] > 0]
                otm_puts = otm_puts[otm_puts["volume"] >= min_volume]

                if not otm_puts.empty:
                    best = otm_puts.iloc[-1]
                    results.append({
                        "Ticker": symbol,
                        "Strategy": "Cash Secured Put",
                        "Price": round(price, 2),
                        "Strike": best["strike"],
                        "Premium": best["bid"],
                        "Expiry": expiry,
                        "Annual Return %": round((best["bid"] / price) * (365 / days_to_expiry) * 100, 1),
                        "Volume": int(best["volume"]) if not pd.isna(best["volume"]) else 0
                    })

            except Exception as e:
                st.warning(f"Skipped {symbol}: {str(e)}")

    if results:
        df = pd.DataFrame(results).sort_values("Annual Return %", ascending=False)
        st.success(f"Found {len(df)} opportunities!")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("No results found. Try lowering the minimum volume or changing tickers.")
