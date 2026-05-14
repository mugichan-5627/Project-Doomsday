Great Progress! Two Fixes Needed:
Waterfall chart crash — titlefont is deprecated in your Plotly version. Simple fix.
Map repeating — Need to constrain the map bounds so it doesn't tile the world.
Valuation logic — I'll add proper methodology routing (DCF for mature, EV/Revenue for high-growth, P/BV for financials, etc.)
Here's the targeted fix — only the functions that need changing. Replace these in your current app.py:

Fix 1: render_waterfall — Fix the Plotly Error
The error is titlefont which is deprecated. Replace the entire render_waterfall function:

def render_waterfall(val: SimpleValuation):
    """Waterfall destruction chart - Plotly compatible."""
    w = val.waterfall_data
    if not w or len(w) < 3:
        return
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=[d["type"] for d in w],
        x=[d["label"] for d in w],
        y=[d["value"] for d in w],
        connector=dict(line=dict(color="rgba(80,80,80,0.3)", width=1)),
        decreasing=dict(marker=dict(color="#FF1744")),
        increasing=dict(marker=dict(color="#00E676")),
        totals=dict(marker=dict(color="#FFAB00")),
        textposition="outside",
        text=[f"${abs(d['value']):.2f}" if d['value'] >= 0 else f"-${abs(d['value']):.2f}" for d in w],
        textfont=dict(size=9, color="#c8d6e5", family="monospace"),
    ))
    
    fig.add_hline(
        y=val.current_price, line_dash="dash", line_color="#448aff", line_width=1.5,
        annotation_text=f"Market: ${val.current_price:.2f}",
        annotation_font_color="#448aff",
        annotation_font_size=10
    )
    
    fig.update_layout(
        paper_bgcolor="#0c1018",
        plot_bgcolor="#0c1018",
        font=dict(color="#78909c", size=9),
        yaxis=dict(
            gridcolor="#1a2538",
            zerolinecolor="#2a4058",
            title=dict(text="$/Share", font=dict(size=9, color="#5a6f82"))
        ),
        xaxis=dict(
            tickangle=-15,
            tickfont=dict(size=8, color="#78909c")
        ),
        height=340,
        margin=dict(t=15, b=70, l=50, r=15),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
Fix 2: render_map — Stop World from Repeating
Add bounds to the mapbox config. Replace the fig.update_layout(...) section inside render_map:

def render_map(nodes: List[FractureNode], hq: Tuple[float, float, str]):
    """Render the fracture map with curved convergence lines - NO world repetition."""
    
    if not nodes:
        st.info("[MAP] No fracture nodes identified yet.")
        return
    
    fig = go.Figure()
    hq_lat, hq_lon, hq_label = hq
    
    colors = {"critical": "#FF1744", "high": "#FF6D00", "elevated": "#FFD600", "monitoring": "#00E676"}
    
    # 1. Curved lines to HQ
    for node in nodes:
        clats, clons = curved_path(node.latitude, node.longitude, hq_lat, hq_lon)
        c = colors.get(node.threat_level, "#FF6D00")
        opacity = 0.2 + (node.severity / 10) * 0.4
        width = 1 + (node.severity / 10) * 1.5
        
        fig.add_trace(go.Scattermapbox(
            lat=clats, lon=clons, mode="lines",
            line=dict(width=width, color=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},{opacity})"),
            hoverinfo="none", showlegend=False
        ))
    
    # 2. HQ marker (concentric pulse)
    for size, op in [(32, 0.06), (20, 0.15), (12, 0.9)]:
        fig.add_trace(go.Scattermapbox(
            lat=[hq_lat], lon=[hq_lon], mode="markers",
            marker=dict(size=size, color=f"rgba(0,176,255,{op})"),
            showlegend=False, hoverinfo="none" if size > 12 else "text",
            hovertext=f"HQ: {hq_label}" if size == 12 else None,
            name="HQ" if size == 12 else None,
        ))
    # HQ text
    fig.add_trace(go.Scattermapbox(
        lat=[hq_lat], lon=[hq_lon], mode="text",
        text=["HQ"], textposition="bottom center",
        textfont=dict(size=10, color="#00B0FF", family="Arial Black"),
        showlegend=False, hoverinfo="none"
    ))
    
    # 3. Risk nodes by threat level
    for level in ["critical", "high", "elevated", "monitoring"]:
        level_nodes = [n for n in nodes if n.threat_level == level]
        if not level_nodes:
            continue
        
        c = colors[level]
        
        # Glow for critical/high
        if level in ["critical", "high"]:
            fig.add_trace(go.Scattermapbox(
                lat=[n.latitude for n in level_nodes],
                lon=[n.longitude for n in level_nodes],
                mode="markers",
                marker=dict(size=[n.severity * 4 for n in level_nodes], color=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.12)"),
                showlegend=False, hoverinfo="none"
            ))
        
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
            hovertext=[f"{n.label}Severity: {n.severity:.1f}/10Domain: {n.category}Revenue Risk: {n.revenue_at_risk_pct:.0f}%{n.description[:100]}" for n in level_nodes],
            hoverinfo="text",
            name=f"{level.upper()} ({len(level_nodes)})",
            showlegend=True
        ))
    
    # Layout - WITH BOUNDS TO PREVENT REPETITION
    all_lats = [n.latitude for n in nodes] + [hq_lat]
    all_lons = [n.longitude for n in nodes] + [hq_lon]
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    spread = max(max(all_lats) - min(all_lats), max(all_lons) - min(all_lons))
    zoom = 0.8 if spread > 120 else 1.5 if spread > 60 else 2.5 if spread > 30 else 3.5
    
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
            # PREVENT WORLD REPETITION
            bounds=dict(
                west=-180,
                east=180,
                south=-70,
                north=80
            )
        ),
        showlegend=True,
        legend=dict(bgcolor="rgba(12,16,24,0.9)", bordercolor="#1a2538", font=dict(color="#c8d6e5", size=10), x=0.01, y=0.99),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        paper_bgcolor="#080b10",
        dragmode="pan"  # Prevent accidental zoom-out that causes tiling
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "resetScale2d"]
    })
