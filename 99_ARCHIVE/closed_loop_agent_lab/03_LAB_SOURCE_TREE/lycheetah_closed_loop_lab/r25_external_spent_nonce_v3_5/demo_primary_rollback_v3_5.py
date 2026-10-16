"""Fast, loopback-only demonstration: remote spent nonce survives primary-ledger restore."""
from __future__ import annotations
import json
from test_remote_monotonic_verifier import RemoteMonotonicVerifierTests, INTEGRITY_KEY
from durable_freshness_verifier import DurableFreshnessVerifier
from remote_monotonic_verifier import RemoteMonotonicFreshnessVerifier
from spent_nonce_registry import RegistryRejected


def main():
    harness = RemoteMonotonicVerifierTests(methodName="test_primary_ledger_snapshot_rollback_is_rejected_by_remote_spent_nonce")
    harness.setUp()
    try:
        challenge, reports = harness.issue_reports()
        snapshot = harness.snapshot(harness.local_path, "demo-primary-before-consume.sqlite")
        harness.wrapper.verify_and_consume([harness.certificate], reports, challenge)
        harness.restore_db(harness.local_path, snapshot)
        restored_local = DurableFreshnessVerifier(harness.local_path, harness.anchor_keys,
            harness.witness_public, integrity_key=INTEGRITY_KEY)
        restored_wrapper = RemoteMonotonicFreshnessVerifier(restored_local, harness.client)
        try:
            restored_wrapper.verify_and_consume([harness.certificate], reports, challenge)
            result = "ERROR_REPLAY_ACCEPTED"
        except RegistryRejected as exc:
            result = str(exc)
        summary = {
            "demo": "PASS" if result == "challenge-already-consumed" else "FAIL",
            "primary_ledger_restored": True,
            "registry_restored": False,
            "replay_result": result,
            "statement": "Primary-ledger rollback is rejected while the spent-nonce registry remains current.",
            "hosted_calls": 0,
        }
        print(json.dumps(summary, indent=2))
        if summary["demo"] != "PASS":
            raise SystemExit(1)
    finally:
        harness.tearDown()

if __name__ == "__main__":
    main()
