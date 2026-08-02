\# ⚡ Global Equity DCF Analytics \& Peer Benchmarking Suite



A comprehensive financial valuation and market intelligence dashboard built with Python and Streamlit. This application integrates a \*\*Discounted Cash Flow (DCF) Valuation Engine\*\*, \*\*Cross-Company Peer Benchmarking\*\*, \*\*Risk Sensitivity Modeling\*\*, and \*\*Live Headline Sentiment Analysis\*\* into an interactive web interface.



\---



\## 🎯 Key Features



\### 1. Intrinsic DCF Valuation Engine

\* \*\*CAPM WACC Computation\*\*: Dynamic calculation of Cost of Capital using beta, market risk premium, and corporate tax rates.

\* \*\*5-Year FCFF Forecasting\*\*: Multi-year Free Cash Flow to Firm projections based on user-configured growth and margin assumptions.

\* \*\*Readable Large Number Formatting\*\*: Automatically formats enterprise values, cash flows, and market caps into clean \*\*Million ($M)\*\*, \*\*Billion ($B)\*\*, and \*\*Trillion ($T)\*\* scales.



\### 2. Cross-Company Peer Benchmarking

\* \*\*Side-by-Side Comparison Matrix\*\*: Compare valuation multiples (P/E, EV/EBITDA, P/B, P/S), margins, and growth metrics across global peers.

\* \*\*Relative Valuation Mapping\*\*: Flag stocks as \*Relatively Undervalued\* or \*Relatively Overvalued\* against sector medians.

\* \*\*Multi-Attribute Radar Charts\*\*: Plot standardized percentile ranks across Growth, Profitability, Return (ROE), Valuation, and Financial Health using Plotly.



\### 3. Risk Sensitivity \& Scenario Modeling

\* \*\*2D WACC vs. Terminal Growth Heatmap\*\*: Evaluate stock sensitivity across a grid of WACC (±1.0%) and Terminal Growth Rates (±0.5%).

\* \*\*Scenario Analysis\*\*: Test Bull, Base, and Bear operational cases to project upside/downside ranges.



\### 4. News Sentiment \& Market Intelligence

\* \*\*Real-Time News Feed\*\*: Retrieve stock news headlines using `yfinance`.

\* \*\*Lexicon Polarity Scoring\*\*: Classify live market sentiment as \*\*Bullish 🟢\*\*, \*\*Neutral 🟡\*\*, or \*\*Bearish 🔴\*\*.



\---



\## 🛠️ Tech Stack



\* \*\*Language\*\*: Python

\* \*\*Frontend/UI\*\*: Streamlit

\* \*\*Financial Data\*\*: `yfinance`

\* \*\*Data Processing\*\*: `pandas`, `numpy`

\* \*\*Data Visualization\*\*: `plotly`



\---



\## 🚀 Installation \& Local Run Instructions



\### 1. Clone the Repository

```bash

git clone \[https://github.com/YOUR\_USERNAME/global-equity-dcf-analytics.git](https://github.com/YOUR\_USERNAME/global-equity-dcf-analytics.git)

cd global-equity-dcf-analytics