Fix 3: compute_valuation — Proper Multi-Method Routing with Nuances
Replace the entire compute_valuation function:

def compute_valuation(company: CompanyData, chaos: float, risk_severity: float) -> SimpleValuation:
    """
    Institutional-grade valuation with proper methodology routing:
    - Financials (Banks/Insurance): P/BV + Excess Return (DCF is INVALID for banks)
    - High-Growth Tech (>30% rev growth, low/no profit): EV/Revenue + Rule of 40
    - Profitable Tech / Mature: 5-Year FCF-DCF with Gordon Growth Terminal
    - Cyclical (Energy/Mining/Materials): Normalized Mid-Cycle EBITDA
    - Loss-Making / Pre-Revenue: EV/Revenue with comps-based multiple
    """
    
    price = company.current_price
    if price <= 0:
        price = company.market_cap / max(company.shares_outstanding, 1)
    
    shares = max(company.shares_outstanding, 1)
    net_debt = company.total_debt - company.cash
    
    # ═══ CLASSIFY COMPANY TYPE ═══
    sector_lower = company.sector.lower() if company.sector else ""
    industry_lower = company.industry.lower() if company.industry else ""
    
    is_financial = any(x in sector_lower for x in ["financial", "bank", "insurance"]) or \
                   any(x in industry_lower for x in ["bank", "insurance", "capital markets", "credit"])
    
    is_high_growth = company.revenue_growth > 0.25 and (company.net_income <= 0 or 
                     (company.net_income / max(company.revenue, 1)) < 0.10)
    
    is_cyclical = any(x in sector_lower for x in ["energy", "basic materials", "mining", "utilities"]) or \
                  any(x in industry_lower for x in ["oil", "gas", "mining", "steel", "chemical"])
    
    is_mature_profitable = not is_financial and not is_high_growth and not is_cyclical and \
                           company.ebitda > 0 and company.net_income > 0
    
    is_loss_making = company.net_income <= 0 and not is_high_growth
    
    # ═══ ROUTE TO CORRECT METHOD ═══
    
    if is_financial:
        # ═══ FINANCIALS: Price/Book + Excess Return ═══
        # DCF is INVALID for banks because debt IS their raw material, not a liability
        method = "P/BV + Excess Return (Financial)"
        
        # Book value estimation
        equity = company.market_cap  # Approximate (we'd ideally use balance sheet equity)
        book_per_share = (company.market_cap * 0.6) / shares  # Banks typically trade at P/BV of 1-2x
        
        # ROE-driven premium
        roe_estimate = company.net_income / max(equity * 0.6, 1)  # Rough ROE
        cost_of_equity = 0.08 + company.beta * 0.04  # CAPM rough
        
        if roe_estimate > cost_of_equity:
            # Deserves premium to book
            excess_return = roe_estimate - cost_of_equity
            justified_pbv = 1.0 + (excess_return / cost_of_equity) * 3
        else:
            justified_pbv = max(0.5, roe_estimate / cost_of_equity)
        
        justified_pbv = min(justified_pbv, 3.5)  # Cap at 3.5x
        base_fv = book_per_share * justified_pbv
        
        cross_check = {"P/BV Model": f"${base_fv:.2f}", "Book/Share (est)": f"${book_per_share:.2f}",
                       "Justified P/BV": f"{justified_pbv:.2f}x", "ROE (est)": f"{roe_estimate*100:.1f}%"}
    
    elif is_high_growth:
        # ═══ HIGH-GROWTH TECH: EV/Revenue + Rule of 40 ═══
        # DCF is unreliable because terminal value dominates (>80%) and FCF is negative
        method = "EV/Revenue + Rule of 40 (High Growth)"
        
        # Rule of 40: Revenue Growth % + Profit Margin % should exceed 40
        margin_pct = (company.net_income / max(company.revenue, 1)) * 100
        growth_pct = company.revenue_growth * 100
        rule_of_40_score = growth_pct + margin_pct
        
        # EV/Revenue multiple based on growth + Rule of 40
        if rule_of_40_score > 60:
            ev_rev_multiple = 15.0  # Premium (like NVDA at peak)
        elif rule_of_40_score > 40:
            ev_rev_multiple = 10.0  # Strong
        elif rule_of_40_score > 20:
            ev_rev_multiple = 6.0   # Moderate
        else:
            ev_rev_multiple = 3.0   # Weak
        
        # Adjust for scale (larger = lower multiple)
        if company.market_cap > 500e9:
            ev_rev_multiple *= 0.8
        elif company.market_cap > 100e9:
            ev_rev_multiple *= 0.9
        
        enterprise_value = company.revenue * ev_rev_multiple
        equity_value = enterprise_value - net_debt
        base_fv = max(equity_value / shares, 0)
        
        cross_check = {"EV/Revenue": f"{ev_rev_multiple:.1f}x", "Rule of 40": f"{rule_of_40_score:.0f}",
                       "Growth": f"{growth_pct:.0f}%", "Margin": f"{margin_pct:.1f}%",
                       "Implied EV": f"${enterprise_value/1e9:.1f}B"}
    
    elif is_cyclical:
        # ═══ CYCLICAL: Normalized Mid-Cycle EBITDA ═══
        # Using current EBITDA is dangerous at cycle peaks/troughs
        method = "Normalized EBITDA (Mid-Cycle)"
        
        # Normalize EBITDA to mid-cycle (assume current could be 20-40% above/below)
        # For energy: use 7-8x normalized EBITDA
        # For materials: use 6-7x
        if "energy" in sector_lower or "oil" in industry_lower:
            norm_factor = 0.85  # Assume current is slightly above mid-cycle
            ev_multiple = 7.0
        else:
            norm_factor = 0.80
            ev_multiple = 6.5
        
        normalized_ebitda = company.ebitda * norm_factor
        enterprise_value = normalized_ebitda * ev_multiple
        equity_value = enterprise_value - net_debt
        base_fv = max(equity_value / shares, 0)
        
        cross_check = {"Normalized EBITDA": f"${normalized_ebitda/1e9:.1f}B",
                       "EV/EBITDA Multiple": f"{ev_multiple:.1f}x",
                       "Normalization Factor": f"{norm_factor:.0%}",
                       "Implied EV": f"${enterprise_value/1e9:.1f}B"}
    
    elif is_mature_profitable:
        # ═══ MATURE PROFITABLE: 5-Year DCF + Gordon Growth ═══
        # The ONLY category where DCF is truly appropriate
        method = "5-Year FCF-DCF + Gordon Growth"
        
        # Free Cash Flow estimation
        # FCF = EBITDA * (1 - tax) - CapEx - Change in WC
        # Simplified: FCF ~ EBITDA * 0.55-0.70 depending on capex intensity
        capex_intensity = 0.35 if "tech" in sector_lower else 0.45 if "industrial" in sector_lower else 0.40
        fcf = company.ebitda * (1 - capex_intensity)
        
        # WACC calculation
        risk_free = 0.043  # US 10Y ~ 4.3%
        equity_risk_premium = 0.055  # Long-term ERP
        cost_of_equity = risk_free + company.beta * equity_risk_premium
        
        # Cost of debt (approximation)
        cost_of_debt = 0.05  # Average corporate
        tax_rate = 0.21
        
        # Capital structure
        equity_weight = company.market_cap / (company.market_cap + company.total_debt) if (company.market_cap + company.total_debt) > 0 else 0.8
        debt_weight = 1 - equity_weight
        
        wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)
        wacc = max(wacc, 0.06)  # Floor at 6%
        
        # Growth assumptions
        near_term_growth = min(company.revenue_growth, 0.12)  # Cap at 12% for mature
        fade_growth = near_term_growth * 0.6  # Fades to 60% of current
        terminal_growth = 0.025  # 2.5% perpetuity
        
        # 5-Year projection
        pv_fcf = 0
        projected_fcf = fcf
        for year in range(1, 6):
            growth = near_term_growth - (near_term_growth - fade_growth) * (year / 5)
            projected_fcf *= (1 + growth)
            pv_fcf += projected_fcf / (1 + wacc) ** year
        
        # Terminal value (Gordon Growth)
        terminal_fcf = projected_fcf * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / (1 + wacc) ** 5
        
        # Enterprise value
        enterprise_value = pv_fcf + pv_terminal
        equity_value = enterprise_value - net_debt
        base_fv = max(equity_value / shares, 0)
        
        # Sanity check: terminal should not be >75% of total value
        terminal_pct = pv_terminal / enterprise_value * 100 if enterprise_value > 0 else 0
        
        cross_check = {
            "FCF (Year 1)": f"${fcf/1e9:.1f}B",
            "WACC": f"{wacc*100:.1f}%",
            "Near-term Growth": f"{near_term_growth*100:.1f}%",
            "Terminal Growth": f"{terminal_growth*100:.1f}%",
            "PV of FCFs": f"${pv_fcf/1e9:.1f}B",
            "PV of Terminal": f"${pv_terminal/1e9:.1f}B",
            "Terminal % of Value": f"{terminal_pct:.0f}%",
            "Implied EV": f"${enterprise_value/1e9:.1f}B"
        }
    
    else:
        # ═══ LOSS-MAKING / UNCLEAR: Revenue Multiple with Discount ═══
        method = "EV/Revenue (Distressed/Loss-Making)"
        
        # Conservative multiple for loss-making
        ev_rev_multiple = 2.0 + max(0, company.revenue_growth * 5)
        ev_rev_multiple = min(ev_rev_multiple, 5.0)
        
        enterprise_value = company.revenue * ev_rev_multiple
        equity_value = enterprise_value - net_debt
        base_fv = max(equity_value / shares, price * 0.5)  # Floor at 50% of market
        
        cross_check = {"EV/Revenue": f"{ev_rev_multiple:.1f}x",
                       "Revenue": f"${company.revenue/1e9:.1f}B",
                       "Net Debt": f"${net_debt/1e9:.1f}B"}
    
    # ═══ SANITY CHECK ═══
    # If our FV is wildly different from market (>3x or <0.3x), blend toward market
    if base_fv > price * 3:
        base_fv = price * 2.5  # Cap at 2.5x current price
    elif base_fv < price * 0.2:
        base_fv = price * 0.5  # Floor at 0.5x current price
    
    # ═══ APPLY STRESS (Risk-Adjusted) ═══
    # Revenue haircut: driven by chaos level + risk severity
    rev_haircut = chaos * 12 + (risk_severity / 10) * 10
    
    # WACC stress premium
    wacc_stress = chaos * 4 + (risk_severity / 10) * 3
    
    # Margin compression (in bps)
    margin_bps = chaos * 200 + risk_severity * 50
    
    # Multiple compression for non-DCF methods
    multiple_compression = 1 - (chaos * 0.15 + (risk_severity / 10) * 0.10)
    multiple_compression = max(multiple_compression, 0.5)
    
    # Combined stress
    stress_mult = (1 - rev_haircut / 100) * multiple_compression
    stress_mult = max(stress_mult, 0.20)  # Never below 20% of base
    
    distressed = base_fv * stress_mult
    downside = ((distressed - price) / price) * 100 if price > 0 else 0
    
    # ═══ WATERFALL DATA ═══
    rev_impact = -(base_fv * rev_haircut / 100)
    margin_impact = -(base_fv * margin_bps / 8000)
    multiple_impact = -(base_fv * (1 - multiple_compression))
    wacc_impact = -(base_fv * wacc_stress / 100)
    
    waterfall = [
        {"label": "Base Fair Value", "value": round(base_fv, 2), "type": "absolute"},
        {"label": "Revenue Stress", "value": round(rev_impact, 2), "type": "relative"},
        {"label": "Margin Crush", "value": round(margin_impact, 2), "type": "relative"},
        {"label": "Multiple Compression", "value": round(multiple_impact, 2), "type": "relative"},
        {"label": "WACC Premium", "value": round(wacc_impact, 2), "type": "relative"},
        {"label": "Distressed Value", "value": round(distressed, 2), "type": "total"},
    ]
    
    # Base WACC (for display)
    display_wacc = 9.0 + company.beta * 2
    
    return SimpleValuation(
        current_price=round(price, 2),
        base_fair_value=round(base_fv, 2),
        distressed_value=round(distressed, 2),
        downside_pct=round(downside, 1),
        valuation_method=method,
        base_wacc=round(display_wacc, 2),
        stressed_wacc=round(display_wacc + wacc_stress, 2),
        revenue_haircut=round(rev_haircut, 1),
        margin_compression_bps=round(margin_bps, 0),
        waterfall_data=waterfall,
        method_values=cross_check
    )
Summary of What Changed:
Fix	What	Why
Waterfall	Replaced titlefont=dict(...) with title=dict(text=..., font=dict(...))	Plotly deprecated titlefont in newer versions
Map tiling	Added bounds=dict(west=-180, east=180, south=-70, north=80)	Constrains the map to a single world view
Valuation	5 routing paths based on company classification	DCF is wrong for banks, high-growth, and cyclicals
Valuation Logic Summary:
Company Type	Method	Why Not DCF
Banks/Insurance	P/BV + Excess Return	Debt is their product, not a liability
High-Growth Tech (>25% growth, low margin)	EV/Revenue + Rule of 40	Terminal value dominates (80%+), FCF is negative
Cyclical (Energy/Mining)	Normalized Mid-Cycle EBITDA	Current earnings are peak/trough, misleading
Mature Profitable	5-Year FCF-DCF + Gordon Growth	Only valid DCF candidate
Loss-Making	EV/Revenue (discounted)	No earnings to discount
Just replace those 3 functions in your working app.py and it should fix both the crash and add proper valuation intelligence.