"""
Stock analysis module.

This module orchestrates the data fetching and LLM analysis pipeline.
"""

from typing import Optional
from .llm_client import ask_llm
# Updated import line based on your request
from .data_sources import get_price_history, get_news, get_fundamentals, format_market_cap, get_company_info


async def analyze_ticker(ticker: str) -> str:
    """
    Analyze a stock ticker using real-time data, fundamentals, and LLM.
    
    This function:
    1. Fetches price history + technicals
    2. Fetches fundamental valuation data
    3. Fetches recent news
    4. Returns the LLM's comprehensive analysis
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        
    Returns:
        str: Formatted analysis from the LLM
    """
    print(f"[INFO] Starting analysis for {ticker}...")
    
    # Step 1: Fetch Market Data (Price + Technicals)
    print(f"[INFO] Fetching price history for {ticker}...")
    try:
        price_data = get_price_history(ticker)
        if "No price data found" in price_data:
            raise ValueError(f"No price data available for ticker {ticker}. Please verify the symbol is correct.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch price data: {e}")
        raise ValueError(f"Could not fetch price data for {ticker}: {str(e)}")
    
    # Step 2: Fetch Fundamental Data (Valuation) - NEW!
    print(f"[INFO] Fetching fundamentals for {ticker}...")
    try:
        fund_data = get_fundamentals(ticker)
    except Exception as e:
        print(f"[WARNING] Failed to fetch fundamentals: {e}")
        fund_data = "Fundamentals unavailable."

    # Step 3: Fetch News
    print(f"[INFO] Fetching news for {ticker}...")
    try:
        news_data = get_news(ticker)
    except Exception as e:
        print(f"[WARNING] Failed to fetch news: {e}")
        news_data = f"Unable to fetch news for {ticker} at this time."
    
    # Step 4: Construct the Analysis Prompt
    prompt = f"""You are a professional financial analyst. You analyze Technicals (Charts), Fundamentals (Value), and Sentiment (News).

Analyze the following data for **{ticker}** and provide a strategic report.

## 1. MARKET DATA & TECHNICALS
{price_data}

## 2. FUNDAMENTAL DATA (Valuation & Health)
{fund_data}

## 3. RECENT NEWS
{news_data}

## YOUR TASK
Write a report with these exact sections:

### 1. Executive Summary
- Give a 2-sentence overview of the situation.

### 2. Fundamental Analysis (Value)
- **Valuation:** Is the P/E Ratio high or low? (Historical avg is ~20-25).
- **Health:** Comment on Profit Margins or Growth. Is this a profitable company?

### 3. Technical Analysis (Momentum)
- **RSI:** State the value.
- **Trend:** Compare Price vs SMA 50.
- **Signals:** ONLY mention "Golden Cross" or "Death Cross" if explicitly stated in the data.

### 4. News Sentiment
- Summarize top drivers.
- Rate sentiment: Bullish/Bearish/Neutral.

### 5. Final Verdict & Recommendation
- **Verdict:** BUY, SELL, or HOLD.
- **Reasoning:** Weigh the Fundamentals (is it a good company?) against Technicals (is it a good time to buy?).
- **Risk:** Mention 1 key risk.

**Style:** Professional, concise, Markdown.
"""
    
    # Step 5: Send to LLM
    print(f"[INFO] Sending data to LLM...")
    try:
        analysis = await ask_llm(prompt)
    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")
        raise Exception(f"LLM analysis failed: {str(e)}")
    
    print(f"[SUCCESS] Analysis complete for {ticker}")
    return analysis


async def quick_sentiment(ticker: str) -> dict:
    """
    Quick sentiment analysis without full report.
    Useful for batch processing multiple tickers.
    """
    try:
        news_data = get_news(ticker, limit=3)
        
        prompt = f"""Based on these recent news headlines for {ticker}:

{news_data}

Respond with ONLY a JSON object in this exact format:
{{"sentiment": "positive|neutral|negative", "confidence": "high|medium|low"}}

No other text, just the JSON."""
        
        response = await ask_llm(prompt)
        
        # Try to parse as JSON, fallback to neutral if parsing fails
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                result = json.loads(json_str)
                result['ticker'] = ticker
                return result
            else:
                raise ValueError("No JSON found")
        except:
            return {
                "ticker": ticker,
                "sentiment": "neutral",
                "confidence": "low"
            }
    except Exception as e:
        print(f"[ERROR] Quick sentiment failed for {ticker}: {e}")
        return {
            "ticker": ticker,
            "sentiment": "unknown",
            "confidence": "none",
            "error": str(e)
        }