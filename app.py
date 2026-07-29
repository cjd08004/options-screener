import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="The Premium Collector",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f8f9fa; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* Logo area */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    .logo-icon {
        width: 36px;
        height: 36px;
        background: #e8f0fe;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .logo-text {
        font-size: 15px;
        font-weight: 600;
        color: #1a1a2e;
    }

    /* Metric cards */
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6c757d;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 600;
        color: #1a1a2e;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 12px;
        color: #6c757d;
        margin-top: 2px;
    }

    /* Strategy badges */
    .badge-call {
        background: #e8f0fe;
        color: #1a56db;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    .badge-put {
        background: #e8f8e8;
        color: #1a6b1a;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }

    /* Page header */
    .page-header {
        margin-bottom: 1.5rem;
    }
    .page-title {
        font-size: 22px;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 2px;
    }
    .page-subtitle {
        font-size: 13px;
        color: #6c757d;
    }

    /* Run button */
    .stButton > button {
        background-color: #1a56db;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        width: 100%;
        font-size: 14px;
    }
    .stButton > button:hover {
        background-color: #1446b8;
        color: white;
    }

    /* Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e9ecef;
    }

    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">📈</div>
        <div class="logo-text">The Premium Collector</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Sectors**")
    sectors = {
        "Tech": st.checkbox("Tech", value=True),
        "Finance": st.checkbox("Finance", value=True),
        "Healthcare": st.checkbox("Healthcare", value=True),
        "ETFs": st.checkbox("ETFs", value=True),
    }

    st.markdown("**Strategy**")
    show_calls = st.checkbox("Covered calls", value=True)
    show_puts = st.checkbox("Cash secured puts", value=True)

    st.markdown("**Filters**")
    min_volume = st.slider("Min volume", 0, 5000, 500, step=100)
    min_iv = st.slider("Min IV %", 0, 100, 20)
    expiry_index = st.selectbox("Expiry", options=[1, 2, 3],
        format_func=lambda x: f"Expiry #{x} (nearest first)")

    run = st.button("Run screener")

# --- WATCHLIST ---
full_watchlist = {
    "Tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "AMD", "CRM", "ADBE", "INTC"],
    "Finance": ["JPM", "BAC", "GS", "MS", "WFC", "BLK", "C", "AXP", "V", "MA"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "CVS", "MDT", "BMY", "AMGN", "GILD"],
    "ETFs": ["SPY", "QQQ", "IWM", "GLD", "SLV", "XLE", "XLF", "XLV", "XLK", "TLT"]
}

# --- RISK RATING ---
def get_risk_rating(iv, volume, days_to_expiry, strike, price):
    score = 0
    if iv < 0.30: score += 1
    elif iv < 0.60: score += 2
    else: score += 3
    if volume > 3000: score += 1
    elif volume > 800: score += 2
    else: score += 3
    distance = abs(strike - price) / price
    if distance > 0.03: score += 1
    elif distance > 0.01: score += 2
    else: score += 3
    if days_to_expiry <= 5: score -= 1
    if score <= 4: return "🟢 Low"
    elif score <= 7: return "🟡 Medium"
    else: return "🔴 High"

# --- MAIN PAGE ---
st.markdown(f"""
<div class="page-header">
    <div class="page-title">Today's opportunities</div>
    <div class="page-subtitle">{datetime.today().strftime("%A, %B %d %Y")} · 40 tickers</div>
</div>
""", unsafe_allow_html=True)

if run:
    selected = {s: full_watchlist[s] for s, checked in sectors.items() if checked}
    strategy_filter = []
    if show_calls: strategy_filter.append("Covered Call")
    if show_puts: strategy_filter.append("Cash Secured Put")

    results = []
    total = sum(len(v) for v in selected.values())
    progress = st.progress(0)
    status = st.empty()
    count = 0

    for sector, tickers in selected.items():
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
                pass

            count += 1
            progress.progress(count / total)

    progress.empty()
    status.empty()

    if results:
        df = pd.DataFrame(results).sort_values("Annual Return %", ascending=False).head(25)

        # Metric cards
        top_return = df["Annual Return %"].max()
        avg_return = round(df["Annual Return %"].mean(), 1)
        low_risk = len(df[df["Risk"] == "🟢 Low"])
        best_sector = df.groupby("Sector")["Annual Return %"].mean().idxmax()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Top return</div>
                <div class="metric-value">{top_return}%</div>
                <div class="metric-sub">{df.iloc[0]["Ticker"]} {df.iloc[0]["Strategy"].lower()}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Avg return</div>
                <div class="metric-value">{avg_return}%</div>
                <div class="metric-sub">Annualized across all picks</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Low risk picks</div>
                <div class="metric-value">{low_risk}</div>
                <div class="metric-sub">Of {len(df)} results</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Best sector</div>
                <div class="metric-value">{best_sector}</div>
                <div class="metric-sub">Highest avg return</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Sector tabs
        tabs = st.tabs(["All"] + list(selected.keys()))
        with tabs[0]:
            st.dataframe(df, use_container_width=True, hide_index=True)
        for i, sector in enumerate(selected.keys()):
            with tabs[i + 1]:
                sector_df = df[df["Sector"] == sector]
                if sector_df.empty:
                    st.write("No results for this sector.")
                else:
                    st.dataframe(sector_df, use_container_width=True, hide_index=True)
    else:
        st.error("No results found. Try adjusting your filters.")
else:
    st.info("Set your filters and click Run screener to see today's opportunities.")
