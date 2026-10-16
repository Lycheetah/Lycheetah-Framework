"""Durable one-use freshness challenge lifecycle for the Lycheetah witness quorum.

This is a local reference adapter, not a production anti-rollback database.
A deployment must place the integrity key and monotonic challenge store in a
separately administered trust domain if rollback/host compromise is in scope.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import hashlib
import hmac
import sqlite3
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from remote_anchor_http import canonical
from checkpoint_witness_quorum import (
    HEX64, VALID_ID, VALID_CHALLENGE, Head,
    new_freshness_challenge, verify_current_chain, quorum_threshold, VERSION as WITNESS_PROTOCOL_VERSION,
    _validate_anchor_registry, _validate_witness_registry,
)


class ChallengeLifecycleError(ValueError):
    """Freshness challenge was absent, invalid, expired, or already consumed."""


@dataclass(frozen=True)
class FreshnessChallenge:
    """Public challenge envelope. The fields are not trusted without ledger lookup."""
    database_id: str
    nonce: str
    issued_at_ms: int
    expires_at_ms: int


class DurableFreshnessVerifier:
    """Verify signed chain/current-head evidence and atomically consume its nonce.

    The exact challenge policy is stored in the authenticated ledger when the
    nonce is issued. Callers cannot lower the Byzantine budget or widen the
    response clock window when submitting reports.

    All signature/quorum checks are performed by the v3.3 verifier. Consumption
    happens only after those checks pass, and a transaction makes successful
    consumption one-use under concurrent verifier calls.
    """

    def __init__(
        self,
        ledger_path: str | Path,
        anchor_keys: Mapping[str, Any],
        witness_keys: Mapping[str, Any],
        *,
        integrity_key: bytes,
        max_byzantine: int = 1,
        max_clock_skew_seconds: int = 60,
        challenge_ttl_seconds: int = 120,
        clock_ms: Callable[[], int] | None = None,
        nonce_factory: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
            raise ValueError("integrity_key-must-be-at-least-32-bytes")
        if type(max_byzantine) is not int or max_byzantine < 0:
            raise ValueError("max_byzantine-invalid")
        if type(max_clock_skew_seconds) is not int or max_clock_skew_seconds < 1:
            raise ValueError("max_clock_skew_seconds-invalid")
        if type(challenge_ttl_seconds) is not int or not 1 <= challenge_ttl_seconds <= 3600:
            raise ValueError("challenge_ttl_seconds-invalid")
        _validate_anchor_registry(anchor_keys)
        _validate_witness_registry(witness_keys)
        quorum_threshold(len(witness_keys), max_byzantine)
        self._anchor_key_registry = dict(anchor_keys)
        self._witness_key_registry = dict(witness_keys)
        self.path = Path(ledger_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._integrity_key = bytes(integrity_key)
        self._max_byzantine = max_byzantine
        self._max_clock_skew_seconds = max_clock_skew_seconds
        self._challenge_ttl_ms = challenge_ttl_seconds * 1000
        anchor_fingerprints = [
            (key_id, key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex())
            for key_id, key in sorted(self._anchor_key_registry.items())
        ]
        witness_fingerprints = [
            (witness_id, key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex())
            for witness_id, key in sorted(self._witness_key_registry.items())
        ]
        self._policy_sha256 = hashlib.sha256(canonical({
            "protocol_version": WITNESS_PROTOCOL_VERSION,
            "anchor_keys": anchor_fingerprints,
            "witness_keys": witness_fingerprints,
            "max_byzantine": self._max_byzantine,
            "max_clock_skew_seconds": self._max_clock_skew_seconds,
            "challenge_ttl_ms": self._challenge_ttl_ms,
        })).hexdigest()
        self._clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)
        self._nonce_factory = nonce_factory or new_freshness_challenge
        with closing(self._db()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS freshness_challenges (
                nonce TEXT NOT NULL PRIMARY KEY,
                database_id TEXT NOT NULL,
                issued_at_ms INTEGER NOT NULL,
                expires_at_ms INTEGER NOT NULL,
                max_byzantine INTEGER NOT NULL,
                max_clock_skew_seconds INTEGER NOT NULL,
                policy_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('PENDING','CONSUMED')),
                consumed_at_ms INTEGER,
                row_hmac TEXT NOT NULL
            )""")
            actual_info = db.execute("PRAGMA table_info(freshness_challenges)").fetchall()
            actual_schema = [(row["name"], row["type"].upper(), row["notnull"], row["pk"]) for row in actual_info]
            expected_schema = [
                ("nonce", "TEXT", 1, 1),
                ("database_id", "TEXT", 1, 0),
                ("issued_at_ms", "INTEGER", 1, 0),
                ("expires_at_ms", "INTEGER", 1, 0),
                ("max_byzantine", "INTEGER", 1, 0),
                ("max_clock_skew_seconds", "INTEGER", 1, 0),
                ("policy_sha256", "TEXT", 1, 0),
                ("state", "TEXT", 1, 0),
                ("consumed_at_ms", "INTEGER", 0, 0),
                ("row_hmac", "TEXT", 1, 0),
            ]
            if actual_schema != expected_schema:
                raise ChallengeLifecycleError("challenge-ledger-schema-incompatible")
            db.commit()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        return db

    @staticmethod
    def _row_body(row: Mapping[str, Any]) -> dict[str, Any]:
        return {name: row[name] for name in (
            "nonce", "database_id", "issued_at_ms", "expires_at_ms",
            "max_byzantine", "max_clock_skew_seconds", "policy_sha256", "state", "consumed_at_ms",
        )}

    def _row_hmac(self, row: Mapping[str, Any]) -> str:
        return hmac.new(self._integrity_key, canonical(self._row_body(row)), hashlib.sha256).hexdigest()

    def _validate_row(self, row: Mapping[str, Any]) -> None:
        required = {"nonce", "database_id", "issued_at_ms", "expires_at_ms",
                    "max_byzantine", "max_clock_skew_seconds", "policy_sha256", "state", "consumed_at_ms", "row_hmac"}
        if set(row.keys()) != required:
            raise ChallengeLifecycleError("challenge-ledger-row-shape-invalid")
        if not isinstance(row["nonce"], str) or not row["nonce"]:
            raise ChallengeLifecycleError("challenge-ledger-nonce-invalid")
        if not isinstance(row["database_id"], str) or not VALID_ID.fullmatch(row["database_id"]):
            raise ChallengeLifecycleError("challenge-ledger-database-id-invalid")
        for name in ("issued_at_ms", "expires_at_ms", "max_byzantine", "max_clock_skew_seconds"):
            if type(row[name]) is not int:
                raise ChallengeLifecycleError(f"challenge-ledger-{name}-invalid")
        if row["issued_at_ms"] < 0 or row["expires_at_ms"] <= row["issued_at_ms"]:
            raise ChallengeLifecycleError("challenge-ledger-time-range-invalid")
        if row["max_byzantine"] < 0 or row["max_clock_skew_seconds"] < 1:
            raise ChallengeLifecycleError("challenge-ledger-policy-invalid")
        if not isinstance(row["policy_sha256"], str) or not HEX64.fullmatch(row["policy_sha256"]):
            raise ChallengeLifecycleError("challenge-ledger-policy-digest-invalid")
        if row["state"] not in {"PENDING", "CONSUMED"}:
            raise ChallengeLifecycleError("challenge-ledger-state-invalid")
        if row["state"] == "PENDING" and row["consumed_at_ms"] is not None:
            raise ChallengeLifecycleError("challenge-ledger-state-time-invalid")
        if row["state"] == "CONSUMED" and type(row["consumed_at_ms"]) is not int:
            raise ChallengeLifecycleError("challenge-ledger-state-time-invalid")
        if not isinstance(row["row_hmac"], str) or not HEX64.fullmatch(row["row_hmac"]):
            raise ChallengeLifecycleError("challenge-ledger-authenticator-invalid")
        expected = self._row_hmac(row)
        if not hmac.compare_digest(expected, row["row_hmac"]):
            raise ChallengeLifecycleError("challenge-ledger-integrity-invalid")

    def issue(self, database_id: str) -> FreshnessChallenge:
        if not isinstance(database_id, str) or not VALID_ID.fullmatch(database_id):
            raise ChallengeLifecycleError("database-id-invalid")
        issued = self._clock_ms()
        if type(issued) is not int or issued < 0:
            raise ChallengeLifecycleError("clock-invalid")
        expires = issued + self._challenge_ttl_ms
        for _ in range(3):
            nonce = self._nonce_factory()
            if not isinstance(nonce, str) or not VALID_CHALLENGE.fullmatch(nonce):
                raise ChallengeLifecycleError("nonce-generator-invalid")
            row = {
                "nonce": nonce,
                "database_id": database_id,
                "issued_at_ms": issued,
                "expires_at_ms": expires,
                "max_byzantine": self._max_byzantine,
                "max_clock_skew_seconds": self._max_clock_skew_seconds,
                "policy_sha256": self._policy_sha256,
                "state": "PENDING",
                "consumed_at_ms": None,
            }
            tag = self._row_hmac(row)
            with closing(self._db()) as db:
                db.execute("BEGIN IMMEDIATE")
                try:
                    db.execute("INSERT INTO freshness_challenges VALUES(?,?,?,?,?,?,?,?,?,?)", (
                        row["nonce"], row["database_id"], row["issued_at_ms"], row["expires_at_ms"],
                        row["max_byzantine"], row["max_clock_skew_seconds"], row["policy_sha256"],
                        row["state"], row["consumed_at_ms"], tag,
                    ))
                    db.commit()
                    return FreshnessChallenge(database_id, nonce, issued, expires)
                except sqlite3.IntegrityError:
                    db.rollback()
        raise ChallengeLifecycleError("nonce-collision-retry-exhausted")

    def _load_pending(self, nonce: str, *, database_id: str | None = None, now_ms: int | None = None) -> dict[str, Any]:
        if not isinstance(nonce, str) or not nonce:
            raise ChallengeLifecycleError("challenge-nonce-invalid")
        now = self._clock_ms() if now_ms is None else now_ms
        if type(now) is not int or now < 0:
            raise ChallengeLifecycleError("clock-invalid")
        with closing(self._db()) as db:
            raw = db.execute("SELECT * FROM freshness_challenges WHERE nonce=?", (nonce,)).fetchone()
        if raw is None:
            raise ChallengeLifecycleError("challenge-not-issued-by-this-verifier")
        row = dict(raw)
        self._validate_row(row)
        if database_id is not None and row["database_id"] != database_id:
            raise ChallengeLifecycleError("challenge-database-mismatch")
        if row["policy_sha256"] != self._policy_sha256:
            raise ChallengeLifecycleError("challenge-policy-changed")
        if row["state"] != "PENDING":
            raise ChallengeLifecycleError("challenge-already-consumed")
        if now >= row["expires_at_ms"]:
            raise ChallengeLifecycleError("challenge-expired")
        return row

    def verify_and_consume(
        self,
        certificates: Sequence[Mapping[str, Any]],
        freshness_reports: Sequence[Mapping[str, Any]],
        challenge: FreshnessChallenge,
    ) -> tuple[Head, ...]:
        """Verify history/currentness against a persisted challenge and consume it once.

        A caller-created envelope cannot mint a challenge: the nonce must exist in
        this verifier's ledger and pass its HMAC/state/time checks. Failed report
        verification leaves a pending challenge usable until expiry; successful
        concurrent attempts race on one conditional consumption transaction.
        """
        if not isinstance(challenge, FreshnessChallenge):
            raise ChallengeLifecycleError("challenge-envelope-invalid")
        row = self._load_pending(challenge.nonce, database_id=challenge.database_id)
        # Never trust caller-provided expires/issued metadata or quorum settings.
        heads = verify_current_chain(
            list(certificates), list(freshness_reports),
            self._anchor_key_registry, self._witness_key_registry,
            database_id=row["database_id"], challenge_nonce=row["nonce"],
            max_byzantine=row["max_byzantine"],
            max_clock_skew_seconds=row["max_clock_skew_seconds"],
        )
        consumed_at = self._clock_ms()
        if type(consumed_at) is not int or consumed_at < 0:
            raise ChallengeLifecycleError("clock-invalid")
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            current_raw = db.execute("SELECT * FROM freshness_challenges WHERE nonce=?", (row["nonce"],)).fetchone()
            if current_raw is None:
                db.rollback()
                raise ChallengeLifecycleError("challenge-not-issued-by-this-verifier")
            current = dict(current_raw)
            self._validate_row(current)
            if current["database_id"] != row["database_id"]:
                db.rollback()
                raise ChallengeLifecycleError("challenge-database-mismatch")
            if current["policy_sha256"] != self._policy_sha256:
                db.rollback()
                raise ChallengeLifecycleError("challenge-policy-changed")
            if current["state"] != "PENDING":
                db.rollback()
                raise ChallengeLifecycleError("challenge-already-consumed")
            if consumed_at >= current["expires_at_ms"]:
                db.rollback()
                raise ChallengeLifecycleError("challenge-expired")
            updated = {**self._row_body(current), "state": "CONSUMED", "consumed_at_ms": consumed_at}
            tag = self._row_hmac(updated)
            cursor = db.execute(
                "UPDATE freshness_challenges SET state='CONSUMED',consumed_at_ms=?,row_hmac=? "
                "WHERE nonce=? AND state='PENDING' AND row_hmac=?",
                (consumed_at, tag, current["nonce"], current["row_hmac"]),
            )
            if cursor.rowcount != 1:
                db.rollback()
                raise ChallengeLifecycleError("challenge-consume-race-lost")
            db.commit()
        return heads

