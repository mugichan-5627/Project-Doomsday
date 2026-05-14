🔥 PROJECT DOOMSDAY: COMPLETE REBUILD BLUEPRINT
For Milan AI Week Hackathon — Built to Win
PART 1: ARCHITECTURAL FIXES & UPGRADES
1.1 The Core Problem with Your Current Architecture
Your current setup is a linear pipeline pretending to be a swarm. True swarm intelligence needs:

Debate/Consensus (inspired by llm-council)
Parallel execution with convergence
Disagreement resolution that produces higher-quality output than any single agent
Here's the rebuilt architecture:

┌─────────────────────────────────────────────────────────────────────┐
│                    🧠 DOOMSDAY ORCHESTRATOR                          │
│                  (State Machine + Debate Engine)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  PHASE 1: INTELLIGENCE GATHERING (Parallel)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   SENTINEL    │  │   SENTINEL    │  │   SENTINEL    │              │
│  │  (Geopolitical)│  │  (Financial) │  │(Supply Chain)│              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│  PHASE 2: ADVERSARIAL DEBATE (llm-council style)                     │
│  ┌─────────────────────────────────────────────────────┐            │
│  │              🗣️ FRACTURE TRIBUNAL                     │            │
│  │  Bull Advocate ←→ Bear Advocate ←→ Black Swan Judge  │            │
│  │         (3 rounds of structured debate)               │            │
│  └──────────────────────┬──────────────────────────────┘            │
│                         │                                            │
│  PHASE 3: SPATIAL MAPPING                                            │
│  ┌──────────────────────▼──────────────────────────────┐            │
│  │           🌍 LOGISTICS SABOTEUR                       │            │
│  │   Consensus Risks → GPS Fracture Nodes + Severity    │            │
│  └──────────────────────┬──────────────────────────────┘            │
│                         │                                            │
│  PHASE 4: QUANTIFICATION                                             │
│  ┌──────────────────────▼──────────────────────────────┐            │
│  │           💀 VULTURE ARCHITECT                        │            │
│  │   Fracture Nodes → Distressed DCF → Fair Value       │            │
│  └──────────────────────┬──────────────────────────────┘            │
│                         │                                            │
│  PHASE 5: SYNTHESIS                                                  │
│  ┌──────────────────────▼──────────────────────────────┐            │
│  │           📋 DEAL CHAMPION                            │            │
│  │   All Data → IC Memo + Risk Score + Recommendation   │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
1.2 The Debate Engine (Inspired by llm-council)
This is what will make your project stand out at Milan. Instead of one LLM call producing risks, you have adversarial agents arguing about whether a risk is real, and the transcript of that debate becomes part of your output.

# debate_engine.py
"""
Fracture Tribunal: Adversarial Debate System
Inspired by: https://github.com/karpathy/llm-council
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import asyncio
import json
from google import genai
from google.genai import types

class DebateRole(Enum):
    BULL_ADVOCATE = "bull_advocate"
    BEAR_ADVOCATE = "bear_advocate"  
    BLACK_SWAN_JUDGE = "black_swan_judge"

@dataclass
class DebateMessage:
    role: DebateRole
    content: str
    round_number: int
    confidence: float  # 0.0 to 1.0
    evidence_cited: List[str] = field(default_factory=list)

@dataclass
class DebateVerdict:
    risk_id: str
    risk_description: str
    severity_score: float  # 1-10
    probability: float  # 0.0 to 1.0
    time_horizon: str  # "immediate", "3_months", "6_months", "12_months"
    bull_argument_summary: str
    bear_argument_summary: str
    judge_reasoning: str
    consensus_reached: bool
    debate_transcript: List[DebateMessage]

@dataclass  
class TribunalOutput:
    ticker: str
    validated_risks: List[DebateVerdict]
    dismissed_risks: List[DebateVerdict]
    overall_threat_level: str  # "LOW", "ELEVATED", "HIGH", "CRITICAL"
    debate_quality_score: float


SYSTEM_PROMPTS = {
    DebateRole.BULL_ADVOCATE: """You are the BULL ADVOCATE in a financial risk tribunal.
Your job is to DEFEND the company against alleged risks. You must:
1. Challenge the evidence quality (is it speculative? outdated? misattributed?)
2. Present mitigating factors (hedging, diversification, management action)
3. Argue that the market has already priced in the risk
4. Cite specific counterexamples or data points

You are NOT blindly optimistic. If a risk is genuinely catastrophic and well-evidenced,
you concede gracefully. Your credibility matters.

