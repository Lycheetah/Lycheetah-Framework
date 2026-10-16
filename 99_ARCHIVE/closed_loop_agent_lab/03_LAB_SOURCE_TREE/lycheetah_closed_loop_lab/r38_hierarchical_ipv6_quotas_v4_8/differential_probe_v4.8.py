#!/usr/bin/env python3
"""Paired v4.7 exact-/64 baseline vs v4.8 hierarchical /56 quota probe."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path

from shared_ingress_quota import SharedIngressQuotaStore

ROOT = Path(__file__).resolve().parent
BASELINE_PATH = ROOT / "shared_ingress_quota_v4_7_baseline_fixture.py"
spec = importlib.util.spec_from_file_location("shared_ingress_quota_v47_baseline", BASELINE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load preserved v4.7 baseline")
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)

IPS = [
    "2001:db8:1234:5601::1",
    "2001:db8:1234:56fe::2",
    "2001:db8:1234:56ab::3",
]
OTHER_PREFIX = "2001:db8:1234:5701::1"


def run_baseline(path: Path):
    store = baseline.SharedIngressQuotaStore(
        path, max_active_connections=8, max_connections_per_ip=1,
        max_new_connections_per_minute=100, ipv6_prefix_length=64,
        active_lease_ttl_seconds=20, boot_id="v4.8-differential", auto_renew=False,
    )
    outcomes=[]; leases=[]
    for ip in IPS:
        lease, reason = store.reserve(ip, auto_renew=False)
        outcomes.append({"ip": ip, "admitted": lease is not None, "reason": reason})
        if lease is not None: leases.append(lease)
    for lease in leases: lease.close()
    return outcomes


def run_hierarchical(path: Path):
    store = SharedIngressQuotaStore(
        path, max_active_connections=8, max_connections_per_ip=1,
        max_new_connections_per_minute=100, ipv6_prefix_length=64,
        ipv6_aggregate_prefix_length=56, max_connections_per_ipv6_aggregate=2,
        active_lease_ttl_seconds=20, boot_id="v4.8-differential", auto_renew=False,
    )
    outcomes=[]; leases=[]
    for ip in IPS:
        lease, reason = store.reserve(ip, auto_renew=False)
        outcomes.append({"ip": ip, "admitted": lease is not None, "reason": reason})
        if lease is not None: leases.append(lease)
    other, other_reason = store.reserve(OTHER_PREFIX, auto_renew=False)
    other_result={"ip": OTHER_PREFIX, "admitted": other is not None, "reason": other_reason}
    if other is not None: leases.append(other)
    for lease in leases: lease.close()
    return {"same_parent_prefix": outcomes, "independent_parent_prefix": other_result}


def main():
    with tempfile.TemporaryDirectory(prefix="lyc-v4-8-diff-") as td:
        root=Path(td)
        before=run_baseline(root / "before.sqlite3")
        after=run_hierarchical(root / "after.sqlite3")
    base_admitted=sum(row["admitted"] for row in before)
    hierarchy_admitted=sum(row["admitted"] for row in after["same_parent_prefix"])
    assert base_admitted == 3, before
    assert hierarchy_admitted == 2, after
    assert after["same_parent_prefix"][2]["reason"] == "ipv6-aggregate-connection-limit", after
    assert after["independent_parent_prefix"]["admitted"] is True, after
    result={
        "comparison":"preserved-v4.7-/64-baseline-vs-v4.8-configured-/56-aggregate",
        "configuration":{"leaf_prefix_length":64,"aggregate_prefix_length":56,"aggregate_active_limit":2},
        "same_parent_prefix_addresses":IPS,
        "v4_7_exact_leaf_bucket_baseline":{"admitted_count":base_admitted,"outcomes":before},
        "v4_8_hierarchical":{"admitted_count":hierarchy_admitted,**after},
        "expected_delta_observed":True,
        "scope":"local deterministic store probe; not internet traffic/load test",
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == "__main__": main()
