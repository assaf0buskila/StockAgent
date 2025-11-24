"""
Main FastAPI application for the Financial AI Agent.

This application provides an API for analyzing stock tickers using:
- Real-time price data from yfinance
- Latest news from Google News RSS
- AI-powered analysis using a local LLM (Ollama)
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from .llm_client import ask_llm
from .analysis import analyze_ticker

app = FastAPI(
    title="Financial AI Agent",
    version="0.1.0",
    description="AI-powered stock analysis using LLM and real-time data"
)

# CORS configuration
# Note: For production, replace "*" with your specific frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # More secure for local dev
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["Content-Type"],
)

# Mount static files for frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")
else:
    print(f"[WARNING] Static directory not found: {static_dir}")


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for stock analysis endpoint."""
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol (e.g., NVDA, AAPL)",
        example="NVDA"
    )


class AnalyzeResponse(BaseModel):
    """Response model for stock analysis endpoint."""
    ticker: str
    analysis: str
    status: str = "success"


class ErrorResponse(BaseModel):
    """Error response model."""
    ticker: str
    error: str
    status: str = "error"


# API Endpoints
@app.get("/")
async def root():
    """Redirect root to the UI."""
    return RedirectResponse(url="/ui/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "service": "Financial AI Agent",
        "version": "0.1.0"
    }


@app.post("/test-llm")
async def test_llm():
    """
    Test endpoint to verify LLM connectivity.
    
    Returns a simple response from the LLM to ensure it's working.
    """
    try:
        reply = await ask_llm("Explain what a stock ticker is in one sentence.")
        return {
            "status": "success",
            "reply": reply
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service unavailable: {str(e)}"
        )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_stock(req: AnalyzeRequest):
    """
    Analyze a stock ticker using AI.
    
    This endpoint:
    1. Fetches recent price history from yfinance
    2. Retrieves latest news from Google News
    3. Sends data to LLM for analysis
    4. Returns comprehensive analysis with sentiment and recommendations
    
    Args:
        req: AnalyzeRequest containing the ticker symbol
        
    Returns:
        AnalyzeResponse with analysis results
        
    Raises:
        HTTPException: If analysis fails or ticker is invalid
    """
    ticker = req.ticker.upper().strip()

    # Validate ticker format (basic validation)
    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker format. Please provide a valid stock symbol (e.g., NVDA, AAPL)."
        )

    try:
        # Run the analysis
        analysis_result = await analyze_ticker(ticker)
        
        return AnalyzeResponse(
            ticker=ticker,
            analysis=analysis_result,
            status="success"
        )
        
    except ValueError as e:
        # Handle data fetching errors (no data found, etc.)
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for ticker {ticker}: {str(e)}"
        )
        
    except Exception as e:
        # Handle unexpected errors
        print(f"[ERROR] Analysis failed for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=(
                f"Analysis pipeline failed for {ticker}. "
                "Please check:\n"
                "1. yfinance is working correctly\n"
                "2. Google News RSS is accessible\n"
                "3. Ollama/LLM service is running\n"
                f"Error: {str(e)}"
            )
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 50)
    print("🚀 Financial AI Agent Starting...")
    print("=" * 50)
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🎨 Frontend UI: http://localhost:8000/ui/index.html")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )