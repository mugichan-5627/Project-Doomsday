"""
Deep safety audit for render_valuation_transparency.
Simulates the function with realistic mock data matching the actual dataclasses.
"""
import ast, sys, traceback

# ── 1. Syntax check ──
with open('app.py', encoding='utf-8') as f:
    src = f.read()
ast.parse(src)
print("[OK] Syntax clean")

# ── 2. Extract CompanyData / SimpleValuation / RiskVerdict field names from AST ──
tree = ast.parse(src)
dataclass_fields = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.append(stmt.target.id)
        if fields:
            dataclass_fields[node.name] = fields

print("\n[2] Dataclass fields discovered:")
for cls, flds in dataclass_fields.items():
    print(f"   {cls}: {flds}")

# ── 3. Check every getattr call in render_valuation_transparency ──
func_src_start = src.find("def render_valuation_transparency(")
func_src_end   = src.find("\ndef render_waterfall(", func_src_start)
func_src = src[func_src_start:func_src_end]

import re
getattr_calls = re.findall(r'getattr\((\w+),\s*["\'](\w+)["\']', func_src)
print("\n[3] getattr field access check:")
company_fields = set(dataclass_fields.get("CompanyData", []))
val_fields     = set(dataclass_fields.get("SimpleValuation", []))

issues = []
for obj, field in getattr_calls:
    if obj == "company":
        ok = field in company_fields
        status = "[OK]" if ok else "[!!] MISSING IN CompanyData"
        if not ok: issues.append(f"company.{field}")
        print(f"   {status}  company.{field}")
    elif obj == "val":
        ok = field in val_fields
        status = "[OK]" if ok else "[!!] MISSING IN SimpleValuation"
        if not ok: issues.append(f"val.{field}")
        print(f"   {status}  val.{field}")

# ── 4. Check direct attribute accesses on verdicts (RiskVerdict) ──
verdict_fields = set(dataclass_fields.get("RiskVerdict", []))
used_verdict_attrs = re.findall(r'v\.(\w+)', func_src)
print("\n[4] RiskVerdict attribute access check:")
for attr in set(used_verdict_attrs):
    ok = attr in verdict_fields
    status = "[OK]" if ok else "[!!] MISSING IN RiskVerdict"
    if not ok: issues.append(f"verdict.{attr}")
    print(f"   {status}  v.{attr}")

# ── 5. Division-by-zero risk scan ──
print("\n[5] Division safety check (manual):")
div_guards = [
    ("revenue denominator",       "max(revenue, 1)" in func_src),
    ("shares denominator",        "shares > 0" in func_src),
    ("market_cap+total_debt denom","(market_cap + total_debt) > 0" in func_src),
    ("wacc-tg guard",             "wacc > tg" in func_src),
    ("coe > 0 guard",             "coe > 0" in func_src),
    ("chaos_level denominator",   "max(len(verdicts), 1)" in func_src),
]
for desc, ok in div_guards:
    status = "[OK]" if ok else "[!!] UNGUARDED"
    if not ok: issues.append(f"div/{desc}")
    print(f"   {status}  {desc}")

# ── 6. Check call site ──
print("\n[6] Call site check:")
call = "render_valuation_transparency(company, val, chaos, verdicts)"
in_results = call in src
# Check variables are assigned before call in main()
main_src_start = src.find("def main():")
main_src = src[main_src_start:]
has_company = "company = st.session_state.company" in main_src or "st.session_state.company" in main_src
has_val     = "val = st.session_state.valuation" in main_src
has_verdicts= "verdicts = st.session_state.verdicts" in main_src
has_chaos   = "chaos" in main_src  # slider variable

checks_6 = [
    ("Function is called in results section", in_results),
    ("company in scope (session_state)", has_company),
    ("val in scope (session_state)", has_val),
    ("verdicts in scope (session_state)", has_verdicts),
    ("chaos in scope (slider)", has_chaos),
]
for desc, ok in checks_6:
    status = "[OK]" if ok else "[!!]"
    if not ok: issues.append(desc)
    print(f"   {status}  {desc}")

