"""
PROJECT DOOMSDAY - REST API SERVER (Forecasting Track Endpoint)
Version: 1.0 (Stabilized - OpenAI-Compatible)
Exposes `/v1/chat/completions` for programmatic Swarm Intelligence stress forecasting.
"""

import os
import re
import json
import time
import sys
from typing import List, Dict, Any, Optional

# Force import resolution from Project_Doomsday workspace root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import core analytical modules and dataclasses from app.py
from app import (
    DoomsdayAI,
    fetch_company_data,
    fetch_world_state_data,
    run_intelligence_scan,
    run_debate,
    generate_contagion_chains,
    compute_valuation,
    get_tavily,
    CompanyData,
    WorldState,
    RiskVerdict,
    SimpleValuation
)

# Initialize FastAPI App
app = FastAPI(
    title="Project Doomsday - Financial Forecasting API",
    description="OpenAI-compatible endpoints for multi-agent black swan and stress valuation models.",
    version="1.0"
)

# Enable CORS for maximum client compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================================
# PYDANTIC SCHEMAS (Standard OpenAI Spec)
# ===============================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message author (system, user, assistant).")
    content: str = Field(..., description="Content of the message.")

class ChatCompletionRequest(BaseModel):
    model: str = Field("doomsday-swarm", description="Target model name.")
    messages: List[ChatMessage] = Field(..., description="Conversational history.")
    temperature: float = Field(0.5, description="Sampling temperature.")
    max_tokens: int = Field(4000, description="Max response tokens.")
    stream: bool = Field(False, description="Whether to stream responses.")

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

# ===============================================================
# EXTRACTION UTILITIES (LLM + Regex Parser)
# ===============================================================

def extract_target_params(ai: DoomsdayAI, user_prompt: str) -> tuple[str, float]:
    """
    Extract target stock ticker and stress level (0.0 to 1.0) from the user's prompt.
    Uses AI extraction with a robust regex fallback.
    """
    ticker = "NVDA"
    chaos = 0.5
    
    # Define fallback regex matching patterns first
    ticker_match = re.search(r'\b([A-Z]{1,5}(\.[A-Z]{2})?)\b', user_prompt)
    if ticker_match:
        ticker = ticker_match.group(1).upper()
    
    # Simple semantic keyword matching for stress level fallback
    lower_prompt = user_prompt.lower()
    if any(k in lower_prompt for k in ["extreme", "worst-case", "maximum", "total chaos", "critical"]):
        chaos = 0.9
    elif any(k in lower_prompt for k in ["severe", "high", "deep"]):
        chaos = 0.75
    elif any(k in lower_prompt for k in ["moderate", "medium", "stable"]):
        chaos = 0.5
    elif any(k in lower_prompt for k in ["low", "mild", "soft"]):
        chaos = 0.25
        
    # Check for direct number references (e.g. "0.8 stress" or "80% chaos")
    stress_num_match = re.search(r'\b(0\.\d+|1\.0)\b', user_prompt)
    pct_match = re.search(r'\b(\d{1,2})%\s*(stress|chaos|risk|level)\b', lower_prompt)
    if stress_num_match:
        chaos = float(stress_num_match.group(1))
    elif pct_match:
        chaos = float(pct_match.group(1)) / 100.0
        
    # Attempt high-fidelity LLM parsing if AI is initialized
    if ai and ai.provider:
        prompt = f"""
        Extract the target stock ticker and stress level from this prompt:
        "{user_prompt}"
        
        Respond ONLY with a raw JSON object matching this schema:
        {{
          "ticker": "SYMBOL",
          "chaos": 0.5
        }}
        
        Rules:
        - Ticker symbol: Must be capital letters (e.g., "AAPL", "MSFT", "RELIANCE"). If the user names a company but no ticker, resolve it (e.g., "Apple" -> "AAPL", "Nvidia" -> "NVDA").
        - Chaos level: A float from 0.0 to 1.0 representing stress/chaos level. If not explicitly specified, default to 0.5. Scale up to 0.9 for words like "extreme" or "worst-case", down to 0.2 for "mild".
        - Do not output markdown code blocks (e.g. no ```json). Only output raw string JSON.
        """
        try:
            res = ai.generate(prompt, temperature=0.0, max_tokens=150, json_mode=True)
            if res:
                # Strip code fence indicators if present
                clean_res = res.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_res)
                if "ticker" in parsed and parsed["ticker"]:
                    ticker = parsed["ticker"].strip().upper()
                if "chaos" in parsed:
                    chaos = min(max(float(parsed["chaos"]), 0.0), 1.0)
        except Exception:
            pass # Keep regex parsed parameters
            
    return ticker, chaos

