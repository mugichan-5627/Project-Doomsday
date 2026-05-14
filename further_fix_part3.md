PART 3: UPDATED app.py — Integration Points
Here are the specific changes to integrate the filing engine and proper valuation into your existing app.py:

# Add these imports at the top of app.py
from filing_intelligence import UnifiedFilingEngine, SECEdgarEngine, SEBIFilingEngine
from valuation_engine import ValuationRouter, CompanyProfile, CompanyType, classify_company


# ═══════════════════════════════════════════════════════════════
# REPLACE the old fetch_company_data and calculate_valuation functions
# ═══════════════════════════════════════════════════════════════

def fetch_company_profile(ticker: str) -> Optional[CompanyProfile]:
    """Fetch company profile using the proper ValuationRouter."""
    return ValuationRouter.build_profile(ticker)


def calculate_proper_valuation(
    profile: CompanyProfile, 
    chaos_level: float, 
    risk_severity: float = 5.0
) -> 'StressedValuation':
    """Route to correct valuation model based on company type."""
    return ValuationRouter.value_company(profile, chaos_level, risk_severity)


# ═══════════════════════════════════════════════════════════════
# REPLACE the intelligence gathering to include SEC/SEBI filings
# ═══════════════════════════════════════════════════════════════

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
    
    # === PHASE 2: Multi-domain Tavily Search (same as before) ===
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


# ═══════════════════════════════════════════════════════════════
# ADD: Valuation Method Explanation Panel (shows in UI)
# ═══════════════════════════════════════════════════════════════