Respond in JSON:
{
    "argument": "your structured argument",
    "confidence_in_dismissal": 0.0-1.0,
    "key_counterpoints": ["point1", "point2"],
    "concessions": ["any points you concede"],
    "evidence_cited": ["source1", "source2"]
}""",

    DebateRole.BEAR_ADVOCATE: """You are the BEAR ADVOCATE in a financial risk tribunal.
Your job is to PROSECUTE the risk case. You must:
1. Present the worst-case scenario with specificity (not vague doom)
2. Identify second-order effects and contagion paths
3. Challenge the bull's mitigating factors with historical precedent
4. Quantify potential financial impact (revenue %, margin compression, etc.)

You are NOT a fear-monger. You present evidence-based bear cases.
Weak risks that lack evidence should be prosecuted weakly.

Respond in JSON:
{
    "argument": "your structured argument",
    "confidence_in_risk": 0.0-1.0,
    "severity_estimate": 1-10,
    "contagion_paths": ["path1", "path2"],
    "historical_precedent": "relevant historical analog",
    "financial_impact_estimate": "specific % or $ impact",
    "evidence_cited": ["source1", "source2"]
}""",

    DebateRole.BLACK_SWAN_JUDGE: """You are the BLACK SWAN JUDGE in a financial risk tribunal.
You have heard arguments from both the Bull Advocate and Bear Advocate.
Your job is to deliver a FINAL VERDICT on each risk. You must:

1. Evaluate evidence quality from both sides (not just who sounds more confident)
2. Identify any risks NEITHER side mentioned (tail risks, correlation risks)
3. Assign a final severity score (1-10) and probability (0.0-1.0)
4. Determine if this risk warrants inclusion in the Fracture Map

You are calibrated: a score of 8+ should be reserved for risks with clear evidence
of potential >25% valuation impact. Most risks should score 3-6.

Respond in JSON:
{
    "verdict": "VALIDATED" or "DISMISSED" or "MONITORING",
    "final_severity": 1-10,
    "final_probability": 0.0-1.0,
    "time_horizon": "immediate|3_months|6_months|12_months",
    "reasoning": "structured reasoning citing both sides",
    "overlooked_factors": ["any tail risks neither side mentioned"],
    "financial_impact_range": {"low": "-X%", "high": "-Y%"},
    "geographic_nexus": "primary geographic location of this risk"
}"""
}


class FractureTribunal:
    """
    Runs adversarial debates between AI agents to validate/dismiss risks.
    Produces higher-quality risk assessments than single-shot prompting.
    """
    
    def __init__(self, client: genai.Client, model: str = "gemini-2.5-flash"):
        self.client = client
        self.model = model
        self.debate_rounds = 3
        
    async def run_tribunal(
        self, 
        ticker: str,
        company_context: str,
        raw_risks: List[Dict],
        world_state: Dict
    ) -> TribunalOutput:
        """Run full tribunal on all identified risks."""
        
        validated = []
        dismissed = []
        
        for risk in raw_risks:
            verdict = await self._debate_single_risk(
                ticker=ticker,
                company_context=company_context,
                risk=risk,
                world_state=world_state
            )
            
            if verdict.severity_score >= 4.0 and verdict.probability >= 0.3:
                validated.append(verdict)
            else:
                dismissed.append(verdict)
        
        # Determine overall threat level
        if not validated:
            threat_level = "LOW"
        else:
            max_severity = max(v.severity_score for v in validated)
            avg_severity = sum(v.severity_score for v in validated) / len(validated)
            
            if max_severity >= 9 or avg_severity >= 7:
                threat_level = "CRITICAL"
            elif max_severity >= 7 or avg_severity >= 5:
                threat_level = "HIGH"
            elif max_severity >= 5:
                threat_level = "ELEVATED"
            else:
                threat_level = "LOW"
        
        return TribunalOutput(
            ticker=ticker,
            validated_risks=validated,
            dismissed_risks=dismissed,
            overall_threat_level=threat_level,
            debate_quality_score=self._calculate_debate_quality(validated + dismissed)
        )
    
    async def _debate_single_risk(
        self,
        ticker: str,
        company_context: str,
        risk: Dict,
        world_state: Dict
    ) -> DebateVerdict:
        """Run a 3-round debate on a single risk."""
        
        transcript: List[DebateMessage] = []
        
        # Context shared with all debaters
        shared_context = f"""
