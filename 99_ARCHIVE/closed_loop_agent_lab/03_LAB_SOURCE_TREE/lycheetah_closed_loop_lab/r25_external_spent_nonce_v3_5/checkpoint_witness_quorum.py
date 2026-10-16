"""Independent witness quorum for Lycheetah checkpoint records (v3.3 prototype).

The input record must already be signed by the configured primary anchor and is
verified through remote_anchor_http.verify_record. A witness votes once per
(database_id, sequence) and protects its high-water mark through a separate CAS
Guard interface. SQLiteCASGuard is only a local test/reference adapter; production
must provide a separately administered, non-rollbackable compare-and-swap service.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import json
import re
import secrets
from datetime import datetime, timezone
import sqlite3
import threading
from pathlib import Path
from typing import Any, Mapping, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from remote_anchor_http import AnchorProtocolError, canonical, sha256, verify_record, b64, unb64, iso, utc_now, parse_time

VERSION = "lycheetah-witness-quorum-v3.3"
DOMAIN_WITNESS = b"lycheetah-checkpoint-witness-v3.3\n"
HEX64 = re.compile(r"^[a-f0-9]{64}$")
VALID_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
VALID_CHALLENGE = re.compile(r"^[A-Za-z0-9_-]{32,128}$")


class WitnessProtocolError(ValueError):
    """A checkpoint, witness vote, or quorum certificate is invalid."""


class EquivocationError(WitnessProtocolError):
    """An attempted second checkpoint for a locked database sequence."""


@dataclass(frozen=True)
class Head:
    database_id: str
    sequence: int
    record_sha256: str
    previous_record_sha256: str | None
    logical_sha256: str
    anchor_server_key_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "database_id": self.database_id,
            "sequence": self.sequence,
            "record_sha256": self.record_sha256,
            "previous_record_sha256": self.previous_record_sha256,
            "logical_sha256": self.logical_sha256,
            "anchor_server_key_id": self.anchor_server_key_id,
        }


def verified_head(record: Mapping[str, Any], anchor_keys: Mapping[str, Ed25519PublicKey]) -> Head:
    _validate_anchor_registry(anchor_keys)
    try:
        verified = verify_record(record, anchor_keys)
    except (AnchorProtocolError, TypeError, KeyError) as exc:
        raise WitnessProtocolError(f"primary-anchor-record-invalid:{exc}") from None
    body = verified.body
    return Head(
        database_id=body["database_id"],
        sequence=body["sequence"],
        record_sha256=verified.record_sha256,
        previous_record_sha256=body["previous_record_sha256"],
        logical_sha256=body["logical_sha256"],
        anchor_server_key_id=verified.server_key_id,
    )


def _validate_witness_registry(witness_keys: Mapping[str, Ed25519PublicKey]) -> None:
    if not isinstance(witness_keys, Mapping) or not witness_keys:
        raise WitnessProtocolError("witness-key-registry-invalid")
    if any(not isinstance(wid, str) or not VALID_ID.fullmatch(wid)
           or not isinstance(key, Ed25519PublicKey) for wid, key in witness_keys.items()):
        raise WitnessProtocolError("witness-key-registry-invalid")
    # Quorum arithmetic counts identities. If two identities resolve to the same
    # public key, one compromised private key can impersonate multiple votes.
    fingerprints = [key.public_bytes(Encoding.Raw, PublicFormat.Raw)
                    for key in witness_keys.values()]
    if len(fingerprints) != len(set(fingerprints)):
        raise WitnessProtocolError("witness-key-registry-duplicate-public-key")


def _validate_anchor_registry(anchor_keys: Mapping[str, Ed25519PublicKey]) -> None:
    if not isinstance(anchor_keys, Mapping) or not anchor_keys:
        raise WitnessProtocolError("anchor-key-registry-invalid")
    if any(not isinstance(key_id, str) or not VALID_ID.fullmatch(key_id)
           or not isinstance(key, Ed25519PublicKey) for key_id, key in anchor_keys.items()):
        raise WitnessProtocolError("anchor-key-registry-invalid")


def _validate_head(head: Head) -> None:
    if not VALID_ID.fullmatch(head.database_id):
        raise WitnessProtocolError("database-id-invalid")
    if type(head.sequence) is not int or head.sequence < 1:
        raise WitnessProtocolError("sequence-invalid")
    if not HEX64.fullmatch(head.record_sha256) or not HEX64.fullmatch(head.logical_sha256):
        raise WitnessProtocolError("head-digest-invalid")
    parent = head.previous_record_sha256
    if head.sequence == 1 and parent is not None:
        raise WitnessProtocolError("genesis-parent-invalid")
    if head.sequence > 1 and (not isinstance(parent, str) or not HEX64.fullmatch(parent)):
        raise WitnessProtocolError("parent-hash-invalid")
    if not VALID_ID.fullmatch(head.anchor_server_key_id):
        raise WitnessProtocolError("anchor-key-id-invalid")


class MonotonicGuard(Protocol):
    def get_head(self, database_id: str) -> tuple[int, str | None] | None:
        """Return (sequence, record hash), or None before the first checkpoint."""

    def compare_and_swap(
        self, database_id: str, expected_sequence: int, expected_hash: str | None,
        new_sequence: int, new_hash: str, new_parent_hash: str | None,
    ) -> bool:
        """Advance exactly one sequence iff the current head matches expected."""


class SQLiteCASGuard:
    """Separate SQLite monotonic-guard reference adapter for tests only.

    This deliberately does not claim protection against an attacker who can roll
    back both this file and the witness's local vote ledger.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._thread_lock = threading.RLock()
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("CREATE TABLE IF NOT EXISTS monotonic_heads (database_id TEXT PRIMARY KEY, sequence INTEGER NOT NULL, record_sha256 TEXT NOT NULL)")
            db.commit()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def get_head(self, database_id: str) -> tuple[int, str | None] | None:
        with self._thread_lock, closing(self._db()) as db:
            row = db.execute("SELECT sequence,record_sha256 FROM monotonic_heads WHERE database_id=?", (database_id,)).fetchone()
            return (int(row["sequence"]), str(row["record_sha256"])) if row else None

    def compare_and_swap(self, database_id: str, expected_sequence: int, expected_hash: str | None,
                         new_sequence: int, new_hash: str, new_parent_hash: str | None) -> bool:
        if new_sequence != expected_sequence + 1 or new_parent_hash != expected_hash:
            return False
        with self._thread_lock, closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT sequence,record_sha256 FROM monotonic_heads WHERE database_id=?", (database_id,)).fetchone()
            current_seq, current_hash = (int(row["sequence"]), str(row["record_sha256"])) if row else (0, None)
            if (current_seq, current_hash) != (expected_sequence, expected_hash):
                db.rollback()
                return False
            if row:
                db.execute("UPDATE monotonic_heads SET sequence=?,record_sha256=? WHERE database_id=?",
                           (new_sequence, new_hash, database_id))
            else:
                db.execute("INSERT INTO monotonic_heads(database_id,sequence,record_sha256) VALUES(?,?,?)",
                           (database_id, new_sequence, new_hash))
            db.commit()
            return True


