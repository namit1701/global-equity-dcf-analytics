import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf


def fetch_peer_metrics(ticker_list: list) -> pd.DataFrame:
    """
    Retrieves side-by-side metrics including valuation ratios, margins, and growth rates
    for a list of tickers.
    """
    records = []
    for ticker in ticker_list:
        try:
            t = yf.Ticker(ticker)
            info = t.info if t.info else {}

            market_cap = info.get("marketCap", np.nan)
            trailing_pe = info.get("trailingPE", np.nan)
            forward_pe = info.get("forwardPE", np.nan)
            ev_ebitda = info.get("enterpriseToEbitda", np.nan)
            price_to_book = info.get("priceToBook", np.nan)
            price_to_sales = info.get("priceToSalesTrailing12Months", np.nan)

            gross_margin = info.get("grossMargins", np.nan)
            op_margin = info.get("operatingMargins", np.nan)
            profit_margin = info.get("profitMargins", np.nan)
            roe = info.get("returnOnEquity", np.nan)

            rev_growth = info.get("revenueGrowth", np.nan)
            earnings_growth = info.get("earningsGrowth", np.nan)
            debt_to_equity = info.get("debtToEquity", np.nan)

            records.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                "Sector": info.get("sector", "N/A"),
                "Market Cap ($B)": round(market_cap / 1e9, 2) if pd.notna(market_cap) else np.nan,
                # Valuation Metrics
                "Trailing P/E": round(trailing_pe, 2) if pd.notna(trailing_pe) else np.nan,
                "Forward P/E": round(forward_pe, 2) if pd.notna(forward_pe) else np.nan,
                "EV/EBITDA": round(ev_ebitda, 2) if pd.notna(ev_ebitda) else np.nan,
                "P/B Ratio": round(price_to_book, 2) if pd.notna(price_to_book) else np.nan,
                "P/S Ratio": round(price_to_sales, 2) if pd.notna(price_to_sales) else np.nan,
                # Operating Efficiency & Margins
                "Gross Margin (%)": round(gross_margin * 100, 2) if pd.notna(gross_margin) else np.nan,
                "Operating Margin (%)": round(op_margin * 100, 2) if pd.notna(op_margin) else np.nan,
                "Profit Margin (%)": round(profit_margin * 100, 2) if pd.notna(profit_margin) else np.nan,
                "ROE (%)": round(roe * 100, 2) if pd.notna(roe) else np.nan,
                # Growth & Capital Structure
                "Revenue Growth (%)": round(rev_growth * 100, 2) if pd.notna(rev_growth) else np.nan,
                "Earnings Growth (%)": round(earnings_growth * 100, 2) if pd.notna(earnings_growth) else np.nan,
                "Debt/Equity": round(debt_to_equity, 2) if pd.notna(debt_to_equity) else np.nan,
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    return pd.DataFrame(records)


def apply_relative_valuation_tags(df_peers: pd.DataFrame) -> pd.DataFrame:
    """
    Compares company P/E and EV/EBITDA against peer group medians
    to tag stocks as 'Relatively Undervalued' or 'Relatively Overvalued'.
    """
    df = df_peers.copy()
    if df.empty or "Trailing P/E" not in df.columns:
        return df

    median_pe = df["Trailing P/E"].median(skipna=True)
    median_ev_ebitda = df["EV/EBITDA"].median(skipna=True)

    def valuation_tag(row):
        pe = row.get("Trailing P/E")
        ev = row.get("EV/EBITDA")

        score = 0
        valid_counts = 0

        if pd.notna(pe) and pd.notna(median_pe):
            valid_counts += 1
            if pe < median_pe:
                score += 1
            elif pe > median_pe:
                score -= 1

        if pd.notna(ev) and pd.notna(median_ev_ebitda):
            valid_counts += 1
            if ev < median_ev_ebitda:
                score += 1
            elif ev > median_ev_ebitda:
                score -= 1

        if valid_counts == 0:
            return "Neutral / N/A"
        if score > 0:
            return "Relatively Undervalued 🟢"
        elif score < 0:
            return "Relatively Overvalued 🔴"
        else:
            return "Fairly Valued 🟡"

    df["Relative Valuation Tag"] = df.apply(valuation_tag, axis=1)
    return df


def generate_radar_chart(df_peers: pd.DataFrame) -> go.Figure:
    """
    Generates a multi-attribute Radar / Spider chart comparing Growth, Profitability,
    Valuation, Return, and Financial Health across peers normalized to percentile ranks (0-100).
    """
    fig = go.Figure()
    
    if df_peers.empty:
        return fig

    # Attributes mapped for scoring (higher score = better percentile rank)
    # Note: P/E is inverted so lower P/E yields higher rank score
    df_norm = df_peers.copy()
    
    df_norm["Valuation Score"] = 100 - df_norm["Trailing P/E"].rank(pct=True, ascending=True).fillna(0.5) * 100
    df_norm["Profitability Score"] = df_norm["Operating Margin (%)"].rank(pct=True, ascending=True).fillna(0.5) * 100
    df_norm["Return Score"] = df_norm["ROE (%)"].rank(pct=True, ascending=True).fillna(0.5) * 100
    df_norm["Growth Score"] = df_norm["Revenue Growth (%)"].rank(pct=True, ascending=True).fillna(0.5) * 100
    df_norm["Financial Health Score"] = 100 - df_norm["Debt/Equity"].rank(pct=True, ascending=True).fillna(0.5) * 100

    categories = ["Valuation", "Profitability", "Return (ROE)", "Growth", "Financial Health"]

    for _, row in df_norm.iterrows():
        values = [
            row["Valuation Score"],
            row["Profitability Score"],
            row["Return Score"],
            row["Growth Score"],
            row["Financial Health Score"],
        ]
        # Close the loop for radar chart display
        values.append(values[0])

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=f"{row['Ticker']} ({row['Company']})"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Multi-Attribute Peer Radar Benchmark (Percentile Ranks)"
    )

    return fig


if __name__ == "__main__":
    # Test script execution locally
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    print(f"--- Fetching Peer Comparison Data for {test_tickers} ---")
    df_p = fetch_peer_metrics(test_tickers)
    df_p = apply_relative_valuation_tags(df_p)
    print(df_p[["Ticker", "Trailing P/E", "EV/EBITDA", "Operating Margin (%)", "Relative Valuation Tag"]])