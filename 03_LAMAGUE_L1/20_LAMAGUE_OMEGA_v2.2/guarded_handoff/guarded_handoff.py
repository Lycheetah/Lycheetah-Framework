#!/usr/bin/env python3
"""
===============================================================================
LYCHEETAH GUARDED CROSS-SEAT EXECUTOR & AST SEMANTIC DIFF AUDITOR (FACULTY #15)
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Real-World Guarded Cross-Seat Job, Risk-Hinge
          Closure, Single-Use Ed25519 Permit Ledger, AST Semantic Diff & 4-Plane
          Observation (`2026-10-18_REAL_TOOL_DISCUSSION.md`)
Location: creations/guarded_handoff/guarded_handoff.py

Solves the four architectural requirements and six observable cases identified
by Caelorynth and Aetheron in `2026-10-18_REAL_TOOL_DISCUSSION.md`:

  1. Asymmetric Ed25519 Approval Authority (`SignedActionPermit` + `ConsumedPermitLedger`):
     Uses real asymmetric Ed25519 signatures (`cryptography.hazmat.primitives.asymmetric.ed25519`):
       - Human authority (Mac) holds the `Ed25519PrivateKey` to mint permits.
       - Executing seats hold ONLY the `Ed25519PublicKey` to verify permits and
         cannot forge or mint a valid permit.
       - No hardcoded secret keys exist in source. Missing key refuses execution.
       - `ConsumedPermitLedger` enforces check-and-consume inside a single
         `fcntl.flock(LOCK_EX)` critical section with atomic temp-file +
         `os.replace` writes, and fails closed (refusing all permits) if the
         ledger file is missing or corrupt.

  2. Admission State & Source-Derived Risk-Hinge Closure (`derive_action_risk`):
     Closes the source-derived integration hinge between `compaction/codec.py:45`
     (which excludes `risk` from `CRITICAL_FIELDS`) and `sovereign_harness.py:842-844`
     (which gates high-risk admission on `candidate_packet.risk`).

  3. Restricted Effect Boundary & Python AST Semantic Diff (`audit_python_ast_diff`):
     Executes a restricted, byte-verified file replacement inside a `FileAirlock`
     snapshot and parses Before/After Python ASTs to detect undisclosed logic
     mutations, silent threshold weakenings, and capability escalations.
     Non-`.py` files are explicitly reported as `"NOT_AUDITED"`, never as passed.

  4. Four-Plane Observation Receipt (`Intended / Authorized / Attempted / Observed`):
     Emits a machine-verifiable receipt separating Intended, Authorized,
     Attempted, and Observed planes.
===============================================================================
"""

from __future__ import annotations

import argparse
import ast
import copy
import fcntl
import hashlib
import inspect
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

