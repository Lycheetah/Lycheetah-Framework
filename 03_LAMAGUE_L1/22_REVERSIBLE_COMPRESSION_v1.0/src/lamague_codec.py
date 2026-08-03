
"""LAMAGUE reversible semantic packet codec.

This codec compresses a declared structured semantic packet. It does not infer
the packet from unrestricted natural language.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from typing import Any, Iterable

SCHEMA = "LAMAGUE-SEMANTIC-PACKET-1"
CODEBOOK_SCHEMA = "LAMAGUE-CODEBOOK-1"
VALID_RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_OPS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
RISK_ENCODE = {"LOW": "L", "MEDIUM": "M", "HIGH": "H", "CRITICAL": "C"}
RISK_DECODE = {value: key for key, value in RISK_ENCODE.items()}
CONSENT_ENCODE = {"REVOCABLE": "R", "IRREVOCABLE": "I", "NONE": "N"}
CONSENT_DECODE = {value: key for key, value in CONSENT_ENCODE.items()}

REQUIRED_FIELDS = [
    "schema",
    "id",
    "purpose",
    "claim",
    "risk",
    "operations",
    "evidence",
    "unknowns",
    "invariants",
    "authority",
    "participants",
    "affectedParties",
    "dissent",
    "valueFlow",
    "recovery",
    "horizon",
    "yield",
]

CRITICAL_FIELDS = [
    "purpose",
    "claim",
    "unknowns",
    "invariants",
    "authority",
    "participants",
    "affectedParties",
    "dissent",
    "valueFlow",
    "recovery",
]


class CodecError(ValueError):
    """Fail-closed codec error."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _require_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise CodecError(f"{name} must be a non-empty string")
    return value


