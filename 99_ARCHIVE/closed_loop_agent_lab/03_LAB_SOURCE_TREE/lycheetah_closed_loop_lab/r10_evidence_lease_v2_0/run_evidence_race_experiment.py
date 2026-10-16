"""Concurrent SQLite race experiment for the evidence lease protocol."""
from __future__ import annotations
import json, tempfile, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from durable_action_broker import Evidence, Requirement, sha256_json
from evidence_lease import EvidenceLocked, LeaseUnavailable, SQLiteEvidenceLeaseAuthority

KEY = b"research-evidence-lease-key-32-bytes-minimum-000000"
class Clock:
    def __call__(self): return 1000.0

def main(rounds: int = 200):
    counts = {"update_linearized_first": 0, "lease_linearized_first": 0}
    violations = []
    with tempfile.TemporaryDirectory() as td:
        auth = SQLiteEvidenceLeaseAuthority(Path(td)/"evidence.sqlite", KEY, clock=Clock(), lease_seconds=60)
        for i in range(rounds):
            key = f"release.{i}"
            req = Requirement(key, "EXACT", "PASS", f"subject-{i}")
            good = Evidence(key, f"v{i}", f"subject-{i}", f"digest-{i}", "PASS")
            bad = Evidence(key, f"v{i+1}", f"subject-{i}", f"digest-{i+1}", "FAIL")
            auth.put(good)
            items = [{"requirement": req.to_dict(), "admitted": good.to_dict()}]
            barrier = threading.Barrier(2)
            outcome = {}
            def update():
                barrier.wait()
                try:
                    auth.put(bad)
                    outcome["update"] = "applied"
                except EvidenceLocked:
                    outcome["update"] = "blocked"
            def lease():
                barrier.wait()
                try:
                    outcome["token"] = auth.acquire_lease(f"op-{i}", sha256_json({"op": i}), (req,), items)
                    outcome["lease"] = "issued"
                except LeaseUnavailable:
                    outcome["lease"] = "denied"
            with ThreadPoolExecutor(max_workers=2) as pool:
                fu = pool.submit(update); fl = pool.submit(lease)
                fu.result(); fl.result()
            observed = auth.get_evidence(key)
            if outcome["update"] == "applied" and outcome["lease"] == "denied" and observed == bad:
                counts["update_linearized_first"] += 1
            elif outcome["update"] == "blocked" and outcome["lease"] == "issued" and observed == good:
                counts["lease_linearized_first"] += 1
                auth.release(outcome["token"])
            else:
                violations.append({"round": i, "outcome": {k:v for k,v in outcome.items() if k != "token"},
                                   "evidence": observed.to_dict() if observed else None})
    report = {
        "experiment": "SQLite evidence-write vs atomic lease-acquisition race",
        "rounds": rounds,
        "counts": counts,
        "invariant": "Either evidence mutation commits before lease and acquisition is denied, or lease commits before mutation and mutation is blocked.",
        "violations": violations,
        "result": "PASS" if not violations and sum(counts.values()) == rounds else "FAIL",
        "scope": "Single-host, local SQLite reference implementation; not multi-host/provider integration evidence."
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "PASS" else 1
if __name__ == "__main__":
    raise SystemExit(main())
