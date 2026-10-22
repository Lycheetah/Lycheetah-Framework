"""Batch 6 (RV07) probes: what the compaction shield detects, and what it cannot.

Run against one tree at a time and compare the outputs:

    python3 repro_batch6.py <tree-root> > out.jsonl

Each line is one probe: the drift applied and the shield's verdict. Nothing here
writes to disk. The probes use synthetic packets only.
"""

import json
import sys
from dataclasses import replace

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else ".")

import lycheetah  # noqa: E402
from lycheetah.compaction import AgentStatePacket, CompactionShield, ContextProtector  # noqa: E402

U1 = {"id": "U1", "protected": True, "requiredFor": "cutover"}
U2 = {"id": "U2", "protected": False, "requiredFor": "reporting"}
E1 = {"id": "E1", "text": "Plan reviewed", "provenance": "reviewer"}
E2 = {"id": "E2", "text": "Backup taken", "provenance": "operator"}
KEYS = ("classification", "is_safe", "fields", "violations", "changed_fields", "unchecked_fields")


def packet(**changes):
    base = AgentStatePacket(
        id="drift-packet",
        purpose="Migrate a synthetic ledger",
        claim="Dry run only",
        risk="CRITICAL",
        evidence=[dict(E1), dict(E2)],
        unknowns=[dict(U1)],
        invariants=[{"id": "I1", "text": "no deletes"}, {"id": "I2", "text": "no writes"}],
        authority=[{"id": "A1", "scope": "db:write", "text": "Owner approval"}],
        participants=["worker", "reviewer"],
        affected_parties=["customers"],
        dissent=[{"party": "reviewer", "position": "wait for backup"}],
        recovery=[{"id": "R1", "text": "Restore the snapshot"}],
        horizon="this week",
        yield_desc="halt",
    )
    return replace(base, **changes)


def protector():
    live = ContextProtector("drift-live", "Migrate a synthetic ledger", "Dry run only", risk="HIGH")
    live.add_invariant("I1", "no deletes").add_unknown("U1", "cutover")
    live.add_recovery("R1", "Restore the snapshot").add_authority("A1", "db:write", "Owner")
    live.add_participant("worker").add_affected_party("customers")
    live.add_evidence("E1", "Plan reviewed", "reviewer")
    return live


def emit(probe_id, what, result):
    row = {"id": probe_id, "what": what}
    row.update({key: result[key] for key in KEYS if key in result})
    print(json.dumps(row, sort_keys=True))


def verify(probe_id, what, reference, candidate):
    emit(probe_id, what, CompactionShield.verify_integrity(reference, candidate))


print(json.dumps({"id": "ENV", "lycheetah": lycheetah.__file__}))

# Export independence, both directions.
live = protector()
snapshot = live.export_packet()
snapshot.evidence[0]["text"] = "forged"
snapshot.unknowns.append(dict(U2))
snapshot.authority.clear()
held = live.evidence[0]["text"] == "Plan reviewed" and len(live.unknowns) == len(live.authority) == 1
emit("X1", "mutating an export leaves the accumulator alone", {"is_safe": held})
fresh = live.export_packet()
kept = fresh.to_dict()
live.evidence[0]["text"] = "changed later"
live.unknowns[0]["protected"] = False
live.add_dissent("auditor", "object")
emit("X2", "mutating the accumulator leaves an export alone", {"is_safe": fresh.to_dict() == kept})

# Fields outside the critical projection.
verify("N1", "risk CRITICAL -> LOW", packet(), packet(risk="LOW"))
verify("N2", "risk LOW -> CRITICAL", packet(risk="LOW"), packet())
verify("N3", "evidence dropped", packet(), packet(evidence=[]))
verify("N4", "evidence replaced by an invented claim", packet(),
       packet(evidence=[{"id": "E1", "text": "All tests passed", "provenance": "invented"}]))
verify("N5", "evidence reordered", packet(), packet(evidence=[dict(E2), dict(E1)]))
verify("N6", "yield halt -> proceed", packet(), packet(yield_desc="proceed"))
verify("N7", "horizon changed", packet(), packet(horizon="indefinite"))
verify("N8", "id changed", packet(), packet(id="another-packet"))

# Missing, altered and reordered critical context.
verify("C1", "authority dropped", packet(), packet(authority=[]))
verify("C2", "dissent dropped", packet(), packet(dissent=[]))
verify("C3", "recovery dropped beside a protected unknown", packet(), packet(recovery=[]))
verify("C4", "authority scope altered, same count", packet(),
       packet(authority=[{"id": "A1", "scope": "db:admin", "text": "Owner approval"}]))
verify("C5", "claim altered", packet(), packet(claim="Live run"))
verify("C6", "participants reordered", packet(), packet(participants=["reviewer", "worker"]))
verify("C7", "invariants reordered", packet(),
       packet(invariants=[{"id": "I2", "text": "no writes"}, {"id": "I1", "text": "no deletes"}]))
verify("C8", "protected unknown unprotected", packet(),
       packet(unknowns=[{**U1, "protected": False}]))
verify("C9", "protected unknown swapped for a different protected one", packet(),
       packet(unknowns=[{**U1, "id": "U9"}]))

# A protected and an unprotected unknown side by side.
mixed = packet(unknowns=[dict(U1), dict(U2)])
verify("M1", "mixed unknowns, only horizon changed", mixed, replace(mixed, horizon="next week"))
verify("M2", "mixed unknowns, U1 unprotected", mixed,
       replace(mixed, unknowns=[{**U1, "protected": False}, dict(U2)]))
verify("M3", "protected unknowns, new unprotected one added", packet(),
       packet(unknowns=[dict(U1), dict(U2)]))

# A reference that already breaks a packet rule.
broken = packet(operations=["Y"])
verify("V1", "inherited violation, packet reference", broken, replace(broken, risk="LOW"))
verify("V2", "inherited violation, digest reference", broken.critical_hash, replace(broken, risk="LOW"))
verify("V3", "inherited violation, exact copy", broken, broken)

# Stale snapshots against the live accumulator.
live = protector()
stale = live.export_packet()
live.set_risk("CRITICAL")
emit("S1", "stale snapshot after a risk escalation", live.verify_candidate_summary(stale))
live.add_authority("A2", "db:admin", "Second approver")
emit("S2", "stale snapshot after an authority was added", live.verify_candidate_summary(stale))

# Digest references.
digest = packet().critical_hash
verify("H1", "digest match, risk and evidence changed", digest, packet(risk="LOW", evidence=[]))
verify("H2", "digest in uppercase", digest.upper(), packet())
verify("H3", "64 characters, not hexadecimal", "z" * 64, packet())
verify("H4", "digest with a trailing newline", digest + "\n", packet())
