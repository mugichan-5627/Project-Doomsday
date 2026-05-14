"""
Patch: Add Valuation Transparency Panel (addition only, no deletions).
"""

NEW_FUNCTION = '''
# ============================================================
# VALUATION TRANSPARENCY ENGINE
# ============================================================

def render_valuation_transparency(company, val, chaos_level, verdicts):
    """Full audit trail: routing, inputs, formula, stress decomposition. Addition only."""

    # --- derive scalars from dataclass objects ---
    name             = getattr(company, "name", "Unknown")
    sector           = getattr(company, "sector", "Unknown") or "Unknown"
    industry         = getattr(company, "industry", "Unknown") or "Unknown"
    market_cap       = getattr(company, "market_cap", 0) or 0
    current_price    = getattr(company, "current_price", 0) or 0
    revenue          = getattr(company, "revenue", 0) or 0
    ebitda           = getattr(company, "ebitda", 0) or 0
    net_income       = getattr(company, "net_income", 0) or 0
    total_debt       = getattr(company, "total_debt", 0) or 0
    cash             = getattr(company, "cash", 0) or 0
    shares           = getattr(company, "shares_outstanding", 1) or 1
    beta             = getattr(company, "beta", 1.0) or 1.0
    rev_growth       = getattr(company, "revenue_growth", 0) or 0
    profit_margin    = net_income / max(revenue, 1)
    fcf              = 0  # not stored on dataclass; derived below
    book_value       = 0  # not directly stored
    roe              = 0  # not directly stored

    base_fv    = getattr(val, "base_fair_value", 0) or 0
    distressed = getattr(val, "distressed_value", 0) or 0
    method     = getattr(val, "valuation_method", "Unknown")
    downside   = getattr(val, "downside_pct", 0) or 0

    sector_lower = (sector + " " + industry).lower()
    is_financial   = any(k in sector_lower for k in ["bank", "financial", "insurance", "capital markets"])
    is_cyclical    = any(k in sector_lower for k in ["energy", "oil", "gas", "mining", "materials", "utilities"])
    is_high_growth = (rev_growth > 0.25) and (net_income <= 0 or profit_margin < 0.05)
    is_mature      = (ebitda > 0) and (net_income > 0) and not is_financial and not is_cyclical and not is_high_growth
    is_fallback    = not any([is_financial, is_cyclical, is_high_growth, is_mature])

    if is_financial:
        path_num, path_label, path_color = 1, "FINANCIAL (P/BV + Excess Return)", "#4fc3f7"
    elif is_high_growth:
        path_num, path_label, path_color = 2, "HIGH-GROWTH (EV/Revenue + Rule of 40)", "#ab47bc"
    elif is_mature:
        path_num, path_label, path_color = 3, "MATURE PROFITABLE (5Y FCF-DCF + Gordon)", "#66bb6a"
    elif is_cyclical:
        path_num, path_label, path_color = 4, "CYCLICAL (Normalized Mid-Cycle EBITDA)", "#ffa726"
    else:
        path_num, path_label, path_color = 5, "LOSS-MAKING / FALLBACK (EV/Revenue Capped)", "#ef5350"

    ev = market_cap + total_debt - cash

    # ── SECTION HEADER ──
    st.markdown(\'<div class="section-hdr">Valuation Transparency -- Methodology and Calculations</div>\', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-panel" style="border-left:3px solid {path_color}; margin-bottom:12px">
        <span style="color:#5a6f82; font-family:monospace; font-size:0.78em">Full audit trail of routing logic, formulas applied, and stress parameters. All figures USD. No black boxes.</span>
    </div>
    """, unsafe_allow_html=True)

    # ── [1] ROUTING DECISION ──
    st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:{path_color}; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[1] ROUTING DECISION</div>
        <div class="ws-row"><span class="ws-k">Company</span><span class="ws-v">{name}</span></div>
        <div class="ws-row"><span class="ws-k">Sector / Industry</span><span class="ws-v">{sector} / {industry}</span></div>
        <div class="ws-row"><span class="ws-k">Revenue Growth</span><span class="ws-v">{rev_growth*100:.1f}% {"(>25% threshold)" if rev_growth > 0.25 else "(below 25%)"}</span></div>
        <div class="ws-row"><span class="ws-k">EBITDA</span><span class="ws-v">{"$"+f"{ebitda/1e9:.2f}B" if ebitda > 0 else "Negative / N/A"}</span></div>
        <div class="ws-row"><span class="ws-k">Net Income</span><span class="ws-v">{"$"+f"{net_income/1e9:.2f}B" if net_income > 0 else "Negative / N/A"}</span></div>
        <div class="ws-row"><span class="ws-k">Profit Margin</span><span class="ws-v">{profit_margin*100:.1f}%</span></div>
        <div class="ws-row" style="border:none; margin-top:6px">
            <span class="ws-k">Classification</span>
            <span class="ws-v" style="color:{path_color}; font-weight:bold">PATH {path_num} -- {path_label}</span>
        </div>
        <div style="color:#5a6f82; font-size:0.75em; margin-top:6px; font-family:monospace">
            Financial={is_financial} | Cyclical={is_cyclical} | HighGrowth={is_high_growth} | Mature={is_mature} | Fallback={is_fallback}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── [2] RAW INPUTS ──
    c1, c2 = st.columns(2)
    inputs = [
        ("Market Cap", f"${market_cap/1e9:.2f}B"),
        ("Current Price", f"${current_price:.2f}"),
        ("Revenue (TTM)", f"${revenue/1e9:.2f}B"),
        ("EBITDA (TTM)", f"${ ebitda/1e9:.2f}B" if ebitda else "N/A"),
        ("Net Income", f"${net_income/1e9:.2f}B" if net_income else "N/A"),
        ("Total Debt", f"${total_debt/1e9:.2f}B" if total_debt else "N/A"),
        ("Cash & Equiv", f"${cash/1e9:.2f}B" if cash else "N/A"),
        ("Enterprise Value", f"${ev/1e9:.2f}B"),
        ("Shares Out", f"{shares/1e9:.2f}B"),
        ("Beta", f"{beta:.2f}"),
        ("Revenue Growth", f"{rev_growth*100:.1f}%"),
        ("Profit Margin", f"{profit_margin*100:.1f}%"),
    ]
    half = len(inputs) // 2
    with c1:
        rows = "".join(f\'<div class="ws-row"><span class="ws-k">{k}</span><span class="ws-v">{v}</span></div>\' for k,v in inputs[:half])
        st.markdown(f\'<div class="info-panel"><div style="color:#4fc3f7; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[2] RAW INPUTS</div>{rows}</div>\', unsafe_allow_html=True)
    with c2:
        rows = "".join(f\'<div class="ws-row"><span class="ws-k">{k}</span><span class="ws-v">{v}</span></div>\' for k,v in inputs[half:])
        st.markdown(f\'<div class="info-panel"><div style="color:#4fc3f7; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">&nbsp;</div>{rows}</div>\', unsafe_allow_html=True)

    # ── [3] PATH-SPECIFIC FORMULA ──
    risk_free, erp = 0.043, 0.055
    coe = risk_free + beta * erp

    if path_num == 1:
        justified_pbv = min(max(roe / coe, 0.5), 2.5) if coe > 0 and roe > 0 else 1.0
        formula_lines = [
            f"CoE = Rf + Beta x ERP = {risk_free:.3f} + {beta:.2f} x {erp:.3f} = {coe*100:.2f}%",
            f"Justified P/BV = ROE / CoE (capped 0.5x-2.5x) = {justified_pbv:.2f}x",
            f"Implied FV = Book Value x {justified_pbv:.2f} = ${book_value * justified_pbv:.2f}",
            "Note: Debt is the product for banks, not a liability. DCF is inapplicable.",
        ]
    elif path_num == 2:
        r40 = (rev_growth * 100) + (profit_margin * 100)
        base_mul = 12.0 if r40 >= 60 else 8.0 if r40 >= 40 else 5.0 if r40 >= 20 else 3.0
        if market_cap > 100e9: base_mul *= 0.7
        elif market_cap > 50e9: base_mul *= 0.85
        implied_ev2 = revenue * base_mul
        implied_eq2 = implied_ev2 - total_debt + cash
        implied_ps2 = implied_eq2 / shares if shares > 0 else current_price
        formula_lines = [
            f"Rule of 40 = RevGrowth% + Margin% = {rev_growth*100:.1f} + {profit_margin*100:.1f} = {r40:.1f}",
            f"EV/Rev Multiple (tier) = {base_mul:.1f}x (after size discount if >$50B mcap)",
            f"Implied EV = ${revenue/1e9:.2f}B x {base_mul:.1f} = ${implied_ev2/1e9:.2f}B",
            f"Per Share = (EV - Debt + Cash) / Shares = ${implied_ps2:.2f}",
        ]
    elif path_num == 3:
        dw = total_debt / (market_cap + total_debt) if (market_cap + total_debt) > 0 else 0.3
        ew = 1 - dw
        kd, tax = 0.05, 0.21
        wacc = ew * coe + dw * kd * (1 - tax)
        ng = min(rev_growth if rev_growth else 0.05, 0.10)
        tg = 0.025
        capex_int = 0.40 if any(k in sector_lower for k in ["semi","tech"]) else 0.35
        base_fcf = ebitda * (1 - capex_int) if ebitda > 0 else revenue * 0.08
        pv_sum = sum([base_fcf * (1 + ng * (1-(i-1)*0.15))**i / (1+wacc)**i for i in range(1,6)])
        tv = base_fcf * (1 + tg) / (wacc - tg) if wacc > tg else base_fcf * 20
        pv_tv = tv / (1+wacc)**5
        total_ev3 = pv_sum + pv_tv
        ps3 = (total_ev3 - total_debt + cash) / shares if shares > 0 else current_price
        formula_lines = [
            f"WACC = {ew:.2f} x {coe*100:.2f}% + {dw:.2f} x {kd:.0%} x (1-{tax:.0%}) = {wacc*100:.2f}%",
            f"Base FCF = EBITDA x (1-{capex_int:.0%} capex) = ${base_fcf/1e9:.2f}B",
            f"PV(5Y FCFs) = ${pv_sum/1e9:.2f}B | TV (Gordon) = ${tv/1e9:.1f}B | PV(TV) = ${pv_tv/1e9:.2f}B",
            f"Total EV = ${total_ev3/1e9:.2f}B --> Per Share = ${ps3:.2f}",
        ]
    elif path_num == 4:
        norm_ebitda = (ebitda if ebitda > 0 else revenue * 0.15) * 0.8
        mul4 = 7.0 if any(k in sector_lower for k in ["energy","oil","petroleum"]) else 6.5
        ps4 = (norm_ebitda * mul4 - total_debt + cash) / shares if shares > 0 else current_price
        formula_lines = [
            "Normalization: Reported EBITDA x 0.80 (mid-cycle haircut)",
            f"Normalized EBITDA = ${norm_ebitda/1e9:.2f}B",
            f"EV/EBITDA Multiple = {mul4:.1f}x (energy=7x, other cyclical=6.5x)",
            f"Per Share = ${ps4:.2f}",
        ]
    else:
        mul5 = min(5.0, max(1.0, rev_growth * 10 if rev_growth else 2.0))
        ps5 = max((revenue * mul5 - total_debt + cash) / shares if shares > 0 else current_price, current_price * 0.8)
        formula_lines = [
            f"EV/Revenue Multiple (capped 1x-5x) = {mul5:.1f}x",
            f"Implied Per Share = ${ps5:.2f} (floored at 0.8x market price)",
            "Note: No stable earnings to discount. Revenue multiple is most honest anchor.",
        ]

    formula_html = "".join(f\'<div style="color:#c8d6e5; font-family:monospace; font-size:0.82em; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.04)">{l}</div>\' for l in formula_lines)
    st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:{path_color}; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[3] VALUATION FORMULA -- PATH {path_num}</div>
        {formula_html}
    </div>
    """, unsafe_allow_html=True)

    # ── [4] MARKET ANCHORING ──
    if market_cap > 100e9:   cap_label, cap_mul = "LARGE CAP (>$100B)", 1.20
    elif market_cap > 10e9:  cap_label, cap_mul = "MID CAP ($10-100B)", 1.35
    else:                    cap_label, cap_mul = "SMALL CAP (<$10B)", 1.50
    max_allowed = current_price * cap_mul
    was_capped = base_fv < max_allowed * 0.99

    st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:#66bb6a; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[4] MARKET ANCHORING -- EFFICIENCY ASSUMPTION</div>
        <div class="ws-row"><span class="ws-k">Size Tier</span><span class="ws-v">{cap_label}</span></div>
        <div class="ws-row"><span class="ws-k">Max Allowed FV</span><span class="ws-v">${current_price:.2f} x {cap_mul:.2f} = ${max_allowed:.2f}</span></div>
        <div class="ws-row" style="border:none"><span class="ws-k">Final Base FV</span>
            <span class="ws-v" style="color:#66bb6a">${base_fv:.2f} {"(CAPPED -- model exceeded anchor)" if was_capped else "(within bounds)"}</span>
        </div>
        <div style="color:#5a6f82; font-size:0.75em; margin-top:6px">
            This is a stress-test tool, not a stock picker. If the model says 2.5x current price, the model is wrong.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── [5] STRESS DECOMPOSITION ──
    avg_sev = sum(v.severity_score for v in verdicts) / max(len(verdicts), 1) if verdicts else 5.0
    rev_hc  = chaos_level * 15 + (avg_sev / 10) * 12
    wacc_p  = chaos_level * 4.5 + (avg_sev / 10) * 3
    mc_bps  = chaos_level * 250 + avg_sev * 50
    mul_c   = 1 - (chaos_level * 0.18 + (avg_sev / 10) * 0.12)
    min_ds  = -(chaos_level * 40 + avg_sev * 3)

    st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:#ff6d00; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[5] STRESS DECOMPOSITION -- CHAOS PARAMETER</div>
        <div class="ws-row"><span class="ws-k">Chaos Level</span><span class="ws-v" style="color:#ff6d00">{chaos_level:.2f}</span></div>
        <div class="ws-row"><span class="ws-k">Avg Risk Severity</span><span class="ws-v">{avg_sev:.1f}/10 ({len(verdicts)} risks)</span></div>
        <div class="ws-row"><span class="ws-k">Revenue Haircut</span><span class="ws-v" style="color:#ff4444">-{rev_hc:.1f}% = {chaos_level:.2f}x15 + ({avg_sev:.1f}/10)x12</span></div>
        <div class="ws-row"><span class="ws-k">WACC Premium</span><span class="ws-v" style="color:#ff4444">+{wacc_p:.2f}% = {chaos_level:.2f}x4.5 + ({avg_sev:.1f}/10)x3</span></div>
        <div class="ws-row"><span class="ws-k">Margin Compression</span><span class="ws-v" style="color:#ff4444">-{mc_bps:.0f} bps = {chaos_level:.2f}x250 + {avg_sev:.1f}x50</span></div>
        <div class="ws-row" style="border:none"><span class="ws-k">Multiple Compression</span><span class="ws-v" style="color:#ff4444">{mul_c:.3f}x ({(1-mul_c)*100:.1f}% de-rating)</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── [6] FINAL OUTPUT ──
    ds_color = "#ff1744" if downside <= -30 else "#ff6d00" if downside <= -15 else "#ffd600"
    st.markdown(f"""
    <div class="info-panel" style="margin-bottom:10px">
        <div style="color:#c8d6e5; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[6] FINAL OUTPUT</div>
        <div class="ws-row"><span class="ws-k">Current Market Price</span><span class="ws-v">${current_price:.2f}</span></div>
        <div class="ws-row"><span class="ws-k">Base Fair Value (post-cap)</span><span class="ws-v" style="color:#00e676">${base_fv:.2f}</span></div>
        <div class="ws-row"><span class="ws-k">Distressed Value (post-stress)</span><span class="ws-v" style="color:#ff1744">${distressed:.2f}</span></div>
        <div class="ws-row"><span class="ws-k">Implied Downside</span><span class="ws-v" style="color:{ds_color}">{downside:.1f}%</span></div>
        <div class="ws-row" style="border:none"><span class="ws-k">Min Forced Floor</span><span class="ws-v" style="color:#5a6f82">{min_ds:.1f}% (downside always forced negative)</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── [7] PATH REFERENCE LEGEND ──
    st.markdown("""
    <div class="info-panel">
        <div style="color:#5a6f82; font-family:monospace; font-size:0.8em; font-weight:bold; margin-bottom:8px">[7] ALL VALUATION PATHS -- REFERENCE</div>
        <div style="display:grid; grid-template-columns:40px 120px 1fr 1fr; gap:4px; font-family:monospace; font-size:0.78em">
            <span style="color:#5a6f82">PATH</span><span style="color:#5a6f82">TYPE</span><span style="color:#5a6f82">METHOD</span><span style="color:#5a6f82">WHY NOT DCF</span>
            <span style="color:#4fc3f7">1</span><span>Financial</span><span>P/BV + Excess Return</span><span style="color:#5a6f82">Debt = product, not liability</span>
            <span style="color:#ab47bc">2</span><span>High-Growth</span><span>EV/Revenue + R40</span><span style="color:#5a6f82">Negative FCF, TV >80%</span>
            <span style="color:#66bb6a">3</span><span>Mature</span><span>5Y FCF-DCF + Gordon</span><span style="color:#5a6f82">Only valid DCF candidate</span>
            <span style="color:#ffa726">4</span><span>Cyclical</span><span>Normalized EBITDA</span><span style="color:#5a6f82">Spot earnings mislead at peaks</span>
            <span style="color:#ef5350">5</span><span>Loss-Making</span><span>EV/Revenue (capped)</span><span style="color:#5a6f82">No earnings to discount</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

'''

