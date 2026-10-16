"""A real committed upstream example remains valid under both contracts."""
import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/customer_support_policy.json"
EXPECTED_GIT_BLOB = "419d4894db9480ce6d850c2115f767fe09a237ad"
MODEL_PATH = ROOT.parent / "r5_policy_contract_v1_5/policy_contract_parity.py"


def _model():
    spec = importlib.util.spec_from_file_location("policy_contract_parity_compat_test", MODEL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_customer_support_policy_is_compatible_with_candidate():
    raw = FIXTURE.read_bytes()
    assert hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest() == EXPECTED_GIT_BLOB
    data = json.loads(raw)
    current_schema = json.loads((ROOT / "policy.schema.current-snapshot.json").read_text(encoding="utf-8"))
    candidate_schema = json.loads((ROOT / "policy.schema.strict-candidate.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(current_schema).validate(data)
    jsonschema.Draft202012Validator(candidate_schema).validate(data)
    model = _model()
    assert model.parse_policy(data) is True
    strict_ok, note = model.strict_type_gate(data)
    assert strict_ok, note
