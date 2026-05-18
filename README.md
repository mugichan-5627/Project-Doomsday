# Project Doomsday

**Multi-Agent Black Swan Stress-Testing Engine**

An institutional-grade financial intelligence engine that stress-tests company valuations against global Black Swan events using a multi-agent AI swarm, adversarial debate architecture, and contagion propagation modeling.

## What It Does

Enter any stock ticker. In 60 seconds, the system:
- Deploys 5 AI agents across geopolitical, supply chain, financial, regulatory, and technology domains
- Runs adversarial Bear/Bull/Judge debates to validate each risk
- Maps threats geographically with convergence lines to company HQ
- Computes distressed valuations using 5-path methodology routing
- Models contagion cascades showing second/third-order propagation effects
- Displays full calculation transparency — no black boxes

## Tech Stack

- **AI Engine:** Google Gemini 2.0 Flash (with NVIDIA NIM / Fireworks AI failover)
- **Real-Time Search:** Tavily API
- **Financial Data:** yfinance
- **Frontend:** Streamlit
- **Visualization:** Plotly (maps, waterfall charts)
- **Markets Supported:** US, India (NSE/BSE), Global equities

## Setup

### Option 1: Use the deployed app
Visit the live dashboard: **[https://project-doomsday.streamlit.app/](https://project-doomsday.streamlit.app/)**

### Option 2: Run locally (Supports Concurrent UI & REST API)
1. Clone this repo
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from the template:
   ```env
   GOOGLE_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   NVIDIA_API_KEY=optional_failover_key
   FIREWORKS_API_KEY=optional_failover_key
   ```
4. Run the concurrent startup script:
   - **Windows:** Double-click `run.bat` (launches Streamlit on Port 8501 and uvicorn FastAPI server on Port 8000 in separate windows)
   - **Unix/Mac:** Run `bash run.sh`

### 🔮 Forecasting Track API Endpoint
For the hackathon's forecasting track evaluation harness, Project Doomsday exposes a high-performance, programmatically queryable **OpenAI-Compatible REST API**.

- **Endpoint:** `POST http://localhost:8000/v1/chat/completions`
- **Request Format:** Standard OpenAI Chat Completions payload
- **Capabilities:** Automatically extracts the target ticker (e.g. `AAPL`) and crisis stress intensity (e.g. `0.8` or `80%`) from unstructured conversational prompts, runs the complete multi-agent tribunal swarm, and responds with a premium stressed valuation executive Markdown report inside standard OpenAI choice structures.

#### Request Example (cURL)
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doomsday-swarm",
    "messages": [
      {"role": "user", "content": "Analyze AAPL with 0.85 extreme stress regime"}
    ]
  }'
```

#### Programmatic Verification Test
We have provided a robust compliance test script to instantly verify the REST API without manual configuration:
```bash
python scratch/verify_api.py
```

### Getting API Keys (Free)
- **Google AI Studio (Gemini):** https://ai.google.dev
- **NVIDIA NIM:** https://build.nvidia.com
- **Fireworks AI:** https://fireworks.ai
- **Tavily (Optional):** https://tavily.com (Analysis works without this using fallback news modeling).

## Features

- Multi-agent adversarial risk validation (Bear/Bull/Judge tribunal)
- 5-path valuation routing (Financial, High-Growth, Mature DCF, Cyclical, Fallback)
- Global fracture map with geographic vulnerability convergence
- Contagion cascade modeling (second/third/fourth-order effects)
- Real-time chaos slider (stress-test without re-running AI)
- Full valuation transparency panel (every formula, every number)
- Supports US + Indian + Global tickers with auto currency conversion

## Built For

Milan AI Week Hackathon 2025
