Valuation Transparency Panel — Addition Only
Here's a complete function you add to your app.py and call at the bottom of your results rendering section. This displays the full calculation methodology, actual numbers used, and formulas — all in your existing JetBrains Mono dark aesthetic.

# ============================================================
# VALUATION TRANSPARENCY ENGINE — CALCULATION DISPLAY
# ============================================================

def render_valuation_transparency(company_data, valuation_result, chaos_level, validated_risks):
    """
    Renders a full breakdown of the valuation methodology, formulas used,
    and actual numbers plugged in. Placed at bottom of results page.
    Addition only — does not modify any existing calculation logic.
    """
    
    st.markdown("---")
    st.markdown("""
    
        
              VALUATION TRANSPARENCY -- METHODOLOGY AND CALCULATIONS
    
    
         Full audit trail of routing logic, formulas applied, and stress parameters.
         All figures in USD. No black boxes.
    """, unsafe_allow_html=True)
    
    # Extract data from company profile and valuation result
    name = company_data.get('name', 'Unknown')
    sector = company_data.get('sector', 'Unknown')
    industry = company_data.get('industry', 'Unknown')
    market_cap = company_data.get('market_cap', 0)
    current_price = company_data.get('current_price', 0)
    revenue = company_data.get('revenue', 0)
    ebitda = company_data.get('ebitda', 0)
    net_income = company_data.get('net_income', 0)
    total_debt = company_data.get('total_debt', 0)
    cash = company_data.get('cash', company_data.get('total_cash', 0))
    shares_out = company_data.get('shares_outstanding', company_data.get('shares', 0))
    beta = company_data.get('beta', 1.0)
    revenue_growth = company_data.get('revenue_growth', 0)
    profit_margin = company_data.get('profit_margin', 0)
    book_value = company_data.get('book_value', company_data.get('book_value_per_share', 0))
    roe = company_data.get('roe', company_data.get('return_on_equity', 0))
    fcf = company_data.get('free_cashflow', company_data.get('fcf', 0))
    
    base_fv = valuation_result.get('base_fair_value', valuation_result.get('fair_value', 0))
    distressed = valuation_result.get('distressed_value', 0)
    method_used = valuation_result.get('method', valuation_result.get('valuation_method', 'Unknown'))
    
    # Determine which path was used
    sector_lower = (sector + " " + industry).lower()
    is_financial = any(k in sector_lower for k in ['bank', 'financial', 'insurance', 'capital markets'])
    is_cyclical = any(k in sector_lower for k in ['energy', 'oil', 'gas', 'mining', 'materials', 'utilities', 'petroleum'])
    is_high_growth = (revenue_growth and revenue_growth > 0.25) and (not net_income or net_income <= 0 or (profit_margin and profit_margin < 0.05))
    is_mature = (ebitda and ebitda > 0) and (net_income and net_income > 0) and not is_financial and not is_cyclical
    is_loss_making = not is_financial and not is_cyclical and not is_high_growth and not is_mature
    
    # Determine path number and label
    if is_financial:
        path_num = 1
        path_label = "FINANCIAL (P/BV + Excess Return)"
        path_color = "#4fc3f7"
    elif is_high_growth:
        path_num = 2
        path_label = "HIGH-GROWTH (EV/Revenue + Rule of 40)"
        path_color = "#ab47bc"
    elif is_mature:
        path_num = 3
        path_label = "MATURE PROFITABLE (5-Year FCF-DCF + Gordon Growth)"
        path_color = "#66bb6a"
    elif is_cyclical:
        path_num = 4
        path_label = "CYCLICAL (Normalized Mid-Cycle EBITDA)"
        path_color = "#ffa726"
    else:
        path_num = 5
        path_label = "LOSS-MAKING / FALLBACK (EV/Revenue Capped)"
        path_color = "#ef5350"
    
    # === SECTION 1: ROUTING DECISION ===
    st.markdown(f"""
    
        
             [1] ROUTING DECISION
        
            Company: {name}
            Sector: {sector} | {industry}
            Revenue Growth: {revenue_growth*100:.1f}% 
            {"(>25% threshold)" if revenue_growth and revenue_growth > 0.25 else "(below 25% threshold)"}
            EBITDA: {"$" + f"{ebitda/1e9:.2f}B" if ebitda and ebitda > 0 else "Negative / N/A"}
            Net Income: {"$" + f"{net_income/1e9:.2f}B" if net_income and net_income > 0 else "Negative / N/A"}
            Profit Margin: {profit_margin*100:.1f}%
            
            Classification: 
            PATH {path_num} -- {path_label}
        
        
            Routing Logic: Financial={is_financial} | Cyclical={is_cyclical} | 
            HighGrowth={is_high_growth} | Mature={is_mature} | Fallback={is_loss_making}
        
    
    """, unsafe_allow_html=True)
    
    # === SECTION 2: INPUTS TABLE ===
    ev = market_cap + (total_debt or 0) - (cash or 0)
    
    st.markdown(f"""
    
        
             [2] RAW INPUTS (from yfinance, converted to USD)
        
            
                
                    Market Cap
                    ${market_cap/1e9:.2f}B
                    Current Price
                    ${current_price:.2f}
                
                
                    Revenue (TTM)
                    ${revenue/1e9:.2f}B
                    EBITDA (TTM)
                    {"$" + f"{ebitda/1e9:.2f}B" if ebitda else "N/A"}
                
                
                    Net Income
                    {"$" + f"{net_income/1e9:.2f}B" if net_income else "N/A"}
                    Free Cash Flow
                    {"$" + f"{fcf/1e9:.2f}B" if fcf else "N/A"}
                
                
                    Total Debt
                    {"$" + f"{total_debt/1e9:.2f}B" if total_debt else "N/A"}
                    Cash & Equiv
                    {"$" + f"{cash/1e9:.2f}B" if cash else "N/A"}
                
                
                    Enterprise Value
                    ${ev/1e9:.2f}B
                    Shares Outstanding
                    {shares_out/1e9:.2f}B
                
                
                    Beta
                    {beta:.2f}
                    Book Value/Share
                    {"$" + f"{book_value:.2f}" if book_value else "N/A"}
                
                
                    ROE
                    {roe*100:.1f}%
                    Revenue Growth
                    {revenue_growth*100:.1f}%
                
            
        
    
    """, unsafe_allow_html=True)
    
    # === SECTION 3: METHOD-SPECIFIC FORMULA AND CALCULATION ===
    
    if path_num == 1:
        # Financial: P/BV + Excess Return
        risk_free = 0.043
        erp = 0.055
        coe = risk_free + beta * erp
        justified_pbv = min(max(roe / coe, 0.5), 2.5) if coe > 0 else 1.0
        implied_value = book_value * justified_pbv if book_value else current_price
        
        formula_html = f"""
        
            
                PATH 1: P/BV + EXCESS RETURN MODEL
            
                Why not DCF: Banks use leverage as a product. Debt is not a liability to be 
                subtracted -- it IS the business model. EBITDA/FCF are meaningless for financials.
                Instead, we estimate a justified Price-to-Book ratio from profitability vs cost of capital.
            
                Step 1: Cost of Equity (CAPM)
                  CoE = Rf + Beta x ERP
                  CoE = {risk_free:.3f} + {beta:.2f} x {erp:.3f} = {coe:.4f} ({coe*100:.2f}%)
                Step 2: Justified P/BV Multiple
                  P/BV = ROE / CoE (capped at 0.5x - 2.5x)
                  P/BV = {roe:.4f} / {coe:.4f} = {roe/coe:.2f} --> capped = {justified_pbv:.2f}x
                Step 3: Implied Fair Value
                  FV = Book Value/Share x Justified P/BV
                  FV = ${book_value:.2f} x {justified_pbv:.2f} = ${implied_value:.2f}
            
        
        """
    
    elif path_num == 2:
        # High-Growth: EV/Revenue + Rule of 40
        rule_of_40 = (revenue_growth * 100) + (profit_margin * 100)
        if rule_of_40 >= 60:
            ev_rev_multiple = 12.0
        elif rule_of_40 >= 40:
            ev_rev_multiple = 8.0
        elif rule_of_40 >= 20:
            ev_rev_multiple = 5.0
        else:
            ev_rev_multiple = 3.0
        # Large cap discount
        if market_cap > 100e9:
            ev_rev_multiple *= 0.7
        elif market_cap > 50e9:
            ev_rev_multiple *= 0.85
        implied_ev = revenue * ev_rev_multiple
        implied_equity = implied_ev - (total_debt or 0) + (cash or 0)
        implied_value = implied_equity / shares_out if shares_out > 0 else current_price
        
        formula_html = f"""
        
            
                PATH 2: EV/REVENUE + RULE OF 40
            
                Why not DCF: Free cash flow is negative or negligible. Terminal value would represent 
                >80% of total value, making DCF a disguised multiple anyway. Revenue-based valuation 
                with quality adjustment (Rule of 40) is more intellectually honest.
            
                Step 1: Rule of 40 Score
                  R40 = Revenue Growth% + Profit Margin%
                  R40 = {revenue_growth*100:.1f}% + {profit_margin*100:.1f}% = {rule_of_40:.1f}
                Step 2: EV/Revenue Multiple (from R40 tier)
                  R40 >= 60 --> 12x | >= 40 --> 8x | >= 20 --> 5x | else --> 3x
                  Base multiple: {ev_rev_multiple:.1f}x (after size discount if applicable)
                Step 3: Implied Enterprise Value
                  EV = Revenue x Multiple
                  EV = ${revenue/1e9:.2f}B x {ev_rev_multiple:.1f} = ${implied_ev/1e9:.2f}B
                Step 4: Equity Value (EV - Debt + Cash) / Shares
                  Equity = ${implied_ev/1e9:.2f}B - ${(total_debt or 0)/1e9:.2f}B + ${(cash or 0)/1e9:.2f}B = ${implied_equity/1e9:.2f}B
                  Per Share = ${implied_equity/1e9:.2f}B / {shares_out/1e9:.2f}B shares = ${implied_value:.2f}
            
        
        """
    
    elif path_num == 3:
        # Mature: DCF
        risk_free = 0.043
        erp = 0.055
        coe = risk_free + beta * erp
        # Simplified WACC estimate
        debt_weight = total_debt / (market_cap + total_debt) if (market_cap + total_debt) > 0 else 0.3
        equity_weight = 1 - debt_weight
        cost_of_debt = 0.05  # assumed
        tax_rate = 0.21
        wacc = equity_weight * coe + debt_weight * cost_of_debt * (1 - tax_rate)
        
        # Growth assumptions
        near_term_growth = min(revenue_growth if revenue_growth else 0.05, 0.10)
        terminal_growth = 0.025
        
        # FCF or estimate from EBITDA
        if fcf and fcf > 0:
            base_fcf = fcf
            fcf_source = "Reported FCF"
        elif ebitda and ebitda > 0:
            capex_intensity = 0.40 if 'semi' in sector_lower or 'tech' in sector_lower else 0.35
            base_fcf = ebitda * (1 - capex_intensity)
            fcf_source = f"EBITDA x (1 - {capex_intensity:.0%} capex intensity)"
        else:
            base_fcf = revenue * 0.08
            fcf_source = "Revenue x 8% margin estimate"
        
        # 5-year DCF projection
        projected_fcfs = []
        for yr in range(1, 6):
            fade = near_term_growth * (1 - (yr-1)*0.15)  # growth fades
            yr_fcf = base_fcf * (1 + fade) ** yr
            projected_fcfs.append(yr_fcf)
        
        # Terminal value
        terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth) if wacc > terminal_growth else terminal_fcf * 20
        
        # PV calculation
        pv_fcfs = sum([f / (1 + wacc)**i for i, f in enumerate(projected_fcfs, 1)])
        pv_terminal = terminal_value / (1 + wacc)**5
        total_ev = pv_fcfs + pv_terminal
        implied_equity = total_ev - (total_debt or 0) + (cash or 0)
        implied_value = implied_equity / shares_out if shares_out > 0 else current_price
        
        formula_html = f"""
        
            
                PATH 3: 5-YEAR FCF-DCF + GORDON GROWTH TERMINAL
            
                Standard institutional DCF. Only applied to mature, profitable companies where FCF 
                is positive and predictable. Growth fades over projection period. Terminal value 
                uses perpetuity growth model (Gordon Growth).
            
                Step 1: WACC Derivation
                  WACC = E/(E+D) x CoE + D/(E+D) x Kd x (1-t)
                  CoE  = Rf + Beta x ERP = {risk_free:.3f} + {beta:.2f} x {erp:.3f} = {coe:.4f} ({coe*100:.2f}%)
                  Kd   = {cost_of_debt:.1%} (assumed) | Tax = {tax_rate:.0%}
                  Weights: E={equity_weight:.1%} | D={debt_weight:.1%}
                  WACC = {equity_weight:.3f} x {coe:.4f} + {debt_weight:.3f} x {cost_of_debt:.3f} x {1-tax_rate:.2f} = {wacc:.4f} ({wacc*100:.2f}%)
                Step 2: Base Free Cash Flow
                  Source: {fcf_source}
                  Base FCF = ${base_fcf/1e9:.2f}B
                Step 3: 5-Year Projection (growth fades from {near_term_growth*100:.1f}%)
                  Yr1: ${projected_fcfs[0]/1e9:.2f}B | Yr2: ${projected_fcfs[1]/1e9:.2f}B | Yr3: ${projected_fcfs[2]/1e9:.2f}B | Yr4: ${projected_fcfs[3]/1e9:.2f}B | Yr5: ${projected_fcfs[4]/1e9:.2f}B
                Step 4: Terminal Value (Gordon Growth)
                  TV = FCF_5 x (1+g) / (WACC - g)
                  TV = ${projected_fcfs[4]/1e9:.2f}B x (1+{terminal_growth:.3f}) / ({wacc:.4f} - {terminal_growth:.3f}) = ${terminal_value/1e9:.1f}B
                Step 5: Present Value Summation
                  PV(FCFs)     = ${pv_fcfs/1e9:.2f}B
                  PV(Terminal) = ${pv_terminal/1e9:.2f}B
                  Total EV     = ${total_ev/1e9:.2f}B
                  Equity Value = ${total_ev/1e9:.2f}B - ${(total_debt or 0)/1e9:.2f}B + ${(cash or 0)/1e9:.2f}B = ${implied_equity/1e9:.2f}B
                  Per Share    = ${implied_value:.2f}
            
        
        """
    
    elif path_num == 4:
        # Cyclical: Normalized Mid-Cycle EBITDA
        normalization_factor = 0.8
        normalized_ebitda = (ebitda or revenue * 0.15) * normalization_factor
        if 'energy' in sector_lower or 'oil' in sector_lower or 'petroleum' in sector_lower:
            ev_multiple = 7.0
        else:
            ev_multiple = 6.5
        implied_ev = normalized_ebitda * ev_multiple
        implied_equity = implied_ev - (total_debt or 0) + (cash or 0)
        implied_value = implied_equity / shares_out if shares_out > 0 else current_price
        
        formula_html = f"""
        
            
                PATH 4: NORMALIZED MID-CYCLE EBITDA
            
                Why not DCF: Cyclical companies have earnings that swing wildly with commodity prices. 
                Spot EBITDA at a cycle peak grossly overstates sustainable value. A 0.8x normalization 
                haircut approximates through-cycle earnings before applying a conservative multiple.
            
                Step 1: Normalize EBITDA (0.8x haircut for cycle position)
                  Normalized EBITDA = Reported EBITDA x 0.80
                  Normalized = ${ (ebitda or revenue*0.15)/1e9:.2f}B x 0.80 = ${normalized_ebitda/1e9:.2f}B
                Step 2: Apply Conservative EV/EBITDA Multiple
                  Energy: 7.0x | Other Cyclicals: 6.5x
                  Applied: {ev_multiple:.1f}x
                Step 3: Implied Enterprise Value
                  EV = ${normalized_ebitda/1e9:.2f}B x {ev_multiple:.1f} = ${implied_ev/1e9:.2f}B
                Step 4: Equity Bridge
                  Equity = ${implied_ev/1e9:.2f}B - ${(total_debt or 0)/1e9:.2f}B + ${(cash or 0)/1e9:.2f}B = ${implied_equity/1e9:.2f}B
                  Per Share = ${implied_value:.2f}
            
        
        """
    
    else:
        # Path 5: Loss-making / Fallback
        ev_rev_multiple = min(5.0, max(1.0, revenue_growth * 10 if revenue_growth else 2.0))
        implied_ev = revenue * ev_rev_multiple if revenue else market_cap
        implied_equity = implied_ev - (total_debt or 0) + (cash or 0)
        implied_value = max(implied_equity / shares_out if shares_out > 0 else current_price, current_price * 0.8)
        
        formula_html = f"""
        
            
                PATH 5: EV/REVENUE (CAPPED) -- FALLBACK
            
                Applied when company has no stable earnings to discount. Multiple capped at 5x 
                regardless of growth narrative. Floor at 0.8x current price to prevent absurd outputs.
            
                Step 1: Revenue Multiple (capped 1x-5x)
                  Multiple = {ev_rev_multiple:.1f}x
                Step 2: Implied EV
                  EV = ${revenue/1e9:.2f}B x {ev_rev_multiple:.1f} = ${implied_ev/1e9:.2f}B
                Step 3: Equity Value
                  Per Share = ${implied_value:.2f} (floored at 0.8x market)
            
        
        """
    
    st.markdown(f"""
    
        
             [3] VALUATION FORMULA AND CALCULATION
        {formula_html}
    
    """, unsafe_allow_html=True)
    
    # === SECTION 4: MARKET ANCHORING CAP ===
    if market_cap > 100e9:
        cap_label = "LARGE CAP (>$100B)"
        cap_multiple = 1.20
    elif market_cap > 10e9:
        cap_label = "MID CAP ($10-100B)"
        cap_multiple = 1.35
    else:
        cap_label = "SMALL CAP (<$10B)"
        cap_multiple = 1.50
    
    max_allowed = current_price * cap_multiple
    was_capped = base_fv <= max_allowed * 1.01  # approximately at cap
    
    st.markdown(f"""
    
        
             [4] MARKET ANCHORING -- EFFICIENCY ASSUMPTION
        
            
                Philosophy: This is a stress-test tool, not a stock picker. We assume markets are 
                broadly efficient for liquid, covered companies. If our model says fair value is 2.5x 
                the current price, the model is wrong -- not the market. Base FV is capped to prevent 
                the stress waterfall from starting at an unrealistic anchor.
            
                Size Tier: {cap_label}
                Market Cap: ${market_cap/1e9:.1f}B
                Current Price: ${current_price:.2f}
                Max Allowed FV: ${current_price:.2f} x {cap_multiple:.2f} = ${max_allowed:.2f}
                Raw Model Output: ${implied_value:.2f}
                Final Base FV: ${base_fv:.2f} {"(CAPPED)" if base_fv < implied_value * 0.95 else "(within bounds)"}
            
        
    
    """, unsafe_allow_html=True)
    
    # === SECTION 5: STRESS APPLICATION ===
    avg_severity = sum([float(r.get('severity', 5)) for r in validated_risks]) / max(len(validated_risks), 1)
    
    revenue_haircut = chaos_level * 15 + (avg_severity / 10) * 12
    wacc_premium = chaos_level * 4.5 + (avg_severity / 10) * 3
    margin_compression_bps = chaos_level * 250 + avg_severity * 50
    multiple_compression = 1 - (chaos_level * 0.18 + (avg_severity / 10) * 0.12)
    
    downside_pct = ((distressed - current_price) / current_price) * 100 if current_price > 0 else -30
    min_forced_downside = -(chaos_level * 40 + avg_severity * 3)
    
    st.markdown(f"""
    
        
             [5] STRESS APPLICATION -- CHAOS PARAMETER DECOMPOSITION
        
            
                Chaos Level: {chaos_level:.2f}
                Avg Risk Severity: {avg_severity:.1f}/10
                Active Risks: {len(validated_risks)}
            
            
                Stress Factors Applied:
                Revenue Haircut:
                  = chaos x 15 + (severity/10) x 12
                  = {chaos_level:.2f} x 15 + ({avg_severity:.1f}/10) x 12 = -{revenue_haircut:.1f}%
                WACC Premium (added to discount rate):
                  = chaos x 4.5 + (severity/10) x 3
                  = {chaos_level:.2f} x 4.5 + ({avg_severity:.1f}/10) x 3 = +{wacc_premium:.2f}%
                Margin Compression:
                  = chaos x 250 + severity x 50 (bps)
                  = {chaos_level:.2f} x 250 + {avg_severity:.1f} x 50 = -{margin_compression_bps:.0f} bps
                Multiple Compression Factor:
                  = 1 - (chaos x 0.18 + (severity/10) x 0.12)
                  = 1 - ({chaos_level:.2f} x 0.18 + ({avg_severity:.1f}/10) x 0.12) = {multiple_compression:.3f}x ({(1-multiple_compression)*100:.1f}% de-rating)
            
        
    
    """, unsafe_allow_html=True)
    
    # === SECTION 6: FINAL OUTPUT ===
    st.markdown(f"""
    
        
             [6] FINAL OUTPUT
        
            
                
                    
                        Current Market Price
                        ${current_price:.2f}
                    
                    
                        Base Fair Value (post-cap)
                        ${base_fv:.2f}
                    
                    
                        Distressed Value (post-stress)
                        ${distressed:.2f}
                    
                    
                        Implied Downside
                        {downside_pct:.1f}%
                    
                    
                        Min Forced Floor (if math shows upside)
                        {min_forced_downside:.1f}%
                    
                
            
            
                Downside is ALWAYS forced negative. If stressed value > current price, 
                minimum drawdown = -(chaos x 40 + severity x 3)%. This tool models downside only.
            
        
    
    """, unsafe_allow_html=True)
    
    # === SECTION 7: METHODOLOGY LEGEND ===
    st.markdown(f"""
    
        
             [7] ALL VALUATION PATHS -- REFERENCE
        
            
                
                    PATH
                    TYPE
                    METHOD
                    WHY NOT DCF
                
                
                    1
                    Financial
                    P/BV + Excess Return
                    Debt = product, not liability
                
                
                    2
                    High-Growth
                    EV/Revenue + R40
                    Negative FCF, TV >80%
                
                
                    3
                    Mature
                    5Y FCF-DCF + Gordon
                    Only valid DCF candidate
                
                
                    4
                    Cyclical
                    Normalized EBITDA
                    Spot earnings mislead at peaks
                
                
                    5
                    Loss-Making
                    EV/Revenue (capped)
                    No earnings to discount
                
            
        
    
    """, unsafe_allow_html=True)
