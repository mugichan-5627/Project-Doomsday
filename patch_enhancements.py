"""
Patch script: Apply both enhancements from "Project Doomsday enhancements.md"
Fix 1: Map tooltip multi-line formatting (add <br> tags)
Fix 2: Contagion Cascade Engine (additive new section)
"""
import re

with open('app.py', encoding='utf-8') as f:
    content = f.read()

# ================================================================
# FIX 1: Replace single-line hovertext with proper <br> formatting
# ================================================================
OLD_HOVER = (
    'hovertext=[f"{n.label}Severity: {n.severity:.1f}/10Domain: {n.category}'
    'Revenue Risk: {n.revenue_at_risk_pct:.0f}%{n.description[:100]}" for n in level_nodes],'
)
NEW_HOVER = (
    'hovertext=[(\n'
    '                f"<b>{n.label}</b><br>"\n'
    '                f"Severity: {n.severity:.1f}/10 | Prob: {n.probability:.0%}<br>"\n'
    '                f"Domain: {n.category} | Revenue Risk: {n.revenue_at_risk_pct:.0f}%<br>"\n'
    '                f"<i>{n.description[:90]}...</i>"\n'
    '            ) for n in level_nodes],'
)
if OLD_HOVER in content:
    content = content.replace(OLD_HOVER, NEW_HOVER)
    print("Fix 1 applied: hovertext formatted")
else:
    print("Fix 1 WARNING: hovertext pattern not found, trying regex...")
    pat = r'hovertext=\[f"\{n\.label\}Severity:.*?for n in level_nodes\],'
    if re.search(pat, content, re.DOTALL):
        content = re.sub(pat,
            'hovertext=[\n'
            '                (\n'
            '                    f"<b>{n.label}</b><br>"\n'
            '                    f"Severity: {n.severity:.1f}/10 | Prob: {n.probability:.0%}<br>"\n'
            '                    f"Domain: {n.category} | Revenue Risk: {n.revenue_at_risk_pct:.0f}%<br>"\n'
            '                    f"<i>{n.description[:90]}...</i>"\n'
            '                )\n'
            '                for n in level_nodes\n'
            '            ],',
            content, flags=re.DOTALL)
        print("Fix 1 applied via regex")
    else:
        print("Fix 1 FAILED: could not find hovertext pattern")

# ================================================================
# FIX 2: Add hoverlabel styling to the node trace
# ================================================================
OLD_SHOWLEGEND = '            name=f"{level.upper()} ({len(level_nodes)})",\n            showlegend=True\n        ))'
NEW_SHOWLEGEND = (
    '            name=f"{level.upper()} ({len(level_nodes)})",\n'
    '            showlegend=True,\n'
    '            hoverlabel=dict(\n'
    '                bgcolor="#0d1117",\n'
    '                bordercolor=c,\n'
    '                font=dict(family="monospace", size=11, color="#e0e0e0"),\n'
    '                align="left"\n'
    '            )\n'
    '        ))'
)
if OLD_SHOWLEGEND in content:
    content = content.replace(OLD_SHOWLEGEND, NEW_SHOWLEGEND)
    print("Fix 1b applied: hoverlabel styling added")
else:
    print("Fix 1b WARNING: showlegend pattern not found")

