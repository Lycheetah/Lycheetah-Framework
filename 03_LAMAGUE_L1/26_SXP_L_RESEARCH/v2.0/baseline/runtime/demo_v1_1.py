"""Deterministic non-executing examples for a reviewer."""
from pathlib import Path
import json
from discourse11 import parse_expression,render_expression,interpret
for name in ['quoted_permission_is_not_permission.sxh','contrast_love_and_limit.sxh','unverified_causal_claim.sxh']:
    s=(Path(__file__).parent/'examples'/name).read_text(encoding='utf-8').strip()
    d=parse_expression(s)
    print(json.dumps({'example':name,'kind':d['node']['kind'],
        'reversible':render_expression(d)==s,'interpretation':interpret(d)},indent=2))
