"""Context exports are independent references, not views of live session lists."""

import copy
from hashlib import sha256

import pytest

from lycheetah.compaction import CompactionShield, ContextProtector, build_codebook


COLLECTIONS = (
    "invariants",
    "unknowns",
    "recovery",
    "authority",
    "participants",
    "affected_parties",
    "dissent",
    "value_flow",
    "evidence",
)
NESTED_FIELDS = (
    ("invariants", "text"),
    ("unknowns", "requiredFor"),
    ("recovery", "text"),
    ("authority", "text"),
    ("dissent", "position"),
    ("value_flow", "kind"),
    ("evidence", "text"),
)


def populated_context():
    context = ContextProtector("snapshot-session", "Preserve the declared task")
    context.add_invariant("I1", "Keep the input unchanged")
    context.add_unknown("U1", "artifact:create")
    context.add_recovery("R1", "Discard the temporary artifact")
    context.add_authority("reviewer", "artifact:create", "Declared reviewer")
    context.add_participant("worker")
    context.add_affected_party("owner")
    context.add_dissent("reviewer", "Keep the unresolved question visible")
    context.add_value_flow("worker", "owner", "explicit", "artifact")
    context.add_evidence("E1", "Fixture input exists", "constructed test")
    return context


@pytest.mark.parametrize("field", COLLECTIONS)
@pytest.mark.parametrize("direction", ("context_to_packet", "packet_to_context"))
def test_exported_collections_are_independent(field, direction):
    context = populated_context()
    packet = context.export_packet()
    source, observer = (context, packet) if direction == "context_to_packet" else (packet, context)
    expected = copy.deepcopy(getattr(observer, field))
    getattr(source, field).clear()
    assert getattr(observer, field) == expected


@pytest.mark.parametrize("field,key", NESTED_FIELDS)
@pytest.mark.parametrize("direction", ("context_to_packet", "packet_to_context"))
def test_exported_nested_records_are_independent(field, key, direction):
    context = populated_context()
    packet = context.export_packet()
    source, observer = (context, packet) if direction == "context_to_packet" else (packet, context)
    expected = copy.deepcopy(getattr(observer, field))
    getattr(source, field)[0][key] = "changed after export"
    assert getattr(observer, field) == expected


def test_exports_have_independent_generated_operations():
    context = populated_context()
    first = context.export_packet()
    second = context.export_packet()
    expected = list(second.operations)
    first.operations.clear()
    assert second.operations == expected
    assert context.export_packet().operations == expected


@pytest.mark.parametrize("dictionary_mode", (False, True))
def test_snapshot_compaction_roundtrip(dictionary_mode):
    context = populated_context()
    reference = context.export_packet()
    original = reference.to_dict()
    codebook = build_codebook([original]) if dictionary_mode else None
    wire = CompactionShield.compact(reference, codebook)
    restored = CompactionShield.decompact(wire, codebook)
    assert wire.startswith("L1D" if dictionary_mode else "L1{")
    assert restored.to_dict() == original
    assert restored.critical_hash == reference.critical_hash
    assert restored.full_hash == reference.full_hash
    # Recorded from this fixture before the snapshot repair: copying must not
    # change either hash profile or either existing wire encoding.
    assert reference.critical_hash == (
        "e4ea0917727ec0bb74678b42d3d5da022e806c0df0cb559a0e0e52ed1ab15983"
    )
    assert reference.full_hash == (
        "c76baf576a21e58385c108c4447205e4f2136d93d810355bc83c90cf369d9fc7"
    )
    expected_wire_hash = (
        "d4c5f6e7d28401f92ea869fe189247e7ca437cd80ee82f73f7af80d4a1003263"
        if dictionary_mode
        else "8ea502f3ef73d2fd6580feaa785506149a170903e453d26f26d8b04754812964"
    )
    assert sha256(wire.encode()).hexdigest() == expected_wire_hash
    assert restored.to_wire(codebook) == wire == context.compact(codebook)
    assert (
        CompactionShield.verify_integrity(reference, restored)["classification"]
        == "EXACT_EQUIVALENT"
    )


def test_saved_reference_rejects_invariant_removed_from_live_context():
    context = populated_context()
    reference = context.export_packet()
    saved_hash = reference.critical_hash
    saved_wire = reference.to_wire()
    context.invariants.clear()
    candidate = context.export_packet()
    assert reference.critical_hash == saved_hash
    assert reference.to_wire() == saved_wire
    assert CompactionShield.verify_integrity(reference, candidate)["is_safe"] is False
    assert CompactionShield.verify_integrity(saved_hash, candidate)["is_safe"] is False
