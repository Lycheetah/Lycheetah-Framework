"""Disposable file-write demonstration of protected context and bound risk.

Uses synthetic numerical proposals and declared demo approval metadata. This
does not authenticate a human, sandbox arbitrary executor code, or implement a
separately deployed signer/publisher. No model or network provider is called.
"""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lycheetah import SovereignExecutionHarness  # noqa: E402
from lycheetah.compaction import AgentStatePacket, CompactionShield  # noqa: E402
from lycheetah.consensus import ConsensusArena  # noqa: E402


def run_demo() -> dict:
    content = b"One declared demo action, carried through a protected context packet.\n"
    action = {
        "tool": "artifact.create", "path": "handoff.txt",
        "content_sha256": sha256(content).hexdigest(),
        "bytes": len(content), "side_effect": True,
    }
    packet = AgentStatePacket(
        id="demo-handoff-packet",
        purpose="Create one fixed file in a disposable workspace",
        claim="Demonstrate risk/context binding, one use and observed output",
        risk="HIGH",
        invariants=[{"id": "I1", "text": "Only create the declared handoff.txt"}],
        authority=[{
            "id": "demo-reviewer", "scope": "artifact:create",
            "text": "Synthetic declared approval; not a human-authenticated signature",
        }],
        recovery=[{"id": "R1", "text": "Discard the temporary demo workspace"}],
    )
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
            permit_id="demo-single-use", actor="demo-worker", authority_id="demo-reviewer",
            allowed_scopes=("artifact:create",), bound_scope="artifact:create",
            state_version="disposable-empty-workspace-v1", action=action,
            consensus_verdict=verdict, reference_packet=packet,
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
                permit=permit, consensus=verdict, reference_packet=packet,
                candidate_packet=candidate, live_action=live_action or action,
                live_scope="artifact:create", current_state_version="disposable-empty-workspace-v1",
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
            or downgraded.provider_called or swapped.provider_called or calls or target.exists()
        ):
            raise RuntimeError("An altered request was not refused before the file operation")
        valid = dispatch()
        if not valid.accepted or calls != ["publish"] or target.read_bytes() != content:
            raise RuntimeError("Valid declared demo action did not produce the exact output once")
        replay = dispatch()
        if replay.stop_reason != "PERMIT_REPLAYED" or replay.provider_called or calls != ["publish"]:
            raise RuntimeError("Replay was not refused without a second callback")
        observed = target.read_bytes()
        return {
            "mode": "DISPOSABLE_LAB_DEMONSTRATION",
            "limits": [
                "Synthetic numerical proposals, not live agent deliberation",
                "Declared demo approval, not authenticated human consent",
                "Trusted fixed callback, not arbitrary-executor containment",
                "Observation in this process, not an independent filesystem witness",
            ],
            "permit_schema": permit.to_dict()["schema"], "bound_risk": permit.bound_risk,
            "critical_hash_unchanged_by_risk_downgrade": True,
            "risk_downgrade": downgraded.to_dict(), "action_substitution": swapped.to_dict(),
            "valid_execution": valid.to_dict(), "replay": replay.to_dict(),
            "observed_file": {
                "relative_path": "handoff.txt", "bytes": len(observed),
                "sha256": sha256(observed).hexdigest(), "matches_declared_content": observed == content,
            },
            "executor_calls": len(calls), "temporary_workspace_removed_on_exit": True,
        }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
