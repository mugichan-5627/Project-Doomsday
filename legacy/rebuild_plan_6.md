PART 5: CRITICAL FIXES FOR YOUR EXISTING TROUBLES
Fix 1: Model Availability (Improved Brute-Force Hunter)
# utils/model_hunter.py
"""
Intelligent model selection with fallback chain.
"""

from google import genai
from google.genai import types
import time


class ModelHunter:
    """Finds the best available Gemini model for the user's account."""
    
    # Priority order (best to worst)
    MODEL_PRIORITY = [
        "gemini-2.5-flash-preview-04-17",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    
    def __init__(self, client: genai.Client):
        self.client = client
        self._cached_model = None
    
    def get_best_model(self) -> str:
        """Find and cache the best available model."""
        if self._cached_model:
            return self._cached_model
        
        for model in self.MODEL_PRIORITY:
            if self._test_model(model):
                self._cached_model = model
                print(f"✅ Selected model: {model}")
                return model
        
        raise RuntimeError("No Gemini models available. Check API key and quota.")
    
    def _test_model(self, model: str) -> bool:
        """Quick test if a model responds."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents="Say 'ok'",
                config=types.GenerateContentConfig(
                    max_output_tokens=5,
                    temperature=0.0
                )
            )
            return response.text is not None
        except Exception as e:
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
                print(f"  ❌ {model}: Not available")
            elif "429" in error_str or "quota" in error_str:
                print(f"  ⚠️ {model}: Quota exceeded, trying next...")
            else:
                print(f"  ❌ {model}: {e}")
            return False
Fix 2: JSON Parsing Robustness
# utils/json_normalizer.py
"""
Robust JSON extraction from LLM outputs.
Handles markdown code blocks, partial JSON, and common LLM quirks.
"""

import json
import re
from typing import Any, Optional


def extract_json(text: str) -> Optional[Any]:
    """
    Extract JSON from LLM output, handling common formatting issues.
    """
    if not text:
        return None
    
    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract from markdown code block
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{[\s\S]*\}',
        r'$$[\s\S]*$$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                candidate = match.group(1) if match.lastindex else match.group(0)
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    
    # Strategy 3: Fix common issues
    cleaned = text.strip()
    # Remove trailing commas before } or ]
    cleaned = re.sub(r',\s*([}$$])', r'\1', cleaned)
    # Fix single quotes to double quotes
    cleaned = cleaned.replace("'", '"')
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Strategy 4: Return None (caller should handle)
    return None


def safe_get(data: Any, *keys, default=None):
    """Safely navigate nested dict/list structures."""
    current = data
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        except (KeyError, IndexError, TypeError):
            return default
    return current
Fix 3: Caching Layer (Avoid Redundant API Calls)
# utils/cache.py
"""
Simple TTL cache to avoid hammering APIs during development/demo.
"""

import time
import hashlib
import json
from typing import Any, Optional
from functools import wraps


class TTLCache:
    """Simple in-memory TTL cache."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, timestamp = self._store[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self._store[key]
        return None
    
    def set(self, key: str, value: Any):
        self._store[key] = (value, time.time())
    
    def make_key(self, *args) -> str:
        """Create a cache key from arguments."""
        raw = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()


# Global cache instances
world_state_cache = TTLCache(ttl_seconds=300)  # 5 min
intelligence_cache = TTLCache(ttl_seconds=600)  # 10 min
financials_cache = TTLCache(ttl_seconds=60)     # 1 min
PART 6: HACKATHON PRESENTATION STRATEGY
6.1 Demo Script (3-minute pitch)
## DEMO FLOW:

**[0:00-0:20] HOOK**
"What would happen to your portfolio if Taiwan was invaded tomorrow? 
If the Suez Canal closed again? If a major cloud provider went down?"
[Show blank Doomsday interface — dark, ominous]

**[0:20-0:50] THE PROBLEM**
"Traditional financial models only model upside. But the risks that destroy 
companies aren't in Excel models — they're in geopolitics, supply chains, 
and black swan events. We built an AI swarm that thinks like a short seller."

**[0:50-1:30] LIVE DEMO**
[Type "TSM" (TSMC) — the perfect demo ticker because:
  - Massive geopolitical risk (Taiwan/China)
  - Clear supply chain dependencies
  - Specific geographic vulnerabilities
  - Everyone knows the company]
  
[Click LAUNCH — show progress bar with stage names]
[Map populates with fracture nodes across Taiwan Strait, shipping lanes, etc.]

**[1:30-2:15] THE DIFFERENTIATORS**
"Three things make this different:"
1. "Our agents DEBATE each other" [Show debate transcript]
   "The Bear says TSMC loses 40% revenue. The Bull says they have Japan fabs.
   The Judge weighs evidence and assigns a calibrated severity score."
   
2. "It's grounded in real-time data" [Point to World State panel]
   "VIX at 28, GPR rising, Taiwan Strait tensions elevated — this isn't 
   hallucinated risk, it's calibrated to TODAY's world."
   
3. "The valuation is auditable" [Drag Chaos Slider — waterfall updates live]
   "Every dollar of value destruction is attributable to a specific risk.
   No black boxes."

**[2:15-2:45] THE NUMBERS**
[Show waterfall chart]
"At current chaos levels, our distressed DCF gives TSMC a fair value of $XX 
— a XX% downside from current market price. Here's exactly where that 
value gets destroyed."

**[2:45-3:00] CLOSE**
"This is Project Doomsday. Built for PE firms, distressed investors, and 
anyone who needs to know what breaks before it breaks."
6.2 Killer Demo Tickers (Pick Based on Current Events)
Ticker	Why It's Perfect for Demo
TSM (TSMC)	Taiwan/China, semiconductor dependency, everyone knows it
ASML	Similar to TSM but European angle
MAERSK (AMKBY)	Red Sea/Suez, global shipping
NVDA	AI hype vs. export controls, concentration risk
BABA	China regulatory, US delisting, geopolitical
My recommendation: Demo TSM. It hits every visual element — the Taiwan Strait lights up red on the map, shipping lanes show orange supply chain paths, Japan/Arizona fabs show green (mitigation), and the debate between "China invasion risk" Bull vs Bear is viscerally compelling.

PART 7: WHAT WILL MAKE JUDGES GO "WOW"
Based on the Milan AI Week hackathon criteria:

7.1 Technical Innovation
Multi-agent adversarial debate (not just sequential LLM calls)
Real-time world state calibration (grounded AI, not hallucinating)
Deterministic DCF engine (LLM qualitative → math quantitative)
7.2 Visual Impact
Dark-mode military aesthetic (like the worldmonitor screenshots)
Pulsing severity markers on global map
Supply chain path lines connecting fracture nodes
Live waterfall chart that collapses as you drag the slider
7.3 Business Value
Clear buyer: PE firms, hedge funds, risk committees
Actionable output: Not just "risks" but a distressed valuation with a price target
Audit trail: Full debate transcript shows WHY each risk was validated
7.4 Things to Add If You Have Time
PDF Export: Auto-generate IC memo as PDF (one button)
Historical Backtesting: "Here's what Doomsday would have flagged for SVB in January 2023"
Sound effects: Subtle alert sound when critical risk is detected (seriously, this works in demos)
DEFCON-style meter: Like worldmonitor's DEFCON indicator in the top bar
PART 8: CONFIG & ENVIRONMENT
# config.py
"""
Project Doomsday Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Model preferences
    PREFERRED_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17")
    
    # Pipeline settings
    DEBATE_ROUNDS = 2  # Reduce to 2 for speed during demo
    MAX_RISKS_TO_DEBATE = 6  # Don't debate more than 6 risks (latency)
    
    # Map settings
    MAPBOX_STYLE = "carto-darkmatter"
    DEFAULT_MAP_CENTER = {"lat": 25, "lon": 50}
    DEFAULT_MAP_ZOOM = 1.8
    
    # DCF settings
    PROJECTION_YEARS = 5
    RISK_FREE_RATE = 0.045
    EQUITY_RISK_PREMIUM = 0.055
    
    # Cache TTLs (seconds)
    WORLD_STATE_TTL = 300
    INTELLIGENCE_TTL = 600
    
    @classmethod
    def validate(cls):
        """Check all required config is present."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if missing:
            raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
# .env.example
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GEMINI_MODEL=gemini-2.5-flash-preview-04-17
SUMMARY: YOUR ACTION PLAN
Priority 1 (Must Ship for Hackathon):
Task	Time Estimate	Status
World State Engine	2 hours	New
Sentinel v2 (parallel multi-domain)	3 hours	Upgrade
Debate Engine (2-round version)	4 hours	New — differentiator
Saboteur v2 (map-ready output)	2 hours	Upgrade
Vulture DCF (deterministic)	3 hours	New
Streamlit UI (dark theme + map)	4 hours	Upgrade
Total	~18 hours	
Priority 2 (Nice to Have):
Full 3-round debates (vs 2-round)
Supply chain path visualization (lines on map)
PDF IC memo export
Backtesting example
Priority 3 (Mention in Pitch, Don't Build):
Real-time streaming updates
Multi-ticker portfolio analysis
Integration with Bloomberg/Refinitiv
Mobile app version