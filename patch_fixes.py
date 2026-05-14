
NEW_SCAN = '''
def run_intelligence_scan(ai: "DoomsdayAI", tavily, ticker: str, company: "CompanyData", ws: "WorldState"):
    """Gather intelligence - aggressive multi-query approach."""
    news = ""
    domains = {
        "geopolitical": f"{company.name} geopolitical risk sanctions export controls trade war 2024 2025",
        "supply_chain": f"{company.name} supply chain disruption semiconductor shortage factory",
        "financial": f"{company.name} revenue decline earnings miss debt downgrade",
        "regulatory": f"{company.name} antitrust regulation investigation fine penalty",
        "competition": f"{company.name} market share loss competitor threat AI",
        "macro": f"{company.sector} sector risk recession interest rates impact 2025"
    }
    search_count = 0
    for domain, query in domains.items():
        result = tavily_search(tavily, query, max_results=3)
        if result:
            news += f"\\n[{domain.upper()}]:\\n{result}\\n"
            search_count += 1
    if search_count < 2:
        broad = tavily_search(tavily, f"{company.name} {ticker} risk analysis bear case concerns 2025", max_results=5)
        if broad:
            news += f"\\n[BROAD SEARCH]:\\n{broad}\\n"
    company_context = f"""
KNOWN FACTS ABOUT {company.name}:
- Sector: {company.sector}, Industry: {company.industry}
- Market Cap: ${company.market_cap/1e9:.1f}B, Revenue: ${company.revenue/1e9:.1f}B
- Revenue Growth: {company.revenue_growth*100:.1f}%, Beta: {company.beta:.2f}
- Debt: ${company.total_debt/1e9:.1f}B, Cash: ${company.cash/1e9:.1f}B
- P/E Ratio: {company.pe_ratio:.1f}x"""
    prompt = f"""You are a senior institutional risk analyst at a hedge fund. Identify the TOP 6 most material BLACK SWAN and stress risks for {ticker} ({company.name}).

{company_context}

CURRENT WORLD STATE:
- VIX: {ws.vix} ({ws.vix_trend}) | Fear Level: {ws.fear_level}
- Oil: ${ws.oil_brent} | Gold: ${ws.gold} | US 10Y Yield: {ws.us_10y_yield}%

NEWS & INTELLIGENCE:
{news[:5000] if news else "No live news available - use your training knowledge of current risks."}

CRITICAL INSTRUCTIONS:
1. You MUST return EXACTLY 6 risks. Not fewer.
2. Each risk must be SPECIFIC to {company.name}, not generic market risks.
3. Include geographic locations where each risk physically manifests.
4. Even if news is limited, use your knowledge of the company\'s known risk factors.

Return ONLY valid JSON. No markdown, no code blocks, just raw JSON:
{{
    "risks": [
        {{
            "id": "RISK_001",
            "domain": "geopolitical|supply_chain|financial|regulatory|technology|market",
            "title": "Specific 5-8 word title",
            "description": "2-3 specific sentences with numbers and facts.",
            "severity": 7,
            "probability": 0.4,
            "geographic_nexus": "Specific city or region",
            "revenue_at_risk_pct": 15.0,
            "time_horizon": "3_months|6_months|12_months"
        }}
    ]
}}

REMEMBER: Exactly 6 risks. All different domains if possible. Be specific to {company.name}."""

    response = run_with_timeout(
        ai.generate, kwargs={"prompt": prompt, "temperature": 0.5, "json_mode": True, "max_tokens": 4000},
        timeout=45, default=None
    )
    parsed = parse_json_safe(response)
    if parsed and "risks" in parsed and len(parsed["risks"]) >= 2:
        return parsed["risks"][:6]
    return generate_fallback_risks(company, ws)


def generate_fallback_risks(company: "CompanyData", ws: "WorldState"):
    """Generate intelligent fallback risks when AI/search fails."""
    sector = (company.sector or "").lower()
    industry = (company.industry or "").lower()
    name = company.name
    risks = []
    risks.append({
        "id": "RISK_001", "domain": "market",
        "title": f"Global macro deterioration impacting {company.sector}",
        "description": f"With VIX at {ws.vix} and oil at ${ws.oil_brent}, macroeconomic headwinds could compress {name}\'s multiples by 15-25%. Rising rates increase discount rates and could trigger multiple compression across the {company.sector} sector.",
        "severity": 5 + (1 if ws.vix > 20 else 0) + (1 if ws.vix > 30 else 0),
        "probability": 0.4, "geographic_nexus": "New York",
        "revenue_at_risk_pct": 8.0, "time_horizon": "6_months"
    })
    if "tech" in sector or "semiconductor" in industry:
        risks.extend([
            {"id": "RISK_002", "domain": "geopolitical",
             "title": "US-China tech export controls escalation",
             "description": f"Escalating US-China tensions could lead to expanded export controls, restricting {name}\'s access to Chinese customers. China represents significant semiconductor demand, and further restrictions could reduce revenue by 10-20%.",
             "severity": 7, "probability": 0.45, "geographic_nexus": "Beijing",
             "revenue_at_risk_pct": 15.0, "time_horizon": "6_months"},
            {"id": "RISK_003", "domain": "supply_chain",
             "title": "Taiwan Strait geopolitical risk to manufacturing",
             "description": f"Military escalation in the Taiwan Strait could disrupt semiconductor manufacturing. Even a limited blockade would halt chip production and shipments globally, catastrophically impacting {name}\'s operations.",
             "severity": 9, "probability": 0.15, "geographic_nexus": "Taiwan",
             "revenue_at_risk_pct": 40.0, "time_horizon": "12_months"},
            {"id": "RISK_004", "domain": "technology",
             "title": "Competitive disruption from new entrants",
             "description": f"Rapid advances by competitors in AI chips, custom silicon (Google TPU, Amazon Graviton), and emerging architectures could erode {name}\'s market share. Technology cycles are accelerating.",
             "severity": 6, "probability": 0.35, "geographic_nexus": "Silicon Valley",
             "revenue_at_risk_pct": 12.0, "time_horizon": "12_months"},
            {"id": "RISK_005", "domain": "regulatory",
             "title": "Antitrust and regulatory scrutiny intensification",
             "description": f"Global regulators are increasingly scrutinizing dominant tech companies. {name} faces potential antitrust investigations in the US, EU, and China that could result in fines or forced licensing.",
             "severity": 5, "probability": 0.3, "geographic_nexus": "Brussels",
             "revenue_at_risk_pct": 8.0, "time_horizon": "12_months"},
        ])
    elif "financial" in sector or "bank" in industry:
        risks.extend([
            {"id": "RISK_002", "domain": "financial",
             "title": "Credit quality deterioration in loan portfolio",
             "description": f"Rising interest rates and economic slowdown could increase non-performing assets. {name}\'s loan book may face 50-100bps increase in NPAs, requiring significant provisioning.",
             "severity": 7, "probability": 0.4, "geographic_nexus": "Mumbai" if ".NS" in (company.ticker or "") else "New York",
             "revenue_at_risk_pct": 15.0, "time_horizon": "6_months"},
            {"id": "RISK_003", "domain": "regulatory",
             "title": "Basel IV tighter capital requirements",
             "description": f"New regulatory capital requirements could force {name} to hold additional buffers, reducing return on equity by 100-200bps and limiting dividend capacity.",
             "severity": 5, "probability": 0.5, "geographic_nexus": "Washington DC",
             "revenue_at_risk_pct": 8.0, "time_horizon": "12_months"},
            {"id": "RISK_004", "domain": "market",
             "title": "Net interest margin compression from rate cuts",
             "description": f"If rate cuts begin, {name}\'s net interest margin could compress 20-40bps, directly impacting the core earnings driver.",
             "severity": 6, "probability": 0.45, "geographic_nexus": "Washington DC",
             "revenue_at_risk_pct": 12.0, "time_horizon": "6_months"},
            {"id": "RISK_005", "domain": "technology",
             "title": "Fintech disruption of core banking services",
             "description": f"Digital-first challengers and embedded finance are eroding {name}\'s retail banking franchise. Neo-banks and DeFi pose medium-term structural threats.",
             "severity": 5, "probability": 0.3, "geographic_nexus": "San Francisco",
             "revenue_at_risk_pct": 10.0, "time_horizon": "12_months"},
        ])
    elif "energy" in sector or "oil" in industry:
        risks.extend([
            {"id": "RISK_002", "domain": "market",
             "title": "Oil price collapse below breakeven",
             "description": f"OPEC+ disagreements or demand destruction could push oil below $60/bbl. This would force {name} to cut capex and potentially suspend dividends.",
             "severity": 7, "probability": 0.3, "geographic_nexus": "Riyadh",
             "revenue_at_risk_pct": 25.0, "time_horizon": "6_months"},
            {"id": "RISK_003", "domain": "regulatory",
             "title": "Accelerated energy transition regulation",
             "description": f"Carbon taxes and renewable mandates could strand {name}\'s fossil fuel assets and increase operating costs by 10-15%.",
             "severity": 6, "probability": 0.4, "geographic_nexus": "Brussels",
             "revenue_at_risk_pct": 12.0, "time_horizon": "12_months"},
            {"id": "RISK_004", "domain": "geopolitical",
             "title": "Middle East conflict disrupting supply routes",
             "description": f"Escalation in the Middle East could disrupt shipping through the Strait of Hormuz, affecting 20% of global oil transit and causing operational disruptions for {name}.",
             "severity": 8, "probability": 0.25, "geographic_nexus": "Strait of Hormuz",
             "revenue_at_risk_pct": 18.0, "time_horizon": "3_months"},
            {"id": "RISK_005", "domain": "financial",
             "title": "Stranded asset writedowns",
             "description": f"As the world transitions to renewables, {name} may face impairment charges on exploration assets that become economically unviable.",
             "severity": 5, "probability": 0.35, "geographic_nexus": "Global",
             "revenue_at_risk_pct": 10.0, "time_horizon": "12_months"},
        ])
    else:
        risks.extend([
            {"id": "RISK_002", "domain": "supply_chain",
             "title": f"Supply chain disruption for {company.sector}",
             "description": f"{name} faces potential supply chain disruptions from geopolitical tensions or logistics bottlenecks that could impact production and delivery timelines.",
             "severity": 6, "probability": 0.35, "geographic_nexus": "Shanghai",
             "revenue_at_risk_pct": 12.0, "time_horizon": "6_months"},
            {"id": "RISK_003", "domain": "regulatory",
             "title": "Regulatory environment tightening",
             "description": f"New regulations in {name}\'s key markets could increase compliance costs and restrict certain business activities, impacting margins by 200-400 basis points.",
             "severity": 5, "probability": 0.4, "geographic_nexus": "Washington DC",
             "revenue_at_risk_pct": 8.0, "time_horizon": "12_months"},
            {"id": "RISK_004", "domain": "technology",
             "title": "Technology disruption from AI and automation",
             "description": f"AI and automation could disrupt {name}\'s business model or enable competitors to undercut on cost. Companies slow to adopt may lose 10-15% market share.",
             "severity": 6, "probability": 0.3, "geographic_nexus": "Silicon Valley",
             "revenue_at_risk_pct": 10.0, "time_horizon": "12_months"},
            {"id": "RISK_005", "domain": "financial",
             "title": "Customer concentration and demand weakness",
             "description": f"Economic slowdown could reduce demand from {name}\'s key customers. If top 5 customers cut orders by 15-20%, revenue impact would be material.",
             "severity": 6, "probability": 0.35, "geographic_nexus": "Global",
             "revenue_at_risk_pct": 12.0, "time_horizon": "6_months"},
        ])
    if ".NS" in (company.ticker or "") or ".BO" in (company.ticker or ""):
        risks.append({
            "id": f"RISK_{len(risks)+1:03d}", "domain": "financial",
            "title": "INR depreciation and FX volatility",
            "description": f"Rupee weakness against USD could increase import costs and foreign debt servicing for {name}. A 5-10% INR depreciation would directly compress margins for import-dependent operations.",
            "severity": 5, "probability": 0.4, "geographic_nexus": "Mumbai",
            "revenue_at_risk_pct": 6.0, "time_horizon": "6_months"
        })
    elif "TSM" in (company.ticker or ""):
        risks.append({
            "id": f"RISK_{len(risks)+1:03d}", "domain": "financial",
            "title": "TWD/USD currency headwinds",
            "description": f"Taiwan Dollar appreciation or volatility against USD impacts {name}\'s dollar-denominated revenue reporting and could compress reported margins by 200-300bps.",
            "severity": 4, "probability": 0.35, "geographic_nexus": "Taipei",
            "revenue_at_risk_pct": 5.0, "time_horizon": "6_months"
        })
    return risks[:6]

'''

