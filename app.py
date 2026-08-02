import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf

# Page Setup
st.set_page_config(
    page_title="Global Equity Valuation & Analytics Suite",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2a2e39;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Global Equity Valuation, Sentiment & Analytics Engine")
st.caption("Comprehensive Corporate Finance Suite | DCF Modeling • Peer Benchmarking • Market Sentiment")

# --- GLOBAL MARKETS PRESET DATA ---
COUNTRY_TOP_20 = {
    "🇺🇸 United States": [
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK-B", "TSLA", "LLY", "AVGO",
        "JPM", "WMT", "V", "UNH", "XOM", "MA", "PG", "COST", "HD", "JNJ"
    ],
    "🇮🇳 India (NSE)": [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS",
        "INFY.NS", "SBIN.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS",
        "L T.NS", "BAJFINANCE.NS", "HCLTECH.NS", "SUNPHARMA.NS", "ONGC.NS",
        "TATAMOTORS.NS", "NTPC.NS", "KOTAKBANK.NS", "TITAN.NS", "MARUTI.NS"
    ],
    "🇬🇧 United Kingdom": [
        "SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "GSK.L", "RIO.L", "REL.L", "DGE.L", "BATS.L",
        "PRU.L", "LSEG.L", "BA.L", "NG.L", "CPG.L", "VOD.L", "AHT.L", "BARC.L", "TSCO.L", "FLTR.L"
    ],
    "🇯🇵 Japan": [
        "7203.T", "6758.T", "8306.T", "6861.T", "9984.T", "6501.T", "8058.T", "9983.T", "4063.T", "8031.T",
        "7741.T", "6367.T", "6098.T", "7267.T", "4568.T", "8316.T", "6902.T", "6981.T", "8001.T", "7974.T"
    ],
    "🇩🇪 Germany": [
        "SAP.DE", "SIE.DE", "ALV.DE", "AIR.DE", "DT.DE", "DTE.DE", "MBG.DE", "BMW.DE", "BAS.DE", "BAYN.DE",
        "MUV2.DE", "DHL.DE", "IFX.DE", "ADS.DE", "VOW3.DE", "RWE.DE", "DB1.DE", "HEI.DE", "HEN3.DE", "BEI.DE"
    ],
    "🇨🇳 / 🇭🇰 China & Hong Kong": [
        "0700.HK", "9988.HK", "3690.HK", "0939.HK", "1398.HK", "3988.HK", "2318.HK", "1299.HK", "0883.HK", "1810.HK",
        "0941.HK", "2269.HK", "1024.HK", "2020.HK", "1113.HK", "0005.HK", "0388.HK", "2382.HK", "0669.HK", "0270.HK"
    ]
}

# --- NAVIGATION TABS ---
nav_tab1, nav_tab2, nav_tab3 = st.tabs([
    "📊 Intrinsic DCF Valuation Engine", 
    "⚔️ Global Top 20 Peer Comparison", 
    "🧠 Sentiment & Market Intelligence"
])

# ==========================================
# TAB 1: INTRINSIC DCF VALUATION ENGINE
# ==========================================
with nav_tab1:
    st.sidebar.header("1. Country & Ticker Selector")
    selected_country = st.sidebar.selectbox("Select Country Market", list(COUNTRY_TOP_20.keys()))
    selected_ticker = st.sidebar.selectbox("Select Top 20 Stock", COUNTRY_TOP_20[selected_country])
    
    custom_ticker = st.sidebar.text_input("Or Enter Custom Ticker (e.g. NVDA, RELIANCE.NS)", value="").upper()
    active_ticker = custom_ticker if custom_ticker else selected_ticker

    # Fetch Data Function
    @st.cache_data(ttl=3600)
    def load_stock_data(ticker):
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period="1y")
            return info, hist
        except Exception:
            return None, None

    info, hist = load_stock_data(active_ticker)

    if info and ('currentPrice' in info or 'regularMarketPrice' in info):
        currency = info.get('currency', 'USD')
        curr_price = info.get('currentPrice', info.get('regularMarketPrice', 100.0))
        shares_out = info.get('sharesOutstanding', 100000000) / 1e6
        total_debt = info.get('totalDebt', 100000000) / 1e6
        total_cash = info.get('totalCash', 50000000) / 1e6
        revenue = info.get('totalRevenue', 1000000000) / 1e6

        st.subheader(f"DCF Model: {info.get('longName', active_ticker)} ({active_ticker})")

        # Sidebar Inputs for Model
        st.sidebar.subheader("DCF Valuation Assumptions")
        base_rev = st.sidebar.number_input(f"Base Revenue ({currency} Millions)", value=float(revenue))
        rev_growth = st.sidebar.slider("5-Year Revenue CAGR (%)", 0.0, 40.0, 10.0, 0.5) / 100
        ebit_margin = st.sidebar.slider("EBIT Margin (%)", 1.0, 60.0, 25.0, 0.5) / 100
        tax_rate = st.sidebar.slider("Tax Rate (%)", 0.0, 40.0, 21.0, 0.5) / 100
        wacc = st.sidebar.slider("WACC / Discount Rate (%)", 4.0, 20.0, 9.0, 0.25) / 100
        g_rate = st.sidebar.slider("Terminal Growth Rate (%)", 0.0, 6.0, 2.5, 0.25) / 100

        # Calculations
        years = [f"Year {i}" for i in range(1, 6)]
        revs = [base_rev * ((1 + rev_growth) ** i) for i in range(1, 6)]
        ebit = [r * ebit_margin for r in revs]
        nopat = [e * (1 - tax_rate) for e in ebit]
        ufcf = [n * 0.85 for n in nopat]
        
        discount_factors = [1 / ((1 + wacc) ** i) for i in range(1, 6)]
        pv_ufcf = [f * d for f, d in zip(ufcf, discount_factors)]
        sum_pv_ufcf = sum(pv_ufcf)
        
        tv = (ufcf[-1] * (1 + g_rate)) / (wacc - g_rate)
        pv_tv = tv * discount_factors[-1]
        
        ev = sum_pv_ufcf + pv_tv
        net_debt = total_debt - total_cash
        eq_val = ev - net_debt
        intrinsic_price = eq_val / shares_out if shares_out > 0 else 0
        upside = ((intrinsic_price - curr_price) / curr_price) * 100

        # Primary Metrics Summary
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Intrinsic Share Price", f"{intrinsic_price:.2f} {currency}", f"{upside:+.1f}% vs Market")
        m2.metric("Current Market Price", f"{curr_price:.2f} {currency}")
        m3.metric("Enterprise Value", f"{(ev/1000):.2f}B {currency}")
        m4.metric("Equity Value", f"{(eq_val/1000):.2f}B {currency}")

        st.markdown("---")

        # Visuals
        c1, c2 = st.columns([3, 2])
        with c1:
            fig_hist = px.line(hist, y="Close", title=f"1-Year Price History ({active_ticker})", labels={"Close": f"Price ({currency})"})
            fig_hist.update_traces(line_color="#00CC96")
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            st.subheader("Sensitivities: WACC vs. Growth")
            w_range = np.linspace(wacc - 0.02, wacc + 0.02, 5)
            g_range = np.linspace(g_rate - 0.01, g_rate + 0.01, 5)
            s_matrix = []
            for g in g_range:
                row = []
                for w in w_range:
                    if w <= g:
                        row.append(np.nan)
                    else:
                        dfs = [1 / ((1 + w) ** i) for i in range(1, 6)]
                        pv_f = sum([f * df for f, df in zip(ufcf, dfs)])
                        t_val = (ufcf[-1] * (1 + g)) / (w - g)
                        p_tv = t_val * dfs[-1]
                        price = ((pv_f + p_tv) - net_debt) / shares_out
                        row.append(round(price, 2))
                s_matrix.append(row)
            
            df_sens = pd.DataFrame(s_matrix, index=[f"g={g*100:.1f}%" for g in g_range], columns=[f"WACC={w*100:.1f}%" for w in w_range])
            fig_hm = px.imshow(df_sens, text_auto=True, color_continuous_scale="Blues", aspect="auto")
            st.plotly_chart(fig_hm, use_container_width=True)

    else:
        st.error(f"Unable to load market data for '{active_ticker}'. Please verify ticker symbol.")