# ===============================================================
# REPORT COMPILER
# ===============================================================

def compile_forecast_report(
    company: CompanyData,
    world_state: WorldState,
    verdicts: List[RiskVerdict],
    chains: List[Dict],
    val: SimpleValuation,
    chaos: float
) -> str:
    """Compile calculations, tribunal logs, and cascade paths into a gorgeous executive report."""
    
    # Format global metrics
    downside_color = "red" if val.downside_pct <= -25 else "orange" if val.downside_pct <= -15 else "yellow"
    threat_level = "CRITICAL" if chaos >= 0.8 else "HIGH" if chaos >= 0.6 else "ELEVATED" if chaos >= 0.3 else "LOW"
    
    report = f"""# PROJECT DOOMSDAY -- SWARM FORECASTING ANALYSIS REPORT
**Asset Target**: {company.name} ({company.ticker})  
**Sector/Industry**: {company.sector} / {company.industry}  
**Timestamp**: {world_state.timestamp}  
**Chaos Regime**: `{chaos:.0%}` ({threat_level} Stress Level)

---

## 📊 EXECUTIVE VALUATION METRICS

| Stress Metric | Value | Breakdown / Notes |
| :--- | :--- | :--- |
| **Current Market Price** | **${val.current_price:.2f}** | Real-time market rate (USD adjusted) |
| **Base Fair Value** | **${val.base_fair_value:.2f}** | Standard forward-looking intrinsic value |
| **Distressed Value** | **${val.distressed_value:.2f}** | Intrinsic value under `{chaos:.0%}` systemic crisis |
| **Implied Downside Risk** | <span style="color:{downside_color}">**{val.downside_pct:.1f}%**</span> | Total capital loss exposure |
| **Valuation Engine Routing** | **{val.valuation_method}** | Automatically matched company archetype |

### 🛠️ Stress Methodology Summary
- **Base WACC**: `{val.base_wacc:.1f}%` $\rightarrow$ **Stressed WACC**: `{val.stressed_wacc:.1f}%` (Implied Premium Adjustment: `+{val.stressed_wacc - val.base_wacc:.1f}%`)
- **Revenue Stress Haircut**: `{val.revenue_haircut:.1f}%`
- **Margin Compression Applied**: `{val.margin_compression_bps:.0f} bps`

---

## 🌐 GLOBAL SYSTEMIC RISK NEXUS (WORLD STATE)
- **VIX (Volatility Index)**: `{world_state.vix}`
- **Global Fear Level Designation**: `{world_state.fear_level}`
- **US 10-Year Bond Yield**: `{world_state.us_10y_yield}%`
- **Commodity Benchmarks**: Brent Oil: `${world_state.oil_brent}/bbl` | Gold: `${world_state.gold}/oz`

---

## ⚡ VALIDATED BLACK SWAN THREAT FEED ({len(verdicts)} Risks Confirmed)

| ID | Domain | Threat / Catalyst | Severity | Prob | Geographic Nexus | Timeframe |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    
    for v in verdicts:
        report += f"| `{v.risk_id}` | {v.domain.upper()} | {v.risk_description[:70]}... | **{v.severity_score:.1f}/10** | `{v.probability*100:.0f}%` | {v.geographic_nexus} | `{v.time_horizon}` |\n"
        
    report += "\n---\n\n## ⚔️ FRACTURE TRIBUNAL -- ADVERSARIAL DEBATES\n"
    
    for idx, v in enumerate(verdicts[:2]):
        report += f"### Risk Analysis: {v.risk_description[:80]}... (`{v.risk_id}`)\n"
        report += f"- **Bear Advocate (Risk Case)**: *\"{v.bear_summary}\"*\n"
        report += f"- **Bull Advocate (Mitigation Case)**: *\"{v.bull_summary}\"*\n"
        report += f"- **Tribunal Judge Verdict (Calibrated Rationale)**: *\"{v.judge_reasoning}\"*\n\n"
        
    report += "\n---\n\n## 🔗 SYSTEMIC CONTAGION CASCADE (PROPAGATION CHAINS)\n"
    
    if not chains:
        report += "*No active contagion paths identified for this asset regime.*\n"
    else:
        for idx, chain in enumerate(chains[:2]):
            report += f"### Contagion Pathway {idx+1}: {chain.get('primary_risk', 'Trigger Event')}\n"
            report += f"**Trigger Severity**: `{chain.get('primary_severity', 6.0)}/10`\n"
            
            for step in chain.get("cascade", []):
                arrow = "$\rightarrow$" if step.get("order", 2) == 2 else "  $\rightarrow$"
                report += f"- **[{step.get('order')}nd-Order Effect]** {arrow} *{step.get('effect')}*  \n"
                report += f"  - Impacted Metric: `{step.get('metric_impacted')}` ({step.get('magnitude')})  \n"
                report += f"  - Time Delay: `{step.get('time_delay')}` | Cumulative Loss: **-{step.get('cumulative_value_destruction_pct')}%**  \n"
            report += "\n"
            
    # Compound contagion assessment formulas
    avg_dest = sum([c.get('cascade', [{}])[-1].get('cumulative_value_destruction_pct', 0) for c in chains if c.get('cascade')]) / max(len(chains), 1)
    compound_factor = 1 + (chaos * 0.3 * (len(chains) - 1))
    compound_dest = min(avg_dest * compound_factor, 65)
    rho = min(0.4 + chaos * 0.5, 0.95)
    
    report += f"""