# ================================================================
# FIX 2: Insert Contagion Cascade Engine before render_waterfall
# ================================================================
CONTAGION_ENGINE = '''
# ============================================================
# CONTAGION CASCADE ENGINE
# ============================================================

def generate_contagion_chains(ai, company, validated_risks, chaos_level):
    """
    For top 3 risks by severity, generate second and third-order effects.
    Models how a single shock propagates through the company\'s financial structure.
    """
    if not validated_risks:
        return []

    sorted_risks = sorted(validated_risks, key=lambda r: float(r.get(\'severity_score\', r.get(\'severity\', 5))), reverse=True)[:3]

    company_name = getattr(company, \'name\', \'the company\')
    sector = getattr(company, \'sector\', \'general\') or \'general\'
    revenue = getattr(company, \'revenue\', 0) or 0
    debt = getattr(company, \'total_debt\', 0) or 0
    net_income = getattr(company, \'net_income\', 0) or 0
    margin = net_income / max(revenue, 1)

    def risk_title(r):
        return r.get(\'risk_description\', r.get(\'title\', \'Unknown\'))[:60]

    prompt = f"""You are a financial contagion analyst. For each primary risk event below,
model the CAUSAL CHAIN of how it propagates through {company_name}\'s financial structure.

Company Context:
- Sector: {sector}
- Revenue: ${revenue/1e9:.1f}B
- Debt: ${debt/1e9:.1f}B
- Profit Margin: {margin*100:.1f}%
- Chaos/Stress Level: {chaos_level:.2f}

For each primary risk, provide EXACTLY 3 propagation steps (second-order, third-order, fourth-order effects).
Each step: what breaks next, quantified impact estimate, time delay.

Primary Risks:
{chr(10).join([f"{i+1}. {risk_title(r)} (Severity: {r.get(\'severity_score\', r.get(\'severity\', 5))}/10)" for i, r in enumerate(sorted_risks)])}

Return ONLY valid JSON:
{{
  "chains": [
    {{
      "primary_risk": "name of trigger event",
      "primary_severity": 7,
      "cascade": [
        {{"order": 2, "effect": "second-order effect", "metric_impacted": "e.g. COGS", "magnitude": "e.g. +15%", "time_delay": "2-4 weeks", "cumulative_value_destruction_pct": 5.0}},
        {{"order": 3, "effect": "third-order effect", "metric_impacted": "e.g. Credit Rating", "magnitude": "1-notch downgrade", "time_delay": "1-3 months", "cumulative_value_destruction_pct": 12.0}},
        {{"order": 4, "effect": "fourth-order effect", "metric_impacted": "e.g. Refinancing Cost", "magnitude": "+200bps", "time_delay": "3-6 months", "cumulative_value_destruction_pct": 20.0}}
      ]
    }}
  ]
}}"""

    try:
        response = run_with_timeout(
            ai.generate, kwargs={"prompt": prompt, "temperature": 0.5, "json_mode": True, "max_tokens": 2000},
            timeout=40, default=None
        )
        chains_data = parse_json_safe(response)
        if chains_data and \'chains\' in chains_data and len(chains_data[\'chains\']) >= 1:
            return chains_data[\'chains\']
    except Exception:
        pass

    return generate_fallback_chains(sorted_risks, sector, chaos_level)


def generate_fallback_chains(risks, sector, chaos_level):
    """Intelligent fallback contagion chains based on sector patterns."""
    sector_lower = (sector or \'\').lower()

    if any(k in sector_lower for k in [\'energy\', \'oil\', \'gas\']):
        template = [
            {"order": 2, "effect": "Input cost spike forces margin compression", "metric_impacted": "Operating Margin",
             "magnitude": f"-{int(chaos_level*800+200)}bps", "time_delay": "1-2 weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 8 + 3, 1)},
            {"order": 3, "effect": "Credit agencies place on negative watch", "metric_impacted": "Credit Rating",
             "magnitude": "Negative outlook", "time_delay": "4-8 weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 15 + 6, 1)},
            {"order": 4, "effect": "Debt refinancing costs spike, capex cuts forced", "metric_impacted": "Capex Budget",
             "magnitude": f"-{int(chaos_level*30+10)}% cut", "time_delay": "2-4 months",
             "cumulative_value_destruction_pct": round(chaos_level * 22 + 10, 1)},
        ]
    elif any(k in sector_lower for k in [\'tech\', \'software\', \'semiconductor\']):
        template = [
            {"order": 2, "effect": "Supply chain disruption delays product launches", "metric_impacted": "Revenue Growth",
             "magnitude": f"-{int(chaos_level*500+100)}bps", "time_delay": "2-6 weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 7 + 2, 1)},
            {"order": 3, "effect": "Market share loss as competitors fill gap", "metric_impacted": "Market Share",
             "magnitude": f"-{int(chaos_level*3+1)}% share", "time_delay": "1-3 months",
             "cumulative_value_destruction_pct": round(chaos_level * 14 + 5, 1)},
            {"order": 4, "effect": "Talent attrition as stock compensation falls underwater", "metric_impacted": "R&D Productivity",
             "magnitude": f"{int(chaos_level*15+5)}% attrition spike", "time_delay": "3-6 months",
             "cumulative_value_destruction_pct": round(chaos_level * 20 + 8, 1)},
        ]
    elif any(k in sector_lower for k in [\'bank\', \'financial\', \'insurance\']):
        template = [
            {"order": 2, "effect": "Deposit flight / AUM redemptions accelerate", "metric_impacted": "Funding Cost",
             "magnitude": f"+{int(chaos_level*150+50)}bps", "time_delay": "Days to weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 10 + 4, 1)},
            {"order": 3, "effect": "Forced asset sales at distressed prices", "metric_impacted": "Book Value",
             "magnitude": f"-{int(chaos_level*12+4)}% writedown", "time_delay": "2-6 weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 18 + 8, 1)},
            {"order": 4, "effect": "Counterparty contagion triggers collateral calls", "metric_impacted": "Liquidity Ratio",
             "magnitude": "Below regulatory minimum", "time_delay": "1-3 months",
             "cumulative_value_destruction_pct": round(chaos_level * 28 + 12, 1)},
        ]
    else:
        template = [
            {"order": 2, "effect": "Revenue decline triggers cost restructuring", "metric_impacted": "Operating Costs",
             "magnitude": f"+{int(chaos_level*500+200)}bps as % of revenue", "time_delay": "1-4 weeks",
             "cumulative_value_destruction_pct": round(chaos_level * 7 + 3, 1)},
            {"order": 3, "effect": "Supplier tightens payment terms, working capital strain", "metric_impacted": "Working Capital",
             "magnitude": f"{int(chaos_level*20+10)} days DSO increase", "time_delay": "1-3 months",
             "cumulative_value_destruction_pct": round(chaos_level * 13 + 6, 1)},
            {"order": 4, "effect": "Dividend cut / buyback suspension signals distress", "metric_impacted": "Investor Confidence",
             "magnitude": "Multiple de-rating", "time_delay": "3-6 months",
             "cumulative_value_destruction_pct": round(chaos_level * 20 + 9, 1)},
        ]

    chains = []
    for risk in risks[:3]:
        chains.append({
            "primary_risk": risk.get(\'risk_description\', risk.get(\'title\', \'Unknown Risk\'))[:70],
            "primary_severity": float(risk.get(\'severity_score\', risk.get(\'severity\', 6))),
            "cascade": template
        })
    return chains


def render_contagion_section(chains, chaos_level):
    """Render the Contagion Cascade visualization section."""
    st.markdown(\'<div class="section-hdr">Contagion Cascade -- Second-Order Propagation Model</div>\', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-panel" style="margin-bottom:16px; border-left: 3px solid #ff6d00">
        <span style="color:#ff6d00; font-family:monospace; font-size:0.8em">[THEORY]</span>
        <span style="color:#7a8b9a; font-size:0.85em; margin-left:8px">
        In crisis regimes, asset correlations converge to 1. Individual risks do not remain isolated --
        they propagate through financial linkages, supplier networks, and investor psychology.
        This model traces causal chains from primary shock to terminal value destruction.
        </span>
    </div>
    """, unsafe_allow_html=True)

    if not chains:
        st.markdown(\'<div class="info-panel" style="color:#5a6f82">No contagion chains generated. Increase chaos level or re-run analysis.</div>\', unsafe_allow_html=True)
        return

    for idx, chain in enumerate(chains):
        primary = chain.get(\'primary_risk\', \'Unknown\')[:70]
        severity = chain.get(\'primary_severity\', 6)
        cascade = chain.get(\'cascade\', [])

        final_destruction = cascade[-1].get(\'cumulative_value_destruction_pct\', 10) if cascade else 10
        if final_destruction > 20:
            chain_color = "#ff4444"
            chain_label = "CRITICAL CHAIN"
        elif final_destruction > 12:
            chain_color = "#ff8c00"
            chain_label = "SEVERE CHAIN"
        else:
            chain_color = "#ffaa00"
            chain_label = "MODERATE CHAIN"

        st.markdown(f"""
        <div class="info-panel" style="border-left: 3px solid {chain_color}; margin-bottom: 6px">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
                <span style="color:{chain_color}; font-family:monospace; font-size:0.85em; font-weight:bold">
                    CHAIN {idx+1}: {primary}
                </span>
                <span style="color:{chain_color}; font-family:monospace; font-size:0.75em; border:1px solid {chain_color}; padding:2px 6px">
                    {chain_label}
                </span>
            </div>
            <div style="color:#5a6f82; font-size:0.8em; margin-bottom:10px">
                Primary Severity: {severity}/10 | Terminal Value Destruction: -{final_destruction:.1f}%
            </div>
        """, unsafe_allow_html=True)

        # Cascade steps
        for step_idx, step in enumerate(cascade):
            order = step.get(\'order\', step_idx + 2)
            effect = step.get(\'effect\', \'Unknown effect\')
            metric = step.get(\'metric_impacted\', \'N/A\')
            magnitude = step.get(\'magnitude\', \'N/A\')
            time_delay = step.get(\'time_delay\', \'N/A\')
            cum_dest = step.get(\'cumulative_value_destruction_pct\', 0)
            bar_w = min(int(cum_dest * 4), 100)
            step_color = "#ff4444" if step_idx == 2 else "#ff8c00" if step_idx == 1 else "#ffaa00"

            arrow = "&gt;&gt;&gt;" if step_idx == 0 else "&nbsp;&nbsp;&gt;&gt;&gt;"
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; margin:4px 0; padding:6px 8px; background:rgba(255,255,255,0.03); border-radius:4px">
                <div style="min-width:28px; color:{step_color}; font-family:monospace; font-size:0.8em; font-weight:bold; margin-right:8px">
                    [{order}]
                </div>
                <div style="flex:1">
                    <div style="color:#c8d6e5; font-size:0.85em">{arrow} {effect}</div>
                    <div style="color:#5a6f82; font-size:0.78em; margin-top:3px">
                        {metric}: <span style="color:{step_color}">{magnitude}</span>
                        &nbsp;| Delay: {time_delay}
                        &nbsp;| Cumulative: <span style="color:{step_color}">-{cum_dest:.1f}%</span>
                    </div>
                    <div style="margin-top:4px; height:3px; background:rgba(255,255,255,0.05); border-radius:2px">
                        <div style="width:{bar_w}%; height:100%; background:{step_color}; border-radius:2px; opacity:0.7"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(\'</div>\', unsafe_allow_html=True)

    # Compound Contagion Score
    if chains:
        max_dest = max(
            [c.get(\'cascade\', [{}])[-1].get(\'cumulative_value_destruction_pct\', 0) for c in chains if c.get(\'cascade\')],
            default=0
        )
        avg_dest = sum(
            [c.get(\'cascade\', [{}])[-1].get(\'cumulative_value_destruction_pct\', 0) for c in chains if c.get(\'cascade\')]
        ) / max(len(chains), 1)
        compound_factor = 1 + (chaos_level * 0.3 * (len(chains) - 1))
        compound_dest = min(avg_dest * compound_factor, 65)
        rho = min(0.4 + chaos_level * 0.5, 0.95)

        if compound_dest > 30:
            cc_color = "#ff4444"
            cc_status = "SYSTEMIC FAILURE REGIME"
        elif compound_dest > 18:
            cc_color = "#ff8c00"
            cc_status = "CONTAGION AMPLIFICATION"
        else:
            cc_color = "#ffaa00"
            cc_status = "CONTAINED PROPAGATION"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="info-panel" style="border-left:3px solid {cc_color}; text-align:center">
                <div style="color:#5a6f82; font-family:monospace; font-size:0.75em; margin-bottom:4px">COMPOUND CONTAGION ASSESSMENT</div>
                <div style="color:{cc_color}; font-size:2em; font-weight:bold; font-family:monospace">-{compound_dest:.1f}%</div>
                <div style="color:#5a6f82; font-size:0.78em; margin-top:4px">
                    {len(chains)} active chains | Compound factor: {compound_factor:.2f}x
                </div>
                <div style="color:{cc_color}; font-family:monospace; font-size:0.75em; margin-top:6px">{cc_status}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="info-panel" style="border-left:3px solid #5a6f82; text-align:center">
                <div style="color:#5a6f82; font-family:monospace; font-size:0.75em; margin-bottom:4px">CRISIS CORRELATION</div>
                <div style="color:#c8d6e5; font-size:2em; font-weight:bold; font-family:monospace">rho = {rho:.2f}</div>
                <div style="color:#5a6f82; font-size:0.78em; margin-top:4px">
                    In crisis regimes correlations converge to 1.<br>Diversification breaks down.
                </div>
            </div>
            """, unsafe_allow_html=True)

'''

