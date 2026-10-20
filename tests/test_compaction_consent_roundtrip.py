"""The protected consent field must be reversible over admitted input values."""

import pytest

from lycheetah.compaction import AgentStatePacket, CompactionShield
from lycheetah.compaction.codec import CodecError, build_codebook, critical_hash


def packet(consent):
    return AgentStatePacket(
        id="consent-fixture", purpose="retain the declared permission", claim="local fixture",
        affected_parties=["reader"],
        value_flow=[{"source":"owner","recipient":"reader","consent":consent,"kind":"copy"}],
    )


@pytest.mark.parametrize("consent", ["R", "I", "N"])
def test_reserved_wire_codes_are_rejected_as_input_consent(consent):
    with pytest.raises(CodecError, match="consent"):
        CompactionShield.compact(packet(consent))


@pytest.mark.parametrize("consent", ["REVOCABLE", "IRREVOCABLE", "NONE", "OTHER"])
@pytest.mark.parametrize("dictionary", [False, True])
def test_admitted_consent_preserves_full_packet_and_protected_hash(consent, dictionary):
    original = packet(consent).to_dict()
    book = build_codebook([original, original]) if dictionary else None
    restored = CompactionShield.decompact(CompactionShield.compact(original, book), book).to_dict()
    assert restored == original
    assert critical_hash(restored) == critical_hash(original)
