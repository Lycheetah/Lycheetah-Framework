from __future__ import annotations

import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lamague_core import run_source
from lamague_core.contracts import OPERATOR_CONTRACTS, law_result

ATOMS = ["Ao", "Φ", "Ψ"]
checks = []

for op in OPERATOR_CONTRACTS:
    comm_status = law_result(op, "commutative")["status"]
    assoc_status = law_result(op, "associative")["status"]
    idem_status = law_result(op, "idempotent")["status"]

    comm_values = []
    for a, b in itertools.product(ATOMS, repeat=2):
        _, _, result = run_source(
            f"check equivalent({a} {op} {b}, {b} {op} {a});"
        )
        comm_values.append(result["checks"][0]["equivalent"])

    assoc_values = []
    for a, b, c in itertools.product(ATOMS, repeat=3):
        _, _, result = run_source(
            f"check equivalent(({a} {op} {b}) {op} {c}, "
            f"{a} {op} ({b} {op} {c}));"
        )
        assoc_values.append(result["checks"][0]["equivalent"])

    idem_values = []
    for a in ATOMS:
        _, _, result = run_source(
            f"check equivalent({a} {op} {a}, {a});"
        )
        idem_values.append(result["checks"][0]["equivalent"])

    comm_ok = (
        all(comm_values) if comm_status == "PROVEN"
        else not all(comm_values)
    )
    assoc_ok = (
        all(assoc_values) if assoc_status == "PROVEN"
        else not all(assoc_values)
    )
    idem_ok = (
        all(idem_values) if idem_status == "PROVEN"
        else not all(idem_values)
    )

    checks.append({
        "operator": op,
        "commutative_status": comm_status,
        "commutative_verified": comm_ok,
        "associative_status": assoc_status,
        "associative_verified": assoc_ok,
        "idempotent_status": idem_status,
        "idempotent_verified": idem_ok,
    })

payload = {
    "version": "0.3.0",
    "atom_basis": ATOMS,
    "operators": checks,
    "passed": all(
        row["commutative_verified"]
        and row["associative_verified"]
        and row["idempotent_verified"]
        for row in checks
    ),
    "boundary": (
        "Finite structural verification over the listed atom basis. "
        "It supports implementation conformance, not universal domain laws."
    ),
}
(ROOT / "reports" / "DECLARED_LAW_VERIFICATION.json").write_text(
    json.dumps(payload, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps(payload, indent=2, ensure_ascii=False))
raise SystemExit(0 if payload["passed"] else 1)
