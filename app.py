# 1. Imports at the top
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Custom Modules
from data_fetcher import fetch_company_overview, fetch_financial_statements
from dcf_engine import calculate_wacc, run_dcf_model
from company_comparator import fetch_peer_metrics, apply_relative_valuation_tags, generate_radar_chart
from analytics import generate_2d_sensitivity_matrix, run_scenario_analysis
from sentiment import fetch_and_analyze_news_sentiment

# 2. Helper Functions (PASTE HERE)
def format_currency_scale(value: float) -> str:
    """Formats large monetary numbers into $M, $B, or $T notation."""
    if pd.isna(value) or value is None:
        return "N/A"
    
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_val >= 1e12:
        return f"{sign}${abs_val / 1e12:.2f}T"
    elif abs_val >= 1e9:
        return f"{sign}${abs_val / 1e9:.2f}B"
    elif abs_val >= 1e6:
        return f"{sign}${abs_val / 1e6:.2f}M"
    else:
        return f"{sign}${abs_val:,.2f}"

# 3. Streamlit Page Config & Main Dashboard Code
st.set_page_config(
    page_title="Global Equity DCF & Sentiment Engine",
    page_icon="⚡",
    layout="wide"
)

# ... (the rest of your app.py UI code)

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

st.title("⚡ Global Equity DCF Valuation, Peer Benchmarking & Sentiment Engine")
st.caption("Integrated Corporate Finance Suite | CAPM WACC • 5-Yr FCFF Modeling • Radar Benchmarking • Headline Sentiment")

# Preset Tickers by Country Market
COUNTRY_PRESETS = {
    "🇺🇸 United States": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"],
    "🇮🇳 India (NSE)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "INFY.NS"],
    "🇬🇧 United Kingdom": ["SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L"],
    "🇯🇵 Japan": ["7203.T", "6758.T", "8306.T", "9984.T"],
    "🇩🇪 Germany": ["SAP.DE", "SIE.DE", "ALV.DE", "BMW.DE"],
}

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Target Stock Selection")
selected_country = st.sidebar.selectbox("Select Market", list(COUNTRY_PRESETS.keys()))
selected_ticker = st.sidebar.selectbox("Select Preset Stock", COUNTRY_PRESETS[selected_country])
custom_ticker = st.sidebar.text_input("Or Custom Ticker (e.g. AMD, INFY.NS)", value="").upper()

active_ticker = custom_ticker if custom_ticker else selected_ticker

# Load Core Overview Data
overview = fetch_company_overview(active_ticker)

# Check if data loaded properly
if pd.isna(overview["Market Cap ($B)"]) and overview["Company Name"] == active_ticker:
    st.error(f"Unable to load financial data for '{active_ticker}'. Please verify ticker symbol.")
