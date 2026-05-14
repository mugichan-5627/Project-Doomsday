# app.py
"""
☣️ PROJECT DOOMSDAY — Complete Streamlit Application
Fixed: Map rendering, DCF calculations, layout, visualizations
Version: 2.0 (Milan AI Week Hackathon)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv
from filing_intelligence import UnifiedFilingEngine, SECEdgarEngine, SEBIFilingEngine
from valuation_engine import ValuationRouter, CompanyProfile, CompanyType, classify_company, StressedValuation

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG — Must be first Streamlit command
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="☣️ PROJECT DOOMSDAY",
    page_icon="☣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# DATA MODELS (Self-contained — no external imports needed)
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
    category: str  # conflict, supply_chain, regulatory, financial, cyber, infrastructure
    severity: float  # 1-10
    probability: float  # 0-1
    threat_level: str  # critical, high, elevated, monitoring
    affected_assets: List[str] = field(default_factory=list)
    time_horizon: str = "6_months"
    revenue_at_risk_pct: float = 5.0
    connected_to: List[str] = field(default_factory=list)

@dataclass
class DebateMessage:
    role: str  # "bull", "bear", "judge"
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

# ValuationResult removed, using valuation_engine.StressedValuation instead

# ═══════════════════════════════════════════════════════════════
# CSS — Dark military/monitor aesthetic
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
    
    /* === HEADER BAR === */
    .doom-header {
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
    
    .doom-title {
        font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
        font-size: 1.3em;
        color: #ff3344;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(255, 51, 68, 0.4);
    }
    
    .header-badges {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7em;
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
    
    .badge-time {
        border-color: #546e7a;
        color: #78909c;
        background: rgba(84, 110, 122, 0.08);
    }
    
    @keyframes threat-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* === METRIC CARDS === */
    .metrics-grid {
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
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6em;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.65em;
        color: #5a6f82;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Colors for metrics */
    .val-blue { color: #448aff; }
    .val-red { color: #ff1744; }
    .val-orange { color: #ff6d00; }
    .val-yellow { color: #ffd600; }
    .val-green { color: #00e676; }
    .val-white { color: #eceff1; }
    .val-critical { color: #ff1744; animation: threat-pulse 1.5s infinite; }
    
    /* === SECTION HEADERS === */
    .section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85em;
        color: #78909c;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 24px 0 12px 0;
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
    
    .debate-msg {
        margin: 10px 0;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.82em;
        line-height: 1.6;
        border-left: 3px solid;
    }
    
    .msg-bear {
        background: rgba(255, 23, 68, 0.06);
        border-left-color: #ff1744;
    }
    
    .msg-bull {
        background: rgba(0, 230, 118, 0.06);
        border-left-color: #00e676;
    }
    
    .msg-judge {
        background: rgba(255, 214, 0, 0.06);
        border-left-color: #ffd600;
    }
    
    .msg-role {
        font-weight: 700;
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    
    /* === RISK FEED === */
    .risk-item {
        padding: 10px 0;
        border-bottom: 1px solid #1a2538;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.6em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .rbadge-critical { background: #ff1744; color: white; }
    .rbadge-high { background: #ff6d00; color: white; }
    .rbadge-elevated { background: #ffd600; color: black; }
    .rbadge-monitoring { background: #00e676; color: black; }
    
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
    
    /* === HIDE STREAMLIT DEFAULTS === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #080b10; }
    ::-webkit-scrollbar-thumb { background: #1a2538; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2a4058; }
    
    /* Fix Streamlit expander styling */
    .streamlit-expanderHeader {
        background: #0c1018 !important;
        border: 1px solid #1a2538 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CORE ENGINE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

class UnifiedAIClient:
    """Unified client for Gemini, NVIDIA, and Fireworks AI providers."""
    def __init__(self):
        self.gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.nvidia_key = os.getenv("NVIDIA_API_KEY")
        self.fireworks_key = os.getenv("FIREWORKS_API_KEY")
        
        self.genai_client = None
        if self.gemini_key:
            from google import genai
            try:
                self.genai_client = genai.Client(api_key=self.gemini_key)
            except:
                pass
            
        from openai import OpenAI
        self.openai_client = None
        if self.nvidia_key or self.fireworks_key:
            self.openai_client = OpenAI(api_key="sk-dummy") # Placeholder

    class ModelsWrapper:
        def __init__(self, parent):
            self.parent = parent
        def generate_content(self, model, contents, config=None):
            return self.parent.generate(model, contents, config)

    @property
    def models(self):
        return self.ModelsWrapper(self)

    def generate(self, model, contents, config=None):
        # 1. Gemini Dispatch
        if "gemini" in model.lower():
            if not self.genai_client:
                raise ValueError("Gemini client not initialized")
            return self.genai_client.models.generate_content(model=model, contents=contents, config=config)
        
        # 2. OpenAI-Compatible Dispatch (NVIDIA / Fireworks)
        is_nvidia = "nvidia" in model.lower() or "llama" in model.lower() and not "fireworks" in model.lower()
        base_url = "https://integrate.api.nvidia.com/v1" if is_nvidia else "https://api.fireworks.ai/inference/v1"
        api_key = self.nvidia_key if is_nvidia else self.fireworks_key
        
        if not api_key:
            raise ValueError(f"API Key for {model} not found in environment.")

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # Extract prompt
        prompt = contents
        if isinstance(contents, list):
            parts = []
            for c in contents:
                if hasattr(c, 'text'): parts.append(c.text)
                elif isinstance(c, str): parts.append(c)
                else: parts.append(str(c))
            prompt = "\n".join(parts)
        
        # Extract config
        temp = 0.7
        max_tokens = 2048
        if config:
            if hasattr(config, 'temperature'): temp = config.temperature
            if hasattr(config, 'max_output_tokens'): max_tokens = config.max_output_tokens

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )
        
        class FakeResponse:
            def __init__(self, text): self.text = text
        return FakeResponse(response.choices[0].message.content)


def get_ai_client():
    """Initialize unified AI client."""
    return UnifiedAIClient()


def get_tavily_client():
    """Initialize Tavily client."""
    from tavily import TavilyClient
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        st.error("❌ TAVILY_API_KEY not found in environment. Add it to .env file.")
        st.stop()
    return TavilyClient(api_key=api_key)


def find_best_model(client) -> str:
    """Find available model across providers (Gemini -> NVIDIA -> Fireworks)."""
    from google.genai import types
    
    # Priority 1: Gemini
    gemini_models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    
    # Priority 2: NVIDIA
    nvidia_models = [
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct",
    ]
    
    # Priority 3: Fireworks
    fireworks_models = [
        "accounts/fireworks/models/llama-v3p1-405b-instruct",
        "accounts/fireworks/models/llama-v3p1-70b-instruct",
    ]
    
    # Try Gemini first
    for model in gemini_models:
        try:
            if not client.gemini_key: break
            response = client.models.generate_content(
                model=model,
                contents="Respond with just the word 'ready'",
                config=types.GenerateContentConfig(max_output_tokens=10, temperature=0)
            )
            if response and response.text:
                return model
        except Exception:
            continue
            
    # Try NVIDIA next
    for model in nvidia_models:
        try:
            if not client.nvidia_key: break
            response = client.models.generate_content(
                model=model,
                contents="Respond with just the word 'ready'"
            )
            if response and response.text:
                st.info(f"⚡ Falling back to NVIDIA: `{model}`")
                return model
        except Exception:
            continue
            
    # Try Fireworks last
    for model in fireworks_models:
        try:
            if not client.fireworks_key: break
            response = client.models.generate_content(
                model=model,
                contents="Respond with just the word 'ready'"
            )
            if response and response.text:
                st.info(f"⚡ Falling back to Fireworks: `{model}`")
                return model
        except Exception:
            continue
    
    st.error("❌ No AI models available. Check Gemini, NVIDIA, and Fireworks API keys/quota.")
    st.stop()



def fetch_world_state(tavily_client) -> WorldState:
    """Fetch real-time world state indicators."""
    import yfinance as yf
    
    ws = WorldState(timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    # Fetch market indicators
    indicators = {
        "vix": "^VIX",
        "dxy": "DX-Y.NYB", 
        "us_10y_yield": "^TNX",
        "oil_brent": "BZ=F",
        "gold": "GC=F"
    }
    
    for key, ticker in indicators.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")
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
    
    # Fear level
    score = 0
    if ws.vix >= 35: score += 3
    elif ws.vix >= 25: score += 2
    elif ws.vix >= 18: score += 1
    if ws.gold > 2500: score += 1
    if ws.oil_brent > 95: score += 1
    if ws.us_10y_yield > 5.0: score += 1
    
    ws.fear_level = "PANIC" if score >= 5 else "ANXIOUS" if score >= 3 else "CAUTIOUS" if score >= 2 else "CALM"
    
    # Active crises from Tavily
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


def fetch_company_profile(ticker: str, ai_client=None, tavily_client=None, model: str=None) -> Optional[CompanyProfile]:
    """Fetch company profile using the proper ValuationRouter with LLM fallback."""
    # 1. Try traditional yfinance
    profile = ValuationRouter.build_profile(ticker)
    if profile and profile.market_cap > 0:
        return profile
        
    # 2. Try deep LLM search if traditional fails
    if ai_client and tavily_client and model:
        st.info(f"YFinance failed for '{ticker}'. Initiating Deep Intelligence Search...")
        deep_data = run_deep_ticker_search(ai_client, tavily_client, model, ticker)
        if deep_data:
            return ValuationRouter.build_profile_from_data(deep_data)
            
    return None


def run_deep_ticker_search(ai_client, tavily_client, model: str, ticker: str) -> Optional[Dict]:
    """Use Tavily + LLM to find live data for a ticker when APIs fail."""
    from google.genai import types
    
    search_query = f"financial data for {ticker} company 2024 2025: market cap, revenue, EBITDA, debt, cash, sector, correct yfinance ticker"
    
    try:
        search_results = tavily_client.search(query=search_query, search_depth="advanced", max_results=5)
        context = ""
        for r in search_results.get("results", []):
            context += f"\n--- {r.get('title')} ---\n{r.get('content')}\n"
            
        extraction_prompt = f"""You are a financial data extractor. I need to build a company profile for '{ticker}' but yfinance failed.
        
        Using the search results below, extract the most recent annual or TTM financial metrics.
        
        SEARCH RESULTS:
        {context}
        
        TASK:
        1. Identify the correct company name and its actual yfinance ticker (e.g. if I gave 'TSMC' you find 'TSM', if I gave 'RELIANCE' you find 'RELIANCE.NS').
        2. Extract: market_cap, current_price, revenue, ebitda, net_income, total_debt, cash, shares_outstanding, sector, industry.
        3. If a value is missing, provide a best-estimate based on peer data or market context in the search results.
        4. ALWAYS respond in valid JSON.
        
        JSON FORMAT:
        {{
            "ticker": "TSM",
            "name": "Taiwan Semiconductor Manufacturing Company",
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
        }}
        """
        
        response = ai_client.models.generate_content(
            model=model,
            contents=extraction_prompt,
            config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json")
        )
        
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Deep search failed: {e}")
        return None


def calculate_proper_valuation(
    profile: CompanyProfile, 
    chaos_level: float, 
    risk_severity: float = 5.0
) -> StressedValuation:
    """Route to correct valuation model based on company type."""
    return ValuationRouter.value_company(profile, chaos_level, risk_severity)


def run_enhanced_intelligence(
    gemini_client, tavily_client, model: str, 
    ticker: str, profile: CompanyProfile, world_state
) -> List[Dict]:
    """
    Enhanced intelligence gathering:
    1. SEC EDGAR / SEBI filings (company self-disclosed risks)
    2. Tavily multi-domain search (current news/events)
    3. Gemini synthesis of both
    """
    from google.genai import types
    
    # === PHASE 1: Regulatory Filing Intelligence ===
    filing_engine = UnifiedFilingEngine(tavily_client=tavily_client)
    filing_risks, filing_source = filing_engine.extract_all_risks(ticker)
    filing_context = filing_engine.format_for_llm(filing_risks)
    
    # === PHASE 2: Multi-domain Tavily Search ===
    domains = {
        "geopolitical": f"{profile.name} geopolitical risk sanctions trade war tariff 2025",
        "supply_chain": f"{profile.name} supply chain disruption shortage factory logistics risk",
        "financial": f"{profile.name} debt credit risk revenue decline margin pressure",
        "regulatory": f"{profile.name} regulation antitrust investigation fine lawsuit 2025",
        "technology": f"{profile.name} technology disruption AI competition obsolescence risk"
    }
    
    news_intelligence = ""
    for domain, query in domains.items():
        try:
            result = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            domain_text = f"\n[{domain.upper()} NEWS]:\n"
            for r in result.get("results", []):
                domain_text += f"• [{r.get('title', '')}]: {r.get('content', '')[:200]}\n"
            news_intelligence += domain_text
        except:
            pass
    
    # === PHASE 3: LLM Synthesis (combining filings + news) ===
    synthesis_prompt = f"""You are an institutional risk analyst performing deep due diligence on {ticker} ({profile.name}).

