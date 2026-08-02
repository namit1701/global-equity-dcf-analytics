import numpy as np
import pandas as pd


def calculate_wacc(
    beta: float,
    risk_free_rate: float = 0.042,
    market_return: float = 0.10,
    cost_of_debt_pre_tax: float = 0.05,
    tax_rate: float = 0.21,
    equity_market_cap: float = 1000.0,
    total_debt: float = 200.0,
) -> dict:
    """
    Calculates Weighted Average Cost of Capital (WACC) using CAPM for Cost of Equity
    and after-tax Cost of Debt.
    """
    # 1. Cost of Equity via CAPM: E(Ri) = Rf + Beta * (Rm - Rf)
    equity_risk_premium = market_return - risk_free_rate
    cost_of_equity = risk_free_rate + (beta * equity_risk_premium)

    # 2. After-Tax Cost of Debt: Rd * (1 - Tax Rate)
    cost_of_debt_after_tax = cost_of_debt_pre_tax * (1 - tax_rate)

    # 3. Capital Structure Weights
    total_capital = equity_market_cap + total_debt
    if total_capital == 0:
        weight_equity = 1.0
        weight_debt = 0.0
    else:
        weight_equity = equity_market_cap / total_capital
        weight_debt = total_debt / total_capital

    # 4. WACC Formula
    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt_after_tax)

    return {
        "wacc": round(wacc, 4),
        "cost_of_equity": round(cost_of_equity, 4),
        "cost_of_debt_after_tax": round(cost_of_debt_after_tax, 4),
        "weight_equity": round(weight_equity, 4),
        "weight_debt": round(weight_debt, 4),
    }


def run_dcf_model(
    base_revenue: float,
    revenue_growth_rate: float,
    ebit_margin: float,
    tax_rate: float,
    reinvestment_rate: float,
    wacc: float,
    terminal_growth_rate: float,
    total_debt: float,
    total_cash: float,
    shares_outstanding: float,
    current_price: float,
    projection_years: int = 5,
) -> dict:
    """
    Performs 5-Year FCFF Forecasting, Gordon Growth Terminal Value,
    Enterprise Value, Equity Value, and Intrinsic Price per Share calculation.
    """
    yearly_projections = []
    pv_fcff_list = []

    current_rev = base_revenue
    for yr in range(1, projection_years + 1):
        rev = current_rev * (1 + revenue_growth_rate)
        ebit = rev * ebit_margin
        nopat = ebit * (1 - tax_rate)
        # Free Cash Flow to Firm (FCFF) = NOPAT - Net Reinvestment
        fcff = nopat * (1 - reinvestment_rate)
        discount_factor = 1 / ((1 + wacc) ** yr)
        pv_fcff = fcff * discount_factor

        yearly_projections.append({
            "Year": f"Year {yr}",
            "Revenue": round(rev, 2),
            "EBIT": round(ebit, 2),
            "NOPAT": round(nopat, 2),
            "FCFF": round(fcff, 2),
            "PV_FCFF": round(pv_fcff, 2),
        })

        pv_fcff_list.append(pv_fcff)
        current_rev = rev

    sum_pv_fcff = sum(pv_fcff_list)
    last_year_fcff = yearly_projections[-1]["FCFF"]

    # Gordon Growth Terminal Value: TV = [FCF5 * (1 + g)] / (WACC - g)
    if wacc <= terminal_growth_rate:
        terminal_value = 0.0
        pv_terminal_value = 0.0
    else:
        terminal_value = (last_year_fcff * (1 + terminal_growth_rate)) / (wacc - terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1 + wacc) ** projection_years)

    # Enterprise Value & Equity Value bridge
    enterprise_value = sum_pv_fcff + pv_terminal_value
    net_debt = total_debt - total_cash
    equity_value = enterprise_value - net_debt

    # Per Share Calculation
    intrinsic_price = equity_value / shares_outstanding if shares_outstanding > 0 else 0.0
    upside_downside_pct = ((intrinsic_price - current_price) / current_price) * 100 if current_price > 0 else 0.0

    return {
        "intrinsic_price": round(intrinsic_price, 2),
        "current_price": round(current_price, 2),
        "upside_downside_pct": round(upside_downside_pct, 2),
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "sum_pv_fcff": round(sum_pv_fcff, 2),
        "pv_terminal_value": round(pv_terminal_value, 2),
        "terminal_value": round(terminal_value, 2),
        "projections_table": pd.DataFrame(yearly_projections),
    }


def generate_sensitivity_matrix(
    base_revenue: float,
    revenue_growth_rate: float,
    ebit_margin: float,
    tax_rate: float,
    reinvestment_rate: float,
    base_wacc: float,
    base_g: float,
    total_debt: float,
    total_cash: float,
    shares_outstanding: float,
    current_price: float,
    wacc_steps: list = [-0.02, -0.01, 0.0, 0.01, 0.02],
    g_steps: list = [-0.01, -0.005, 0.0, 0.005, 0.01],
) -> pd.DataFrame:
    """
    Generates a 2D matrix evaluating Intrinsic Price sensitivity to changes in WACC and Terminal Growth Rate (g).
    """
    wacc_range = [base_wacc + step for step in wacc_steps]
    g_range = [base_g + step for step in g_steps]

    matrix_data = []
    for g in g_range:
        row = []
        for w in wacc_range:
            if w <= g:
                row.append(np.nan)
            else:
                res = run_dcf_model(
                    base_revenue=base_revenue,
                    revenue_growth_rate=revenue_growth_rate,
                    ebit_margin=ebit_margin,
                    tax_rate=tax_rate,
                    reinvestment_rate=reinvestment_rate,
                    wacc=w,
                    terminal_growth_rate=g,
                    total_debt=total_debt,
                    total_cash=total_cash,
                    shares_outstanding=shares_outstanding,
                    current_price=current_price,
                )
                row.append(res["intrinsic_price"])
        matrix_data.append(row)

    df_sens = pd.DataFrame(
        matrix_data,
        index=[f"g = {round(g * 100, 2)}%" for g in g_range],
        columns=[f"WACC = {round(w * 100, 2)}%" for w in wacc_range],
    )
    return df_sens


if __name__ == "__main__":
    # Test execution
    wacc_res = calculate_wacc(beta=1.2, equity_market_cap=3000.0, total_debt=100.0)
    print("WACC Result:", wacc_res)

    dcf_res = run_dcf_model(
        base_revenue=1000.0,
        revenue_growth_rate=0.10,
        ebit_margin=0.25,
        tax_rate=0.21,
        reinvestment_rate=0.15,
        wacc=wacc_res["wacc"],
        terminal_growth_rate=0.025,
        total_debt=100.0,
        total_cash=50.0,
        shares_outstanding=50.0,
        current_price=150.0,
    )
    print("\nIntrinsic Price:", dcf_res["intrinsic_price"])
    print("Upside / Downside:", dcf_res["upside_downside_pct"], "%")
    print("\nFCFF Projections:\n", dcf_res["projections_table"])