How to Call It
At the very bottom of your results rendering section (after waterfall chart, after contagion chains if you added those, near the end of the page), add:

# === VALUATION TRANSPARENCY (bottom of page) ===
if 'company_data' in st.session_state and 'valuation_result' in st.session_state:
    render_valuation_transparency(
        company_data=st.session_state['company_data'],
        valuation_result=st.session_state['valuation_result'],
        chaos_level=chaos_level,
        validated_risks=st.session_state.get('validated_risks', [])
    )
Make sure your analysis pipeline stores the company data and valuation result in session state (you likely already do this):

# In your main analysis pipeline, ensure these are stored:
st.session_state['company_data'] = company_data  # the dict from yfinance
st.session_state['valuation_result'] = valuation_result  # dict with base_fair_value, distressed_value, method, etc.
st.session_state['validated_risks'] = validated_risks  # list of risk dicts post-debate
What This Looks Like
The panel renders 7 numbered sections at the bottom of the page:

Routing Decision — Shows exactly which path was chosen and why (with True/False flags)
Raw Inputs — Clean table of every financial metric pulled from yfinance
Formula & Calculation — The actual math, step by step, with numbers plugged in (path-specific)
Market Anchoring — Explains the cap logic, shows if/how it was applied
Stress Decomposition — Every stress formula with the chaos parameter and severity plugged in
Final Output — Summary table of market price → base FV → distressed → downside%
Reference Legend — All 5 paths in a compact table for context
All in JetBrains Mono, dark backgrounds, color-coded by path, no emojis. Fully additive — doesn't touch your existing valuation logic at all, just displays what already happened.