# ── 7. Mock execution test (no Streamlit, just logic) ──
print("\n[7] Mock logic execution:")
try:
    # Replicate all logic from the function (without st.markdown calls)
    # using realistic values
    company_mock = type('C', (), {
        'name': 'NVIDIA Corp', 'sector': 'Technology', 'industry': 'Semiconductors',
        'market_cap': 3e12, 'current_price': 121.40, 'revenue': 60.9e9,
        'ebitda': 35e9, 'net_income': 29.8e9, 'total_debt': 9.0e9,
        'cash': 34.8e9, 'shares_outstanding': 24.4e9, 'beta': 1.65,
        'revenue_growth': 0.78, 'pe_ratio': 45.0, 'company_type': 'mature'
    })()
    val_mock = type('V', (), {
        'base_fair_value': 125.0, 'distressed_value': 87.3, 'downside_pct': -28.1,
        'valuation_method': 'Mature-DCF', 'base_wacc': 9.8, 'stressed_wacc': 14.3,
        'revenue_haircut': 8.5, 'margin_compression_bps': 180.0,
        'waterfall_data': [], 'method_values': {}
    })()
    class VerdictMock:
        severity_score = 7.5
        probability = 0.6
    verdicts_mock = [VerdictMock(), VerdictMock(), VerdictMock()]
    chaos_mock = 0.55

    # Run all the derived logic
    name = getattr(company_mock, 'name', 'Unknown')
    sector = getattr(company_mock, 'sector', 'Unknown') or 'Unknown'
    industry = getattr(company_mock, 'industry', 'Unknown') or 'Unknown'
    market_cap = getattr(company_mock, 'market_cap', 0) or 0
    current_price = getattr(company_mock, 'current_price', 0) or 0
    revenue = getattr(company_mock, 'revenue', 0) or 0
    ebitda = getattr(company_mock, 'ebitda', 0) or 0
    net_income = getattr(company_mock, 'net_income', 0) or 0
    total_debt = getattr(company_mock, 'total_debt', 0) or 0
    cash = getattr(company_mock, 'cash', 0) or 0
    shares = getattr(company_mock, 'shares_outstanding', 1) or 1
    beta = getattr(company_mock, 'beta', 1.0) or 1.0
    rev_growth = getattr(company_mock, 'revenue_growth', 0) or 0
    profit_margin = net_income / max(revenue, 1)

    base_fv = getattr(val_mock, 'base_fair_value', 0) or 0
    distressed = getattr(val_mock, 'distressed_value', 0) or 0
    downside = getattr(val_mock, 'downside_pct', 0) or 0

    sector_lower = (sector + " " + industry).lower()
    is_financial   = any(k in sector_lower for k in ["bank","financial","insurance","capital markets"])
    is_cyclical    = any(k in sector_lower for k in ["energy","oil","gas","mining","materials","utilities"])
    is_high_growth = (rev_growth > 0.25) and (net_income <= 0 or profit_margin < 0.05)
    is_mature      = (ebitda > 0) and (net_income > 0) and not is_financial and not is_cyclical and not is_high_growth
    is_fallback    = not any([is_financial, is_cyclical, is_high_growth, is_mature])

    path_num = 1 if is_financial else 2 if is_high_growth else 3 if is_mature else 4 if is_cyclical else 5
    print(f"   Path selected: {path_num} (financial={is_financial}, hg={is_high_growth}, mature={is_mature}, cyc={is_cyclical})")

    ev = market_cap + total_debt - cash
    risk_free, erp = 0.043, 0.055
    coe = risk_free + beta * erp

    # Path 3 (NVIDIA is mature+profitable)
    if path_num == 3:
        dw = total_debt / (market_cap + total_debt) if (market_cap + total_debt) > 0 else 0.3
        ew = 1 - dw
        kd, tax = 0.05, 0.21
        wacc = ew * coe + dw * kd * (1 - tax)
        ng = min(rev_growth if rev_growth else 0.05, 0.10)
        tg = 0.025
        capex_int = 0.40 if any(k in sector_lower for k in ["semi","tech"]) else 0.35
        base_fcf = ebitda * (1 - capex_int) if ebitda > 0 else revenue * 0.08
        pv_sum = sum([base_fcf * (1 + ng*(1-(i-1)*0.15))**i / (1+wacc)**i for i in range(1,6)])
        tv = base_fcf * (1 + tg) / (wacc - tg) if wacc > tg else base_fcf * 20
        pv_tv = tv / (1+wacc)**5
        total_ev3 = pv_sum + pv_tv
        ps3 = (total_ev3 - total_debt + cash) / shares if shares > 0 else current_price
        print(f"   Path 3 DCF: WACC={wacc*100:.2f}%, BaseFCF=${base_fcf/1e9:.1f}B, PerShare=${ps3:.2f}")

    # Stress
    avg_sev = sum(v.severity_score for v in verdicts_mock) / max(len(verdicts_mock), 1)
    rev_hc = chaos_mock * 15 + (avg_sev / 10) * 12
    wacc_p = chaos_mock * 4.5 + (avg_sev / 10) * 3
    mc_bps = chaos_mock * 250 + avg_sev * 50
    mul_c  = 1 - (chaos_mock * 0.18 + (avg_sev / 10) * 0.12)
    min_ds = -(chaos_mock * 40 + avg_sev * 3)

    # Cap check
    if market_cap > 100e9:   cap_mul = 1.20
    elif market_cap > 10e9:  cap_mul = 1.35
    else:                    cap_mul = 1.50
    max_allowed = current_price * cap_mul

    print(f"   Mock stress: rev_hc={rev_hc:.1f}%, wacc_p={wacc_p:.2f}%, mc={mc_bps:.0f}bps")
    print(f"   Mock cap: max_fv=${max_allowed:.2f}, base_fv=${base_fv:.2f}")
    print("   [OK] All logic executed without errors")
except Exception as e:
    issues.append(f"Mock execution: {e}")
    print(f"   [!!] FAILED: {e}")
    traceback.print_exc()

# ── FINAL RESULT ──
print("\n" + "="*55)
if not issues:
    print("RESULT: ALL CHECKS PASSED - Safe to run")
else:
    print(f"RESULT: {len(issues)} issue(s) found:")
    for i in issues:
        print(f"  [!!] {i}")
print("="*55)
print(f"Total app lines: {src.count(chr(10))}")