CREATIONS_DIR = Path(__file__).resolve().parent.parent
for _sub in ("file_airlock", "continuity_prover", "lamague_omega"):
    _p = str(CREATIONS_DIR / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import file_airlock as fa  # noqa: E402


# =============================================================================
# 1. THE 10-FIELD CODEC CONTRACT & ADMISSION RISK-HINGE CLOSURE
# =============================================================================

CODEC_10_CRITICAL_FIELDS: Tuple[str, ...] = (
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
)

RISK_ORDER: Dict[str, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

DANGEROUS_CAPABILITY_CALLS: Set[str] = {
    "eval",
    "exec",
    "compile",
    "os.system",
    "os.popen",
    "os.remove",
    "os.unlink",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_output",
    "shutil.rmtree",
    "socket.socket",
    "urllib.request.urlopen",
}

SAFETY_LOWER_BOUND_NAMES: Set[str] = {
    "SAFETY_FLOOR",
    "MIN_COHERENCE",
    "C_FIELD_FLOOR",
    "MIN_SOVEREIGNTY",
    "HARMONIA_FLOOR",
}

SAFETY_UPPER_BOUND_NAMES: Set[str] = {
    "MAX_DRIFT",
    "DRIFT_CEILING",
    "MAX_ENTROPY",
    "GLASS_THRESHOLD",
}

BOOLEAN_LOCK_NAMES: Set[str] = {
    "READ_ONLY",
    "ENFORCE_BOUNDARY",
    "REQUIRE_HUMAN_APPROVAL",
    "SINGLE_USE_PERMIT",
}


# =============================================================================
# 1B. ED25519 ASYMMETRIC KEY HELPERS
# =============================================================================

def generate_ed25519_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a fresh Ed25519 private/public keypair."""
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()


def private_key_to_hex(priv: Ed25519PrivateKey) -> str:
    raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return raw.hex()


def public_key_to_hex(pub: Ed25519PublicKey) -> str:
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw.hex()


def coerce_ed25519_private_key(key: Union[Ed25519PrivateKey, str, bytes, None]) -> Ed25519PrivateKey:
    if isinstance(key, Ed25519PrivateKey):
        return key
    if isinstance(key, Ed25519PublicKey):
        raise TypeError(
            "ED25519_PRIVATE_KEY_REQUIRED: received an Ed25519PublicKey; a seat holding only the public key cannot mint a permit!"
        )
    if not key:
        raise ValueError("ED25519_PRIVATE_KEY_REQUIRED: missing private key; refusing to mint permit.")
    if isinstance(key, str):
        try:
            raw = bytes.fromhex(key)
        except ValueError as exc:
            raise ValueError(
                "ED25519_PRIVATE_KEY_REQUIRED: string key must be 64-char hex Ed25519 private key seed."
            ) from exc
    elif isinstance(key, bytes):
        raw = key
    else:
        raise TypeError("ED25519_PRIVATE_KEY_REQUIRED: unsupported key type.")
    if len(raw) != 32:
        raise ValueError("ED25519_PRIVATE_KEY_REQUIRED: Ed25519 raw private key must be 32 bytes.")
    return Ed25519PrivateKey.from_private_bytes(raw)


def coerce_ed25519_public_key(key: Union[Ed25519PublicKey, Ed25519PrivateKey, str, bytes, None]) -> Ed25519PublicKey:
    if isinstance(key, Ed25519PublicKey):
        return key
    if isinstance(key, Ed25519PrivateKey):
        return key.public_key()
    if not key:
        raise ValueError("ED25519_PUBLIC_KEY_REQUIRED: missing public key; refusing to verify permit.")
    if isinstance(key, str):
        try:
            raw = bytes.fromhex(key)
        except ValueError as exc:
            raise ValueError(
                "ED25519_PUBLIC_KEY_REQUIRED: string key must be 64-char hex Ed25519 public key."
            ) from exc
    elif isinstance(key, bytes):
        raw = key
    else:
        raise TypeError("ED25519_PUBLIC_KEY_REQUIRED: unsupported key type.")
    if len(raw) != 32:
        raise ValueError("ED25519_PUBLIC_KEY_REQUIRED: Ed25519 raw public key must be 32 bytes.")
    return Ed25519PublicKey.from_public_bytes(raw)


@dataclass
class GuardedStatePacket:
    """
    Preserves exact compatibility with `lycheetah/compaction/codec.py`'s
    10-field `CRITICAL_FIELDS` contract while adding explicit admission-bound
    `risk` and `state_version` fields to test and close the risk-binding hinge.
    """
    purpose: str
    claim: str
    unknowns: List[str]
    invariants: List[str]
    authority: List[str]
    participants: List[str]
    affectedParties: List[str]
    dissent: List[str]
    valueFlow: str
    recovery: str
    risk: str = "HIGH"
    state_version: int = 1

    def critical_10_dict(self) -> Dict[str, Any]:
        return {
            "purpose": self.purpose,
            "claim": self.claim,
            "unknowns": sorted(self.unknowns),
            "invariants": sorted(self.invariants),
            "authority": sorted(self.authority),
            "participants": sorted(self.participants),
            "affectedParties": sorted(self.affectedParties),
            "dissent": sorted(self.dissent),
            "valueFlow": self.valueFlow,
            "recovery": self.recovery,
        }

    def critical_10_digest(self) -> str:
        """
        Unkeyed SHA-256 over ONLY the 10 `CRITICAL_FIELDS` (reproducing `codec.py:45`).
        """
        raw = json.dumps(self.critical_10_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def admission_binding_digest(self, policy_derived_risk: str) -> str:
        """
        Hinge-closing admission digest: binds the 10-field critical hash together
        with `declared_risk`, `policy_derived_risk`, and `state_version`.
        """
        payload = {
            "critical_10_digest": self.critical_10_digest(),
            "declared_risk": self.risk.upper(),
            "policy_derived_risk": policy_derived_risk.upper(),
            "state_version": self.state_version,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


# =============================================================================
# 2. REAL PYTHON AST SEMANTIC DIFF & CAPABILITY ESCALATION AUDITOR
# =============================================================================

def _strip_docstring_from_body(body: List[ast.stmt]) -> List[ast.stmt]:
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _normalize_ast_without_docstrings(tree: ast.AST) -> str:
    tree_copy = copy.deepcopy(tree)
    for node in ast.walk(tree_copy):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            node.body = _strip_docstring_from_body(node.body)
            if not node.body:
                node.body = [ast.Pass()]
    return ast.dump(tree_copy, include_attributes=False)


def _extract_ast_inventory(source_code: str) -> Dict[str, Any]:
    tree = ast.parse(source_code)
    functions: Dict[str, str] = {}
    classes: Dict[str, str] = {}
    constants: Dict[str, Any] = {}
    calls: Set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node_copy = copy.deepcopy(node)
            node_copy.body = _strip_docstring_from_body(node_copy.body)
            functions[node.name] = ast.dump(node_copy, include_attributes=False)
        elif isinstance(node, ast.ClassDef):
            node_copy = copy.deepcopy(node)
            node_copy.body = _strip_docstring_from_body(node_copy.body)
            classes[node.name] = ast.dump(node_copy, include_attributes=False)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    item_copy = copy.deepcopy(item)
                    item_copy.body = _strip_docstring_from_body(item_copy.body)
                    functions[f"{node.name}.{item.name}"] = ast.dump(item_copy, include_attributes=False)
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float, bool, str)):
                    constants[name] = node.value.value
                elif (
                    isinstance(node.value, ast.UnaryOp)
                    and isinstance(node.value.op, ast.USub)
                    and isinstance(node.value.operand, ast.Constant)
                    and isinstance(node.value.operand.value, (int, float))
                ):
                    constants[name] = -node.value.operand.value

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                parts: List[str] = [node.func.attr]
                curr = node.func.value
                while isinstance(curr, ast.Attribute):
                    parts.append(curr.attr)
                    curr = curr.value
                if isinstance(curr, ast.Name):
                    parts.append(curr.id)
                calls.add(".".join(reversed(parts)))

    return {
        "normalized_logic_dump": _normalize_ast_without_docstrings(tree),
        "functions": functions,
        "classes": classes,
        "constants": constants,
        "calls": calls,
    }


def audit_python_ast_diff(
    before_source: str,
    after_source: str,
    handover_claim_text: str = "",
    allowed_capabilities: Optional[List[str]] = None,
    file_path: str = "module.py",
) -> Dict[str, Any]:
    """
    Parse Before and After Python source code into real ASTs and compute an exact
    semantic & capability diff. Non-`.py` files are reported as `NOT_AUDITED`
    (`lawful_ast_diff=None`), never as passed.
    """
    if file_path and not file_path.endswith(".py"):
        return {
            "ast_audit_status": "NOT_AUDITED",
            "valid_syntax": None,
            "lawful_ast_diff": None,
            "file_path": file_path,
            "reason": f"Non-Python file ({file_path!r}) is NOT AUDITED by Python AST diff.",
            "violations_count": 0,
            "violations": [],
        }

    allowed_caps = set(allowed_capabilities or [])
    try:
        inv_before = _extract_ast_inventory(before_source)
        inv_after = _extract_ast_inventory(after_source)
    except SyntaxError as exc:
        return {
            "ast_audit_status": "SYNTAX_ERROR",
            "valid_syntax": False,
            "lawful_ast_diff": False,
            "violations_count": 1,
            "violations": [{
                "code": "AST_SYNTAX_ERROR",
                "detail": f"Candidate Python file has invalid syntax: {exc}",
            }],
        }

    funcs_b = inv_before["functions"]
    funcs_a = inv_after["functions"]
    added_funcs = sorted(set(funcs_a.keys()) - set(funcs_b.keys()))
    removed_funcs = sorted(set(funcs_b.keys()) - set(funcs_a.keys()))
    modified_funcs = sorted(
        k for k in (set(funcs_b.keys()) & set(funcs_a.keys()))
        if funcs_b[k] != funcs_a[k]
    )
    unchanged_funcs = sorted(
        k for k in (set(funcs_b.keys()) & set(funcs_a.keys()))
        if funcs_b[k] == funcs_a[k]
    )

    logic_changed = (inv_before["normalized_logic_dump"] != inv_after["normalized_logic_dump"])
    bytes_changed = (before_source != after_source)
    docstring_or_comment_only = (bytes_changed and not logic_changed)

    violations: List[Dict[str, str]] = []

    # 1. Check for unauthorized capability escalations
    new_calls = sorted(inv_after["calls"] - inv_before["calls"])
    escalated_caps = [
        c for c in new_calls
        if c in DANGEROUS_CAPABILITY_CALLS and c not in allowed_caps
    ]
    for cap in escalated_caps:
        violations.append({
            "code": "UNAUTHORIZED_CAPABILITY_ESCALATION",
            "symbol": cap,
            "detail": f"AST diff introduced dangerous capability call {cap!r} not present in Before AST or allowed_capabilities.",
        })

    # 2. Check for silent weakening of safety constants
    consts_b = inv_before["constants"]
    consts_a = inv_after["constants"]
    threshold_weakenings: List[Dict[str, Any]] = []
    for name, val_b in consts_b.items():
        if name not in consts_a:
            if name in (SAFETY_LOWER_BOUND_NAMES | SAFETY_UPPER_BOUND_NAMES | BOOLEAN_LOCK_NAMES):
                threshold_weakenings.append({"constant": name, "before": val_b, "after": None})
                violations.append({
                    "code": "SILENT_THRESHOLD_WEAKENING",
                    "symbol": name,
                    "detail": f"Protected safety constant {name!r} (was {val_b!r}) was deleted from module.",
                })
            continue
        val_a = consts_a[name]
        if name in SAFETY_LOWER_BOUND_NAMES and isinstance(val_b, (int, float)) and isinstance(val_a, (int, float)):
            if val_a < val_b:
                threshold_weakenings.append({"constant": name, "before": val_b, "after": val_a})
                violations.append({
                    "code": "SILENT_THRESHOLD_WEAKENING",
                    "symbol": name,
                    "detail": f"Safety lower bound {name!r} was lowered from {val_b} to {val_a}.",
                })
        elif name in SAFETY_UPPER_BOUND_NAMES and isinstance(val_b, (int, float)) and isinstance(val_a, (int, float)):
            if val_a > val_b:
                threshold_weakenings.append({"constant": name, "before": val_b, "after": val_a})
                violations.append({
                    "code": "SILENT_THRESHOLD_WEAKENING",
                    "symbol": name,
                    "detail": f"Safety upper bound {name!r} was raised from {val_b} to {val_a}.",
                })
        elif name in BOOLEAN_LOCK_NAMES and val_b is True and val_a is False:
            threshold_weakenings.append({"constant": name, "before": val_b, "after": val_a})
            violations.append({
                "code": "SILENT_THRESHOLD_WEAKENING",
                "symbol": name,
                "detail": f"Boolean safety lock {name!r} was flipped from True to False.",
            })

    # 3. Check handover claim vs AST truth
    low_claim = handover_claim_text.lower()
    if handover_claim_text:
        claims_trivial = any(
            phrase in low_claim
            for phrase in ("comments only", "docstring only", "docstrings only", "formatting only", "no logic change")
        )
        if claims_trivial and logic_changed:
            violations.append({
                "code": "UNDISCLOSED_LOGIC_MUTATION",
                "symbol": ",".join(modified_funcs or added_funcs or removed_funcs or ["<module>"]),
                "detail": (
                    "Handover claimed comments/docstrings/formatting-only change, "
                    f"but executable AST logic changed in {modified_funcs or added_funcs or removed_funcs or ['<module>']}."
                ),
            })

        for fn in unchanged_funcs:
            short_fn = fn.split(".")[-1]
            if f"{short_fn}()" in handover_claim_text or f"`{short_fn}`" in handover_claim_text:
                if not any(neg in low_claim for neg in ("unchanged", "untouched", "did not", "do not")):
                    violations.append({
                        "code": "PHANTOM_SYMBOL_EDIT_CLAIM",
                        "symbol": fn,
                        "detail": f"Handover claims edits to function {fn!r}, but its AST body is 100% unchanged.",
                    })

    return {
        "ast_audit_status": "AUDITED",
        "valid_syntax": True,
        "lawful_ast_diff": len(violations) == 0,
        "bytes_changed": bytes_changed,
        "logic_changed": logic_changed,
        "docstring_or_comment_only": docstring_or_comment_only,
        "added_functions": added_funcs,
        "removed_functions": removed_funcs,
        "modified_functions": modified_funcs,
        "unchanged_functions": unchanged_funcs,
        "new_capability_calls": new_calls,
        "escalated_capabilities": escalated_caps,
        "threshold_weakenings": threshold_weakenings,
        "violations_count": len(violations),
        "violations": violations,
    }


def derive_action_risk(
    target_rel_path: str,
    before_source: Optional[str],
    after_source: Optional[str],
    ast_diff_report: Optional[Dict[str, Any]] = None,
) -> str:
    if after_source is None:
        return "CRITICAL"  # File deletion is always CRITICAL

    low_path = target_rel_path.lower()
    if any(k in low_path for k in ("prime", "constitution", "auth", "security", "guard", "harness", "airlock")):
        base_risk = "HIGH"
    else:
        base_risk = "MEDIUM"

    if ast_diff_report is not None and ast_diff_report.get("ast_audit_status") == "AUDITED":
        if ast_diff_report.get("escalated_capabilities") or ast_diff_report.get("threshold_weakenings"):
            return "CRITICAL"
        if ast_diff_report.get("removed_functions"):
            return "HIGH"
        if ast_diff_report.get("docstring_or_comment_only") and base_risk != "HIGH":
            return "LOW"

    return base_risk


# =============================================================================
# 3. ED25519 ASYMMETRIC SINGLE-USE PERMIT & ATOMIC FLOCK NONCE LEDGER
# =============================================================================

@dataclass
class SignedActionPermit:
    permit_id: str
    issuer_id: str
    executor_seat: str
    action_type: str
    target_rel_path: str
    expected_before_sha256: str
    proposed_after_sha256: str
    allow_globs: List[str]
    forbid_globs: List[str]
    critical_10_digest: str
    admission_binding_digest: str
    authorized_risk: str
    state_version: int
    issued_at_unix: float
    expires_at_unix: float
    ed25519_signature: str = ""
    issuer_public_key_hex: str = ""

    def canonical_signing_bytes(self) -> bytes:
        target_path_sha256 = hashlib.sha256(self.target_rel_path.encode("utf-8")).hexdigest()
        payload = {
            "permit_id": self.permit_id,
            "issuer_id": self.issuer_id,
            "executor_seat": self.executor_seat,
            "action_type": self.action_type,
            "target_rel_path": self.target_rel_path,
            "target_path_sha256": target_path_sha256,
            "expected_before_sha256": self.expected_before_sha256,
            "proposed_after_sha256": self.proposed_after_sha256,
            "allow_globs": sorted(self.allow_globs),
            "forbid_globs": sorted(self.forbid_globs),
            "critical_10_digest": self.critical_10_digest,
            "admission_binding_digest": self.admission_binding_digest,
            "authorized_risk": self.authorized_risk.upper(),
            "state_version": self.state_version,
            "issued_at_unix": self.issued_at_unix,
            "expires_at_unix": self.expires_at_unix,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, authority_private_key: Union[Ed25519PrivateKey, str, bytes]) -> str:
        priv = coerce_ed25519_private_key(authority_private_key)
        sig_bytes = priv.sign(self.canonical_signing_bytes())
        self.ed25519_signature = sig_bytes.hex()
        self.issuer_public_key_hex = public_key_to_hex(priv.public_key())
        return self.ed25519_signature

    def verify_signature(self, authority_public_key: Union[Ed25519PublicKey, Ed25519PrivateKey, str, bytes, None] = None) -> bool:
        if not self.ed25519_signature:
            return False
        key_source = authority_public_key if authority_public_key is not None else self.issuer_public_key_hex
        if not key_source:
            return False
        try:
            pub = coerce_ed25519_public_key(key_source)
            sig_bytes = bytes.fromhex(self.ed25519_signature)
            pub.verify(sig_bytes, self.canonical_signing_bytes())
            return True
        except (ValueError, TypeError, InvalidSignature):
            return False


class ConsumedPermitLedger:
    """
    Persistent single-use permit ledger with:
      - `fcntl.flock(LOCK_EX)` atomic check-and-consume across concurrent OS processes.
      - Atomic temp-file + `os.replace` writes.
      - Fail-closed behavior: missing or corrupt ledger refuses ALL permits.
    """

    def __init__(self, ledger_path: Path):
        self.ledger_path = Path(ledger_path)
        self.lock_path = self.ledger_path.with_suffix(self.ledger_path.suffix + ".lock")

    @classmethod
    def create_new(cls, ledger_path: Path) -> "ConsumedPermitLedger":
        p = Path(ledger_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        lock_p = p.with_suffix(p.suffix + ".lock")
        with open(lock_p, "a+", encoding="utf-8") as lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                cls._atomic_write_json(p, {"consumed_permits": {}})
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        return cls(p)

    @staticmethod
    def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".ledger_tmp_")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(raw)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, str(path))
        except Exception:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise

    def _read_validated_unlocked(self) -> Optional[Dict[str, Any]]:
        if not self.ledger_path.is_file():
            return None
        try:
            data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(data, dict) or not isinstance(data.get("consumed_permits"), dict):
            return None
        return data

    def is_healthy(self) -> bool:
        return self._read_validated_unlocked() is not None

    def is_consumed(self, permit_id: str) -> bool:
        """
        Fail-closed: if the ledger is missing or corrupt, returns True (treated as unconsumable/refused).
        """
        data = self._read_validated_unlocked()
        if data is None:
            return True
        return permit_id in data["consumed_permits"]

    def try_consume(self, permit_id: str, effect_sha256: str) -> Tuple[bool, str]:
        """
        Atomically check and consume `permit_id` under `fcntl.flock(LOCK_EX)`.
        Returns `(True, "CONSUMED")` for the single winner, or `(False, reason)` otherwise.
        """
        if not self.ledger_path.parent.is_dir():
            return False, "LEDGER_CORRUPT_OR_MISSING: parent directory does not exist."
        try:
            lock_fh = open(self.lock_path, "a+", encoding="utf-8")
        except OSError as exc:
            return False, f"LEDGER_CORRUPT_OR_MISSING: cannot open lock file ({exc})."

        with lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                data = self._read_validated_unlocked()
                if data is None:
                    return False, "LEDGER_CORRUPT_OR_MISSING: ledger file is missing or contains invalid JSON."
                consumed = data["consumed_permits"]
                if permit_id in consumed:
                    return False, f"PERMIT_ALREADY_CONSUMED: single-use permit {permit_id!r} was already consumed."
                consumed[permit_id] = {
                    "consumed_at_unix": round(time.time(), 3),
                    "effect_sha256": effect_sha256,
                }
                self._atomic_write_json(self.ledger_path, data)
                return True, "CONSUMED"
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


def issue_signed_action_permit(
    *,
    permit_id: str,
    issuer_id: str,
    executor_seat: str,
    workspace_root: Path,
    target_rel_path: str,
    proposed_after_content: str,
    parent_packet: GuardedStatePacket,
    allow_globs: List[str],
    forbid_globs: List[str],
    authority_private_key: Union[Ed25519PrivateKey, str, bytes, None] = None,
    action_type: str = "WRITE_FILE",
    ttl_seconds: float = 3600.0,
) -> SignedActionPermit:
    """
    Human Authority Issuer: requires an `Ed25519PrivateKey` (never a public key!),
    inspects the current target file on disk, computes Before/After SHA-256 digests
    and policy-derived risk, and signs a single-use `SignedActionPermit`.
    """
    priv = coerce_ed25519_private_key(authority_private_key)
    target_file = (workspace_root / target_rel_path).resolve()
    before_text = target_file.read_text(encoding="utf-8") if target_file.is_file() else ""
    before_sha256 = hashlib.sha256(before_text.encode("utf-8")).hexdigest()
    after_sha256 = hashlib.sha256(proposed_after_content.encode("utf-8")).hexdigest()

    ast_rep = None
    if target_rel_path.endswith(".py"):
        ast_rep = audit_python_ast_diff(before_text, proposed_after_content, file_path=target_rel_path)

    derived_risk = derive_action_risk(target_rel_path, before_text, proposed_after_content, ast_rep)
    effective_risk = (
        derived_risk
        if RISK_ORDER.get(derived_risk, 1) > RISK_ORDER.get(parent_packet.risk.upper(), 1)
        else parent_packet.risk.upper()
    )

    now = round(time.time(), 3)
    permit = SignedActionPermit(
        permit_id=permit_id,
        issuer_id=issuer_id,
        executor_seat=executor_seat,
        action_type=action_type,
        target_rel_path=target_rel_path,
        expected_before_sha256=before_sha256,
        proposed_after_sha256=after_sha256,
        allow_globs=list(allow_globs),
        forbid_globs=list(forbid_globs),
        critical_10_digest=parent_packet.critical_10_digest(),
        admission_binding_digest=parent_packet.admission_binding_digest(effective_risk),
        authorized_risk=effective_risk,
        state_version=parent_packet.state_version,
        issued_at_unix=now,
        expires_at_unix=round(now + ttl_seconds, 3),
    )
    permit.sign(priv)
    return permit


# =============================================================================
# 4. GUARDED CROSS-SEAT EXECUTOR & 4-PLANE OBSERVATION RECEIPT
# =============================================================================

def execute_guarded_cross_seat_job(
    *,
    workspace_root: Path,
    permit: SignedActionPermit,
    authority_public_key: Union[Ed25519PublicKey, Ed25519PrivateKey, str, bytes, None],
    ledger: ConsumedPermitLedger,
    intended_parent_packet: GuardedStatePacket,
    candidate_child_packet: GuardedStatePacket,
    attempted_target_rel_path: str,
    attempted_after_content: str,
    handover_claim_text: str,
    attempted_action_type: str = "WRITE_FILE",
    simulate_post_write_corruption: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a single guarded cross-seat file operation using ONLY the authority's
    `Ed25519PublicKey` for verification.
    """
    root = workspace_root.resolve()
    snap = fa.open_airlock_snapshot(
        root,
        allow_globs=permit.allow_globs,
        forbid_globs=permit.forbid_globs,
    )

    target_path = (root / attempted_target_rel_path).resolve()
    before_text = target_path.read_text(encoding="utf-8") if target_path.is_file() else ""
    actual_before_sha256 = hashlib.sha256(before_text.encode("utf-8")).hexdigest()
    attempted_after_sha256 = hashlib.sha256(attempted_after_content.encode("utf-8")).hexdigest()

    ast_diff_rep = audit_python_ast_diff(
        before_text,
        attempted_after_content,
        handover_claim_text=handover_claim_text,
        file_path=attempted_target_rel_path,
    )

    policy_derived_risk = derive_action_risk(
        attempted_target_rel_path,
        before_text,
        attempted_after_content,
        ast_diff_rep,
    )
    candidate_crit10 = candidate_child_packet.critical_10_digest()
    candidate_admission_digest = candidate_child_packet.admission_binding_digest(
        max(
            [candidate_child_packet.risk.upper(), policy_derived_risk],
            key=lambda r: RISK_ORDER.get(r, 1),
        )
    )

    # -------------------------------------------------------------------------
    # PRE-EXECUTION ADMISSION GATES
    # -------------------------------------------------------------------------
    rejection_reasons: List[Dict[str, str]] = []

    # Gate 0: Ledger health (fail-closed if ledger is missing or corrupt)
    if not ledger.is_healthy():
        rejection_reasons.append({
            "code": "LEDGER_CORRUPT_OR_MISSING",
            "detail": f"ConsumedPermitLedger at {str(ledger.ledger_path)!r} is missing or corrupt; failing closed.",
        })

    # Gate 1: Cryptographic Ed25519 Signature on Permit
    if not authority_public_key or not permit.verify_signature(authority_public_key):
        rejection_reasons.append({
            "code": "INVALID_PERMIT_SIGNATURE",
            "detail": "SignedActionPermit Ed25519 signature verification failed or public key missing.",
        })

    # Gate 2: Single-Use Consumed Permit Replay Check (pre-check before mutations)
    if ledger.is_healthy() and ledger.is_consumed(permit.permit_id):
        rejection_reasons.append({
            "code": "PERMIT_ALREADY_CONSUMED",
            "detail": f"Single-use permit {permit.permit_id!r} was already consumed and cannot be replayed.",
        })

    # Gate 3: Permit Expiry Check
    if time.time() > permit.expires_at_unix:
        rejection_reasons.append({
            "code": "PERMIT_EXPIRED",
            "detail": f"Permit {permit.permit_id!r} expired at {permit.expires_at_unix}.",
        })

    # Gate 4: Protected 10-Field Context Continuity Check (`CRITICAL_FIELDS`)
    if candidate_crit10 != permit.critical_10_digest:
        dropped_unknowns = sorted(set(intended_parent_packet.unknowns) - set(candidate_child_packet.unknowns))
        dropped_invariants = sorted(set(intended_parent_packet.invariants) - set(candidate_child_packet.invariants))
        rejection_reasons.append({
            "code": "ALTERED_PROTECTED_CONTEXT",
            "detail": (
                f"Candidate 10-field critical digest ({candidate_crit10[:12]}...) != "
                f"authorized ({permit.critical_10_digest[:12]}...). "
                f"Dropped unknowns={dropped_unknowns}, dropped invariants={dropped_invariants}."
            ),
        })

    # Gate 5: Source-Derived Risk-Binding Hinge Check (`codec.py` vs `sovereign_harness.py`)
    if (
        candidate_child_packet.risk.upper() != permit.authorized_risk.upper()
        or RISK_ORDER.get(candidate_child_packet.risk.upper(), 1) < RISK_ORDER.get(policy_derived_risk, 1)
        or candidate_admission_digest != permit.admission_binding_digest
    ):
        rejection_reasons.append({
            "code": "RISK_ADMISSION_HINGE_BREACH",
            "detail": (
                f"Candidate risk={candidate_child_packet.risk!r} conflicts with authorized_risk={permit.authorized_risk!r} "
                f"and policy_derived_risk={policy_derived_risk!r} (10-field hash matched={candidate_crit10 == permit.critical_10_digest})."
            ),
        })

    # Gate 6: Restricted Effect Boundary (Exact Action Type, Target Path, Before Hash, Proposed After Hash, AST Diff)
    if attempted_action_type != permit.action_type:
        rejection_reasons.append({
            "code": "ACTION_TYPE_MISMATCH",
            "detail": f"Attempted action_type {attempted_action_type!r} != authorized {permit.action_type!r}.",
        })
    if attempted_target_rel_path != permit.target_rel_path:
        rejection_reasons.append({
            "code": "TARGET_PATH_MISMATCH",
            "detail": f"Attempted path {attempted_target_rel_path!r} != authorized {permit.target_rel_path!r}.",
        })
    if actual_before_sha256 != permit.expected_before_sha256:
        rejection_reasons.append({
            "code": "STALE_BEFORE_STATE_SHA256",
            "detail": "File on disk changed since permit was issued (expected_before_sha256 mismatch).",
        })
    if attempted_after_sha256 != permit.proposed_after_sha256:
        rejection_reasons.append({
            "code": "ALTERED_ACTION_PAYLOAD_SHA256",
            "detail": (
                f"Attempted payload SHA-256 ({attempted_after_sha256[:12]}...) != "
                f"authorized permit payload ({permit.proposed_after_sha256[:12]}...)."
            ),
        })
    if ast_diff_rep.get("ast_audit_status") == "AUDITED" and not ast_diff_rep["lawful_ast_diff"]:
        for v in ast_diff_rep["violations"]:
            rejection_reasons.append({
                "code": v["code"],
                "detail": v["detail"],
            })

    # Gate 7: Atomic flock check-and-consume right before execution
    if not rejection_reasons:
        consumed_ok, consume_reason = ledger.try_consume(permit.permit_id, attempted_after_sha256)
        if not consumed_ok:
            code = "LEDGER_CORRUPT_OR_MISSING" if "LEDGER_CORRUPT_OR_MISSING" in consume_reason else "PERMIT_ALREADY_CONSUMED"
            rejection_reasons.append({
                "code": code,
                "detail": consume_reason,
            })

    if rejection_reasons:
        post_airlock = fa.verify_airlock_state(snap)
        return {
            "executed": False,
            "committed": False,
            "classification": f"BLOCKED_{rejection_reasons[0]['code']}",
            "rejection_reasons": rejection_reasons,
            "planes": {
                "intended": {
                    "purpose": intended_parent_packet.purpose,
                    "unknowns": intended_parent_packet.unknowns,
                    "declared_risk": intended_parent_packet.risk,
                    "critical_10_digest": intended_parent_packet.critical_10_digest(),
                    "handover_claim_text": handover_claim_text,
                },
                "authorized": {
                    "permit_id": permit.permit_id,
                    "issuer_id": permit.issuer_id,
                    "action_type": permit.action_type,
                    "target_rel_path": permit.target_rel_path,
                    "authorized_after_sha256": permit.proposed_after_sha256,
                    "authorized_risk": permit.authorized_risk,
                    "admission_binding_digest": permit.admission_binding_digest,
                },
                "attempted": {
                    "executor_seat": permit.executor_seat,
                    "attempted_action_type": attempted_action_type,
                    "attempted_target_rel_path": attempted_target_rel_path,
                    "attempted_after_sha256": attempted_after_sha256,
                    "candidate_declared_risk": candidate_child_packet.risk,
                    "candidate_critical_10_digest": candidate_crit10,
                    "policy_derived_risk": policy_derived_risk,
                    "ast_semantic_diff": ast_diff_rep,
                },
                "observed": {
                    "disk_mutated": False,
                    "observed_after_sha256": actual_before_sha256,
                    "airlock_verdict": post_airlock["verdict"],
                    "rollback_executed": False,
                },
            },
        }

    # -------------------------------------------------------------------------
    # RESTRICTED EFFECT EXECUTION & INDEPENDENT POST-TASK WITNESS
    # -------------------------------------------------------------------------
    target_path.write_text(attempted_after_content, encoding="utf-8")

    if simulate_post_write_corruption is not None:
        target_path.write_text(simulate_post_write_corruption, encoding="utf-8")

    observed_bytes = target_path.read_bytes()
    observed_sha256 = hashlib.sha256(observed_bytes).hexdigest()
    airlock_audit = fa.verify_airlock_state(snap, handover_md_text=handover_claim_text)

    post_condition_ok = (
        observed_sha256 == permit.proposed_after_sha256
        and airlock_audit["lawful"] is True
        and airlock_audit["counts"]["authorized_changes"] == 1
        and airlock_audit["counts"]["boundary_breaches"] == 0
    )

    rollback_rep: Optional[Dict[str, Any]] = None
    if not post_condition_ok:
        rollback_rep = fa.rollback_airlock_snapshot(snap, remove_added_files=True)

    return {
        "executed": True,
        "committed": post_condition_ok,
        "classification": (
            "COMMITTED_AND_WITNESSED"
            if post_condition_ok
            else "OBSERVED_EFFECT_DIVERGENCE_ROLLED_BACK"
        ),
        "rejection_reasons": [],
        "planes": {
            "intended": {
                "purpose": intended_parent_packet.purpose,
                "unknowns": intended_parent_packet.unknowns,
                "declared_risk": intended_parent_packet.risk,
                "critical_10_digest": intended_parent_packet.critical_10_digest(),
                "handover_claim_text": handover_claim_text,
            },
            "authorized": {
                "permit_id": permit.permit_id,
                "issuer_id": permit.issuer_id,
                "action_type": permit.action_type,
                "target_rel_path": permit.target_rel_path,
                "authorized_after_sha256": permit.proposed_after_sha256,
                "authorized_risk": permit.authorized_risk,
                "admission_binding_digest": permit.admission_binding_digest,
            },
            "attempted": {
                "executor_seat": permit.executor_seat,
                "attempted_action_type": attempted_action_type,
                "attempted_target_rel_path": attempted_target_rel_path,
                "attempted_after_sha256": attempted_after_sha256,
                "candidate_declared_risk": candidate_child_packet.risk,
                "candidate_critical_10_digest": candidate_crit10,
                "policy_derived_risk": policy_derived_risk,
                "ast_semantic_diff": ast_diff_rep,
            },
            "observed": {
                "disk_mutated": post_condition_ok,
                "observed_after_sha256": observed_sha256,
                "matches_authorized_sha256": observed_sha256 == permit.proposed_after_sha256,
                "airlock_verdict": airlock_audit["verdict"],
                "rollback_executed": rollback_rep is not None,
                "rollback_report": rollback_rep,
            },
        },
    }


# =============================================================================
# 5. 6-CASE GUARDED CROSS-SEAT VERIFICATION SUITE
# =============================================================================

def run_guarded_cross_seat_breakthrough_suite() -> Dict[str, Any]:
    """
    Execute the 6-Case Guarded Cross-Seat Verification Suite in a temporary workspace
    using ephemeral Ed25519 asymmetric keys (Mac holds `authority_private_key`,
    executor receives ONLY `authority_public_key`).
    """
    before_py = (
        '"""Guard Service v1."""\n\n'
        "SAFETY_FLOOR = 0.80\n"
        "READ_ONLY = True\n\n"
        "def check_admission(score: float) -> bool:\n"
        '    """Return True if score meets safety floor."""\n'
        "    return score >= SAFETY_FLOOR\n"
    )
    approved_after_py = (
        '"""Guard Service v2 — Added audit receipt helper."""\n\n'
        "SAFETY_FLOOR = 0.80\n"
        "READ_ONLY = True\n\n"
        "def check_admission(score: float) -> bool:\n"
        '    """Return True if score meets safety floor."""\n'
        "    return score >= SAFETY_FLOOR\n\n"
        "def format_receipt(score: float) -> str:\n"
        '    """Format deterministic admission receipt."""\n'
        '    return f"ADMISSION:{score >= SAFETY_FLOOR}:{score:.3f}"\n'
    )
    malicious_after_py = (
        '"""Guard Service v2 — Updated docstrings only."""\n\n'
        "import subprocess\n\n"
        "SAFETY_FLOOR = 0.20\n"
        "READ_ONLY = False\n\n"
        "def check_admission(score: float) -> bool:\n"
        "    subprocess.run(['echo', 'pwn'], check=False)\n"
        "    return score >= SAFETY_FLOOR\n"
    )

    parent_packet = GuardedStatePacket(
        purpose="Add deterministic receipt formatter to src/guard_service.py without weakening SAFETY_FLOOR.",
        claim="Added format_receipt() to src/guard_service.py while preserving SAFETY_FLOOR = 0.80.",
        unknowns=["U<post_crash_commit_gap>", "U<external_key_hsm_binding>"],
        invariants=["I1_TRUTH_NO_FABRICATION", "I4_BOUNDARY_RESPECT"],
        authority=["SCOPE_WRITE:src/*", "SCOPE_READONLY:foreign/*"],
        participants=["Mac", "Caelorynth", "Aetheron"],
        affectedParties=["Lycheetah_Operators"],
        dissent=["v_Cael != v_Aetheron on immediate multi-file batching; restricted to single-file airlock."],
        valueFlow="EARNED_LIGHT_PRESERVED",
        recovery="AIRLOCK_ZLIB_SNAPSHOT_READY",
        risk="HIGH",
        state_version=1,
    )

    authority_private_key, authority_public_key = generate_ed25519_keypair()

    with tempfile.TemporaryDirectory() as tdir, tempfile.TemporaryDirectory() as auth_dir:
        ws = Path(tdir)
        (ws / "src").mkdir()
        (ws / "foreign").mkdir()
        target_file = ws / "src" / "guard_service.py"
        foreign_file = ws / "foreign" / "CAELORYNTH_PRIME.md"
        target_file.write_text(before_py, encoding="utf-8")
        foreign_file.write_text("# FOREIGN CONSTITUTION — READ ONLY\n", encoding="utf-8")

        ledger = ConsumedPermitLedger.create_new(Path(auth_dir) / "consumed_permits.json")

        permit_1 = issue_signed_action_permit(
            permit_id="PERMIT-CROSS-SEAT-001",
            issuer_id="Mac_Human_Authority",
            authority_private_key=authority_private_key,
            executor_seat="Aetheron",
            workspace_root=ws,
            target_rel_path="src/guard_service.py",
            proposed_after_content=approved_after_py,
            parent_packet=parent_packet,
            allow_globs=["src/*"],
            forbid_globs=["foreign/*"],
        )

        # CASE 2: Source-Derived Risk-Downgrade Hinge (`risk: HIGH -> LOW`)
        hinge_packet = copy.deepcopy(parent_packet)
        hinge_packet.risk = "LOW"
        case2_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_1,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=hinge_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=approved_after_py,
            handover_claim_text="Updated `src/guard_service.py` with `format_receipt()`.",
        )

        # CASE 3: Altered Protected Context (Erased Unknown `U<T>`)
        erased_u_packet = copy.deepcopy(parent_packet)
        erased_u_packet.unknowns = ["U<external_key_hsm_binding>"]
        case3_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_1,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=erased_u_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=approved_after_py,
            handover_claim_text="Updated `src/guard_service.py` with `format_receipt()`.",
        )

        # CASE 4: Altered Action Payload + AST Capability & Threshold Breach
        case4_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_1,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=parent_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=malicious_after_py,
            handover_claim_text="Updated docstrings only in `src/guard_service.py` and `check_admission()`.",
        )

        # CASE 1: Lawful Approved Cross-Seat Execution (`COMMITTED_AND_WITNESSED`)
        case1_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_1,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=parent_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=approved_after_py,
            handover_claim_text="Updated `src/guard_service.py` by adding `format_receipt()`.",
        )

        # CASE 5: Replay of Consumed Single-Use Permit (`PERMIT-CROSS-SEAT-001`)
        target_file.write_text(before_py, encoding="utf-8")
        case5_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_1,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=parent_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=approved_after_py,
            handover_claim_text="Updated `src/guard_service.py` by adding `format_receipt()`.",
        )

        # CASE 6: Post-Write Corruption / Interrupted Effect & Atomic Rollback
        permit_2 = issue_signed_action_permit(
            permit_id="PERMIT-CROSS-SEAT-002",
            issuer_id="Mac_Human_Authority",
            authority_private_key=authority_private_key,
            executor_seat="Aetheron",
            workspace_root=ws,
            target_rel_path="src/guard_service.py",
            proposed_after_content=approved_after_py,
            parent_packet=parent_packet,
            allow_globs=["src/*"],
            forbid_globs=["foreign/*"],
        )
        case6_res = execute_guarded_cross_seat_job(
            workspace_root=ws,
            permit=permit_2,
            authority_public_key=authority_public_key,
            ledger=ledger,
            intended_parent_packet=parent_packet,
            candidate_child_packet=parent_packet,
            attempted_target_rel_path="src/guard_service.py",
            attempted_after_content=approved_after_py,
            handover_claim_text="Updated `src/guard_service.py` by adding `format_receipt()`.",
            simulate_post_write_corruption="# CORRUPTED PARTIAL WRITE ON DISK\n",
        )
        restored_matches_before = (target_file.read_text(encoding="utf-8") == before_py)

    case4_codes = {r["code"] for r in case4_res["rejection_reasons"]}
    all_verified = (
        case1_res["committed"] is True
        and case1_res["classification"] == "COMMITTED_AND_WITNESSED"
        and case2_res["committed"] is False
        and case2_res["classification"] == "BLOCKED_RISK_ADMISSION_HINGE_BREACH"
        and parent_packet.critical_10_digest() == hinge_packet.critical_10_digest()
        and case3_res["committed"] is False
        and case3_res["classification"] == "BLOCKED_ALTERED_PROTECTED_CONTEXT"
        and case4_res["committed"] is False
        and "ALTERED_ACTION_PAYLOAD_SHA256" in case4_codes
        and "UNAUTHORIZED_CAPABILITY_ESCALATION" in case4_codes
        and "SILENT_THRESHOLD_WEAKENING" in case4_codes
        and "UNDISCLOSED_LOGIC_MUTATION" in case4_codes
        and case5_res["committed"] is False
        and case5_res["classification"] == "BLOCKED_PERMIT_ALREADY_CONSUMED"
        and case6_res["executed"] is True
        and case6_res["committed"] is False
        and case6_res["classification"] == "OBSERVED_EFFECT_DIVERGENCE_ROLLED_BACK"
        and case6_res["planes"]["observed"]["rollback_report"]["rollback_verified"] is True
        and restored_matches_before is True
    )

    return {
        "suite": "SUITE_8_GUARDED_CROSS_SEAT_EXECUTION_AND_AST_SEMANTIC_DIFF",
        "theorem": "THEOREM_8_GUARDED_CROSS_SEAT_EXECUTION_AND_AST_SEMANTIC_DIFF",
        "status": "VERIFIED" if all_verified else "FAILED",
        "all_6_cases_verified": all_verified,
        "summary": {
            "case_1_approved_cross_seat_job": case1_res["classification"],
            "case_2_risk_downgrade_hinge_caught": case2_res["classification"],
            "case_2_ten_field_hash_identical": parent_packet.critical_10_digest() == hinge_packet.critical_10_digest(),
            "case_3_altered_context_caught": case3_res["classification"],
            "case_4_ast_capability_and_threshold_breach_caught": sorted(case4_codes),
            "case_5_consumed_permit_replay_caught": case5_res["classification"],
            "case_6_post_write_divergence_rolled_back": case6_res["classification"],
        },
        "cases": {
            "case_1_approved": case1_res,
            "case_2_risk_hinge": case2_res,
            "case_3_altered_context": case3_res,
            "case_4_altered_action_ast": case4_res,
            "case_5_replay_rejected": case5_res,
            "case_6_corrupted_rollback": case6_res,
        },
    }


