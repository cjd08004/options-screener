st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2a2d3a;
    }

    /* All text */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label {
        color: #e8eaf0;
    }

    /* Checkboxes and labels */
    [data-testid="stCheckbox"] label { color: #e8eaf0 !important; }
    [data-testid="stSelectbox"] label { color: #e8eaf0 !important; }
    [data-testid="stSlider"] label { color: #e8eaf0 !important; }
    .stSelectbox div { background-color: #1a1d27 !important; color: #e8eaf0 !important; }
    
    /* Logo */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid #2a2d3a;
        margin-bottom: 1.5rem;
    }
    .logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .logo-text {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.02em;
    }

    /* Metric cards */
    .metric-card {
        background: #1a1d27;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #2a2d3a;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .metric-card.green::before { background: linear-gradient(90deg, #00d2aa, #00a86b); }
    .metric-card.blue::before { background: linear-gradient(90deg, #667eea, #764ba2); }
    .metric-card.amber::before { background: linear-gradient(90deg, #f7971e, #ffd200); }
    .metric-card.coral::before { background: linear-gradient(90deg, #f953c6, #b91d73); }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6c7293;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #6c7293;
        margin-top: 4px;
    }

    /* Page header */
    .page-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }
    .page-subtitle {
        font-size: 13px;
        color: #6c7293;
    }

    /* Run button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        font-size: 14px;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        color: white;
    }

    /* Table */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2a2d3a !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: #1a1d27 !important;
        color: #6c7293 !important;
    }
    [data-testid="stDataFrame"] td {
        background-color: #0f1117 !important;
        color: #e8eaf0 !important;
        border-color: #2a2d3a !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1d27;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #6c7293;
        border-radius: 6px;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* Info box */
    [data-testid="stInfoMessage"] {
        background-color: #1a1d27;
        border: 1px solid #2a2d3a;
        color: #e8eaf0;
        border-radius: 10px;
    }

    /* Share bar */
    .share-bar {
        background: #1a1d27;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #2a2d3a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 1rem;
    }
    .share-title { font-weight: 600; color: #ffffff; font-size: 14px; }
    .share-url { color: #6c7293; font-size: 12px; margin-top: 2px; }
    .share-btn {
        background: #1da1f2;
        color: white;
        padding: 8px 18px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 13px;
        font-weight: 600;
    }

    /* Sidebar section headers */
    .stSidebar .stMarkdown strong { color: #ffffff !important; }

    /* Caption text */
    .stCaption { color: #6c7293 !important; }

    /* Progress bar */
    .stProgress > div > div { background: linear-gradient(90deg, #667eea, #764ba2); }

    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