def render_valuation_method_panel(profile: CompanyProfile, valuation: 'StressedValuation'):
    """Show which valuation method was used and WHY."""
    
    from valuation_engine import ValuationRouter
    
    explanation = ValuationRouter.get_valuation_explanation(profile.company_type)
    
    st.markdown(f"""
    
        
            VALUATION METHODOLOGY
        
        
            {valuation.valuation_method}
        
        
            Company classified as: {profile.company_type.value.upper()}
            {explanation.replace(chr(10), '')}
        
    
    """, unsafe_allow_html=True)
    
    # Show cross-check values
    if valuation.method_values:
        st.markdown("**📊 Cross-Check Values:**")
        for method, value in valuation.method_values.items():
            st.markdown(f"• {method}: {value}", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ADD: Filing Intelligence Display Panel
# ═══════════════════════════════════════════════════════════════

def render_filing_intelligence_panel(filing_risks: List, filing_source: str):
    """Display regulatory filing intelligence."""
    
    if not filing_risks:
        st.info(f"📁 No filing risks extracted from {filing_source}")
        return
    
    st.markdown(f"""
    
        
            📁 REGULATORY FILING INTELLIGENCE
        
        
            Source: {filing_source} | Risks Found: {len(filing_risks)}
        
    
    """, unsafe_allow_html=True)
    
    for i, risk in enumerate(filing_risks[:8]):
        badge_color = "#ff6d00" if risk.risk_category in ["financial", "regulatory"] else "#ffab00"
        st.markdown(f"""
        
            
                {risk.risk_category.upper()}
            
             [{risk.source}]
            {risk.risk_text[:200]}...
        
        """, unsafe_allow_html=True)
PART 4: UPDATED MAIN ANALYSIS FLOW
Replace the run_full_analysis / launch section in your app.py:

if launch:
        with st.status("☣️ Activating Doomsday Swarm...", expanded=True) as status:
            
            # Step 1: Init
            st.write("🔌 Initializing AI clients...")
            gemini_client = get_gemini_client()
            tavily_client = get_tavily_client()
            model = find_best_model(gemini_client)
            st.write(f"✅ Model: `{model}`")
            
            # Step 2: World State
            st.write("📡 Scanning global threat environment...")
            world_state = fetch_world_state(tavily_client)
            st.session_state.world_state = world_state
            st.write(f"✅ World State: VIX={world_state.vix}, Fear={world_state.fear_level}")
            
            # Step 3: Company Profile (with proper classification)
            st.write(f"💰 Building company profile for {ticker}...")
            profile = ValuationRouter.build_profile(ticker)
            if not profile:
                st.error(f"❌ Failed to fetch data for '{ticker}'.")
                st.stop()
            st.session_state.profile = profile
            st.write(f"✅ {profile.name} | Type: **{profile.company_type.value.upper()}** | MCap: ${profile.market_cap/1e9:.1f}B")
            
            # Show valuation method selection
            st.write(f"📐 Valuation model selected: **{profile.company_type.value}** "
                    f"({'P/BV + DDM' if profile.company_type == CompanyType.FINANCIAL else 'Revenue Multiple' if profile.company_type == CompanyType.HIGH_GROWTH else 'FCF-DCF'})")
            
            # Step 4: Regulatory Filing Intelligence
            st.write(f"📁 Extracting regulatory filing risks ({'SEC EDGAR' if not profile.ticker.endswith('.NS') else 'SEBI/BSE'})...")
            filing_engine = UnifiedFilingEngine(tavily_client=tavily_client)
            filing_risks, filing_source = filing_engine.extract_all_risks(ticker)
            st.session_state.filing_risks = filing_risks
            st.session_state.filing_source = filing_source
            st.write(f"✅ {len(filing_risks)} risks from {filing_source}")
            
            # Step 5: Enhanced Intelligence (Filings + News + LLM)
            st.write("🔍 Multi-source intelligence gathering (Filings + News + AI)...")
            risks = run_enhanced_intelligence(gemini_client, tavily_client, model, ticker, profile, world_state)
            st.write(f"✅ Synthesized {len(risks)} potential risks")
            
            # Step 6: Debate
            st.write("🗣️ Fracture Tribunal — Adversarial debate...")
            verdicts = run_adversarial_debate(gemini_client, model, ticker, 
                                            {"name": profile.name, "sector": profile.sector}, 
                                            risks, world_state)
            st.session_state.verdicts = verdicts
            st.write(f"✅ {len(verdicts)} risks validated by tribunal")
            
            # Step 7: Mapping
            st.write("🌍 Mapping fracture points...")
            nodes, paths = run_geographic_mapping(gemini_client, model, ticker, verdicts)
            st.session_state.nodes = nodes
            st.session_state.paths = paths
            st.write(f"✅ {len(nodes)} fracture nodes mapped")
            
            # Step 8: Proper Multi-Model Valuation
            st.write(f"💀 Computing distressed valuation ({profile.company_type.value} model)...")
            avg_severity = sum(v.severity_score for v in verdicts) / len(verdicts) if verdicts else 5.0
            valuation = ValuationRouter.value_company(profile, chaos_level, avg_severity)
            st.session_state.valuation = valuation
            st.write(f"✅ Base: ${valuation.base_fair_value:.2f} → Distressed: ${valuation.distressed_value:.2f} ({valuation.downside_pct:.1f}%)")
            
            st.session_state.analysis_done = True
            st.session_state.last_chaos = chaos_level
            status.update(label="☣️ DOOMSDAY ANALYSIS COMPLETE", state="complete", expanded=False)
        
        st.rerun()
And in the results section, add these panels:

if st.session_state.analysis_done:
        # ... existing metrics and map code ...
        
        # After the waterfall chart, add:
        st.markdown('📐 VALUATION METHODOLOGY', unsafe_allow_html=True)
        
        col_method, col_filings = st.columns([1, 1])
        
        with col_method:
            render_valuation_method_panel(st.session_state.profile, st.session_state.valuation)
        
        with col_filings:
            render_filing_intelligence_panel(
                st.session_state.get("filing_risks", []),
                st.session_state.get("filing_source", "Unknown")
            )
        
        # ... rest of existing code (debate panel, etc.) ...
PART 5: WHAT THIS GIVES YOU THAT COMPETITORS WON'T HAVE
Feature	Most Hackathon Projects	Project Doomsday
Data Source	Just Tavily/web scraping	SEC EDGAR + SEBI + Tavily (multi-source triangulation)
Valuation	Single DCF for everything	Company-type-aware routing (P/BV for banks, Revenue Multiple for growth, FCF-DCF for mature)
Risk Quality	LLM hallucinations	Company self-disclosed risks from regulatory filings + confirmed by news
Financial Rigor	Might DCF a bank	Explicitly explains WHY each model is used
India Coverage	Usually ignored	SEBI/BSE filings pulled for .NS tickers
Transparency	Black box	Full valuation method explanation and cross-check values
QUICK REFERENCE: What Model for What Company
Input Ticker → Classify → Route to Model

NVDA (Mature Tech, +FCF)      → FCF-DCF
PLTR (High Growth, -FCF)      → Revenue Multiple + Path-to-Profit
JPM (Bank)                     → P/BV + DDM + Excess Return
HDFCBANK.NS (Indian Bank)      → P/BV + DDM
XOM (Energy/Cyclical)          → Normalized EV/EBITDA
SNOW (High Growth SaaS)        → Revenue Multiple
BRK-B (Holding/Financial)      → P/BV + Sum-of-Parts
RELIANCE.NS (Diversified)      → Sum-of-Parts / EV/EBITDA
When a judge asks "Why did you use P/BV for JPM instead of DCF?" — you explain that debt IS the business for banks, making FCF meaningless. That's the kind of answer that wins hackathons.