### 🧮 Crisis Correlation Assessment
- **Asset Convergence Coefficient ($\\rho$)**: `{rho:.2f}` (In systemic crises, all asset correlations converge toward 1.0, rendering conventional portfolio diversification useless)
- **Net Compound Value Destruction**: **-{compound_dest:.1f}%**

---

## 🏛️ INVESTMENT COMMITTEE SUMMARY & HEDGING MANDATE
1. **Capital Allocation Recommendation**: Under a `{chaos:.0%}` chaos scenario, **{company.name}** fair valuation shifts from **${val.base_fair_value:.2f}** to **${val.distressed_value:.2f}**. 
2. **Immediate Directive**: Hold protective put options or direct short hedges proportional to the **{val.downside_pct:.1f}% downside risk** to insulate credit lines from regional cascades in `{verdicts[0].geographic_nexus if verdicts else 'global nexuses'}`.
"""
    return report

# ===============================================================
# ENDPOINTS
# ===============================================================

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible Chat Completions endpoint.
    Runs Project Doomsday's complete multi-agent forecasting swarm.
    """
    # 1. Initialize AI Swarm Provider
    ai = DoomsdayAI()
    try:
        ai.initialize()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No AI provider (Gemini, NVIDIA, Fireworks) initialized. Details: {e}"
        )
        
    # 2. Extract Last User Prompt
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message list cannot be empty."
        )
    
    user_prompt = request.messages[-1].content
    
    # 3. Parse Ticker and Stress Parameters
    ticker, chaos = extract_target_params(ai, user_prompt)
    
    # 4. Fetch Global Macro Indicators
    world_state = fetch_world_state_data()
    
    # 5. Fetch target financial data
    company = fetch_company_data(ticker)
    if not company:
        # Graceful fallback: return a structured completion informing the user
        content = f"### ⚠️ Forecast Interrupted\nFailed to fetch or resolve financial data for target stock ticker: **'{ticker}'**.\n\nPlease check that the ticker is a valid symbol on yfinance (e.g. `NVDA`, `AAPL`, `TSM`, `RELIANCE.NS`)."
        return ChatCompletionResponse(
            id=f"chatcmpl-doomsday-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=content),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(prompt_tokens=10, completion_tokens=50, total_tokens=60)
        )
        
    # 6. Execute Multi-Domain Intelligence scan
    tavily = get_tavily()
    risks = run_intelligence_scan(ai, tavily, ticker, company, world_state)
    
    # 7. Run Adversarial Debates for Risk Validation
    verdicts = []
    for risk in risks:
        verdict = run_debate(ai, ticker, risk, world_state)
        if verdict:
            verdicts.append(verdict)
            
    # 8. Model Propagation cascades
    raw_verdicts = [v.__dict__ if hasattr(v, '__dict__') else v for v in verdicts]
    chains = generate_contagion_chains(ai, company, raw_verdicts, chaos)
    
    # 9. Compute Stressed Valuation
    avg_sev = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
    valuation = compute_valuation(company, chaos, avg_sev)
    
    # 10. Compile Premium Markdown Report
    markdown_report = compile_forecast_report(company, world_state, verdicts, chains, valuation, chaos)
    
    # 11. Format & Return standard response
    return ChatCompletionResponse(
        id=f"chatcmpl-doomsday-{int(time.time())}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=markdown_report),
                finish_reason="stop"
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=len(user_prompt) // 4,
            completion_tokens=len(markdown_report) // 4,
            total_tokens=(len(user_prompt) + len(markdown_report)) // 4
        )
    )

@app.get("/health")
async def health_check():
    """Simple status check for local verification."""
    return {"status": "operational", "project": "doomsday-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