COMPANY PROFILE:
- Type: {profile.company_type.value.upper()}
- Sector: {profile.sector} | Industry: {profile.industry}
- Market Cap: ${profile.market_cap/1e9:.1f}B | Revenue: ${profile.revenue/1e9:.1f}B
- EBITDA Margin: {profile.ebitda_margin:.1f}% | Net Debt: ${profile.net_debt/1e9:.1f}B
- Revenue Growth: {profile.revenue_growth*100:.1f}% | Beta: {profile.beta:.2f}
- ROE: {profile.roe*100:.1f}% | P/E: {profile.pe_ratio:.1f}x

WORLD STATE:
- VIX: {world_state.vix} ({world_state.vix_trend}) | Fear: {world_state.fear_level}
- Oil: ${world_state.oil_brent} | Gold: ${world_state.gold} | US 10Y: {world_state.us_10y_yield}%

═══════════════════════════════════════════════════════════
SOURCE 1: REGULATORY FILINGS (Legally mandated disclosures)
From: {filing_source}
═══════════════════════════════════════════════════════════
{filing_context}

═══════════════════════════════════════════════════════════
SOURCE 2: CURRENT NEWS & EVENTS (Last 30 days)
═══════════════════════════════════════════════════════════
{news_intelligence}

═══════════════════════════════════════════════════════════

TASK: Synthesize the regulatory filings AND current news to identify the TOP 6 most material risks.

CRITICAL RULES:
1. PRIORITIZE risks that appear in BOTH regulatory filings AND current news (confirmation = high confidence)
2. Flag any NEW risks in news that are NOT yet in filings (emerging risks = early warning)
3. Each risk must cite whether evidence comes from "FILING", "NEWS", or "BOTH"
4. Be specific — not "competition may increase" but "AWS gaining 3% market share per quarter"
5. For financial companies: focus on credit quality, NPA trends, capital adequacy, interest rate sensitivity
6. For tech companies: focus on customer concentration, regulatory (antitrust), geopolitical (export controls)

