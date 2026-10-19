"""Lycheetah Sovereign Choice Forge VI — attested approval and mediated local effects.

RESEARCH ONLY. Approval is authenticated to an out-of-band PINNED PUBLIC KEY,
not necessarily to a living, informed, uncoerced person. Signer private keys
MUST remain outside the agent/host proposal path. The SQLite database and
CommitFence are privileged host internals; do not expose those resources to
agents. The host owns the clock. There is NO network provider integration.

The real upstream CommitFence and Forge V AtomicChoiceLedger are reused;
this wrapper adds atomic signed-authority updates and a signed-event gate.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from hashlib import sha256
import base64
import json
import re
import time
import sqlite3
from pathlib import Path
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from research_support import Action
from choice_ledger import AtomicChoiceLedger
from commit_fence import CommitFence

SCHEMA = "lycheetah.choice-attestation.v1"
FIELDS = frozenset({"schema", "kind", "key_id", "principal", "scope_key", "expected_version",
                    "nonce", "issued_at", "expires_at", "purpose", "action_hash"})
KINDS = {"APPROVE", "WITHDRAW"}
MAX_TTL_SECONDS = 300
CLOCK_SKEW_SECONDS = 30


def canonical_json(obj: dict) -> bytes:
    """Defined UTF-8 serialization within restricted JSON types (not RFC 8785)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def verify_signed_message(message: dict, signature_b64: str,
                          keys: dict[str, tuple[str, Ed25519PublicKey]],
                          now: int) -> None:
    """Raise ValueError for invalid host-pinned signature/fields/validity window."""
    if type(message) is not dict or set(message) != FIELDS:
        raise ValueError("invalid_message_fields")
    if message["schema"] != SCHEMA or message["kind"] not in KINDS:
        raise ValueError("invalid_schema_or_kind")
    for field in ("key_id", "principal", "scope_key", "nonce", "purpose", "action_hash"):
        if type(message[field]) is not str:
            raise ValueError("invalid_type_" + field)
    if not (1 <= len(message["principal"]) <= 128 and
            1 <= len(message["scope_key"]) <= 128 and
            1 <= len(message["key_id"]) <= 128 and
            re.fullmatch(r"[0-9a-f]{32}", message["nonce"])):
        raise ValueError("invalid_identifiers")
    for field in ("expected_version", "issued_at", "expires_at"):
        if type(message[field]) is not int:
            raise ValueError("invalid_integer_" + field)
    if message["expected_version"] < 0:
        raise ValueError("invalid_expected_version")
    if (message["issued_at"] > now + CLOCK_SKEW_SECONDS or
        now > message["expires_at"] or
        message["expires_at"] <= message["issued_at"] or
        message["expires_at"] - message["issued_at"] > MAX_TTL_SECONDS):
        raise ValueError("approval_not_in_valid_time_window")
    if message["kind"] == "APPROVE":
        if (not 1 <= len(message["purpose"]) <= 500 or
            not re.fullmatch(r"[a-f0-9]{64}", message["action_hash"])):
            raise ValueError("invalid_approval_contents")
    else:
        if message["purpose"] != "" or message["action_hash"] != "":
            raise ValueError("withdrawal_must_be_content_free")
    key_entry = keys.get(message["key_id"])
    if key_entry is None or key_entry[0] != message["principal"]:
        raise ValueError("unrecognised_principal_key")
    if type(signature_b64) is not str or len(signature_b64) > 128:
        raise ValueError("malformed_signature")
    try:
        raw = base64.b64decode(signature_b64, validate=True)
        if len(raw) != 64:
            raise ValueError("malformed_signature")
        key_entry[1].verify(raw, canonical_json(message))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise ValueError("invalid_signature") from exc


@dataclass(frozen=True)
class GateResult:
    accepted: bool
    reason: str
    version: int | None = None
    generation: int | None = None
    effect_state: str | None = None


class TrustedClockCommitFence(CommitFence):
    """Keep upstream commit; register a host-owned clock on every DB connection."""
    def __init__(self, db_path: str | Path, clock: Callable[[], int]):
        self._trusted_clock = clock
        super().__init__(db_path)

    def connect(self):
        con = super().connect()
        con.create_function("lycheetah_trusted_time", 0,
                            lambda: int(self._trusted_clock()))
        return con


