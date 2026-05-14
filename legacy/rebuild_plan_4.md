PART 2: THE VISUALIZATION (Inspired by worldmonitor & globalthreatmap)
2.1 Full Streamlit Dashboard
# app.py
"""
Project Doomsday: Main Streamlit Application
Dark theme, military-grade aesthetic, inspired by worldmonitor/globalthreatmap
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import asyncio
import json
from datetime import datetime
import time

# Import our modules
from world_state import WorldStateEngine, WorldState
from sentinel import GlobalSentinel
from debate_engine import FractureTribunal, TribunalOutput
from saboteur import LogisticsSaboteur, FractureNode
from vulture_dcf import VultureArchitect, CompanyFinancials, VultureValuation

# ═══════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════

st.set_page_config(
    page_title="☣️ PROJECT DOOMSDAY",
    page_icon="☣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════
# CUSTOM CSS (Dark Military Aesthetic)
# ═══════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background-color: #0a0a0f;
        color: #e0e0e0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1a2332;
    }
    
    /* Header bar */
    .doomsday-header {
        background: linear-gradient(90deg, #0d1117 0%, #1a0a0a 50%, #0d1117 100%);
        border: 1px solid #2d1f1f;
        border-radius: 4px;
        padding: 12px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .doomsday-title {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 1.4em;
        color: #ff4444;
        letter-spacing: 3px;
        text-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
    }
    
    .status-badge {
        background: #1a2332;
        border: 1px solid #2d4a3e;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 0.75em;
        color: #00e676;
        font-family: monospace;
    }
    
    .status-badge-critical {
        border-color: #ff1744;
        color: #ff1744;
        animation: pulse-critical 2s ease-in-out infinite;
    }
    
    @keyframes pulse-critical {
        0%, 100% { opacity: 1; box-shadow: 0 0 5px rgba(255, 23, 68, 0.3); }
        50% { opacity: 0.7; box-shadow: 0 0 15px rgba(255, 23, 68, 0.6); }
    }
    
    /* Metric cards */
    .metric-card {
        background: #0d1117;
        border: 1px solid #1a2332;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-label {
        font-size: 0.75em;
        color: #8899aa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Threat level colors */
    .threat-critical { color: #ff1744; }
    .threat-high { color: #ff6d00; }
    .threat-elevated { color: #ffd600; }
    .threat-low { color: #00e676; }
    
    /* Event feed */
    .event-feed {
        background: #0d1117;
        border: 1px solid #1a2332;
        border-radius: 8px;
        padding: 16px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .event-item {
        border-bottom: 1px solid #1a2332;
        padding: 8px 0;
        font-size: 0.85em;
    }
    
    .event-severity-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7em;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    /* Debate transcript */
    .debate-message {
        margin: 8px 0;
        padding: 12px;
        border-radius: 8px;
        font-size: 0.85em;
        line-height: 1.5;
    }
    
    .debate-bull {
        background: #0d1f0d;
        border-left: 3px solid #00e676;
    }
    
    .debate-bear {
        background: #1f0d0d;
        border-left: 3px solid #ff1744;
    }
    
    .debate-judge {
        background: #1a1a0d;
        border-left: 3px solid #ffd600;
    }
    
    /* Chaos slider custom */
    .chaos-slider-container {
        background: linear-gradient(90deg, #00e676, #ffd600, #ff6d00, #ff1744);
        border-radius: 4px;
        padding: 2px;
        margin: 10px 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: #2d4a3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════

def render_header(world_state: WorldState = None):
    threat = world_state.fear_level if world_state else "SCANNING"
    threat_class = f"threat-{threat.lower()}" if threat in ["CRITICAL", "HIGH"] else "threat-low"
    
    st.markdown(f"""
    
        ☣️ PROJECT DOOMSDAY
        
            ◉ SWARM ACTIVE
            
                THREAT: {threat}
            
            
                {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
        
    
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# FRACTURE MAP (The Centerpiece)
# ═══════════════════════════════════════════════════════

def render_fracture_map(nodes: list, paths: list = None):
    """
    Renders the global Fracture Map inspired by worldmonitor/globalthreatmap.
    Dark Mapbox style with color-coded severity markers.
    """
    
    if not nodes:
        st.info("🔍 No fracture nodes detected. Run analysis to populate the map.")
        return
    
    # Convert nodes to DataFrame
    df = pd.DataFrame([n.to_map_dict() for n in nodes])
    
    # Category icon mapping
    category_symbols = {
        "conflict": "triangle-up",
        "supply_chain": "square",
        "regulatory": "diamond",
        "financial": "circle",
        "cyber": "hexagon",
        "infrastructure": "pentagon"
    }
    
    fig = go.Figure()
    
    # Add supply chain paths as lines (if available)
    if paths:
        for path in paths:
            path_nodes = [n for n in nodes if n.node_id in path.get("nodes", [])]
            if len(path_nodes) >= 2:
                fig.add_trace(go.Scattermapbox(
                    lat=[n.latitude for n in path_nodes],
                    lon=[n.longitude for n in path_nodes],
                    mode='lines',
                    line=dict(width=2, color='rgba(255, 100, 100, 0.4)'),
                    name=path.get("description", "Supply Chain Path")[:50],
                    hoverinfo='text',
                    text=path.get("description", "")
                ))
    
    # Add fracture nodes by threat level
    for threat_level in ["critical", "high", "elevated", "monitoring"]:
        level_nodes = [n for n in nodes if n.threat_level == threat_level]
        if not level_nodes:
            continue
        
        colors = {
            "critical": "#FF1744",
            "high": "#FF6D00",
            "elevated": "#FFD600",
            "monitoring": "#00E676"
        }
        
        sizes = [n._calculate_marker_size() for n in level_nodes]
        
        hover_texts = []
        for n in level_nodes:
            hover_texts.append(
                f"{n.label}"
                f"Category: {n.category.upper()}"
                f"Severity: {n.severity:.1f}/10"
                f"Probability: {n.probability:.0%}"
                f"Revenue at Risk: {n.revenue_at_risk_pct:.1f}%"
                f"Time Horizon: {n.time_horizon}"
                f"{n.description[:150]}..."
            )
        
        fig.add_trace(go.Scattermapbox(
            lat=[n.latitude for n in level_nodes],
            lon=[n.longitude for n in level_nodes],
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=colors[threat_level],
                opacity=0.8,
                sizemode='diameter'
            ),
            text=[n.label for n in level_nodes],
            textposition="top center",
            textfont=dict(size=9, color=colors[threat_level]),
            hovertext=hover_texts,
            hoverinfo='text',
            name=f"⬤ {threat_level.upper()}"
        ))
    
    # Map layout (dark style matching worldmonitor)
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",  # Dark map style
            center=dict(lat=25, lon=40),  # Center on Middle East/Asia
            zoom=1.5,
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(13, 17, 23, 0.9)",
            bordercolor="#1a2332",
            borderwidth=1,
            font=dict(color="#e0e0e0", size=11),
            x=0.01,
            y=0.99
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        paper_bgcolor='#0a0a0f',
        plot_bgcolor='#0a0a0f',
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'displaylogo': False
    })


