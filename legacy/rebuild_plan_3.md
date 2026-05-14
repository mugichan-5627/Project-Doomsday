1.5 Logistics Saboteur v2 (Beautiful Map-Ready Output)
# saboteur.py
"""
Logistics Saboteur v2: Converts validated risks into precise Fracture Nodes
with severity, category, and rich metadata for visualization.
Inspired by: worldmonitor & globalthreatmap map interfaces
"""

import json
from typing import List, Dict
from dataclasses import dataclass, field
from google import genai
from google.genai import types


@dataclass
class FractureNode:
    """A single point on the Fracture Map."""
    node_id: str
    latitude: float
    longitude: float
    
    # Display properties
    label: str  # Short name for map marker
    description: str  # Full description for popup
    
    # Classification (maps to visual encoding)
    category: str  # "conflict", "supply_chain", "regulatory", "financial", "cyber", "infrastructure"
    severity: float  # 1-10 (from debate verdict)
    probability: float  # 0-1 (from debate verdict)
    
    # Threat level for color coding
    threat_level: str  # "critical", "high", "elevated", "monitoring"
    
    # Rich metadata
    risk_id: str  # Links back to debate verdict
    affected_assets: List[str] = field(default_factory=list)  # Ports, factories, cables, etc.
    time_horizon: str = "6_months"
    revenue_at_risk_pct: float = 0.0
    
    # For connecting related nodes (supply chain paths)
    connected_to: List[str] = field(default_factory=list)  # Other node_ids
    
    def to_map_dict(self) -> Dict:
        """Format for Plotly/Mapbox rendering."""
        return {
            "lat": self.latitude,
            "lon": self.longitude,
            "label": self.label,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "probability": self.probability,
            "threat_level": self.threat_level,
            "size": self._calculate_marker_size(),
            "color": self._get_threat_color(),
            "opacity": min(0.9, 0.3 + (self.probability * 0.6)),
            "affected_assets": self.affected_assets,
            "revenue_at_risk": f"{self.revenue_at_risk_pct:.1f}%",
            "time_horizon": self.time_horizon
        }
    
    def _calculate_marker_size(self) -> int:
        """Marker size based on severity and revenue impact."""
        base = 8
        severity_bonus = self.severity * 2
        revenue_bonus = self.revenue_at_risk_pct * 0.3
        return int(base + severity_bonus + revenue_bonus)
    
    def _get_threat_color(self) -> str:
        """Color coding matching worldmonitor aesthetic."""
        colors = {
            "critical": "#FF1744",   # Red
            "high": "#FF6D00",       # Orange
            "elevated": "#FFD600",   # Yellow
            "monitoring": "#00E676"  # Green
        }
        return colors.get(self.threat_level, "#FFFFFF")


GEOCODING_PROMPT = """You are a geospatial intelligence analyst. Given validated risks from a financial 
risk tribunal, your job is to map each risk to PRECISE physical locations on Earth.

RULES:
1. Each risk maps to 1-3 geographic nodes (where the risk physically manifests)
2. Use EXACT coordinates (not approximate) - think specific ports, factories, government buildings, data centers
3. Identify the specific infrastructure at risk (e.g., "Port of Shanghai", "TSMC Fab 18 Tainan", "Strait of Hormuz")
4. Assign appropriate categories for map visualization
5. If a risk has a SUPPLY CHAIN PATH, create connected nodes showing the flow

CATEGORIES: conflict, supply_chain, regulatory, financial, cyber, infrastructure

COMPANY: {ticker}
VALIDATED RISKS:
{risks_json}

Respond in JSON:
{{
    "fracture_nodes": [
        {{
            "node_id": "NODE_001",
            "risk_id": "RISK_001",
            "latitude": 31.2304,
            "longitude": 121.4737,
            "label": "Shanghai Port Complex",
            "description": "Primary export hub handling 40% of company's APAC shipments. Vulnerable to Taiwan Strait escalation.",
            "category": "supply_chain",
            "severity": 7.5,
            "probability": 0.4,
            "threat_level": "high",
            "affected_assets": ["Yangshan Deep Water Port", "Container Terminal 4"],
            "time_horizon": "3_months",
            "revenue_at_risk_pct": 15.0,
            "connected_to": ["NODE_002"]
        }}
    ],
    "supply_chain_paths": [
        {{
            "path_id": "PATH_001",
            "nodes": ["NODE_001", "NODE_002", "NODE_003"],
            "description": "Critical semiconductor supply route: Taiwan → Shanghai → Rotterdam",
            "vulnerability_score": 8.0
        }}
    ]
}}
"""