# ==========================================
# TAB 2: GLOBAL TOP 20 PEER COMPARISON
# ==========================================
with nav_tab2:
    st.subheader("⚔️ Multi-Company Head-to-Head Comparison")
    st.write("Compare valuation metrics, margins, and market caps across top global equities.")

    comp_country = st.selectbox("Select Market for Preset Comparison", list(COUNTRY_TOP_20.keys()))
    default_peers = COUNTRY_TOP_20[comp_country][:5]
    selected_peers = st.multiselect("Select Companies to Compare", COUNTRY_TOP_20[comp_country], default=default_peers)

    if selected_peers:
        peer_data = []
        with st.spinner("Fetching live metrics for selected peers..."):
            for p in selected_peers:
                t = yf.Ticker(p)
                inf = t.info
                peer_data.append({
                    "Ticker": p,
                    "Name": inf.get("shortName", p),
                    "Market Cap ($B)": round(inf.get("marketCap", 0) / 1e9, 2),
                    "Forward P/E": inf.get("forwardPE", np.nan),
                    "P/S Ratio": inf.get("priceToSalesTrailing12Months", np.nan),
                    "Profit Margin (%)": round(inf.get("profitMargins", 0) * 100, 2) if inf.get("profitMargins") else np.nan,
                    "ROE (%)": round(inf.get("returnOnEquity", 0) * 100, 2) if inf.get("returnOnEquity") else np.nan,
                    "Revenue Growth (%)": round(inf.get("revenueGrowth", 0) * 100, 2) if inf.get("revenueGrowth") else np.nan,
                })
        
        df_peers = pd.DataFrame(peer_data)
        st.dataframe(df_peers.style.highlight_max(axis=0, subset=["Market Cap ($B)", "Profit Margin (%)", "ROE (%)"]), use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig_bar1 = px.bar(df_peers, x="Ticker", y="Market Cap ($B)", title="Market Capitalization Comparison ($B)", color="Market Cap ($B)", color_continuous_scale="Viridis")
            st.plotly_chart(fig_bar1, use_container_width=True)
        with col_b:
            fig_bar2 = px.bar(df_peers, x="Ticker", y="Profit Margin (%)", title="Profit Margin Comparison (%)", color="Profit Margin (%)", color_continuous_scale="Plasma")
            st.plotly_chart(fig_bar2, use_container_width=True)

# ==========================================
# TAB 3: SENTIMENT & MARKET INTELLIGENCE
# ==========================================
with nav_tab3:
    st.subheader(f"🧠 Analyst Ratings & Sentiment Breakdown: {active_ticker}")
    
    if info:
        col_s1, col_s2, col_s3 = st.columns(3)
        
        target_mean = info.get("targetMeanPrice", np.nan)
        recommendation = info.get("recommendationKey", "N/A").upper().replace("_", " ")
        num_analysts = info.get("numberOfAnalystOpinions", "N/A")
        
        col_s1.metric("Analyst Consensus", recommendation)
        col_s2.metric("Mean Price Target", f"{target_mean} {info.get('currency', 'USD')}" if target_mean else "N/A")
        col_s3.metric("Analyst Coverage Count", str(num_analysts))

        st.markdown("---")
        
        st.subheader("📌 Key Financial Ratios")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Trailing P/E", f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A")
        r2.metric("PEG Ratio", f"{info.get('pegRatio', 0):.2f}" if info.get('pegRatio') else "N/A")
        r3.metric("Debt-to-Equity", f"{info.get('debtToEquity', 0):.2f}" if info.get('debtToEquity') else "N/A")
        r4.metric("Free Cashflow", f"{(info.get('freeCashflow', 0)/1e9):.2f}B" if info.get('freeCashflow') else "N/A")

        st.subheader("ℹ️ Business Profile")
        st.write(info.get("longBusinessSummary", "No company summary available."))