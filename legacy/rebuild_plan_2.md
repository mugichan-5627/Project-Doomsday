1.3 World State Engine (The Missing Calibration Layer)
# world_state.py
"""
Real-time World State Generator
Provides calibration context for all agents.
"""

import yfinance as yf
from tavily import TavilyClient
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from datetime import datetime


@dataclass
class WorldState:
    """Structured snapshot of current global conditions."""
    timestamp: str
    
    # Market Fear Gauges
    vix: float
    vix_trend: str  # "rising", "falling", "stable"
    
    # Currency & Rates
    dxy: float  # Dollar index
    us_10y_yield: float
    
    # Commodities
    oil_brent: float
    gold: float
    
    # Geopolitical
    gpr_index: Optional[float]  # Geopolitical Risk Index
    active_crises: List[Dict]  # From Tavily real-time
    
    # Derived
    fear_level: str  # "CALM", "CAUTIOUS", "ANXIOUS", "PANIC"
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "market_fear": {
                "vix": self.vix,
                "vix_trend": self.vix_trend,
                "fear_level": self.fear_level
            },
            "macro": {
                "dxy": self.dxy,
                "us_10y_yield": self.us_10y_yield,
                "oil_brent": self.oil_brent,
                "gold": self.gold
            },
            "geopolitical": {
                "gpr_index": self.gpr_index,
                "active_crises": self.active_crises
            }
        }
    
    def to_prompt_context(self) -> str:
        """Human-readable context for LLM prompts."""
        return f"""
🌍 CURRENT WORLD STATE (as of {self.timestamp}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEAR LEVEL: {self.fear_level}
VIX: {self.vix} ({self.vix_trend})
US Dollar (DXY): {self.dxy}
US 10Y Yield: {self.us_10y_yield}%
Brent Crude: ${self.oil_brent}
Gold: ${self.gold}

ACTIVE GLOBAL CRISES:
{chr(10).join([f"  ⚠️ {c['title']} (Severity: {c.get('severity', 'unknown')})" for c in self.active_crises[:5]])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class WorldStateEngine:
    """Generates real-time world state for agent calibration."""
    
    # Ticker mappings for macro indicators
    INDICATORS = {
        "vix": "^VIX",
        "dxy": "DX-Y.NYB",
        "us_10y": "^TNX",
        "oil_brent": "BZ=F",
        "gold": "GC=F"
    }
    
    def __init__(self, tavily_api_key: str):
        self.tavily = TavilyClient(api_key=tavily_api_key)
    
    def generate(self) -> WorldState:
        """Pull all data and construct world state."""
        
        # Fetch market data
        market_data = self._fetch_market_data()
        
        # Fetch active crises
        crises = self._fetch_active_crises()
        
        # Calculate fear level
        vix = market_data.get("vix", 20.0)
        fear_level = self._calculate_fear_level(vix, market_data)
        
        # VIX trend (compare to 5-day average)
        vix_trend = self._calculate_vix_trend()
        
        return WorldState(
            timestamp=datetime.utcnow().isoformat() + "Z",
            vix=vix,
            vix_trend=vix_trend,
            dxy=market_data.get("dxy", 104.0),
            us_10y_yield=market_data.get("us_10y", 4.5),
            oil_brent=market_data.get("oil_brent", 80.0),
            gold=market_data.get("gold", 2400.0),
            gpr_index=None,  # Would need GPR API or proxy
            active_crises=crises,
            fear_level=fear_level
        )
    
    def _fetch_market_data(self) -> Dict:
        """Fetch current market indicators via yfinance."""
        data = {}
        for key, ticker in self.INDICATORS.items():
            try:
                info = yf.Ticker(ticker)
                hist = info.history(period="1d")
                if not hist.empty:
                    data[key] = round(hist['Close'].iloc[-1], 2)
            except Exception as e:
                print(f"Warning: Could not fetch {key} ({ticker}): {e}")
        return data
    
    def _fetch_active_crises(self) -> List[Dict]:
        """Use Tavily to find current global crises."""
        try:
            result = self.tavily.search(
                query="major global crisis geopolitical conflict 2024 2025",
                search_depth="advanced",
                max_results=5,
                include_answer=True
            )
            
            crises = []
            for r in result.get("results", []):
                crises.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:200],
                    "severity": "HIGH"  # Could be refined with NLP
                })
            return crises
        except Exception as e:
            print(f"Warning: Tavily crisis fetch failed: {e}")
            return []
    
    def _calculate_fear_level(self, vix: float, data: Dict) -> str:
        """Multi-factor fear classification."""
        score = 0
        
        # VIX thresholds
        if vix >= 35: score += 3
        elif vix >= 25: score += 2
        elif vix >= 18: score += 1
        
        # Gold above $2500 = flight to safety
        if data.get("gold", 0) > 2500: score += 1
        
        # Oil above $95 = supply stress
        if data.get("oil_brent", 0) > 95: score += 1
        
        # 10Y yield above 5% = rate stress
        if data.get("us_10y", 0) > 5.0: score += 1
        
        if score >= 5: return "PANIC"
        elif score >= 3: return "ANXIOUS"
        elif score >= 2: return "CAUTIOUS"
        else: return "CALM"
    
    def _calculate_vix_trend(self) -> str:
        """5-day VIX trend."""
        try:
            vix_hist = yf.Ticker("^VIX").history(period="5d")
            if len(vix_hist) >= 2:
                change = vix_hist['Close'].iloc[-1] - vix_hist['Close'].iloc[0]
                if change > 2: return "rising"
                elif change < -2: return "falling"
            return "stable"
        except:
            return "stable"
1.4 Enhanced Sentinel (Parallel Multi-Domain Intelligence)
# sentinel.py
"""
Global Sentinel v2: Multi-Domain Parallel Intelligence Gathering
"""

import asyncio
import json
from typing import List, Dict
from google import genai
from google.genai import types
from tavily import TavilyClient
from dataclasses import dataclass


@dataclass
class RawRisk:
    id: str
    domain: str  # "geopolitical", "supply_chain", "financial", "regulatory", "cyber"
    description: str
    evidence: List[str]
    initial_severity: int  # 1-10 (pre-debate)
    geographic_hint: str
    affected_revenue_pct: float  # Estimated % of revenue at risk


class GlobalSentinel:
    """
    Multi-domain intelligence gatherer.
    Runs 3 parallel searches, then synthesizes.
    """
    
    DOMAINS = {
        "geopolitical": {
            "query_template": "{company} geopolitical risk sanctions trade war tariff exposure 2024 2025",
            "focus": "government actions, sanctions, trade restrictions, diplomatic tensions"
        },
        "supply_chain": {
            "query_template": "{company} supply chain disruption shortage factory shutdown logistics",
            "focus": "manufacturing concentration, shipping routes, supplier dependencies, inventory risks"
        },
        "financial": {
            "query_template": "{company} debt refinancing credit downgrade liquidity crisis revenue decline",
            "focus": "balance sheet stress, covenant triggers, customer concentration, margin compression"
        },
        "regulatory": {
            "query_template": "{company} regulatory investigation antitrust fine compliance lawsuit",
            "focus": "pending legislation, enforcement actions, industry regulation changes"
        },
        "cyber_tech": {
            "query_template": "{company} cybersecurity breach data leak technology disruption AI replacement",
            "focus": "technology obsolescence, data privacy, platform dependency, AI displacement"
        }
    }
    
    SYNTHESIS_PROMPT = """You are an institutional-grade risk analyst. You have been given raw search results 
