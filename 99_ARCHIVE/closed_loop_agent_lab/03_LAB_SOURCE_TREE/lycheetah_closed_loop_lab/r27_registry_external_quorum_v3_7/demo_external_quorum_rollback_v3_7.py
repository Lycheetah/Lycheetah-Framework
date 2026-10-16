#!/usr/bin/env python3
"""Demonstrate that external witness heads detect coordinated local rollback.

This imports the same fixture used by the focused tests, but does not call any
hosted endpoint. Witness objects are local test stores, not deployed services.
"""
from __future__ import annotations
import json
from test_registry_checkpoint_quorum import RegistryCheckpointQuorumTests
from registry_checkpoint_quorum import RegistryRollbackDetected

t = RegistryCheckpointQuorumTests()
t.setUp()
try:
    challenge = t.challenge()
    status, _, _ = t.register(challenge)
    if status != 201:
        raise RuntimeError(f"registration did not succeed: {status}")
    registry_snapshot = t.root / "registry-snapshot.sqlite"
    anchor_snapshot = t.root / "anchor-snapshot.sqlite"
    t.sqlite_snapshot(t.db_path, registry_snapshot)
    t.sqlite_snapshot(t.anchor_path, anchor_snapshot)
    consume_status, _, _ = t.consume(challenge)
    if consume_status != 200:
        raise RuntimeError(f"consumption did not succeed: {consume_status}")
    live_before_restore = t.anchor.check_current()
    t.restore_snapshot(registry_snapshot, t.db_path)
    t.restore_snapshot(anchor_snapshot, t.anchor_path)
    restarted = t.make_anchor()
    try:
        restarted.check_current()
        detected = False
        reason = "rollback-not-detected"
    except RegistryRollbackDetected as exc:
        detected = True
        reason = str(exc)
    result = {
        "demo": "PASS" if detected else "FAIL",
        "registry_and_client_anchor_restored": True,
        "witness_stores_restored": False,
        "pre_restore_quorum_sequence": live_before_restore["quorum_head"]["sequence"],
        "rollback_detected": detected,
        "reason": reason,
        "hosted_network_calls": 0,
        "trust_boundary": "witness stores are local per-witness SQLite files in this simulation; not independent remote domains"
    }
    print(json.dumps(result, indent=2))
    if not detected:
        raise SystemExit(1)
finally:
    t.doCleanups()
