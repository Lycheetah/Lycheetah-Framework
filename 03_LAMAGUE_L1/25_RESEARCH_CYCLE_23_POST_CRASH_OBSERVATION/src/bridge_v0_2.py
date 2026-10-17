#!/usr/bin/env python3
"""LAMAGUE BRIDGE 0.2 reference: typed intent -> no-clobber file-copy plan.

Dry-run by default. Execution requires --approve-plan with the exact SHA-256
of the compiled plan. This is a local reference prototype, not a security
boundary against a hostile local administrator or compromised host.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

PROTOCOL = "lamague.bridge.filecopy"
VERSION = "0.2"
PRESENCE_STATES = {"PRESENT", "EXPLICITLY_ABSENT", "UNKNOWN", "NOT_APPLICABLE", "WITHHELD"}
REQUIRED_PRESENCE = {
    "purpose", "authority", "invariants", "protected_unknowns", "recovery",
    "participants", "affected_parties", "action_graph", "preconditions", "postconditions", "effect_contract",
}
REQUIRED_CAPABILITIES = {"file.read", "file.hash", "file.copy_no_clobber", "receipt.emit"}

# BRIDGE v0.2 makes the executable outcome explicit. The values are intentionally
# narrow: this reference executor only copies preselected files without clobbering.
EFFECT_CONTRACT_KEYS = {
    "requested_outcome", "source_effect", "destination_effect", "overwrite_policy",
    "source_deletion_policy", "on_collision", "on_failure", "verification",
}
EXPECTED_EFFECT_CONTRACT = {
    "requested_outcome": "COPY_SELECTED_FILES",
    "source_effect": "PRESERVE",
    "destination_effect": "CREATE_ONLY_IF_ABSENT",
    "overwrite_policy": "FORBID",
    "source_deletion_policy": "FORBID",
    "on_collision": "STOP_WITHOUT_OVERWRITE",
    "on_failure": "STOP_AND_REPORT_PARTIAL_RESULTS",
    "verification": "SHA256_DESTINATION_EQUALS_SOURCE_AND_SOURCE_PRESERVED",
}
PURPOSE_CONFLICT_PATTERNS = [
    # Known affirmative source mutation/removal cues.
    re.compile(r"\b(?:delet(?:e|es|ed|ing)|remov(?:e|es|ed|ing)|eras(?:e|es|ed|ing)|wip(?:e|es|ed|ing)|destroy(?:s|ed|ing)?|discard(?:s|ed|ing)?|clean\s+up|mov(?:e|es|ed|ing)|relocat(?:e|es|ed|ing)|renam(?:e|es|ed|ing)|will\s+be\s+gone|will\s+disappear|will\s+no\s+longer\s+(?:exist|be\s+present)|(?:is|are|become|becomes|became)\s+(?:gone|absent|missing))\b", re.I),
    # Common euphemisms for destroying the source copy or replacing it with the archive.
    re.compile(r"\b(?:be|become|remain|leave)\s+(?:as\s+)?the\s+only\s+(?:surviving|remaining|existing)\s+copy\b", re.I),
    re.compile(r"\b(?:empty|clear)\s+(?:the\s+)?(?:source|working)\s+(?:tree|folder|directory)\b", re.I),
    re.compile(r"\b(?:source|working)\s+(?:tree|folder|directory)\s+(?:will\s+be\s+)?(?:empty|cleared)\b", re.I),
    re.compile(r"\b(?:overwrite|clobber|replace)\b", re.I),
]
PURPOSE_TARGET_PATTERN = re.compile(
    r"\b(?:originals?|source(?:\s+(?:files?|data|documents?|folder|directory|tree))?|"
    r"working\s+(?:files?|folder|directory|tree|copy|set)|(?:the|these|those|selected)?\s*(?:files?|documents?|copies?|archive|working\s+set))\b",
    re.I,
)
EXISTING_TARGET_PATTERN = re.compile(r"\b(?:existing|current|destination|archive|files?|copies?|working\s+copy)\b", re.I)
NEGATION_AT_END = re.compile(r"\b(?:no|not|never|without|avoid|refuse|refuses|refused|refusing|prevent|prevents|preventing|forbid|forbids|forbidden|don't|dont|doesn't|doesnt|won't|wont|mustn't|mustnt|shouldn't|shouldnt)\b(?:\W+\w+){0,3}\W*$", re.I)
NEGATION_BEFORE_PASSIVE = re.compile(r"\b(?:not|never|no|without|avoid|don't|dont|doesn't|doesnt|won't|wont|mustn't|mustnt|shouldn't|shouldnt)\b(?:\W+\w+){0,2}\W+(?:be\W+)?$", re.I)


def _clause_is_negated_before(text: str, start: int) -> bool:
    prefix = text[:start]
    # Limit negation scope to the latest clause marker to avoid letting a prior
    # negation suppress a later independent destructive statement.
    prefix = re.split(r"[.;!?\n]", prefix)[-1]
    return bool(NEGATION_AT_END.search(prefix))


def purpose_conflicts_with_copy_contract(packet: dict[str, Any]) -> list[str]:
    """Return known positive destructive/overwrite cues conflicting with copy-only effects.

    This is a narrow contradiction tripwire over explicitly enumerated English cues.
    It cannot prove arbitrary prose agrees with the typed contract; unknown phrasing
    remains a human-review question. No text is rewritten or silently reinterpreted.
    """
    fields: list[tuple[str, Any]] = [("purpose", packet.get("purpose", ""))]
    for field_name in ("invariants", "preconditions", "postconditions", "recovery"):
        if isinstance(packet.get(field_name), list):
            fields.extend((f"{field_name}[{i}]", value) for i, value in enumerate(packet[field_name]))
    findings = []
    for field_name, value in fields:
        if not isinstance(value, str):
            continue
        # Split into clauses; each clause is judged independently.
        for clause in re.split(r"[.;!?\n]", value):
            if not clause.strip():
                continue
            verbs = [(pattern, match) for pattern in PURPOSE_CONFLICT_PATTERNS for match in pattern.finditer(clause)]
            for pattern, match in verbs:
                verb = match.group(0).casefold()
                after = clause[match.end():]
                before = clause[:match.start()]
                target = bool(PURPOSE_TARGET_PATTERN.search(after) or PURPOSE_TARGET_PATTERN.search(before))
                overwrite = verb in {"overwrite", "clobber", "replace"}
                if overwrite:
                    target = bool(EXISTING_TARGET_PATTERN.search(after) or EXISTING_TARGET_PATTERN.search(before))
                if not target:
                    continue
                if _clause_is_negated_before(clause, match.start()):
                    continue
                # Handle passive negatives such as "source files must not be deleted".
                if re.search(r"\b(?:must|should|will|shall|may)\s+not\b(?:\W+\w+){0,2}\W*$", before, re.I):
                    continue
                findings.append(f"{field_name}: affirmative {verb!r} cue conflicts with the copy-only effect contract")
                break
            if findings and findings[-1].startswith(field_name + ":"):
                continue
    return findings


def validate_effect_contract(contract: Any, constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(contract, dict) or set(contract) != EFFECT_CONTRACT_KEYS:
        got = set(contract) if isinstance(contract, dict) else set()
        raise BridgeError(f"effect_contract field shape mismatch; missing={sorted(EFFECT_CONTRACT_KEYS - got)}, extra={sorted(got - EFFECT_CONTRACT_KEYS)}")
    if contract != EXPECTED_EFFECT_CONTRACT:
        disagreements = {key: {"expected": EXPECTED_EFFECT_CONTRACT[key], "actual": contract.get(key)}
                         for key in EFFECT_CONTRACT_KEYS if contract.get(key) != EXPECTED_EFFECT_CONTRACT[key]}
        raise BridgeError(f"effect_contract contradicts this executor's limited capability contract: {disagreements}")
    if constraints is not None:
        if not isinstance(constraints, dict):
            raise BridgeError("authority.constraints must be an object before effect-contract comparison")
        if constraints.get("overwrite") is not False or constraints.get("delete_source") is not False:
            raise BridgeError("effect_contract requires overwrite=false and delete_source=false")
    return contract


def coherence_report() -> dict[str, Any]:
    return {
        "status": "STRUCTURED_CONTRACT_COHERENT",
        "checks": [
            "requested_outcome_is_copy_selected_files",
            "source_effect_is_preserve",
            "destination_effect_is_create_only_if_absent",
            "overwrite_policy_forbid_matches_authority",
            "source_deletion_policy_forbid_matches_authority",
            "collision_policy_stop_without_overwrite",
            "failure_policy_stop_and_report_partial_results",
            "verification_requires_destination_hash_match_and_source_preservation",
            "known_affirmative_prose_conflicts_absent",
        ],
        "boundary": "The bounded cue scanner detects only enumerated contradiction patterns; it does not establish arbitrary natural-language equivalence.",
    }


class BridgeError(ValueError):
    """Fail-closed request, plan, or execution validation failure."""


CANONICALIZATION_PROFILE = "LAMAGUE-JCS-SUBSET-0.1"
MAX_SAFE_INTEGER = 9_007_199_254_740_991


def _prepare_canonical(value: Any) -> Any:
    """Validate and key-sort the JSON subset used by BRIDGE.

    This intentionally accepts only objects, arrays, strings, booleans, null,
    and safe integers. Floating-point numbers are not part of the v0.1 packet
    contract. Object key order follows UTF-16 code-unit order as in RFC 8785.
    """
    if value is None or isinstance(value, bool) or isinstance(value, str):
        return value
    if type(value) is int:
        if abs(value) > MAX_SAFE_INTEGER:
            raise ValueError("integer exceeds the safe interoperable JSON range")
        return value
    if isinstance(value, float):
        raise ValueError("floating-point values are not permitted by the BRIDGE v0.1 canonicalization profile")
    if isinstance(value, list):
        return [_prepare_canonical(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        ordered_keys = sorted(value, key=lambda key: key.encode("utf-16-be", errors="strict"))
        return {key: _prepare_canonical(value[key]) for key in ordered_keys}
    raise ValueError(f"value of type {type(value).__name__} is not supported by canonicalization")


def canonical_json(obj: Any) -> bytes:
    prepared = _prepare_canonical(obj)
    try:
        return json.dumps(prepared, ensure_ascii=False, sort_keys=False, separators=(",", ":"), allow_nan=False).encode("utf-8", errors="strict")
    except (UnicodeEncodeError, ValueError) as exc:
        raise ValueError(f"value cannot be canonically serialized: {exc}") from exc


def _unique_object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BridgeError(f"duplicate JSON property name: {key}")
        result[key] = value
    return result


def _parse_safe_int(raw: str) -> int:
    if raw == "-0":
        raise BridgeError("negative zero is refused by the BRIDGE canonicalization profile")
    value = int(raw)
    if abs(value) > MAX_SAFE_INTEGER:
        raise BridgeError("JSON integer exceeds the safe interoperable range")
    return value


def _reject_float(raw: str):
    raise BridgeError(f"floating-point JSON number is not supported by the BRIDGE v0.1 profile: {raw}")


def digest_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_stream(stream: BinaryIO) -> tuple[str, int]:
    h = hashlib.sha256()
    count = 0
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        count += len(chunk)
        h.update(chunk)
    return h.hexdigest(), count


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_time(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise BridgeError(f"{field} must be an ISO-8601 timestamp with timezone")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BridgeError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None:
        raise BridgeError(f"{field} must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


WINDOWS_RESERVED_STEMS = {
    "con", "prn", "aux", "nul", "conin$", "conout$",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
    *(f"com{n}" for n in ("¹", "²", "³")),
    *(f"lpt{n}" for n in ("¹", "²", "³")),
}
WINDOWS_FORBIDDEN = set('<>:"|?*')


def portable_path_key(path: PurePosixPath) -> tuple[str, ...]:
    """Conservative cross-platform identity key for relative path components.

    This does not rewrite a path used for I/O. It only detects aliases likely
    to collide on common case-insensitive or Unicode-normalizing filesystems.
    """
    return tuple(unicodedata.normalize("NFC", unicodedata.normalize("NFC", part).casefold()) for part in path.parts)


def register_portable_path_namespace(registry: dict[tuple[str, ...], tuple[str, ...]],
                                    path: PurePosixPath, label: str) -> None:
    """Reject component spellings that alias under conservative portable rules."""
    for depth in range(1, len(path.parts) + 1):
        key = portable_path_key(PurePosixPath(*path.parts[:depth]))
        spelling = tuple(path.parts[:depth])
        prior = registry.get(key)
        if prior is not None and prior != spelling:
            raise BridgeError(
                f"{label} has a portable path alias: {'/'.join(spelling)!r} conflicts with {'/'.join(prior)!r}"
            )
        registry.setdefault(key, spelling)


def validate_relative_path(value: Any, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise BridgeError(f"{label} must be a non-empty POSIX-style relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise BridgeError(f"{label} must identify a file below the root; absolute, empty, dot, and dot-dot paths are forbidden")
    if path.as_posix() != value:
        raise BridgeError(f"{label} must use canonical relative-path spelling")
    for part in path.parts:
        if part.endswith((".", " ")):
            raise BridgeError(f"{label} contains a component ending in a dot or space, unsafe for portable filesystems: {part!r}")
        if any(ord(ch) < 32 or ch in WINDOWS_FORBIDDEN for ch in part):
            raise BridgeError(f"{label} contains a character forbidden by common Windows path rules: {part!r}")
        device_stem = part.split(".", 1)[0].casefold()
        if device_stem in WINDOWS_RESERVED_STEMS:
            raise BridgeError(f"{label} contains a reserved device-name component: {part!r}")
    return path


def assert_plain_directory(path_str: Any, label: str) -> Path:
    if not isinstance(path_str, str) or not path_str:
        raise BridgeError(f"{label} must be an explicit path")
    path = Path(path_str).expanduser()
    try:
        st = path.lstat()
    except OSError as exc:
        raise BridgeError(f"{label} does not exist or cannot be inspected: {exc}") from exc
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise BridgeError(f"{label} must be an existing non-symlink directory")
    return path.resolve(strict=True)


def _check_no_symlink_components(root: Path, relative: PurePosixPath, *, include_leaf: bool) -> Path:
    current = root
    parts = relative.parts if include_leaf else relative.parts[:-1]
    for part in parts:
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            raise BridgeError(f"path component does not exist: {current}")
        if stat.S_ISLNK(st.st_mode):
            raise BridgeError(f"symlink component is not allowed: {current}")
        if current != root and not stat.S_ISDIR(st.st_mode) and part != parts[-1]:
            raise BridgeError(f"non-directory path component: {current}")
    return root.joinpath(*relative.parts)


def _open_regular_nofollow(path: Path) -> BinaryIO:
    try:
        before = path.lstat()
    except OSError as exc:
        raise BridgeError(f"cannot stat source file {path}: {exc}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise BridgeError(f"source is not a regular non-symlink file: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise BridgeError(f"cannot safely open source {path}: {exc}") from exc
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise BridgeError(f"source changed during safe-open check: {path}")
        return os.fdopen(fd, "rb")
    except Exception:
        os.close(fd)
        raise


def validate_packet(packet: Any) -> tuple[Path, Path, dict[str, Any]]:
    if not isinstance(packet, dict):
        raise BridgeError("packet must be a JSON object")
    expected_packet_keys = {
        "bridge_version", "intent_id", "purpose", "authority", "invariants",
        "protected_unknowns", "recovery", "presence_map", "participants",
        "affected_parties", "preconditions", "postconditions", "action_graph", "effect_contract",
    }
    missing_packet_keys = expected_packet_keys - set(packet)
    extra_packet_keys = set(packet) - expected_packet_keys - {"extensions"}
    if missing_packet_keys or extra_packet_keys:
        raise BridgeError(f"packet field shape mismatch; missing={sorted(missing_packet_keys)}, extra={sorted(extra_packet_keys)}")
    if "extensions" in packet and not isinstance(packet["extensions"], dict):
        raise BridgeError("extensions must be an object")
    if packet.get("bridge_version") != VERSION:
        raise BridgeError(f"unsupported bridge_version; expected {VERSION}")
    if not isinstance(packet.get("intent_id"), str) or not packet["intent_id"].strip():
        raise BridgeError("intent_id is required")
    if not isinstance(packet.get("purpose"), str) or not packet["purpose"].strip():
        raise BridgeError("purpose must be explicit non-empty text")
    presence = packet.get("presence_map")
    if not isinstance(presence, dict):
        raise BridgeError("presence_map is required; missing fields must not be guessed")
    missing = REQUIRED_PRESENCE - set(presence)
    extra_invalid = {k: v for k, v in presence.items() if not isinstance(v, str) or v not in PRESENCE_STATES}
    extra_presence = set(presence) - REQUIRED_PRESENCE
    if missing:
        raise BridgeError(f"presence_map lacks required keys: {sorted(missing)}")
    if extra_presence:
        raise BridgeError(f"presence_map has undeclared keys: {sorted(extra_presence)}")
    if extra_invalid:
        raise BridgeError(f"presence_map has invalid states: {extra_invalid}")
    if any(presence[k] != "PRESENT" for k in ("purpose", "authority", "invariants", "recovery", "action_graph", "preconditions", "postconditions", "effect_contract")):
        raise BridgeError("required operational fields must be PRESENT")
    effect_contract = validate_effect_contract(packet.get("effect_contract"), packet.get("authority", {}).get("constraints") if isinstance(packet.get("authority"), dict) else None)
    prose_conflicts = purpose_conflicts_with_copy_contract(packet)
    if prose_conflicts:
        raise BridgeError("known purpose/effect contradiction: " + "; ".join(prose_conflicts))
    if not isinstance(packet.get("invariants"), list) or not packet["invariants"] or any(not isinstance(x, str) or not x.strip() for x in packet["invariants"]):
        raise BridgeError("at least one explicit invariant string is required")
    if not isinstance(packet.get("participants"), list) or not packet["participants"] or any(not isinstance(x, str) or not x.strip() for x in packet["participants"]):
        raise BridgeError("participants must be a non-empty list of explicit strings")
    affected = packet.get("affected_parties")
    if not isinstance(affected, list) or any(not isinstance(x, str) or not x.strip() for x in affected):
        raise BridgeError("affected_parties must be a list of explicit strings")
    if presence["participants"] != "PRESENT":
        raise BridgeError("participants must be PRESENT for this operation")
    if presence["affected_parties"] == "EXPLICITLY_ABSENT" and affected:
        raise BridgeError("affected_parties says EXPLICITLY_ABSENT but list is not empty")
    if presence["affected_parties"] == "PRESENT" and not affected:
        raise BridgeError("affected_parties says PRESENT but list is empty")
    if not isinstance(packet.get("preconditions"), list) or not packet["preconditions"] or any(not isinstance(x, str) or not x.strip() for x in packet["preconditions"]):
        raise BridgeError("preconditions must be a non-empty list of explicit strings")
    if not isinstance(packet.get("postconditions"), list) or not packet["postconditions"] or any(not isinstance(x, str) or not x.strip() for x in packet["postconditions"]):
        raise BridgeError("postconditions must be a non-empty list of explicit strings")
    if not isinstance(packet.get("protected_unknowns"), list) or any(not isinstance(x, str) or not x.strip() for x in packet["protected_unknowns"]):
        raise BridgeError("protected_unknowns must be a list of explicit non-empty strings (use presence_map to state its status)")
    if presence["protected_unknowns"] == "UNKNOWN" and not packet["protected_unknowns"]:
        raise BridgeError("protected_unknowns is UNKNOWN but no unknown is described")
    if presence["protected_unknowns"] == "PRESENT" and not packet["protected_unknowns"]:
        raise BridgeError("protected_unknowns says PRESENT but list is empty")
    if presence["protected_unknowns"] == "EXPLICITLY_ABSENT" and packet["protected_unknowns"]:
        raise BridgeError("protected_unknowns says EXPLICITLY_ABSENT but list is not empty")
    recovery = packet.get("recovery")
    if not isinstance(recovery, list) or not recovery:
        raise BridgeError("recovery path must be explicit and non-empty")
    authority = packet.get("authority")
    if not isinstance(authority, dict):
        raise BridgeError("authority must be a typed grant object")
    authority_keys = {"principal", "delegate", "capabilities", "source_root", "destination_root", "constraints", "expires_at"}
    missing_authority = authority_keys - set(authority)
    extra_authority = set(authority) - authority_keys
    if missing_authority or extra_authority:
        raise BridgeError(f"authority field shape mismatch; missing={sorted(missing_authority)}, extra={sorted(extra_authority)}")
    if not isinstance(authority["principal"], str) or not authority["principal"].strip():
        raise BridgeError("authority.principal must be explicit")
    if not isinstance(authority["delegate"], str) or not authority["delegate"].strip():
        raise BridgeError("authority.delegate must be explicit")
    capabilities = authority["capabilities"]
    if not isinstance(capabilities, list) or any(not isinstance(x, str) for x in capabilities):
        raise BridgeError("authority.capabilities must be a list of string capability IDs")
    if len(capabilities) != len(set(capabilities)):
        raise BridgeError("authority.capabilities must not contain duplicates")
    extras = set(capabilities) - REQUIRED_CAPABILITIES
    if extras:
        raise BridgeError(f"this prototype rejects undeclared capabilities: {sorted(extras)}")
    if set(capabilities) != REQUIRED_CAPABILITIES:
        raise BridgeError(f"authority must declare exactly the limited capabilities {sorted(REQUIRED_CAPABILITIES)}")
    if parse_time(authority["expires_at"], "authority.expires_at") <= utc_now():
        raise BridgeError("authority grant has expired")
    constraints = authority["constraints"]
    if not isinstance(constraints, dict):
        raise BridgeError("authority.constraints must be an object")
    required_constraints = {"overwrite", "delete_source", "max_files", "max_bytes"}
    if not required_constraints.issubset(constraints):
        raise BridgeError(f"authority constraints missing {sorted(required_constraints - set(constraints))}")
    if constraints["overwrite"] is not False or constraints["delete_source"] is not False:
        raise BridgeError("prototype invariant: overwrite=false and delete_source=false")
    if type(constraints["max_files"]) is not int or constraints["max_files"] < 1:
        raise BridgeError("max_files must be a positive integer")
    if type(constraints["max_bytes"]) is not int or constraints["max_bytes"] < 0:
        raise BridgeError("max_bytes must be a non-negative integer")
    source_root = assert_plain_directory(authority.get("source_root"), "authority.source_root")
    destination_root = assert_plain_directory(authority.get("destination_root"), "authority.destination_root")
    if source_root == destination_root or source_root in destination_root.parents or destination_root in source_root.parents:
        raise BridgeError("source and destination roots must be separate, non-nested directories")
    actions = packet.get("action_graph")
    if not isinstance(actions, list) or not actions:
        raise BridgeError("action_graph must be a non-empty array")
    if len(actions) > constraints["max_files"]:
        raise BridgeError("action count exceeds authority max_files")
    destinations: list[str] = []
    destination_keys: set[tuple[str, ...]] = set()
    destination_namespace: dict[tuple[str, ...], tuple[str, ...]] = {}
    source_namespace: dict[tuple[str, ...], tuple[str, ...]] = {}
    for index, action in enumerate(actions):
        if not isinstance(action, dict) or set(action) != {"capability", "source", "destination"}:
            raise BridgeError(f"action_graph[{index}] must have only capability, source, destination")
        if action["capability"] != "file.copy_no_clobber":
            raise BridgeError(f"action_graph[{index}] requests a capability outside this prototype")
        src_rel = validate_relative_path(action["source"], f"action_graph[{index}].source")
        dst_rel = validate_relative_path(action["destination"], f"action_graph[{index}].destination")
        register_portable_path_namespace(source_namespace, src_rel, f"action_graph[{index}].source")
        register_portable_path_namespace(destination_namespace, dst_rel, f"action_graph[{index}].destination")
        dst_key = portable_path_key(dst_rel)
        if dst_key in destination_keys:
            raise BridgeError(f"duplicate destination or portable alias in action graph: {dst_rel}")
        destination_keys.add(dst_key)
        destinations.append(str(dst_rel))
        src = _check_no_symlink_components(source_root, src_rel, include_leaf=True)
        dst = _check_no_symlink_components(destination_root, dst_rel, include_leaf=False)
        if not src.exists() or not src.is_file():
            raise BridgeError(f"source must be an existing regular file: {src}")
        if not dst.parent.exists() or not dst.parent.is_dir():
            raise BridgeError(f"destination parent must already exist: {dst.parent}")
        if dst.exists() or dst.is_symlink():
            raise BridgeError(f"destination already exists; overwrite is forbidden: {dst}")
    return source_root, destination_root, authority


def build_plan(packet: dict[str, Any]) -> dict[str, Any]:
    source_root, destination_root, authority = validate_packet(packet)
    effect_contract = packet["effect_contract"]  # validate_packet has checked the complete fixed v0.2 contract
    actions = []
    total_bytes = 0
    for index, action in enumerate(packet["action_graph"]):
        src_rel = validate_relative_path(action["source"], f"action_graph[{index}].source")
        dst_rel = validate_relative_path(action["destination"], f"action_graph[{index}].destination")
        src = _check_no_symlink_components(source_root, src_rel, include_leaf=True)
        with _open_regular_nofollow(src) as stream:
            source_hash, source_size = sha256_stream(stream)
        total_bytes += source_size
        actions.append({
            "action_id": f"copy-{index + 1:03d}",
            "capability": "file.copy_no_clobber",
            "source_relative": src_rel.as_posix(),
            "destination_relative": dst_rel.as_posix(),
            "source_sha256": source_hash,
            "source_bytes": source_size,
            "preconditions": ["source_hash_equals_plan", "destination_absent", "destination_parent_existing", "no_symlink_components"],
            "postconditions": ["destination_hash_equals_source_hash", "source_hash_unchanged"],
        })
    if total_bytes > authority["constraints"]["max_bytes"]:
        raise BridgeError(f"plan size {total_bytes} exceeds authority max_bytes {authority['constraints']['max_bytes']}")
    packet_hash = digest_obj(packet)
    canonical_authority = dict(authority)
    canonical_authority["source_root"] = str(source_root)
    canonical_authority["destination_root"] = str(destination_root)
    plan: dict[str, Any] = {
        "protocol": PROTOCOL,
        "bridge_version": VERSION,
        "canonicalization": CANONICALIZATION_PROFILE,
        "intent_id": packet["intent_id"],
        "purpose": packet["purpose"],
        "packet_sha256": packet_hash,
        "packet_snapshot": packet,
        "compiled_at": utc_now().isoformat().replace("+00:00", "Z"),
        "source_root": str(source_root),
        "destination_root": str(destination_root),
        "authority": canonical_authority,
        "invariants": packet["invariants"],
        "protected_unknowns": packet["protected_unknowns"],
        "recovery": packet["recovery"],
        "effect_contract": effect_contract,
        "effect_contract_sha256": digest_obj(effect_contract),
        "contract_coherence": coherence_report(),
        "action_count": len(actions),
        "total_bytes": total_bytes,
        "actions": actions,
        "approval_required": True,
        "side_effect_class": "COMPENSATABLE",
        "execution_policy": {
            "dry_run_default": True,
            "overwrite": False,
            "delete_source": False,
            "arbitrary_commands": False,
            "destination_parent_creation": False,
            "commit_method": "same-directory-hard-link-no-clobber; fail closed if unsupported",
        },
    }
    plan["plan_sha256"] = digest_obj(plan)
    return plan


def verify_plan_integrity(plan: Any) -> dict[str, Any]:
    """Validate both the plan digest and the restricted execution language."""
    if not isinstance(plan, dict):
        raise BridgeError("plan must be a JSON object")
    expected_keys = {
        "protocol", "bridge_version", "canonicalization", "intent_id", "purpose",
        "packet_sha256", "packet_snapshot", "compiled_at", "source_root", "destination_root", "authority",
        "invariants", "protected_unknowns", "recovery", "effect_contract", "effect_contract_sha256", "contract_coherence", "action_count", "total_bytes",
        "actions", "approval_required", "side_effect_class", "execution_policy", "plan_sha256",
    }
    if set(plan) != expected_keys:
        raise BridgeError(f"plan field shape mismatch; missing={sorted(expected_keys - set(plan))}, extra={sorted(set(plan) - expected_keys)}")
    if plan.get("protocol") != PROTOCOL or plan.get("bridge_version") != VERSION:
        raise BridgeError("unsupported plan protocol or version")
    if plan.get("canonicalization") != CANONICALIZATION_PROFILE:
        raise BridgeError("unsupported plan canonicalization profile")
    claimed = plan.get("plan_sha256")
    if not isinstance(claimed, str) or not re.fullmatch(r"[0-9a-f]{64}", claimed):
        raise BridgeError("plan_sha256 must be 64 lowercase hexadecimal characters")
    payload = {k: v for k, v in plan.items() if k != "plan_sha256"}
    actual = digest_obj(payload)
    if claimed != actual:
        raise BridgeError("plan digest mismatch; plan may have been modified")
    if plan.get("approval_required") is not True or plan.get("side_effect_class") != "COMPENSATABLE":
        raise BridgeError("plan must require approval and use the declared COMPENSATABLE side-effect class")
    for field_name in ("intent_id", "purpose", "source_root", "destination_root"):
        if not isinstance(plan.get(field_name), str) or not plan[field_name].strip():
            raise BridgeError(f"plan {field_name} must be explicit non-empty text")
    if not isinstance(plan["packet_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", plan["packet_sha256"]):
        raise BridgeError("packet_sha256 must be 64 lowercase hexadecimal characters")
    snapshot = plan["packet_snapshot"]
    if not isinstance(snapshot, dict) or digest_obj(snapshot) != plan["packet_sha256"]:
        raise BridgeError("packet snapshot digest does not match packet_sha256")
    snapshot_keys = {
        "bridge_version", "intent_id", "purpose", "authority", "invariants", "protected_unknowns",
        "recovery", "presence_map", "participants", "affected_parties", "preconditions", "postconditions", "action_graph", "effect_contract",
    }
    if set(snapshot) - snapshot_keys - {"extensions"} or snapshot_keys - set(snapshot):
        raise BridgeError("packet snapshot field shape mismatch")
    if snapshot.get("bridge_version") != VERSION:
        raise BridgeError("packet snapshot version mismatch")
    if plan["intent_id"] != snapshot.get("intent_id") or plan["purpose"] != snapshot.get("purpose"):
        raise BridgeError("compiled identity/purpose differs from the protected packet snapshot")
    if plan["invariants"] != snapshot.get("invariants") or plan["protected_unknowns"] != snapshot.get("protected_unknowns") or plan["recovery"] != snapshot.get("recovery"):
        raise BridgeError("compiled protected fields differ from the packet snapshot")
    checked_effect_contract = validate_effect_contract(snapshot.get("effect_contract"), snapshot.get("authority", {}).get("constraints") if isinstance(snapshot.get("authority"), dict) else None)
    if plan.get("effect_contract") != checked_effect_contract:
        raise BridgeError("compiled effect contract differs from the protected packet snapshot")
    if plan.get("effect_contract_sha256") != digest_obj(checked_effect_contract):
        raise BridgeError("effect_contract_sha256 does not match the typed effect contract")
    if plan.get("contract_coherence") != coherence_report():
        raise BridgeError("contract_coherence report differs from the frozen v0.2 coherence rules")
    prose_conflicts = purpose_conflicts_with_copy_contract(snapshot)
    if prose_conflicts:
        raise BridgeError("known purpose/effect contradiction: " + "; ".join(prose_conflicts))
    snapshot_authority = snapshot.get("authority")
    if not isinstance(snapshot_authority, dict):
        raise BridgeError("packet snapshot authority must be an object")
    normalized_snapshot_authority = dict(snapshot_authority)
    for root_key in ("source_root", "destination_root"):
        try:
            normalized_snapshot_authority[root_key] = str(Path(snapshot_authority[root_key]).expanduser().resolve(strict=False))
        except (KeyError, OSError, TypeError) as exc:
            raise BridgeError(f"packet snapshot authority has invalid {root_key}") from exc
    if normalized_snapshot_authority != plan.get("authority"):
        raise BridgeError("compiled authority differs from the protected packet snapshot")
    snapshot_actions = snapshot.get("action_graph")
    if not isinstance(snapshot_actions, list) or len(snapshot_actions) != len(plan.get("actions", [])):
        raise BridgeError("compiled action count differs from the packet snapshot")
    for index, (requested, compiled) in enumerate(zip(snapshot_actions, plan["actions"])):
        if not isinstance(requested, dict) or set(requested) != {"capability", "source", "destination"}:
            raise BridgeError(f"packet snapshot action {index} has an invalid shape")
        if requested.get("capability") != compiled.get("capability") or requested.get("source") != compiled.get("source_relative") or requested.get("destination") != compiled.get("destination_relative"):
            raise BridgeError(f"compiled action {index} differs from the protected packet snapshot")
    parse_time(plan["compiled_at"], "plan.compiled_at")
    if not isinstance(plan["invariants"], list) or not plan["invariants"] or any(not isinstance(x, str) or not x.strip() for x in plan["invariants"]):
        raise BridgeError("plan invariants must be a non-empty list of strings")
    if not isinstance(plan["protected_unknowns"], list) or any(not isinstance(x, str) or not x.strip() for x in plan["protected_unknowns"]):
        raise BridgeError("plan protected_unknowns must be a list of explicit strings")
    if not isinstance(plan["recovery"], list) or not plan["recovery"] or any(not isinstance(x, str) or not x.strip() for x in plan["recovery"]):
        raise BridgeError("plan recovery must be a non-empty list of strings")

    authority = plan["authority"]
    if not isinstance(authority, dict):
        raise BridgeError("plan authority must be an object")
    authority_keys = {"principal", "delegate", "capabilities", "source_root", "destination_root", "constraints", "expires_at"}
    if set(authority) != authority_keys:
        raise BridgeError(f"plan authority field shape mismatch; missing={sorted(authority_keys - set(authority))}, extra={sorted(set(authority) - authority_keys)}")
    if any(not isinstance(authority.get(k), str) or not authority[k].strip() for k in ("principal", "delegate", "source_root", "destination_root")):
        raise BridgeError("plan authority principal, delegate, and resource roots must be explicit")
    if authority["source_root"] != plan["source_root"] or authority["destination_root"] != plan["destination_root"]:
        raise BridgeError("plan resource roots do not match the authority grant")
    if not Path(plan["source_root"]).is_absolute() or not Path(plan["destination_root"]).is_absolute():
        raise BridgeError("plan source and destination roots must be canonical absolute paths")
    capabilities = authority["capabilities"]
    if not isinstance(capabilities, list) or any(not isinstance(x, str) for x in capabilities):
        raise BridgeError("plan authority capabilities must be a list of string IDs")
    if len(capabilities) != len(set(capabilities)) or set(capabilities) != REQUIRED_CAPABILITIES:
        raise BridgeError("plan authority capability set is not the exact v0.1 allowlist")
    parse_time(authority["expires_at"], "authority.expires_at")
    constraints = authority["constraints"]
    constraint_keys = {"overwrite", "delete_source", "max_files", "max_bytes"}
    if not isinstance(constraints, dict) or set(constraints) != constraint_keys:
        raise BridgeError("plan authority constraints have an unexpected shape")
    if constraints["overwrite"] is not False or constraints["delete_source"] is not False:
        raise BridgeError("plan authority must forbid overwrite and source deletion")
    if type(constraints["max_files"]) is not int or constraints["max_files"] < 1 or type(constraints["max_bytes"]) is not int or constraints["max_bytes"] < 0:
        raise BridgeError("plan authority file/byte ceilings are invalid")

    expected_policy = {
        "dry_run_default": True,
        "overwrite": False,
        "delete_source": False,
        "arbitrary_commands": False,
        "destination_parent_creation": False,
        "commit_method": "same-directory-hard-link-no-clobber; fail closed if unsupported",
    }
    if plan["execution_policy"] != expected_policy:
        raise BridgeError("plan execution policy differs from the executable v0.1 policy")
    actions = plan["actions"]
    if not isinstance(actions, list) or not actions:
        raise BridgeError("plan actions must be a non-empty array")
    if type(plan["action_count"]) is not int or plan["action_count"] != len(actions):
        raise BridgeError("plan action_count does not match its action list")
    if plan["action_count"] > constraints["max_files"]:
        raise BridgeError("plan action count exceeds authority max_files")
    total_bytes = 0
    seen_action_ids: set[str] = set()
    seen_destinations: set[tuple[str, ...]] = set()
    destination_namespace: dict[tuple[str, ...], tuple[str, ...]] = {}
    source_namespace: dict[tuple[str, ...], tuple[str, ...]] = {}
    action_keys = {"action_id", "capability", "source_relative", "destination_relative", "source_sha256", "source_bytes", "preconditions", "postconditions"}
    expected_preconditions = ["source_hash_equals_plan", "destination_absent", "destination_parent_existing", "no_symlink_components"]
    expected_postconditions = ["destination_hash_equals_source_hash", "source_hash_unchanged"]
    for i, action in enumerate(actions):
        if not isinstance(action, dict) or set(action) != action_keys:
            raise BridgeError(f"plan action {i} has an unexpected shape")
        if not isinstance(action["action_id"], str) or not action["action_id"] or action["action_id"] in seen_action_ids:
            raise BridgeError(f"plan action {i} has missing or duplicate action_id")
        seen_action_ids.add(action["action_id"])
        if action["capability"] != "file.copy_no_clobber":
            raise BridgeError(f"plan action {i} requests a capability outside the executable allowlist")
        src_rel = validate_relative_path(action["source_relative"], f"plan action {i} source_relative")
        dst_rel = validate_relative_path(action["destination_relative"], f"plan action {i} destination_relative")
        register_portable_path_namespace(source_namespace, src_rel, f"plan action {i} source_relative")
        register_portable_path_namespace(destination_namespace, dst_rel, f"plan action {i} destination_relative")
        dst_key = portable_path_key(dst_rel)
        if dst_key in seen_destinations:
            raise BridgeError(f"duplicate destination or portable alias in plan: {dst_rel}")
        seen_destinations.add(dst_key)
        if not isinstance(action["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", action["source_sha256"]):
            raise BridgeError(f"plan action {i} source_sha256 is invalid")
        if type(action["source_bytes"]) is not int or action["source_bytes"] < 0:
            raise BridgeError(f"plan action {i} source_bytes is invalid")
        if action["preconditions"] != expected_preconditions or action["postconditions"] != expected_postconditions:
            raise BridgeError(f"plan action {i} preconditions/postconditions differ from the declared executor contract")
        total_bytes += action["source_bytes"]
    if type(plan["total_bytes"]) is not int or plan["total_bytes"] != total_bytes:
        raise BridgeError("plan total_bytes does not match action lengths")
    if total_bytes > constraints["max_bytes"]:
        raise BridgeError("plan byte count exceeds authority max_bytes")
    return plan


def _verify_authority_now(authority: dict[str, Any], source_root: Path, destination_root: Path) -> None:
    if parse_time(authority.get("expires_at"), "authority.expires_at") <= utc_now():
        raise BridgeError("authority grant expired after plan creation")
    if Path(authority.get("source_root", "")).resolve(strict=True) != source_root:
        raise BridgeError("source root no longer matches grant")
    if Path(authority.get("destination_root", "")).resolve(strict=True) != destination_root:
        raise BridgeError("destination root no longer matches grant")
    if authority.get("constraints", {}).get("overwrite") is not False or authority.get("constraints", {}).get("delete_source") is not False:
        raise BridgeError("unsafe authority constraints")


def _copy_to_temp(source: Path, temp_path: Path, expected_hash: str, expected_size: int) -> None:
    h = hashlib.sha256()
    copied = 0
    # Re-open the already-created same-directory staging file without following
    # a substituted symlink where supported; compare inode to the pre-open stat.
    try:
        temp_before = temp_path.lstat()
    except OSError as exc:
        raise BridgeError(f"staging file disappeared: {exc}") from exc
    if stat.S_ISLNK(temp_before.st_mode) or not stat.S_ISREG(temp_before.st_mode):
        raise BridgeError("staging path is no longer a regular file")
    flags = os.O_WRONLY | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(temp_path, flags)
    except OSError as exc:
        raise BridgeError(f"cannot safely open staging file: {exc}") from exc
    with _open_regular_nofollow(source) as src:
        try:
            temp_after = os.fstat(fd)
            if (temp_before.st_dev, temp_before.st_ino) != (temp_after.st_dev, temp_after.st_ino):
                raise BridgeError("staging file changed during safe-open check")
            with os.fdopen(fd, "wb") as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    copied += len(chunk)
                    if copied > expected_size:
                        raise BridgeError(f"source grew beyond approved size while copying: {source}")
                    h.update(chunk)
                    dst.write(chunk)
                dst.flush()
                os.fsync(dst.fileno())
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
    if copied != expected_size or h.hexdigest() != expected_hash:
        raise BridgeError(f"source bytes/hash changed since plan: {source}")


def _hash_path(path: Path) -> tuple[str, int]:
    with _open_regular_nofollow(path) as stream:
        return sha256_stream(stream)


def _emit_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    receipt = dict(payload)
    receipt["receipt_sha256"] = digest_obj(receipt)
    return receipt


def execute_plan(plan: dict[str, Any], approval_hash: str) -> dict[str, Any]:
    verify_plan_integrity(plan)
    if not isinstance(approval_hash, str) or approval_hash != plan["plan_sha256"]:
        raise BridgeError("approval hash does not match this exact plan; no action taken")
    source_root = assert_plain_directory(plan.get("source_root"), "plan.source_root")
    destination_root = assert_plain_directory(plan.get("destination_root"), "plan.destination_root")
    _verify_authority_now(plan["authority"], source_root, destination_root)
    if len(plan.get("actions", [])) != plan.get("action_count"):
        raise BridgeError("plan action count mismatch")
    if sum(a.get("source_bytes", -1) for a in plan["actions"]) != plan.get("total_bytes"):
        raise BridgeError("plan total byte count mismatch")

    execution_started_at = utc_now().isoformat().replace("+00:00", "Z")
    receipt_actions = []
    failures = []
    for action in plan["actions"]:
        # Structural validation already checked these fields; keep path resolution
        # inside the guarded block so a disappearing path still yields a receipt.
        src_rel = PurePosixPath(action["source_relative"])
        dst_rel = PurePosixPath(action["destination_relative"])
        record: dict[str, Any] = {
            "action_id": action["action_id"], "source_relative": str(src_rel),
            "destination_relative": str(dst_rel), "expected_sha256": action["source_sha256"],
            "status": "NOT_STARTED",
        }
        temp_path: Path | None = None
        try:
            src = _check_no_symlink_components(source_root, src_rel, include_leaf=True)
            dst = _check_no_symlink_components(destination_root, dst_rel, include_leaf=False)
            if dst.exists() or dst.is_symlink():
                raise BridgeError("destination appeared after planning; refusing to overwrite")
            temp_fd, temp_name = tempfile.mkstemp(prefix=".lamague-bridge-", suffix=".stage", dir=dst.parent)
            os.close(temp_fd)
            temp_path = Path(temp_name)
            _copy_to_temp(src, temp_path, action["source_sha256"], action["source_bytes"])
            temp_hash, temp_size = _hash_path(temp_path)
            if temp_hash != action["source_sha256"] or temp_size != action["source_bytes"]:
                raise BridgeError("staged artifact verification failed")
            try:
                # Same-directory hard link is atomic and refuses an existing name.
                os.link(temp_path, dst, follow_symlinks=False)
            except FileExistsError as exc:
                raise BridgeError("destination collision at commit; no overwrite performed") from exc
            except OSError as exc:
                raise BridgeError(f"atomic no-clobber commit unavailable; failed closed: {exc}") from exc
            dest_stat = dst.stat(follow_symlinks=False)
            created_destination_inode = (dest_stat.st_dev, dest_stat.st_ino)
            temp_path.unlink()
            temp_path = None
            dest_hash, dest_size = _hash_path(dst)
            source_after_hash, source_after_size = _hash_path(src)
            if (dest_hash, dest_size) != (action["source_sha256"], action["source_bytes"]):
                raise BridgeError("destination postcondition failed; created copy retained for inspection")
            if (source_after_hash, source_after_size) != (action["source_sha256"], action["source_bytes"]):
                raise BridgeError("source-unchanged postcondition failed; destination retained for inspection")
            record.update({"status": "VERIFIED", "destination_sha256": dest_hash, "destination_bytes": dest_size,
                           "source_after_sha256": source_after_hash, "source_after_bytes": source_after_size})
        except Exception as exc:
            record.update({"status": "FAILED_CONTAINED", "error": str(exc)})
            failures.append({"action_id": action["action_id"], "error": str(exc)})
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    record["staging_cleanup_warning"] = "temporary staging file could not be removed"
        receipt_actions.append(record)
        if failures:
            # Avoid silently continuing a multi-file job after the first failure.
            break

    all_verified = not failures and len(receipt_actions) == plan["action_count"] and all(a["status"] == "VERIFIED" for a in receipt_actions)
    return _emit_receipt({
        "receipt_version": "0.2",
        "canonicalization": CANONICALIZATION_PROFILE,
        "protocol": PROTOCOL,
        "intent_id": plan["intent_id"],
        "purpose": plan["purpose"],
        "plan_sha256": plan["plan_sha256"],
        "packet_sha256": plan["packet_sha256"],
        "effect_contract_sha256": plan["effect_contract_sha256"],
        "effect_contract": plan["effect_contract"],
        "contract_coherence_status": plan["contract_coherence"]["status"],
        "principal": plan["authority"]["principal"],
        "delegate": plan["authority"]["delegate"],
        "started_at": execution_started_at,
        "completed_at": utc_now().isoformat().replace("+00:00", "Z"),
        "status": "COMPLETED_VERIFIED" if all_verified else "FAILED_CONTAINED",
        "actions": receipt_actions,
        "failures": failures,
        "invariants_checked": ["overwrite=false", "delete_source=false", "source hash matches approved plan", "destination hash verified", "source remains unchanged"],
        "receipt_integrity": f"sha256 over {CANONICALIZATION_PROFILE} bytes excluding receipt_sha256; integrity only, not issuer authentication",
    })


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object_pairs,
                          parse_int=_parse_safe_int, parse_float=_reject_float,
                          parse_constant=lambda value: (_ for _ in ()).throw(BridgeError(f"invalid JSON constant: {value}")))
    except (OSError, json.JSONDecodeError) as exc:
        raise BridgeError(f"cannot load {path}: {exc}") from exc


def reserve_json_output(path: Path) -> tuple[Path, Path, int]:
    """Reserve a unique staging file before side effects begin; never replace output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise BridgeError(f"output already exists; refusing to overwrite: {path}")
    fd, temp_name = tempfile.mkstemp(prefix=".lamague-output-", suffix=".tmp", dir=path.parent)
    return path, Path(temp_name), fd


