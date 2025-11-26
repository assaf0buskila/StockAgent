"""
Main FastAPI application for the Financial AI Agent.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field

from .llm_client import ask_llm
from .analysis import analyze_ticker
# Import the new function here
from .data_sources import get_chart_data


app = FastAPI(
    title="Financial AI Agent",
    version="0.1.0",
    description="Analyze stocks using live data + a local LLM"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Mount static files for frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")
else:
    print(f"[WARNING] Static directory not found: {static_dir}")

# Custom Error Handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        html_path = static_dir / "404.html"
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content, status_code=404)
    
    if exc.status_code == 500:
        html_path = static_dir / "500.html"
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content, status_code=500)

    return HTMLResponse(
        content=f"<h1>Error {exc.status_code}</h1><p>{exc.detail}</p>",
        status_code=exc.status_code,
    )

# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for stock analysis endpoint."""
    ticker: str = Field(..., min_length=1, max_length=10)

class AnalyzeResponse(BaseModel):
    """Response model for stock analysis endpoint."""
    ticker: str
    analysis: str
    chart_data: Optional[Dict[str, Any]] = None  # <--- Added this field
    status: str = "success"

# API Endpoints
@app.get("/")
async def root():
    return RedirectResponse(url="/ui/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/test-llm")
async def test_llm():
    try:
        reply = await ask_llm("Explain what a stock ticker is in one sentence.")
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_stock(req: AnalyzeRequest):
    ticker = req.ticker.upper().strip()

    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(status_code=400, detail="Invalid ticker format.")

    try:
        # Run the AI analysis
        analysis_result = await analyze_ticker(ticker)
        
        # Fetch the Chart Data (Numbers)
        chart_data = get_chart_data(ticker)
        
        return AnalyzeResponse(
            ticker=ticker,
            analysis=analysis_result,
            chart_data=chart_data,  # <--- Return chart data to frontend
            status="success"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Data error: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Analysis failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")