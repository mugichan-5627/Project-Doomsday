"""
Patch: Implement all 4 changes from 'review of app python in markdown form.md'
  1. Clamp severity 1-10, probability 0.01-0.99 in run_debate()
  2. Replace hovertext/hoverinfo with hovertemplate+customdata in render_map()
  3. Derive book_value and roe in render_valuation_transparency()
  4. Add Section [3.5] Risk Scoring Methodology in render_valuation_transparency()
All additive — zero deletions to calculation logic.
"""
import ast

with open('app.py', encoding='utf-8') as f:
    content = f.read()

original_len = content.count('\n')
issues = []

# ═══════════════════════════════════════════════════════
# CHANGE 1: Clamp severity & probability in run_debate()
# ═══════════════════════════════════════════════════════
OLD1 = (
    '    return RiskVerdict(\n'
    '        risk_id=risk.get("id", f"RISK_{hash(risk_title) % 999:03d}"),\n'
    '        risk_description=risk.get("description", risk_title),\n'
    '        domain=risk.get("domain", "unknown"),\n'
    '        severity_score=float(judge.get("final_severity", risk.get("severity", 5))),\n'
    '        probability=float(judge.get("final_probability", risk.get("probability", 0.4))),'
)
NEW1 = (
    '    # Clamp Judge outputs — LLMs occasionally return out-of-bounds values\n'
    '    final_severity = max(1.0, min(10.0, float(judge.get("final_severity", risk.get("severity", 5)))))\n'
    '    final_probability = max(0.01, min(0.99, float(judge.get("final_probability", risk.get("probability", 0.4)))))\n'
    '\n'
    '    return RiskVerdict(\n'
    '        risk_id=risk.get("id", f"RISK_{hash(risk_title) % 999:03d}"),\n'
    '        risk_description=risk.get("description", risk_title),\n'
    '        domain=risk.get("domain", "unknown"),\n'
    '        severity_score=final_severity,\n'
    '        probability=final_probability,'
)

if OLD1 in content:
    content = content.replace(OLD1, NEW1)
    print('[OK] Change 1: Severity/probability clamps added')
else:
    issues.append('Change 1: anchor not found')
    print('[!!] Change 1: FAILED — anchor not found')

