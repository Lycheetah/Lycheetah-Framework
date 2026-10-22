"""A compact wire decodes only when it is the exact wire encode emits for its packet."""

import json
import types
from pathlib import Path

import pytest

from lycheetah.compaction.codec import (
    CodecError,
    classify,
    decode,
    encode,
    full_hash,
    validate_packet,
)

FROZEN = Path(__file__).resolve().parents[1] / "03_LAMAGUE_L1" / "22_REVERSIBLE_COMPRESSION_v1.0"
CORPUS = [
    json.loads(line)
    for line in (FROZEN / "corpus" / "packets.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
SHIPPED_CODEBOOK = json.loads((FROZEN / "corpus" / "codebook.json").read_text(encoding="utf-8"))

PACKET = {
    "schema": "LAMAGUE-SEMANTIC-PACKET-1",
    "id": "wire-packet",
    "purpose": "Migrate a synthetic ledger",
    "claim": "Dry run only",
    "risk": "HIGH",
    "operations": ["G", "U", "V", "F", "Y"],
    "evidence": [{"id": "E1", "text": "Plan reviewed", "provenance": "reviewer"}],
    "unknowns": [{"id": "U1", "protected": True, "requiredFor": "cutover"}],
    "invariants": [{"id": "I1", "text": "no deletes"}],
    "authority": [{"id": "A1", "scope": "db:write", "text": "Owner approval"}],
    "participants": ["worker", "reviewer"],
    "affectedParties": ["customers"],
    "dissent": [{"party": "reviewer", "position": "wait for backup"}],
    "valueFlow": [
        {"source": "customers", "recipient": "ledger", "consent": "REVOCABLE", "kind": "data"}
    ],
    "recovery": [{"id": "R1", "text": "Restore the snapshot"}],
    "horizon": "this week",
    "yield": "halt",
}
WIRE = encode(PACKET)
CODEBOOK = {"schema": "LAMAGUE-CODEBOOK-1", "entries": ["Migrate a synthetic ledger"]}


def _body():
    return json.loads(WIRE[2:])


def _wire(obj, **options):
    return "L1" + json.dumps(obj, ensure_ascii=False, separators=(",", ":"), **options)


def _with_flag(value):
    obj = _body()
    obj["u"][0][1] = value
    return _wire(obj)


def _with_extra_item():
    obj = _body()
    obj["e"][0].append("unseen")
    return _wire(obj)


def _frozen_codec():
    # Executed from source so the archive gains no __pycache__ beside its manifest.
    path = FROZEN / "src" / "lamague_codec.py"
    module = types.ModuleType("frozen_lamague_codec")
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


@pytest.mark.parametrize(
    "wire, message",
    [
        ('L1{"c":"Live run",' + WIRE[3:], "repeats key 'c'"),
        (WIRE[:-1] + ',"c":"Live run"}', "repeats key 'c'"),
        (_with_extra_item(), "not the canonical encoding"),
        ("L1" + json.dumps(_body(), ensure_ascii=False), "not the canonical encoding"),
        (WIRE + " ", "not the canonical encoding"),
        (_wire(dict(reversed(_body().items()))), "not the canonical encoding"),
        (_with_flag(1.0), "not the canonical encoding"),
        (_with_flag(True), "not the canonical encoding"),
        (WIRE.replace("Dry run only", "Dry run \\u006fnly"), "not the canonical encoding"),
    ],
    ids=["repeated_key_first", "repeated_key_last", "extra_array_item", "spaced_json",
         "trailing_space", "reordered_keys", "flag_as_float", "flag_as_true", "escaped_letter"],
)
def test_a_wire_other_than_the_canonical_one_is_refused(wire, message):
    with pytest.raises(CodecError, match=message):
        decode(wire)


def test_a_codebook_string_written_out_in_full_is_refused():
    wire = encode(PACKET, CODEBOOK)
    obj = json.loads(wire[3:])
    assert obj["p"] == 0
    obj["p"] = PACKET["purpose"]
    with pytest.raises(CodecError, match="not the canonical encoding"):
        decode("L1D" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")), CODEBOOK)
    assert decode(wire, CODEBOOK) == PACKET


def test_canonical_wires_still_decode():
    assert decode(WIRE) == PACKET
    assert decode(WIRE, CODEBOOK) == PACKET
    unprotected = {**PACKET, "unknowns": [{**PACKET["unknowns"][0], "protected": False}]}
    assert decode(encode(unprotected)) == unprotected
    accented = {**PACKET, "claim": "Prüfung nur, 試験のみ"}
    assert decode(encode(accented)) == accented
    assert decode(encode(accented, CODEBOOK), CODEBOOK) == accented


@pytest.mark.parametrize("mode", ["L1", "L1D"])
def test_corpus_wires_from_the_v1_encoder_decode_unchanged(mode):
    frozen = _frozen_codec()
    codebook = SHIPPED_CODEBOOK if mode == "L1D" else None
    assert len(CORPUS) == 36
    for packet in CORPUS:
        wire = frozen.encode(packet, codebook)
        assert wire.startswith(mode + "{")
        assert encode(packet, codebook) == wire
        assert decode(wire, codebook) == packet


def test_text_that_is_not_valid_unicode_is_a_codec_error():
    packet = {**PACKET, "claim": "Dry run \ud800"}
    with pytest.raises(CodecError, match="claim must be valid Unicode text"):
        validate_packet(packet)
    with pytest.raises(CodecError, match="valid Unicode"):
        encode(packet)
    with pytest.raises(CodecError, match="valid Unicode"):
        full_hash(packet)
    assert classify(PACKET, packet)["classification"] == "UNDECODABLE"