def _require_string_list(name: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise CodecError(f"{name} must be a list")
    return [_require_string(f"{name}[{index}]", item) for index, item in enumerate(value)]


def validate_packet(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise CodecError("packet must be an object")

    missing = [field for field in REQUIRED_FIELDS if field not in packet]
    if missing:
        raise CodecError(f"missing required fields: {', '.join(missing)}")

    extra = sorted(set(packet) - set(REQUIRED_FIELDS))
    if extra:
        raise CodecError(f"unknown packet fields: {', '.join(extra)}")

    if packet["schema"] != SCHEMA:
        raise CodecError(f"schema must equal {SCHEMA}")

    _require_string("id", packet["id"])
    _require_string("purpose", packet["purpose"])
    _require_string("claim", packet["claim"])
    _require_string("horizon", packet["horizon"])
    _require_string("yield", packet["yield"])

    if packet["risk"] not in VALID_RISKS:
        raise CodecError(f"risk must be one of {sorted(VALID_RISKS)}")

    operations = _require_string_list("operations", packet["operations"])
    for operation in operations:
        if len(operation) != 1 or operation not in VALID_OPS:
            raise CodecError(f"invalid operation {operation!r}")

    for field in ("evidence", "unknowns", "invariants", "authority", "dissent", "valueFlow", "recovery"):
        if not isinstance(packet[field], list):
            raise CodecError(f"{field} must be a list")

    for index, item in enumerate(packet["evidence"]):
        if not isinstance(item, dict) or set(item) != {"id", "text", "provenance"}:
            raise CodecError(f"evidence[{index}] has invalid shape")
        for key in ("id", "text", "provenance"):
            _require_string(f"evidence[{index}].{key}", item[key])

    for index, item in enumerate(packet["unknowns"]):
        if not isinstance(item, dict) or set(item) != {"id", "protected", "requiredFor"}:
            raise CodecError(f"unknowns[{index}] has invalid shape")
        _require_string(f"unknowns[{index}].id", item["id"])
        if not isinstance(item["protected"], bool):
            raise CodecError(f"unknowns[{index}].protected must be boolean")
        _require_string(f"unknowns[{index}].requiredFor", item["requiredFor"])

    for field in ("invariants", "recovery"):
        for index, item in enumerate(packet[field]):
            if not isinstance(item, dict) or set(item) != {"id", "text"}:
                raise CodecError(f"{field}[{index}] has invalid shape")
            _require_string(f"{field}[{index}].id", item["id"])
            _require_string(f"{field}[{index}].text", item["text"])

    for index, item in enumerate(packet["authority"]):
        if not isinstance(item, dict) or set(item) != {"id", "scope", "text"}:
            raise CodecError(f"authority[{index}] has invalid shape")
        for key in ("id", "scope", "text"):
            _require_string(f"authority[{index}].{key}", item[key])

    packet["participants"] = _require_string_list("participants", packet["participants"])
    packet["affectedParties"] = _require_string_list("affectedParties", packet["affectedParties"])

    for index, item in enumerate(packet["dissent"]):
        if not isinstance(item, dict) or set(item) != {"party", "position"}:
            raise CodecError(f"dissent[{index}] has invalid shape")
        _require_string(f"dissent[{index}].party", item["party"])
        _require_string(f"dissent[{index}].position", item["position"])

    for index, item in enumerate(packet["valueFlow"]):
        if not isinstance(item, dict) or set(item) != {"source", "recipient", "consent", "kind"}:
            raise CodecError(f"valueFlow[{index}] has invalid shape")
        for key in ("source", "recipient", "consent", "kind"):
            _require_string(f"valueFlow[{index}].{key}", item[key])

    return packet


def safety_violations(packet: dict[str, Any]) -> list[str]:
    validate_packet(copy.deepcopy(packet))
    operations = set(packet["operations"])
    violations = []

    if packet["unknowns"] and "U" not in operations:
        violations.append("UNKNOWN_WITHOUT_U")
    if (packet["authority"] or packet["affectedParties"]) and "G" not in operations:
        violations.append("AUTHORITY_OR_AFFECTED_WITHOUT_G")
    if packet["dissent"] and "V" not in operations:
        violations.append("DISSENT_WITHOUT_V")
    if packet["recovery"] and "F" not in operations:
        violations.append("RECOVERY_WITHOUT_FOLD")
    if packet["yield"] and "Y" not in operations:
        violations.append("YIELD_WITHOUT_Y")
    if packet["valueFlow"] and not packet["affectedParties"]:
        violations.append("VALUE_FLOW_WITHOUT_AFFECTED_PARTY")
    if any(item["protected"] for item in packet["unknowns"]) and not packet["recovery"]:
        violations.append("PROTECTED_UNKNOWN_WITHOUT_RECOVERY")

    return violations


def critical_projection(packet: dict[str, Any]) -> dict[str, Any]:
    validate_packet(copy.deepcopy(packet))
    return {field: packet[field] for field in CRITICAL_FIELDS}


def full_hash(packet: dict[str, Any]) -> str:
    validate_packet(copy.deepcopy(packet))
    return sha256_json(packet)


def critical_hash(packet: dict[str, Any]) -> str:
    return sha256_json(critical_projection(packet))


def _compact_object(packet: dict[str, Any]) -> dict[str, Any]:
    validate_packet(copy.deepcopy(packet))
    return {
        "i": packet["id"],
        "p": packet["purpose"],
        "c": packet["claim"],
        "r": RISK_ENCODE[packet["risk"]],
        "o": "".join(packet["operations"]),
        "e": [[item["id"], item["text"], item["provenance"]] for item in packet["evidence"]],
        "u": [[item["id"], 1 if item["protected"] else 0, item["requiredFor"]] for item in packet["unknowns"]],
        "n": [[item["id"], item["text"]] for item in packet["invariants"]],
        "a": [[item["id"], item["scope"], item["text"]] for item in packet["authority"]],
        "t": packet["participants"],
        "f": packet["affectedParties"],
        "d": [[item["party"], item["position"]] for item in packet["dissent"]],
        "v": [
            [
                item["source"],
                item["recipient"],
                CONSENT_ENCODE.get(item["consent"], item["consent"]),
                item["kind"],
            ]
            for item in packet["valueFlow"]
        ],
        "x": [[item["id"], item["text"]] for item in packet["recovery"]],
        "h": packet["horizon"],
        "y": packet["yield"],
    }


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)


def build_codebook(training_packets: list[dict[str, Any]], max_entries: int = 20) -> dict[str, Any]:
    if max_entries < 0:
        raise CodecError("max_entries must be non-negative")

    counter = Counter()
    for packet in training_packets:
        counter.update(_strings(_compact_object(packet)))

    candidates = []
    for string, count in counter.items():
        if count < 2 or len(string) < 5:
            continue
        raw_size = len(json.dumps(string, ensure_ascii=False).encode("utf-8"))
        estimated_net_saving = (raw_size - 2) * count - (raw_size + 1)
        if estimated_net_saving > 0:
            candidates.append((estimated_net_saving, count, string))

    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    entries = [string for _, _, string in candidates[:max_entries]]
    return {"schema": CODEBOOK_SCHEMA, "entries": entries}


def validate_codebook(codebook: Any) -> dict[str, Any]:
    if not isinstance(codebook, dict) or set(codebook) != {"schema", "entries"}:
        raise CodecError("codebook has invalid shape")
    if codebook["schema"] != CODEBOOK_SCHEMA:
        raise CodecError(f"codebook schema must equal {CODEBOOK_SCHEMA}")
    entries = _require_string_list("codebook.entries", codebook["entries"])
    if len(entries) != len(set(entries)):
        raise CodecError("codebook entries must be unique")
    return codebook


def _reference_encoder(codebook: dict[str, Any]):
    validate_codebook(copy.deepcopy(codebook))
    index = {string: number for number, string in enumerate(codebook["entries"])}

    def encode_string(value: str) -> str | int:
        return index.get(value, value)

    return encode_string


def _reference_decoder(codebook: dict[str, Any]):
    validate_codebook(copy.deepcopy(codebook))
    entries = codebook["entries"]

    def decode_string(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            if 0 <= value < len(entries):
                return entries[value]
            raise CodecError(f"dictionary reference {value} is out of range")
        raise CodecError("expected literal string or dictionary reference")

    return decode_string


def _compact_with_dictionary(packet: dict[str, Any], codebook: dict[str, Any]) -> dict[str, Any]:
    ref = _reference_encoder(codebook)
    obj = _compact_object(packet)
    return {
        "i": ref(obj["i"]),
        "p": ref(obj["p"]),
        "c": ref(obj["c"]),
        "r": ref(obj["r"]),
        "o": ref(obj["o"]),
        "e": [[ref(a), ref(b), ref(c)] for a, b, c in obj["e"]],
        "u": [[ref(a), b, ref(c)] for a, b, c in obj["u"]],
        "n": [[ref(a), ref(b)] for a, b in obj["n"]],
        "a": [[ref(a), ref(b), ref(c)] for a, b, c in obj["a"]],
        "t": [ref(value) for value in obj["t"]],
        "f": [ref(value) for value in obj["f"]],
        "d": [[ref(a), ref(b)] for a, b in obj["d"]],
        "v": [[ref(a), ref(b), ref(c), ref(d)] for a, b, c, d in obj["v"]],
        "x": [[ref(a), ref(b)] for a, b in obj["x"]],
        "h": ref(obj["h"]),
        "y": ref(obj["y"]),
    }


def encode(packet: dict[str, Any], codebook: dict[str, Any] | None = None) -> str:
    packet = validate_packet(copy.deepcopy(packet))
    violations = safety_violations(packet)
    if violations:
        raise CodecError(f"packet violates semantic safety rules: {', '.join(violations)}")

    if codebook is None:
        return "L1" + json.dumps(_compact_object(packet), ensure_ascii=False, separators=(",", ":"))

    return "L1D" + json.dumps(
        _compact_with_dictionary(packet, codebook),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _expand_object(obj: Any, codebook: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise CodecError("compressed body must be an object")

    expected = {"i", "p", "c", "r", "o", "e", "u", "n", "a", "t", "f", "d", "v", "x", "h", "y"}
    if set(obj) != expected:
        missing = sorted(expected - set(obj))
        extra = sorted(set(obj) - expected)
        raise CodecError(f"compressed fields differ; missing={missing}, extra={extra}")

    if codebook is None:
        def string(value: Any) -> str:
            return _require_string("compressed string", value)
    else:
        string = _reference_decoder(codebook)

    risk_code = string(obj["r"])
    if risk_code not in RISK_DECODE:
        raise CodecError(f"unknown compact risk code {risk_code!r}")

    operations_string = string(obj["o"])
    operations = list(operations_string)
    for operation in operations:
        if operation not in VALID_OPS:
            raise CodecError(f"unknown compact operation {operation!r}")

    try:
        evidence = [
            {"id": string(item[0]), "text": string(item[1]), "provenance": string(item[2])}
            for item in obj["e"]
        ]
        unknowns = [
            {
                "id": string(item[0]),
                "protected": bool(item[1]) if item[1] in (0, 1, False, True) else (_ for _ in ()).throw(CodecError("invalid protected flag")),
                "requiredFor": string(item[2]),
            }
            for item in obj["u"]
        ]
        invariants = [{"id": string(item[0]), "text": string(item[1])} for item in obj["n"]]
        authority = [
            {"id": string(item[0]), "scope": string(item[1]), "text": string(item[2])}
            for item in obj["a"]
        ]
        participants = [string(value) for value in obj["t"]]
        affected = [string(value) for value in obj["f"]]
        dissent = [{"party": string(item[0]), "position": string(item[1])} for item in obj["d"]]
        value_flow = [
            {
                "source": string(item[0]),
                "recipient": string(item[1]),
                "consent": CONSENT_DECODE.get(string(item[2]), string(item[2])),
                "kind": string(item[3]),
            }
            for item in obj["v"]
        ]
        recovery = [{"id": string(item[0]), "text": string(item[1])} for item in obj["x"]]
    except (IndexError, TypeError) as error:
        raise CodecError(f"invalid compact array shape: {error}") from error

    packet = {
        "schema": SCHEMA,
        "id": string(obj["i"]),
        "purpose": string(obj["p"]),
        "claim": string(obj["c"]),
        "risk": RISK_DECODE[risk_code],
        "operations": operations,
        "evidence": evidence,
        "unknowns": unknowns,
        "invariants": invariants,
        "authority": authority,
        "participants": participants,
        "affectedParties": affected,
        "dissent": dissent,
        "valueFlow": value_flow,
        "recovery": recovery,
        "horizon": string(obj["h"]),
        "yield": string(obj["y"]),
    }

    validate_packet(packet)
    violations = safety_violations(packet)
    if violations:
        raise CodecError(f"decoded packet violates semantic safety rules: {', '.join(violations)}")
    return packet


def decode(source: str, codebook: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(source, str):
        raise CodecError("source must be a string")

    if source.startswith("L1D"):
        if codebook is None:
            raise CodecError("L1D source requires a codebook")
        body = source[3:]
        active_codebook = validate_codebook(copy.deepcopy(codebook))
    elif source.startswith("L1"):
        if codebook is not None:
            active_codebook = None
        else:
            active_codebook = None
        body = source[2:]
    else:
        raise CodecError("source must begin with L1 or L1D")

    try:
        obj = json.loads(body)
    except json.JSONDecodeError as error:
        raise CodecError(f"invalid compressed JSON: {error.msg}") from error

    return _expand_object(obj, active_codebook)


def classify(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    try:
        reference = validate_packet(copy.deepcopy(reference))
        candidate = validate_packet(copy.deepcopy(candidate))
    except CodecError as error:
        return {"classification": "UNDECODABLE", "reason": str(error)}

    reference_violations = set(safety_violations(reference))
    candidate_violations = set(safety_violations(candidate))
    new_violations = sorted(candidate_violations - reference_violations)
    if new_violations:
        return {
            "classification": "UNSAFE_COLLAPSE",
            "reason": "candidate introduced semantic safety violations",
            "violations": new_violations,
        }

    if full_hash(reference) == full_hash(candidate):
        return {"classification": "EXACT_EQUIVALENT", "reason": "full canonical hash matches"}

    protected_loss = []
    for field in ("unknowns", "authority", "participants", "affectedParties", "dissent", "valueFlow", "recovery"):
        if len(candidate[field]) < len(reference[field]):
            protected_loss.append(field)

    if any(item["protected"] for item in reference["unknowns"]) and not all(
        item["protected"] for item in candidate["unknowns"]
    ):
        protected_loss.append("unknown_protection")

    if protected_loss:
        return {
            "classification": "UNSAFE_COLLAPSE",
            "reason": "protected meaning disappeared or weakened",
            "fields": sorted(set(protected_loss)),
        }

    if reference["purpose"] != candidate["purpose"] or reference["claim"] != candidate["claim"]:
        return {"classification": "DIVERGENT", "reason": "purpose or claim changed"}

    if reference["invariants"] != candidate["invariants"]:
        return {"classification": "DIVERGENT", "reason": "invariant content changed"}

    if critical_hash(reference) == critical_hash(candidate):
        return {
            "classification": "PARTIAL_EQUIVALENT",
            "reason": "critical fields match while non-critical content differs",
        }

    return {"classification": "DIVERGENT", "reason": "critical semantic hash changed"}
