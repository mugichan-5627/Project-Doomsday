Complete Review & Analysis
I've reviewed your full app.py. Here are my findings:

1. Severity/Probability — Confirmation & Suggested Guard
You're right — there's no clamping on the Judge's output. The code takes raw values:

severity_score = float(judge.get("final_severity", risk.get("severity", 5)))
probability    = float(judge.get("final_probability", risk.get("probability", 0.4)))
Add these two lines right after (around line 1040, inside run_debate, just before the return RiskVerdict(...) statement):

# Clamp Judge outputs to valid ranges (LLMs occasionally return out-of-bounds)
    final_severity = max(1.0, min(10.0, float(judge.get("final_severity", risk.get("severity", 5)))))
    final_probability = max(0.01, min(0.99, float(judge.get("final_probability", risk.get("probability", 0.4)))))
Then update the RiskVerdict construction to use final_severity and final_probability instead of the inline float(judge.get(...)) calls. Tiny change, zero risk.

2. Map Tooltip Fix — Your Specific Issue
Looking at your render_map function (around line 700), the hovertext is already using <br> tags:

hovertext=[(
    f"{n.label}"
    f"Severity: {n.severity:.1f}/10 | Prob: {n.probability:.0%}"
    f"Domain: {n.category} | Revenue Risk: {n.revenue_at_risk_pct:.0f}%"
    f"{n.description[:90]}..."
) for n in level_nodes],
The issue you're seeing (everything on one line) is likely because Plotly's Scattermapbox hover doesn't always respect <br> properly without setting hoverlabel width or using <br> within a proper hovertemplate.

Replace the hovertext construction in the main markers section (around line 710) with this improved version:

# Main markers
            fig.add_trace(go.Scattermapbox(
                lat=[n.latitude for n in level_nodes],
                lon=[n.longitude for n in level_nodes],
                mode="markers+text",
                marker=dict(
                    size=[max(10, 8 + n.severity * 2) for n in level_nodes],
                    color=c, opacity=0.85
                ),
                text=[n.label for n in level_nodes],
                textposition="top center",
                textfont=dict(size=9, color=c),
                customdata=[[n.severity, n.probability*100, n.category, n.revenue_at_risk_pct, n.description[:120]] for n in level_nodes],
                hovertemplate=(
                    "%{text}"
                    ""
                    "Severity: %{customdata[0]:.1f}/10"
                    "Probability: %{customdata[1]:.0f}%"
                    "Domain: %{customdata[2]}"
                    "Revenue at Risk: %{customdata[3]:.0f}%"
                    ""
                    "%{customdata[4]}"
                    "<extra></extra>"
                ),
                name=f"{level.upper()} ({len(level_nodes)})",
                showlegend=True,
                hoverlabel=dict(
                    bgcolor="#0d1117",
                    bordercolor=c,
                    font=dict(family="JetBrains Mono, monospace", size=11, color="#e0e0e0"),
                    align="left",
                    namelength=-1
                )
            ))
Key differences:

Uses hovertemplate instead of hovertext — this gives Plotly proper control over line breaks
Uses customdata array for structured data access
<extra></extra> suppresses the secondary box
align="left" in hoverlabel ensures left-aligned text
Each metric gets its own line
Blank <br> between sections for readability
Remove the old hovertext=[...] and hoverinfo="text" lines — hovertemplate replaces both.

3. Review of Valuation Transparency Panel
Looking at your render_valuation_transparency function — it's well-integrated and uses your existing CSS classes (.info-panel, .ws-row, .ws-k, .ws-v, .section-hdr).

One issue I see: In the Path 1 (Financial) formula section, you reference roe and book_value but these are set to 0 at the top:

book_value = 0  # not directly stored
roe = 0         # not directly stored
This means the Path 1 formula display will show zeros. Fix: Derive them the same way compute_valuation does:

# Derive values not stored on dataclass but used in compute_valuation
    book_value = (market_cap * 0.55) / shares if shares > 0 else 0  # same as compute_valuation
    roe = net_income / max(market_cap * 0.55, 1) if market_cap > 0 else 0  # same estimate
Add these two lines right after where book_value = 0 and roe = 0 are set (around the top of render_valuation_transparency).

4. Additional Suggestions (Non-Breaking, High-Impact)
A. Add Debate Scoring Transparency to the Panel
Since you now have the full debate system documented, add a Section [3.5] between the formula and market anchoring that shows how severity was determined. Add this after the [3] VALUATION FORMULA section in render_valuation_transparency:

# ── [3.5] RISK SCORING METHODOLOGY ──
    if verdicts:
        avg_sev = sum(v.severity_score for v in verdicts) / len(verdicts)
        avg_prob = sum(v.probability for v in verdicts) / len(verdicts)
        highest = max(verdicts, key=lambda v: v.severity_score)
        
        st.markdown(f"""
        
            [3.5] RISK SCORING -- ADVERSARIAL TRIBUNAL
            
                Each risk passes through a 3-agent adversarial debate. The Judge's calibration:
                8+ = Catastrophic (>25% impairment) | 6-7 = Material | 4-5 = Moderate | <4 = Dismissed
            
            Risks Debated{len(verdicts)} validated / debated
            Avg Severity (Judge){avg_sev:.2f}/10
            Avg Probability (Judge){avg_prob:.0%}
            Highest Threat{highest.risk_description[:60]}... ({highest.severity_score:.1f}/10)
            Judge Temperature0.3 (low variance, high conviction)
            
                Scoring pipeline: Intelligence Scan (AI + Tavily) --> Bear Advocate (T=0.6) --> Bull Advocate (T=0.6) --> Judge (T=0.3)
                Revenue-at-risk % is set at scan stage, not modified by tribunal. Severity and probability are Judge's final word.
                Dismissal rule: verdict=DISMISSED AND severity<4 --> risk dropped entirely from analysis.
            
        
        """, unsafe_allow_html=True)
B. One Structural Observation
In your generate_contagion_chains, you pass verdicts as:

[v.__dict__ if hasattr(v, '__dict__') else v for v in verdicts]
But inside generate_contagion_chains, you access them with:

r.get('severity_score', r.get('severity', 5))
This works because RiskVerdict.__dict__ will have severity_score as a key. But it's fragile. The code works fine now — just noting it. No change needed.

5. Summary of All Changes (All Additive)
#	Change	Location	Risk
1	Clamp severity to 1-10, probability to 0.01-0.99	run_debate(), 2 lines	Zero
2	Replace hovertext with hovertemplate + customdata in map	render_map()	Zero (visual improvement only)
3	Derive book_value and roe for Path 1 display	render_valuation_transparency(), 2 lines	Zero
4	Add Section [3.5] Risk Scoring Methodology	render_valuation_transparency()	Zero (additive display)
None of these touch your calculation logic, visual aesthetic, or architecture. All are additive fixes or display improvements.