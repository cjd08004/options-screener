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

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2a2d3a;
    }
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label { color: #e8eaf0; }
    [data-testid="stCheckbox"] label { color: #e8eaf0 !important; }
    [data-testid="stSelectbox"] label { color: #e8eaf0 !important; }
    [data-testid="stSlider"] label { color: #e8eaf0 !important; }
    .stSelectbox div { background-color: #1a1d27 !important; color: #e8eaf0 !important; }
    .logo-container {
        display: flex; align-items: center; gap: 10px;
        padding: 0 0 1.5rem 0; border-bottom: 1px solid #2a2d3a; margin-bottom: 1.5rem;
    }
    .logo-icon {
        width: 36px; height: 36px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;
    }
    .logo-text { font-size: 15px; font-weight: 700; color: #ffffff; letter-spacing: 0.02em; }
    .metric-card {
        background: #1a1d27; border-radius: 12px; padding: 18px 20px;
        border: 1px solid #2a2d3a; position: relative; overflow: hidden;
    }
    .metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
    .metric-card.green::before { background: linear-gradient(90deg, #00d2aa, #00a86b); }
    .metric-card.blue::before { background: linear-gradient(90deg, #667eea, #764ba2); }
    .metric-card.amber::before { background: linear-gradient(90deg, #f7971e, #ffd200); }
    .metric-card.coral::before { background: linear-gradient(90deg, #f953c6, #b91d73); }
    .metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #6c7293; margin-bottom: 6px; }
    .metric-value { font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.1; }
    .metric-sub { font-size: 12px; color: #6c7293; margin-top: 4px; }
    .page-title { font-size: 24px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
    .page-subtitle { font-size: 13px; color: #6c7293; }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 8px;
        padding: 12px 24px; font-weight: 600; width: 100%; font-size: 14px; letter-spacing: 0.02em;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); color: white;
    }
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #2a2d3a !important; }
    [data-testid="stDataFrame"] th { background-color: #1a1d27 !important; color: #6c7293 !important; }
    [data-testid="stDataFrame"] td { background-color: #0f1117 !important; color: #e8eaf0 !important; border-color: #2a2d3a !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1d27; border-radius: 8px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #6c7293; border-radius: 6px; font-size: 13px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; }
    [data-testid="stInfoMessage"] { background-color: #1a1d27; border: 1px solid #2a2d3a; color: #e8eaf0; border-radius: 10px; }
    .stSidebar .stMarkdown strong { color: #ffffff !important; }
    .stCaption { color: #6c7293 !important; }
    .stProgress > div > div { background: linear-gradient(90deg, #667eea, #764ba2); }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] p {
        color: #ffffff !important;
        background-color: #1a1d27 !important;
    }
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
    expiry_index = st.selectbox(
        "Expiry",
        options=[1, 2, 3],
        format_func=lambda x: {
            1: "This week — highest premium, short time",
            2: "Next week — balanced risk and return",
            3: "Two weeks out — safer, more breathing room"
        }[x]
    )
    st.caption("This week = highest annualized return but less time. Further out = safer with more breathing room.")

    run = st.button("Run screener")

# --- WATCHLIST ---
full_watchlist = {
    "Tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "AMD", "CRM", "ADBE", "INTC"],
    "Finance": ["JPM", "BAC", "GS", "MS", "WFC", "BLK", "C", "AXP", "V", "MA"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "CVS", "MDT", "BMY", "AMGN", "GILD"],
    "ETFs": ["SPY", "QQQ", "IWM", "GLD", "SLV", "XLE", "XLF", "XLV", "XLK", "TLT"]
}

# --- CACHED DATA FETCH (15 min TTL — cuts Yahoo requests massively) ---
@st.cache_data(ttl=900, show_spinner=False)
def fetch_ticker_data(symbol, expiry_idx):
    ticker = yf.Ticker(symbol)
    price = ticker.info.get("currentPrice")
    if not price:
        return None
    expirations = ticker.options
    if len(expirations) <= expiry_idx:
        return None
    expiry = expirations[expiry_idx]
    chain = ticker.option_chain(expiry)
    return {
        "price": price,
        "expiry": expiry,
        "calls": chain.calls,
        "puts": chain.puts
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

# --- BUILD ONE RESULT ROW (shared by calls and puts, no duplicated logic) ---
def build_row(best, sector, symbol, strategy, price, expiry, days_to_expiry):
    iv = best.get("impliedVolatility", 0) or 0
    volume = int(best["volume"]) if not pd.isna(best["volume"]) else 0
    premium = best["bid"]
    strike = best["strike"]

    if strategy == "Covered Call":
        capital = price                      # you own 100 shares at current price
        breakeven = round(price - premium, 2)
        protection = round((premium / price) * 100, 2)
    else:
        capital = strike                     # cash secured at the strike
        breakeven = round(strike - premium, 2)
        protection = round(((price - breakeven) / price) * 100, 2)

    period_return = round((premium / capital) * 100, 2)
    annualized = round(period_return * (365 / days_to_expiry), 1)

    return {
        "Sector": sector,
        "Ticker": symbol,
        "Strategy": strategy,
        "Price": round(price, 2),
        "Strike": strike,
        "Premium": premium,
        "IV %": round(iv * 100, 1),
        "Expiry": expiry,
        "Days": days_to_expiry,
        "Period %": period_return,
        "Annualized %": annualized,
        "Breakeven": breakeven,
        "Protection %": protection,
        "Volume": volume,
        "Risk": get_risk_rating(iv, volume, days_to_expiry, strike, price)
    }

# --- MAIN PAGE ---
st.markdown(f"""
<div style="margin-bottom: 1.5rem;">
    <div class="page-title">Today's opportunities</div>
    <div class="page-subtitle">{datetime.today().strftime("%A, %B %d %Y")} · 40 tickers scanned</div>
</div>
""", unsafe_allow_html=True)

if run:
    selected = {s: full_watchlist[s] for s, checked in sectors.items() if checked}
    strategy_filter = []
    if show_calls: strategy_filter.append("Covered Call")
    if show_puts: strategy_filter.append("Cash Secured Put")

    results = []
    skipped = []
    total = sum(len(v) for v in selected.values())
    progress = st.progress(0)
    status = st.empty()
    count = 0

    for sector, tickers in selected.items():
        for symbol in tickers:
            status.text(f"Checking {symbol}...")
            try:
                data = fetch_ticker_data(symbol, expiry_index)
                if data is None:
                    skipped.append(symbol)
                    count += 1
                    progress.progress(count / total)
                    continue

                price = data["price"]
                expiry = data["expiry"]
                days_to_expiry = max((datetime.strptime(expiry, "%Y-%m-%d") - datetime.today()).days + 1, 1)

                if "Covered Call" in strategy_filter:
                    calls = data["calls"].copy()
                    calls["volume"] = calls["volume"].fillna(0)
                    calls["impliedVolatility"] = calls["impliedVolatility"].fillna(0)
                    otm = calls[(calls["strike"] > price) &
                                (calls["strike"] <= price * 1.05) &
                                (calls["bid"] > 0) &
                                (calls["volume"] >= min_volume) &
                                (calls["impliedVolatility"] >= min_iv / 100)]
                    if not otm.empty:
                        results.append(build_row(otm.iloc[0], sector, symbol, "Covered Call", price, expiry, days_to_expiry))

                if "Cash Secured Put" in strategy_filter:
                    puts = data["puts"].copy()
                    puts["volume"] = puts["volume"].fillna(0)
                    puts["impliedVolatility"] = puts["impliedVolatility"].fillna(0)
                    otm = puts[(puts["strike"] < price) &
                               (puts["strike"] >= price * 0.95) &
                               (puts["bid"] > 0) &
                               (puts["volume"] >= min_volume) &
                               (puts["impliedVolatility"] >= min_iv / 100)]
                    if not otm.empty:
                        results.append(build_row(otm.iloc[-1], sector, symbol, "Cash Secured Put", price, expiry, days_to_expiry))

                time.sleep(0.5)

            except Exception:
                skipped.append(symbol)

            count += 1
            progress.progress(count / total)

    progress.empty()
    status.empty()

    if skipped:
        st.caption(f"Skipped (no data or rate limited): {', '.join(skipped)}")

    if results:
        df = pd.DataFrame(results).sort_values("Period %", ascending=False).head(25)

        top = df.iloc[0]
        avg_period = round(df["Period %"].mean(), 2)
        low_risk = len(df[df["Risk"] == "🟢 Low"])
        best_sector = df.groupby("Sector")["Period %"].mean().idxmax()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card green">
                <div class="metric-label">Top pick</div>
                <div class="metric-value">{top["Period %"]}%</div>
                <div class="metric-sub">{top["Ticker"]} · {top["Days"]} days · {top["Annualized %"]}% annualized</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="metric-card blue">
                <div class="metric-label">Avg period return</div>
                <div class="metric-value">{avg_period}%</div>
                <div class="metric-sub">Premium ÷ capital at risk</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card amber">
                <div class="metric-label">Low risk picks</div>
                <div class="metric-value">{low_risk}</div>
                <div class="metric-sub">Of {len(df)} results</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="metric-card coral">
                <div class="metric-label">Best sector</div>
                <div class="metric-value">{best_sector}</div>
                <div class="metric-sub">Highest avg period return</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

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

        # CSV download
        csv = df.to_csv(index=False).encode("utf-8")
        col_dl, col_share = st.columns([1, 2])
        with col_dl:
            st.download_button("Download CSV", csv,
                file_name=f"premium_collector_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv")

        # Share bar
        share_url = "https://options-screener-nz8kgd62xpbgfsflhwnnrs.streamlit.app/"
        st.markdown(f"""
        <div style="background:#1a1d27;border-radius:12px;padding:16px 20px;border:1px solid #2a2d3a;display:flex;align-items:center;justify-content:space-between;margin-top:1rem;">
            <div>
                <div style="font-weight:600;color:#ffffff;font-size:14px;">Share today's opportunities</div>
                <div style="color:#6c7293;font-size:12px;margin-top:2px;">{share_url}</div>
            </div>
            <a href="https://twitter.com/intent/tweet?text=Today%27s+top+options+income+opportunities+%F0%9F%93%88+The+Premium+Collector&url={share_url}"
               target="_blank"
               style="background:#1da1f2;color:white;padding:8px 18px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;">
                Share on X
            </a>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("No results found. Try adjusting your filters.")

else:
    st.markdown("""
    <div style="background:#1a1d27;border-radius:12px;padding:24px;border:1px solid #2a2d3a;text-align:center;margin-top:2rem;">
        <div style="font-size:32px;margin-bottom:12px;">📈</div>
        <div style="font-size:16px;font-weight:600;color:#ffffff;margin-bottom:6px;">Ready to scan the market</div>
        <div style="font-size:13px;color:#6c7293;">Set your filters and click Run screener to see today's best options income opportunities.</div>
    </div>
    """, unsafe_allow_html=True)

# Disclaimer — always visible
st.markdown("""
<div style="text-align:center;color:#6c7293;font-size:11px;margin-top:2rem;padding-top:1rem;border-top:1px solid #2a2d3a;">
    The Premium Collector is for informational purposes only. Not financial advice.
    Options trading involves significant risk of loss. Data may be delayed. Trade responsibly.
</div>
""", unsafe_allow_html=True)
