import yfinance as yf
import pandas as pd
import numpy as np

def fetch_company_overview(ticker_symbol: str) -> dict:
    """
    Extracts high-level info, capital structure parameters, and relative financial ratios.
    """
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info if ticker.info else {}

    # Capital Structure Parameters
    shares_outstanding = info.get("sharesOutstanding", np.nan)
    market_cap = info.get("marketCap", np.nan)
    total_debt = info.get("totalDebt", 0.0)
    total_cash = info.get("totalCash", 0.0)
    net_debt = total_debt - total_cash if (total_debt is not None and total_cash is not None) else np.nan
    beta = info.get("beta", np.nan)

    # Relative Performance & Valuation Ratios
    summary_data = {
        "Ticker": ticker_symbol,
        "Company Name": info.get("shortName", ticker_symbol),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Currency": info.get("currency", "USD"),
        "Market Cap ($B)": round(market_cap / 1e9, 2) if pd.notna(market_cap) else np.nan,
        "Shares Outstanding (M)": round(shares_outstanding / 1e6, 2) if pd.notna(shares_outstanding) else np.nan,
        "Total Debt ($M)": round(total_debt / 1e6, 2) if pd.notna(total_debt) else np.nan,
        "Total Cash ($M)": round(total_cash / 1e6, 2) if pd.notna(total_cash) else np.nan,
        "Net Debt ($M)": round(net_debt / 1e6, 2) if pd.notna(net_debt) else np.nan,
        "Beta": round(beta, 2) if pd.notna(beta) else np.nan,
        # Performance & Valuation Ratios
        "Trailing P/E": round(info.get("trailingPE", np.nan), 2) if info.get("trailingPE") else np.nan,
        "Forward P/E": round(info.get("forwardPE", np.nan), 2) if info.get("forwardPE") else np.nan,
        "EV/EBITDA": round(info.get("enterpriseToEbitda", np.nan), 2) if info.get("enterpriseToEbitda") else np.nan,
        "P/S Ratio": round(info.get("priceToSalesTrailing12Months", np.nan), 2) if info.get("priceToSalesTrailing12Months") else np.nan,
        "P/B Ratio": round(info.get("priceToBook", np.nan), 2) if info.get("priceToBook") else np.nan,
        "ROE (%)": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else np.nan,
        "ROA (%)": round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else np.nan,
        "Debt-to-Equity": round(info.get("debtToEquity", np.nan), 2) if info.get("debtToEquity") else np.nan,
        "Operating Margin (%)": round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else np.nan,
        "Profit Margin (%)": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else np.nan,
    }
    
    return summary_data


def fetch_financial_statements(ticker_symbol: str) -> dict:
    """
    Extracts core Income Statement, Balance Sheet, and Cash Flow Statement.
    Calculates Free Cash Flow to Firm (FCFF).
    """
    ticker = yf.Ticker(ticker_symbol)
    
    inc_stmt = ticker.financials
    bal_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    # Extract key line items for DCF / FCFF Modeling
    key_metrics = {}
    
    if not cash_flow.empty and not inc_stmt.empty:
        try:
            # Operating Cash Flow
            ocf = cash_flow.loc["Operating Cash Flow"] if "Operating Cash Flow" in cash_flow.index else cash_flow.loc["Total Cash From Operating Activities"]
            
            # Capital Expenditures (CapEx)
            capex = cash_flow.loc["Capital Expenditure"] if "Capital Expenditure" in cash_flow.index else cash_flow.loc["Capital Expenditures"]
            
            # Free Cash Flow to Firm (FCFF) estimate = OCF + CapEx (CapEx is typically negative in standard cash flow statements)
            fcff = ocf + capex
            
            key_metrics["Operating Cash Flow ($M)"] = (ocf / 1e6).round(2).to_dict()
            key_metrics["CapEx ($M)"] = (capex / 1e6).round(2).to_dict()
            key_metrics["FCFF ($M)"] = (fcff / 1e6).round(2).to_dict()
        except KeyError:
            pass

    return {
        "income_statement": inc_stmt,
        "balance_sheet": bal_sheet,
        "cash_flow": cash_flow,
        "key_metrics": key_metrics
    }


def fetch_peer_benchmark_data(ticker_list: list) -> pd.DataFrame:
    """
    Fetches comparative ratios and capital metrics for a batch of tickers.
    """
    peers_list = []
    for t in ticker_list:
        try:
            data = fetch_company_overview(t)
            peers_list.append(data)
        except Exception as e:
            print(f"Failed to fetch data for {t}: {e}")
            
    return pd.DataFrame(peers_list)


if __name__ == "__main__":
    # Test script locally
    test_ticker = "AAPL"
    print(f"--- Fetching Data for {test_ticker} ---")
    overview = fetch_company_overview(test_ticker)
    for k, v in overview.items():
        print(f"{k}: {v}")