Respond ONLY in this JSON format:
{{
    "risks": [
        {{
            "id": "RISK_001",
            "domain": "geopolitical|supply_chain|financial|regulatory|technology|market",
            "title": "Short descriptive title (5-8 words)",
            "description": "Detailed 2-3 sentence description with specific facts and numbers",
            "evidence_source": "FILING|NEWS|BOTH",
            "evidence": ["Quote or fact 1", "Quote or fact 2"],
            "severity": 7,
            "probability": 0.4,
            "geographic_nexus": "Specific country/city/region where risk manifests",
            "revenue_at_risk_pct": 15.0,
            "time_horizon": "3_months|6_months|12_months",
            "second_order_effects": ["Effect 1", "Effect 2"],
            "filing_reference": "From 10-K Item 1A / BSE disclosure / null if news only"
        }}
    ],
    "intelligence_summary": {{
        "filing_risks_found": {len(filing_risks)},
        "news_confirmations": 0,
        "emerging_risks_not_in_filings": 0,
        "overall_risk_trend": "increasing|stable|decreasing"
    }}
}}"""

    try:
        response = gemini_client.models.generate_content(
            model=model,
            contents=synthesis_prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
        )
        
        parsed = json.loads(response.text)
        return parsed.get("risks", [])
    except Exception as e:
        # Fallback: return basic risks from filings
        fallback_risks = []
        for i, fr in enumerate(filing_risks[:6]):
            fallback_risks.append({
                "id": f"RISK_{i+1:03d}",
                "domain": fr.risk_category,
                "title": fr.risk_text[:50],
                "description": fr.risk_text[:300],
                "evidence_source": "FILING",
                "evidence": [fr.risk_text[:200]],
                "severity": 5,
                "probability": 0.4,
                "geographic_nexus": "Global",
                "revenue_at_risk_pct": 10.0,
                "time_horizon": "6_months"
            })
        return fallback_risks


def run_adversarial_debate(gemini_client, model: str, ticker: str, company: Dict, risks: List[Dict], world_state: WorldState) -> List[RiskVerdict]:
    """Run adversarial debate on each risk — Bull vs Bear vs Judge."""
    from google.genai import types
    
    verdicts = []
    
    for risk in risks[:6]:  # Max 6 risks to debate (latency management)
        debate_transcript = []
        
        # === BEAR PROSECUTION ===
        bear_prompt = f"""You are the BEAR ADVOCATE in a financial risk tribunal for {ticker}.

RISK UNDER EXAMINATION:
{json.dumps(risk, indent=2)}

Present your PROSECUTION. You must:
1. Articulate the worst-case scenario with specifics
2. Identify second-order contagion effects
3. Cite historical precedents where similar risks caused >20% drawdowns
4. Estimate specific financial impact (revenue %, margin impact)

Be rigorous, not fear-mongering. If the risk is weak, say so.

Respond in JSON:
{{"argument": "Your 3-4 sentence prosecution", "severity_estimate": 1-10, "financial_impact": "Specific % estimate", "historical_precedent": "One relevant precedent", "confidence": 0.0-1.0}}"""

        try:
            bear_response = gemini_client.models.generate_content(
                model=model, contents=bear_prompt,
                config=types.GenerateContentConfig(temperature=0.6, response_mime_type="application/json")
            )
            bear_parsed = json.loads(bear_response.text)
        except:
            bear_parsed = {"argument": "Unable to generate bear case", "severity_estimate": 5, "confidence": 0.5}
        
        debate_transcript.append(DebateMessage(role="bear", content=bear_parsed.get("argument", ""), round_number=1, confidence=bear_parsed.get("confidence", 0.5)))
        
        # === BULL DEFENSE ===
        bull_prompt = f"""You are the BULL ADVOCATE defending {ticker} against this risk:

RISK: {risk.get('description', '')}
BEAR'S ARGUMENT: {bear_parsed.get('argument', '')}

Present your DEFENSE. You must:
1. Challenge the evidence quality — is it speculative?
2. Present specific mitigating factors (hedging, diversification, management actions)
3. Argue market has already priced in the risk
4. Cite the company's strengths that offset this risk

Concede points that are genuinely strong. Your credibility matters.

Respond in JSON:
{{"argument": "Your 3-4 sentence defense", "mitigating_factors": ["Factor 1", "Factor 2"], "market_already_priced": true/false, "confidence_in_dismissal": 0.0-1.0}}"""

        try:
            bull_response = gemini_client.models.generate_content(
                model=model, contents=bull_prompt,
                config=types.GenerateContentConfig(temperature=0.6, response_mime_type="application/json")
            )
            bull_parsed = json.loads(bull_response.text)
        except:
            bull_parsed = {"argument": "Unable to generate bull case", "confidence_in_dismissal": 0.5}
        
        debate_transcript.append(DebateMessage(role="bull", content=bull_parsed.get("argument", ""), round_number=1, confidence=bull_parsed.get("confidence_in_dismissal", 0.5)))
        
        # === JUDGE VERDICT ===
        judge_prompt = f"""You are the BLACK SWAN JUDGE. You've heard both sides debate this risk for {ticker}:

RISK: {risk.get('description', '')}
BEAR ARGUES: {bear_parsed.get('argument', '')} (Severity: {bear_parsed.get('severity_estimate', 5)})
BULL ARGUES: {bull_parsed.get('argument', '')}

WORLD CONTEXT: VIX={world_state.vix}, Fear={world_state.fear_level}

Deliver your VERDICT. You must:
1. Weigh evidence from both sides objectively
2. Assign final severity (1-10) and probability (0.0-1.0)
3. Determine if this risk is VALIDATED, DISMISSED, or MONITORING
4. Identify anything NEITHER side mentioned

CALIBRATION: 8+ severity = potential >25% impairment. Most risks should be 4-7.

Respond in JSON:
{{"verdict": "VALIDATED|DISMISSED|MONITORING", "final_severity": 1-10, "final_probability": 0.0-1.0, "reasoning": "2-3 sentence explanation", "overlooked_factors": ["Any tail risks neither side mentioned"], "time_horizon": "3_months|6_months|12_months"}}"""

        try:
            judge_response = gemini_client.models.generate_content(
                model=model, contents=judge_prompt,
                config=types.GenerateContentConfig(temperature=0.3, response_mime_type="application/json")
            )
            judge_parsed = json.loads(judge_response.text)
        except:
            judge_parsed = {"verdict": "MONITORING", "final_severity": 5, "final_probability": 0.4, "reasoning": "Unable to parse judge response"}
        
        debate_transcript.append(DebateMessage(role="judge", content=judge_parsed.get("reasoning", ""), round_number=1, confidence=0.9))
        
        # Build verdict
        verdict = RiskVerdict(
            risk_id=risk.get("id", f"RISK_{len(verdicts)+1:03d}"),
            risk_description=risk.get("description", risk.get("title", "Unknown risk")),
            domain=risk.get("domain", "unknown"),
            severity_score=judge_parsed.get("final_severity", 5),
            probability=judge_parsed.get("final_probability", 0.4),
            time_horizon=judge_parsed.get("time_horizon", risk.get("time_horizon", "6_months")),
            bull_summary=bull_parsed.get("argument", ""),
            bear_summary=bear_parsed.get("argument", ""),
            judge_reasoning=judge_parsed.get("reasoning", ""),
            geographic_nexus=risk.get("geographic_nexus", "Global"),
            revenue_at_risk_pct=risk.get("revenue_at_risk_pct", 10.0),
            debate_transcript=debate_transcript
        )
        
        # Only include if judge validated or severity is meaningful
        if judge_parsed.get("verdict") != "DISMISSED" and judge_parsed.get("final_severity", 0) >= 3:
            verdicts.append(verdict)
    
    return verdicts


def run_geographic_mapping(gemini_client, model: str, ticker: str, verdicts: List[RiskVerdict]) -> Tuple[List[FractureNode], List[Dict]]:
    """Map validated risks to precise geographic coordinates."""
    from google.genai import types
    
    if not verdicts:
        return [], []
    
    risks_for_mapping = [{
        "risk_id": v.risk_id,
        "description": v.risk_description,
        "domain": v.domain,
        "severity": v.severity_score,
        "probability": v.probability,
        "geographic_nexus": v.geographic_nexus,
        "revenue_at_risk_pct": v.revenue_at_risk_pct
    } for v in verdicts]
    
    mapping_prompt = f"""You are a geospatial intelligence analyst. Map these validated risks for {ticker} to PRECISE physical locations.