# =============================================================================
# 6. LIVE GIT REPOSITORY & WORKING-TREE CONSTITUTIONAL GATE (`audit-git`)
# =============================================================================

def audit_git_working_tree(
    repo_dir: Path,
    allow_globs: Optional[List[str]] = None,
    forbid_globs: Optional[List[str]] = None,
    handover_claim_text: str = "",
) -> Dict[str, Any]:
    """
    Inspect a real Git repository's working tree, staging area, and untracked files
    (`git status --porcelain -uall`) against `HEAD`:
      - Non-`.py` files are reported with `ast_audit_status="NOT_AUDITED"`.
      - Untracked `.py` files (`??`) are audited against an empty baseline (`""`) so
        newly added untracked Python files cannot sneak in capability escalations.
      - An unmodified working tree (`changed_files_count == 0`) is reported as
        `GIT_TREE_CLEAN_NO_CHANGES_TO_AUDIT` (not a proof of safety).
    """
    import subprocess
    import lamague_discourse as ld

    root = repo_dir.resolve()
    allow = list(allow_globs) if allow_globs else ["*"]
    forbid = list(forbid_globs) if forbid_globs else []

    head_proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    head_commit = head_proc.stdout.strip() if head_proc.returncode == 0 else "UNCOMMITTED_REPO"

    status_proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "-uall"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [ln for ln in status_proc.stdout.splitlines() if ln.strip()]

    file_audits: List[Dict[str, Any]] = []
    boundary_breaches: List[Dict[str, Any]] = []
    ast_violations: List[Dict[str, Any]] = []
    highest_risk = "LOW"
    first_verified_receipt: Optional[Dict[str, str]] = None

    for ln in lines:
        status_code = ln[:2].strip()
        rel_path = ln[3:].strip()
        if " -> " in rel_path:
            rel_path = rel_path.split(" -> ")[-1].strip()

        ok, policy_reason = fa._is_path_authorized(rel_path, allow, forbid)
        full_p = root / rel_path
        after_src = full_p.read_text(encoding="utf-8", errors="replace") if full_p.is_file() else None
        if full_p.is_file() and first_verified_receipt is None:
            raw_b = full_p.read_bytes()
            first_verified_receipt = {
                "path": str(full_p),
                "sha256": hashlib.sha256(raw_b).hexdigest(),
            }

        before_src: Optional[str] = ""
        if head_commit != "UNCOMMITTED_REPO" and status_code != "??":
            show_proc = subprocess.run(
                ["git", "-C", str(root), "show", f"HEAD:{rel_path}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if show_proc.returncode == 0:
                before_src = show_proc.stdout

        if rel_path.endswith(".py") and after_src is not None:
            ast_rep = audit_python_ast_diff(
                before_src or "",
                after_src,
                handover_claim_text=handover_claim_text,
                file_path=rel_path,
            )
            ast_status = ast_rep.get("ast_audit_status", "AUDITED")
            if not ast_rep.get("lawful_ast_diff", True):
                for v in ast_rep.get("violations", []):
                    ast_violations.append({"rel_path": rel_path, **v})
        else:
            ast_rep = audit_python_ast_diff("", "", file_path=rel_path)
            ast_status = "NOT_AUDITED"

        file_risk = derive_action_risk(rel_path, before_src, after_src, ast_rep)
        if RISK_ORDER.get(file_risk, 1) > RISK_ORDER.get(highest_risk, 1):
            highest_risk = file_risk

        entry = {
            "rel_path": rel_path,
            "git_status": status_code,
            "authorized_path": ok,
            "policy_reason": policy_reason,
            "derived_risk": file_risk,
            "ast_audit_status": ast_status,
            "ast_semantic_diff": ast_rep,
        }
        file_audits.append(entry)
        if not ok:
            boundary_breaches.append(entry)

    if len(file_audits) == 0:
        lawful = True
        verdict = "GIT_TREE_CLEAN_NO_CHANGES_TO_AUDIT"
        summary_en = f"Unknown Git working tree at {head_commit[:8]}: 0 changed files to audit."
    else:
        lawful = (len(boundary_breaches) == 0) and (len(ast_violations) == 0)
        verdict = "GIT_TREE_CLEAN_AND_LAWFUL" if lawful else "GIT_TREE_VIOLATION_DETECTED"
        summary_en = (
            f"Witnessed Git working tree at {head_commit[:8]}: {len(file_audits)} changed files, "
            f"witnessed risk {highest_risk}, lawful={lawful}."
            if lawful
            else f"Refuted Git working tree at {head_commit[:8]}: high risk boundary or AST violation detected."
        )

    sig = inspect.signature(ld.translate_english_to_lamague_v22)
    if "receipt" in sig.parameters and lawful and first_verified_receipt is not None:
        lamague_seal = ld.translate_english_to_lamague_v22(summary_en, receipt=first_verified_receipt)
    else:
        lamague_seal = ld.translate_english_to_lamague_v22(summary_en)

    return {
        "repo_dir": str(root),
        "head_commit": head_commit,
        "changed_files_count": len(file_audits),
        "lawful_working_tree": lawful,
        "verdict": verdict,
        "highest_derived_risk": highest_risk,
        "boundary_breaches_count": len(boundary_breaches),
        "ast_violations_count": len(ast_violations),
        "boundary_breaches": boundary_breaches,
        "ast_violations": ast_violations,
        "files": file_audits,
        "lamague_v22_seal": {
            "sxp_v22_utterance": lamague_seal["sxp_v22_utterance"],
            "core_v04_expression": lamague_seal["core_v04_expression"],
            "r4_semantic_hash": lamague_seal["r4_semantic_hash"],
        },
    }


# =============================================================================
# 7. CLI INTERFACE
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="guarded-handoff",
        description="Lycheetah Guarded Cross-Seat Executor & AST Semantic Diff Auditor (Faculty #15)",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_prove = sub.add_parser("prove", help="Run the 6-Case Guarded Cross-Seat Verification Suite")
    p_prove.add_argument("--json", action="store_true", help="Emit JSON output")

    p_ast = sub.add_parser("ast-diff", help="Audit semantic AST diff & capability escalations between two files")
    p_ast.add_argument("before_py", help="Path to Before file")
    p_ast.add_argument("after_py", help="Path to After file")
    p_ast.add_argument("--claim", default="", help="Optional handover claim text to cross-check against AST diff")
    p_ast.add_argument("--json", action="store_true", help="Emit JSON output")

    p_git = sub.add_parser("audit-git", help="Audit a live Git repository working tree against HEAD, scope globs & AST gates")
    p_git.add_argument("--repo", default=".", help="Path to Git repository (default: current directory)")
    p_git.add_argument("--allow", action="append", default=[], help="Allowed write glob (e.g. 'src/*')")
    p_git.add_argument("--forbid", action="append", default=[], help="Forbidden read-only glob (e.g. 'foreign/*')")
    p_git.add_argument("--claim", default="", help="Optional commit/handover claim text to verify against AST diffs")
    p_git.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args(argv)
    cmd = args.cmd or "prove"

    if cmd == "ast-diff":
        b_text = Path(args.before_py).read_text(encoding="utf-8")
        a_text = Path(args.after_py).read_text(encoding="utf-8")
        rep = audit_python_ast_diff(b_text, a_text, handover_claim_text=args.claim, file_path=str(args.after_py))
        if getattr(args, "json", False):
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            print(f"AST Audit Status: {rep['ast_audit_status']} | Lawful: {rep['lawful_ast_diff']} (Violations: {rep['violations_count']})")
            for v in rep.get("violations", []):
                print(f"  - [{v['code']}] {v['detail']}")
        return 0 if rep["lawful_ast_diff"] is True else 1

    if cmd == "audit-git":
        rep = audit_git_working_tree(
            Path(args.repo),
            allow_globs=args.allow or ["*"],
            forbid_globs=args.forbid or [],
            handover_claim_text=args.claim,
        )
        if getattr(args, "json", False):
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            print(f"Git Working Tree Verdict: {rep['verdict']} (HEAD={rep['head_commit'][:12]}, Changed={rep['changed_files_count']}, Risk={rep['highest_derived_risk']})")
            print(f"LAMAGUE Ω v2.2 Seal     : {rep['lamague_v22_seal']['sxp_v22_utterance']}")
            for v in rep.get("ast_violations", []):
                print(f"  - [AST:{v['code']}] {v['rel_path']}: {v['detail']}")
        return 0 if rep["lawful_working_tree"] else 1

    rep = run_guarded_cross_seat_breakthrough_suite()
    if getattr(args, "json", False):
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print(f"  LYCHEETAH GUARDED CROSS-SEAT EXECUTOR (SUITE 8): {rep['status']}")
        print("=" * 78)
        s = rep["summary"]
        print(f"  • Case 1 (Approved Cross-Seat Job)       : {s['case_1_approved_cross_seat_job']}")
        print(f"  • Case 2 (Risk-Downgrade Hinge Closed)   : {s['case_2_risk_downgrade_hinge_caught']} (10-field hash identical: {s['case_2_ten_field_hash_identical']})")
        print(f"  • Case 3 (Altered Context / Unknowns)    : {s['case_3_altered_context_caught']}")
        print(f"  • Case 4 (AST Capability/Threshold Gate) : {', '.join(s['case_4_ast_capability_and_threshold_breach_caught'])}")
        print(f"  • Case 5 (Single-Use Permit Replay)      : {s['case_5_consumed_permit_replay_caught']}")
        print(f"  • Case 6 (Post-Write Divergence Rollback): {s['case_6_post_write_divergence_rolled_back']}")
        print("=" * 78)
    return 0 if rep["all_6_cases_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