COMPANY: {ticker}
COMPANY CONTEXT: {company_context}
WORLD STATE: {json.dumps(world_state, indent=2)}
RISK UNDER EXAMINATION: {json.dumps(risk, indent=2)}
"""
        
        # Round 1: Bear presents the case
        bear_r1 = await self._agent_speak(
            role=DebateRole.BEAR_ADVOCATE,
            context=shared_context,
            history=[],
            instruction="Present your initial prosecution of this risk. Be specific and evidence-based."
        )
        transcript.append(bear_r1)
        
        # Round 1: Bull responds
        bull_r1 = await self._agent_speak(
            role=DebateRole.BULL_ADVOCATE,
            context=shared_context,
            history=transcript,
            instruction="Respond to the Bear's initial case. Challenge their evidence and present mitigating factors."
        )
        transcript.append(bull_r1)
        
        # Round 2: Bear rebuts
        bear_r2 = await self._agent_speak(
            role=DebateRole.BEAR_ADVOCATE,
            context=shared_context,
            history=transcript,
            instruction="Rebut the Bull's counterarguments. Introduce second-order effects or new evidence."
        )
        transcript.append(bear_r2)
        
        # Round 2: Bull final defense
        bull_r2 = await self._agent_speak(
            role=DebateRole.BULL_ADVOCATE,
            context=shared_context,
            history=transcript,
            instruction="Final defense. Concede any points that are genuinely strong, but defend your core thesis."
        )
        transcript.append(bull_r2)
        
        # Round 3: Judge delivers verdict
        judge_verdict = await self._judge_deliberate(
            context=shared_context,
            transcript=transcript
        )
        
        return DebateVerdict(
            risk_id=risk.get("id", "unknown"),
            risk_description=risk.get("description", ""),
            severity_score=judge_verdict.get("final_severity", 5.0),
            probability=judge_verdict.get("final_probability", 0.5),
            time_horizon=judge_verdict.get("time_horizon", "6_months"),
            bull_argument_summary=self._summarize_side(transcript, DebateRole.BULL_ADVOCATE),
            bear_argument_summary=self._summarize_side(transcript, DebateRole.BEAR_ADVOCATE),
            judge_reasoning=judge_verdict.get("reasoning", ""),
            consensus_reached=judge_verdict.get("verdict") != "MONITORING",
            debate_transcript=transcript
        )
    
    async def _agent_speak(
        self,
        role: DebateRole,
        context: str,
        history: List[DebateMessage],
        instruction: str
    ) -> DebateMessage:
        """Single agent turn in the debate."""
        
        history_text = "\n\n".join([
            f"[{msg.role.value.upper()} - Round {msg.round_number}]: {msg.content}"
            for msg in history
        ])
        
        prompt = f"""{context}

DEBATE HISTORY SO FAR:
{history_text if history else "No prior debate. You are opening."}

YOUR INSTRUCTION: {instruction}
"""
        
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPTS[role],
                temperature=0.7,  # Some creativity in argumentation
                response_mime_type="application/json"
            )
        )
        
        try:
            parsed = json.loads(response.text)
            confidence = parsed.get("confidence_in_risk", parsed.get("confidence_in_dismissal", 0.5))
        except:
            parsed = {"argument": response.text}
            confidence = 0.5
        
        return DebateMessage(
            role=role,
            content=json.dumps(parsed),
            round_number=len([m for m in history if m.role == role]) + 1,
            confidence=confidence,
            evidence_cited=parsed.get("evidence_cited", [])
        )
    
    async def _judge_deliberate(
        self, 
        context: str, 
        transcript: List[DebateMessage]
    ) -> Dict:
        """Judge reviews full debate and delivers verdict."""
        
        history_text = "\n\n".join([
            f"[{msg.role.value.upper()} - Round {msg.round_number}]: {msg.content}"
            for msg in transcript
        ])
        
        prompt = f"""{context}

FULL DEBATE TRANSCRIPT:
{history_text}

Deliver your final verdict on this risk.
"""
        
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPTS[DebateRole.BLACK_SWAN_JUDGE],
                temperature=0.3,  # More deterministic for judgment
                response_mime_type="application/json"
            )
        )
        
        try:
            return json.loads(response.text)
        except:
            return {
                "verdict": "MONITORING",
                "final_severity": 5.0,
                "final_probability": 0.5,
                "time_horizon": "6_months",
                "reasoning": response.text
            }
    
    def _summarize_side(self, transcript: List[DebateMessage], role: DebateRole) -> str:
        messages = [m for m in transcript if m.role == role]
        return " | ".join([m.content[:200] for m in messages])
    
    def _calculate_debate_quality(self, verdicts: List[DebateVerdict]) -> float:
        """Heuristic: good debates have evidence citations and varied confidence levels."""
        if not verdicts:
            return 0.0
        scores = []
        for v in verdicts:
            cited = sum(len(m.evidence_cited) for m in v.debate_transcript)
            variance = abs(v.severity_score - 5.0) / 5.0  # Polarized = more decisive
            scores.append(min(1.0, (cited * 0.1 + variance * 0.5)))
        return sum(scores) / len(scores)