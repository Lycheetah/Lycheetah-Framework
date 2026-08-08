"""
Worked example — compacting an agent's carried state without losing the caveats.

THE PROBLEM
-----------
A long-running agent summarises its own history to fit a context window. Every
such summary silently drops things, and the things most worth keeping are the
ones a summariser finds least quotable: what is still unknown, who actually holds
authority, who objected, how to get back to the prior state.

Ordinary compression optimises bytes and is indifferent to which bytes. This
codec is indifferent to bytes and opinionated about which fields.

WHAT THIS DEMONSTRATES
----------------------
1. A protected unknown with no recovery path is a validation ERROR, not a warning
   — the packet will not encode at all.
2. `critical_hash` gives a third party proof that the ten accountability fields
   survived a compaction round trip, without their having to trust the compactor.
3. Round-tripping is exact.

Run:
    python3 examples/agent_state_compaction.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from lamague_codec import (  # noqa: E402
    CodecError,
    critical_hash,
    decode,
    encode,
    full_hash,
    safety_violations,
    validate_packet,
)

BAR = "─" * 70


def agent_session_packet() -> dict:
    """
    One turn of an agent session, expressed as an accountability record.

    The operations string declares which semantic operations the packet uses.
    The codec cross-checks it against the content: an unknown without `U`, or a
    dissent without `V`, fails closed rather than encoding a record whose
    declared shape and actual shape disagree.
    """
    return {
        "schema": "LAMAGUE-SEMANTIC-PACKET-1",
        "id": "session-2026-08-08-turn-41",
        "purpose": "Compact 40 turns of agent context into carried state",
        "claim": "The migration script is safe to run against staging",
        "risk": "HIGH",
        # U unknowns · G authority/affected · V dissent · F recovery · Y yield
        "operations": ["U", "G", "V", "F", "Y"],
        "evidence": [
            {
                "id": "e1",
                "text": "Dry run completed against a staging snapshot, 0 errors",
                "provenance": "tool:bash turn 37",
            },
            {
                "id": "e2",
                "text": "Schema diff reviewed, 3 columns added, none dropped",
                "provenance": "tool:read turn 39",
            },
        ],
        # This is the payload the whole codec exists to protect.
        "unknowns": [
            {
                "id": "u1",
                "protected": True,
                "requiredFor": "Production rollout — staging has 1/1000th of prod row count",
            },
            {
                "id": "u2",
                "protected": True,
                "requiredFor": "Rollback window — no one has confirmed the backup is restorable",
            },
        ],
        "invariants": [
            {"id": "i1", "text": "No destructive DDL without an explicit human confirmation"},
        ],
        "authority": [
            {"id": "a1", "scope": "production-database", "text": "Platform on-call holds the go/no-go"},
        ],
        "participants": ["agent", "engineer-on-duty"],
        "affectedParties": ["platform-oncall", "downstream-consumers"],
        "dissent": [
            {
                "party": "engineer-on-duty",
                "position": "Staging row count is not representative; wants a prod-scale rehearsal first",
            },
        ],
        "valueFlow": [
            {
                "source": "platform-oncall",
                "recipient": "agent",
                "consent": "REVOCABLE",
                "kind": "delegated-execution-authority",
            },
        ],
        # Present because u1 and u2 are protected. Remove this and the packet
        # will not encode — see demonstrate_the_invariant() below.
        "recovery": [
            {"id": "r1", "text": "Restore from snapshot staging-2026-08-08T09:00Z, verified restorable"},
        ],
        "horizon": "Until the prod-scale rehearsal completes",
        "yield": "Proceed on staging only; production blocked pending u1 and u2",
    }


def demonstrate_the_invariant() -> None:
    """
    Drop the recovery path while protected unknowns remain, and watch it fail.

    This is the whole product in six lines. Most compaction schemes would
    cheerfully drop `recovery` — it is prose, it is long, and it is the field a
    summariser is least likely to think is load-bearing.
    """
    print("\n1. THE INVARIANT")
    packet = agent_session_packet()
    packet["recovery"] = []

    violations = safety_violations(packet)
    print(f"   removed the recovery path, kept two protected unknowns")
    print(f"   safety_violations() → {violations}")

    try:
        encode(packet)
        print("   ✗ REGRESSION: it encoded anyway")
    except CodecError as exc:
        print(f"   ✓ refused to encode: {exc}")


def demonstrate_the_proof() -> None:
    """
    critical_hash proves the ten accountability fields survived compaction.

    A consumer who never sees the original can still verify the projection,
    because the hash is over canonical JSON of the critical fields alone.
    """
    print("\n2. THE PROOF")
    packet = validate_packet(agent_session_packet())

    before_full = full_hash(packet)
    before_critical = critical_hash(packet)

    wire = encode(packet)
    restored = decode(wire)

    print(f"   encoded to {len(wire)} chars")
    print(f"   full_hash      before {before_full[:16]}…")
    print(f"                   after {full_hash(restored)[:16]}…")
    print(f"   critical_hash  before {before_critical[:16]}…")
    print(f"                   after {critical_hash(restored)[:16]}…")

    assert restored == packet, "round trip was not exact"
    assert full_hash(restored) == before_full
    assert critical_hash(restored) == before_critical
    print("   ✓ round trip exact; both hashes match")


def demonstrate_the_boundary() -> None:
    """
    State plainly what this does NOT do. The codec's own docs say it; a README
    that omitted it would be selling something the code does not deliver.
    """
    print("\n3. THE BOUNDARY")
    print("   · operates on DECLARED structured packets")
    print("   · does NOT infer a packet from unrestricted natural language")
    print("   · benchmark corpus is synthetic and structured")
    print("   · mutation accuracy measured on constructed deletions,")
    print("     not on adversarial model output")
    print("   See docs/CLAIM_BOUNDARY.md — the limits are the module's own.")


def main() -> int:
    print(BAR)
    print("Agent state compaction — a provable floor under a lossy summary")
    print(BAR)
    demonstrate_the_invariant()
    demonstrate_the_proof()
    demonstrate_the_boundary()
    print("\n" + BAR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