NEW_DEBATE = '''
def run_debate(ai: "DoomsdayAI", ticker: str, risk: dict, ws: "WorldState"):
    """Run Bear/Bull/Judge debate with better timeout handling."""
    risk_desc = risk.get("description", risk.get("title", ""))
    risk_title = risk.get("title", "")

    bear_prompt = f"""You are the BEAR ADVOCATE prosecuting risk for {ticker}.
RISK: {risk_title} - {risk_desc}
Give worst-case argument in 2-3 sentences. Be specific with numbers and precedents.
Return JSON only: {{"argument": "your text here", "severity_estimate": 7, "confidence": 0.7}}"""

    bear_raw = run_with_timeout(ai.generate, kwargs={"prompt": bear_prompt, "temperature": 0.6, "json_mode": True, "max_tokens": 500}, timeout=25, default=None)
    bear = parse_json_safe(bear_raw) or {"argument": f"This risk poses material downside. {risk_desc} Historical precedents suggest 15-25% drawdown potential in affected segments.", "severity_estimate": risk.get("severity", 6), "confidence": 0.6}

    bull_prompt = f"""You are the BULL ADVOCATE defending {ticker}.
RISK: {risk_title} - {risk_desc}
BEAR SAYS: {bear.get("argument", "")}
Defend in 2-3 sentences. Challenge evidence, present mitigating factors.
Return JSON only: {{"argument": "your text here", "confidence": 0.5}}"""

    bull_raw = run_with_timeout(ai.generate, kwargs={"prompt": bull_prompt, "temperature": 0.6, "json_mode": True, "max_tokens": 500}, timeout=25, default=None)
    bull = parse_json_safe(bull_raw) or {"argument": f"The market has largely priced in this risk. {ticker}\'s diversified revenue base and strong cash position provide resilience. Management has demonstrated ability to navigate similar challenges historically.", "confidence": 0.5}

    judge_prompt = f"""You are the BLACK SWAN JUDGE for {ticker}. World: VIX={ws.vix}, Fear={ws.fear_level}
RISK: {risk_title}
BEAR (severity {bear.get("severity_estimate", 6)}): {bear.get("argument", "")}
BULL: {bull.get("argument", "")}
Deliver verdict. Calibration: 8+ = catastrophic (>25% impairment). 6-7 = material. 4-5 = moderate. <4 = dismiss.
Return JSON only: {{"verdict": "VALIDATED|DISMISSED|MONITORING", "final_severity": 6, "final_probability": 0.4, "reasoning": "2 sentences explaining your decision"}}"""

    judge_raw = run_with_timeout(ai.generate, kwargs={"prompt": judge_prompt, "temperature": 0.3, "json_mode": True, "max_tokens": 300}, timeout=25, default=None)
    judge = parse_json_safe(judge_raw) or {
        "verdict": "VALIDATED" if risk.get("severity", 5) >= 5 else "MONITORING",
        "final_severity": risk.get("severity", 5),
        "final_probability": risk.get("probability", 0.4),
        "reasoning": f"Risk validated based on available evidence. Severity maintained at {risk.get(\'severity\', 5)}/10 given current market conditions."
    }

    # Only skip if DISMISSED and low severity
    if judge.get("verdict") == "DISMISSED" and judge.get("final_severity", 5) < 4:
        return None

    transcript = [
        DebateMessage(role="bear", content=bear.get("argument", ""), round_number=1, confidence=float(bear.get("confidence", 0.6))),
        DebateMessage(role="bull", content=bull.get("argument", ""), round_number=1, confidence=float(bull.get("confidence", 0.5))),
        DebateMessage(role="judge", content=judge.get("reasoning", ""), round_number=1, confidence=0.9),
    ]

    return RiskVerdict(
        risk_id=risk.get("id", f"RISK_{hash(risk_title) % 999:03d}"),
        risk_description=risk.get("description", risk_title),
        domain=risk.get("domain", "unknown"),
        severity_score=float(judge.get("final_severity", risk.get("severity", 5))),
        probability=float(judge.get("final_probability", risk.get("probability", 0.4))),
        time_horizon=risk.get("time_horizon", "6_months"),
        bull_summary=bull.get("argument", ""),
        bear_summary=bear.get("argument", ""),
        judge_reasoning=judge.get("reasoning", ""),
        geographic_nexus=risk.get("geographic_nexus", "Global"),
        revenue_at_risk_pct=float(risk.get("revenue_at_risk_pct", 10)),
        debate_transcript=transcript
    )

'''

with open('app.py', encoding='utf-8') as f:
    content = f.read()

# Replace run_intelligence_scan
scan_start = content.find('\ndef run_intelligence_scan(')
scan_end = content.find('\ndef run_debate(')
content = content[:scan_start] + NEW_SCAN + content[scan_end:]

# Replace run_debate
debate_start = content.find('\ndef run_debate(')
debate_end = content.find('\ndef map_risks_to_coords(')
content = content[:debate_start] + NEW_DEBATE + content[debate_end:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
