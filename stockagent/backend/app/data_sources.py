"""
Data source integrations for stock market information.

This module handles fetching data from:
- Yahoo Finance (via yfinance) for price history
- Google News RSS for recent news articles
"""

import yfinance as yf
import pandas as pd
import feedparser
from urllib.parse import quote_plus
from typing import Optional, Dict, List, Any
from datetime import datetime


def get_price_history(ticker: str, period: str = "1mo") -> str:
    """
    Fetch historical price data and calculate technical indicators.
    """
    try:
        print(f"[DEBUG] Fetching price data for {ticker}")
        
        # 1. Fetch 1 Year of data (Approx 252 trading days)
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty:
            return f"No price data found for {ticker}. Please verify the ticker symbol is correct."

        # ---------------------------------------------------------
        # 2. Calculate Technical Indicators
        # ---------------------------------------------------------
        
        # Calculate RSI (14-day)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate SMAs 
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # Get the latest values
        latest = df.iloc[-1]
        current_price = latest['Close']
        current_rsi = latest['RSI']
        sma_50 = latest['SMA_50']
        sma_200 = latest['SMA_200']

        # Determine RSI Status
        rsi_status = "Neutral"
        if pd.notna(current_rsi):
            if current_rsi > 70: rsi_status = "Overbought (High risk of pullback)"
            elif current_rsi < 30: rsi_status = "Oversold (Potential buying opportunity)"

        # Determine Trend
        trend = "Neutral"
        
        if pd.notna(sma_50) and pd.notna(sma_200):
            if current_price > sma_50 and current_price > sma_200:
                trend = "Strong Uptrend (Bullish)"
                if sma_50 > sma_200:
                    trend += " | Golden Cross Active 🟢"
            elif current_price < sma_50 and current_price < sma_200:
                trend = "Strong Downtrend (Bearish)"
                if sma_50 < sma_200:
                    trend += " | Death Cross Active 🔴"
        else:
            trend = "Insufficient data for Long-Term Trend"

        # ---------------------------------------------------------
        # 3. Format the Output
        # ---------------------------------------------------------

        tech_summary = f"""
🛠️ TECHNICAL ANALYSIS (Automated):
  • RSI (14-day): {current_rsi:.2f} → {rsi_status}
  • SMA 50: ${sma_50:.2f}
  • SMA 200: ${sma_200:.2f}
  • Trend Signal: {trend}
"""
        
        tail = df.tail(7)
        lines = []
        for idx, row in tail.iterrows():
            date_str = idx.strftime("%Y-%m-%d")
            close = row["Close"]
            daily_change = ((close - row["Open"]) / row["Open"] * 100) if row["Open"] > 0 else 0.0
            
            lines.append(
                f"  {date_str}: Close ${close:.2f} ({daily_change:+.2f}%) | RSI: {row['RSI']:.1f}"
            )
        
        high_52w = df["Close"].max()
        low_52w = df["Close"].min()

        final_output = f"""Price History & Technicals for {ticker.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{tech_summary}
📊 Market Metrics:
  • Current Price: ${current_price:.2f}
  • 52-Week Range: ${low_52w:.2f} - ${high_52w:.2f}

📈 Recent Trading Days:
""" + "\n".join(lines)

        print(f"[DEBUG] Technicals calculated successfully for {ticker}")
        return final_output
        
    except Exception as e:
        error_msg = f"Error fetching price data for {ticker}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)


def get_news(ticker: str, limit: int = 5) -> str:
    """Fetch recent news articles from Google News RSS feed."""
    try:
        query = quote_plus(f"{ticker} stock news")
        url = (
            f"https://news.google.com/rss/search?"
            f"q={query}&hl=en-US&gl=US&ceid=US:en"
        )
        
        print(f"[DEBUG] Fetching news for {ticker} from Google News RSS")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return f"No recent news found for {ticker}."
        
        news_lines = [f"Recent News for {ticker.upper()}"]
        news_lines.append("━" * 60)
        news_lines.append("")
        
        for i, entry in enumerate(feed.entries[:limit], 1):
            title = getattr(entry, "title", "No title")
            link = getattr(entry, "link", "No link")
            published = getattr(entry, "published", "Date unknown")
            
            try:
                pub_date = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
                published_formatted = pub_date.strftime("%B %d, %Y at %H:%M")
            except:
                published_formatted = published
            
            news_lines.append(f"{i}. {title}")
            news_lines.append(f"   📅 Published: {published_formatted}")
            news_lines.append(f"   🔗 {link}")
            news_lines.append("")
        
        result = "\n".join(news_lines)
        return result
        
    except Exception as e:
        error_msg = f"Error fetching news for {ticker}: {str(e)}"
        print(f"[WARNING] {error_msg}")
        return f"Unable to fetch news for {ticker} at this time. Error: {str(e)}"


def get_company_info(ticker: str) -> Optional[dict]:
    """Fetch basic company information."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "description": info.get("longBusinessSummary", "No description available")[:300] + "..."
        }
    except Exception as e:
        print(f"[WARNING] Could not fetch company info for {ticker}: {e}")
        return None


def format_market_cap(market_cap: int) -> str:
    """Format market cap in human-readable format."""
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"


def get_fundamentals(ticker: str) -> str:
    """Fetch key fundamental metrics (P/E, Margins, Growth)."""
    try:
        print(f"[DEBUG] Fetching fundamentals for {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        pe = info.get('trailingPE')
        f_pe = info.get('forwardPE')
        market_cap = info.get('marketCap', 0)
        profit_margin = info.get('profitMargins', 0)
        revenue_growth = info.get('revenueGrowth', 0)
        
        if market_cap >= 1_000_000_000_000:
            cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
        elif market_cap >= 1_000_000_000:
            cap_str = f"${market_cap / 1_000_000_000:.2f}B"
        elif market_cap >= 1_000_000:
            cap_str = f"${market_cap / 1_000_000:.2f}M"
        else:
            cap_str = "N/A"

        pe_str = f"{pe:.2f}" if pe is not None else "N/A"
        f_pe_str = f"{f_pe:.2f}" if f_pe is not None else "N/A"
        margin_str = f"{profit_margin * 100:.2f}%" if profit_margin is not None else "N/A"
        growth_str = f"{revenue_growth * 100:.2f}%" if revenue_growth is not None else "N/A"

        result = f"""
🏢 FUNDAMENTAL ANALYSIS:
  • Market Cap: {cap_str}
  • P/E Ratio: {pe_str} (Forward P/E: {f_pe_str})
  • Profit Margin: {margin_str}
  • Revenue Growth: {growth_str}
"""
        return result
        
    except Exception as e:
        print(f"[WARNING] Could not fetch fundamentals for {ticker}: {e}")
        return "Fundamentals: Data unavailable."

# --- NEW FUNCTION FOR CHARTS ---
def get_chart_data(ticker: str, period: str = "1y") -> dict:
    """
    Fetch raw price data for plotting.
    Returns a dictionary of lists: {dates: [], open: [], high: [], low: [], close: []}
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return {}
            
        # Format for Plotly (Candlestick chart needs Open, High, Low, Close)
        return {
            "dates": df.index.strftime('%Y-%m-%d').tolist(),
            "open": df["Open"].tolist(),
            "high": df["High"].tolist(),
            "low": df["Low"].tolist(),
            "close": df["Close"].tolist(),
        }
    except Exception as e:
        print(f"[ERROR] Could not fetch chart data: {e}")
        return {}