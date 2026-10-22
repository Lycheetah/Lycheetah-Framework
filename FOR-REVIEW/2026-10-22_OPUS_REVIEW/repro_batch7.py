"""Batch 7 (RV08) probes: exact codec and consent preservation.

    python3 repro_batch7.py <tree-root> > out.jsonl

Loads the maintained codec (lycheetah/compaction/codec.py) and the frozen research
codec (03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/src/lamague_codec.py) from
<tree-root> by file path, so neither package import can pick up the wrong tree.
Each line is one probe against one codec. Nothing here writes to disk.
"""

import copy
import importlib.util
import json
import sys

sys.dont_write_bytecode = True  # never leave bytecode beside a sealed manifest
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
FROZEN = ROOT / "03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODECS = {
    "maintained": load("maintained_codec", ROOT / "lycheetah/compaction/codec.py"),
    "frozen": load("frozen_codec", FROZEN / "src/lamague_codec.py"),
}
CORPUS = [json.loads(line) for line in (FROZEN / "corpus/packets.jsonl").read_text().splitlines() if line]
CODEBOOK = json.loads((FROZEN / "corpus/codebook.json").read_text())


def emit(probe, codec, **row):
    print(json.dumps({"id": probe, "codec": codec, **row}, sort_keys=True, ensure_ascii=True))


def attempt(fn, *args):
    try:
        return "ok", fn(*args)
    except Exception as error:  # the probe reports the type, it does not judge it
        return type(error).__name__, str(error)[:90]


def with_flow(packet, consent):
    packet = copy.deepcopy(packet)
    packet["valueFlow"] = [{"source": "org", "recipient": "user", "consent": consent, "kind": "data"}]
    if not packet["affectedParties"]:
        packet["affectedParties"] = ["user"]
        if "G" not in packet["operations"]:
            packet["operations"] = packet["operations"] + ["G"]
    return packet


emit("ENV", "-", root=str(ROOT), python=sys.version.split()[0],
     files={k: v.__file__.replace(str(ROOT) + "/", "") for k, v in CODECS.items()})
BASE = next(p for p in CORPUS if CODECS["frozen"].safety_violations(p) == [])
emit("K0", "-", what="corpus", packets=len(CORPUS), codebook_entries=len(CODEBOOK["entries"]),
     consent_values=sorted({f["consent"] for p in CORPUS for f in p["valueFlow"]}))