# Insert Contagion Engine before render_waterfall
INSERT_BEFORE = '\ndef render_waterfall(val: SimpleValuation):'
if INSERT_BEFORE in content:
    content = content.replace(INSERT_BEFORE, CONTAGION_ENGINE + INSERT_BEFORE)
    print("Fix 2 applied: Contagion Cascade Engine inserted")
else:
    print("Fix 2 FAILED: could not find render_waterfall insertion point")

# ================================================================
# FIX 2b: Wire contagion into the ANALYSIS PIPELINE (after debate)
# ================================================================
OLD_STEP6 = "        st.session_state.verdicts = verdicts\n        add_log(f\"Tribunal complete: {len(verdicts)} risks validated, {len(risks) - len(verdicts)} dismissed\", \"ok\")"
NEW_STEP6 = """        st.session_state.verdicts = verdicts
        add_log(f\"Tribunal complete: {len(verdicts)} risks validated, {len(risks) - len(verdicts)} dismissed\", \"ok\")

        # STEP 5b: Contagion Cascade
        add_log(\"[SWARM] Modeling contagion propagation chains...\", \"info\")
        render_terminal()
        contagion_chains = generate_contagion_chains(ai, company, [v.__dict__ if hasattr(v, '__dict__') else v for v in verdicts], chaos)
        st.session_state['contagion_chains'] = contagion_chains
        add_log(f\"Contagion: {len(contagion_chains)} chains modeled\", \"ok\")
        render_terminal()"""

