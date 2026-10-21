"""Local file-write demonstration of protected context and bound risk.

Uses synthetic numerical proposals and declared demo approval metadata. This
does not authenticate a human, sandbox arbitrary executor code, or implement a
separately deployed signer/publisher. No model or network provider is called.
By default its workspace is disposable. --export retains an inspectable bundle
without copying private checkpoint keys; --verify only reads that bundle.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lycheetah import SovereignExecutionHarness  # noqa: E402
from lycheetah.assurance import AssuranceReceipt, action_digest  # noqa: E402
from lycheetah.assurance.jsonutil import sha256_json  # noqa: E402
from lycheetah.compaction import AgentStatePacket, CompactionShield  # noqa: E402
from lycheetah.consensus import ConsensusArena  # noqa: E402
from lycheetah.handoff import HandoffCapsule, create_capsule, verify_handoff  # noqa: E402
from lycheetah.sovereign_harness import (  # noqa: E402
    EPISTEMIC_BOUNDARIES,
    HARNESS_SCHEMA_VERSION,
    PERMIT_SCHEMA_VERSION,
    SovereignExecutionPermit,
)


BUNDLE_SCHEMA = "lycheetah.guarded-handoff-demo.v1"
BUNDLE_FILES = (
    "task.json",
    "completed-task.json",
    "packet.json",
    "context.l1",
    "action.json",
    "assurance-receipt.json",
    "run-report.json",
    "handoff.txt",
)
MAX_FILE_BYTES = 1_048_576
BUNDLE_LIMITS = [
    "Synthetic numerical proposals, not live agent deliberation",
    "Declared demo approval, not authenticated human consent",
    "Trusted fixed callback, not arbitrary-executor containment",
    "Observation in this process, not an independent filesystem witness",
    "Unsigned hashes establish consistency; retain the manifest digest separately",
    "A bundle does not export or independently authenticate checkpoint signing keys",
]


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode()


def _read_json(payload: bytes) -> Any:
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj

    def invalid_constant(value):
        raise ValueError(f"nonfinite JSON value: {value}")

    return json.loads(payload, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def _export_bundle(directory: Path, files: dict[str, bytes]) -> dict[str, Any]:
    """Explicitly create a new directory. Never export the private guard store."""
    if set(files) != set(BUNDLE_FILES):
        raise ValueError("incomplete export file set")
    directory.mkdir(mode=0o700)  # Existing paths, including symlinks, are refused.
    manifest = {"schema": BUNDLE_SCHEMA, "files": {}}
    for name in BUNDLE_FILES:
        payload = files[name]
        with (directory / name).open("xb") as stream:
            stream.write(payload)
        manifest["files"][name] = {"bytes": len(payload), "sha256": sha256(payload).hexdigest()}
    # Written last: a partial export cannot pass as a complete bundle.
    payload = _json_bytes(manifest)
    with (directory / "manifest.json").open("xb") as stream:
        stream.write(payload)
    return {
        "directory": str(directory),
        "manifest_sha256": sha256(payload).hexdigest(),
        "files": len(files),
        "private_keys_exported": False,
    }


def _recorded_witness_digest(record: dict[str, Any]) -> str:
    """Reconstruct the documented v1 witness projection for read-only inspection.

    This envelope covers a subset of gateway fields. Cross-checking its remaining
    receipt, result and artifact relationships is also required below.
    """
    gateway = record["gateway_result"]
    return sha256_json(
        {
            "schema": record["schema"],
            "accepted": record["accepted"],
            "status": record["status"],
            "stop_reason": record["stop_reason"],
            "provider_called": record["provider_called"],
            "permit_digest": record["permit"]["permit_digest"],
            "live_action_hash": record["live_action_hash"],
            "live_scope": record["live_scope"],
            "live_state_version": record["live_state_version"],
            "evaluated_at": record["evaluated_at"],
            "consensus_summary": record["consensus_summary"],
            "compaction_summary": record["compaction_summary"],
            "gateway_effect_id": gateway["effect_id"] if gateway else None,
            "gateway_status": gateway["status"] if gateway else None,
            "epistemic_boundaries": list(record["epistemic_boundaries"]),
        }
    )


def verify_bundle(directory: Path, expected_digest: str | None = None) -> dict[str, Any]:
    """Read local evidence, without executing a task or trusting its author identity.

    A separately retained manifest digest pins the evidence bytes. Without that
    reference, a fully rewritten self-consistent bundle cannot be detected.
    """
    errors: list[str] = []
    checks = 0
    digest = None

    def check(condition: bool, description: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(description)

    try:
        manifest_path = directory / "manifest.json"
        if (
            manifest_path.is_symlink()
            or not manifest_path.is_file()
            or manifest_path.stat().st_size > MAX_FILE_BYTES
        ):
            raise ValueError("manifest must be a bounded regular file")
        payload = manifest_path.read_bytes()
        digest = sha256(payload).hexdigest()
        if expected_digest is not None:
            check(digest == expected_digest, "manifest differs from the retained digest")
        manifest = _read_json(payload)
        check(set(manifest) == {"schema", "files"}, "invalid manifest fields")
        check(manifest["schema"] == BUNDLE_SCHEMA, "unsupported bundle schema")
        check(set(manifest["files"]) == set(BUNDLE_FILES), "missing or unexpected manifest files")
        check(
            {p.name for p in directory.iterdir()} == {*BUNDLE_FILES, "manifest.json"},
            "missing or unexpected bundle entries",
        )
        if errors:
            raise ValueError("manifest checks failed")
        files = {}
        for name in BUNDLE_FILES:
            path = directory / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError(f"{name} must be a bounded regular file")
            data = path.read_bytes()
            entry = manifest["files"][name]
            check(
                entry == {"bytes": len(data), "sha256": sha256(data).hexdigest()},
                f"{name} size or digest mismatch",
            )
            files[name] = data
        if errors:
            raise ValueError("file checks failed")

        task = HandoffCapsule.from_dict(_read_json(files["task.json"]))
        completed = HandoffCapsule.from_dict(_read_json(files["completed-task.json"]))
        packet = AgentStatePacket.from_dict(_read_json(files["packet.json"]))
        restored = CompactionShield.decompact(files["context.l1"].decode("utf-8"))
        action = _read_json(files["action.json"])
        receipt = AssuranceReceipt.from_dict(_read_json(files["assurance-receipt.json"]))
        report = _read_json(files["run-report.json"])
        observed = files["handoff.txt"]
        observed_hash = sha256(observed).hexdigest()
        check(packet.to_dict() == restored.to_dict(), "wire context differs from the full packet")
        check(task.to_agent_state_packet().to_dict() == packet.to_dict(), "task context differs")
        check(verify_handoff(task, completed).passed, "completion declarations differ from task")
        check(receipt.verify().valid, "assurance receipt integrity or decision mismatch")
        check(completed.result is not None, "completion result is absent")
        if completed.result is not None:
            check(
                completed.result.receipt_digest == receipt.digest,
                "completion names another receipt",
            )
            check(
                completed.result.modified_files == ("handoff.txt",),
                "completion omits the actual write",
            )
            check(
                completed.result.completed_by == task.recipient,
                "completion names another recipient",
            )
        check(task.target_paths == ("handoff.txt",), "unexpected target declaration")
        check(
            action
            == {
                "tool": "artifact.create",
                "path": "handoff.txt",
                "content_sha256": observed_hash,
                "bytes": len(observed),
                "side_effect": True,
                "task_digest": task.task_digest(),
                "context_full_hash": packet.full_hash,
            },
            "action does not bind the task, full context and observed bytes",
        )
        check(
            receipt.event.get("action_hash") == action_digest(action),
            "receipt names another action",
        )
        check(receipt.event.get("actor") == task.recipient, "receipt actor differs from recipient")
        check(receipt.event.get("scope") == task.scope, "receipt scope differs from task")
        check(receipt.metrics.get("execution_status") == "SUCCEEDED", "execution did not succeed")
        check(report["executor_calls"] == 1, "run does not report exactly one executor call")
        success = report["valid_execution"]
        check(
            success["accepted"] is True and success["status"] == "SUCCEEDED", "run did not succeed"
        )
        check(success["provider_called"] is True, "run did not report an executor call")
        check(
            success["permit"]["action_hash"] == action_digest(action), "permit names another action"
        )
        permit_data = dict(success["permit"])
        check(permit_data.pop("schema") == PERMIT_SCHEMA_VERSION, "unexpected permit schema")
        permit_data["allowed_scopes"] = tuple(permit_data["allowed_scopes"])
        permit = SovereignExecutionPermit(**permit_data)
        check(permit.compute_digest() == permit.permit_digest, "permit digest mismatch")
        check(permit.bound_risk == packet.risk, "permit risk differs from context")
        check(
            permit.compaction_critical_hash == packet.critical_hash, "permit context hash differs"
        )
        check(permit.bound_packet_id == packet.id, "permit packet identity differs")
        check(
            permit.actor == task.recipient and permit.authority_id == task.authority_id,
            "permit participants differ from task",
        )
        check(
            permit.bound_scope == task.scope and task.scope in permit.allowed_scopes,
            "permit scope differs from task",
        )
        check(permit.state_version == success["live_state_version"], "permit state version differs")
        check(
            permit.issued_at <= success["evaluated_at"] < permit.expires_at,
            "reported execution falls outside permit validity",
        )
        check(
            permit.consensus_digest == success["consensus_summary"]["consensus_digest"],
            "permit consensus digest differs",
        )
        context = success["compaction_summary"]
        check(
            context["candidate_critical_hash"] == packet.critical_hash
            and context["packet_id"] == packet.id,
            "reported context identity differs from packet",
        )
        check(
            all(context[key] == packet.risk for key in ("risk", "reference_risk", "bound_risk")),
            "reported context risk differs from packet",
        )
        check(
            context["is_safe"] is True
            and context["classification"] == "EXACT_EQUIVALENT"
            and context["has_recovery"] == bool(packet.recovery),
            "reported context comparison contradicts the retained packet",
        )
        check(success["live_scope"] == task.scope, "reported live scope differs")
        check(success["live_action_hash"] == action_digest(action), "reported live action differs")
        gateway = success["gateway_result"]
        check(
            gateway["status"] == "SUCCEEDED" and gateway["provider_called"] is True,
            "gateway outcome contradicts success",
        )
        check(gateway["assurance_receipt_digest"] == receipt.digest, "run receipt differs")
        check(
            gateway["effect_id"] == receipt.metrics["effect_id"],
            "gateway effect differs from receipt",
        )
        check(
            gateway["action_hash"] == action_digest(action), "gateway action differs from receipt"
        )
        check(
            gateway["checkpoint_generation"] == receipt.metrics["checkpoint_generation"],
            "gateway checkpoint differs from receipt",
        )
        check(
            gateway["result"] == {"status": "success", "sha256": observed_hash},
            "gateway result differs from observed bytes",
        )
        check(
            report["observed_file"]
            == {
                "relative_path": "handoff.txt",
                "bytes": len(observed),
                "sha256": observed_hash,
                "matches_declared_content": True,
            },
            "run observation differs from retained artifact",
        )
        for key, reason in (
            ("risk_downgrade", "CANDIDATE_RISK_MISMATCH"),
            ("action_substitution", "ACTION_PAYLOAD_MISMATCH"),
            ("replay", "PERMIT_REPLAYED"),
        ):
            check(
                report[key]["stop_reason"] == reason and report[key]["provider_called"] is False,
                f"{key} control did not report the expected stop",
            )
        for key in ("valid_execution", "risk_downgrade", "action_substitution", "replay"):
            record = report[key]
            check(
                record["schema"] == HARNESS_SCHEMA_VERSION
                and record["epistemic_boundaries"] == list(EPISTEMIC_BOUNDARIES),
                f"{key} witness format differs",
            )
            check(
                _recorded_witness_digest(record) == record["witness_digest"],
                f"{key} witness digest mismatch",
            )
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        errors.append(str(error))

    return {
        "valid": not errors,
        "status": "INVALID_BUNDLE"
        if errors
        else ("MATCHES_RETAINED_DIGEST" if expected_digest is not None else "SELF_CONSISTENT"),
        "checks": checks,
        "manifest_sha256": digest,
        "retained_digest_supplied": expected_digest is not None,
        "errors": errors,
        "limits": BUNDLE_LIMITS,
    }


def run_demo(export_dir: Path | None = None) -> dict:
    if export_dir is not None and (export_dir.exists() or export_dir.is_symlink()):
        raise FileExistsError(f"export destination already exists: {export_dir}")
    content = b"One declared demo action, carried through a protected context packet.\n"
    task = create_capsule(
        purpose="Create one fixed file in a disposable workspace",
        issuer="demo-reviewer",
        recipient="demo-worker",
        scope="artifact:create",
        risk="HIGH",
        target_paths=["handoff.txt"],
        protected_paths=["guard"],
        invariants=["Only create the declared handoff.txt"],
        recovery=["Discard the temporary demo workspace"],
        unknowns=["Does this local fixture predict behavior in a real deployment? Unmeasured."],
        authority_id="demo-reviewer",
    )
    packet = task.to_agent_state_packet()
    action = {
        "tool": "artifact.create",
        "path": "handoff.txt",
        "content_sha256": sha256(content).hexdigest(),
        "bytes": len(content),
        "side_effect": True,
        "task_digest": task.task_digest(),
        "context_full_hash": packet.full_hash,
    }
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("demo-worker", [1.0, 0.0], claim="Synthetic numerical fixture")
    arena.add_agent("demo-reviewer", [1.0, 0.0], claim="Synthetic numerical fixture")
    verdict = arena.deliberate()
    wire = CompactionShield.compact(packet)
    with tempfile.TemporaryDirectory(prefix="lycheetah_guarded_handoff_") as temporary:
        root = Path(temporary)
        workspace = root / "output"
        workspace.mkdir()
        target = workspace / "handoff.txt"
        harness = SovereignExecutionHarness(root / "guard")
        permit = harness.issue_permit(
            permit_id="demo-single-use",
            actor="demo-worker",
            authority_id="demo-reviewer",
            allowed_scopes=("artifact:create",),
            bound_scope="artifact:create",
            state_version="disposable-empty-workspace-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=packet,
        )
        calls = []

        def publish():
            # Trusted demo callback: the path/bytes are fixed by this script.
            # A deployment needs a restricted publisher and protected approval issuer.
            calls.append("publish")
            with target.open("xb") as output:
                output.write(content)
            return {"status": "success", "sha256": sha256(target.read_bytes()).hexdigest()}

        def dispatch(candidate=wire, live_action=None):
            return harness.evaluate_and_execute(
                permit=permit,
                consensus=verdict,
                reference_packet=packet,
                candidate_packet=candidate,
                live_action=action if live_action is None else live_action,
                live_scope="artifact:create",
                current_state_version="disposable-empty-workspace-v1",
                executor=publish,
            )

        changed_risk = replace(packet, risk="LOW")
        if changed_risk.critical_hash != packet.critical_hash:
            raise RuntimeError("Demo did not exercise a risk-only change outside the critical hash")
        downgraded = dispatch(CompactionShield.compact(changed_risk))
        swapped = dispatch(live_action={**action, "path": "another-file.txt"})
        if (
            downgraded.stop_reason != "CANDIDATE_RISK_MISMATCH"
            or swapped.stop_reason != "ACTION_PAYLOAD_MISMATCH"
            or downgraded.provider_called
            or swapped.provider_called
            or calls
            or target.exists()
        ):
            raise RuntimeError("An altered request was not refused before the file operation")
        valid = dispatch()
        if not valid.accepted or calls != ["publish"] or target.read_bytes() != content:
            raise RuntimeError("Valid declared demo action did not produce the exact output once")
        replay = dispatch()
        if (
            replay.stop_reason != "PERMIT_REPLAYED"
            or replay.provider_called
            or calls != ["publish"]
        ):
            raise RuntimeError("Replay was not refused without a second callback")
        observed = target.read_bytes()
        if valid.gateway_result is None or valid.gateway_result.receipt is None:
            raise RuntimeError("Successful action did not retain a full assurance receipt")
        receipt = valid.gateway_result.receipt
        if not receipt.verify().valid:
            raise RuntimeError("The emitted assurance receipt failed its own verifier")
        completed = task.complete(
            completed_by=task.recipient,
            summary="Observed the exact declared file bytes once",
            modified_files=["handoff.txt"],
            receipt_digest=receipt.digest,
            evidence_notes="Local in-process observation; no external human or filesystem attestation",
        )
        if not verify_handoff(task, completed).passed:
            raise RuntimeError("Completion declarations differ from the task")
        report = {
            "mode": "DISPOSABLE_LAB_DEMONSTRATION",
            "limits": BUNDLE_LIMITS,
            "permit_schema": permit.to_dict()["schema"],
            "bound_risk": permit.bound_risk,
            "critical_hash_unchanged_by_risk_downgrade": True,
            "risk_downgrade": downgraded.to_dict(),
            "action_substitution": swapped.to_dict(),
            "valid_execution": valid.to_dict(),
            "replay": replay.to_dict(),
            "observed_file": {
                "relative_path": "handoff.txt",
                "bytes": len(observed),
                "sha256": sha256(observed).hexdigest(),
                "matches_declared_content": observed == content,
            },
            "executor_calls": len(calls),
            "temporary_workspace_removed_on_exit": True,
        }
        if export_dir is not None:
            report["export"] = _export_bundle(
                export_dir,
                {
                    "task.json": _json_bytes(task.to_dict()),
                    "completed-task.json": _json_bytes(completed.to_dict()),
                    "packet.json": _json_bytes(packet.to_dict()),
                    "context.l1": wire.encode("utf-8"),
                    "action.json": _json_bytes(action),
                    "assurance-receipt.json": _json_bytes(receipt.to_dict()),
                    "run-report.json": _json_bytes(report),
                    "handoff.txt": observed,
                },
            )
        return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--export", type=Path, help="Retain evidence in a new directory")
    mode.add_argument(
        "--verify", type=Path, help="Read and verify an existing bundle without executing"
    )
    parser.add_argument("--expected-digest", help="Separately retained SHA-256 of manifest.json")
    args = parser.parse_args(argv)
    if args.expected_digest is not None:
        if not args.verify:
            parser.error("--expected-digest requires --verify")
        if len(args.expected_digest) != 64 or any(
            c not in "0123456789abcdef" for c in args.expected_digest
        ):
            parser.error("--expected-digest must be 64 lowercase hexadecimal characters")
    try:
        report = (
            verify_bundle(args.verify, args.expected_digest)
            if args.verify
            else run_demo(args.export)
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Handoff demonstration failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 1 if report.get("valid") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