for name, codec in CODECS.items():
    # K1: the reserved literals R, I, N in both wire modes.
    for literal in ("R", "I", "N"):
        for mode, book in (("L1", None), ("L1D", CODEBOOK)):
            packet = with_flow(BASE, literal)
            status, wire = attempt(codec.encode, packet, book)
            if status != "ok":
                emit("K1", name, literal=literal, mode=mode, encode=status, detail=wire)
                continue
            status, back = attempt(codec.decode, wire, book)
            emit("K1", name, literal=literal, mode=mode, encode="ok", decode=status,
                 consent_after=back["valueFlow"][0]["consent"] if status == "ok" else back,
                 full_hash_kept=status == "ok" and codec.full_hash(back) == codec.full_hash(packet),
                 critical_hash_kept=status == "ok" and codec.critical_hash(back) == codec.critical_hash(packet))

    # K2: every other consent spelling must come back exactly, in both modes.
    sweep = ["REVOCABLE", "IRREVOCABLE", "NONE", "revocable", "r", "R ", " R", "RI", "N/A",
             "Revocable", "NONE ", "ÑONE", "撤回可能", "REVOCABLE\u200b"]
    lost = []
    for consent in sweep:
        for mode, book in (("L1", None), ("L1D", CODEBOOK), ("L1D+", {"schema": CODEBOOK["schema"], "entries": ["R", "REVOCABLE", consent] if consent not in ("R", "REVOCABLE") else ["R", "REVOCABLE"]})):
            packet = with_flow(BASE, consent)
            status, wire = attempt(codec.encode, packet, book)
            status2, back = attempt(codec.decode, wire, book) if status == "ok" else (status, None)
            if status2 != "ok" or back != packet:
                lost.append([consent, mode, status2])
    emit("K2", name, values=len(sweep), modes=3, changed_or_failed=lost)

    # K3: the corpus round trips in both modes.
    bad = [i for i, p in enumerate(CORPUS) if codec.decode(codec.encode(p)) != p
           or codec.decode(codec.encode(p, CODEBOOK), CODEBOOK) != p]
    emit("K3", name, packets=len(CORPUS), roundtrip_failures=bad)

    # W: malformed or non-canonical wire. "accepted" means decode returned a packet.
    wire = codec.encode(BASE)
    body = wire[2:]
    cases = {
        "W1_dup_key_first": "L1" + '{"c":"INJECTED",' + body[1:],
        "W2_dup_key_last": "L1" + body[:-1] + ',"c":"INJECTED"}',
        "W3_extra_array_element": "L1" + body.replace('"e":[[', '"e":[["E-extra-0",', 1).replace(
            '"e":[["E-extra-0",', '"e":[[', 1).replace('"x":[[', '"x":[["SMUGGLED",', 0),
        "W4_whitespace": "L1 " + body + "\n",
        "W5_keys_reordered": "L1" + json.dumps(dict(reversed(list(json.loads(body).items()))),
                                               ensure_ascii=False, separators=(",", ":")),
        "W6_protected_float": None,
        "W7_protected_true": None,
        "W8_l1d_literal_for_entry": None,
    }
    obj = json.loads(body)
    if obj["u"]:
        alt = copy.deepcopy(obj); alt["u"][0][1] = float(alt["u"][0][1])
        cases["W6_protected_float"] = "L1" + json.dumps(alt, ensure_ascii=False, separators=(",", ":"))
        alt = copy.deepcopy(obj); alt["u"][0][1] = bool(alt["u"][0][1])
        cases["W7_protected_true"] = "L1" + json.dumps(alt, ensure_ascii=False, separators=(",", ":"))
    alt = copy.deepcopy(obj)
    for key in ("e", "n", "x", "a", "d"):
        if alt[key]:
            alt[key][0] = alt[key][0] + ["SMUGGLED"]
            cases["W3_extra_array_element"] = "L1" + json.dumps(alt, ensure_ascii=False, separators=(",", ":"))
            cases["W3_field"] = key
            break
    dwire = codec.encode(BASE, CODEBOOK)
    dobj = json.loads(dwire[3:])
    literalised = copy.deepcopy(dobj)
    for key, value in literalised.items():
        if isinstance(value, int) and not isinstance(value, bool):
            literalised[key] = CODEBOOK["entries"][value]
            cases["W8_l1d_literal_for_entry"] = "L1D" + json.dumps(literalised, ensure_ascii=False, separators=(",", ":"))
            break
    field = cases.pop("W3_field", None)
    for case, source in cases.items():
        if source is None:
            emit(case, name, status="not applicable to the base packet")
            continue
        book = CODEBOOK if source.startswith("L1D") else None
        status, back = attempt(codec.decode, source, book)
        row = {"status": "accepted" if status == "ok" else status}
        if status == "ok":
            row["claim"] = back["claim"]
            row["equals_base"] = back == BASE
            row["reencodes_to_source"] = codec.encode(back, book) == source
        if case.startswith("W3"):
            row["field"] = field
        emit(case, name, **row)

    # U: a string Python holds but UTF-8 cannot carry.
    lone = copy.deepcopy(BASE)
    lone["claim"] = "Dry run \ud800 only"
    emit("U1", name, validate=attempt(codec.validate_packet, copy.deepcopy(lone))[0],
         encode=attempt(codec.encode, lone)[0], full_hash=attempt(codec.full_hash, lone)[0],
         classify=attempt(codec.classify, lone, lone)[0])
