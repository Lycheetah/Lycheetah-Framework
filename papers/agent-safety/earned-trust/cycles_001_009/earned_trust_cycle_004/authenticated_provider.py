"""Earned Trust Cycle 003: local signed-intent and signed-commit evidence laboratory.

All operations are SYNTHETIC and run against one SQLite database on one host.
Authorization tokens and provider receipts use domain-separated HMAC-SHA256.
An HMAC is NOT a public signature, does NOT authenticate a real human, and does
NOT prove a refund occurred outside this local database.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any
import hmac
import json
import sqlite3

GENESIS = sha256(b"lycheetah.earned-trust.cycle-003.audit.genesis").hexdigest()
ACTION_KEYS = frozenset(("actor", "subject", "amount_cents", "scope"))
TOKEN_FIELDS = frozenset(("schema", "effect_id", "approval_id", "actor", "scope", "action_sha256", "subject_version", "policy_version", "issued_at", "expires_at", "nonce"))
PROOF_FIELDS = frozenset(("schema", "result", "effect_id", "approval_id", "token_sha256", "action_sha256", "subject_ref", "amount_cents", "observed_evidence_version", "observed_policy_version", "observed_authority_epoch", "committed_at", "audit_seq", "audit_hash"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def hash_obj(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()


def _mac(secret: bytes, domain: str, body: dict[str, Any]) -> str:
    return hmac.new(secret, domain.encode() + b"\0" + canonical(body), "sha256").hexdigest()


def seal(secret: bytes, domain: str, key_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"body": body, "auth": {"algorithm": "HMAC-SHA256", "key_id": key_id, "mac": _mac(secret, domain, body)}}


def verify_artifact(artifact: Any, secret: bytes, domain: str, key_id: str, required_fields: frozenset[str]) -> bool:
    if not isinstance(artifact, dict) or set(artifact) != {"body", "auth"}:
        return False
    body, auth = artifact["body"], artifact["auth"]
    if not isinstance(body, dict) or set(body) != required_fields:
        return False
    if not isinstance(auth, dict) or set(auth) != {"algorithm", "key_id", "mac"}:
        return False
    if auth["algorithm"] != "HMAC-SHA256" or auth["key_id"] != key_id:
        return False
    if not isinstance(auth["mac"], str) or len(auth["mac"]) != 64:
        return False
    try:
        expected = _mac(secret, domain, body)
    except (TypeError, ValueError, OverflowError):
        return False
    return hmac.compare_digest(auth["mac"], expected)


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def decode_wire(blob: bytes | str) -> dict[str, Any]:
    """Strict parser for untrusted JSON wire data, not a general JSON format."""
    if isinstance(blob, bytes):
        blob = blob.decode("utf-8", errors="strict")
    item = json.loads(blob, object_pairs_hook=_no_duplicate_keys,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite number")))
    if not isinstance(item, dict):
        raise ValueError("expected JSON object")
    return item


def valid_action(action: Any) -> bool:
    return (isinstance(action, dict) and set(action) == ACTION_KEYS
            and all(type(action[k]) is str and bool(action[k]) for k in ("actor", "subject", "scope"))
            and type(action["amount_cents"]) is int and 0 < action["amount_cents"] <= 2_147_483_647)


def valid_token_fields(body: Any) -> bool:
    return (isinstance(body, dict) and set(body) == TOKEN_FIELDS
            and body["schema"] == "earned-trust.authorization.v1"
            and all(type(body[k]) is str and bool(body[k]) for k in
                    ("effect_id", "approval_id", "actor", "scope", "action_sha256", "nonce"))
            and type(body["subject_version"]) is int and body["subject_version"] > 0
            and type(body["policy_version"]) is int and body["policy_version"] > 0
            and type(body["issued_at"]) is int and type(body["expires_at"]) is int
            and body["issued_at"] < body["expires_at"]
            and len(body["action_sha256"]) == 64)


@dataclass(frozen=True)
class Outcome:
    code: str
    committed: bool = False
    replay: bool = False
    receipt: dict[str, Any] | None = None


class LostResponse(ConnectionError):
    """Simulated transport failure after a confirmed local transaction."""


class TrustedIssuer:
    """Host-side token issuer. Its possession by a model would break the boundary."""
    def __init__(self, secret: bytes, key_id: str = "authority-lab-v1") -> None:
        if len(secret) < 32:
            raise ValueError("authority key must be at least 32 bytes")
        self.secret, self.key_id = secret, key_id

    def issue(self, *, action: dict[str, Any], effect_id: str, approval_id: str,
              subject_version: int, policy_version: int, now: int, expires_at: int,
              nonce: str) -> dict[str, Any]:
        if not valid_action(action):
            raise ValueError("invalid proposed action")
        body = {"schema": "earned-trust.authorization.v1", "effect_id": effect_id,
                "approval_id": approval_id, "actor": action["actor"], "scope": action["scope"],
                "action_sha256": hash_obj(action), "subject_version": subject_version,
                "policy_version": policy_version, "issued_at": now, "expires_at": expires_at,
                "nonce": nonce}
        if not valid_token_fields(body):
            raise ValueError("invalid token parameters")
        return seal(self.secret, "earned-trust.token.v1", self.key_id, body)


class _ClosingConnection(sqlite3.Connection):
    """Context manager that closes the descriptor after commit/rollback."""
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


class SignedSQLiteProvider:
    """One trust-domain provider; local atomicity, not remote transactions."""
    def __init__(self, path: str | Path, *, authority_secret: bytes, provider_secret: bytes,
                 authority_key_id: str = "authority-lab-v1", provider_key_id: str = "provider-lab-v1") -> None:
        if len(authority_secret) < 32 or len(provider_secret) < 32:
            raise ValueError("lab secrets must be 32+ bytes")
        if authority_secret == provider_secret:
            raise ValueError("authority and provider must have separate keys")
        self.path = str(path)
        self.authority_secret = authority_secret
        self.provider_secret = provider_secret
        self.authority_key_id = authority_key_id
        self.provider_key_id = provider_key_id
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS principals(actor TEXT PRIMARY KEY, epoch INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS grants(
                    approval_id TEXT PRIMARY KEY, actor TEXT NOT NULL, approver TEXT NOT NULL,
                    scope TEXT NOT NULL, action_sha TEXT NOT NULL,
                    issued_at INTEGER NOT NULL, expires_at INTEGER NOT NULL, epoch INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS subjects(
                    subject TEXT PRIMARY KEY, status TEXT NOT NULL, eligible INTEGER NOT NULL,
                    version INTEGER NOT NULL, truth INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS policy(id INTEGER PRIMARY KEY CHECK(id=1),
                    version INTEGER NOT NULL, max_cents INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS audit(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, prev_hash TEXT NOT NULL,
                    entry TEXT NOT NULL, entry_hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS effects(
                    effect_id TEXT PRIMARY KEY, approval_id TEXT NOT NULL UNIQUE,
                    action_sha TEXT NOT NULL, token_sha TEXT NOT NULL,
                    action_json TEXT NOT NULL, receipt_json TEXT NOT NULL);
                INSERT OR IGNORE INTO policy VALUES(1,1,5000);
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, isolation_level=None, timeout=15, factory=_ClosingConnection)
        db.execute("PRAGMA busy_timeout=15000")
        db.row_factory = sqlite3.Row
        return db

    def seed(self, action: dict[str, Any], *, approval_id: str = "a1",
             issued_at: int = 100, expires_at: int = 300, eligible: bool = True,
             truth: bool = True, approver: str = "host-declared-reviewer") -> None:
        """TRUSTED laboratory setup method, not a user- or model-facing API."""
        if not valid_action(action):
            raise ValueError("invalid action")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO principals(actor,epoch) VALUES(?,0)", (action["actor"],))
            epoch = db.execute("SELECT epoch FROM principals WHERE actor=?", (action["actor"],)).fetchone()[0]
            db.execute("INSERT OR REPLACE INTO grants VALUES(?,?,?,?,?,?,?,?)",
                       (approval_id, action["actor"], approver, action["scope"], hash_obj(action),
                        issued_at, expires_at, epoch))
            db.execute("INSERT OR REPLACE INTO subjects VALUES(?,?,?,?,?)",
                       (action["subject"], "PASS", int(eligible), 1, int(truth)))
            db.execute("COMMIT")

    def snapshot(self, subject: str) -> tuple[int, int]:
        with self._connect() as db:
            ev = db.execute("SELECT version FROM subjects WHERE subject=?", (subject,)).fetchone()
            pol = db.execute("SELECT version FROM policy WHERE id=1").fetchone()
            if ev is None or pol is None:
                raise ValueError("missing evidence or policy")
            return int(ev[0]), int(pol[0])

    def change(self, *, subject: str | None = None, eligible: bool | None = None,
               status: str | None = None, truth: bool | None = None,
               max_cents: int | None = None, revoke_actor: str | None = None) -> None:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if subject is not None and any(v is not None for v in (eligible, status, truth)):
                record = db.execute("SELECT eligible,status,truth FROM subjects WHERE subject=?", (subject,)).fetchone()
                if record is None:
                    raise ValueError("unknown subject")
                db.execute("UPDATE subjects SET eligible=?,status=?,truth=?,version=version+1 WHERE subject=?",
                           (int(eligible) if eligible is not None else record["eligible"],
                            status if status is not None else record["status"],
                            int(truth) if truth is not None else record["truth"], subject))
            if max_cents is not None:
                if type(max_cents) is not int or max_cents < 0:
                    raise ValueError("invalid maximum")
                db.execute("UPDATE policy SET max_cents=?,version=version+1 WHERE id=1", (max_cents,))
            if revoke_actor is not None:
                db.execute("UPDATE principals SET epoch=epoch+1 WHERE actor=?", (revoke_actor,))
            db.execute("COMMIT")

    def _ledger_integrity(self, db: sqlite3.Connection) -> bool:
        """Reject observable local hash/receipt corruption before any new effect.

        This is not proof against a compromised key or host. Linear scan is a
        laboratory policy; production would require indexed/anchored design.
        """
        audits = db.execute("SELECT * FROM audit ORDER BY seq").fetchall()
        prev, expected_seq = GENESIS, 1
        by_seq = {}
        for row in audits:
            try:
                entry = decode_wire(row["entry"])
            except (TypeError, ValueError):
                return False
            if (row["seq"] != expected_seq or row["prev_hash"] != prev or
                row["entry_hash"] != hash_obj({"seq":row["seq"], "prev_hash":prev, "entry":entry})):
                return False
            by_seq[expected_seq] = (row["entry_hash"], entry)
            prev = row["entry_hash"]
            expected_seq += 1
        effects = db.execute("SELECT * FROM effects").fetchall()
        if len(effects) != len(audits):
            return False
        for eff in effects:
            try:
                proof = decode_wire(eff["receipt_json"])
                action = decode_wire(eff["action_json"])
            except (TypeError, ValueError):
                return False
            if not self.verify_proof(proof, action=action):
                return False
            body = proof["body"]
            row = by_seq.get(body["audit_seq"])
            if row is None or row[0] != body["audit_hash"]:
                return False
            entry = row[1]
            pairs = (("effect_id","effect_id"), ("approval_id","approval_id"),
                     ("token_sha256","token_sha256"), ("action_sha256","action_sha256"),
                     ("subject_ref","subject_ref"), ("evidence_version","observed_evidence_version"),
                     ("policy_version","observed_policy_version"),
                     ("authority_epoch","observed_authority_epoch"), ("committed_at","committed_at"))
            if any(entry.get(e) != body.get(b) for e,b in pairs):
                return False
            if (eff["effect_id"] != body["effect_id"] or
                eff["approval_id"] != body["approval_id"] or
                eff["action_sha"] != body["action_sha256"] or
                eff["token_sha"] != body["token_sha256"]):
                return False
        return True

    def commit(self, action: dict[str, Any], token: dict[str, Any], *, now: int,
               lose_response: bool = False) -> Outcome:
        if not valid_action(action):
            return Outcome("INVALID_ACTION")
        if not verify_artifact(token, self.authority_secret, "earned-trust.token.v1",
                               self.authority_key_id, TOKEN_FIELDS):
            return Outcome("INVALID_TOKEN_AUTH")
        body = token["body"]
        if not valid_token_fields(body):
            return Outcome("INVALID_TOKEN_SCHEMA")
        action_sha = hash_obj(action)
        if (body["action_sha256"] != action_sha or body["actor"] != action["actor"]
                or body["scope"] != action["scope"]):
            return Outcome("ACTION_BINDING_MISMATCH")
        token_sha = hash_obj(token)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if not self._ledger_integrity(db):
                db.execute("ROLLBACK")
                return Outcome("LEDGER_INTEGRITY_FAILED")
            old = db.execute("SELECT * FROM effects WHERE effect_id=?", (body["effect_id"],)).fetchone()
            if old is not None:
                if old["token_sha"] != token_sha or old["action_sha"] != action_sha:
                    db.execute("COMMIT")
                    return Outcome("EFFECT_ID_CONFLICT")
                proof = decode_wire(old["receipt_json"])
                db.execute("COMMIT")
                return Outcome("IDEMPOTENT_REPLAY", replay=True, receipt=proof)
            if not (body["issued_at"] <= now < body["expires_at"]):
                db.execute("COMMIT")
                return Outcome("TOKEN_NOT_CURRENT")
            grant = db.execute("SELECT * FROM grants WHERE approval_id=?", (body["approval_id"],)).fetchone()
            if (grant is None or grant["actor"] != action["actor"] or grant["scope"] != action["scope"]
                    or grant["action_sha"] != action_sha):
                db.execute("COMMIT")
                return Outcome("GRANT_MISMATCH")
            epoch = db.execute("SELECT epoch FROM principals WHERE actor=?", (action["actor"],)).fetchone()
            if epoch is None or epoch[0] != grant["epoch"]:
                db.execute("COMMIT")
                return Outcome("REVOKED")
            if not (grant["issued_at"] <= now < grant["expires_at"]):
                db.execute("COMMIT")
                return Outcome("GRANT_NOT_CURRENT")
            ev = db.execute("SELECT * FROM subjects WHERE subject=?", (action["subject"],)).fetchone()
            if ev is None or ev["status"] != "PASS" or not ev["eligible"]:
                db.execute("COMMIT")
                return Outcome("EVIDENCE_UNSATISFIED")
            if ev["version"] != body["subject_version"]:
                db.execute("COMMIT")
                return Outcome("EVIDENCE_REVISION_CHANGED")
            pol = db.execute("SELECT * FROM policy WHERE id=1").fetchone()
            if pol["version"] != body["policy_version"]:
                db.execute("COMMIT")
                return Outcome("POLICY_REVISION_CHANGED")
            if action["amount_cents"] > pol["max_cents"]:
                db.execute("COMMIT")
                return Outcome("POLICY_LIMIT")
            consumed = db.execute("SELECT effect_id FROM effects WHERE approval_id=?", (body["approval_id"],)).fetchone()
            if consumed is not None:
                db.execute("COMMIT")
                return Outcome("APPROVAL_CONSUMED")
            last = db.execute("SELECT seq,entry_hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
            prev_hash = last["entry_hash"] if last else GENESIS
            subject_ref = hmac.new(self.provider_secret, b"subject-ref\0" + action["subject"].encode(), "sha256").hexdigest()
            entry = {"event": "LOCAL_EFFECT_COMMITTED", "effect_id": body["effect_id"],
                     "approval_id": body["approval_id"], "token_sha256": token_sha,
                     "action_sha256": action_sha, "subject_ref": subject_ref,
                     "evidence_version": ev["version"], "policy_version": pol["version"],
                     "authority_epoch": epoch[0], "committed_at": now}
            cursor = db.execute("INSERT INTO audit(prev_hash,entry,entry_hash) VALUES(?,?,?)",
                                (prev_hash, canonical(entry).decode(), "PENDING"))
            seq = int(cursor.lastrowid)
            entry_hash = hash_obj({"seq": seq, "prev_hash": prev_hash, "entry": entry})
            db.execute("UPDATE audit SET entry_hash=? WHERE seq=?", (entry_hash, seq))
            proof_body = {"schema": "earned-trust.local-commit.v1", "result": "COMMITTED",
                          "effect_id": body["effect_id"], "approval_id": body["approval_id"],
                          "token_sha256": token_sha, "action_sha256": action_sha,
                          "subject_ref": subject_ref, "amount_cents": action["amount_cents"],
                          "observed_evidence_version": ev["version"],
                          "observed_policy_version": pol["version"],
                          "observed_authority_epoch": epoch[0], "committed_at": now,
                          "audit_seq": seq, "audit_hash": entry_hash}
            proof = seal(self.provider_secret, "earned-trust.provider-proof.v1",
                         self.provider_key_id, proof_body)
            db.execute("INSERT INTO effects(effect_id,approval_id,action_sha,token_sha,action_json,receipt_json) VALUES(?,?,?,?,?,?)",
                       (body["effect_id"], body["approval_id"], action_sha, token_sha,
                        canonical(action).decode(), canonical(proof).decode()))
            db.execute("COMMIT")
        if lose_response:
            raise LostResponse("committed local effect, simulated response loss")
        return Outcome("COMMITTED", committed=True, receipt=proof)

    def lookup(self, effect_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT receipt_json FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            return decode_wire(row[0]) if row else None

    def verify_proof(self, proof: dict[str, Any], *, token: dict[str, Any] | None = None,
                     action: dict[str, Any] | None = None) -> bool:
        if not verify_artifact(proof, self.provider_secret, "earned-trust.provider-proof.v1",
                               self.provider_key_id, PROOF_FIELDS):
            return False
        body = proof["body"]
        if (body["schema"] != "earned-trust.local-commit.v1" or body["result"] != "COMMITTED"
                or type(body["audit_seq"]) is not int or body["audit_seq"] < 1):
            return False
        if action is not None and (not valid_action(action) or hash_obj(action) != body["action_sha256"]):
            return False
        if token is not None and (not verify_artifact(token, self.authority_secret,
                             "earned-trust.token.v1", self.authority_key_id, TOKEN_FIELDS)
                             or hash_obj(token) != body["token_sha256"]
                             or token["body"]["action_sha256"] != body["action_sha256"]
                             or token["body"]["effect_id"] != body["effect_id"]):
            return False
        return True

    def verify_audit(self, anchor: dict[str, Any] | None = None) -> dict[str, Any]:
        """Verify hash chain and an independently trusted *historical* anchor.

        The anchor must have been captured and protected outside this SQLite file.
        An attacker who edits both the ledger and the anchor defeats this test.
        """
        with self._connect() as db:
            rows = db.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            prev, last = GENESIS, 0
            roots = {0: GENESIS}
            for row in rows:
                seq = int(row["seq"])
                try:
                    entry = decode_wire(row["entry"])
                except (TypeError, ValueError):
                    return {"valid": False, "reason": "malformed_entry", "seq": seq}
                if seq != last + 1 or row["prev_hash"] != prev or row["entry_hash"] != hash_obj({"seq": seq, "prev_hash": prev, "entry": entry}):
                    return {"valid": False, "reason": "chain_mutation", "seq": seq}
                prev, last = row["entry_hash"], seq
                roots[last] = prev
            checkpoint = {"event_count": last, "root_hash": prev}
            if anchor is not None:
                count = anchor.get("event_count") if isinstance(anchor, dict) else None
                root = anchor.get("root_hash") if isinstance(anchor, dict) else None
                if type(count) is not int or count not in roots or root != roots[count]:
                    return {"valid": False, "reason": "trusted_anchor_mismatch", **checkpoint}
            return {"valid": True, "reason": "ok", **checkpoint}

    def verify_stored_effect(self, effect_id: str, *, token: dict[str, Any] | None = None) -> bool:
        """Cross-check signed local receipt, corresponding audit event, and stored action.

        This authenticates a *local record*, not an external provider's state.
        """
        with self._connect() as db:
            eff = db.execute("SELECT * FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
            if eff is None:
                return False
            try:
                action = decode_wire(eff["action_json"])
                proof = decode_wire(eff["receipt_json"])
            except (TypeError, ValueError):
                return False
            if not self.verify_proof(proof, token=token, action=action):
                return False
            body = proof["body"]
            if (eff["approval_id"] != body["approval_id"] or eff["action_sha"] != body["action_sha256"]
                    or eff["token_sha"] != body["token_sha256"] or effect_id != body["effect_id"]):
                return False
            audit = db.execute("SELECT * FROM audit WHERE seq=?", (body["audit_seq"],)).fetchone()
            if audit is None or audit["entry_hash"] != body["audit_hash"]:
                return False
            try:
                entry = decode_wire(audit["entry"])
            except (TypeError, ValueError):
                return False
            if audit["entry_hash"] != hash_obj({"seq": audit["seq"], "prev_hash": audit["prev_hash"], "entry": entry}):
                return False
            required_equalities = (
                ("effect_id", "effect_id"), ("approval_id", "approval_id"),
                ("token_sha256", "token_sha256"), ("action_sha256", "action_sha256"),
                ("subject_ref", "subject_ref"), ("evidence_version", "observed_evidence_version"),
                ("policy_version", "observed_policy_version"),
                ("authority_epoch", "observed_authority_epoch"),
                ("committed_at", "committed_at"),
            )
            return all(entry.get(e) == body.get(b) for e, b in required_equalities)

    def effect_count(self) -> int:
        with self._connect() as db:
            return db.execute("SELECT count(*) FROM effects").fetchone()[0]

    def recorded_truth(self, subject: str) -> bool:
        """Lab-only oracle deliberately not read at commit; not independently verified."""
        with self._connect() as db:
            row = db.execute("SELECT truth FROM subjects WHERE subject=?", (subject,)).fetchone()
            return bool(row[0]) if row else False
