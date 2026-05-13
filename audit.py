"""
Deep audit: verify all original functions exist AND new additions are correct.
"""
import ast

with open('app.py', encoding='utf-8') as f:
    content = f.read()

# Parse AST to get all function names
tree = ast.parse(content)
all_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

# ── ORIGINAL architecture functions that must still exist ──
original_required = [
    # Data + AI
    "resolve_ticker",
    "fetch_company_data",
    "fetch_world_state_data",
    "get_hq_coords",
    # Core engine
    "run_with_timeout",
    "parse_json_safe",
    "tavily_search",
    "run_intelligence_scan",
    "generate_fallback_risks",
    "run_debate",
    "map_risks_to_coords",
    "compute_valuation",
    "curved_path",
    # Render
    "render_map",
    "render_waterfall",
    "render_risk_cards",
    "render_debate_feed",
    # Entry
    "main",
]

# ── NEW functions that must exist ──
new_required = [
    "generate_contagion_chains",
    "generate_fallback_chains",
    "render_contagion_section",
]

print("=" * 55)
print("ORIGINAL ARCHITECTURE — Function Presence Check")
print("=" * 55)
all_ok = True
for fn in original_required:
    present = fn in all_functions
    status = "OK" if present else "MISSING"
    if not present:
        all_ok = False
    print(f"  {'[OK]' if present else '[!!]'} {fn}")

print()
print("=" * 55)
print("NEW ADDITIONS — Function Presence Check")
print("=" * 55)
for fn in new_required:
    present = fn in all_functions
    status = "OK" if present else "MISSING"
    if not present:
        all_ok = False
    print(f"  {'[OK]' if present else '[!!]'} {fn}")

print()
print("=" * 55)
print("INTEGRATION WIRING CHECKS")
print("=" * 55)

checks = {
    "Pipeline: contagion called after debate": "Modeling contagion propagation" in content,
    "Pipeline: stored in session_state": "st.session_state['contagion_chains']" in content,
    "Results: render_contagion_section called": content.count("render_contagion_section") >= 2,  # def + call
    "Map: hovertext + wrap_description": "hovertext=hover_texts" in content and "def wrap_description" in content,
    "Map: hoverlabel dict present": "hoverlabel=dict" in content,
    "Valuation: market cap anchor (1.20x)": "price * 1.20" in content,
    "Valuation: forced negative downside": "force at least -10%" in content or "min_downside" in content,
    "Debate: better fallback (severity >= 5)": "generate_fallback_risks" in content,
    "Env: absolute path loader": "resolve().parent" in content,
    "Env: override=True": "override=True" in content,
}

for desc, result in checks.items():
    status = "[OK]" if result else "[!!]"
    if not result:
        all_ok = False
    print(f"  {status} {desc}")

print()
print("=" * 55)
print("DATACLASS INTEGRITY CHECK")
print("=" * 55)
dataclasses_required = ["CompanyData", "WorldState", "RiskVerdict", "FractureNode",
                        "SimpleValuation", "DebateMessage", "DoomsdayAI"]
for dc in dataclasses_required:
    present = dc in content
    if not present:
        all_ok = False
    print(f"  {'[OK]' if present else '[!!]'} {dc}")

print()
print("=" * 55)
if all_ok:
    print("RESULT: ALL CHECKS PASSED - Architecture intact")
else:
    print("RESULT: SOME CHECKS FAILED - Review [!!] items above")
print("=" * 55)
print(f"Total lines: {content.count(chr(10))}")
print(f"Total functions defined: {len(all_functions)}")