else:
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Intrinsic DCF & Risk Sensitivity", 
        "⚔️ Peer Benchmarking & Radar", 
        "🧠 News Sentiment & Market Intelligence"
    ])

    # ==========================================
    # TAB 1: SINGLE-STOCK DCF & SENSITIVITY
    # ==========================================
    with tab1:
        st.sidebar.subheader("2. DCF Model Assumptions")
        
        # Default Inputs Derived from Company Data
        default_price = fetch_company_overview(active_ticker).get("Current Price", 150.0)
        curr_price = default_price if isinstance(default_price, (int, float)) and default_price > 0 else 150.0
        
        shares_out = overview.get("Shares Outstanding (M)", 100.0)
        total_debt = overview.get("Total Debt ($M)", 0.0)
        total_cash = overview.get("Total Cash ($M)", 0.0)
        beta_val = overview.get("Beta", 1.0)
        if pd.isna(beta_val):
            beta_val = 1.0

        # User Sliders
        rev_growth = st.sidebar.slider("5-Year Revenue CAGR (%)", 0.0, 40.0, 10.0, 0.5) / 100
        ebit_margin = st.sidebar.slider("EBIT Margin (%)", 1.0, 60.0, 20.0, 0.5) / 100
        tax_rate = st.sidebar.slider("Tax Rate (%)", 0.0, 40.0, 21.0, 0.5) / 100
        reinvestment_rate = st.sidebar.slider("Reinvestment Rate (% of NOPAT)", 0.0, 50.0, 15.0, 1.0) / 100
        
        st.sidebar.subheader("3. WACC & Terminal Growth")
        rf_rate = st.sidebar.number_input("Risk-Free Rate (%)", value=4.2, step=0.1) / 100
        erp = st.sidebar.number_input("Equity Risk Premium (%)", value=5.8, step=0.1) / 100
        cost_of_debt = st.sidebar.number_input("Pre-Tax Cost of Debt (%)", value=5.0, step=0.1) / 100
        terminal_g = st.sidebar.slider("Terminal Growth Rate (%)", 0.0, 5.0, 2.5, 0.25) / 100

        # Compute WACC
        wacc_dict = calculate_wacc(
            beta=beta_val,
            risk_free_rate=rf_rate,
            market_return=rf_rate + erp,
            cost_of_debt_pre_tax=cost_of_debt,
            tax_rate=tax_rate,
            equity_market_cap=overview.get("Market Cap ($B)", 100.0) * 1000,
            total_debt=total_debt
        )
        calculated_wacc = wacc_dict["wacc"]

        # Base Revenue Proxy from Market Cap / PS or default
        base_rev = (overview.get("Market Cap ($B)", 10.0) * 1000) / (overview.get("P/S Ratio", 2.0) if pd.notna(overview.get("P/S Ratio")) else 2.0)

        # Run DCF Engine
        dcf_results = run_dcf_model(
            base_revenue=base_rev,
            revenue_growth_rate=rev_growth,
            ebit_margin=ebit_margin,
            tax_rate=tax_rate,
            reinvestment_rate=reinvestment_rate,
            wacc=calculated_wacc,
            terminal_growth_rate=terminal_g,
            total_debt=total_debt,
            total_cash=total_cash,
            shares_outstanding=shares_out,
            current_price=curr_price
        )

        # TOP BANNER KPI METRICS
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Intrinsic Share Price", f"${dcf_results['intrinsic_price']:.2f}", f"{dcf_results['upside_downside_pct']:+.2f}% vs Market")
        kpi2.metric("Market Price", f"${curr_price:.2f}")
        kpi3.metric("Computed WACC", f"{calculated_wacc * 100:.2f}%", f"CAPM Beta: {beta_val:.2f}")
        kpi4.metric("Enterprise Value", f"${dcf_results['enterprise_value']:.2f}M")

        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("5-Year Free Cash Flow Projections")
            st.dataframe(dcf_results["projections_table"], use_container_width=True)

            # Scenario Analysis
            st.subheader("Operational Scenario Analysis")
            df_scenarios = run_scenario_analysis(
                base_revenue=base_rev,
                tax_rate=tax_rate,
                reinvestment_rate=reinvestment_rate,
                base_wacc=calculated_wacc,
                base_g=terminal_g,
                total_debt=total_debt,
                total_cash=total_cash,
                shares_outstanding=shares_out,
                current_price=curr_price,
                base_growth=rev_growth,
                base_ebit_margin=ebit_margin
            )
            st.dataframe(df_scenarios, use_container_width=True)

        with col_right:
            st.subheader("2D Sensitivity Heatmap (WACC vs. Terminal Growth)")
            df_sens = generate_2d_sensitivity_matrix(
                base_revenue=base_rev,
                revenue_growth_rate=rev_growth,
                ebit_margin=ebit_margin,
                tax_rate=tax_rate,
                reinvestment_rate=reinvestment_rate,
                base_wacc=calculated_wacc,
                base_g=terminal_g,
                total_debt=total_debt,
                total_cash=total_cash,
                shares_outstanding=shares_out,
                current_price=curr_price
            )
            fig_hm = px.imshow(
                df_sens,
                text_auto=True,
                color_continuous_scale="RdYlGn",
                labels=dict(x="WACC", y="Terminal Growth Rate", color="Intrinsic Price ($)"),
                aspect="auto"
            )
            st.plotly_chart(fig_hm, use_container_width=True)

    # ==========================================
    # TAB 2: CROSS-COMPANY COMPARISON
    # ==========================================
    with tab2:
        st.subheader("⚔️ Peer Benchmarking & Relative Valuation")
        
        default_peers = COUNTRY_PRESETS[selected_country][:4]
        selected_peers = st.multiselect(
            "Select Tickers for Side-by-Side Analysis",
            options=COUNTRY_PRESETS[selected_country] + [active_ticker],
            default=list(set(default_peers + [active_ticker]))
        )

        if selected_peers:
            df_peers = fetch_peer_metrics(selected_peers)
            df_peers_tagged = apply_relative_valuation_tags(df_peers)

            st.dataframe(df_peers_tagged, use_container_width=True)

            st.markdown("---")

            col_radar, col_bars = st.columns([1, 1])

            with col_radar:
                st.subheader("Multi-Attribute Radar Performance Chart")
                fig_radar = generate_radar_chart(df_peers)
                st.plotly_chart(fig_radar, use_container_width=True)

            with col_bars:
                st.subheader("Operating Margins vs. Trailing P/E")
                fig_bar = px.bar(
                    df_peers,
                    x="Ticker",
                    y="Operating Margin (%)",
                    color="Trailing P/E",
                    text="Operating Margin (%)",
                    title="Operating Margin (%) & Trailing P/E Multiple",
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================
    # TAB 3: SENTIMENT & MARKET INTELLIGENCE
    # ==========================================
    with tab3:
        st.subheader(f"🧠 Real-Time Headline News Sentiment: {active_ticker}")
        
        sentiment_res = fetch_and_analyze_news_sentiment(active_ticker)

        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        s_col1.metric("Overall Sentiment", sentiment_res["overall_sentiment"])
        s_col2.metric("Average Polarity Score", f"{sentiment_res['average_polarity']:.3f}")
        s_col3.metric("Bullish Headlines", f"{sentiment_res['bullish_pct']:.1f}%")
        s_col4.metric("Bearish Headlines", f"{sentiment_res['bearish_pct']:.1f}%")

        st.markdown("---")

        st.subheader("Live News Feed & Article Polarity Breakdown")
        if not sentiment_res["articles_table"].empty:
            st.dataframe(
                sentiment_res["articles_table"][["Headline", "Publisher", "Polarity Score", "Sentiment"]],
                use_container_width=True
            )
        else:
            st.info(f"No recent news headlines available for '{active_ticker}'.")