RULES:
1. Each risk → 1-3 geographic nodes with EXACT lat/lon coordinates
2. Use specific infrastructure: ports, factories, data centers, government buildings, shipping chokepoints
3. Coordinates must be ACCURATE (not approximate). Verify mentally.
4. Include supply chain paths where risks connect locations

RISKS TO MAP:
{json.dumps(risks_for_mapping, indent=2)}

IMPORTANT: Every coordinate must be valid (-90 to 90 lat, -180 to 180 lon).

Respond in JSON:
{{
    "fracture_nodes": [
        {{
            "node_id": "NODE_001",
            "risk_id": "RISK_001",
            "latitude": 25.2048,
            "longitude": 55.2708,
            "label": "Port of Jebel Ali",
            "description": "Critical transshipment hub for 60% of regional trade. Vulnerable to Strait of Hormuz closure.",
            "category": "infrastructure",
            "severity": 7.5,
            "probability": 0.35,
            "threat_level": "high",
            "affected_assets": ["Container Terminal 3", "Free Zone Warehouses"],
            "revenue_at_risk_pct": 12.0,
            "time_horizon": "6_months",
            "connected_to": ["NODE_002"]
        }}
    ],
    "supply_chain_paths": [
        {{
            "path_id": "PATH_001",
            "nodes": ["NODE_001", "NODE_002"],
            "description": "Semiconductor supply route: Taiwan → Shanghai assembly",
            "vulnerability": 8.0
        }}
    ]
}}"""

    # Fallback heuristic if LLM fails
    def get_coords(loc: str):
        db = {
            "taiwan": (23.69, 120.96), "china": (35.86, 104.19), "usa": (37.09, -95.71),
            "india": (20.59, 78.96), "shanghai": (31.23, 121.47), "shenzhen": (22.54, 114.05),
            "tokyo": (35.67, 139.65), "seoul": (37.56, 126.97), "singapore": (1.35, 103.81),
            "germany": (51.16, 10.45), "london": (51.50, -0.12), "ny": (40.71, -74.00),
            "silicon valley": (37.38, -122.05), "beijing": (39.90, 116.40), "global": (20.0, 30.0)
        }
        for k, v in db.items():
            if k in loc.lower(): return v
        return (20.0, 30.0)

    try:
        # Optimized: only map top 5 risks to save time
        risks_for_mapping = risks_for_mapping[:5]
        
        # Adjust mapping_prompt for speed
        mapping_prompt = f"Map these {ticker} risks to JSON: " + json.dumps(risks_for_mapping)
        
        response = gemini_client.models.generate_content(
            model=model, contents=mapping_prompt,
            config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json")
        )
        parsed = json.loads(response.text)
    except Exception:
        nodes = []
        for i, v in enumerate(verdicts):
            lat, lon = get_coords(v.geographic_nexus)
            nodes.append(FractureNode(
                node_id=f"NODE_{i}", risk_id=v.risk_id,
                latitude=lat, longitude=lon, label=v.geographic_nexus,
                description=v.risk_description[:100], category=v.domain,
                severity=v.severity_score, probability=v.probability,
                threat_level="high" if v.severity_score > 6 else "elevated"
            ))
        return nodes, []
    
    # Parse nodes with safety
    nodes = []
    for n in parsed.get("fracture_nodes", []):
        try:
            nodes.append(FractureNode(
                node_id=n.get("node_id", f"NODE_{len(nodes)}"),
                risk_id=n.get("risk_id", "unknown"),
                latitude=float(n.get("latitude", 20)),
                longitude=float(n.get("longitude", 30)),
                label=n.get("label", "Unknown"),
                description=n.get("description", ""),
                category=n.get("category", "infrastructure"),
                severity=float(n.get("severity", 5)),
                probability=float(n.get("probability", 0.5)),
                threat_level="high" if float(n.get("severity", 5)) > 6 else "elevated",
                revenue_at_risk_pct=float(n.get("revenue_at_risk_pct", 5))
            ))
        except: continue
    
    return nodes, parsed.get("supply_chain_paths", [])


def fetch_hq_coordinates(ticker: str, company_name: str, ai_client, tavily_client, model: str) -> Optional[Tuple[float, float, str]]:
    """Use AI to find the HQ location (City, Country) and coordinates."""
    from google.genai import types
    
    query = f"Where is the global headquarters of {company_name} ({ticker})? City and Country."
    try:
        search_results = tavily_client.search(query=query, max_results=3)
        context = "\n".join([r.get('content', '') for r in search_results.get('results', [])])
        
        prompt = f"""Find the latitude and longitude of the global headquarters for {company_name}.
        
        SEARCH CONTEXT:
        {context}
        
        RESPONSE FORMAT: JSON ONLY
        {{
            "city": "Cupertino",
            "country": "USA",
            "latitude": 37.3349,
            "longitude": -122.0091
        }}
        """
        
        response = ai_client.models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json")
        )
        data = json.loads(response.text)
        return (float(data['latitude']), float(data['longitude']), f"{data['city']}, {data['country']}")
    except:
        return None


def render_valuation_method_panel(profile: CompanyProfile, valuation: StressedValuation):
    """Show which valuation method was used and WHY."""
    explanation = ValuationRouter.get_valuation_explanation(profile.company_type)
    
    st.markdown(f"""
    <div class="info-panel">
        <div class="metric-label" style="color: #448aff; margin-bottom: 8px;">
            VALUATION METHODOLOGY
        </div>
        <div class="metric-value" style="font-size: 1.2em; color: #eceff1; margin-bottom: 12px;">
            {valuation.valuation_method}
        </div>
        <div style="font-size: 0.85em; line-height: 1.5; color: #78909c;">
            Company classified as: <b>{profile.company_type.value.upper()}</b><br><br>
            {explanation}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show cross-check values
    if valuation.method_values:
        st.markdown("<div style='margin-top: 10px; font-size: 0.8em; color: #5a6f82;'>📊 Cross-Check Values:</div>", unsafe_allow_html=True)
        for method, value in valuation.method_values.items():
            st.markdown(f"<div style='font-size: 0.8em; color: #78909c;'>• {method}: {value}</div>", unsafe_allow_html=True)


