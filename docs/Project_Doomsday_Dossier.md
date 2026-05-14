# ☣️ PROJECT DOOMSDAY: TECHNICAL DOSSIER
**Date**: May 12, 2026  
**Status**: Alpha (Swarm Core Active)  
**Target**: Milan AI Week Hackathon

## 1. PROJECT ORIGIN & MISSION
Project Doomsday was conceived as a "Chaos-Driven" Financial Intelligence engine. Unlike traditional models that look for "upside," Doomsday is a "Stress-Testing Swarm" that proactively identifies global "Fracture Points" (geopolitical, supply chain, and macro) to simulate the catastrophic failure of a company's valuation.

**The Goal**: To provide Private Equity and Institutional investors with a "Worst Case" interactive map and a distressed valuation (Vulture-DCF).

## 2. ARCHITECTURAL SWARM (6-AGENT MODEL)
The project utilizes a multi-agent orchestration pattern where each agent has a specific "Chaos Objective":
1.  **Global Sentinel**: (ACTIVE) The intelligence hunter. Scans transcripts and news via Tavily, anchored by the Geopolitical Risk Index (GPR).
2.  **Logistics Saboteur**: (ACTIVE) The geographic specialist. Converts Sentinel's text risks into GPS coordinates (Fracture Nodes).
3.  **Vulture Architect**: (IN-DEV) The math engine. Performs distressed DCF calculations with Model Fracture guardrails.
4.  **Signal Triangulator**: Correlates sentiment across diverse institutional domains.
5.  **Sentiment Analyst**: Detects "Fear Entropy" in earnings calls.
6.  **Deal Champion**: Synthesizes all data into a final Investment Committee (IC) memo.

## 3. TECH STACK & INTEGRATIONS
- **LLM Engine**: Google Gemini (Auto-scaling: tries 2.5 Flash, 3.1 Flash, and 1.5 Pro).
- **SDK**: `google-genai` (v1 Stable).
- **Intelligence**: Tavily Search API (Institutional filter).
- **Market Data**: `yfinance` (Ticker-agnostic for US & Indian markets).
- **Visualization**: Streamlit + Plotly (Interactive Global Scatter Geo).
- **Security**: Hybrid Auth (Supports both ADC and API Keys via `.env`).

## 4. CURRENT IMPLEMENTATION STATUS
- [x] **Global Sentinel**: Now "Macro-Aware." It first samples the global "Geopolitical Pulse" (GPR/VIX) before analyzing the specific ticker.
- [x] **Logistics Saboteur**: Maps high-level risks to physical infrastructure (Ports, Cities, Factories) with exact Lat/Lon coordinates.
- [x] **Fracture Map UI**: A dark-themed Streamlit dashboard with pulsing vulnerability nodes.
- [x] **Universal Ticker Support**: Hardened logic for both US (MSFT) and India (RELIANCE.NS).

## 5. RECENT TECHNICAL HURDLES & SOLUTIONS
- **Auth Crisis**: Navigated the transition from Vertex AI (Enterprise ADC) to AI Studio (API Key) to bypass organization security constraints.
- **SDK Deprecation**: Successfully migrated from `google-generativeai` to the brand-new `google-genai` library.
- **Quota/Model 404s**: Implemented a "Brute-Force Model Hunter" in `sentinel.py` that automatically scans the user's account for the best available Gemini model, resolving 404/429 errors autonomously.
- **JSON Formatting**: Built a normalization layer in the frontend to handle both List and Dictionary outputs from the LLM swarm.

## 6. NEXT OBJECTIVES
1.  **Vulture-DCF**: Finalize the core valuation logic that takes "Chaos Factors" and produces a distressed Fair Value.
2.  **The Chaos Slider**: Connect the UI slider to the DCF engine to allow real-time "What-If" stress testing.
3.  **Institutional Memo**: Auto-generate the "IC Report" for the final Hackathon submission.