class LogisticsSaboteur:
    """Converts debate-validated risks into mappable Fracture Nodes."""
    
    def __init__(self, gemini_client: genai.Client, model: str):
        self.gemini = gemini_client
        self.model = model
    
    async def map_risks(
        self, 
        ticker: str, 
        validated_risks: List[Dict]
    ) -> tuple[List[FractureNode], List[Dict]]:
        """
        Convert validated risks to geographic fracture nodes.
        Returns (nodes, supply_chain_paths)
        """
        import asyncio
        
        risks_json = json.dumps(validated_risks, indent=2)
        
        prompt = GEOCODING_PROMPT.format(
            ticker=ticker,
            risks_json=risks_json
        )
        
        response = await asyncio.to_thread(
            self.gemini.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # Low temp for factual geo data
                response_mime_type="application/json"
            )
        )
        
        try:
            parsed = json.loads(response.text)
        except json.JSONDecodeError:
            # Attempt to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                parsed = {"fracture_nodes": [], "supply_chain_paths": []}
        
        nodes = []
        for n in parsed.get("fracture_nodes", []):
            try:
                node = FractureNode(
                    node_id=n["node_id"],
                    latitude=float(n["latitude"]),
                    longitude=float(n["longitude"]),
                    label=n["label"],
                    description=n["description"],
                    category=n.get("category", "infrastructure"),
                    severity=float(n.get("severity", 5.0)),
                    probability=float(n.get("probability", 0.5)),
                    threat_level=n.get("threat_level", "elevated"),
                    risk_id=n.get("risk_id", "unknown"),
                    affected_assets=n.get("affected_assets", []),
                    time_horizon=n.get("time_horizon", "6_months"),
                    revenue_at_risk_pct=float(n.get("revenue_at_risk_pct", 5.0)),
                    connected_to=n.get("connected_to", [])
                )
                # Validate coordinates
                if -90 <= node.latitude <= 90 and -180 <= node.longitude <= 180:
                    nodes.append(node)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Warning: Skipping malformed node: {e}")
                continue
        
        paths = parsed.get("supply_chain_paths", [])
        
        return nodes, paths
1.6 Vulture Architect (Deterministic DCF with Chaos Multipliers)
# vulture_dcf.py
"""
Vulture Architect: Distressed DCF Engine
The LLM provides qualitative severity → deterministic math produces valuations.
No hallucinated numbers.
"""

import yfinance as yf
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np


@dataclass
class CompanyFinancials:
    """Base case financials from yfinance."""
    ticker: str
    current_price: float
    market_cap: float
    revenue_ttm: float
    ebitda_ttm: float
    net_income_ttm: float
    free_cash_flow_ttm: float
    total_debt: float
    cash: float
    shares_outstanding: float
    beta: float
    sector: str
    
    # Derived
    ev: float = 0.0  # Enterprise Value
    ebitda_margin: float = 0.0
    fcf_yield: float = 0.0
    net_debt: float = 0.0
    
    def __post_init__(self):
        self.net_debt = self.total_debt - self.cash
        self.ev = self.market_cap + self.net_debt
        if self.revenue_ttm > 0:
            self.ebitda_margin = self.ebitda_ttm / self.revenue_ttm
        if self.market_cap > 0:
            self.fcf_yield = self.free_cash_flow_ttm / self.market_cap


@dataclass
class ChaosScenario:
    """A stress scenario with specific financial impacts."""
    name: str  # e.g., "Base Case", "Moderate Stress", "Severe Distress", "Doomsday"
    chaos_level: float  # 0.0 to 1.0 (maps to slider)
    
    # Revenue impact
    revenue_haircut_pct: float  # e.g., -15.0 means 15% revenue decline
    
    # Margin impact
    margin_compression_bps: float  # e.g., 300 = 3% margin compression
    
    # Cost of capital impact
    wacc_adder_bps: float  # e.g., 200 = 2% higher WACC
    
    # Terminal value impact
    terminal_multiple_haircut: float  # e.g., -2.0x reduction in exit multiple
    
    # Probability weighting
    scenario_probability: float  # 0.0 to 1.0