# ═══════════════════════════════════════════════════════
# VALUATION WATERFALL CHART
# ═══════════════════════════════════════════════════════

def render_waterfall(valuation: VultureValuation):
    """Waterfall chart showing value destruction path."""
    
    if not valuation.waterfall_data:
        return
    
    waterfall = valuation.waterfall_data
    
    # Separate into components
    labels = [w["label"] for w in waterfall if w["type"] != "reference"]
    values = [w["value"] for w in waterfall if w["type"] != "reference"]
    
    # Determine measure type for plotly waterfall
    measures = []
    for w in waterfall:
        if w["type"] == "reference":
            continue
        elif w["type"] == "start":
            measures.append("absolute")
        elif w["type"] == "end":
            measures.append("total")
        else:
            measures.append("relative")
    
    fig = go.Figure(go.Waterfall(
        name="Valuation Bridge",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        connector=dict(line=dict(color="rgba(63, 63, 63, 0.5)")),
        decreasing=dict(marker=dict(color="#ff1744")),
        increasing=dict(marker=dict(color="#00e676")),
        totals=dict(marker=dict(color="#ffd600")),
        textposition="outside",
        text=[f"${v:.2f}" if v > 0 else f"-${abs(v):.2f}" for v in values],
        textfont=dict(size=10, color="#e0e0e0")
    ))
    
    # Add current price reference line
    current_price = next((w["value"] for w in waterfall if w["type"] == "reference"), None)
    if current_price:
        fig.add_hline(
            y=current_price, 
            line_dash="dash", 
            line_color="#4488ff",
            annotation_text=f"Current Price: ${current_price:.2f}",
            annotation_font_color="#4488ff"
        )
    
    fig.update_layout(
        title=dict(
            text="💀 Value Destruction Waterfall",
            font=dict(color="#e0e0e0", size=14)
        ),
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        font=dict(color="#8899aa"),
        yaxis=dict(
            title="Per Share Value ($)",
            gridcolor='#1a2332',
            zerolinecolor='#2d4a3e'
        ),
        xaxis=dict(gridcolor='#1a2332'),
        height=400,
        margin=dict(t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# DEBATE TRANSCRIPT VIEWER
# ═══════════════════════════════════════════════════════

def render_debate_transcript(tribunal_output: TribunalOutput):
    """Renders the adversarial debate transcript."""
    
    st.markdown("### 🗣️ Fracture Tribunal — Adversarial Debate")
    
    for i, verdict in enumerate(tribunal_output.validated_risks + tribunal_output.dismissed_risks):
        status_emoji = "✅" if verdict.consensus_reached and verdict.severity_score >= 4 else "❌"
        
        with st.expander(
            f"{status_emoji} {verdict.risk_description[:80]}... | Severity: {verdict.severity_score:.1f}/10",
            expanded=(i == 0)
        ):
            # Verdict summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Severity", f"{verdict.severity_score:.1f}/10")
            with col2:
                st.metric("Probability", f"{verdict.probability:.0%}")
            with col3:
                st.metric("Time Horizon", verdict.time_horizon)
            
            # Debate transcript
            for msg in verdict.debate_transcript:
                try:
                    content = json.loads(msg.content)
                    display_text = content.get("argument", msg.content)
                except:
                    display_text = msg.content
                
                role_class = {
                    "bull_advocate": "debate-bull",
                    "bear_advocate": "debate-bear",
                    "black_swan_judge": "debate-judge"
                }.get(msg.role.value, "")
                
                role_emoji = {
                    "bull_advocate": "🟢 BULL",
                    "bear_advocate": "🔴 BEAR",
                    "black_swan_judge": "⚖️ JUDGE"
                }.get(msg.role.value, "")
                
                st.markdown(f"""
                
                    {role_emoji} (Round {msg.round_number})
                    {display_text[:500]}
                
                """, unsafe_allow_html=True)
            
            # Judge reasoning
            if verdict.judge_reasoning:
                st.markdown(f"""
                
                    ⚖️ FINAL VERDICT
                    {verdict.judge_reasoning}
                
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# METRICS ROW
# ═══════════════════════════════════════════════════════

def render_metrics(valuation: VultureValuation, tribunal: TribunalOutput, world_state: WorldState):
    """Top row of key metrics."""
    
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""
        
            ${valuation.base_per_share:.2f}
            Base Fair Value
        
        """, unsafe_allow_html=True)
    
    with cols[1]:
        color = "#ff1744" if valuation.downside_pct < -30 else "#ff6d00" if valuation.downside_pct < -15 else "#ffd600"
        st.markdown(f"""
        
            ${valuation.distressed_per_share:.2f}
            Distressed Value
        
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        
            {valuation.downside_pct:.1f}%
            Downside Risk
        
        """, unsafe_allow_html=True)
    
    with cols[3]:
        threat_color = {"CRITICAL": "#ff1744", "HIGH": "#ff6d00", "ELEVATED": "#ffd600", "LOW": "#00e676"}
        st.markdown(f"""
        
            
                {tribunal.overall_threat_level}
            
            Threat Level
        
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown(f"""
        
            {len(tribunal.validated_risks)}
            Validated Risks
        
        """, unsafe_allow_html=True)
    
    with cols[5]:
        st.markdown(f"""
        
            {world_state.vix:.1f}
            VIX (Fear Index)
        
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# EVENT FEED (Sidebar - like globalthreatmap)
# ═══════════════════════════════════════════════════════

def render_event_feed(tribunal: TribunalOutput):
    """Live-style event feed in sidebar."""
    
    st.sidebar.markdown("### 📡 Risk Feed")
    
    # Category filter (like globalthreatmap)
    categories = list(set(
        v.risk_description.split(":")[0] if ":" in v.risk_description else "General"
        for v in tribunal.validated_risks
    ))
    
    severity_badges = {
        "critical": 'CRITICAL',
        "high": 'HIGH',
        "elevated": 'ELEVATED',
        "monitoring": 'LOW'
    }
    
    for verdict in sorted(tribunal.validated_risks, key=lambda x: x.severity_score, reverse=True):
        if verdict.severity_score >= 8:
            badge = severity_badges["critical"]
        elif verdict.severity_score >= 6:
            badge = severity_badges["high"]
        elif verdict.severity_score >= 4:
            badge = severity_badges["elevated"]
        else:
            badge = severity_badges["monitoring"]
        
        st.sidebar.markdown(f"""
        
            {badge}
            {verdict.risk_description[:60]}...
            <small>Severity: {verdict.severity_score:.1f} | P: {verdict.probability:.0%} | {verdict.time_horizon}</small>
        
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════

def main():
    """Main application orchestrator."""
    
    # Initialize session state
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "tribunal_output" not in st.session_state:
        st.session_state.tribunal_output = None
    if "fracture_nodes" not in st.session_state:
        st.session_state.fracture_nodes = []
    if "valuation" not in st.session_state:
        st.session_state.valuation = None
    if "world_state" not in st.session_state:
        st.session_state.world_state = None
    if "chaos_level" not in st.session_state:
        st.session_state.chaos_level = 0.5
    
    # ═══ SIDEBAR ═══
    with st.sidebar:
        st.markdown("## ☣️ DOOMSDAY CONSOLE")
        st.markdown("---")
        
        # Ticker input
        ticker = st.text_input(
            "TARGET TICKER",
            value="TSMC",
            placeholder="e.g., MSFT, ASML, RELIANCE.NS"
        ).upper().strip()
        
        # Chaos slider
        st.markdown("### 🎚️ CHAOS LEVEL")
        chaos_level = st.slider(
            "Stress Intensity",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.chaos_level,
            step=0.05,
            format="%.2f",
            help="0.0 = Base Case | 1.0 = Maximum Doomsday"
        )
        st.session_state.chaos_level = chaos_level
        
        # Chaos level label
        if chaos_level <= 0.2:
            st.success("🟢 MILD STRESS")
        elif chaos_level <= 0.4:
            st.info("🔵 MODERATE STRESS")
        elif chaos_level <= 0.6:
            st.warning("🟡 SEVERE STRESS")
        elif chaos_level <= 0.8:
            st.error("🟠 CRISIS MODE")
        else:
            st.error("🔴 DOOMSDAY SCENARIO")
        
        st.markdown("---")
        
        # Launch button
        launch = st.button(
            "🚀 LAUNCH DOOMSDAY ANALYSIS",
            type="primary",
            use_container_width=True
        )
        
        # Event feed (populated after analysis)
        if st.session_state.tribunal_output:
            st.markdown("---")
            render_event_feed(st.session_state.tribunal_output)
    
    # ═══ MAIN CONTENT ═══
    
    # Render header
    render_header(st.session_state.world_state)
    
    if launch:
        run_full_analysis(ticker, chaos_level)
    
    # If analysis is complete, render everything
    if st.session_state.analysis_complete:
        # Metrics row
        render_metrics(
            st.session_state.valuation,
            st.session_state.tribunal_output,
            st.session_state.world_state
        )
        
        st.markdown("---")
        
        # Main map
        st.markdown("### 🌍 Global Fracture Map")
        render_fracture_map(
            st.session_state.fracture_nodes,
            st.session_state.supply_chain_paths
        )
        
        st.markdown("---")
        
        # Two columns: Waterfall + Debate
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            render_waterfall(st.session_state.valuation)
        
        with col_right:
            render_debate_transcript(st.session_state.tribunal_output)
        
        # Real-time chaos slider update (recompute DCF without re-running agents)
        if chaos_level != st.session_state.get("last_chaos_level"):
            st.session_state.last_chaos_level = chaos_level
            # Recompute valuation with new chaos level (fast — no API calls)
            architect = VultureArchitect()
            financials = st.session_state.get("financials")
            if financials:
                new_valuation = architect.calculate_distressed_value(
                    financials=financials,
                    chaos_level=chaos_level,
                    validated_risks=[
                        {"severity_score": v.severity_score, "revenue_at_risk_pct": v.probability * 20}
                        for v in st.session_state.tribunal_output.validated_risks
                    ]
                )
                st.session_state.valuation = new_valuation
                st.rerun()
    
    else:
        # Landing state
        st.markdown("""
        
            ☣️ AWAITING TARGET
            
                Enter a ticker symbol and launch analysis to activate the Doomsday Swarm.
            
            
                The swarm will scan global intelligence, debate risk validity, map fracture points,
                and compute distressed valuations — all in under 60 seconds.
            
        
        """, unsafe_allow_html=True)


def run_full_analysis(ticker: str, chaos_level: float):
    """Execute the full Doomsday pipeline with progress tracking."""
    
    import os
    from google import genai
    from tavily import TavilyClient
    
    # Initialize clients
    gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    model = "gemini-2.5-flash-preview-04-17"  # Or your best available model
    
    progress = st.progress(0, text="Initializing Doomsday Swarm...")
    
    # Phase 1: World State
    progress.progress(10, text="📡 Scanning Global Threat Environment...")
    world_engine = WorldStateEngine(tavily_api_key=os.getenv("TAVILY_API_KEY"))
    world_state = world_engine.generate()
    st.session_state.world_state = world_state
    
    # Phase 2: Company Financials
    progress.progress(20, text="💰 Fetching Financial Data...")
    architect = VultureArchitect()
    financials = architect.fetch_financials(ticker)
    
    if not financials or financials.market_cap == 0:
        st.error(f"❌ Could not fetch financials for {ticker}. Check ticker symbol.")
        return
    
    st.session_state.financials = financials
    company_context = (
        f"Sector: {financials.sector} | "
        f"Market Cap: ${financials.market_cap/1e9:.1f}B | "
        f"Revenue: ${financials.revenue_ttm/1e9:.1f}B | "
        f"EBITDA Margin: {financials.ebitda_margin:.1%} | "
        f"Net Debt: ${financials.net_debt/1e9:.1f}B"
    )
    
    # Phase 3: Intelligence Gathering
    progress.progress(35, text="🔍 Global Sentinel scanning multi-domain intelligence...")
    sentinel = GlobalSentinel(gemini_client, tavily_client, model)
    raw_risks = asyncio.run(sentinel.gather_intelligence(
        ticker=ticker,
        company_context=company_context,
        world_state_text=world_state.to_prompt_context()
    ))
    
    # Phase 4: Adversarial Debate
    progress.progress(55, text="🗣️ Fracture Tribunal — Agents debating risk validity...")
    tribunal = FractureTribunal(client=gemini_client, model=model)
    tribunal_output = asyncio.run(tribunal.run_tribunal(
        ticker=ticker,
        company_context=company_context,
        raw_risks=[{
            "id": r.id,
            "domain": r.domain,
            "description": r.description,
            "evidence": r.evidence,
            "initial_severity": r.initial_severity,
            "geographic_hint": r.geographic_hint,
            "affected_revenue_pct": r.affected_revenue_pct
        } for r in raw_risks],
        world_state=world_state.to_dict()
    ))
    st.session_state.tribunal_output = tribunal_output
    
    # Phase 5: Geographic Mapping
    progress.progress(75, text="🌍 Logistics Saboteur mapping fracture points...")
    saboteur = LogisticsSaboteur(gemini_client, model)
    validated_risk_dicts = [{
        "risk_id": v.risk_id,
        "description": v.risk_description,
        "severity": v.severity_score,
        "probability": v.probability,
        "time_horizon": v.time_horizon,
        "judge_reasoning": v.judge_reasoning
    } for v in tribunal_output.validated_risks]
    
    nodes, paths = asyncio.run(saboteur.map_risks(ticker, validated_risk_dicts))
    st.session_state.fracture_nodes = nodes
    st.session_state.supply_chain_paths = paths
    
    # Phase 6: Valuation
    progress.progress(90, text="💀 Vulture Architect computing distressed valuation...")
    valuation = architect.calculate_distressed_value(
        financials=financials,
        chaos_level=chaos_level,
        validated_risks=[{
            "severity_score": v.severity_score,
            "revenue_at_risk_pct": v.probability * 20  # Proxy
        } for v in tribunal_output.validated_risks]
    )
    st.session_state.valuation = valuation
    
    # Done!
    progress.progress(100, text="☣️ DOOMSDAY ANALYSIS COMPLETE")
    time.sleep(1)
    progress.empty()
    
    st.session_state.analysis_complete = True
    st.session_state.last_chaos_level = chaos_level
    st.rerun()


if __name__ == "__main__":
    main()