class AttestedChoiceGateway:
    """Trusted host facade. Do NOT place this object or its SQLite file in AI tools.

    The public untrusted protocol is a JSON message and a detached signature,
    plus proposed Action. Pinned key registration is trusted operator work.
    """
    def __init__(self, db_path: str | Path,
                 keys: dict[str, tuple[str, Ed25519PublicKey]],
                 clock: Callable[[], int] | None = None,
                 *, enforce_finality_guard: bool = True):
        self._clock = clock if clock is not None else lambda: int(time.time())
        self._fence = TrustedClockCommitFence(db_path, self._clock)
        self._ledger = AtomicChoiceLedger(self._fence)
        self._keys = keys.copy()
        # False is a deliberately insecure negative-control fixture only.
        self._enforce_finality_guard = enforce_finality_guard
        with closing(self._fence.connect()) as con:
            con.execute('''CREATE TABLE IF NOT EXISTS signed_authority_events (
                nonce TEXT PRIMARY KEY,
                principal TEXT NOT NULL,
                scope_key TEXT NOT NULL,
                key_id TEXT NOT NULL,
                event_kind TEXT NOT NULL,
                version INTEGER NOT NULL,
                generation INTEGER NOT NULL,
                action_hash TEXT NOT NULL,
                issued_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                message_digest TEXT NOT NULL,
                signature_b64 TEXT NOT NULL)''')
            if self._enforce_finality_guard:
                con.execute('''CREATE TRIGGER IF NOT EXISTS attested_effect_finality_guard
                    BEFORE INSERT ON effects
                    BEGIN
                      SELECT CASE WHEN NOT EXISTS (
                        SELECT 1 FROM handles h
                        JOIN choice_intents i ON i.principal=h.principal AND i.scope_key=h.scope_key
                        JOIN authorities a ON a.principal=h.principal AND a.scope_key=h.scope_key
                        JOIN signed_authority_events s ON s.principal=i.principal
                          AND s.scope_key=i.scope_key AND s.version=i.version
                        WHERE h.handle_id=NEW.handle_id AND h.effect_id=NEW.effect_id
                          AND h.action_hash=NEW.action_hash AND h.generation=NEW.generation
                          AND i.active=1 AND a.active=1
                          AND i.generation=a.generation AND i.generation=NEW.generation
                          AND i.action_hash=NEW.action_hash
                          AND s.event_kind='APPROVE'
                          AND s.generation=NEW.generation
                          AND s.action_hash=NEW.action_hash
                          AND s.expires_at>=lycheetah_trusted_time()
                      ) THEN RAISE(ABORT, 'attestation_invalid_at_finality') END;
                    END''')

    def submit(self, message: dict, signature_b64: str, action: Action | None = None,
               *, inject_failure: bool = False) -> GateResult:
        """Apply externally signed choice event atomically with authority fence.

        inject_failure is a test-only hook used to demonstrate rollback.
        """
        now = int(self._clock())  # Host clock, never provided by untrusted message alone.
        verify_signed_message(message, signature_b64, self._keys, now)
        principal, scope = message["principal"], message["scope_key"]
        kind = message["kind"]
        ah = ""
        if kind == "APPROVE":
            if action is None:
                return GateResult(False, "missing_action")
            ah = self._ledger._check_action(principal, scope, action)
            if ah != message["action_hash"]:
                return GateResult(False, "signed_action_mismatch")
        elif action is not None:
            return GateResult(False, "withdrawal_takes_no_action")

        with closing(self._fence.connect()) as con:
            con.execute("BEGIN IMMEDIATE")
            try:
                previous = con.execute('''SELECT * FROM choice_intents
                    WHERE principal=? AND scope_key=?''', (principal, scope)).fetchone()
                authority = con.execute('''SELECT generation,active FROM authorities
                    WHERE principal=? AND scope_key=?''', (principal,scope)).fetchone()
                actual_version = 0 if previous is None else int(previous["version"])
                if actual_version != message["expected_version"]:
                    con.execute("ROLLBACK")
                    return GateResult(False, "stale_expected_version")
                if previous is not None and (authority is None or
                    previous["generation"] != authority["generation"] or
                    bool(previous["active"]) != bool(authority["active"])):
                    con.execute("ROLLBACK")
                    return GateResult(False, "out_of_band_authority_change")
                if con.execute('SELECT 1 FROM signed_authority_events WHERE nonce=?',
                               (message["nonce"],)).fetchone():
                    con.execute("ROLLBACK")
                    return GateResult(False, "replayed_nonce")
                generation = 1 if authority is None else int(authority["generation"]) + 1
                version = actual_version + 1
                active = (kind == "APPROVE")
                con.execute('''INSERT INTO authorities(principal,scope_key,generation,active)
                    VALUES(?,?,?,?) ON CONFLICT(principal,scope_key) DO UPDATE SET
                    generation=excluded.generation,active=excluded.active''',
                    (principal, scope, generation, int(active)))
                if kind == "APPROVE":
                    purpose = message["purpose"]
                else:
                    purpose = "" if previous is None else previous["purpose"]
                    ah = "" if previous is None else previous["action_hash"]
                self._ledger._write(con, principal, scope, version, generation, purpose,
                                    ah, active, kind, "signed_host_verified")
                con.execute('''INSERT INTO signed_authority_events
                    (nonce,principal,scope_key,key_id,event_kind,version,generation,
                     action_hash,issued_at,expires_at,message_digest,signature_b64)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (message["nonce"],principal,scope,message["key_id"],kind,
                     version,generation,ah,message["issued_at"],message["expires_at"],
                     sha256(canonical_json(message)).hexdigest(),signature_b64))
                if inject_failure:
                    raise RuntimeError("simulated_precommit_failure")
                con.execute("COMMIT")
            except BaseException:
                con.execute("ROLLBACK")
                raise
        return GateResult(True, "signed_choice_recorded", version, generation)

    def dispatch(self, action: Action) -> GateResult:
        """Mediated local effect. Untrusted agent gets this facade, not raw fence.

        Each dispatch checks newest choice and signed-event row before handle
        issue; upstream fence serialises revocation and protected local commit.
        """
        if type(action) is not Action:
            return GateResult(False, "invalid_action_type")
        principal,scope = action.principal,action.tool
        with closing(self._fence.connect()) as con:
            row = con.execute('''SELECT i.version,i.generation,i.active,i.action_hash,
                a.active AS auth_active,a.generation AS auth_generation,
                s.event_kind,s.version AS signed_version,s.generation AS signed_generation,
                s.action_hash AS signed_action_hash,s.expires_at AS signed_expiry
                FROM choice_intents i
                LEFT JOIN authorities a ON a.principal=i.principal AND a.scope_key=i.scope_key
                LEFT JOIN signed_authority_events s ON s.principal=i.principal
                    AND s.scope_key=i.scope_key AND s.version=i.version
                WHERE i.principal=? AND i.scope_key=?''', (principal,scope)).fetchone()
        if row is None:
            return GateResult(False, "no_signed_approval")
        if (not row["active"] or not row["auth_active"] or
            row["generation"] != row["auth_generation"]):
            return GateResult(False, "authority_not_active_or_mismatched")
        if (row["event_kind"] != "APPROVE" or row["signed_version"] != row["version"] or
            row["signed_generation"] != row["generation"] or
            row["action_hash"] != row["signed_action_hash"]):
            return GateResult(False, "no_matching_attestation")
        if int(self._clock()) > row["signed_expiry"]:
            return GateResult(False, "approval_expired")
        if row["action_hash"] != action.action_hash:
            return GateResult(False, "action_not_endorsed")
        v = self._ledger.issue(principal,scope,action)
        if not v.allowed:
            return GateResult(False, v.reason)
        # A concurrent revoke/revision between issue and commit is blocked by
        # upstream CommitFence's generation check at protected local finality.
        try:
            result = self._ledger.commit(v.handle,action)
        except sqlite3.IntegrityError as exc:
            if "attestation_invalid_at_finality" in str(exc):
                return GateResult(False, "attestation_invalid_at_finality",row["version"],
                                  row["generation"],"DENIED")
            raise
        if result.state == "COMMITTED":
            return GateResult(True, "new_local_effect_committed", row["version"],
                              row["generation"], result.state)
        if result.state == "CONFIRMED":
            return GateResult(True, "previously_committed_same_effect",row["version"],
                              row["generation"],result.state)
        return GateResult(False, "upstream_"+result.reason, row["version"],
                          row["generation"],result.state)

    def records(self) -> list[dict]:
        """Metadata-only audit, NOT independently tamper-proof."""
        with closing(self._fence.connect()) as con:
            return [dict(x) for x in con.execute('''SELECT nonce,principal,scope_key,key_id,
                event_kind,version,generation,action_hash,issued_at,expires_at,
                message_digest FROM signed_authority_events ORDER BY rowid''')]