class CheckpointWitness:
    """A witness that signs one head per sequence, protected by an external guard."""
    def __init__(self, witness_id: str, private_key: Ed25519PrivateKey,
                 local_ledger_path: str | Path, guard: MonotonicGuard,
                 anchor_keys: Mapping[str, Ed25519PublicKey]):
        if not VALID_ID.fullmatch(witness_id):
            raise WitnessProtocolError("witness-id-invalid")
        if not isinstance(private_key, Ed25519PrivateKey):
            raise WitnessProtocolError("witness-private-key-invalid")
        _validate_anchor_registry(anchor_keys)
        self.witness_id = witness_id
        self.private_key = private_key
        self.guard = guard
        self.anchor_keys = dict(anchor_keys)
        self.local_ledger_path = Path(local_ledger_path).resolve()
        guard_path = getattr(guard, "path", None)
        if guard_path is not None and Path(guard_path).resolve() == self.local_ledger_path:
            raise WitnessProtocolError("witness-guard-must-use-independent-storage")
        self.local_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.local_ledger_path)) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("CREATE TABLE IF NOT EXISTS witness_votes (database_id TEXT NOT NULL, sequence INTEGER NOT NULL, record_sha256 TEXT NOT NULL, statement_json TEXT NOT NULL, vote_json TEXT NOT NULL, PRIMARY KEY(database_id,sequence))")
            db.commit()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.local_ledger_path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _checked_guard_head(self, database_id: str) -> tuple[int, str | None]:
        """Validate the CAS guard's return value at this trust boundary.

        A remote or pluggable guard is an input boundary. In particular, bool
        must not be accepted as an integer sequence merely because True == 1.
        """
        current = self.guard.get_head(database_id)
        if current is None:
            return (0, None)
        if not isinstance(current, tuple) or len(current) != 2:
            raise WitnessProtocolError("monotonic-guard-head-shape-invalid")
        sequence, record_hash = current
        if type(sequence) is not int or sequence < 1:
            raise WitnessProtocolError("monotonic-guard-sequence-invalid")
        if not isinstance(record_hash, str) or not HEX64.fullmatch(record_hash):
            raise WitnessProtocolError("monotonic-guard-digest-invalid")
        return sequence, record_hash

    def report_head(self, database_id: str, challenge_nonce: str) -> dict[str, Any]:
        """Sign this witness's current guarded head for one client challenge.

        The verifier must generate a fresh unpredictable nonce. This prevents a
        previously captured status report from satisfying a new freshness query.
        It does not by itself make the local SQLite guard rollback-proof.
        """
        if not isinstance(database_id, str) or not VALID_ID.fullmatch(database_id):
            raise WitnessProtocolError("database-id-invalid")
        if not isinstance(challenge_nonce, str) or not VALID_CHALLENGE.fullmatch(challenge_nonce):
            raise WitnessProtocolError("freshness-challenge-invalid")
        sequence, record_hash = self._checked_guard_head(database_id)
        if sequence > 0:
            # A present local vote at this sequence must not contradict the guard.
            with closing(self._db()) as db:
                row = db.execute("SELECT record_sha256 FROM witness_votes WHERE database_id=? AND sequence=?",
                                 (database_id, sequence)).fetchone()
            if row and row["record_sha256"] != record_hash:
                raise WitnessProtocolError("guard-local-head-disagreement")
        body = {
            "version": VERSION,
            "kind": "fresh-head",
            "witness_id": self.witness_id,
            "database_id": database_id,
            "sequence": sequence,
            "record_sha256": record_hash,
            "challenge_nonce": challenge_nonce,
            "issued_at": iso(utc_now()),
        }
        return {**body, "signature_b64": b64(self.private_key.sign(DOMAIN_WITNESS + canonical(body)))}


    def attest(self, record: Mapping[str, Any]) -> dict[str, Any]:
        head = verified_head(record, self.anchor_keys)
        _validate_head(head)
        statement = {"version": VERSION, **head.to_dict()}
        statement_json = canonical(statement).decode("utf-8")

        # Reject local conflicting history before touching the monotonic guard.
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT record_sha256,statement_json,vote_json FROM witness_votes WHERE database_id=? AND sequence=?",
                                  (head.database_id, head.sequence)).fetchone()
            if existing:
                if existing["record_sha256"] != head.record_sha256 or existing["statement_json"] != statement_json:
                    db.rollback()
                    raise EquivocationError("witness-already-voted-for-different-head-at-sequence")
                stored_vote = json.loads(existing["vote_json"])
                db.commit()
                # Local storage is not itself a trust root: verify the signature
                # before returning a persisted vote to an aggregator.
                try:
                    verify_vote(stored_vote, {self.witness_id: self.private_key.public_key()}, head)
                except WitnessProtocolError:
                    raise WitnessProtocolError("stored-witness-vote-failed-authentication") from None
                # Even stored votes must agree with surviving monotonic state.
                guarded_sequence, guarded_hash = self._checked_guard_head(head.database_id)
                if guarded_sequence == 0 or guarded_sequence < head.sequence:
                    raise WitnessProtocolError("guard-behind-local-vote-ledger")
                if guarded_sequence == head.sequence and guarded_hash != head.record_sha256:
                    raise WitnessProtocolError("guard-local-head-disagreement")
                return stored_vote
            db.commit()

        expected_sequence, expected_hash = self._checked_guard_head(head.database_id)

        if head.sequence == expected_sequence and head.record_sha256 == expected_hash:
            # Recovery case: guard commit succeeded, local vote insert was lost.
            # Ed25519 signatures are deterministic, so the same vote is reproducible.
            pass
        elif head.sequence == expected_sequence + 1 and head.previous_record_sha256 == expected_hash:
            if not self.guard.compare_and_swap(
                head.database_id, expected_sequence, expected_hash,
                head.sequence, head.record_sha256, head.previous_record_sha256,
            ):
                refreshed = self._checked_guard_head(head.database_id)
                if refreshed != (expected_sequence, expected_hash):
                    raise EquivocationError("monotonic-guard-cas-lost-to-competing-head")
                # Same old head means a transient CAS/storage issue; do not guess.
                raise WitnessProtocolError("monotonic-guard-cas-failed")
        elif head.sequence == expected_sequence and head.record_sha256 != expected_hash:
            raise EquivocationError("conflicting-head-at-locked-sequence")
        elif head.sequence < expected_sequence:
            raise WitnessProtocolError("stale-head-not-in-local-vote-ledger")
        else:
            raise WitnessProtocolError("checkpoint-not-next-linked-head")

        vote_body = {"version": VERSION, "witness_id": self.witness_id, **head.to_dict()}
        signature = b64(self.private_key.sign(DOMAIN_WITNESS + canonical(vote_body)))
        vote = {**vote_body, "signature_b64": signature}
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT INTO witness_votes(database_id,sequence,record_sha256,statement_json,vote_json) VALUES(?,?,?,?,?)",
                           (head.database_id, head.sequence, head.record_sha256, statement_json, canonical(vote).decode("utf-8")))
                db.commit()
            except sqlite3.IntegrityError:
                db.rollback()
                # A competing thread may have recorded a vote after our first read.
                row = db.execute("SELECT record_sha256,statement_json,vote_json FROM witness_votes WHERE database_id=? AND sequence=?",
                                 (head.database_id, head.sequence)).fetchone()
                if row and row["record_sha256"] == head.record_sha256 and row["statement_json"] == statement_json:
                    return json.loads(row["vote_json"])
                raise EquivocationError("concurrent-witness-vote-conflict") from None
        return vote


