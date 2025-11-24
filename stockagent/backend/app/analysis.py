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
    prompt = f"""You are a senior financial analyst with expertise in equity research and market sentiment analysis.

Analyze the following data for **{ticker}** and provide a comprehensive report.

## MARKET DATA
{price_data}

## RECENT NEWS
{news_data}

## YOUR TASK
Please provide a structured analysis with the following sections:

### 1. News Summary
- Summarize the 3-5 most important news items
- Focus on developments that could impact stock price

### 2. Sentiment Analysis
- Overall sentiment: Positive / Neutral / Negative
- Explain the reasoning based on news content
- Note any divergence between news sentiment and price action

### 3. Price Action Context
- Describe recent price trends
- Correlate specific news events to price movements if apparent
- Identify any notable patterns or anomalies

### 4. Short-Term Outlook
- Provide a recommendation: Buy / Hold / Sell
- Base this on the short-term data provided (days to weeks)
- List 2-3 key risk factors to monitor

### 5. Important Disclaimer
- Note that this analysis is for informational purposes only
- Not financial advice; investors should do their own research

**Format your response in clear Markdown with headers and bullet points.**
"""
    
    # Step 3: Send to LLM for analysis
    print(f"[INFO] Sending data to LLM (Llama 3.1)...")
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
    
    This is a lighter-weight version that returns just sentiment.
    Useful for batch processing multiple tickers.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        dict: Contains 'ticker', 'sentiment', 'confidence'
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
            result = json.loads(response.strip())
            result['ticker'] = ticker
            return result
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