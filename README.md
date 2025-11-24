# StockAgent – Financial AI Research Assistant

StockAgent is a **local financial research agent** that lets you analyze stock tickers using:

- **Real-time market data** from Yahoo Finance (`yfinance`)
- **Recent news** from Google News RSS feeds
- A **local LLM (Ollama)** for smart, narrative analysis and sentiment

The backend is built with **FastAPI**, and the frontend is a single HTML page served as static files.

---

## Features

- 🔎 Analyze a single ticker with one click (e.g. `NVDA`, `AAPL`)
- 📊 Fetch recent **price history** via `yfinance`
- 📰 Get the latest **news headlines** via Google News RSS
- 🧠 Use a local **Ollama** model to:
  - Summarize market context
  - Infer sentiment (bullish/bearish/neutral)
  - Suggest possible risks and opportunities
- 🌐 Simple web UI (dark theme, one-page app)
- 🧪 `/health` and `/test-llm` endpoints to debug your setup

---

## Project Structure

```text
stockagent/
├─ backend/
│  └─ app/
│     ├─ __init__.py              # Marks this as a Python package
│     ├─ main.py                  # FastAPI app, routes, models, startup logs
│     ├─ analysis.py              # Orchestrates data fetching + LLM analysis
│     ├─ data_sources.py          # yfinance + Google News RSS helpers
│     ├─ llm_client.py            # HTTP client for talking to Ollama
│     ├─ config.py                # Pydantic Settings (.env, timeouts, etc.)
│     ├─ static/
│     │  └─ index.html            # Frontend UI (HTML + CSS + JS)
│     ├─ .env.example             # Example configuration for local dev
│     └─ .gitignore               # Ignore venv, .env, __pycache__, etc.
├─ requirements.txt               # Python dependencies
└─ run.py                         # Convenience script to launch uvicorn
```
## Setup Instructions:

Follow these steps to run the project locally:

1. Install Python

Use Python 3.10+.

2. Install Ollama

Download from: https://ollama.com/

Then pull the required model:

ollama pull llama3.2:3b

3. Install project dependencies

Run this inside the root project folder:

pip install -r requirements.txt

4. Run the application

From inside the stockagent directory:

python run.py


After running the server, open the UI:

http://localhost:8000/ui/index.html

## 🧪 API Overview
GET /health

Returns service status.

POST /test-llm

Tests the LLM connection and prints model response.

POST /analyze

Analyzes a ticker using data + news + LLM.

Example:

{
  "ticker": "NVDA"
}

## 🎨 Frontend (index.html)

The UI includes:

Input field for stock ticker

Button to run analysis

Display sections for:

LLM summary

Sentiment

Price history

Latest news

Raw JSON output

The UI lives at:

backend/app/static/index.html
