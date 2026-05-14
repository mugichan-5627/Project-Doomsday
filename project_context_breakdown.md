# PROJECT DOOMSDAY: Institutional Financial Intelligence Engine
**Version**: 2.0 (Milan AI Week Hackathon Edition)
**Status**: Stabilization & Fallback Integration Phase

## 1. Project Vision
Project Doomsday is a high-fidelity, autonomous due diligence engine designed to stress-test company valuations against global "Black Swan" events. It moves beyond static DCF models by integrating real-time geopolitical intelligence, adversarial AI debates, and geographic vulnerability mapping.

## 2. Current Architecture & Folder Structure
```text
Project_Doomsday/
├── app.py                # Main Streamlit Orchestrator & UI Layer
├── valuation_engine.py   # Mathematical Core (Multi-model Valuation)
├── filing_intelligence.py# Regulatory Data Extraction (SEC/SEBI)
├── .env                  # API Credentials (Gemini, NVIDIA, Fireworks, Tavily)
└── requirements.txt      # Dependencies (yfinance, streamlit, plotly, google-genai)
```

## 3. Core Features Loaded
- **Multi-Model Valuation Router**: Automatically switches between DCF (Mature), P/BV (Financials), EV/Revenue (High Growth), and Normalized EBITDA (Cyclicals).
- **Unified AI Client**: Seamless failover between Google Gemini, NVIDIA (Llama), and Fireworks AI models.
- **Fracture Tribunal**: An adversarial debate loop where "Bear" and "Bull" agents contest specific risks, moderated by a "Black Swan Judge."
- **Geographic Fracture Mapping**: Translates abstract risks into physical lat/lon coordinates on a global map using LLM spatial reasoning.
- **Deep Intelligence Fallback**: LLM-powered web scraping (via Tavily) to fetch financial data when traditional stock APIs (yfinance) fail.
- **Chaos Slider UI**: Real-time stress testing where a user adjusts "Stress Intensity" and sees immediate waterfall destruction of value.

## 4. Current Progress & Stabilization
- **ASCII-Only Sanitization**: Purged all emojis/Unicode from the UI and logs to prevent encoding-related "fetch" errors in the Streamlit frontend.
- **Ticker Discovery**: Implemented logic to automatically find correct tickers (e.g., TSMC -> TSM) using search intelligence.
- **Institutional Styling**: Established a dark, military-grade "Monitor" aesthetic using custom CSS and Plotly.

## 5. Ongoing Problems & Limitations (For "Deeper Thinking")
*I would benefit from the following ideas/solutions from a specialized model:*

1.  **Map Performance & Logic**:
    - *Problem*: Mapping routes from "vulnerability nodes" back to "Company HQ" is currently hardcoded or simplistic. 
    - *Need*: A robust algorithm to find the "Headquarters" of any ticker and visualize a "Spoke-and-Hub" supply chain risk network that looks premium and animated.
2.  **Macro-to-Micro Linkage**:
    - *Problem*: Connecting the "World State" (VIX, Oil prices, etc.) directly to specific line items in the DCF (e.g., how exactly does a 5% rise in Brent Crude impact NVDA's WACC vs. its OpEx?).
    - *Need*: A more rigorous sensitivity matrix that maps macro variables to accounting line items.
3.  **Adversarial Rigor**:
    - *Problem*: The "Fracture Tribunal" can sometimes be too agreeable.
    - *Need*: Better prompting strategies or multi-turn logic to ensure the "Bear" agent is truly ruthless and finds "blind spots" the "Bull" agent is missing.
4.  **Local Execution Stability**:
    - *Problem*: Some users face `streamlit` pathing issues or dependency conflicts in local Windows environments.
    - *Need*: A foolproof `launch.bat` or `setup.py` that handles virtual environment creation and pathing for non-technical judges.

## 6. Immediate Roadmap
1.  **Advanced Map Visualization**: Implement animated "pulsing" red nodes for danger and supply chain paths connecting to HQ.
2.  **Search Result Caching**: Optimize Tavily usage to prevent hitting rate limits during heavy testing.
3.  **PDF Memo Export**: Add a button to generate an institutional-grade investment committee memo (PDF).
