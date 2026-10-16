"""Reproduce four acceptance classes (five concrete cases) in frozen v3.2."""

This script intentionally loads the baseline modules in a subprocess-compatible
layout. It performs no network calls and creates no remote actions.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASELINE = HERE / "baseline_v3_2"
sys.path.insert(0, str(BASELINE))
from remote_anchor_http import canonical, sha256, b64  # noqa: E402
from test_checkpoint_witness_quorum import CheckpointWitnessQuorumTests, DBID  # noqa: E402
from checkpoint_witness_quorum import (  # noqa: E402
    DOMAIN_WITNESS, VERSION, CheckpointWitness, FreshHeadQuorum, create_certificate,
    verify_certificate, verify_current_chain, verified_head,
)


def recompute_public_certificate_digest(cert):
    body = {k: v for k, v in cert.items() if k != "certificate_sha256"}
    cert["certificate_sha256"] = sha256(canonical(body))


def main():
    results = {}
    fixture = CheckpointWitnessQuorumTests()
    fixture.setUp()
    try:
        votes = list(fixture.bootstrap().values())
        cert = create_certificate(fixture.r1, votes, fixture.anchor_keys, fixture.witness_keys)
        fabricated = FreshHeadQuorum(DBID, 1, cert["record_sha256"], "A" * 32, (), ())
        try:
            verify_current_chain([cert], fabricated, fixture.anchor_keys, fixture.witness_keys)
            results["caller_constructed_freshness_summary"] = "ACCEPTED_BY_V3_2"
        except Exception as exc:
            results["caller_constructed_freshness_summary"] = f"REJECTED:{type(exc).__name__}:{exc}"

        # Four distinct roster names alias one Ed25519 public key. That one key
        # can sign three differently named vote statements in the baseline.
        alias_registry = {wid: fixture.witness_keys["witness-1"] for wid in fixture.witness_keys}
        head = verified_head(fixture.r1, fixture.anchor_keys)
        alias_votes = []
        signer = fixture.witness_privates["witness-1"]
        for wid in ("witness-1", "witness-2", "witness-3"):
            body = {"version": VERSION, "witness_id": wid, **head.to_dict()}
            alias_votes.append({**body, "signature_b64": b64(signer.sign(DOMAIN_WITNESS + canonical(body)))})
        alias_cert = create_certificate(fixture.r1, alias_votes, fixture.anchor_keys, alias_registry)
        verify_certificate(alias_cert, fixture.anchor_keys, alias_registry)
        results["aliased_public_key_quorum"] = "ACCEPTED_BY_V3_2"

        # The pluggable guard interface can return malformed wire-like state.
        # v3.2's attest path trusted bool-as-int here even though report_head did not.
        class BooleanGuard:
            def get_head(self, database_id):
                return (True, fixture.r1["record_sha256"])
            def compare_and_swap(self, *args):
                raise AssertionError("unexpected CAS")
        bad_guard = BooleanGuard()
        bad_guard_witness = CheckpointWitness(
            "witness-guard-probe", fixture.witness_privates["witness-1"],
            fixture.root / "bad-guard-probe.sqlite", bad_guard, fixture.anchor_keys,
        )
        try:
            bad_guard_witness.attest(fixture.r1)
            results["boolean_guard_sequence"] = "ACCEPTED_BY_V3_2"
        except Exception as exc:
            results["boolean_guard_sequence"] = f"REJECTED:{type(exc).__name__}:{exc}"

        # Bool is a subclass of int and True == 1. A public digest can be
        # recomputed by any party, so the signature-backed vote set stays valid.
        for field, bad_value in (("sequence", True), ("max_byzantine", True)):
            cert2 = create_certificate(fixture.r1, votes, fixture.anchor_keys, fixture.witness_keys)
            cert2[field] = bad_value
            recompute_public_certificate_digest(cert2)
            try:
                verify_certificate(cert2, fixture.anchor_keys, fixture.witness_keys)
                results[f"boolean_{field}"] = "ACCEPTED_BY_V3_2"
            except Exception as exc:
                results[f"boolean_{field}"] = f"REJECTED:{type(exc).__name__}:{exc}"
    finally:
        fixture.tearDown()
    output = HERE / "baseline_v3_2_reproduction.json"
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