@dataclass
class VultureValuation:
    """Complete distressed valuation output."""
    ticker: str
    
    # Base case
    base_fair_value: float
    base_per_share: float
    
    # Distressed case
    distressed_fair_value: float
    distressed_per_share: float
    
    # Downside
    downside_pct: float
    
    # Components
    scenarios: List[ChaosScenario] = field(default_factory=list)
    dcf_assumptions: Dict = field(default_factory=dict)
    
    # Waterfall data for visualization
    waterfall_data: List[Dict] = field(default_factory=list)


class VultureArchitect:
    """
    Deterministic DCF engine that takes chaos factors from the Tribunal
    and produces auditable distressed valuations.
    """
    
    # Sector-specific base assumptions
    SECTOR_ASSUMPTIONS = {
        "Technology": {"base_growth": 0.12, "terminal_growth": 0.03, "base_multiple": 25.0},
        "Healthcare": {"base_growth": 0.08, "terminal_growth": 0.03, "base_multiple": 18.0},
        "Financial Services": {"base_growth": 0.06, "terminal_growth": 0.02, "base_multiple": 12.0},
        "Energy": {"base_growth": 0.04, "terminal_growth": 0.02, "base_multiple": 8.0},
        "Consumer Cyclical": {"base_growth": 0.07, "terminal_growth": 0.025, "base_multiple": 15.0},
        "Industrials": {"base_growth": 0.06, "terminal_growth": 0.025, "base_multiple": 14.0},
        "default": {"base_growth": 0.06, "terminal_growth": 0.025, "base_multiple": 15.0}
    }
    
    # Chaos level to financial impact mapping
    CHAOS_MATRIX = {
        # chaos_level: (revenue_haircut, margin_compression_bps, wacc_adder_bps, multiple_haircut)
        0.0: (0.0, 0, 0, 0.0),       # Base case
        0.2: (-5.0, 100, 50, -1.0),   # Mild stress
        0.4: (-12.0, 200, 100, -2.5),  # Moderate stress
        0.6: (-20.0, 350, 200, -4.0),  # Severe stress
        0.8: (-30.0, 500, 300, -6.0),  # Crisis
        1.0: (-45.0, 750, 500, -8.0),  # Doomsday
    }
    
    def __init__(self):
        pass
    
    def fetch_financials(self, ticker: str) -> Optional[CompanyFinancials]:
        """Pull base financials from yfinance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Handle missing data gracefully
            financials = CompanyFinancials(
                ticker=ticker,
                current_price=info.get("currentPrice", info.get("previousClose", 0)),
                market_cap=info.get("marketCap", 0),
                revenue_ttm=info.get("totalRevenue", 0),
                ebitda_ttm=info.get("ebitda", 0),
                net_income_ttm=info.get("netIncomeToCommon", 0),
                free_cash_flow_ttm=info.get("freeCashflow", 0),
                total_debt=info.get("totalDebt", 0),
                cash=info.get("totalCash", 0),
                shares_outstanding=info.get("sharesOutstanding", 1),
                beta=info.get("beta", 1.0) or 1.0,
                sector=info.get("sector", "default")
            )
            
            return financials
        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return None
    
    def calculate_distressed_value(
        self,
        financials: CompanyFinancials,
        chaos_level: float,  # 0.0 to 1.0 (from slider)
        validated_risks: List[Dict] = None,  # From tribunal
        projection_years: int = 5
    ) -> VultureValuation:
        """
        Main valuation engine.
        Combines mechanical chaos multipliers with risk-specific adjustments.
        """
        
        # Get sector assumptions
        sector_key = financials.sector if financials.sector in self.SECTOR_ASSUMPTIONS else "default"
        assumptions = self.SECTOR_ASSUMPTIONS[sector_key]
        
        # Interpolate chaos impacts from matrix
        chaos_impacts = self._interpolate_chaos(chaos_level)
        
        # Adjust chaos impacts based on validated risks (if available)
        if validated_risks:
            chaos_impacts = self._adjust_for_specific_risks(chaos_impacts, validated_risks)
        
        # Calculate base WACC
        risk_free = 0.045  # US 10Y proxy
        equity_premium = 0.055
        base_wacc = risk_free + financials.beta * equity_premium
        
        # === BASE CASE DCF ===
        base_fcf_projections = self._project_fcf(
            base_fcf=financials.free_cash_flow_ttm,
            growth_rate=assumptions["base_growth"],
            years=projection_years
        )
        base_terminal = self._terminal_value(
            final_fcf=base_fcf_projections[-1],
            terminal_growth=assumptions["terminal_growth"],
            wacc=base_wacc
        )
        base_ev = self._discount_cash_flows(
            cash_flows=base_fcf_projections,
            terminal_value=base_terminal,
            wacc=base_wacc
        )
        base_equity = base_ev - financials.net_debt
        base_per_share = max(0, base_equity / financials.shares_outstanding)
        
        # === DISTRESSED CASE DCF ===
        # Apply chaos impacts
        stressed_revenue_growth = assumptions["base_growth"] + (chaos_impacts[0] / 100)
        stressed_wacc = base_wacc + (chaos_impacts[2] / 10000)
        
        # Stress the base FCF by revenue haircut and margin compression
        revenue_impact = 1 + (chaos_impacts[0] / 100)
        margin_impact = 1 - (chaos_impacts[1] / 10000 / financials.ebitda_margin) if financials.ebitda_margin > 0 else 1
        stressed_base_fcf = financials.free_cash_flow_ttm * revenue_impact * margin_impact
        
        distressed_fcf_projections = self._project_fcf(
            base_fcf=stressed_base_fcf,
            growth_rate=max(-0.10, stressed_revenue_growth),  # Floor at -10% perpetual decline
            years=projection_years
        )
        
        stressed_terminal_growth = max(0.0, assumptions["terminal_growth"] - 0.01 * chaos_level)
        distressed_terminal = self._terminal_value(
            final_fcf=distressed_fcf_projections[-1],
            terminal_growth=stressed_terminal_growth,
            wacc=stressed_wacc
        )
        
        distressed_ev = self._discount_cash_flows(
            cash_flows=distressed_fcf_projections,
            terminal_value=distressed_terminal,
            wacc=stressed_wacc
        )
        distressed_equity = distressed_ev - financials.net_debt
        distressed_per_share = max(0, distressed_equity / financials.shares_outstanding)
        
        # Downside calculation
        if financials.current_price > 0:
            downside_pct = ((distressed_per_share - financials.current_price) / financials.current_price) * 100
        else:
            downside_pct = 0.0
        
        # Build waterfall for visualization
        waterfall = self._build_waterfall(
            base_per_share=base_per_share,
            distressed_per_share=distressed_per_share,
            current_price=financials.current_price,
            chaos_impacts=chaos_impacts,
            financials=financials
        )
        
        return VultureValuation(
            ticker=financials.ticker,
            base_fair_value=base_equity,
            base_per_share=round(base_per_share, 2),
            distressed_fair_value=distressed_equity,
            distressed_per_share=round(distressed_per_share, 2),
            downside_pct=round(downside_pct, 1),
            dcf_assumptions={
                "base_wacc": round(base_wacc * 100, 2),
                "stressed_wacc": round(stressed_wacc * 100, 2),
                "revenue_haircut": chaos_impacts[0],
                "margin_compression_bps": chaos_impacts[1],
                "projection_years": projection_years,
                "terminal_growth": assumptions["terminal_growth"],
                "chaos_level": chaos_level
            },
            waterfall_data=waterfall
        )
    
    def _interpolate_chaos(self, level: float) -> Tuple[float, float, float, float]:
        """Linear interpolation between chaos matrix levels."""
        levels = sorted(self.CHAOS_MATRIX.keys())
        
        # Find surrounding levels
        lower = max([l for l in levels if l <= level])
        upper = min([l for l in levels if l >= level])
        
        if lower == upper:
            return self.CHAOS_MATRIX[lower]
        
        # Interpolate
        t = (level - lower) / (upper - lower)
        lower_vals = self.CHAOS_MATRIX[lower]
        upper_vals = self.CHAOS_MATRIX[upper]
        
        return tuple(
            lower_vals[i] + t * (upper_vals[i] - lower_vals[i])
            for i in range(4)
        )
    
    def _adjust_for_specific_risks(
        self, 
        base_impacts: Tuple, 
        validated_risks: List[Dict]
    ) -> Tuple[float, float, float, float]:
        """
        Adjust generic chaos impacts based on specific validated risks.
        This is where tribunal output connects to the DCF.
        """
        if not validated_risks:
            return base_impacts
        
        # Sum up revenue-at-risk from validated risks
        total_revenue_risk = sum(
            r.get("revenue_at_risk_pct", 0) for r in validated_risks
        )
        # Average severity
        avg_severity = sum(
            r.get("severity_score", 5) for r in validated_risks
        ) / len(validated_risks) if validated_risks else 5
        
        # Adjust: if validated risks suggest more revenue at risk than generic chaos
        risk_based_haircut = -min(50, total_revenue_risk * 0.7)  # Cap at -50%
        
        # Take the worse of generic chaos or risk-specific
        revenue_haircut = min(base_impacts[0], risk_based_haircut)
        
        # Severity amplifier for WACC
        severity_multiplier = avg_severity / 5.0  # 1.0 at severity 5, 2.0 at severity 10
        wacc_adder = base_impacts[2] * severity_multiplier
        
        return (revenue_haircut, base_impacts[1], wacc_adder, base_impacts[3])
    
    def _project_fcf(self, base_fcf: float, growth_rate: float, years: int) -> List[float]:
        """Project free cash flows."""
        projections = []
        for year in range(1, years + 1):
            # Declining growth rate as it mean-reverts
            year_growth = growth_rate * (0.9 ** (year - 1))
            if not projections:
                projections.append(base_fcf * (1 + year_growth))
            else:
                projections.append(projections[-1] * (1 + year_growth))
        return projections
    
    def _terminal_value(self, final_fcf: float, terminal_growth: float, wacc: float) -> float:
        """Gordon Growth terminal value."""
        if wacc <= terminal_growth:
            return final_fcf * 15  # Fallback multiple
        return final_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    
    def _discount_cash_flows(
        self, 
        cash_flows: List[float], 
        terminal_value: float, 
        wacc: float
    ) -> float:
        """Discount all cash flows to present value."""
        pv = 0.0
        for i, cf in enumerate(cash_flows, 1):
            pv += cf / (1 + wacc) ** i
        pv += terminal_value / (1 + wacc) ** len(cash_flows)
        return pv
    
    def _build_waterfall(
        self,
        base_per_share: float,
        distressed_per_share: float,
        current_price: float,
        chaos_impacts: Tuple,
        financials: CompanyFinancials
    ) -> List[Dict]:
        """Build waterfall chart data showing value destruction path."""
        total_destruction = base_per_share - distressed_per_share
        
        if total_destruction <= 0:
            return []
        
        # Decompose destruction into factors
        revenue_share = abs(chaos_impacts[0]) / (abs(chaos_impacts[0]) + chaos_impacts[1]/100 + chaos_impacts[2]/100 + abs(chaos_impacts[3])/10 + 0.001)
        margin_share = (chaos_impacts[1]/100) / (abs(chaos_impacts[0]) + chaos_impacts[1]/100 + chaos_impacts[2]/100 + abs(chaos_impacts[3])/10 + 0.001)
        wacc_share = (chaos_impacts[2]/100) / (abs(chaos_impacts[0]) + chaos_impacts[1]/100 + chaos_impacts[2]/100 + abs(chaos_impacts[3])/10 + 0.001)
        multiple_share = 1.0 - revenue_share - margin_share - wacc_share
        
        waterfall = [
            {"label": "Base Fair Value", "value": base_per_share, "type": "start"},
            {"label": "Revenue Destruction", "value": -total_destruction * revenue_share, "type": "negative"},
            {"label": "Margin Compression", "value": -total_destruction * margin_share, "type": "negative"},
            {"label": "Risk Premium (WACC↑)", "value": -total_destruction * wacc_share, "type": "negative"},
            {"label": "Multiple De-rating", "value": -total_destruction * multiple_share, "type": "negative"},
            {"label": "Distressed Value", "value": distressed_per_share, "type": "end"},
            {"label": "Current Price", "value": current_price, "type": "reference"},
        ]
        
        return waterfall