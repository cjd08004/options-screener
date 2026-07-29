import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="The Premium Collector", page_icon="📈", layout="wide")
st.title("📈 The Premium Collector")
st.write("Daily options income setups. Covered calls and cash secured puts, screened and ranked.")

# --- WATCHLIST ---
watchlist = {
    "Tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "AMD", "CRM", "ADBE", "INTC"],
    "Finance": ["JPM", "BAC", "GS", "MS", "WFC", "BLK", "C", "AXP", "V", "MA"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "CVS", "MDT", "BMY", "AMGN", "GILD"],
    "ETFs": ["SPY", "QQQ", "IWM", "GLD", "SLV", "XLE", "XLF", "XLV", "XLK", "TLT"]
}

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
selected_sectors = st.sidebar.multiselect(
    "Sectors",
    options=list(watchlist.keys()),
    default=list(watchlist.keys())
)
min_volume = st.sidebar.number_input("Minimum Volume", value=500, step=100)
min_iv = st.sidebar.slider("Minimum IV %", min_value=0, max_value=100, value=20)
expiry_index = st.sidebar.selectbox(
    "Expiry",
    options=[1, 2, 3],
    format_func=lambda x: f"Expiry #{x} (nearest first)"
)
strategy_filter = st.sidebar.multiselect(
    "Strategy",
    options=["Covered Call", "Cash Secured Put"],
    default=["Covered Call", "Cash Secured Put"]
)

run = st.button("Run Screener", type="primary")

# --- RISK RATING ---
def get_risk_rating(iv, volume, days_to_expiry, strike, price):
    score = 0
    if iv < 0.25:
        score += 1
    elif iv < 0.45:
        score += 2
    else:
        score += 3
    if volume > 5000:
        score += 1
    elif volume > 1000:
        score += 2
    else:
        score += 3
    distance = abs(strike - price) / price
    if distance > 0.05:
        score += 1
    elif distance > 0.02:
        score += 2
    else:
        score += 3
    if score <= 4:
        return "🟢 Low"
    elif score <= 7:
        return "🟡 Medium"
    else:
        return "🔴 High"

# --- SCREENER ---
if run:
    results = []
    filtered_watchlist = {s: watchlist[s] for s in selected_sectors}
    total = sum(len(v) for v in filtered_watchlist.values())
    progress = st.progress(0)
    status = st.empty()
    count = 0

    for sector, tickers in filtered_watchlist.items():
        for symbol in tickers:
            status.text(f"Checking {symbol}...")
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.info.get("currentPrice")
                if not price:
                    continue

                expiry = ticker.options[expiry_index]
                days_to_expiry = (datetime.strptime(expiry, "%Y-%m-%d") - datetime.today()).days + 1
                if days_to_expiry < 1:
                    days_to_expiry = 1

                chain = ticker.option_chain(expiry)

                # Covered Calls
                if "Covered Call" in strategy_filter:
                    calls = chain.calls
                    otm_calls = calls[calls["strike"] > price].copy()
                    otm_calls = otm_calls[otm_calls["strike"] <= price * 1.05]
                    otm_calls = otm_calls[otm_calls["bid"] > 0]
                    otm_calls = otm_calls[otm_calls["volume"] >= min_volume]
                    otm_calls = otm_calls[otm_calls["impliedVolatility"] >= min_iv / 100]

                    if not otm_calls.empty:
                        best = otm_calls.iloc[0]
                        iv = best.get("impliedVolatility", 0)
                        volume = int(best["volume"]) if not pd.isna(best["volume"]) else 0
                        annual_return = round((best["bid"] / price) * (365 / days_to_expiry) * 100, 1)
                        results.append({
                            "Sector": sector,
                            "Ticker": symbol,
                            "Strategy": "Covered Call",
                            "Price": round(price, 2),
                            "Strike": best["strike"],
                            "Premium": best["bid"],
                            "IV %": round(iv * 100, 1),
                            "Expiry": expiry,
                            "Annual Return %": annual_return,
                            "Volume": volume,
                            "Risk": get_risk_rating(iv, volume, days_to_expiry, best["strike"], price)
                        })

                # Cash Secured Puts
                if "Cash Secured Put" in strategy_filter:
                    puts = chain.puts
                    otm_puts = puts[puts["strike"] < price].copy()
                    otm_puts = otm_puts[otm_puts["strike"] >= price * 0.95]
                    otm_puts = otm_puts[otm_puts["bid"] > 0]
                    otm_puts = otm_puts[otm_puts["volume"] >= min_volume]
                    otm_puts = otm_puts[otm_puts["impliedVolatility"] >= min_iv / 100]

                    if not otm_puts.empty:
                        best = otm_puts.iloc[-1]
                        iv = best.get("impliedVolatility", 0)
                        volume = int(best["volume"]) if not pd.isna(best["volume"]) else 0
                        annual_return = round((best["bid"] / price) * (365 / days_to_expiry) * 100, 1)
                        results.append({
                            "Sector": sector,
                            "Ticker": symbol,
                            "Strategy": "Cash Secured Put",
                            "Price": round(price, 2),
                            "Strike": best["strike"],
                            "Premium": best["bid"],
                            "IV %": round(iv * 100, 1),
                            "Expiry": expiry,
                            "Annual Return %": annual_return,
                            "Volume": volume,
                            "Risk": get_risk_rating(iv, volume, days_to_expiry, best["strike"], price)
                        })

                time.sleep(1)

            except Exception as e:
                st.sidebar.warning(f"Skipped {symbol}: {str(e)}")

            count += 1
            progress.progress(count / total)

    status.empty()
    progress.empty()

    if results:
        df = pd.DataFrame(results).sort_values("Annual Return %", ascending=False).head(25)
        st.success(f"Found {len(df)} opportunities!")

        # Sector breakdown tabs
        tabs = st.tabs(["All"] + list(filtered_watchlist.keys()))
        with tabs[0]:
            st.dataframe(df, use_container_width=True, hide_index=True)
        for i, sector in enumerate(filtered_watchlist.keys()):
            with tabs[i + 1]:
                sector_df = df[df["Sector"] == sector]
                if sector_df.empty:
                    st.write("No results for this sector.")
                else:
                    st.dataframe(sector_df, use_container_width=True, hide_index=True)
    else:
        st.error("No results found. Try adjusting your filters.")