def render_filing_intelligence_panel(filing_risks: List, filing_source: str):
    """Display regulatory filing intelligence."""
    if not filing_risks:
        st.info(f"📁 No filing risks extracted from {filing_source}")
        return
    
    st.markdown(f"""
    <div class="info-panel">
        <div class="metric-label" style="color: #ff6d00; margin-bottom: 8px;">
            📁 REGULATORY FILING INTELLIGENCE
        </div>
        <div style="font-size: 0.75em; color: #5a6f82; margin-bottom: 12px;">
            Source: {filing_source} | Risks Found: {len(filing_risks)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for i, risk in enumerate(filing_risks[:8]):
        badge_color = "#ff6d00" if risk.risk_category in ["financial", "regulatory"] else "#ffab00"
        st.markdown(f"""
        <div class="risk-item" style="border-bottom: 1px solid #1a2538; padding: 8px 0;">
            <span class="risk-badge" style="background: {badge_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.6em;">
                {risk.risk_category.upper()}
            </span>
            <span style="font-size: 0.7em; color: #5a6f82; margin-left: 8px;">[{risk.source}]</span>
            <div style="font-size: 0.75em; color: #c8d6e5; margin-top: 4px; line-height: 1.4;">
                {risk.risk_text[:200]}...
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION COMPONENTS
# ═══════════════════════════════════════════════════════════════

def render_header(world_state: Optional[WorldState] = None):
    """Top header bar with status badges."""
    fear = world_state.fear_level if world_state else "SCANNING"
    badge_class = "badge-threat" if fear in ["PANIC", "ANXIOUS"] else "badge-active"
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">[!] PROJECT DOOMSDAY</div>
        <div class="header-status">
            <span class="badge {badge_class}">SWARM ACTIVE</span>
            <span class="badge badge-threat">THREAT: {fear}</span>
            <span style="margin-left: 15px; opacity: 0.6;">{ts} UTC</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics_row(valuation: StressedValuation, verdicts: List[RiskVerdict], world_state: WorldState):
    """Top metrics bar with 6 key numbers."""
    
    n_risks = len(verdicts)
    max_sev = max((v.severity_score for v in verdicts), default=0)
    
    # Threat level
    if max_sev >= 8: threat, threat_class = "CRITICAL", "val-critical"
    elif max_sev >= 6: threat, threat_class = "HIGH", "val-orange"
    elif max_sev >= 4: threat, threat_class = "ELEVATED", "val-yellow"
    else: threat, threat_class = "LOW", "val-green"
    
    # Downside color
    if valuation.downside_pct <= -30: ds_class = "val-red"
    elif valuation.downside_pct <= -15: ds_class = "val-orange"
    else: ds_class = "val-yellow"
    
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card"><div class="m-val">${valuation.current_price:.2f}</div><div class="m-label">Current Price</div></div>
        <div class="metric-card"><div class="m-val">${valuation.base_fair_value:.2f}</div><div class="m-label">Base Fair Value</div></div>
        <div class="metric-card"><div class="m-val">${valuation.distressed_value:.2f}</div><div class="m-label">Distressed Value</div></div>
        <div class="metric-card"><div class="m-val {ds_class}">{valuation.downside_pct:.1f}%</div><div class="m-label">Downside Risk</div></div>
        <div class="metric-card"><div class="m-val {threat_class}">{threat}</div><div class="m-label">Threat Level</div></div>
        <div class="metric-card"><div class="m-val">{n_risks}</div><div class="m-label">Validated Risks</div></div>
    </div>
    """, unsafe_allow_html=True)


def render_fracture_map(nodes: List[FractureNode], paths: List[Dict], hq_info: Optional[Tuple[float, float, str]] = None):
    """THE MAP — properly configured with Mapbox/Carto dark style and HQ hub."""
    
    if not nodes:
        st.info("🔍 No fracture nodes to display. Run analysis first.")
        return
    
    fig = go.Figure()
    
    # 1. Plot HQ Node and Hub Lines
    if hq_info:
        hq_lat, hq_lon, hq_label = hq_info
        
        # Hub Lines (Fracture to HQ)
        for n in nodes:
            fig.add_trace(go.Scattermapbox(
                lat=[n.latitude, hq_lat],
                lon=[n.longitude, hq_lon],
                mode="lines",
                line=dict(width=1, color="rgba(255, 0, 0, 0.2)"),
                hoverinfo="none",
                showlegend=False
            ))
            
        # HQ Marker (Animated Effect using two markers)
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon],
            mode="markers",
            marker=dict(size=25, color="rgba(0, 150, 255, 0.3)"),
            showlegend=False, hoverinfo="none"
        ))
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon],
            mode="markers+text",
            marker=dict(size=15, color="#00B0FF", opacity=1),
            text=["HEADQUARTERS"],
            textposition="bottom center",
            textfont=dict(size=12, color="#00B0FF", family="Consolas"),
            name="Company HQ",
            hovertext=f"Strategic Hub: {hq_label}",
            hoverinfo="text"
        ))

    # 2. Draw Supply Chain Paths (Custom paths from AI)
    if paths:
        for path in paths:
            path_node_ids = path.get("nodes", [])
            path_nodes_matched = [n for n in nodes if n.node_id in path_node_ids]
            if len(path_nodes_matched) >= 2:
                fig.add_trace(go.Scattermapbox(
                    lat=[n.latitude for n in path_nodes_matched],
                    lon=[n.longitude for n in path_nodes_matched],
                    mode="lines",
                    line=dict(width=2, color="rgba(255, 68, 68, 0.35)"),
                    name=path.get("description", "Supply Chain")[:40],
                    showlegend=True,
                    hoverinfo="text",
                    hovertext=path.get("description", "")
                ))
    
    # Color and size mapping
    color_map = {
        "critical": "#FF1744",
        "high": "#FF6D00", 
        "elevated": "#FFAB00",
        "monitoring": "#00E676"
    }
    
    # Plot nodes grouped by threat level
    for level in ["critical", "high", "elevated", "monitoring"]:
        level_nodes = [n for n in nodes if n.threat_level == level]
        if not level_nodes:
            continue
        
        lats = [n.latitude for n in level_nodes]
        lons = [n.longitude for n in level_nodes]
        sizes = [max(10, 8 + n.severity * 2.5 + n.revenue_at_risk_pct * 0.4) for n in level_nodes]
        colors = [color_map.get(level, "#FFFFFF")] * len(level_nodes)
        
        hover_texts = []
        for n in level_nodes:
            assets_str = ", ".join(n.affected_assets[:3]) if n.affected_assets else "General infrastructure"
            hover_texts.append(
                f"{n.label}"
                f"━━━━━━━━━━━━━━━"
                f"Category: {n.category.upper()}"
                f"Severity: {n.severity:.1f}/10"
                f"Probability: {n.probability:.0%}"
                f"Revenue at Risk: {n.revenue_at_risk_pct:.1f}%"
                f"Time Horizon: {n.time_horizon.replace('_', ' ')}"
                f"Assets: {assets_str}"
                f"━━━━━━━━━━━━━━━"
                f"{n.description[:200]}"
            )
        
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
            name=f"● {level.upper()} ({len(level_nodes)})",
            showlegend=True
        ))
    
    # Calculate optimal center
    all_lats = [n.latitude for n in nodes]
    all_lons = [n.longitude for n in nodes]
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # Auto-zoom based on spread
    lat_spread = max(all_lats) - min(all_lats)
    lon_spread = max(all_lons) - min(all_lons)
    max_spread = max(lat_spread, lon_spread)
    
    if max_spread > 100: zoom = 1.2
    elif max_spread > 50: zoom = 2.0
    elif max_spread > 20: zoom = 3.0
    else: zoom = 4.0
    
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(12, 16, 24, 0.95)",
            bordercolor="#1a2538",
            borderwidth=1,
            font=dict(color="#c8d6e5", size=11, family="Arial"),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        paper_bgcolor="#080b10",
        plot_bgcolor="#080b10",
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "displaylogo": False,
        "scrollZoom": True
    })


def render_waterfall_chart(valuation: StressedValuation):
    """Value destruction waterfall chart."""
    
    waterfall = valuation.waterfall_data
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
        textfont=dict(size=10, color="#c8d6e5", family="JetBrains Mono, monospace"),
    ))
    
    # Current price reference line
    fig.add_hline(
        y=valuation.current_price,
        line_dash="dash",
        line_color="#448aff",
        line_width=2,
        annotation_text=f"Current Price: ${valuation.current_price:.2f}",
        annotation_position="top right",
        annotation_font_color="#448aff",
        annotation_font_size=11
    )
    
    fig.update_layout(
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        font=dict(color="#78909c", size=10),
        yaxis=dict(
            title="Per Share Value ($)",
            gridcolor="#1a2538",
            zerolinecolor="#2a4058",
            titlefont=dict(color="#78909c")
        ),
        xaxis=dict(
            gridcolor="#1a2538",
            tickangle=-20,
            tickfont=dict(size=9)
        ),
        height=380,
        margin=dict(t=20, b=80, l=60, r=20),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_radar(verdicts: List[RiskVerdict]):
    """Radar chart showing risk across domains."""
    
    if not verdicts:
        return
    
    # Aggregate by domain
    domain_scores = {}
    for v in verdicts:
        domain = v.domain
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(v.severity_score * v.probability)
    
    domains = list(domain_scores.keys())
    scores = [max(s) for s in domain_scores.values()]  # Take max per domain
    
    # Pad to at least 5 axes for visual appeal
    while len(domains) < 5:
        domains.append(f"other_{len(domains)}")
        scores.append(0)
    
    # Close the polygon
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
        name="Risk Intensity"
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor="#0c1018",
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor="#1a2538",
                linecolor="#1a2538",
                tickfont=dict(color="#5a6f82", size=8)
            ),
            angularaxis=dict(
                gridcolor="#1a2538",
                linecolor="#1a2538",
                tickfont=dict(color="#c8d6e5", size=10)
            )
        ),
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        height=300,
        margin=dict(t=30, b=30, l=60, r=60),
        showlegend=False,
        font=dict(color="#c8d6e5")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_severity_timeline(verdicts: List[RiskVerdict]):
    """Horizontal bar chart of risks sorted by severity."""
    
    if not verdicts:
        return
    
    # Sort by severity descending
    sorted_verdicts = sorted(verdicts, key=lambda v: v.severity_score, reverse=True)
    
    labels = [v.risk_description[:45] + "..." if len(v.risk_description) > 45 else v.risk_description for v in sorted_verdicts]
    severities = [v.severity_score for v in sorted_verdicts]
    colors = ["#FF1744" if s >= 8 else "#FF6D00" if s >= 6 else "#FFAB00" if s >= 4 else "#00E676" for s in severities]
    
    fig = go.Figure(go.Bar(
        x=severities,
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(color=colors, width=1)),
        text=[f"{s:.1f}" for s in severities],
        textposition="outside",
        textfont=dict(color="#c8d6e5", size=10, family="monospace")
    ))
    
    fig.update_layout(
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        xaxis=dict(
            range=[0, 11],
            gridcolor="#1a2538",
            title="Severity Score",
            titlefont=dict(color="#78909c", size=10),
            tickfont=dict(color="#5a6f82")
        ),
        yaxis=dict(
            tickfont=dict(color="#c8d6e5", size=9),
            autorange="reversed"
        ),
        height=max(200, len(verdicts) * 45 + 60),
        margin=dict(t=10, b=40, l=300, r=50),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_probability_vs_impact(verdicts: List[RiskVerdict]):
    """Scatter plot: Probability vs Revenue Impact (bubble = severity)."""
    
    if not verdicts:
        return
    
    fig = go.Figure()
    
    for v in verdicts:
        color = "#FF1744" if v.severity_score >= 8 else "#FF6D00" if v.severity_score >= 6 else "#FFAB00" if v.severity_score >= 4 else "#00E676"
        
        fig.add_trace(go.Scatter(
            x=[v.probability * 100],
            y=[v.revenue_at_risk_pct],
            mode="markers+text",
            marker=dict(
                size=v.severity_score * 4,
                color=color,
                opacity=0.7,
                line=dict(color=color, width=1)
            ),
            text=[v.risk_description[:20] + "..."],
            textposition="top center",
            textfont=dict(size=8, color=color),
            hovertext=f"{v.risk_description[:60]}Severity: {v.severity_score:.1f}Probability: {v.probability:.0%}Revenue at Risk: {v.revenue_at_risk_pct:.1f}%",
            hoverinfo="text",
            showlegend=False
        ))
    
    # Add quadrant lines
    fig.add_hline(y=15, line_dash="dot", line_color="#2a4058", line_width=1)
    fig.add_vline(x=50, line_dash="dot", line_color="#2a4058", line_width=1)
    
    # Quadrant labels
    fig.add_annotation(x=75, y=28, text="CRITICAL ZONE", font=dict(color="#FF1744", size=9), showarrow=False)
    fig.add_annotation(x=25, y=5, text="MONITOR", font=dict(color="#00E676", size=9), showarrow=False)
    
    fig.update_layout(
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        xaxis=dict(
            title="Probability (%)",
            gridcolor="#1a2538",
            range=[0, 100],
            titlefont=dict(color="#78909c", size=10),
            tickfont=dict(color="#5a6f82")
        ),
        yaxis=dict(
            title="Revenue at Risk (%)",
            gridcolor="#1a2538",
            range=[0, max(v.revenue_at_risk_pct for v in verdicts) + 10],
            titlefont=dict(color="#78909c", size=10),
            tickfont=dict(color="#5a6f82")
        ),
        height=320,
        margin=dict(t=20, b=50, l=60, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_debate_panel(verdicts: List[RiskVerdict]):
    """Full debate transcript with expandable sections."""
    
    if not verdicts:
        st.info("No debates to display. Run analysis to see adversarial debate transcripts.")
        return
    
    for i, verdict in enumerate(verdicts):
        # Severity badge
        if verdict.severity_score >= 8: badge_class, badge_text = "rbadge-critical", "CRITICAL"
        elif verdict.severity_score >= 6: badge_class, badge_text = "rbadge-high", "HIGH"
        elif verdict.severity_score >= 4: badge_class, badge_text = "rbadge-elevated", "ELEVATED"
        else: badge_class, badge_text = "rbadge-monitoring", "MONITORING"
        
        with st.expander(f"{'RED' if verdict.severity_score >= 7 else 'YELLOW' if verdict.severity_score >= 4 else 'GREEN'} {verdict.risk_description[:70]}... — Severity: {verdict.severity_score:.1f}/10", expanded=(i == 0)):
            
            # Summary metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Severity", f"{verdict.severity_score:.1f}/10")
            c2.metric("Probability", f"{verdict.probability:.0%}")
            c3.metric("Revenue Risk", f"{verdict.revenue_at_risk_pct:.1f}%")
            c4.metric("Horizon", verdict.time_horizon.replace("_", " "))
            
            # Debate transcript
            st.markdown('', unsafe_allow_html=True)
            
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
                <div class="{msg_class}">
                    <div style="font-size: 0.7em; margin-bottom: 5px; opacity: 0.7;">
                        {role_label} — Round {msg.round_number} (Confidence: {msg.confidence:.0%})
                    </div>
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('', unsafe_allow_html=True)


def render_world_state_panel(ws: WorldState):
    """World state sidebar panel."""
    
    fear_colors = {"CALM": "#00E676", "CAUTIOUS": "#FFAB00", "ANXIOUS": "#FF6D00", "PANIC": "#FF1744"}
    fear_color = fear_colors.get(ws.fear_level, "#FFF")
    
    vix_color = "#FF1744" if ws.vix > 30 else "#FF6D00" if ws.vix > 22 else "#FFAB00" if ws.vix > 16 else "#00E676"
    
    st.markdown(f"""
    <div class="world-state-card" style="border-left: 4px solid {fear_color};">
        <div style="font-size: 0.7em; color: #5a6f82; text-transform: uppercase;">Sentiment</div>
        <div style="font-size: 1.2em; font-weight: bold; color: {fear_color}; margin: 4px 0;">
            {ws.fear_level}
        </div>
        <div style="font-size: 0.6em; color: #5a6f82;">GLOBAL FEAR INDEX</div>
    </div>
    
    <div class="metrics-grid">
        <div class="ws-metric">VIX <span>{ws.vix:.1f}</span></div>
        <div class="ws-metric">USD <span>{ws.dxy:.1f}</span></div>
        <div class="ws-metric">Yield <span>{ws.us_10y_yield:.2f}%</span></div>
        <div class="ws-metric">Oil <span>${ws.oil_brent:.1f}</span></div>
        <div class="ws-metric">Gold <span>${ws.gold:.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Active crises
    if ws.active_crises:
        st.markdown("**Active Crises:**")
        for crisis in ws.active_crises[:4]:
            st.markdown(f"""
            <div style="font-size: 0.75em; color: #c8d6e5; margin-bottom: 6px; padding-left: 10px; border-left: 1px solid #1a2538;">
                >> {crisis.get('title', 'Unknown')[:60]}
            </div>
            """, unsafe_allow_html=True)


def render_dcf_assumptions(valuation: StressedValuation, chaos_level: float):
    """Show DCF model assumptions transparently."""
    
    st.markdown(f"""
    <div class="info-panel">
        <div class="metric-label">DCF Model Assumptions</div>
        <div class="ws-metric">Chaos Level <span>{chaos_level:.0%}</span></div>
        <div class="ws-metric">Base WACC <span>{valuation.base_wacc:.2f}%</span></div>
        <div class="ws-metric">Stressed WACC <span>{valuation.stressed_wacc:.2f}%</span></div>
        <div class="ws-metric">Revenue Haircut <span>{valuation.revenue_haircut:.1f}%</span></div>
        <div class="ws-metric">Margin Compression <span>{valuation.margin_compression_bps:.0f} bps</span></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main application flow."""
    
    # ═══ SESSION STATE ═══
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
        "last_chaos": 0.5
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # ═══ SIDEBAR ═══
    with st.sidebar:
        st.markdown("### DOOMSDAY CONSOLE")
        st.markdown("---")
        
        # Ticker
        ticker = st.text_input(
            "TARGET TICKER",
            value="NVDA",
            help="US: NVDA, MSFT, ASML | India: RELIANCE.NS | Any yfinance ticker"
        ).strip().upper()
        
        st.markdown("---")
        
        # Chaos Slider
        st.markdown("### CHAOS LEVEL")
        chaos_level = st.slider(
            "Stress Intensity",
            min_value=0.0, max_value=1.0,
            value=st.session_state.chaos_level,
            step=0.05,
            help="0 = Base Case -> 1 = Maximum Doomsday"
        )
        st.session_state.chaos_level = chaos_level
        
        # Visual chaos indicator
        if chaos_level <= 0.2:
            st.success("MILD STRESS")
        elif chaos_level <= 0.4:
            st.info("MODERATE STRESS")
        elif chaos_level <= 0.6:
            st.warning("SEVERE STRESS")
        elif chaos_level <= 0.8:
            st.error("CRISIS MODE")
        else:
            st.markdown("DOOMSDAY SCENARIO", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Launch button
        launch = st.button("LAUNCH DOOMSDAY ANALYSIS", type="primary", use_container_width=True)
        
        # World State panel (if available)
        if st.session_state.world_state:
            st.markdown("---")
            st.markdown("### GLOBAL FRACTURE MAP")
            render_fracture_map(
                st.session_state.get("fracture_nodes", []), 
                st.session_state.get("fracture_paths", []),
                st.session_state.get("hq_info")
            )
            st.markdown("### World State")
            render_world_state_panel(st.session_state.world_state)
        
        # DCF assumptions (if available)
        if st.session_state.valuation:
            st.markdown("---")
            st.markdown("### DCF Model")
            render_dcf_assumptions(st.session_state.valuation, chaos_level)
    
    # ═══ MAIN CONTENT ═══
    
    render_header(st.session_state.world_state)
    
    # === LAUNCH ANALYSIS ===
    if launch:
        with st.status("Activating Doomsday Swarm...", expanded=True) as status:
            
            # Step 1: Init clients
            st.write("Initializing AI clients...")
            ai_client = get_ai_client()
            tavily_client = get_tavily_client()
            model = find_best_model(ai_client)
            st.write(f"Model locked: `{model}`")
            
            # Step 2: World State
            st.write("Scanning global threat environment...")
            world_state = fetch_world_state(tavily_client)
            st.session_state.world_state = world_state
            st.write(f"World State: VIX={world_state.vix}, Fear={world_state.fear_level}")
            
            # Step 3: Company Profile
            st.write(f"Building company profile for {ticker}...")
            profile = fetch_company_profile(ticker, ai_client, tavily_client, model)
            if not profile:
                st.error(f"Failed to fetch data for '{ticker}'. Try another ticker (e.g., NVDA, MSFT, AAPL, RELIANCE.NS)")
                st.stop()
            st.session_state.profile = profile
            st.write(f"{profile.name} | Type: **{profile.company_type.value.upper()}** | MCap: ${profile.market_cap/1e9:.1f}B")
            
            # Step 4: Regulatory Filing Intelligence
            st.write(f"Extracting regulatory filing risks ({'SEC EDGAR' if not profile.ticker.endswith('.NS') else 'SEBI/BSE'})...")
            filing_engine = UnifiedFilingEngine(tavily_client=tavily_client)
            filing_risks, filing_source = filing_engine.extract_all_risks(ticker)
            st.session_state.filing_risks = filing_risks
            st.session_state.filing_source = filing_source
            st.write(f"Found {len(filing_risks)} risks from {filing_source}")
            
            # Step 5: Enhanced Intelligence
            st.write("Multi-source intelligence gathering (Filings + News + AI)...")
            risks = run_enhanced_intelligence(ai_client, tavily_client, model, ticker, profile, world_state)
            st.write(f"Identified {len(risks)} potential risks")
            
            # Step 6: Debate
            st.write("Fracture Tribunal -- Adversarial debate in progress...")
            # Compatibility fix for run_adversarial_debate which expects a dict
            company_stub = {"name": profile.name, "sector": profile.sector}
            verdicts = run_adversarial_debate(ai_client, model, ticker, company_stub, risks, world_state)
            st.session_state.verdicts = verdicts
            st.write(f"Tribunal complete: {len(verdicts)} risks validated")
            
            # Step 7: Mapping
            st.write("Mapping fracture points to geographic coordinates...")
            hq_info = None
            try:
                hq_info = fetch_hq_coordinates(ticker, profile.name, ai_client, tavily_client, model)
            except: pass
            
            nodes, paths = run_geographic_mapping(ai_client, model, ticker, verdicts)
            st.session_state.fracture_nodes = nodes
            st.session_state.fracture_paths = paths
            st.session_state.hq_info = hq_info
            st.write(f"Mapped {len(nodes)} fracture nodes, {len(paths)} supply chain paths")
            
            # Step 8: Proper Valuation
            st.write(f"Calculating distressed valuation ({profile.company_type.value} model)...")
            avg_severity = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
            valuation = calculate_proper_valuation(profile, chaos_level, avg_severity)
            st.session_state.valuation = valuation
            st.session_state.last_chaos = chaos_level
            st.write(f"Done - Base: ${valuation.base_fair_value:.2f} -> Distressed: ${valuation.distressed_value:.2f} ({valuation.downside_pct:.1f}%)")
            
            st.session_state.analysis_done = True
            status.update(label="DOOMSDAY ANALYSIS COMPLETE", state="complete", expanded=False)
        
        st.rerun()
    
    # === REAL-TIME CHAOS SLIDER UPDATE (no re-running agents) ===
    if st.session_state.analysis_done and chaos_level != st.session_state.last_chaos:
        profile = st.session_state.profile
        verdicts = st.session_state.verdicts
        if profile and verdicts is not None:
            avg_severity = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
            valuation = calculate_proper_valuation(profile, chaos_level, avg_severity)
            st.session_state.valuation = valuation
            st.session_state.last_chaos = chaos_level
    
    # === RENDER RESULTS ===
    if st.session_state.analysis_done:
        valuation = st.session_state.valuation
        verdicts = st.session_state.verdicts
        nodes = st.session_state.get("fracture_nodes", [])
        paths = st.session_state.get("fracture_paths", [])
        world_state = st.session_state.world_state
        profile = st.session_state.profile
        
        # --- METRICS ROW ---
        render_metrics_row(valuation, verdicts, world_state)
        
        # --- MAP SECTION ---
        st.markdown('GLOBAL FRACTURE MAP -- Vulnerability Nodes', unsafe_allow_html=True)
        render_fracture_map(nodes, paths, st.session_state.get("hq_info"))
        
        # --- CHARTS ROW 1: Waterfall + Risk Radar ---
        st.markdown('VALUATION DESTRUCTION ANALYSIS', unsafe_allow_html=True)
        col_waterfall, col_radar = st.columns([3, 2])
        
        with col_waterfall:
            render_waterfall_chart(valuation)
        
        with col_radar:
            st.markdown("**Risk Domain Intensity**")
            render_risk_radar(verdicts)
        
        # --- CHARTS ROW 2: Severity Bar + Probability/Impact Scatter ---
        st.markdown('RISK QUANTIFICATION', unsafe_allow_html=True)
        col_sev, col_scatter = st.columns([1, 1])
        
        with col_sev:
            st.markdown("**Risk Severity Ranking**")
            render_severity_timeline(verdicts)
        
        with col_scatter:
            st.markdown("**Probability vs Impact Matrix**")
            render_probability_vs_impact(verdicts)
        
        # --- DEBATE SECTION ---
        st.markdown('FRACTURE TRIBUNAL -- ADVERSARIAL DEBATE TRANSCRIPTS', unsafe_allow_html=True)
        render_debate_panel(verdicts)
        
        # --- SUMMARY / IC MEMO ---
        st.markdown('VALUATION METHODOLOGY & FILINGS', unsafe_allow_html=True)
        col_method, col_filings = st.columns([1, 1])
        
        with col_method:
            render_valuation_method_panel(st.session_state.profile, valuation)
        
        with col_filings:
            render_filing_intelligence_panel(
                st.session_state.get("filing_risks", []),
                st.session_state.get("filing_source", "Unknown")
            )

        st.markdown('INVESTMENT COMMITTEE SUMMARY', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="info-panel">
                <div class="doom-title" style="font-size: 1em; margin-bottom: 12px;">Doomsday Assessment: {profile.name}</div>
                <div style="font-size: 0.85em;">
                    <div class="world-state-item"><span class="ws-label">Ticker</span><span class="ws-value">{profile.ticker}</span></div>
                    <div class="world-state-item"><span class="ws-label">Current Price</span><span class="ws-value">${valuation.current_price:.2f}</span></div>
                    <div class="world-state-item"><span class="ws-label">Base Fair Value</span><span class="ws-value">${valuation.base_fair_value:.2f}</span></div>
                    <div class="world-state-item"><span class="ws-label">Distressed Value</span><span class="ws-value">${valuation.distressed_value:.2f}</span></div>
                    <div class="world-state-item"><span class="ws-label">Implied Downside</span><span class="ws-value" style="color: {'#ff1744' if valuation.downside_pct < 0 else '#00e676'}">{valuation.downside_pct:.1f}%</span></div>
                    <div class="world-state-item"><span class="ws-label">Chaos Level Applied</span><span class="ws-value">{chaos_level:.0%}</span></div>
                    <div class="world-state-item"><span class="ws-label">Risks Validated</span><span class="ws-value">{len(verdicts)}</span></div>
                    <div class="world-state-item"><span class="ws-label">Fracture Nodes</span><span class="ws-value">{len(nodes)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            if verdicts:
                top_risks_html = ""
                for i, v in enumerate(sorted(verdicts, key=lambda x: x.severity_score, reverse=True)[:5]):
                    color = "#FF1744" if v.severity_score >= 7 else "#FF6D00" if v.severity_score >= 5 else "#FFAB00"
                    top_risks_html += f'<div style="margin-bottom: 8px; border-bottom: 1px solid #1a2538; padding-bottom: 4px;"><span style="color: {color}; font-weight: bold;">[{v.severity_score:.1f}]</span> <span style="font-size: 0.85em; color: #c8d6e5;">{v.risk_description[:80]}...</span></div>'
                
                st.markdown(f"""
                <div class="info-panel">
                    <div style="font-size: 0.7em; color: #5a6f82; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Top Risks by Severity</div>
                    {top_risks_html}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # === LANDING STATE ===
        st.markdown("""
        <div class="landing-hero">
            <div style="font-size: 80px; margin-bottom: 20px;">[!]</div>
            <div class="hero-title">AWAITING TARGET</div>
            <div class="hero-subtitle">
                Enter a ticker symbol and launch analysis to activate the Doomsday Swarm.
                The system will scan global intelligence across 5 domains, run adversarial debates 
                between AI agents, map geographic vulnerabilities, and compute distressed valuations.
            </div>
            <div style="margin-top: 60px; display: flex; justify-content: center; gap: 40px; color: #8a9ba8;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 10px;">[INTEL]</div>
                    <div style="font-size: 0.7em; text-transform: uppercase;">5-Domain Intelligence</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 10px;">[DEBATE]</div>
                    <div style="font-size: 0.7em; text-transform: uppercase;">Adversarial Debate</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 10px;">[MAP]</div>
                    <div style="font-size: 0.7em; text-transform: uppercase;">Fracture Mapping</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 10px;">[VALUE]</div>
                    <div style="font-size: 0.7em; text-transform: uppercase;">Vulture DCF</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
