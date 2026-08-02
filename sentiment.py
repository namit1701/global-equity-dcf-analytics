import yfinance as yf
import pandas as pd

BULLISH_WORDS = {
    "growth", "surge", "up", "gain", "profit", "bull", "bullish", "record", "high",
    "buy", "outperform", "beat", "rally", "positive", "strong", "boost", "climb",
    "revenue", "expansion", "dividend", "upgrade", "lead", "jump", "soar", "top"
}

BEARISH_WORDS = {
    "drop", "fall", "loss", "decline", "down", "bear", "bearish", "sell", "underperform",
    "miss", "slump", "negative", "weak", "cut", "plunge", "risk", "warning", "debt",
    "layoff", "lawsuit", "investigation", "downgrade", "crisis", "fallout", "sink"
}

COUNTRY_BENCHMARK_TICKERS = {
    "🇺🇸 United States": "^GSPC",    # S&P 500
    "🇮🇳 India": "^BSESN",            # BSE Sensex
    "🇬🇧 United Kingdom": "^FTSE",    # FTSE 100
    "🇯🇵 Japan": "^N225",             # Nikkei 225
    "🇩🇪 Germany": "^GDAXI"          # DAX
}


def calculate_simple_polarity(text: str) -> float:
    words = text.lower().replace(",", "").replace(".", "").split()
    if not words:
        return 0.0

    pos_count = sum(1 for w in words if w in BULLISH_WORDS)
    neg_count = sum(1 for w in words if w in BEARISH_WORDS)

    total_matched = pos_count + neg_count
    if total_matched == 0:
        return 0.0

    return (pos_count - neg_count) / total_matched


def extract_raw_news_list(ticker_symbol: str) -> list:
    """Safely extracts news dictionary list across different yfinance versions."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        raw_items = ticker.news
        parsed_articles = []

        if raw_items:
            for item in raw_items:
                title, publisher, link = "", "Unknown", "#"
                if isinstance(item, dict):
                    content = item.get("content", item)
                    if isinstance(content, dict):
                        title = content.get("title", "")
                        provider = content.get("provider", {})
                        publisher = provider.get("displayName", "Unknown") if isinstance(provider, dict) else "Unknown"
                        canonical = content.get("canonicalUrl", {})
                        link = canonical.get("url", "#") if isinstance(canonical, dict) else "#"
                    else:
                        title = item.get("title", "")
                        publisher = item.get("publisher", "Unknown")
                        link = item.get("link", "#")

                if title:
                    polarity = calculate_simple_polarity(title)
                    label = "Bullish 🟢" if polarity > 0.05 else ("Bearish 🔴" if polarity < -0.05 else "Neutral 🟡")
                    parsed_articles.append({
                        "Headline": title,
                        "Publisher": publisher,
                        "Polarity Score": round(polarity, 3),
                        "Sentiment": label,
                        "Link": link
                    })
        return parsed_parsed_articles if 'parsed_parsed_articles' in locals() else parsed_articles
    except Exception:
        return []


def fetch_country_top_headlines() -> pd.DataFrame:
    """Fetches the top 3 headlines for each country's benchmark index."""
    country_headlines = []

    for country, index_ticker in COUNTRY_BENCHMARK_TICKERS.items():
        articles = extract_raw_news_list(index_ticker)
        top_3 = articles[:3] if articles else []

        for art in top_3:
            country_headlines.append({
                "Country / Region": country,
                "Headline": art["Headline"],
                "Publisher": art["Publisher"],
                "Sentiment": art["Sentiment"],
                "Polarity": art["Polarity Score"]
            })

    return pd.DataFrame(country_headlines)


def fetch_and_analyze_news_sentiment(ticker_symbol: str) -> dict:
    articles = extract_raw_news_list(ticker_symbol)
    df_articles = pd.DataFrame(articles)

    if not df_articles.empty:
        polarity_scores = df_articles["Polarity Score"].tolist()
        avg_polarity = sum(polarity_scores) / len(polarity_scores)
        total = len(polarity_scores)
        bull_count = sum(1 for p in polarity_scores if p > 0.05)
        bear_count = sum(1 for p in polarity_scores if p < -0.05)
        neu_count = total - (bull_count + bear_count)

        overall = "Bullish 🟢" if avg_polarity > 0.05 else ("Bearish 🔴" if avg_polarity < -0.05 else "Neutral 🟡")

        return {
            "overall_sentiment": overall,
            "average_polarity": round(avg_polarity, 3),
            "bullish_pct": round((bull_count / total) * 100, 1),
            "bearish_pct": round((bear_count / total) * 100, 1),
            "neutral_pct": round((neu_count / total) * 100, 1),
            "articles_table": df_articles,
        }

    return {
        "overall_sentiment": "Neutral 🟡",
        "average_polarity": 0.0,
        "bullish_pct": 0.0,
        "bearish_pct": 0.0,
        "neutral_pct": 100.0,
        "articles_table": df_articles,
    }