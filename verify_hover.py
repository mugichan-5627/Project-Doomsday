import ast
with open('app.py', encoding='utf-8') as f: src = f.read()
ast.parse(src)
src_unix = src.replace('\r','')
checks = [
    ('wrap_description defined', 'def wrap_description(desc, width=55):' in src),
    ('hover_texts list built', 'hover_texts = []' in src),
    ('hovertext=hover_texts', 'hovertext=hover_texts,' in src),
    ('hoverinfo=text used', 'hoverinfo="text",' in src),
    ('bold label line', '<b>{n.label}</b><br>' in src),
    ('tight metric lines', 'Severity: {n.severity:.1f}/10<br>' in src),
    ('ellipsis truncation', '+ "..."' in src),
    ('max 3 lines guard', 'len(lines) >= 3' in src),
    ('customdata REMOVED', 'customdata=[[n.severity' not in src),
    ('hovertemplate REMOVED', '<extra></extra>' not in src),
    ('hoverlabel still present', 'JetBrains Mono, monospace' in src),
    ('Syntax clean', True),
]
all_ok = True
for desc, ok in checks:
    s = '[OK]' if ok else '[!!]'
    if not ok: all_ok = False
    print(f'  {s}  {desc}')
print(f'\nLines: {src.count(chr(10))}')
print('ALL PASSED' if all_ok else 'FAILURES DETECTED')
