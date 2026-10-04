#!/usr/bin/env python3
import json, sys
from pathlib import Path as _SupportPath
import sys as _support_sys
_support_sys.path.insert(0, str(_SupportPath(__file__).resolve().parents[1]))
from research_support import Action  # noqa: E402
from atomic_finality import AtomicFinalityGate

db, account, principal, scope, idx = sys.argv[1:6]
i = int(idx)
gate = AtomicFinalityGate(db)
action = Action(
    principal=principal,
    tool="job",
    operation="run",
    object_id=f"job-{i}",
    destination="local-worker",
    arguments={"job": i},
    effect_id=f"process-effect-{i}",
)
a = gate.admit(principal, scope, account, action, 1)
if a.state == "RESERVED":
    c = gate.commit(action.effect_id, action, {"job": i})
    print(json.dumps({"admit": a.state, "commit": c.state}, sort_keys=True))
else:
    print(json.dumps({"admit": a.state, "commit": None}, sort_keys=True))
