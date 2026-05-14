Project Doomsday - Complete Analysis & Fix
I've reviewed your entire codebase thoroughly. Let me break down the issues and provide you with a completely fixed and enhanced app.py that addresses:

Smoothness issues (state management, rerun logic, error handling)
Map visualization (animated curved lines converging to HQ, proper color-coded nodes)
General stability (missing CSS classes, broken references, layout issues)
Let me ask a few clarifying questions first, but I'll also provide the fix assuming standard answers:

Quick Questions (but I'll proceed with assumptions):
Do you have valuation_engine.py and filing_intelligence.py working? I'll assume yes and won't modify those.
Which APIs do you actually have active? I'll keep the fallback chain (Gemini → NVIDIA → Fireworks).
Are you running this locally or deploying to Streamlit Cloud? I'll optimize for local.
Here's your completely fixed app.py:
# app.py
"""
PROJECT DOOMSDAY - Complete Streamlit Application
Fixed: Map rendering, smooth interactions, curved supply chain lines,
       animated HQ convergence, state management, CSS consistency
Version: 3.0 (Stabilized)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import os
import time
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Safe imports with error handling
try:
    from filing_intelligence import UnifiedFilingEngine, SECEdgarEngine, SEBIFilingEngine
except ImportError:
    UnifiedFilingEngine = None
    SECEdgarEngine = None
    SEBIFilingEngine = None

try:
    from valuation_engine import ValuationRouter, CompanyProfile, CompanyType, classify_company, StressedValuation
except ImportError:
    ValuationRouter = None
    CompanyProfile = None
    CompanyType = None
    StressedValuation = None

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG - Must be first Streamlit command
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="PROJECT DOOMSDAY",
    page_icon="☣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

@dataclass
class WorldState:
    timestamp: str
    vix: float = 20.0
    vix_trend: str = "stable"
    dxy: float = 104.0
    us_10y_yield: float = 4.5
    oil_brent: float = 80.0
    gold: float = 2400.0
    fear_level: str = "CAUTIOUS"
    active_crises: List[Dict] = field(default_factory=list)

@dataclass
class FractureNode:
    node_id: str
    risk_id: str
    latitude: float
    longitude: float
    label: str
    description: str
    category: str
    severity: float
    probability: float
    threat_level: str
    affected_assets: List[str] = field(default_factory=list)
    time_horizon: str = "6_months"
    revenue_at_risk_pct: float = 5.0
    connected_to: List[str] = field(default_factory=list)

@dataclass
class DebateMessage:
    role: str
    content: str
    round_number: int
    confidence: float = 0.5

@dataclass
class RiskVerdict:
    risk_id: str
    risk_description: str
    domain: str
    severity_score: float
    probability: float
    time_horizon: str
    bull_summary: str
    bear_summary: str
    judge_reasoning: str
    geographic_nexus: str
    revenue_at_risk_pct: float
    debate_transcript: List[DebateMessage] = field(default_factory=list)

@dataclass
class FallbackValuation:
    """Fallback valuation if valuation_engine is not available."""
    current_price: float = 0.0
    base_fair_value: float = 0.0
    distressed_value: float = 0.0
    downside_pct: float = 0.0
    valuation_method: str = "Simplified DCF"
    base_wacc: float = 10.0
    stressed_wacc: float = 15.0
    revenue_haircut: float = 10.0
    margin_compression_bps: float = 200.0
    waterfall_data: List[Dict] = field(default_factory=list)
    method_values: Dict = field(default_factory=dict)

@dataclass
class FallbackProfile:
    """Fallback company profile if valuation_engine is not available."""
    ticker: str = ""
    name: str = ""
    sector: str = "Unknown"
    industry: str = "Unknown"
    market_cap: float = 0.0
    revenue: float = 0.0
    ebitda: float = 0.0
    ebitda_margin: float = 0.0
    net_income: float = 0.0
    net_debt: float = 0.0
    total_debt: float = 0.0
    cash: float = 0.0
    shares_outstanding: float = 0.0
    current_price: float = 0.0
    revenue_growth: float = 0.0
    beta: float = 1.0
    roe: float = 0.0
    pe_ratio: float = 0.0
    company_type: str = "mature"

# ═══════════════════════════════════════════════════════════════
# CSS - Dark military/monitor aesthetic (COMPLETE)
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* === BASE THEME === */
    .stApp {
        background-color: #080b10;
        color: #c8d6e5;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0c1018;
        border-right: 1px solid #1a2538;
    }
    
    /* === HEADER === */
    .header-container {
        background: linear-gradient(135deg, #0c1018 0%, #14080a 50%, #0c1018 100%);
        border: 1px solid #2a1520;
        border-radius: 6px;
        padding: 14px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(255, 23, 68, 0.05);
    }
    
    .header-title {
        font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
        font-size: 1.3em;
        color: #ff3344;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(255, 51, 68, 0.4);
    }
    
    .header-status {
        display: flex;
        gap: 10px;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7em;
    }
    
    .badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8em;
        padding: 4px 10px;
        border-radius: 10px;
        border: 1px solid;
        letter-spacing: 0.5px;
    }
    
    .badge-active {
        border-color: #00e676;
        color: #00e676;
        background: rgba(0, 230, 118, 0.08);
    }
    
    .badge-threat {
        border-color: #ff6d00;
        color: #ff6d00;
        background: rgba(255, 109, 0, 0.08);
        animation: threat-pulse 2.5s ease-in-out infinite;
    }
    
    @keyframes threat-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* === METRICS ROW === */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: #0c1018;
        border: 1px solid #1a2538;
        border-radius: 8px;
        padding: 18px 12px;
        text-align: center;
        transition: border-color 0.3s;
    }
    
    .metric-card:hover {
        border-color: #2a4058;
    }
    
    .m-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5em;
        font-weight: 700;
        margin-bottom: 4px;
        color: #eceff1;
    }
    
    .m-label {
        font-size: 0.65em;
        color: #5a6f82;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Value color classes */
    .val-blue { color: #448aff !important; }
    .val-red { color: #ff1744 !important; }
    .val-orange { color: #ff6d00 !important; }
    .val-yellow { color: #ffd600 !important; }
    .val-green { color: #00e676 !important; }
    .val-white { color: #eceff1 !important; }
    .val-critical { color: #ff1744 !important; animation: threat-pulse 1.5s infinite; }
    
    /* === SECTION HEADERS === */
    .section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
        color: #78909c;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 28px 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1a2538;
    }
    
    /* === DEBATE PANEL === */
    .debate-container {
        background: #0a0e14;
        border: 1px solid #1a2538;
        border-radius: 8px;
        padding: 16px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .msg-bear {
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.82em;
        line-height: 1.6;
        border-left: 3px solid #ff1744;
        background: rgba(255, 23, 68, 0.06);
    }
    
    .msg-bull {
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.82em;
        line-height: 1.6;
        border-left: 3px solid #00e676;
        background: rgba(0, 230, 118, 0.06);
    }
    
    .msg-judge {
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.82em;
        line-height: 1.6;
        border-left: 3px solid #ffd600;
        background: rgba(255, 214, 0, 0.06);
    }
    
    /* === RISK BADGES === */
    .rbadge-critical { background: #ff1744; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.6em; font-weight: 700; text-transform: uppercase; }
    .rbadge-high { background: #ff6d00; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.6em; font-weight: 700; text-transform: uppercase; }
    .rbadge-elevated { background: #ffd600; color: black; padding: 2px 8px; border-radius: 3px; font-size: 0.6em; font-weight: 700; text-transform: uppercase; }
    .rbadge-monitoring { background: #00e676; color: black; padding: 2px 8px; border-radius: 3px; font-size: 0.6em; font-weight: 700; text-transform: uppercase; }
    
    /* === INFO PANELS === */
    .info-panel {
        background: #0c1018;
        border: 1px solid #1a2538;
        border-radius: 8px;
        padding: 16px;
    }
    
    .world-state-item {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #0f1520;
        font-size: 0.82em;
    }
    
    .ws-label { color: #5a6f82; }
    .ws-value { color: #eceff1; font-family: monospace; }
    
    .ws-metric {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 0.8em;
        color: #78909c;
        border-bottom: 1px solid #0f1520;
    }
    
    .ws-metric span {
        color: #eceff1;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* === WORLD STATE CARD === */
    .world-state-card {
        background: #0c1018;
        border: 1px solid #1a2538;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    
    /* === LANDING PAGE === */
    .landing-hero {
        text-align: center;
        padding: 80px 40px;
        color: #5a6f82;
    }
    
    .hero-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2em;
        color: #ff3344;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-bottom: 20px;
        text-shadow: 0 0 20px rgba(255, 51, 68, 0.3);
    }
    
    .hero-subtitle {
        font-size: 0.9em;
        color: #5a6f82;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.7;
    }
    
    /* === DOOM TITLE === */
    .doom-title {
        font-family: 'JetBrains Mono', monospace;
        color: #ff3344;
        letter-spacing: 2px;
    }
    
    .metric-label {
        font-size: 0.7em;
        color: #5a6f82;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4em;
        font-weight: 700;
        color: #eceff1;
    }
    
    /* === HIDE STREAMLIT DEFAULTS === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #080b10; }
    ::-webkit-scrollbar-thumb { background: #1a2538; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2a4058; }
    
    /* Fix Streamlit elements */
    .streamlit-expanderHeader {
        background: #0c1018 !important;
        border: 1px solid #1a2538 !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid #1a2538;
        border-radius: 6px;
        background: #0a0e14;
    }
    
    .stSlider > div > div > div > div {
        background-color: #ff3344 !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# UNIFIED AI CLIENT
# ═══════════════════════════════════════════════════════════════

class UnifiedAIClient:
    """Unified client with failover: Gemini -> NVIDIA -> Fireworks."""
    
    def __init__(self):
        self.gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.nvidia_key = os.getenv("NVIDIA_API_KEY")
        self.fireworks_key = os.getenv("FIREWORKS_API_KEY")
        
        self.genai_client = None
        if self.gemini_key:
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                pass

    class ModelsWrapper:
        def __init__(self, parent):
            self.parent = parent
        def generate_content(self, model, contents, config=None):
            return self.parent.generate(model, contents, config)

    @property
    def models(self):
        return self.ModelsWrapper(self)

    def generate(self, model, contents, config=None):
        """Route to appropriate provider."""
        
        # Extract prompt text
        prompt = self._extract_prompt(contents)
        
        # Extract config params
        temp = 0.7
        max_tokens = 2048
        response_mime = None
        if config:
            if hasattr(config, 'temperature'): temp = config.temperature
            if hasattr(config, 'max_output_tokens'): max_tokens = config.max_output_tokens
            if hasattr(config, 'response_mime_type'): response_mime = config.response_mime_type
        
        # 1. Gemini Dispatch
        if "gemini" in model.lower():
            if not self.genai_client:
                raise ValueError("Gemini client not initialized")
            return self.genai_client.models.generate_content(
                model=model, contents=contents, config=config
            )
        
        # 2. OpenAI-Compatible Dispatch (NVIDIA / Fireworks)
        is_nvidia = "nvidia" in model.lower() or ("llama" in model.lower() and "fireworks" not in model.lower())
        
        if is_nvidia:
            base_url = "https://integrate.api.nvidia.com/v1"
            api_key = self.nvidia_key
        else:
            base_url = "https://api.fireworks.ai/inference/v1"
            api_key = self.fireworks_key
        
        if not api_key:
            raise ValueError(f"API Key for {model} not found.")

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        messages = [{"role": "user", "content": prompt}]
        
        # Add JSON mode if requested
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens
        }
        
        if response_mime == "application/json":
            # Some providers support response_format
            try:
                kwargs["response_format"] = {"type": "json_object"}
            except:
                pass
        
        response = client.chat.completions.create(**kwargs)
        
        class FakeResponse:
            def __init__(self, text): 
                self.text = text
        
        return FakeResponse(response.choices[0].message.content)
    
    def _extract_prompt(self, contents) -> str:
        """Extract text from various content formats."""
        if isinstance(contents, str):
            return contents
        if isinstance(contents, list):
            parts = []
            for c in contents:
                if hasattr(c, 'text'): parts.append(c.text)
                elif isinstance(c, str): parts.append(c)
                else: parts.append(str(c))
            return "\n".join(parts)
        return str(contents)


def get_ai_client():
    """Initialize unified AI client with caching."""
    if "ai_client" not in st.session_state:
        st.session_state.ai_client = UnifiedAIClient()
    return st.session_state.ai_client


def get_tavily_client():
    """Initialize Tavily client."""
    if "tavily_client" in st.session_state:
        return st.session_state.tavily_client
    
    try:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            st.error("TAVILY_API_KEY not found in .env file.")
            st.stop()
        client = TavilyClient(api_key=api_key)
        st.session_state.tavily_client = client
        return client
    except ImportError:
        st.error("tavily-python not installed. Run: pip install tavily-python")
        st.stop()


def find_best_model(client) -> str:
    """Find available model across providers."""
    
    # Priority 1: Gemini
    if client.gemini_key and client.genai_client:
        from google.genai import types
        gemini_models = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        for model in gemini_models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Respond with just the word 'ready'",
                    config=types.GenerateContentConfig(max_output_tokens=10, temperature=0)
                )
                if response and response.text:
                    return model
            except Exception:
                continue
    
    # Priority 2: NVIDIA
    if client.nvidia_key:
        nvidia_models = [
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.1-70b-instruct",
        ]
        for model in nvidia_models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Respond with just the word 'ready'"
                )
                if response and response.text:
                    return model
            except Exception:
                continue
    
    # Priority 3: Fireworks
    if client.fireworks_key:
        fireworks_models = [
            "accounts/fireworks/models/llama-v3p1-405b-instruct",
            "accounts/fireworks/models/llama-v3p1-70b-instruct",
        ]
        for model in fireworks_models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Respond with just the word 'ready'"
                )
                if response and response.text:
                    return model
            except Exception:
                continue
    
    st.error("No AI models available. Check your API keys in .env file (GOOGLE_API_KEY, NVIDIA_API_KEY, or FIREWORKS_API_KEY).")
    st.stop()


# ═══════════════════════════════════════════════════════════════
# DATA FETCHING
# ═══════════════════════════════════════════════════════════════

def fetch_world_state(tavily_client) -> WorldState:
    """Fetch real-time world state indicators."""
    import yfinance as yf
    
    ws = WorldState(timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    indicators = {
        "vix": "^VIX",
        "dxy": "DX-Y.NYB",
        "us_10y_yield": "^TNX",
        "oil_brent": "BZ=F",
        "gold": "GC=F"
    }
    
    for key, ticker_symbol in indicators.items():
        try:
            data = yf.Ticker(ticker_symbol).history(period="2d")
            if not data.empty:
                setattr(ws, key, round(float(data['Close'].iloc[-1]), 2))
        except:
            pass
    
    # VIX trend
    try:
        vix_hist = yf.Ticker("^VIX").history(period="5d")
        if len(vix_hist) >= 2:
            change = float(vix_hist['Close'].iloc[-1] - vix_hist['Close'].iloc[0])
            ws.vix_trend = "rising" if change > 2 else "falling" if change < -2 else "stable"
    except:
        pass
    
    # Fear level calculation
    score = 0
    if ws.vix >= 35: score += 3
    elif ws.vix >= 25: score += 2
    elif ws.vix >= 18: score += 1
    if ws.gold > 2500: score += 1
    if ws.oil_brent > 95: score += 1
    if ws.us_10y_yield > 5.0: score += 1
    
    ws.fear_level = "PANIC" if score >= 5 else "ANXIOUS" if score >= 3 else "CAUTIOUS" if score >= 2 else "CALM"
    
    # Active crises
    try:
        result = tavily_client.search(
            query="major global crisis geopolitical conflict economic risk 2025",
            search_depth="basic",
            max_results=5
        )
        ws.active_crises = [
            {"title": r.get("title", ""), "snippet": r.get("content", "")[:150]}
            for r in result.get("results", [])
        ]
    except:
        ws.active_crises = [{"title": "Unable to fetch live crises", "snippet": "Check Tavily API"}]
    
    return ws


def fetch_company_profile(ticker: str, ai_client=None, tavily_client=None, model: str = None):
    """Fetch company profile - tries yfinance first, then LLM fallback."""
    
    # Try ValuationRouter if available
    if ValuationRouter:
        profile = ValuationRouter.build_profile(ticker)
        if profile and profile.market_cap > 0:
            return profile
    
    # Fallback: Direct yfinance
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or info.get("marketCap", 0) == 0:
            raise ValueError("No data from yfinance")
        
        if CompanyProfile:
            # Use proper CompanyProfile if available
            profile = CompanyProfile(
                ticker=ticker,
                name=info.get("longName", info.get("shortName", ticker)),
                sector=info.get("sector", "Unknown"),
                industry=info.get("industry", "Unknown"),
                market_cap=float(info.get("marketCap", 0)),
                revenue=float(info.get("totalRevenue", 0)),
                ebitda=float(info.get("ebitda", 0)),
                net_income=float(info.get("netIncomeToCommon", 0)),
                total_debt=float(info.get("totalDebt", 0)),
                cash=float(info.get("totalCash", 0)),
                shares_outstanding=float(info.get("sharesOutstanding", 1)),
                current_price=float(info.get("currentPrice", info.get("regularMarketPrice", 0))),
                revenue_growth=float(info.get("revenueGrowth", 0) or 0),
                beta=float(info.get("beta", 1.0) or 1.0),
                roe=float(info.get("returnOnEquity", 0) or 0),
                pe_ratio=float(info.get("trailingPE", 0) or 0),
            )
            return profile
        else:
            # Use fallback profile
            profile = FallbackProfile(
                ticker=ticker,
                name=info.get("longName", info.get("shortName", ticker)),
                sector=info.get("sector", "Unknown"),
                industry=info.get("industry", "Unknown"),
                market_cap=float(info.get("marketCap", 0)),
                revenue=float(info.get("totalRevenue", 0)),
                ebitda=float(info.get("ebitda", 0)),
                ebitda_margin=float(info.get("ebitda", 0)) / max(float(info.get("totalRevenue", 1)), 1) * 100,
                net_income=float(info.get("netIncomeToCommon", 0)),
                total_debt=float(info.get("totalDebt", 0)),
                cash=float(info.get("totalCash", 0)),
                net_debt=float(info.get("totalDebt", 0)) - float(info.get("totalCash", 0)),
                shares_outstanding=float(info.get("sharesOutstanding", 1)),
                current_price=float(info.get("currentPrice", info.get("regularMarketPrice", 0))),
                revenue_growth=float(info.get("revenueGrowth", 0) or 0),
                beta=float(info.get("beta", 1.0) or 1.0),
                roe=float(info.get("returnOnEquity", 0) or 0),
                pe_ratio=float(info.get("trailingPE", 0) or 0),
            )
            return profile
    except Exception as e:
        pass
    
    # Deep search fallback
    if ai_client and tavily_client and model:
        st.info(f"YFinance failed for '{ticker}'. Initiating Deep Intelligence Search...")
        deep_data = run_deep_ticker_search(ai_client, tavily_client, model, ticker)
        if deep_data:
            if ValuationRouter:
                return ValuationRouter.build_profile_from_data(deep_data)
            else:
                return FallbackProfile(
                    ticker=deep_data.get("ticker", ticker),
                    name=deep_data.get("name", ticker),
                    sector=deep_data.get("sector", "Unknown"),
                    industry=deep_data.get("industry", "Unknown"),
                    market_cap=float(deep_data.get("market_cap", 0)),
                    revenue=float(deep_data.get("revenue", 0)),
                    ebitda=float(deep_data.get("ebitda", 0)),
                    current_price=float(deep_data.get("current_price", 0)),
                    shares_outstanding=float(deep_data.get("shares_outstanding", 1)),
                )
    
    return None


def run_deep_ticker_search(ai_client, tavily_client, model: str, ticker: str) -> Optional[Dict]:
    """Use Tavily + LLM to find live data for a ticker."""
    from google.genai import types
    
    search_query = f"financial data for {ticker} company 2024 2025: market cap, revenue, EBITDA, debt, cash, sector"
    
    try:
        search_results = tavily_client.search(query=search_query, search_depth="advanced", max_results=5)
        context = ""
        for r in search_results.get("results", []):
            context += f"\n--- {r.get('title')} ---\n{r.get('content')}\n"
        
        extraction_prompt = f"""Extract financial data for '{ticker}' from this context. Return ONLY valid JSON.

CONTEXT:
{context[:3000]}

JSON FORMAT:
{{
    "ticker": "{ticker}",
    "name": "Company Name",
    "sector": "Technology",
    "industry": "Semiconductors",
    "current_price": 145.20,
    "market_cap": 750000000000,
    "revenue": 70000000000,
    "ebitda": 35000000000,
    "net_income": 25000000000,
    "total_debt": 20000000000,
    "cash": 45000000000,
    "shares_outstanding": 5180000000,
    "company_type": "mature_tech"
}}"""
        
        config_kwargs = {"temperature": 0.1}
        if "gemini" in model.lower():
            config_kwargs["response_mime_type"] = "application/json"
            config = types.GenerateContentConfig(**config_kwargs)
        else:
            config = types.GenerateContentConfig(**config_kwargs) if hasattr(types, 'GenerateContentConfig') else None
        
        response = ai_client.models.generate_content(
            model=model,
            contents=extraction_prompt,
            config=config
        )
        
        # Parse JSON from response
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        return json.loads(text)
    except Exception as e:
        st.warning(f"Deep search parsing failed: {e}")
        return None


def calculate_valuation(profile, chaos_level: float, risk_severity: float = 5.0):
    """Calculate valuation - uses ValuationRouter if available, else simplified."""
    
    if ValuationRouter and hasattr(profile, 'company_type'):
        return ValuationRouter.value_company(profile, chaos_level, risk_severity)
    
    # Simplified fallback valuation
    current_price = getattr(profile, 'current_price', 100.0)
    revenue = getattr(profile, 'revenue', 0)
    ebitda = getattr(profile, 'ebitda', 0)
    shares = getattr(profile, 'shares_outstanding', 1)
    market_cap = getattr(profile, 'market_cap', 0)
    
    if current_price <= 0:
        current_price = market_cap / max(shares, 1)
    
    # Simple P/E based fair value
    pe = getattr(profile, 'pe_ratio', 20)
    if pe <= 0: pe = 20
    net_income = getattr(profile, 'net_income', revenue * 0.1)
    
    base_fair_value = (net_income / max(shares, 1)) * pe * 0.9  # 10% margin of safety
    if base_fair_value <= 0:
        base_fair_value = current_price * 1.1
    
    # Stress application
    revenue_haircut = chaos_level * 15 + (risk_severity / 10) * 10
    wacc_addition = chaos_level * 5 + (risk_severity / 10) * 3
    margin_compression = chaos_level * 300 + risk_severity * 50
    
    stress_multiplier = 1 - (revenue_haircut / 100) - (margin_compression / 10000)
    stress_multiplier = max(stress_multiplier, 0.3)
    
    distressed_value = base_fair_value * stress_multiplier
    downside_pct = ((distressed_value - current_price) / current_price) * 100
    
    # Waterfall data
    waterfall = [
        {"label": "Base Value", "value": base_fair_value, "type": "absolute"},
        {"label": "Revenue Stress", "value": -(base_fair_value * revenue_haircut / 100), "type": "relative"},
        {"label": "Margin Compression", "value": -(base_fair_value * margin_compression / 10000), "type": "relative"},
        {"label": "WACC Premium", "value": -(base_fair_value * wacc_addition / 100), "type": "relative"},
        {"label": "Distressed Value", "value": distressed_value, "type": "total"},
    ]
    
    return FallbackValuation(
        current_price=current_price,
        base_fair_value=round(base_fair_value, 2),
        distressed_value=round(distressed_value, 2),
        downside_pct=round(downside_pct, 1),
        base_wacc=10.0,
        stressed_wacc=10.0 + wacc_addition,
        revenue_haircut=revenue_haircut,
        margin_compression_bps=margin_compression,
        waterfall_data=waterfall,
        method_values={"P/E Based": f"${base_fair_value:.2f}", "Revenue Multiple": f"${(revenue/max(shares,1))*3:.2f}"}
    )


# ═══════════════════════════════════════════════════════════════
# INTELLIGENCE & DEBATE ENGINES
# ═══════════════════════════════════════════════════════════════

def run_enhanced_intelligence(ai_client, tavily_client, model: str, ticker: str, profile, world_state) -> List[Dict]:
    """Multi-source intelligence gathering."""
    from google.genai import types
    
    # Filing intelligence
    filing_context = ""
    if UnifiedFilingEngine:
        try:
            filing_engine = UnifiedFilingEngine(tavily_client=tavily_client)
            filing_risks, filing_source = filing_engine.extract_all_risks(ticker)
            filing_context = filing_engine.format_for_llm(filing_risks)
        except:
            filing_context = "Filing data unavailable."
    
    # Multi-domain Tavily Search
    company_name = getattr(profile, 'name', ticker)
    domains = {
        "geopolitical": f"{company_name} geopolitical risk sanctions trade war 2025",
        "supply_chain": f"{company_name} supply chain disruption shortage risk",
        "financial": f"{company_name} debt credit risk revenue decline",
        "regulatory": f"{company_name} regulation antitrust investigation 2025",
        "technology": f"{company_name} technology disruption AI competition risk"
    }
    
    news_intelligence = ""
    for domain, query in domains.items():
        try:
            result = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            domain_text = f"\n[{domain.upper()}]:\n"
            for r in result.get("results", []):
                domain_text += f"- {r.get('title', '')}: {r.get('content', '')[:200]}\n"
            news_intelligence += domain_text
        except:
            pass
    
    # LLM Synthesis
    sector = getattr(profile, 'sector', 'Unknown')
    industry = getattr(profile, 'industry', 'Unknown')
    market_cap = getattr(profile, 'market_cap', 0)
    revenue = getattr(profile, 'revenue', 0)
    
    synthesis_prompt = f"""You are an institutional risk analyst. Identify the TOP 6 most material risks for {ticker} ({company_name}).

COMPANY: {company_name} | Sector: {sector} | Industry: {industry}
Market Cap: ${market_cap/1e9:.1f}B | Revenue: ${revenue/1e9:.1f}B

WORLD STATE: VIX={world_state.vix} ({world_state.vix_trend}), Oil=${world_state.oil_brent}, Fear={world_state.fear_level}

FILING INTELLIGENCE:
{filing_context[:2000]}

NEWS INTELLIGENCE:
{news_intelligence[:3000]}

RULES:
1. Be SPECIFIC - not "competition may increase" but "AWS gaining market share in cloud"
2. Each risk needs a geographic location where it primarily manifests
3. Estimate revenue at risk percentage realistically

Respond ONLY in valid JSON:
{{
    "risks": [
        {{
            "id": "RISK_001",
            "domain": "geopolitical",
            "title": "Short title (5-8 words)",
            "description": "Detailed 2-3 sentence description with specifics",
            "evidence_source": "FILING|NEWS|BOTH",
            "severity": 7,
            "probability": 0.4,
            "geographic_nexus": "Taiwan",
            "revenue_at_risk_pct": 15.0,
            "time_horizon": "6_months"
        }}
    ]
}}"""

    try:
        config_kwargs = {"temperature": 0.4}
        if "gemini" in model.lower():
            config_kwargs["response_mime_type"] = "application/json"
        config = types.GenerateContentConfig(**config_kwargs)
        
        response = ai_client.models.generate_content(
            model=model,
            contents=synthesis_prompt,
            config=config
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        parsed = json.loads(text)
        return parsed.get("risks", [])
    except Exception as e:
        st.warning(f"Intelligence synthesis error: {e}. Using fallback risks.")
        return [
            {"id": "RISK_001", "domain": "market", "title": "Market Volatility Risk",
             "description": f"General market risk for {ticker} given current VIX at {world_state.vix}",
             "severity": 5, "probability": 0.5, "geographic_nexus": "Global",
             "revenue_at_risk_pct": 10.0, "time_horizon": "6_months"}
        ]


def run_adversarial_debate(ai_client, model: str, ticker: str, company: Dict, risks: List[Dict], world_state: WorldState) -> List[RiskVerdict]:
    """Run adversarial debate: Bull vs Bear vs Judge."""
    from google.genai import types
    
    verdicts = []
    
    for risk in risks[:6]:
        debate_transcript = []
        
        # === BEAR ===
        bear_prompt = f"""You are the BEAR ADVOCATE prosecuting a risk for {ticker}.

RISK: {json.dumps(risk, indent=2)}

Present your worst-case prosecution in 3-4 sentences. Be specific with numbers.
Include: severity estimate (1-10), financial impact (% revenue), one historical precedent.

Respond in JSON:
{{"argument": "Your prosecution", "severity_estimate": 7, "financial_impact": "15% revenue decline", "historical_precedent": "One precedent", "confidence": 0.7}}"""

        try:
            config_kwargs = {"temperature": 0.6}
            if "gemini" in model.lower():
                config_kwargs["response_mime_type"] = "application/json"
            config = types.GenerateContentConfig(**config_kwargs)
            
            bear_response = ai_client.models.generate_content(
                model=model, contents=bear_prompt, config=config
            )
            text = bear_response.text.strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json\n")
            bear_parsed = json.loads(text)
        except:
            bear_parsed = {"argument": "Risk presents material downside potential.", "severity_estimate": 5, "confidence": 0.5}
        
        debate_transcript.append(DebateMessage(
            role="bear", content=bear_parsed.get("argument", ""), 
            round_number=1, confidence=bear_parsed.get("confidence", 0.5)
        ))
        
        # === BULL ===
        bull_prompt = f"""You are the BULL ADVOCATE defending {ticker}.

RISK: {risk.get('description', '')}
BEAR ARGUES: {bear_parsed.get('argument', '')}

Defend in 3-4 sentences. Challenge evidence quality, present mitigating factors.
Concede points that are genuinely strong.

Respond in JSON:
{{"argument": "Your defense", "mitigating_factors": ["Factor 1", "Factor 2"], "confidence_in_dismissal": 0.5}}"""

        try:
            config_kwargs = {"temperature": 0.6}
            if "gemini" in model.lower():
                config_kwargs["response_mime_type"] = "application/json"
            config = types.GenerateContentConfig(**config_kwargs)
            
            bull_response = ai_client.models.generate_content(
                model=model, contents=bull_prompt, config=config
            )
            text = bull_response.text.strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json\n")
            bull_parsed = json.loads(text)
        except:
            bull_parsed = {"argument": "Company has strong fundamentals to weather this risk.", "confidence_in_dismissal": 0.5}
        
        debate_transcript.append(DebateMessage(
            role="bull", content=bull_parsed.get("argument", ""),
            round_number=1, confidence=bull_parsed.get("confidence_in_dismissal", 0.5)
        ))
        
        # === JUDGE ===
        judge_prompt = f"""You are the BLACK SWAN JUDGE for {ticker}.

RISK: {risk.get('description', '')}
BEAR: {bear_parsed.get('argument', '')} (Severity: {bear_parsed.get('severity_estimate', 5)})
BULL: {bull_parsed.get('argument', '')}
WORLD: VIX={world_state.vix}, Fear={world_state.fear_level}

Deliver verdict. Assign final severity (1-10) and probability (0-1).
8+ severity = potential >25% impairment. Most risks: 4-7.

Respond in JSON:
{{"verdict": "VALIDATED|DISMISSED|MONITORING", "final_severity": 6, "final_probability": 0.4, "reasoning": "2-3 sentence explanation", "time_horizon": "6_months"}}"""

        try:
            config_kwargs = {"temperature": 0.3}
            if "gemini" in model.lower():
                config_kwargs["response_mime_type"] = "application/json"
            config = types.GenerateContentConfig(**config_kwargs)
            
            judge_response = ai_client.models.generate_content(
                model=model, contents=judge_prompt, config=config
            )
            text = judge_response.text.strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json\n")
            judge_parsed = json.loads(text)
        except:
            judge_parsed = {"verdict": "MONITORING", "final_severity": 5, "final_probability": 0.4, "reasoning": "Insufficient data for definitive ruling."}
        
        debate_transcript.append(DebateMessage(
            role="judge", content=judge_parsed.get("reasoning", ""),
            round_number=1, confidence=0.9
        ))
        
        # Build verdict
        verdict = RiskVerdict(
            risk_id=risk.get("id", f"RISK_{len(verdicts)+1:03d}"),
            risk_description=risk.get("description", risk.get("title", "Unknown risk")),
            domain=risk.get("domain", "unknown"),
            severity_score=float(judge_parsed.get("final_severity", 5)),
            probability=float(judge_parsed.get("final_probability", 0.4)),
            time_horizon=judge_parsed.get("time_horizon", risk.get("time_horizon", "6_months")),
            bull_summary=bull_parsed.get("argument", ""),
            bear_summary=bear_parsed.get("argument", ""),
            judge_reasoning=judge_parsed.get("reasoning", ""),
            geographic_nexus=risk.get("geographic_nexus", "Global"),
            revenue_at_risk_pct=float(risk.get("revenue_at_risk_pct", 10.0)),
            debate_transcript=debate_transcript
        )
        
        if judge_parsed.get("verdict") != "DISMISSED" and judge_parsed.get("final_severity", 0) >= 3:
            verdicts.append(verdict)
    
    return verdicts


def run_geographic_mapping(ai_client, model: str, ticker: str, verdicts: List[RiskVerdict]) -> Tuple[List[FractureNode], List[Dict]]:
    """Map risks to geographic coordinates."""
    from google.genai import types
    
    if not verdicts:
        return [], []
    
    # Coordinate database for fallback
    COORD_DB = {
        "taiwan": (23.69, 120.96), "china": (35.86, 104.19), "usa": (37.09, -95.71),
        "united states": (37.09, -95.71), "india": (20.59, 78.96), 
        "shanghai": (31.23, 121.47), "shenzhen": (22.54, 114.05),
        "tokyo": (35.67, 139.65), "japan": (35.67, 139.65),
        "seoul": (37.56, 126.97), "south korea": (37.56, 126.97),
        "singapore": (1.35, 103.81), "germany": (51.16, 10.45),
        "london": (51.50, -0.12), "uk": (51.50, -0.12),
        "new york": (40.71, -74.00), "silicon valley": (37.38, -122.05),
        "san francisco": (37.77, -122.41), "beijing": (39.90, 116.40),
        "washington": (38.90, -77.04), "brussels": (50.85, 4.35),
        "europe": (48.85, 2.35), "global": (20.0, 0.0),
        "russia": (55.75, 37.61), "ukraine": (50.45, 30.52),
        "middle east": (25.20, 55.27), "strait of hormuz": (26.57, 56.25),
        "taiwan strait": (24.50, 119.50), "south china sea": (15.0, 115.0),
        "mumbai": (19.07, 72.87), "bangalore": (12.97, 77.59),
        "hyderabad": (17.38, 78.49), "delhi": (28.61, 77.20),
    }
    
    def get_coords(location: str) -> Tuple[float, float]:
        loc_lower = location.lower().strip()
        for key, coords in COORD_DB.items():
            if key in loc_lower:
                return coords
        return (20.0, 0.0)
    
    risks_for_mapping = [{
        "risk_id": v.risk_id,
        "description": v.risk_description[:200],
        "domain": v.domain,
        "severity": v.severity_score,
        "geographic_nexus": v.geographic_nexus,
        "revenue_at_risk_pct": v.revenue_at_risk_pct
    } for v in verdicts[:5]]
    
    mapping_prompt = f"""Map these {ticker} risks to EXACT geographic coordinates (lat/lon).
Each risk should have 1-2 specific locations (ports, cities, factories, government buildings).

RISKS:
{json.dumps(risks_for_mapping, indent=2)}

Respond in JSON:
{{
    "fracture_nodes": [
        {{
            "node_id": "NODE_001",
            "risk_id": "RISK_001",
            "latitude": 25.2048,
            "longitude": 55.2708,
            "label": "Specific Location Name",
            "description": "Why this location matters",
            "category": "infrastructure|conflict|regulatory|financial|supply_chain",
            "severity": 7.5,
            "probability": 0.35,
            "revenue_at_risk_pct": 12.0
        }}
    ]
}}"""

    try:
        config_kwargs = {"temperature": 0.1}
        if "gemini" in model.lower():
            config_kwargs["response_mime_type"] = "application/json"
        config = types.GenerateContentConfig(**config_kwargs)
        
        response = ai_client.models.generate_content(
            model=model, contents=mapping_prompt, config=config
        )
        
        text = response.text.strip()
        if text.startswith("```"): text = text.split("```")[1].lstrip("json\n")
        parsed = json.loads(text)
        
        nodes = []
        for n in parsed.get("fracture_nodes", []):
            try:
                lat = float(n.get("latitude", 0))
                lon = float(n.get("longitude", 0))
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    sev = float(n.get("severity", 5))
                    nodes.append(FractureNode(
                        node_id=n.get("node_id", f"NODE_{len(nodes)}"),
                        risk_id=n.get("risk_id", "unknown"),
                        latitude=lat,
                        longitude=lon,
                        label=n.get("label", "Unknown"),
                        description=n.get("description", ""),
                        category=n.get("category", "infrastructure"),
                        severity=sev,
                        probability=float(n.get("probability", 0.5)),
                        threat_level="critical" if sev >= 8 else "high" if sev >= 6 else "elevated" if sev >= 4 else "monitoring",
                        revenue_at_risk_pct=float(n.get("revenue_at_risk_pct", 5))
                    ))
            except:
                continue
        
        if nodes:
            return nodes, []
    except Exception as e:
        pass
    
    # Fallback: use coordinate database
    nodes = []
    for i, v in enumerate(verdicts):
        lat, lon = get_coords(v.geographic_nexus)
        # Add slight jitter to prevent overlap
        lat += np.random.uniform(-0.5, 0.5)
        lon += np.random.uniform(-0.5, 0.5)
        nodes.append(FractureNode(
            node_id=f"NODE_{i:03d}",
            risk_id=v.risk_id,
            latitude=lat,
            longitude=lon,
            label=v.geographic_nexus,
            description=v.risk_description[:100],
            category=v.domain,
            severity=v.severity_score,
            probability=v.probability,
            threat_level="critical" if v.severity_score >= 8 else "high" if v.severity_score >= 6 else "elevated" if v.severity_score >= 4 else "monitoring",
            revenue_at_risk_pct=v.revenue_at_risk_pct
        ))
    
    return nodes, []


def fetch_hq_coordinates(ticker: str, company_name: str, ai_client, tavily_client, model: str) -> Optional[Tuple[float, float, str]]:
    """Find HQ coordinates using AI."""
    from google.genai import types
    
    # Known HQ database for speed
    KNOWN_HQ = {
        "NVDA": (37.3707, -121.9632, "Santa Clara, CA, USA"),
        "AAPL": (37.3349, -122.0091, "Cupertino, CA, USA"),
        "MSFT": (47.6396, -122.1283, "Redmond, WA, USA"),
        "GOOGL": (37.4220, -122.0841, "Mountain View, CA, USA"),
        "GOOG": (37.4220, -122.0841, "Mountain View, CA, USA"),
        "AMZN": (47.6062, -122.3321, "Seattle, WA, USA"),
        "META": (37.4848, -122.1484, "Menlo Park, CA, USA"),
        "TSLA": (30.2241, -97.7700, "Austin, TX, USA"),
        "TSM": (24.7736, 120.9820, "Hsinchu, Taiwan"),
        "ASML": (51.5840, 5.5294, "Veldhoven, Netherlands"),
        "RELIANCE.NS": (19.0760, 72.8777, "Mumbai, India"),
        "TCS.NS": (19.0760, 72.8777, "Mumbai, India"),
        "INFY.NS": (12.9716, 77.5946, "Bangalore, India"),
        "HDFCBANK.NS": (19.0760, 72.8777, "Mumbai, India"),
        "JPM": (40.7128, -74.0060, "New York, NY, USA"),
        "V": (37.3875, -121.9636, "San Francisco, CA, USA"),
        "WMT": (36.3729, -94.2088, "Bentonville, AR, USA"),
        "JNJ": (40.4774, -74.2591, "New Brunswick, NJ, USA"),
    }
    
    # Check known database first
    ticker_upper = ticker.upper()
    if ticker_upper in KNOWN_HQ:
        return KNOWN_HQ[ticker_upper]
    
    # AI lookup
    try:
        query = f"headquarters location of {company_name} ({ticker}) city country"
        search_results = tavily_client.search(query=query, max_results=2)
        context = "\n".join([r.get('content', '')[:200] for r in search_results.get('results', [])])
        
        prompt = f"""Find the EXACT latitude and longitude of {company_name}'s global headquarters.
Context: {context}

Respond ONLY in JSON:
{{"city": "City Name", "country": "Country", "latitude": 37.33, "longitude": -122.00}}"""
        
        config_kwargs = {"temperature": 0.1}
        if "gemini" in model.lower():
            config_kwargs["response_mime_type"] = "application/json"
        config = types.GenerateContentConfig(**config_kwargs)
        
        response = ai_client.models.generate_content(
            model=model, contents=prompt, config=config
        )
        
        text = response.text.strip()
        if text.startswith("```"): text = text.split("```")[1].lstrip("json\n")
        data = json.loads(text)
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon, f"{data.get('city', 'Unknown')}, {data.get('country', '')}")
    except:
        pass
    
    # Default: assume US company
    return (37.77, -122.42, "San Francisco, CA, USA (assumed)")


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION - THE MAP (Enhanced with curved lines)
# ═══════════════════════════════════════════════════════════════

def generate_curved_path(lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 30) -> Tuple[List[float], List[float]]:
    """
    Generate a curved great-circle-like path between two points.
    Creates a visually appealing arc that bows outward.
    """
    lats = []
    lons = []
    
    for i in range(num_points + 1):
        t = i / num_points
        
        # Linear interpolation for base
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        
        # Add curvature (parabolic arc)
        # The arc height is proportional to distance
        distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        arc_height = distance * 0.15  # 15% of distance as arc height
        
        # Parabolic curve: maximum at midpoint
        curve_factor = 4 * t * (1 - t)  # Peaks at t=0.5
        
        # Perpendicular offset (rotate 90 degrees from the path direction)
        dx = lat2 - lat1
        dy = lon2 - lon1
        length = math.sqrt(dx**2 + dy**2) if (dx**2 + dy**2) > 0 else 1
        
        # Perpendicular direction (normalized)
        perp_lat = -dy / length
        perp_lon = dx / length
        
        # Apply curve
        lat += perp_lat * arc_height * curve_factor
        lon += perp_lon * arc_height * curve_factor
        
        lats.append(lat)
        lons.append(lon)
    
    return lats, lons


def render_fracture_map(nodes: List[FractureNode], paths: List[Dict], hq_info: Optional[Tuple[float, float, str]] = None):
    """
    THE MAP - Premium visualization with:
    - Color-coded risk nodes (red=critical, orange=high, yellow=elevated, green=monitoring)
    - Curved lines from each node converging to HQ
    - Animated-look pulsing markers
    - Dark military aesthetic
    """
    
    if not nodes:
        st.info("No fracture nodes to display. Run analysis first.")
        return
    
    fig = go.Figure()
    
    # Color mapping
    color_map = {
        "critical": "#FF1744",
        "high": "#FF6D00",
        "elevated": "#FFD600",
        "monitoring": "#00E676"
    }
    
    # ═══ 1. CURVED LINES FROM NODES TO HQ ═══
    if hq_info:
        hq_lat, hq_lon, hq_label = hq_info
        
        for node in nodes:
            # Generate curved path
            curve_lats, curve_lons = generate_curved_path(
                node.latitude, node.longitude,
                hq_lat, hq_lon,
                num_points=40
            )
            
            # Line color based on node severity
            node_color = color_map.get(node.threat_level, "#FF6D00")
            
            # Gradient opacity based on severity (more severe = more visible)
            opacity = 0.15 + (node.severity / 10) * 0.45
            
            fig.add_trace(go.Scattermapbox(
                lat=curve_lats,
                lon=curve_lons,
                mode="lines",
                line=dict(
                    width=1.5 + (node.severity / 10) * 1.5,
                    color=f"rgba({int(node_color[1:3], 16)}, {int(node_color[3:5], 16)}, {int(node_color[5:7], 16)}, {opacity})"
                ),
                hoverinfo="none",
                showlegend=False
            ))
        
        # ═══ 2. HQ MARKER (with "pulse" effect using concentric circles) ═══
        # Outer glow
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon],
            mode="markers",
            marker=dict(size=35, color="rgba(0, 176, 255, 0.08)"),
            showlegend=False, hoverinfo="none"
        ))
        # Middle ring
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon],
            mode="markers",
            marker=dict(size=22, color="rgba(0, 176, 255, 0.2)"),
            showlegend=False, hoverinfo="none"
        ))
        # Core marker
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon],
            mode="markers+text",
            marker=dict(
                size=14,
                color="#00B0FF",
                opacity=1,
                symbol="circle"
            ),
            text=["HQ"],
            textposition="bottom center",
            textfont=dict(size=11, color="#00B0FF", family="Arial Black"),
            name=f"HQ: {hq_label}",
            hovertext=f"HEADQUARTERS{hq_label}",
            hoverinfo="text",
            showlegend=True
        ))
    
    # ═══ 3. RISK NODES (grouped by threat level) ═══
    for level in ["critical", "high", "elevated", "monitoring"]:
        level_nodes = [n for n in nodes if n.threat_level == level]
        if not level_nodes:
            continue
        
        lats = [n.latitude for n in level_nodes]
        lons = [n.longitude for n in level_nodes]
        
        # Size based on severity + revenue at risk
        sizes = [max(12, 10 + n.severity * 2.5 + n.revenue_at_risk_pct * 0.3) for n in level_nodes]
        
        # Hover text
        hover_texts = []
        for n in level_nodes:
            hover_texts.append(
                f"{n.label}"
                f"Category: {n.category.upper()}"
                f"Severity: {n.severity:.1f}/10"
                f"Probability: {n.probability:.0%}"
                f"Revenue at Risk: {n.revenue_at_risk_pct:.1f}%"
                f"Horizon: {n.time_horizon.replace('_', ' ')}"
                f"---"
                f"{n.description[:150]}"
            )
        
        # Outer glow for critical/high nodes
        if level in ["critical", "high"]:
            glow_sizes = [s * 1.6 for s in sizes]
            glow_color = color_map[level]
            fig.add_trace(go.Scattermapbox(
                lat=lats, lon=lons,
                mode="markers",
                marker=dict(
                    size=glow_sizes,
                    color=f"rgba({int(glow_color[1:3], 16)}, {int(glow_color[3:5], 16)}, {int(glow_color[5:7], 16)}, 0.15)",
                    sizemode="diameter",
                ),
                showlegend=False,
                hoverinfo="none"
            ))
        
        # Main node markers
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=color_map[level],
                opacity=0.85,
                sizemode="diameter",
            ),
            text=[n.label for n in level_nodes],
            textposition="top center",
            textfont=dict(size=9, color=color_map[level], family="Arial"),
            hovertext=hover_texts,
            hoverinfo="text",
            name=f"{level.upper()} ({len(level_nodes)})",
            showlegend=True
        ))
    
    # ═══ 4. LAYOUT ═══
    all_lats = [n.latitude for n in nodes]
    all_lons = [n.longitude for n in nodes]
    if hq_info:
        all_lats.append(hq_info[0])
        all_lons.append(hq_info[1])
    
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # Auto-zoom
    lat_spread = max(all_lats) - min(all_lats)
    lon_spread = max(all_lons) - min(all_lons)
    max_spread = max(lat_spread, lon_spread)
    
    if max_spread > 120: zoom = 0.8
    elif max_spread > 80: zoom = 1.2
    elif max_spread > 50: zoom = 1.8
    elif max_spread > 20: zoom = 2.5
    elif max_spread > 10: zoom = 3.5
    else: zoom = 4.5
    
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(12, 16, 24, 0.92)",
            bordercolor="#1a2538",
            borderwidth=1,
            font=dict(color="#c8d6e5", size=11, family="Arial"),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
            itemsizing="constant"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        paper_bgcolor="#080b10",
        plot_bgcolor="#080b10",
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "displaylogo": False,
        "scrollZoom": True
    })


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION - CHARTS
# ═══════════════════════════════════════════════════════════════

def render_header(world_state: Optional[WorldState] = None):
    """Top header bar."""
    fear = world_state.fear_level if world_state else "SCANNING"
    badge_class = "badge-threat" if fear in ["PANIC", "ANXIOUS"] else "badge-active"
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    st.markdown(f"""
    
        [!] PROJECT DOOMSDAY
        
            SWARM ACTIVE
            THREAT: {fear}
            {ts}
        
    
    """, unsafe_allow_html=True)


def render_metrics_row(valuation, verdicts: List[RiskVerdict], world_state: WorldState):
    """Top metrics bar."""
    
    n_risks = len(verdicts)
    max_sev = max((v.severity_score for v in verdicts), default=0)
    
    if max_sev >= 8: threat, threat_class = "CRITICAL", "val-critical"
    elif max_sev >= 6: threat, threat_class = "HIGH", "val-orange"
    elif max_sev >= 4: threat, threat_class = "ELEVATED", "val-yellow"
    else: threat, threat_class = "LOW", "val-green"
    
    downside = getattr(valuation, 'downside_pct', 0)
    if downside <= -30: ds_class = "val-red"
    elif downside <= -15: ds_class = "val-orange"
    else: ds_class = "val-yellow"
    
    current_price = getattr(valuation, 'current_price', 0)
    base_fv = getattr(valuation, 'base_fair_value', 0)
    distressed = getattr(valuation, 'distressed_value', 0)
    
    st.markdown(f"""
    
        ${current_price:.2f}Current Price
        ${base_fv:.2f}Base Fair Value
        ${distressed:.2f}Distressed Value
        {downside:.1f}%Downside Risk
        {threat}Threat Level
        {n_risks}Validated Risks
    
    """, unsafe_allow_html=True)


def render_waterfall_chart(valuation):
    """Value destruction waterfall."""
    
    waterfall = getattr(valuation, 'waterfall_data', [])
    if not waterfall or len(waterfall) < 3:
        st.warning("Insufficient data for waterfall chart")
        return
    
    labels = [w["label"] for w in waterfall]
    values = [w["value"] for w in waterfall]
    measures = [w["type"] for w in waterfall]
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        connector=dict(line=dict(color="rgba(100, 100, 100, 0.3)", width=1)),
        decreasing=dict(marker=dict(color="#FF1744", line=dict(color="#FF1744", width=1))),
        increasing=dict(marker=dict(color="#00E676", line=dict(color="#00E676", width=1))),
        totals=dict(marker=dict(color="#FFAB00", line=dict(color="#FFAB00", width=1))),
        textposition="outside",
        text=[f"${abs(v):.2f}" if v >= 0 else f"-${abs(v):.2f}" for v in values],
        textfont=dict(size=9, color="#c8d6e5", family="JetBrains Mono, monospace"),
    ))
    
    current_price = getattr(valuation, 'current_price', 0)
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="#448aff",
        line_width=2,
        annotation_text=f"Market: ${current_price:.2f}",
        annotation_position="top right",
        annotation_font_color="#448aff",
        annotation_font_size=10
    )
    
    fig.update_layout(
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        font=dict(color="#78909c", size=10),
        yaxis=dict(title="Per Share ($)", gridcolor="#1a2538", zerolinecolor="#2a4058", titlefont=dict(color="#78909c")),
        xaxis=dict(gridcolor="#1a2538", tickangle=-20, tickfont=dict(size=9)),
        height=380,
        margin=dict(t=20, b=80, l=60, r=20),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_radar(verdicts: List[RiskVerdict]):
    """Radar chart of risk domains."""
    if not verdicts:
        return
    
    domain_scores = {}
    for v in verdicts:
        domain = v.domain.capitalize()
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(v.severity_score * v.probability)
    
    domains = list(domain_scores.keys())
    scores = [max(s) for s in domain_scores.values()]
    
    while len(domains) < 4:
        domains.append("Other")
        scores.append(0)
    
    domains_closed = domains + [domains[0]]
    scores_closed = scores + [scores[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=domains_closed,
        fill="toself",
        fillcolor="rgba(255, 23, 68, 0.15)",
        line=dict(color="#FF1744", width=2),
        marker=dict(size=6, color="#FF1744"),
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor="#0c1018",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1a2538", tickfont=dict(color="#5a6f82", size=8)),
            angularaxis=dict(gridcolor="#1a2538", tickfont=dict(color="#c8d6e5", size=10))
        ),
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        height=300,
        margin=dict(t=30, b=30, l=60, r=60),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_severity_timeline(verdicts: List[RiskVerdict]):
    """Horizontal bar chart of risk severity."""
    if not verdicts:
        return
    
    sorted_v = sorted(verdicts, key=lambda v: v.severity_score, reverse=True)
    labels = [v.risk_description[:40] + "..." if len(v.risk_description) > 40 else v.risk_description for v in sorted_v]
    severities = [v.severity_score for v in sorted_v]
    colors = ["#FF1744" if s >= 8 else "#FF6D00" if s >= 6 else "#FFAB00" if s >= 4 else "#00E676" for s in severities]
    
    fig = go.Figure(go.Bar(
        x=severities, y=labels, orientation='h',
        marker=dict(color=colors),
        text=[f"{s:.1f}" for s in severities],
        textposition="outside",
        textfont=dict(color="#c8d6e5", size=10, family="monospace")
    ))
    
    fig.update_layout(
        paper_bgcolor="#0c1018", plot_bgcolor="#0c1018",
        xaxis=dict(range=[0, 11], gridcolor="#1a2538", title="Severity", titlefont=dict(color="#78909c", size=10), tickfont=dict(color="#5a6f82")),
        yaxis=dict(tickfont=dict(color="#c8d6e5", size=9), autorange="reversed"),
        height=max(200, len(verdicts) * 45 + 60),
        margin=dict(t=10, b=40, l=280, r=50),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_probability_vs_impact(verdicts: List[RiskVerdict]):
    """Scatter: Probability vs Revenue Impact."""
    if not verdicts:
        return
    
    fig = go.Figure()
    
    for v in verdicts:
        color = "#FF1744" if v.severity_score >= 8 else "#FF6D00" if v.severity_score >= 6 else "#FFAB00" if v.severity_score >= 4 else "#00E676"
        fig.add_trace(go.Scatter(
            x=[v.probability * 100], y=[v.revenue_at_risk_pct],
            mode="markers+text",
            marker=dict(size=v.severity_score * 4, color=color, opacity=0.7, line=dict(color=color, width=1)),
            text=[v.risk_description[:18] + "..."],
            textposition="top center",
            textfont=dict(size=8, color=color),
            hovertext=f"{v.risk_description[:50]}Severity: {v.severity_score:.1f}Prob: {v.probability:.0%}Rev Risk: {v.revenue_at_risk_pct:.1f}%",
            hoverinfo="text",
            showlegend=False
        ))
    
    fig.add_hline(y=15, line_dash="dot", line_color="#2a4058", line_width=1)
    fig.add_vline(x=50, line_dash="dot", line_color="#2a4058", line_width=1)
    fig.add_annotation(x=75, y=max(v.revenue_at_risk_pct for v in verdicts) * 0.9, text="CRITICAL", font=dict(color="#FF1744", size=9), showarrow=False)
    fig.add_annotation(x=25, y=5, text="MONITOR", font=dict(color="#00E676", size=9), showarrow=False)
    
    fig.update_layout(
        paper_bgcolor="#0c1018", plot_bgcolor="#0c1018",
        xaxis=dict(title="Probability (%)", gridcolor="#1a2538", range=[0, 100], titlefont=dict(color="#78909c", size=10), tickfont=dict(color="#5a6f82")),
        yaxis=dict(title="Revenue at Risk (%)", gridcolor="#1a2538", range=[0, max(v.revenue_at_risk_pct for v in verdicts) + 10], titlefont=dict(color="#78909c", size=10), tickfont=dict(color="#5a6f82")),
        height=320, margin=dict(t=20, b=50, l=60, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_debate_panel(verdicts: List[RiskVerdict]):
    """Debate transcripts with expandable sections."""
    if not verdicts:
        st.info("No debates to display.")
        return
    
    for i, verdict in enumerate(verdicts):
        severity_emoji = "🔴" if verdict.severity_score >= 7 else "🟡" if verdict.severity_score >= 4 else "🟢"
        
        with st.expander(
            f"{severity_emoji} {verdict.risk_description[:65]}... | Severity: {verdict.severity_score:.1f}/10",
            expanded=(i == 0)
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Severity", f"{verdict.severity_score:.1f}/10")
            c2.metric("Probability", f"{verdict.probability:.0%}")
            c3.metric("Revenue Risk", f"{verdict.revenue_at_risk_pct:.1f}%")
            c4.metric("Horizon", verdict.time_horizon.replace("_", " "))
            
            for msg in verdict.debate_transcript:
                if msg.role == "bear":
                    role_label = "BEAR ADVOCATE"
                    msg_class = "msg-bear"
                elif msg.role == "bull":
                    role_label = "BULL ADVOCATE"
                    msg_class = "msg-bull"
                else:
                    role_label = "BLACK SWAN JUDGE"
                    msg_class = "msg-judge"
                
                st.markdown(f"""
                
                    
                        {role_label} | Round {msg.round_number} | Confidence: {msg.confidence:.0%}
                    
                    
                        {msg.content}
                    
                
                """, unsafe_allow_html=True)


def render_world_state_panel(ws: WorldState):
    """Sidebar world state."""
    fear_colors = {"CALM": "#00E676", "CAUTIOUS": "#FFAB00", "ANXIOUS": "#FF6D00", "PANIC": "#FF1744"}
    fear_color = fear_colors.get(ws.fear_level, "#FFF")
    
    st.markdown(f"""
    
        Global Sentiment
        
            {ws.fear_level}
        
    
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    
        VIX {ws.vix:.1f} ({ws.vix_trend})
        USD Index {ws.dxy:.1f}
        US 10Y {ws.us_10y_yield:.2f}%
        Oil (Brent) ${ws.oil_brent:.1f}
        Gold ${ws.gold:.0f}
    
    """, unsafe_allow_html=True)
    
    if ws.active_crises:
        st.markdown("**Active Crises:**")
        for crisis in ws.active_crises[:4]:
            title = crisis.get('title', 'Unknown')[:55]
            st.markdown(f"{title}", unsafe_allow_html=True)


def render_valuation_method_panel(profile, valuation):
    """Show valuation methodology."""
    method = getattr(valuation, 'valuation_method', 'Simplified DCF')
    company_type = getattr(profile, 'company_type', 'Unknown')
    if hasattr(company_type, 'value'):
        company_type = company_type.value
    
    st.markdown(f"""
    
        VALUATION METHODOLOGY
        {method}
        
            Company classified as: {str(company_type).upper()}
            Base WACC: {getattr(valuation, 'base_wacc', 10):.1f}% | 
            Stressed WACC: {getattr(valuation, 'stressed_wacc', 15):.1f}%
            Revenue Haircut: {getattr(valuation, 'revenue_haircut', 0):.1f}% | 
            Margin Compression: {getattr(valuation, 'margin_compression_bps', 0):.0f} bps
        
    
    """, unsafe_allow_html=True)
    
    method_values = getattr(valuation, 'method_values', {})
    if method_values:
        st.markdown("Cross-Check Values:", unsafe_allow_html=True)
        for m, v in method_values.items():
            st.markdown(f"- {m}: {v}", unsafe_allow_html=True)


def render_filing_intelligence_panel(filing_risks: List, filing_source: str):
    """Display filing risks."""
    if not filing_risks:
        st.markdown(f"""
        
            REGULATORY FILINGS
            
                Source: {filing_source}No structured filing risks extracted.
            
        
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"""
    
        REGULATORY FILING INTELLIGENCE
        
            Source: {filing_source} | Risks Found: {len(filing_risks)}
        
    
    """, unsafe_allow_html=True)
    
    for risk in filing_risks[:6]:
        category = getattr(risk, 'risk_category', 'unknown') if hasattr(risk, 'risk_category') else 'unknown'
        text = getattr(risk, 'risk_text', str(risk)) if hasattr(risk, 'risk_text') else str(risk)
        st.markdown(f"""
        
            {category.upper()}
            {text[:180]}...
        
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main application orchestrator."""
    
    # ═══ SESSION STATE DEFAULTS ═══
    defaults = {
        "analysis_done": False,
        "world_state": None,
        "profile": None,
        "filing_risks": [],
        "filing_source": "None",
        "verdicts": [],
        "fracture_nodes": [],
        "fracture_paths": [],
        "hq_info": None,
        "valuation": None,
        "chaos_level": 0.5,
        "last_chaos": 0.5,
        "ticker": "NVDA"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # ═══ SIDEBAR ═══
    with st.sidebar:
        st.markdown("""
        
            DOOMSDAY CONSOLE
        
        """, unsafe_allow_html=True)
        
        ticker = st.text_input(
            "TARGET TICKER",
            value=st.session_state.ticker,
            help="US: NVDA, MSFT, AAPL, TSM | India: RELIANCE.NS, TCS.NS"
        ).strip().upper()
        st.session_state.ticker = ticker
        
        st.markdown("---")
        
        st.markdown("""
        
            Chaos Level (Stress Intensity)
        
        """, unsafe_allow_html=True)
        
        chaos_level = st.slider(
            "Stress",
            min_value=0.0, max_value=1.0,
            value=st.session_state.chaos_level,
            step=0.05,
            label_visibility="collapsed"
        )
        st.session_state.chaos_level = chaos_level
        
        # Chaos indicator
        if chaos_level <= 0.2:
            st.success(f"MILD STRESS ({chaos_level:.0%})")
        elif chaos_level <= 0.4:
            st.info(f"MODERATE STRESS ({chaos_level:.0%})")
        elif chaos_level <= 0.6:
            st.warning(f"SEVERE STRESS ({chaos_level:.0%})")
        elif chaos_level <= 0.8:
            st.error(f"CRISIS MODE ({chaos_level:.0%})")
        else:
            st.error(f"DOOMSDAY ({chaos_level:.0%})")
        
        st.markdown("---")
        
        launch = st.button(
            "LAUNCH DOOMSDAY ANALYSIS",
            type="primary",
            use_container_width=True
        )
        
        # Show world state in sidebar if available
        if st.session_state.world_state:
            st.markdown("---")
            st.markdown("World State", unsafe_allow_html=True)
            render_world_state_panel(st.session_state.world_state)
    
    # ═══ MAIN CONTENT ═══
    render_header(st.session_state.world_state)
    
    # === LAUNCH ANALYSIS ===
    if launch:
        with st.status("Activating Doomsday Swarm...", expanded=True) as status:
            try:
                # Step 1: Init
                st.write("Initializing AI clients...")
                ai_client = get_ai_client()
                tavily_client = get_tavily_client()
                model = find_best_model(ai_client)
                st.write(f"Model: `{model}`")
                
                # Step 2: World State
                st.write("Scanning global threat environment...")
                world_state = fetch_world_state(tavily_client)
                st.session_state.world_state = world_state
                st.write(f"VIX={world_state.vix}, Fear={world_state.fear_level}")
                
                # Step 3: Company Profile
                st.write(f"Building profile for {ticker}...")
                profile = fetch_company_profile(ticker, ai_client, tavily_client, model)
                if not profile:
                    st.error(f"Failed to fetch data for '{ticker}'. Try: NVDA, MSFT, AAPL, RELIANCE.NS")
                    st.stop()
                st.session_state.profile = profile
                
                company_name = getattr(profile, 'name', ticker)
                market_cap = getattr(profile, 'market_cap', 0)
                company_type = getattr(profile, 'company_type', 'unknown')
                if hasattr(company_type, 'value'): company_type = company_type.value
                st.write(f"{company_name} | Type: **{str(company_type).upper()}** | MCap: ${market_cap/1e9:.1f}B")
                
                # Step 4: Filing Intelligence
                st.write("Extracting regulatory filing risks...")
                filing_risks = []
                filing_source = "None"
                if UnifiedFilingEngine:
                    try:
                        filing_engine = UnifiedFilingEngine(tavily_client=tavily_client)
                        filing_risks, filing_source = filing_engine.extract_all_risks(ticker)
                    except Exception as e:
                        st.write(f"Filing extraction warning: {e}")
                st.session_state.filing_risks = filing_risks
                st.session_state.filing_source = filing_source
                st.write(f"Found {len(filing_risks)} filing risks from {filing_source}")
                
                # Step 5: Intelligence
                st.write("Multi-source intelligence gathering...")
                risks = run_enhanced_intelligence(ai_client, tavily_client, model, ticker, profile, world_state)
                st.write(f"Identified {len(risks)} potential risks")
                
                # Step 6: Debate
                st.write("Fracture Tribunal - Adversarial debate...")
                company_stub = {"name": company_name, "sector": getattr(profile, 'sector', 'Unknown')}
                verdicts = run_adversarial_debate(ai_client, model, ticker, company_stub, risks, world_state)
                st.session_state.verdicts = verdicts
                st.write(f"Tribunal complete: {len(verdicts)} risks validated")
                
                # Step 7: Geographic Mapping
                st.write("Mapping fracture points...")
                hq_info = fetch_hq_coordinates(ticker, company_name, ai_client, tavily_client, model)
                nodes, paths = run_geographic_mapping(ai_client, model, ticker, verdicts)
                st.session_state.fracture_nodes = nodes
                st.session_state.fracture_paths = paths
                st.session_state.hq_info = hq_info
                st.write(f"Mapped {len(nodes)} nodes | HQ: {hq_info[2] if hq_info else 'Unknown'}")
                
                # Step 8: Valuation
                st.write("Calculating distressed valuation...")
                avg_severity = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
                valuation = calculate_valuation(profile, chaos_level, avg_severity)
                st.session_state.valuation = valuation
                st.session_state.last_chaos = chaos_level
                
                base_fv = getattr(valuation, 'base_fair_value', 0)
                distressed = getattr(valuation, 'distressed_value', 0)
                downside = getattr(valuation, 'downside_pct', 0)
                st.write(f"Base: ${base_fv:.2f} -> Distressed: ${distressed:.2f} ({downside:.1f}%)")
                
                st.session_state.analysis_done = True
                status.update(label="DOOMSDAY ANALYSIS COMPLETE", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label=f"Analysis failed: {str(e)[:50]}", state="error")
                st.error(f"Error during analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
        
        st.rerun()
    
    # === REAL-TIME CHAOS SLIDER UPDATE ===
    if st.session_state.analysis_done and abs(chaos_level - st.session_state.last_chaos) > 0.01:
        profile = st.session_state.profile
        verdicts = st.session_state.verdicts
        if profile:
            avg_severity = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
            valuation = calculate_valuation(profile, chaos_level, avg_severity)
            st.session_state.valuation = valuation
            st.session_state.last_chaos = chaos_level
    
    # === RENDER RESULTS ===
    if st.session_state.analysis_done:
        valuation = st.session_state.valuation
        verdicts = st.session_state.verdicts
        nodes = st.session_state.fracture_nodes
        paths = st.session_state.fracture_paths
        world_state = st.session_state.world_state
        profile = st.session_state.profile
        
        # Metrics Row
        render_metrics_row(valuation, verdicts, world_state)
        
        # MAP
        st.markdown('GLOBAL FRACTURE MAP - Vulnerability Network', unsafe_allow_html=True)
        render_fracture_map(nodes, paths, st.session_state.hq_info)
        
        # Waterfall + Radar
        st.markdown('VALUATION DESTRUCTION ANALYSIS', unsafe_allow_html=True)
        col_w, col_r = st.columns([3, 2])
        with col_w:
            render_waterfall_chart(valuation)
        with col_r:
            st.markdown("**Risk Domain Intensity**")
            render_risk_radar(verdicts)
        
        # Severity + Scatter
        st.markdown('RISK QUANTIFICATION', unsafe_allow_html=True)
        col_s, col_p = st.columns([1, 1])
        with col_s:
            render_severity_timeline(verdicts)
        with col_p:
            render_probability_vs_impact(verdicts)
        
        # Debate
        st.markdown('FRACTURE TRIBUNAL - ADVERSARIAL DEBATE', unsafe_allow_html=True)
        render_debate_panel(verdicts)
        
        # Methodology + Filings
        st.markdown('VALUATION METHODOLOGY & FILINGS', unsafe_allow_html=True)
        col_m, col_f = st.columns([1, 1])
        with col_m:
            render_valuation_method_panel(profile, valuation)
        with col_f:
            render_filing_intelligence_panel(
                st.session_state.filing_risks,
                st.session_state.filing_source
            )
        
        # IC Summary
        st.markdown('INVESTMENT COMMITTEE SUMMARY', unsafe_allow_html=True)
        
        company_name = getattr(profile, 'name', ticker)
        current_price = getattr(valuation, 'current_price', 0)
        base_fv = getattr(valuation, 'base_fair_value', 0)
        distressed = getattr(valuation, 'distressed_value', 0)
        downside = getattr(valuation, 'downside_pct', 0)
        
        col_a, col_b = st.columns(2)
        with col_a:
            downside_color = '#ff1744' if downside < -15 else '#ffab00' if downside < 0 else '#00e676'
            st.markdown(f"""
            
                {company_name}
                
                    Ticker{ticker}
                    Current Price${current_price:.2f}
                    Base Fair Value${base_fv:.2f}
                    Distressed Value${distressed:.2f}
                    Implied Downside{downside:.1f}%
                    Chaos Applied{chaos_level:.0%}
                    Risks Validated{len(verdicts)}
                    Fracture Nodes{len(nodes)}
                
            
            """, unsafe_allow_html=True)
        
        with col_b:
            if verdicts:
                top_risks_html = ""
                for v in sorted(verdicts, key=lambda x: x.severity_score, reverse=True)[:5]:
                    color = "#FF1744" if v.severity_score >= 7 else "#FF6D00" if v.severity_score >= 5 else "#FFAB00"
                    top_risks_html += f'[{v.severity_score:.1f}] {v.risk_description[:75]}...'
                
                st.markdown(f"""
                
                    Top Risks by Severity
                    {top_risks_html}
                
                """, unsafe_allow_html=True)
    
    else:
        # === LANDING STATE ===
        st.markdown("""
        
            ☣
            AWAITING TARGET
            
                Enter a ticker symbol in the sidebar and launch analysis to activate the Doomsday Swarm.
                The system will scan global intelligence across 5 domains, run adversarial AI debates,
                map geographic vulnerabilities, and compute distressed valuations in real-time.
            
            
                
                    01
                    Intelligence
                
                
                    02
                    Debate
                
                
                    03
                    Mapping
                
                
                    04
                    Valuation
                
            
        
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
Key Fixes & Improvements Explained:
1. Smoothness / State Issues Fixed
Session state properly initialized with all defaults
Chaos slider now updates valuation in real-time without re-running the full pipeline (uses threshold abs() > 0.01 to avoid float precision reruns)
Error handling wrapped around every API call with proper fallbacks
Client caching in st.session_state to avoid re-initialization
2. Map - Curved Lines Converging to HQ
The generate_curved_path() function creates parabolic arcs between each risk node and the company HQ:

Uses perpendicular offset with a parabolic curve factor 4*t*(1-t)
Arc height is 15% of the distance between points
Line opacity/width scales with risk severity (more severe = more prominent)
HQ has concentric circle "pulse" markers (3 layers for glow effect)
3. Color-Coded Nodes
Red (#FF1744) = Critical (severity >= 8)
Orange (#FF6D00) = High (severity >= 6)
Yellow (#FFD600) = Elevated (severity >= 4)
Green (#00E676) = Monitoring (severity < 4)
Critical/High nodes get an additional outer "glow" marker
4. CSS Completeness
All CSS classes referenced in HTML are now defined (.header-container, .header-title, .metrics-row, .m-val, .m-label, .ws-metric, .world-state-card, .landing-hero, .hero-title, .hero-subtitle, etc.)
5. Import Safety
filing_intelligence and valuation_engine are imported with try/except - if they're missing, fallback classes are used
This means the app can run even if those files have issues
6. JSON Parsing Robustness
All LLM responses are stripped of markdown code blocks (```json ... ```)
Fallback values for every JSON parse failure
To Run:
# Make sure your .env has:
# GOOGLE_API_KEY=your_gemini_key
# TAVILY_API_KEY=your_tavily_key
# (Optional) NVIDIA_API_KEY=...
# (Optional) FIREWORKS_API_KEY=...

pip install streamlit plotly pandas numpy yfinance python-dotenv google-genai tavily-python openai

streamlit run app.py