def witness_roster_digest(witness_ids: list[str] | tuple[str, ...]) -> str:
    if not witness_ids or any(not isinstance(w, str) or not VALID_ID.fullmatch(w) for w in witness_ids):
        raise WitnessProtocolError("witness-roster-invalid")
    if len(witness_ids) != len(set(witness_ids)):
        raise WitnessProtocolError("witness-roster-duplicate-id")
    return sha256(canonical(sorted(witness_ids)))


def quorum_threshold(witness_count: int, max_byzantine: int) -> int:
    if type(witness_count) is not int or type(max_byzantine) is not int or max_byzantine < 0:
        raise WitnessProtocolError("quorum-parameters-invalid")
    if witness_count < (3 * max_byzantine + 1):
        raise WitnessProtocolError("witness-roster-too-small-for-fault-budget")
    # Require quorum intersection strictly larger than the Byzantine budget:
    # 2*q - n >= f+1. This reduces to floor((n+f)/2)+1.
    return ((witness_count + max_byzantine) // 2) + 1


def _vote_statement(vote: Mapping[str, Any]) -> dict[str, Any]:
    required = {"version", "witness_id", "database_id", "sequence", "record_sha256",
                "previous_record_sha256", "logical_sha256", "anchor_server_key_id", "signature_b64"}
    if set(vote) != required or vote.get("version") != VERSION:
        raise WitnessProtocolError("witness-vote-shape-invalid")
    witness_id = vote.get("witness_id")
    if not isinstance(witness_id, str) or not VALID_ID.fullmatch(witness_id):
        raise WitnessProtocolError("witness-id-invalid")
    fields = {k: vote[k] for k in ("database_id", "sequence", "record_sha256", "previous_record_sha256", "logical_sha256", "anchor_server_key_id")}
    head = Head(**fields)
    _validate_head(head)
    if not isinstance(vote["signature_b64"], str):
        raise WitnessProtocolError("witness-signature-invalid")
    return {"version": VERSION, "witness_id": witness_id, **head.to_dict()}


def verify_vote(vote: Mapping[str, Any], witness_keys: Mapping[str, Ed25519PublicKey], expected_head: Head) -> str:
    _validate_witness_registry(witness_keys)
    body = _vote_statement(vote)
    witness_id = body["witness_id"]
    key = witness_keys.get(witness_id)
    if key is None:
        raise WitnessProtocolError("witness-key-untrusted")
    if body != {"version": VERSION, **expected_head.to_dict(), "witness_id": witness_id}:
        raise WitnessProtocolError("witness-vote-head-mismatch")
    try:
        key.verify(unb64(vote["signature_b64"]), DOMAIN_WITNESS + canonical(body))
    except (InvalidSignature, AnchorProtocolError, ValueError):
        raise WitnessProtocolError("witness-signature-invalid") from None
    return witness_id


def create_certificate(record: Mapping[str, Any], votes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                       anchor_keys: Mapping[str, Ed25519PublicKey], witness_keys: Mapping[str, Ed25519PublicKey],
                       *, max_byzantine: int = 1) -> dict[str, Any]:
    _validate_witness_registry(witness_keys)
    head = verified_head(record, anchor_keys)
    threshold = quorum_threshold(len(witness_keys), max_byzantine)
    used: set[str] = set()
    normalized_votes: list[dict[str, Any]] = []
    for vote in votes:
        witness_id = verify_vote(vote, witness_keys, head)
        if witness_id in used:
            raise WitnessProtocolError("duplicate-witness-vote")
        used.add(witness_id)
        normalized_votes.append(dict(vote))
    if len(used) < threshold:
        raise WitnessProtocolError(f"witness-quorum-insufficient:{len(used)}/{threshold}")
    normalized_votes.sort(key=lambda v: v["witness_id"])
    body = {
        "version": VERSION,
        "database_id": head.database_id,
        "sequence": head.sequence,
        "record_sha256": head.record_sha256,
        "logical_sha256": head.logical_sha256,
        "parent_record_sha256": head.previous_record_sha256,
        "anchor_server_key_id": head.anchor_server_key_id,
        "max_byzantine": max_byzantine,
        "threshold": threshold,
        "witness_roster": sorted(witness_keys),
        "witness_roster_sha256": witness_roster_digest(list(witness_keys)),
        "anchor_record": dict(record),
        "votes": normalized_votes,
    }
    return {**body, "certificate_sha256": sha256(canonical(body))}


def verify_certificate(certificate: Mapping[str, Any], anchor_keys: Mapping[str, Ed25519PublicKey],
                       witness_keys: Mapping[str, Ed25519PublicKey], *, expected_max_byzantine: int = 1) -> Head:
    _validate_witness_registry(witness_keys)
    required = {"version", "database_id", "sequence", "record_sha256", "logical_sha256", "parent_record_sha256",
                "anchor_server_key_id", "max_byzantine", "threshold", "witness_roster", "witness_roster_sha256",
                "anchor_record", "votes", "certificate_sha256"}
    if not isinstance(certificate, Mapping) or set(certificate) != required or certificate.get("version") != VERSION:
        raise WitnessProtocolError("certificate-shape-invalid")

    # Strict JSON wire types: Python bool is a subclass of int, and `True == 1`.
    # Do not let scalar equality make malformed signed/checksummed records valid.
    if not isinstance(certificate["database_id"], str) or not VALID_ID.fullmatch(certificate["database_id"]):
        raise WitnessProtocolError("certificate-database-id-invalid")
    if type(certificate["sequence"]) is not int or certificate["sequence"] < 1:
        raise WitnessProtocolError("certificate-sequence-invalid")
    if type(certificate["max_byzantine"]) is not int or certificate["max_byzantine"] < 0:
        raise WitnessProtocolError("certificate-fault-budget-invalid")
    if type(certificate["threshold"]) is not int or certificate["threshold"] < 1:
        raise WitnessProtocolError("certificate-threshold-invalid")
    for key in ("record_sha256", "logical_sha256", "witness_roster_sha256", "certificate_sha256"):
        if not isinstance(certificate[key], str) or not HEX64.fullmatch(certificate[key]):
            raise WitnessProtocolError(f"certificate-{key.replace('_', '-')}-invalid")
    parent = certificate["parent_record_sha256"]
    if parent is not None and (not isinstance(parent, str) or not HEX64.fullmatch(parent)):
        raise WitnessProtocolError("certificate-parent-hash-invalid")
    if not isinstance(certificate["anchor_server_key_id"], str) or not VALID_ID.fullmatch(certificate["anchor_server_key_id"]):
        raise WitnessProtocolError("certificate-anchor-key-id-invalid")

    roster = certificate["witness_roster"]
    if not isinstance(roster, list) or any(not isinstance(wid, str) for wid in roster):
        raise WitnessProtocolError("certificate-roster-invalid")
    if roster != sorted(witness_keys) or certificate["witness_roster_sha256"] != witness_roster_digest(list(witness_keys)):
        raise WitnessProtocolError("certificate-roster-mismatch")
    expected_threshold = quorum_threshold(len(witness_keys), expected_max_byzantine)
    if certificate["max_byzantine"] != expected_max_byzantine or certificate["threshold"] != expected_threshold:
        raise WitnessProtocolError("certificate-quorum-policy-mismatch")
    record = certificate["anchor_record"]
    if not isinstance(record, Mapping):
        raise WitnessProtocolError("certificate-anchor-record-invalid")
    head = verified_head(record, anchor_keys)
    if (certificate["database_id"], certificate["sequence"], certificate["record_sha256"],
        certificate["logical_sha256"], certificate["parent_record_sha256"], certificate["anchor_server_key_id"]) != (
        head.database_id, head.sequence, head.record_sha256, head.logical_sha256,
        head.previous_record_sha256, head.anchor_server_key_id):
        raise WitnessProtocolError("certificate-head-mismatch")
    votes = certificate["votes"]
    if not isinstance(votes, list):
        raise WitnessProtocolError("certificate-votes-invalid")
    unique: set[str] = set()
    for vote in votes:
        witness_id = verify_vote(vote, witness_keys, head)
        if witness_id in unique:
            raise WitnessProtocolError("duplicate-witness-vote")
        unique.add(witness_id)
    if len(unique) < expected_threshold:
        raise WitnessProtocolError("witness-quorum-insufficient")
    body = {k: certificate[k] for k in required if k != "certificate_sha256"}
    if certificate["certificate_sha256"] != sha256(canonical(body)):
        raise WitnessProtocolError("certificate-digest-invalid")
    return head


def verify_certificate_chain(certificates: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                              anchor_keys: Mapping[str, Ed25519PublicKey],
                              witness_keys: Mapping[str, Ed25519PublicKey],
                              *, expected_max_byzantine: int = 1) -> tuple[Head, ...]:
    """Verify a contiguous chain of quorum certificates from genesis.

    Use this for a new client or restored verifier. For incremental verification,
    first verify a stored chain/certificate and then compare the next certificate's
    parent to that already-trusted head. A standalone non-genesis certificate only
    proves that a quorum signed its stated head; it is not a substitute for history.
    """
    if not isinstance(certificates, (list, tuple)) or not certificates:
        raise WitnessProtocolError("certificate-chain-empty-or-invalid")
    verified_heads: list[Head] = []
    for certificate in certificates:
        head = verify_certificate(certificate, anchor_keys, witness_keys,
                                  expected_max_byzantine=expected_max_byzantine)
        if not verified_heads:
            if head.sequence != 1 or head.previous_record_sha256 is not None:
                raise WitnessProtocolError("certificate-chain-must-start-at-genesis")
        else:
            previous = verified_heads[-1]
            if head.database_id != previous.database_id:
                raise WitnessProtocolError("certificate-chain-database-switch")
            if head.sequence != previous.sequence + 1:
                raise WitnessProtocolError("certificate-chain-sequence-gap-or-replay")
            if head.previous_record_sha256 != previous.record_sha256:
                raise WitnessProtocolError("certificate-chain-parent-mismatch")
        verified_heads.append(head)
    return tuple(verified_heads)


@dataclass(frozen=True)
class FreshHeadQuorum:
    database_id: str
    sequence: int
    record_sha256: str | None
    challenge_nonce: str
    agreeing_witness_ids: tuple[str, ...]
    dissenting_witness_ids: tuple[str, ...]


def new_freshness_challenge() -> str:
    """Generate a 256-bit unpredictable freshness nonce for a live quorum read."""
    return secrets.token_urlsafe(32).rstrip("=")


def verify_fresh_head_quorum(reports: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                             witness_keys: Mapping[str, Ed25519PublicKey], *,
                             database_id: str, challenge_nonce: str,
                             max_byzantine: int = 1, max_clock_skew_seconds: int = 60) -> FreshHeadQuorum:
    """Verify fresh nonce-bound head reports and require a matching quorum."""
    _validate_witness_registry(witness_keys)
    if not isinstance(reports, (list, tuple)) or not reports:
        raise WitnessProtocolError("fresh-head-reports-invalid")
    if not isinstance(database_id, str) or not VALID_ID.fullmatch(database_id):
        raise WitnessProtocolError("database-id-invalid")
    if not isinstance(challenge_nonce, str) or not VALID_CHALLENGE.fullmatch(challenge_nonce):
        raise WitnessProtocolError("freshness-challenge-invalid")
    if type(max_clock_skew_seconds) is not int or max_clock_skew_seconds < 1:
        raise WitnessProtocolError("freshness-clock-window-invalid")
    threshold = quorum_threshold(len(witness_keys), max_byzantine)
    seen: set[str] = set()
    groups: dict[tuple[int, str | None], list[str]] = {}
    now = datetime.now(timezone.utc)
    required = {"version", "kind", "witness_id", "database_id", "sequence", "record_sha256",
                "challenge_nonce", "issued_at", "signature_b64"}
    for report in reports:
        if not isinstance(report, Mapping) or set(report) != required:
            raise WitnessProtocolError("fresh-head-report-shape-invalid")
        body = {k: report[k] for k in required if k != "signature_b64"}
        wid = report.get("witness_id")
        if report.get("version") != VERSION or report.get("kind") != "fresh-head":
            raise WitnessProtocolError("fresh-head-report-version-invalid")
        if not isinstance(wid, str) or wid not in witness_keys:
            raise WitnessProtocolError("witness-key-untrusted")
        if wid in seen:
            raise WitnessProtocolError("duplicate-fresh-head-witness")
        seen.add(wid)
        if report.get("database_id") != database_id:
            raise WitnessProtocolError("fresh-head-database-mismatch")
        if report.get("challenge_nonce") != challenge_nonce:
            raise WitnessProtocolError("fresh-head-challenge-mismatch")
        seq = report.get("sequence")
        digest = report.get("record_sha256")
        if type(seq) is not int or seq < 0:
            raise WitnessProtocolError("fresh-head-sequence-invalid")
        if (seq == 0 and digest is not None) or (seq > 0 and (not isinstance(digest, str) or not HEX64.fullmatch(digest))):
            raise WitnessProtocolError("fresh-head-digest-invalid")
        try:
            issued_at = parse_time(report["issued_at"])
        except AnchorProtocolError:
            raise WitnessProtocolError("fresh-head-timestamp-invalid") from None
        if abs((now - issued_at).total_seconds()) > max_clock_skew_seconds:
            raise WitnessProtocolError("fresh-head-report-stale")
        try:
            witness_keys[wid].verify(unb64(report["signature_b64"]), DOMAIN_WITNESS + canonical(body))
        except (InvalidSignature, AnchorProtocolError, ValueError, TypeError):
            raise WitnessProtocolError("fresh-head-signature-invalid") from None
        groups.setdefault((seq, digest), []).append(wid)
    winner = [(key, ids) for key, ids in groups.items() if len(ids) >= threshold]
    if len(winner) != 1:
        raise WitnessProtocolError("fresh-head-quorum-disagreement")
    (sequence, record_sha256), agreeing = winner[0]
    dissenting = tuple(sorted(seen - set(agreeing)))
    return FreshHeadQuorum(database_id, sequence, record_sha256, challenge_nonce,
                           tuple(sorted(agreeing)), dissenting)


def verify_current_chain(certificates: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                         freshness_reports: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                         anchor_keys: Mapping[str, Ed25519PublicKey],
                         witness_keys: Mapping[str, Ed25519PublicKey], *,
                         database_id: str, challenge_nonce: str, max_byzantine: int = 1,
                         max_clock_skew_seconds: int = 60) -> tuple[Head, ...]:
    """Verify history and raw freshness reports together.

    Deliberately accepts signed reports rather than a caller-constructible
    ``FreshHeadQuorum`` summary. That prevents a caller from forging the summary
    object and skipping signature, nonce, age, roster and quorum verification.
    """
    freshness = verify_fresh_head_quorum(
        freshness_reports, witness_keys, database_id=database_id,
        challenge_nonce=challenge_nonce, max_byzantine=max_byzantine,
        max_clock_skew_seconds=max_clock_skew_seconds,
    )
    heads = verify_certificate_chain(certificates, anchor_keys, witness_keys,
                                     expected_max_byzantine=max_byzantine)
    last = heads[-1]
    if last.database_id != freshness.database_id or last.sequence != freshness.sequence or last.record_sha256 != freshness.record_sha256:
        raise WitnessProtocolError("certificate-chain-is-not-current-fresh-quorum-head")
    return heads


def find_equivocation(first: Mapping[str, Any], second: Mapping[str, Any],
                      anchor_keys: Mapping[str, Ed25519PublicKey], witness_keys: Mapping[str, Ed25519PublicKey],
                      *, max_byzantine: int = 1) -> list[dict[str, Any]]:
    """Return signed double-votes if two valid quorum certificates conflict."""
    h1 = verify_certificate(first, anchor_keys, witness_keys, expected_max_byzantine=max_byzantine)
    h2 = verify_certificate(second, anchor_keys, witness_keys, expected_max_byzantine=max_byzantine)
    if h1.database_id != h2.database_id or h1.sequence != h2.sequence or h1.record_sha256 == h2.record_sha256:
        raise WitnessProtocolError("certificates-do-not-conflict-at-same-sequence")
    v1 = {v["witness_id"]: v for v in first["votes"]}
    v2 = {v["witness_id"]: v for v in second["votes"]}
    evidence=[]
    for witness_id in sorted(set(v1) & set(v2)):
        evidence.append({"witness_id": witness_id, "first_vote": dict(v1[witness_id]), "second_vote": dict(v2[witness_id])})
    if not evidence:
        raise WitnessProtocolError("conflicting-certificates-without-overlap")
    return evidence
