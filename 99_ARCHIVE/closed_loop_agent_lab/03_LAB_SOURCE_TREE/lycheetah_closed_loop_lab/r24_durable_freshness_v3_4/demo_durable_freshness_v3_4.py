"""No-network demo of durable one-use current-chain verification."""
from __future__ import annotations
import json
from pathlib import Path
from durable_freshness_verifier import ChallengeLifecycleError
from test_durable_freshness_verifier import DurableFreshnessVerifierTests


def main() -> None:
    fixture = DurableFreshnessVerifierTests()
    fixture.setUp()
    try:
        challenge, reports = fixture.issue_and_reports()
        heads = fixture.verifier.verify_and_consume([fixture.certificate], reports, challenge)
        result = {
            "demo": "PASS",
            "database_id": heads[-1].database_id,
            "sequence": heads[-1].sequence,
            "head_sha256": heads[-1].record_sha256,
            "network_calls": 0,
        }
        try:
            fixture.verifier.verify_and_consume([fixture.certificate], reports, challenge)
        except ChallengeLifecycleError as exc:
            result["replay_rejected"] = str(exc) == "challenge-already-consumed"
            result["replay_reason"] = str(exc)
        else:
            result["replay_rejected"] = False
        assert result["replay_rejected"]
        Path("demo_durable_freshness_v3.4.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(result, indent=2))
    finally:
        fixture.tearDown()


if __name__ == "__main__":
    main()