if OLD_STEP6 in content:
    content = content.replace(OLD_STEP6, NEW_STEP6)
    print("Fix 2b applied: contagion wired into pipeline")
else:
    print("Fix 2b WARNING: pipeline insertion point not found, trying partial match...")
    partial = "        st.session_state.verdicts = verdicts\n        add_log(f\"Tribunal complete:"
    if partial in content:
        idx = content.find(partial)
        end_idx = content.find('\n\n        # STEP 6', idx)
        if end_idx > 0:
            old_chunk = content[idx:end_idx]
            new_chunk = old_chunk + """

        # STEP 5b: Contagion Cascade
        add_log("[SWARM] Modeling contagion propagation chains...", "info")
        render_terminal()
        contagion_chains = generate_contagion_chains(ai, company, [v.__dict__ if hasattr(v, '__dict__') else v for v in verdicts], chaos)
        st.session_state['contagion_chains'] = contagion_chains
        add_log(f"Contagion: {len(contagion_chains)} chains modeled", "ok")
        render_terminal()"""
            content = content[:idx] + new_chunk + content[end_idx:]
            print("Fix 2b applied via partial match")

# ================================================================
# FIX 2c: Wire contagion render into the RESULTS SECTION
# ================================================================
# Insert after debate transcripts, before terminal log
OLD_TERMINAL = "        # TERMINAL LOG (collapsible)\n        if st.session_state.terminal_log:"
NEW_TERMINAL = """        # CONTAGION CASCADE
        if st.session_state.get('contagion_chains'):
            render_contagion_section(st.session_state['contagion_chains'], chaos)

        # TERMINAL LOG (collapsible)
        if st.session_state.terminal_log:"""

if OLD_TERMINAL in content:
    content = content.replace(OLD_TERMINAL, NEW_TERMINAL)
    print("Fix 2c applied: contagion render wired into results")
else:
    print("Fix 2c WARNING: terminal log marker not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nAll patches written. Running syntax check...")
