"""Offline CLI for external-checkpoint fingerprinting, verification and approved publish."""
from __future__ import annotations
import argparse
import base64
import json
import os
from pathlib import Path
import sys

from external_checkpoint import (
    CheckpointError, SQLiteReferenceAnchor, StateChangeApproval,
    capture_database_snapshot, publish_checkpoint, verify_database_against_anchor,
)
from integrity_key_rotation import KeyRotationError


def _env_key(name: str) -> bytes:
    value = os.environ.get(name)
    if not value:
        raise CheckpointError(f"required environment variable {name} is missing")
    try:
        key = base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error):
        raise CheckpointError(f"environment variable {name} must contain base64 key bytes") from None
    if len(key) < 32:
        raise CheckpointError(f"key loaded from {name} must be at least 32 bytes")
    return key


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reference startup gate for a SQLite database and separate monotonic anchor.")
    parser.add_argument("--mode", choices=("fingerprint", "verify", "publish"), required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--database-id", required=True)
    parser.add_argument("--anchor-database")
    parser.add_argument("--approval-json")
    parser.add_argument("--integrity-key-env", default="LYC_PRIMARY_INTEGRITY_KEY_B64")
    parser.add_argument("--anchor-key-env", default="LYC_EXTERNAL_ANCHOR_KEY_B64")
    parser.add_argument("--operator-key-env", default="LYC_CHECKPOINT_OPERATOR_KEY_B64")
    parser.add_argument("--anchor-key-id", default="anchor-v3")
    args = parser.parse_args(argv)

    try:
        integrity_key = _env_key(args.integrity_key_env)
        if args.mode == "fingerprint":
            snapshot = capture_database_snapshot(args.database, integrity_key)
            print(json.dumps({"status": "FINGERPRINTED", **snapshot.to_dict()}, sort_keys=True))
            return 0
        if not args.anchor_database:
            raise CheckpointError("--anchor-database is required for verify/publish")
        anchor_key = _env_key(args.anchor_key_env)
        anchor = SQLiteReferenceAnchor(args.anchor_database, anchor_key=anchor_key,
                                        anchor_key_id=args.anchor_key_id)
        if args.mode == "verify":
            result = verify_database_against_anchor(args.database, database_id=args.database_id,
                                                    integrity_key=integrity_key, anchor=anchor)
            print(json.dumps(result, sort_keys=True))
            return 0 if result.get("safe_to_continue") is True else 3
        if not args.approval_json:
            raise CheckpointError("--approval-json is required for publish")
        operator_key = _env_key(args.operator_key_env)
        try:
            raw = json.loads(Path(args.approval_json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise CheckpointError("approval file unreadable or invalid JSON") from None
        approval = StateChangeApproval.from_dict(raw)
        record = publish_checkpoint(args.database, database_id=args.database_id,
                                    integrity_key=integrity_key, anchor=anchor,
                                    approval=approval, operator_key=operator_key)
        print(json.dumps({"status": "CHECKPOINT_PUBLISHED", "checkpoint": record.to_dict()}, sort_keys=True))
        return 0
    except (CheckpointError, KeyRotationError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
