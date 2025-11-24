"""
Data source integrations for stock market information.

This module handles fetching data from:
- Yahoo Finance (via yfinance) for price history
- Google News RSS for recent news articles
"""

import yfinance as yf
import feedparser
from urllib.parse import quote_plus
from typing import Optional
from datetime import datetime


def get_price_history(ticker: str, period: str = "1mo") -> str:
    """
    Fetch historical price data using yfinance.
    
    Returns a compact textual summary suitable for LLM consumption.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        period: Time period for history
            Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            
    Returns:
        str: Formatted price history summary
        
    Raises:
        ValueError: If ticker is invalid or no data is found
    """
    try:
        print(f"[DEBUG] Fetching price data for {ticker} (period={period})")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return f"No price data found for {ticker}. Please verify the ticker symbol is correct."
        
        # Get the last 7 days for detailed view
        tail = df.tail(7)
        lines = []
        
        for idx, row in tail.iterrows():
            date_str = idx.strftime("%Y-%m-%d")
            close = row["Close"]
            open_ = row["Open"]
            high = row["High"]
            low = row["Low"]
            volume = int(row["Volume"])
            
            # Calculate daily change
            daily_change = ((close - open_) / open_ * 100) if open_ > 0 else 0.0
            
            lines.append(
                f"  {date_str}: Open ${open_:.2f} | High ${high:.2f} | "
                f"Low ${low:.2f} | Close ${close:.2f} ({daily_change:+.2f}%) | "
                f"Vol {volume:,}"
            )
        
        # Calculate key metrics
        latest_close = tail["Close"].iloc[-1]
        first_close = tail["Close"].iloc[0]
        period_change = ((latest_close - first_close) / first_close * 100) if first_close > 0 else 0.0
        
        # Calculate simple moving average if we have enough data
        avg_price = tail["Close"].mean()
        
        # Get 52-week high/low if available
        full_df = stock.history(period="1y")
        if not full_df.empty:
            high_52w = full_df["Close"].max()
            low_52w = full_df["Close"].min()
            high_52w_str = f"52-week high: ${high_52w:.2f}"
            low_52w_str = f"52-week low: ${low_52w:.2f}"
        else:
            high_52w_str = "52-week high: N/A"
            low_52w_str = "52-week low: N/A"
        
        # Build summary
        header = f"""Price History for {ticker.upper()} (Period: {period})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current Metrics:
  • Latest Close: ${latest_close:.2f}
  • Period Change: {period_change:+.2f}%
  • Average Price (7d): ${avg_price:.2f}
  • {high_52w_str}
  • {low_52w_str}

📈 Recent Trading Days:
"""
        
        result = header + "\n".join(lines)
        print(f"[DEBUG] Price data fetched successfully for {ticker}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching price data for {ticker}: {str(e)}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)


def get_news(ticker: str, limit: int = 5) -> str:
    """
    Fetch recent news articles from Google News RSS feed.
    
    This is a free service that doesn't require an API key.
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of news articles to fetch (default: 5)
        
    Returns:
        str: Formatted news summary with titles, dates, and links
    """
    try:
        # Construct search query
        query = quote_plus(f"{ticker} stock news")
        url = (
            f"https://news.google.com/rss/search?"
            f"q={query}&hl=en-US&gl=US&ceid=US:en"
        )
        
        print(f"[DEBUG] Fetching news for {ticker} from Google News RSS")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return f"No recent news found for {ticker}."
        
        # Format news articles
        news_lines = [f"Recent News for {ticker.upper()}"]
        news_lines.append("━" * 60)
        news_lines.append("")
        
        for i, entry in enumerate(feed.entries[:limit], 1):
            title = getattr(entry, "title", "No title")
            link = getattr(entry, "link", "No link")
            published = getattr(entry, "published", "Date unknown")
            
            # Parse and format the date if available
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
        print(f"[DEBUG] Fetched {min(len(feed.entries), limit)} news articles for {ticker}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching news for {ticker}: {str(e)}"
        print(f"[WARNING] {error_msg}")
        # Return a non-critical error message (news is optional)
        return f"Unable to fetch news for {ticker} at this time. Error: {str(e)}"


def get_company_info(ticker: str) -> Optional[dict]:
    """
    Fetch basic company information.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        dict: Company information including name, sector, industry, etc.
        None: If information cannot be fetched
    """
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
    """
    Format market cap in human-readable format.
    
    Args:
        market_cap: Market cap in dollars
        
    Returns:
        str: Formatted string (e.g., "$2.5T", "$150B", "$3.2M")
    """
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"