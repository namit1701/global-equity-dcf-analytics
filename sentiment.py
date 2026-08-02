import yfinance as yf
import pandas as pd

# Lexicon-based sentiment scorer without NLTK/regex security blocks
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


def calculate_simple_polarity(text: str) -> float:
    """
    Calculates a polarity score (-1.0 to +1.0) based on financial lexicon matching.
    """
    words = text.lower().replace(",", "").replace(".", "").split()
    if not words:
        return 0.0

    pos_count = sum(1 for w in words if w in BULLISH_WORDS)
    neg_count = sum(1 for w in words if w in BEARISH_WORDS)

    total_matched = pos_count + neg_count
    if total_matched == 0:
        return 0.0

    return (pos_count - neg_count) / total_matched


def fetch_and_analyze_news_sentiment(ticker_symbol: str) -> dict:
    """
    Fetches stock news headlines via yfinance, calculates polarity,
    and categorizes real-time market sentiment as Bullish, Neutral, or Bearish.
    """
    ticker = yf.Ticker(ticker_symbol)
    news_items = ticker.news if hasattr(ticker, "news") and ticker.news else []

    if not news_items:
        return {
            "overall_sentiment": "Neutral 🟡",
            "average_polarity": 0.0,
            "bullish_pct": 0.0,
            "bearish_pct": 0.0,
            "neutral_pct": 100.0,
            "articles_table": pd.DataFrame(),
        }

    articles = []
    polarity_scores = []

    for item in news_items:
        title = item.get("title", "") if isinstance(item, dict) else getattr(item, "title", "")
        publisher = item.get("publisher", "Unknown") if isinstance(item, dict) else getattr(item, "publisher", "Unknown")
        link = item.get("link", "#") if isinstance(item, dict) else getattr(item, "link", "#")

        if not title:
            continue

        polarity = calculate_simple_polarity(title)
        polarity_scores.append(polarity)

        if polarity > 0.05:
            label = "Bullish 🟢"
        elif polarity < -0.05:
            label = "Bearish 🔴"
        else:
            label = "Neutral 🟡"

        articles.append({
            "Headline": title,
            "Publisher": publisher,
            "Polarity Score": round(polarity, 3),
            "Sentiment": label,
            "Link": link,
        })

    df_articles = pd.DataFrame(articles)

    if polarity_scores:
        avg_polarity = sum(polarity_scores) / len(polarity_scores)
        total = len(polarity_scores)
        bull_count = sum(1 for p in polarity_scores if p > 0.05)
        bear_count = sum(1 for p in polarity_scores if p < -0.05)
        neu_count = total - (bull_count + bear_count)

        if avg_polarity > 0.05:
            overall = "Bullish 🟢"
        elif avg_polarity < -0.05:
            overall = "Bearish 🔴"
        else:
            overall = "Neutral 🟡"

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


if __name__ == "__main__":
    test_ticker = "AAPL"
    print(f"--- Testing Sentiment Engine for {test_ticker} ---")
    res = fetch_and_analyze_news_sentiment(test_ticker)
    print("Overall Sentiment:", res["overall_sentiment"])
    print("Average Polarity Score:", res["average_polarity"])
    print("Breakdown:", f"Bullish: {res['bullish_pct']}%, Bearish: {res['bearish_pct']}%, Neutral: {res['neutral_pct']}%")
    if not res["articles_table"].empty:
        print("\nHeadlines Sample:\n", res["articles_table"][["Headline", "Polarity Score", "Sentiment"]].head())