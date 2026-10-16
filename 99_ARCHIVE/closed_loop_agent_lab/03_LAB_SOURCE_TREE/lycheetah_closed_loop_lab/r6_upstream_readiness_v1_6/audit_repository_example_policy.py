#!/usr/bin/env python3
"""Verify the real committed customer-support policy against R6 candidate contracts."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parent
POLICY_FILE = ROOT / "fixtures/customer_support_policy.json"
EXPECTED_GIT_BLOB = "419d4894db9480ce6d850c2115f767fe09a237ad"
SOURCE_EQ_MODEL = ROOT.parent / "r5_policy_contract_v1_5/policy_contract_parity.py"

spec = importlib.util.spec_from_file_location("policy_contract_parity", SOURCE_EQ_MODEL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load source-equivalent baseline parser model")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)

data_bytes = POLICY_FILE.read_bytes()
actual_blob = hashlib.sha1(f"blob {len(data_bytes)}\0".encode("ascii") + data_bytes).hexdigest()
data = json.loads(data_bytes)
current_schema = json.loads((ROOT / "policy.schema.current-snapshot.json").read_text(encoding="utf-8"))
candidate_schema = json.loads((ROOT / "policy.schema.strict-candidate.json").read_text(encoding="utf-8"))
current_schema_ok = not list(jsonschema.Draft202012Validator(current_schema).iter_errors(data))
candidate_schema_ok = not list(jsonschema.Draft202012Validator(candidate_schema).iter_errors(data))
try:
    model.parse_policy(data)
    current_parser_ok, current_parser_error = True, None
except Exception as exc:
    current_parser_ok, current_parser_error = False, f"{type(exc).__name__}: {exc}"
strict_parser_ok, strict_parser_note = model.strict_type_gate(data)
result = {
    "source": "Lycheetah/Lycheetah-Framework/examples/assurance/customer_support_policy.json",
    "inspected_base_commit": "8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65",
    "expected_git_blob_sha": EXPECTED_GIT_BLOB,
    "actual_git_blob_sha": actual_blob,
    "fixture_matches_source_blob": actual_blob == EXPECTED_GIT_BLOB,
    "current_schema_accepts": current_schema_ok,
    "source_equivalent_current_parser_accepts": current_parser_ok,
    "candidate_schema_accepts": candidate_schema_ok,
    "source_equivalent_strict_type_gate_accepts": strict_parser_ok,
    "current_parser_error": current_parser_error,
    "strict_parser_note": strict_parser_note,
    "compatibility": "PASS" if actual_blob == EXPECTED_GIT_BLOB and current_schema_ok and current_parser_ok and candidate_schema_ok and strict_parser_ok else "REVIEW",
    "limitations": [
        "The parser being invoked is the audited source-equivalent model, not the full upstream package.",
        "This is one committed example policy; it is not a scan of user-held or production-stored records.",
    ],
}
(ROOT / "repository_example_policy_results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if result["compatibility"] != "PASS":
    raise SystemExit(1)