across multiple domains for a specific company. Your task is to identify the TOP 5-8 most material risks 
that could cause significant valuation impairment.

RULES:
1. Each risk must be SPECIFIC (not "the economy might slow down")
2. Each risk must have EVIDENCE from the search results (cite sources)
3. Estimate the % of revenue potentially affected
4. Assign an initial severity (1-10) — this will be debated by other agents later
5. Provide a geographic hint (where does this risk physically manifest?)

COMPANY: {ticker}
COMPANY CONTEXT: {company_context}
WORLD STATE: {world_state}

RAW INTELLIGENCE:
{raw_intelligence}

Respond in JSON:
{{
    "risks": [
        {{
            "id": "RISK_001",
            "domain": "geopolitical|supply_chain|financial|regulatory|cyber_tech",
            "description": "Specific risk description",
            "evidence": ["Source 1 quote", "Source 2 quote"],
            "initial_severity": 1-10,
            "geographic_hint": "Country or Region or City",
            "affected_revenue_pct": 0.0-100.0
        }}
    ]
}}
"""
    
    def __init__(self, gemini_client: genai.Client, tavily_client: TavilyClient, model: str):
        self.gemini = gemini_client
        self.tavily = tavily_client
        self.model = model
    
    async def gather_intelligence(
        self, 
        ticker: str, 
        company_context: str,
        world_state_text: str
    ) -> List[RawRisk]:
        """Parallel multi-domain intelligence gathering."""
        
        # Phase 1: Parallel Tavily searches across all domains
        search_tasks = []
        for domain, config in self.DOMAINS.items():
            query = config["query_template"].format(company=ticker.replace(".NS", ""))
            search_tasks.append(self._search_domain(domain, query))
        
        raw_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Compile results (skip failures)
        compiled_intelligence = ""
        for domain, result in zip(self.DOMAINS.keys(), raw_results):
            if isinstance(result, Exception):
                compiled_intelligence += f"\n[{domain.upper()}]: Search failed - {str(result)}\n"
            else:
                compiled_intelligence += f"\n[{domain.upper()}]:\n{result}\n"
        
        # Phase 2: LLM synthesis of all intelligence
        prompt = self.SYNTHESIS_PROMPT.format(
            ticker=ticker,
            company_context=company_context,
            world_state=world_state_text,
            raw_intelligence=compiled_intelligence
        )
        
        response = await asyncio.to_thread(
            self.gemini.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
        )
        
        # Parse response
        try:
            parsed = json.loads(response.text)
            risks = []
            for r in parsed.get("risks", []):
                risks.append(RawRisk(
                    id=r["id"],
                    domain=r["domain"],
                    description=r["description"],
                    evidence=r.get("evidence", []),
                    initial_severity=r.get("initial_severity", 5),
                    geographic_hint=r.get("geographic_hint", "Unknown"),
                    affected_revenue_pct=r.get("affected_revenue_pct", 10.0)
                ))
            return risks
        except json.JSONDecodeError:
            # Fallback: return raw text as a single risk
            return [RawRisk(
                id="RISK_PARSE_FAIL",
                domain="unknown",
                description=response.text[:500],
                evidence=[],
                initial_severity=5,
                geographic_hint="Unknown",
                affected_revenue_pct=10.0
            )]
    
    async def _search_domain(self, domain: str, query: str) -> str:
        """Single domain search via Tavily."""
        try:
            result = await asyncio.to_thread(
                self.tavily.search,
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            formatted = []
            for r in result.get("results", []):
                formatted.append(f"- [{r.get('title', 'No title')}] {r.get('content', '')[:300]}")
            
            return "\n".join(formatted) if formatted else "No results found."
        except Exception as e:
            raise Exception(f"Tavily search failed for {domain}: {str(e)}")