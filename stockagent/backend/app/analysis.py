"""
Stock analysis module.

This module orchestrates the data fetching and LLM analysis pipeline.
"""

from typing import Optional
from .llm_client import ask_llm
from .data_sources import get_price_history, get_news


async def analyze_ticker(ticker: str) -> str:
    """
    Analyze a stock ticker using real-time data and LLM.
    
    This function:
    1. Fetches price history from yfinance
    2. Fetches recent news from Google News RSS
    3. Constructs a detailed prompt for the LLM
    4. Returns the LLM's analysis
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        
    Returns:
        str: Formatted analysis from the LLM
        
    Raises:
        ValueError: If no data can be fetched for the ticker
        Exception: If LLM analysis fails
    """
    print(f"[INFO] Starting analysis for {ticker}...")
    
    # Step 1: Fetch real market data
    print(f"[INFO] Fetching price history for {ticker}...")
    try:
        price_data = get_price_history(ticker)
    except Exception as e:
        print(f"[ERROR] Failed to fetch price data: {e}")
        raise ValueError(f"Could not fetch price data for {ticker}: {str(e)}")
    
    # Check if we got valid data
    if "No price data found" in price_data:
        raise ValueError(f"No price data available for ticker {ticker}. Please verify the symbol is correct.")
    
    print(f"[INFO] Fetching news for {ticker}...")
    try:
        news_data = get_news(ticker)
    except Exception as e:
        print(f"[WARNING] Failed to fetch news: {e}")
        news_data = f"Unable to fetch news for {ticker} at this time."
    
    # Step 2: Construct the analysis prompt
    # UPDATED: Added specific instructions for Technical Analysis
    prompt = f"""You are a professional financial analyst using a mix of fundamental news and technical indicators.

Analyze the following data for **{ticker}** and provide a structured report.

MARKET DATA & TECHNICALS
{price_data}

RECENT NEWS
{news_data}

YOUR TASK
Provide a report with these exact sections:

1. Executive Summary
 Give a 2-sentence overview of the current situation.

2. Technical Analysis
RSI: State the value.
Trend: Compare Price vs SMA 50.
Signals:ONLY mention a "Golden Cross" or "Death Cross" if the "Trend Signal" data explicitly says "Active". Do not infer this yourself.

3. News Sentiment
  Summarize the top news drivers.
  Rate sentiment as Bullish, Bearish, or Neutral.

4. Outlook & Recommendation
Verdict: BUY, SELL, or HOLD.
Reasoning: Combine the technicals (RSI/Trends) with the news sentiment.
Risk: Mention 1 key risk factor.

Style: Professional, concise, using Markdown formatting.
"""
    
    # Step 3: Send to LLM for analysis
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
            # Find the start and end of the JSON object in case LLM adds extra text
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