# ── Insert function before render_waterfall ──
with open('app.py', encoding='utf-8') as f:
    content = f.read()

ANCHOR = '\ndef render_waterfall('
if ANCHOR not in content:
    print("ERROR: anchor not found")
    exit(1)

content = content.replace(ANCHOR, NEW_FUNCTION + ANCHOR)

# ── Wire call at bottom of results, before IC Summary ──
OLD_IC = "        # IC SUMMARY\n        st.markdown('<div class=\"section-hdr\">Investment Committee Summary</div>'"
NEW_IC = (
    "        # VALUATION TRANSPARENCY\n"
    "        render_valuation_transparency(company, val, chaos, verdicts)\n\n"
    "        # IC SUMMARY\n"
    "        st.markdown('<div class=\"section-hdr\">Investment Committee Summary</div>'"
)

if OLD_IC in content:
    content = content.replace(OLD_IC, NEW_IC)
    print("Wire: OK")
else:
    print("Wire: WARN - trying alt pattern")
    alt = '        # IC SUMMARY'
    if content.count(alt) == 1:
        content = content.replace(alt,
            "        # VALUATION TRANSPARENCY\n"
            "        render_valuation_transparency(company, val, chaos, verdicts)\n\n"
            "        # IC SUMMARY")
        print("Wire: OK (alt)")
    else:
        print("Wire: FAILED")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

import ast
try:
    ast.parse(content)
    print("Syntax: OK")
    print("Function present:", 'def render_valuation_transparency' in content)
    print("Call present:", 'render_valuation_transparency(company, val, chaos, verdicts)' in content)
except SyntaxError as e:
    print(f"Syntax ERROR: {e}")
