import numpy as np
import pandas as pd
from dcf_engine import run_dcf_model


def generate_2d_sensitivity_matrix(
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
    wacc_spread: float = 0.010,  # ±1.0%
    g_spread: float = 0.005,      # ±0.5%
    steps: int = 5,
) -> pd.DataFrame:
    """
    Generates a 2D Sensitivity Grid evaluating Intrinsic Share Price across a grid 
    of WACC (±1.0%) and Terminal Growth Rates (±0.5%).
    """
    wacc_grid = np.linspace(base_wacc - wacc_spread, base_wacc + wacc_spread, steps)
    g_grid = np.linspace(base_g - g_spread, base_g + g_spread, steps)

    matrix = []
    for g in g_grid:
        row = []
        for w in wacc_grid:
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
        matrix.append(row)

    df_sens = pd.DataFrame(
        matrix,
        index=[f"g = {round(g * 100, 2)}%" for g in g_grid],
        columns=[f"WACC = {round(w * 100, 2)}%" for w in wacc_grid],
    )
    return df_sens


def run_scenario_analysis(
    base_revenue: float,
    tax_rate: float,
    reinvestment_rate: float,
    base_wacc: float,
    base_g: float,
    total_debt: float,
    total_cash: float,
    shares_outstanding: float,
    current_price: float,
    base_growth: float,
    base_ebit_margin: float,
) -> pd.DataFrame:
    """
    Evaluates Bull, Base, and Bear scenarios based on operational growth and margin changes.
    """
    scenarios = {
        "Bear Case 🔴": {"growth": base_growth * 0.70, "margin": base_ebit_margin * 0.80, "wacc_adj": 0.005},
        "Base Case 🟡": {"growth": base_growth, "margin": base_ebit_margin, "wacc_adj": 0.0},
        "Bull Case 🟢": {"growth": base_growth * 1.30, "margin": base_ebit_margin * 1.20, "wacc_adj": -0.005},
    }

    results = []
    for case, params in scenarios.items():
        res = run_dcf_model(
            base_revenue=base_revenue,
            revenue_growth_rate=params["growth"],
            ebit_margin=params["margin"],
            tax_rate=tax_rate,
            reinvestment_rate=reinvestment_rate,
            wacc=base_wacc + params["wacc_adj"],
            terminal_growth_rate=base_g,
            total_debt=total_debt,
            total_cash=total_cash,
            shares_outstanding=shares_outstanding,
            current_price=current_price,
        )
        results.append({
            "Scenario": case,
            "Rev Growth (%)": round(params["growth"] * 100, 2),
            "EBIT Margin (%)": round(params["margin"] * 100, 2),
            "WACC (%)": round((base_wacc + params["wacc_adj"]) * 100, 2),
            "Intrinsic Price": res["intrinsic_price"],
            "Upside / Downside (%)": res["upside_downside_pct"],
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    print("--- Testing Sensitivity Matrix ---")
    df_s = generate_2d_sensitivity_matrix(
        base_revenue=1000.0,
        revenue_growth_rate=0.10,
        ebit_margin=0.25,
        tax_rate=0.21,
        reinvestment_rate=0.15,
        base_wacc=0.09,
        base_g=0.025,
        total_debt=100.0,
        total_cash=50.0,
        shares_outstanding=50.0,
        current_price=150.0,
    )
    print(df_s)
