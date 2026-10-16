#!/usr/bin/env python3
"""Run the same ingress probes against preserved v4.5 code and v4.6 code."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

baseline = load_module(HERE / "shared_ingress_quota_v4_5_baseline_fixture.py", "baseline_ingress_v45")
current = load_module(HERE / "shared_ingress_quota.py", "current_ingress_v46")

def rate_probe(module):
    with tempfile.TemporaryDirectory() as td:
        store = module.SharedIngressQuotaStore(
            Path(td) / "q.sqlite", max_active_connections=1,
            max_connections_per_ip=1, max_new_connections_per_minute=2,
            auto_renew=False,
        )
        first, r1 = store.reserve("192.0.2.1", auto_renew=False)
        _, r2 = store.reserve("192.0.2.2", auto_renew=False)
        _, r3 = store.reserve("192.0.2.3", auto_renew=False)
        first.close()
        final, r4 = store.reserve("192.0.2.4", auto_renew=False)
        if final:
            final.close()
        return {"first": r1 or "accepted", "second_while_full": r2,
                "third_while_full": r3, "after_slot_release": r4 or "accepted"}

def alias_probe(module):
    with tempfile.TemporaryDirectory() as td:
        store = module.SharedIngressQuotaStore(
            Path(td) / "q.sqlite", max_active_connections=4,
            max_connections_per_ip=1, max_new_connections_per_minute=20,
            auto_renew=False,
        )
        first, r1 = store.reserve("192.0.2.44", auto_renew=False)
        second, r2 = store.reserve("::ffff:192.0.2.44", auto_renew=False)
        if first:
            first.close()
        if second:
            second.close()
        return {"ipv4": r1 or "accepted", "mapped_ipv6": r2 or "accepted",
                "canonical_keys_equal": store._peer("192.0.2.44") == store._peer("::ffff:192.0.2.44")}

results = {
    "scope": "local same-host SQLite reference comparison; not a load test",
    "rate_budget": {"v4.5": rate_probe(baseline), "v4.6": rate_probe(current)},
    "mapped_ipv4_identity": {"v4.5": alias_probe(baseline), "v4.6": alias_probe(current)},
}
expected = (
    results["rate_budget"]["v4.5"]["after_slot_release"] == "accepted"
    and results["rate_budget"]["v4.6"]["after_slot_release"] == "connection-rate-limit"
    and results["mapped_ipv4_identity"]["v4.5"]["mapped_ipv6"] == "accepted"
    and results["mapped_ipv4_identity"]["v4.6"]["mapped_ipv6"] == "per-ip-connection-limit"
    and results["mapped_ipv4_identity"]["v4.6"]["canonical_keys_equal"] is True
)
results["expected_delta_observed"] = bool(expected)
print(json.dumps(results, indent=2))
if not expected:
    raise SystemExit(1)
