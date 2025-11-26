# StockAgent – AI Financial Analyst 📈

**StockAgent** is a professional-grade local research assistant that combines **Real-time Data**, **Technical Analysis**, and **LLM reasoning** to generate institutional-quality stock reports.

Unlike basic wrappers, StockAgent uses **Pandas** to calculate its own indicators (RSI, SMA, Crosses) and **Ollama** to synthesize the data into a strategic verdict (BUY/SELL/HOLD).

---

## 🚀 Key Features

### 🧠 The Brains (Backend)
- **Deep Market Data:** Fetches real-time price history via `yfinance`.
- **Technical Analysis Engine:**
  - Auto-calculates **RSI (14-day)**.
  - Tracks **SMA 50** & **SMA 200**.
  - Detects **Golden Crosses** 🟢 and **Death Crosses** 🔴 automatically.
- **Fundamental Analysis:** Checks **P/E Ratios**, **Market Cap**, and **Profit Margins** to assess value.
- **Sentiment Analysis:** Scrapes Google News RSS to gauge market mood.

### 🎨 The Looks (Frontend)
- **Interactive Charts:** Full candlestick charts powered by **Plotly.js**.
- **Modern UI:** "Glassmorphism" design with a clean, fintech aesthetic.
- **Verdict System:** Color-coded badges (BUY/SELL/HOLD) based on AI logic.
- **Smart Feedback:** Loading states that keep the user engaged.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Pandas, Yfinance
- **AI:** Ollama (running Llama 3.2 locally)
- **Frontend:** HTML5, CSS3, Plotly.js (No React/Vue build step required)

---

## 📂 Project Structure

```text
stockagent/
├─ backend/
│  └─ app/
│     ├─ main.py            # FastAPI entry point & routes
│     ├─ analysis.py        # Logic: Combines Tech + Fund + News for LLM
│     ├─ data_sources.py    # math: Calculates RSI, SMA, and fetches Chart Data
│     ├─ llm_client.py      # Connects to your local Ollama instance
│     └─ static/
│        └─ index.html      # The Modern UI (Glassmorphism + Charts)
├─ requirements.txt         # Dependencies (fastapi, pandas, yfinance, etc.)
└─ run.py                   # Launcher script