def commit_reserved_json(reservation: tuple[Path, Path, int], value: Any) -> tuple[Path, bool]:
    """Write to reserved staging; commit without clobber, retain fallback receipt on collision."""
    path, temp, fd = reservation
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temp, path, follow_symlinks=False)
    except FileExistsError:
        # An output collision after execution must not destroy the evidence.
        # Keep the unique staging path as the receipt fallback.
        return temp, False
    except OSError as exc:
        # Preserve the written staging file as the evidence fallback.
        return temp, False
    try:
        temp.unlink(missing_ok=True)
    except OSError:
        # The committed output is valid; a redundant staging link is only cleanup residue.
        pass
    return path, True


def write_json(path: Path, value: Any) -> None:
    reservation = reserve_json_output(path)
    try:
        result_path, committed = commit_reserved_json(reservation, value)
    except Exception:
        try:
            reservation[1].unlink(missing_ok=True)
        except OSError:
            pass
        raise
    if not committed:
        raise BridgeError(f"atomic no-clobber output commit failed; output retained at {result_path}")


def demo_packet(source_root: Path, destination_root: Path) -> dict[str, Any]:
    future = (utc_now() + dt.timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    return {
        "bridge_version": VERSION,
        "intent_id": "demo-file-copy-001",
        "purpose": "Copy explicitly named research fixture files into an archive while preserving originals and refusing overwrite.",
        "authority": {
            "principal": "human:local-operator-demo",
            "delegate": "bridge:reference-python-0.2",
            "capabilities": sorted(REQUIRED_CAPABILITIES),
            "source_root": str(source_root.resolve()),
            "destination_root": str(destination_root.resolve()),
            "constraints": {"overwrite": False, "delete_source": False, "max_files": 3, "max_bytes": 1048576},
            "expires_at": future,
        },
        "invariants": ["never overwrite", "never delete source", "copy only enumerated relative files", "verify source and destination hashes"],
        "protected_unknowns": ["This local demo does not authenticate a human identity or remote destination."],
        "recovery": ["Stop on any failure", "retain source", "inspect receipt and destination before retrying"],
        "effect_contract": dict(EXPECTED_EFFECT_CONTRACT),
        "presence_map": {
            "purpose": "PRESENT", "authority": "PRESENT", "invariants": "PRESENT",
            "protected_unknowns": "PRESENT", "recovery": "PRESENT", "participants": "PRESENT",
            "affected_parties": "EXPLICITLY_ABSENT", "action_graph": "PRESENT",
            "preconditions": "PRESENT", "postconditions": "PRESENT", "effect_contract": "PRESENT",
        },
        "participants": ["local operator", "reference bridge"],
        "affected_parties": [],
        "preconditions": ["all source files exist", "all destinations absent", "paths remain within approved roots"],
        "postconditions": ["every destination hash equals planned source hash", "every source remains unchanged"],
        "action_graph": [
            {"capability": "file.copy_no_clobber", "source": "sample.txt", "destination": "sample.txt"},
            {"capability": "file.copy_no_clobber", "source": "notes/research.txt", "destination": "notes/research.txt"},
        ],
    }


def approval_review_summary(plan: dict[str, Any], plan_path: str) -> dict[str, Any]:
    """Build a human-reviewable summary of the exact compiled plan.

    This is presentation, not an authentication boundary: the plan hash binds
    the reviewed content, but this CLI does not authenticate who reviews it.
    """
    authority = plan["authority"]
    actions = [
        {
            "action_id": action["action_id"],
            "capability": action["capability"],
            "source": action["source_relative"],
            "destination": action["destination_relative"],
            "expected_source_sha256": action["source_sha256"],
            "expected_bytes": action["source_bytes"],
        }
        for action in plan["actions"]
    ]
    return {
        "status": "PLAN_READY_APPROVAL_REQUIRED",
        "review_instruction": (
            "Review purpose, authority, typed effects, invariants, unknowns, "
            "preconditions, postconditions, recovery, paths and hashes before "
            "approving this exact plan."
        ),
        "approval_model": "exact_plan_sha256_confirmation_only",
        "approval_limit": (
            "The digest binds this plan's content; it does not authenticate an "
            "operator, prove the purpose's natural-language meaning, or act as a signature."
        ),
        "plan_sha256": plan["plan_sha256"],
        "purpose": plan["purpose"],
        "authority": {
            "principal": authority["principal"],
            "delegate": authority["delegate"],
            "capabilities": sorted(authority["capabilities"]),
            "source_root": authority["source_root"],
            "destination_root": authority["destination_root"],
            "constraints": authority["constraints"],
            "expires_at": authority["expires_at"],
        },
        "invariants": plan["invariants"],
        "protected_unknowns": plan["protected_unknowns"],
        "recovery": plan["recovery"],
        "preconditions": plan["packet_snapshot"]["preconditions"],
        "postconditions": plan["packet_snapshot"]["postconditions"],
        "effect_contract": plan["effect_contract"],
        "effect_contract_sha256": plan["effect_contract_sha256"],
        "contract_coherence_status": plan["contract_coherence"]["status"],
        "action_count": plan["action_count"],
        "total_bytes": plan["total_bytes"],
        "actions": actions,
        "plan_path": plan_path,
        "approval_required": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    packet_cmd = sub.add_parser("demo-packet", help="write a safe demo packet referencing existing fixture dirs")
    packet_cmd.add_argument("--source", type=Path, required=True)
    packet_cmd.add_argument("--destination", type=Path, required=True)
    packet_cmd.add_argument("-o", "--output", type=Path, required=True)
    plan_cmd = sub.add_parser("plan", help="validate packet and compile a no-side-effect plan")
    plan_cmd.add_argument("packet", type=Path)
    plan_cmd.add_argument("-o", "--output", type=Path, required=True)
    exec_cmd = sub.add_parser("execute", help="execute only after exact plan-hash approval")
    exec_cmd.add_argument("plan", type=Path)
    exec_cmd.add_argument("--approve-plan", required=True, help="exact SHA-256 plan digest reviewed by the operator")
    exec_cmd.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "demo-packet":
            write_json(args.output, demo_packet(args.source, args.destination))
            print(f"Demo packet written: {args.output}")
        elif args.command == "plan":
            plan = build_plan(load_json(args.packet))
            write_json(args.output, plan)
            print(json.dumps(approval_review_summary(plan, str(args.output)), indent=2, ensure_ascii=False))
        elif args.command == "execute":
            plan = verify_plan_integrity(load_json(args.plan))
            if args.approve_plan != plan.get("plan_sha256"):
                raise BridgeError("approval hash does not match this exact plan; no action taken")
            # Reserve the receipt output before performing any file operation.
            reservation = reserve_json_output(args.receipt)
            try:
                receipt = execute_plan(plan, args.approve_plan)
                receipt_path, normal_path_committed = commit_reserved_json(reservation, receipt)
            except Exception:
                try:
                    reservation[1].unlink(missing_ok=True)
                except OSError:
                    pass
                raise
            print(json.dumps({"status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"],
                              "receipt_path": str(receipt_path),
                              "requested_receipt_path_committed": normal_path_committed}, indent=2))
            if receipt["status"] != "COMPLETED_VERIFIED":
                return 3
        return 0
    except (BridgeError, OSError, ValueError, TypeError) as exc:
        print(f"BRIDGE REFUSED: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