# ═══════════════════════════════════════════════════════
# CHANGE 2: Replace hovertext+hoverinfo with hovertemplate+customdata
# ═══════════════════════════════════════════════════════
OLD2 = (
    '            hovertext=[(\n'
    '                f"<b>{n.label}</b><br>"\n'
    '                f"Severity: {n.severity:.1f}/10 | Prob: {n.probability:.0%}<br>"\n'
    '                f"Domain: {n.category} | Revenue Risk: {n.revenue_at_risk_pct:.0f}%<br>"\n'
    '                f"<i>{n.description[:90]}...</i>"\n'
    '            ) for n in level_nodes],\n'
    '            hoverinfo="text",\n'
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
NEW2 = (
    '            customdata=[[n.severity, n.probability*100, n.category, n.revenue_at_risk_pct, n.description[:120]] for n in level_nodes],\n'
    '            hovertemplate=(\n'
    '                "<b>%{text}</b><br>"\n'
    '                "<br>"\n'
    '                "Severity: %{customdata[0]:.1f}/10<br>"\n'
    '                "Probability: %{customdata[1]:.0f}%<br>"\n'
    '                "Domain: %{customdata[2]}<br>"\n'
    '                "Revenue at Risk: %{customdata[3]:.0f}%<br>"\n'
    '                "<br>"\n'
    '                "%{customdata[4]}<br>"\n'
    '                "<extra></extra>"\n'
    '            ),\n'
    '            name=f"{level.upper()} ({len(level_nodes)})",\n'
    '            showlegend=True,\n'
    '            hoverlabel=dict(\n'
    '                bgcolor="#0d1117",\n'
    '                bordercolor=c,\n'
    '                font=dict(family="JetBrains Mono, monospace", size=11, color="#e0e0e0"),\n'
    '                align="left",\n'
    '                namelength=-1\n'
    '            )\n'
    '        ))'
)

if OLD2 in content:
    content = content.replace(OLD2, NEW2)
    print('[OK] Change 2: hovertemplate+customdata applied to map markers')
else:
    issues.append('Change 2: anchor not found')
    print('[!!] Change 2: FAILED — anchor not found')

# ═══════════════════════════════════════════════════════
# CHANGE 3: Derive book_value and roe in render_valuation_transparency()
# ═══════════════════════════════════════════════════════
OLD3 = (
    '    fcf              = 0  # not stored on dataclass; derived below\n'
    '    book_value       = 0  # not directly stored\n'
    '    roe              = 0  # not directly stored'
)
NEW3 = (
    '    fcf              = 0  # not stored on dataclass; derived below\n'
    '    # Derive book_value and roe the same way compute_valuation does\n'
    '    book_value       = (market_cap * 0.55) / shares if shares > 0 else 0\n'
    '    roe              = net_income / max(market_cap * 0.55, 1) if market_cap > 0 else 0'
)

if OLD3 in content:
    content = content.replace(OLD3, NEW3)
    print('[OK] Change 3: book_value and roe derived correctly for Path 1')
else:
    issues.append('Change 3: anchor not found')
    print('[!!] Change 3: FAILED — anchor not found')

# ═══════════════════════════════════════════════════════
# CHANGE 4: Add Section [3.5] Risk Scoring Methodology
# Insert AFTER the [3] formula block, BEFORE [4] Market Anchoring
# ═══════════════════════════════════════════════════════
OLD4 = '    # \u2500\u2500 [4] MARKET ANCHORING \u2500\u2500'
NEW4 = '''    # ── [3.5] RISK SCORING METHODOLOGY ──
    if verdicts:
        avg_sev_35  = sum(v.severity_score for v in verdicts) / len(verdicts)
        avg_prob_35 = sum(v.probability for v in verdicts) / len(verdicts)
        highest_35  = max(verdicts, key=lambda v: v.severity_score)
        st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:#ab47bc; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[3.5] RISK SCORING -- ADVERSARIAL TRIBUNAL</div>
        <div style="color:#5a6f82; font-size:0.75em; font-family:monospace; margin-bottom:8px">
            Each risk passes through a 3-agent adversarial debate. Judge calibration:<br>
            8+ = Catastrophic (&gt;25% impairment) | 6-7 = Material | 4-5 = Moderate | &lt;4 = Dismissed
        </div>
        <div class="ws-row"><span class="ws-k">Risks Debated</span><span class="ws-v">{len(verdicts)} validated / debated</span></div>
        <div class="ws-row"><span class="ws-k">Avg Severity (Judge)</span><span class="ws-v">{avg_sev_35:.2f}/10</span></div>
        <div class="ws-row"><span class="ws-k">Avg Probability (Judge)</span><span class="ws-v">{avg_prob_35:.0%}</span></div>
        <div class="ws-row"><span class="ws-k">Highest Threat</span><span class="ws-v" style="color:#ff4444">{highest_35.risk_description[:60]}... ({highest_35.severity_score:.1f}/10)</span></div>
        <div class="ws-row" style="border:none"><span class="ws-k">Judge Temperature</span><span class="ws-v">0.3 (low variance, high conviction)</span></div>
        <div style="color:#5a6f82; font-size:0.74em; font-family:monospace; margin-top:8px">
            Pipeline: Intel Scan (AI + Tavily) → Bear Advocate (T=0.6) → Bull Advocate (T=0.6) → Judge (T=0.3)<br>
            Revenue-at-risk % is set at scan stage, not modified by tribunal.<br>
            Dismissal rule: verdict=DISMISSED AND severity&lt;4 → risk dropped from analysis.
        </div>
    </div>
        """, unsafe_allow_html=True)

    # ── [4] MARKET ANCHORING ──'''

if OLD4 in content:
    content = content.replace(OLD4, NEW4)
    print('[OK] Change 4: Section [3.5] Risk Scoring Methodology added')
else:
    issues.append('Change 4: anchor not found — trying fallback')
    # Try unicode-escaped version
    OLD4b = '    # \u2500\u2500 [4] MARKET ANCHORING \u2500\u2500'
    if OLD4b in content:
        content = content.replace(OLD4b, NEW4)
        print('[OK] Change 4: Section [3.5] added (fallback anchor)')
    else:
        # Last resort: search by substring
        idx = content.find('[4] MARKET ANCHORING')
        if idx != -1:
            # Find line start
            line_start = content.rfind('\n', 0, idx) + 1
            old_line = content[line_start:content.find('\n', idx)+1]
            content = content.replace(old_line, NEW4.lstrip() + '\n', 1)
            print('[OK] Change 4: Section [3.5] added (last resort)')
        else:
            print('[!!] Change 4: FAILED')

# ═══════════════════════════════════════════════════════
# VALIDATE & WRITE
# ═══════════════════════════════════════════════════════
try:
    ast.parse(content)
    print('\n[OK] Syntax: clean')
except SyntaxError as e:
    issues.append(f'Syntax error: {e}')
    print(f'[!!] Syntax ERROR: {e}')
    exit(1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = content.count('\n')
print(f'[OK] Written. Lines: {original_len} → {new_len} (+{new_len - original_len})')

print('\n' + '='*55)
if not issues:
    print('ALL 4 CHANGES APPLIED SUCCESSFULLY')
else:
    print(f'{len(issues)} issue(s):')
    for i in issues: print(f'  [!!] {i}')
print('='*55)
