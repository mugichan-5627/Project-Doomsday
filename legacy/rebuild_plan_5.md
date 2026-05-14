PART 3: THE ORCHESTRATOR (Tying It All Together)
3.1 Main Orchestrator Module
# orchestrator.py
"""
Doomsday Orchestrator: Manages the full pipeline execution
with error handling, retries, and state management.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum


class PipelineStage(Enum):
    WORLD_STATE = "world_state"
    FINANCIALS = "financials"
    INTELLIGENCE = "intelligence"
    DEBATE = "debate"
    MAPPING = "mapping"
    VALUATION = "valuation"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineState:
    """Shared state across all pipeline stages."""
    ticker: str
    chaos_level: float
    current_stage: PipelineStage = PipelineStage.WORLD_STATE
    
    # Results from each stage
    world_state: Optional[dict] = None
    financials: Optional[dict] = None
    raw_risks: list = field(default_factory=list)
    tribunal_output: Optional[dict] = None
    fracture_nodes: list = field(default_factory=list)
    supply_chain_paths: list = field(default_factory=list)
    valuation: Optional[dict] = None
    
    # Metadata
    start_time: float = 0.0
    stage_timings: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    
    def elapsed(self) -> float:
        return time.time() - self.start_time


class DoomsdayOrchestrator:
    """
    Central orchestrator that manages pipeline execution.
    Handles retries, fallbacks, and graceful degradation.
    """
    
    MAX_RETRIES = 2
    STAGE_TIMEOUT = 30  # seconds per stage
    
    def __init__(self, gemini_client, tavily_client, model: str):
        self.gemini = gemini_client
        self.tavily = tavily_client
        self.model = model
        self._progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates (e.g., Streamlit progress bar)."""
        self._progress_callback = callback
    
    async def execute_pipeline(self, ticker: str, chaos_level: float) -> PipelineState:
        """Execute the full Doomsday pipeline."""
        
        state = PipelineState(
            ticker=ticker,
            chaos_level=chaos_level,
            start_time=time.time()
        )
        
        stages = [
            (PipelineStage.WORLD_STATE, self._stage_world_state, 15),
            (PipelineStage.FINANCIALS, self._stage_financials, 20),
            (PipelineStage.INTELLIGENCE, self._stage_intelligence, 40),
            (PipelineStage.DEBATE, self._stage_debate, 60),
            (PipelineStage.MAPPING, self._stage_mapping, 80),
            (PipelineStage.VALUATION, self._stage_valuation, 95),
        ]
        
        for stage_enum, stage_fn, progress_pct in stages:
            state.current_stage = stage_enum
            self._report_progress(progress_pct, f"Running: {stage_enum.value}")
            
            stage_start = time.time()
            
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    await stage_fn(state)
                    state.stage_timings[stage_enum.value] = time.time() - stage_start
                    break
                except Exception as e:
                    if attempt == self.MAX_RETRIES:
                        state.errors.append({
                            "stage": stage_enum.value,
                            "error": str(e),
                            "fatal": stage_enum in [PipelineStage.FINANCIALS]  # Only financials is fatal
                        })
                        if stage_enum == PipelineStage.FINANCIALS:
                            state.current_stage = PipelineStage.FAILED
                            return state
                    else:
                        await asyncio.sleep(1)  # Brief pause before retry
        
        state.current_stage = PipelineStage.COMPLETE
        self._report_progress(100, "Analysis complete!")
        return state
    
    async def _stage_world_state(self, state: PipelineState):
        """Fetch world state."""
        from world_state import WorldStateEngine
        engine = WorldStateEngine(tavily_api_key=self.tavily.api_key)
        ws = engine.generate()
        state.world_state = ws.to_dict()
    
    async def _stage_financials(self, state: PipelineState):
        """Fetch company financials."""
        from vulture_dcf import VultureArchitect
        architect = VultureArchitect()
        financials = architect.fetch_financials(state.ticker)
        if not financials or financials.market_cap == 0:
            raise ValueError(f"Cannot fetch financials for {state.ticker}")
        state.financials = financials
    
    async def _stage_intelligence(self, state: PipelineState):
        """Run parallel intelligence gathering."""
        from sentinel import GlobalSentinel
        sentinel = GlobalSentinel(self.gemini, self.tavily, self.model)
        
        fin = state.financials
        context = f"Sector: {fin.sector} | MCap: ${fin.market_cap/1e9:.1f}B | Rev: ${fin.revenue_ttm/1e9:.1f}B"
        
        from world_state import WorldState
        ws_text = json.dumps(state.world_state, indent=2) if state.world_state else "World state unavailable"
        
        risks = await sentinel.gather_intelligence(state.ticker, context, ws_text)
        state.raw_risks = risks
    
    async def _stage_debate(self, state: PipelineState):
        """Run adversarial debate tribunal."""
        from debate_engine import FractureTribunal
        tribunal = FractureTribunal(client=self.gemini, model=self.model)
        
        fin = state.financials
        context = f"Sector: {fin.sector} | MCap: ${fin.market_cap/1e9:.1f}B"
        
        output = await tribunal.run_tribunal(
            ticker=state.ticker,
            company_context=context,
            raw_risks=[{
                "id": r.id, "domain": r.domain, "description": r.description,
                "evidence": r.evidence, "initial_severity": r.initial_severity,
                "geographic_hint": r.geographic_hint, "affected_revenue_pct": r.affected_revenue_pct
            } for r in state.raw_risks],
            world_state=state.world_state or {}
        )
        state.tribunal_output = output
    
    async def _stage_mapping(self, state: PipelineState):
        """Convert risks to geographic nodes."""
        from saboteur import LogisticsSaboteur
        saboteur = LogisticsSaboteur(self.gemini, self.model)
        
        validated = [{
            "risk_id": v.risk_id, "description": v.risk_description,
            "severity": v.severity_score, "probability": v.probability,
            "time_horizon": v.time_horizon
        } for v in state.tribunal_output.validated_risks]
        
        nodes, paths = await saboteur.map_risks(state.ticker, validated)
        state.fracture_nodes = nodes
        state.supply_chain_paths = paths
    
    async def _stage_valuation(self, state: PipelineState):
        """Compute distressed valuation."""
        from vulture_dcf import VultureArchitect
        architect = VultureArchitect()
        
        valuation = architect.calculate_distressed_value(
            financials=state.financials,
            chaos_level=state.chaos_level,
            validated_risks=[{
                "severity_score": v.severity_score,
                "revenue_at_risk_pct": v.probability * 20
            } for v in state.tribunal_output.validated_risks]
        )
        state.valuation = valuation
    
    def _report_progress(self, pct: int, message: str):
        if self._progress_callback:
            self._progress_callback(pct, message)
PART 4: FINAL PROJECT STRUCTURE
project-doomsday/
├── app.py                    # Streamlit main UI (render above)
├── orchestrator.py           # Pipeline management
├── world_state.py            # Global macro calibration
├── sentinel.py               # Multi-domain intelligence gathering
├── debate_engine.py          # Adversarial tribunal (llm-council inspired)
├── saboteur.py               # Geographic fracture mapping
├── vulture_dcf.py            # Deterministic distressed valuation
├── models.py                 # Shared Pydantic/dataclass schemas
├── config.py                 # Model selection, API keys, constants
├── utils/
│   ├── model_hunter.py       # Brute-force model availability scanner
│   ├── json_normalizer.py    # LLM output parsing/validation
│   └── cache.py              # Simple TTL cache for API calls
├── assets/
│   └── custom.css            # Additional styling
├── .env                      # API keys (not committed)
├── .env.example              # Template
├── requirements.txt
├── README.md
└── docs/
    ├── architecture.md       # System design doc
    └── demo_script.md        # Hackathon presentation script
requirements.txt:
streamlit>=1.35.0
plotly>=5.22.0
google-genai>=1.0.0
tavily-python>=0.5.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
pydantic>=2.0.0
