"""External witness-quorum checkpoints for the Lycheetah spent-nonce registry.

Reference implementation only. Witnesses are modeled as independent durable SQLite
stores with independent Ed25519 keys. Real anti-rollback requires those stores and
keys to occupy genuinely independent administrative/failure domains.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import re
import secrets
import sqlite3
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from remote_anchor_http import canonical, b64, unb64

VERSION = "lycheetah-registry-witness-quorum-v3.7"
DOMAIN_CHECKPOINT = b"lyc-registry-state-checkpoint-v3.7\n"
DOMAIN_VOTE = b"lyc-registry-state-vote-v3.7\n"
DOMAIN_HEAD = b"lyc-registry-state-head-v3.7\n"
DOMAIN_LOCAL = b"lyc-registry-local-anchor-v3.7\n"
HEX64 = re.compile(r"^[a-f0-9]{64}$")
VALID_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
MIN_KEY_BYTES = 32

class RegistryCheckpointError(ValueError):
    pass

class RegistryQuorumUnavailable(RegistryCheckpointError):
    pass

class RegistryRollbackDetected(RegistryCheckpointError):
    pass


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha_json(value: Any) -> str:
    return _sha256(canonical(value))


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def quorum_threshold(n: int, max_byzantine: int) -> int:
    if type(n) is not int or type(max_byzantine) is not int or n < 1 or max_byzantine < 0:
        raise RegistryCheckpointError("quorum-parameters-invalid")
    if n < 3 * max_byzantine + 1:
        raise RegistryCheckpointError("quorum-roster-too-small-for-fault-budget")
    return (n + max_byzantine) // 2 + 1


def _key_registry(keys: Mapping[str, Ed25519PublicKey]) -> None:
    if not isinstance(keys, Mapping) or not keys:
        raise RegistryCheckpointError("witness-key-registry-invalid")
    raw = []
    for key_id, key in keys.items():
        if not isinstance(key_id, str) or not VALID_ID.fullmatch(key_id) or not isinstance(key, Ed25519PublicKey):
            raise RegistryCheckpointError("witness-key-registry-invalid")
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        raw.append(key.public_bytes(Encoding.Raw, PublicFormat.Raw))
    if len(set(raw)) != len(raw):
        raise RegistryCheckpointError("witness-key-alias-detected")


@dataclass(frozen=True)
class RegistryCheckpoint:
    body: Mapping[str, Any]
    signature_b64: str

    def unsigned(self) -> dict[str, Any]:
        return dict(self.body)

    def to_dict(self) -> dict[str, Any]:
        return {"body": dict(self.body), "signature_b64": self.signature_b64}

    @property
    def record_sha256(self) -> str:
        return _sha_json(self.to_dict())

    @classmethod
    def issue(cls, *, registry_id: str, sequence: int, state_sha256: str,
              previous_record_sha256: str | None, request_id: str,
              private_key: Ed25519PrivateKey, issued_at_ms: int | None = None) -> "RegistryCheckpoint":
        if not isinstance(registry_id, str) or not VALID_ID.fullmatch(registry_id):
            raise RegistryCheckpointError("checkpoint-registry-id-invalid")
        if type(sequence) is not int or sequence < 1:
            raise RegistryCheckpointError("checkpoint-sequence-invalid")
        if not _valid_digest(state_sha256):
            raise RegistryCheckpointError("checkpoint-state-digest-invalid")
        if (sequence == 1) != (previous_record_sha256 is None):
            raise RegistryCheckpointError("checkpoint-parent-inconsistent")
        if previous_record_sha256 is not None and not _valid_digest(previous_record_sha256):
            raise RegistryCheckpointError("checkpoint-parent-digest-invalid")
        if not isinstance(request_id, str) or not VALID_ID.fullmatch(request_id):
            raise RegistryCheckpointError("checkpoint-request-id-invalid")
        stamp = _now_ms() if issued_at_ms is None else issued_at_ms
        if type(stamp) is not int or stamp < 0:
            raise RegistryCheckpointError("checkpoint-time-invalid")
        if not isinstance(private_key, Ed25519PrivateKey):
            raise RegistryCheckpointError("checkpoint-private-key-invalid")
        body = {"version": VERSION, "registry_id": registry_id, "sequence": sequence,
                "state_sha256": state_sha256, "previous_record_sha256": previous_record_sha256,
                "request_id": request_id, "issued_at_ms": stamp}
        signature = private_key.sign(DOMAIN_CHECKPOINT + canonical(body))
        return cls(body, b64(signature))

    @classmethod
    def from_dict(cls, obj: Mapping[str, Any]) -> "RegistryCheckpoint":
        if not isinstance(obj, Mapping) or set(obj) != {"body", "signature_b64"}:
            raise RegistryCheckpointError("checkpoint-envelope-invalid")
        body = obj["body"]
        fields = {"version", "registry_id", "sequence", "state_sha256", "previous_record_sha256", "request_id", "issued_at_ms"}
        if not isinstance(body, Mapping) or set(body) != fields:
            raise RegistryCheckpointError("checkpoint-body-invalid")
        if body["version"] != VERSION or not isinstance(body["registry_id"], str) or not VALID_ID.fullmatch(body["registry_id"]):
            raise RegistryCheckpointError("checkpoint-version-or-id-invalid")
        if type(body["sequence"]) is not int or body["sequence"] < 1:
            raise RegistryCheckpointError("checkpoint-sequence-invalid")
        if not _valid_digest(body["state_sha256"]):
            raise RegistryCheckpointError("checkpoint-state-digest-invalid")
        parent = body["previous_record_sha256"]
        if (body["sequence"] == 1) != (parent is None) or (parent is not None and not _valid_digest(parent)):
            raise RegistryCheckpointError("checkpoint-parent-invalid")
        if not isinstance(body["request_id"], str) or not VALID_ID.fullmatch(body["request_id"]):
            raise RegistryCheckpointError("checkpoint-request-id-invalid")
        if type(body["issued_at_ms"]) is not int or body["issued_at_ms"] < 0:
            raise RegistryCheckpointError("checkpoint-time-invalid")
        if not isinstance(obj["signature_b64"], str):
            raise RegistryCheckpointError("checkpoint-signature-invalid")
        return cls(dict(body), obj["signature_b64"])


def verify_checkpoint(checkpoint: Mapping[str, Any] | RegistryCheckpoint,
                      issuer_keys: Mapping[str, Ed25519PublicKey], *, registry_id: str | None = None) -> RegistryCheckpoint:
    # Even dataclass instances can be directly constructed by untrusted callers;
    # reparse every input through the strict wire validator.
    raw_checkpoint = checkpoint.to_dict() if isinstance(checkpoint, RegistryCheckpoint) else checkpoint
    cp = RegistryCheckpoint.from_dict(raw_checkpoint)
    if not isinstance(issuer_keys, Mapping) or len(issuer_keys) != 1:
        raise RegistryCheckpointError("registry-issuer-keyset-invalid")
    key_id, key = next(iter(issuer_keys.items()))
    if not isinstance(key_id, str) or not VALID_ID.fullmatch(key_id) or not isinstance(key, Ed25519PublicKey):
        raise RegistryCheckpointError("registry-issuer-keyset-invalid")
    if registry_id is not None and cp.body["registry_id"] != registry_id:
        raise RegistryCheckpointError("checkpoint-registry-id-mismatch")
    try:
        key.verify(unb64(cp.signature_b64), DOMAIN_CHECKPOINT + canonical(dict(cp.body)))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise RegistryCheckpointError("checkpoint-signature-invalid") from exc
    return cp


def _vote_body(witness_id: str, cp: RegistryCheckpoint) -> dict[str, Any]:
    b = cp.body
    return {"version": VERSION, "witness_id": witness_id, "registry_id": b["registry_id"],
            "sequence": b["sequence"], "record_sha256": cp.record_sha256,
            "state_sha256": b["state_sha256"], "previous_record_sha256": b["previous_record_sha256"]}


def _head_tag(key: bytes, body: Mapping[str, Any]) -> str:
    return hmac.new(key, DOMAIN_LOCAL + canonical(dict(body)), hashlib.sha256).hexdigest()


def _assert_schema(db: sqlite3.Connection, table: str, expected: Sequence[tuple[str, str, int]]) -> None:
    try:
        actual = [(r["name"], r["type"].upper(), int(r["pk"])) for r in db.execute(f"PRAGMA table_info('{table}')").fetchall()]
    except sqlite3.Error as exc:
        raise RegistryCheckpointError(f"schema-inspection-failed:{table}") from exc
    if actual != list(expected):
        raise RegistryCheckpointError(f"schema-incompatible:{table}")


class RegistryCheckpointWitness:
    """One witness's durable vote ledger. Each instance must use distinct storage/key."""
    def __init__(self, witness_id: str, private_key: Ed25519PrivateKey, path: str | Path,
                 storage_key: bytes, issuer_keys: Mapping[str, Ed25519PublicKey], registry_id: str,
                 clock_ms=None):
        if not isinstance(witness_id, str) or not VALID_ID.fullmatch(witness_id):
            raise RegistryCheckpointError("witness-id-invalid")
        if not isinstance(private_key, Ed25519PrivateKey):
            raise RegistryCheckpointError("witness-private-key-invalid")
        if not isinstance(storage_key, bytes) or len(storage_key) < MIN_KEY_BYTES:
            raise RegistryCheckpointError("witness-storage-key-invalid")
        if not isinstance(registry_id, str) or not VALID_ID.fullmatch(registry_id):
            raise RegistryCheckpointError("witness-registry-id-invalid")
        if not isinstance(issuer_keys, Mapping) or len(issuer_keys) != 1 or any(not isinstance(k, str) or not isinstance(v, Ed25519PublicKey) for k,v in issuer_keys.items()):
            raise RegistryCheckpointError("witness-issuer-keyset-invalid")
        self.witness_id, self.private_key = witness_id, private_key
        self.path = Path(path).resolve(); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_key = bytes(storage_key); self.issuer_keys = dict(issuer_keys); self.registry_id = registry_id
        self.clock_ms = clock_ms or _now_ms
        with closing(self._db()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS votes(
                registry_id TEXT NOT NULL, sequence INTEGER NOT NULL, record_sha256 TEXT NOT NULL,
                state_sha256 TEXT NOT NULL, previous_record_sha256 TEXT, checkpoint_json TEXT NOT NULL,
                vote_json TEXT NOT NULL, row_hmac TEXT NOT NULL, PRIMARY KEY(registry_id,sequence))""")
            db.execute("""CREATE TABLE IF NOT EXISTS current_head(
                registry_id TEXT PRIMARY KEY, sequence INTEGER NOT NULL, record_sha256 TEXT,
                state_sha256 TEXT, row_hmac TEXT NOT NULL)""")
            db.execute("CREATE TRIGGER IF NOT EXISTS votes_no_update BEFORE UPDATE ON votes BEGIN SELECT RAISE(ABORT,'vote-ledger-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS votes_no_delete BEFORE DELETE ON votes BEGIN SELECT RAISE(ABORT,'vote-ledger-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS head_no_delete BEFORE DELETE ON current_head BEGIN SELECT RAISE(ABORT,'witness-head-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS head_no_decrease BEFORE UPDATE ON current_head WHEN OLD.registry_id!=NEW.registry_id OR NEW.sequence!=OLD.sequence+1 BEGIN SELECT RAISE(ABORT,'witness-head-monotonic'); END")
            _assert_schema(db, "votes", [("registry_id","TEXT",1),("sequence","INTEGER",2),("record_sha256","TEXT",0),("state_sha256","TEXT",0),("previous_record_sha256","TEXT",0),("checkpoint_json","TEXT",0),("vote_json","TEXT",0),("row_hmac","TEXT",0)])
            _assert_schema(db, "current_head", [("registry_id","TEXT",1),("sequence","INTEGER",0),("record_sha256","TEXT",0),("state_sha256","TEXT",0),("row_hmac","TEXT",0)])
            db.commit()

    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row; db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA synchronous=FULL")
        return db

    def _verify_current_row(self, row: sqlite3.Row | Mapping[str, Any] | None) -> tuple[int, str | None, str | None]:
        if row is None:
            return 0, None, None
        body = {k: row[k] for k in ("registry_id", "sequence", "record_sha256", "state_sha256")}
        if type(body["sequence"]) is not int or body["sequence"] < 1 or body["registry_id"] != self.registry_id or not _valid_digest(body["record_sha256"]) or not _valid_digest(body["state_sha256"]):
            raise RegistryCheckpointError("witness-head-state-invalid")
        if not hmac.compare_digest(_head_tag(self.storage_key, body), row["row_hmac"]):
            raise RegistryCheckpointError("witness-head-integrity-invalid")
        return body["sequence"], body["record_sha256"], body["state_sha256"]

    def _verify_vote_row(self, row: sqlite3.Row | Mapping[str, Any]) -> dict[str, Any]:
        body = {k: row[k] for k in ("registry_id", "sequence", "record_sha256", "state_sha256", "previous_record_sha256", "checkpoint_json", "vote_json")}
        tag_body = {k: body[k] for k in ("registry_id", "sequence", "record_sha256", "state_sha256", "previous_record_sha256", "checkpoint_json", "vote_json")}
        if not hmac.compare_digest(_head_tag(self.storage_key, tag_body), row["row_hmac"]):
            raise RegistryCheckpointError("witness-vote-ledger-integrity-invalid")
        vote = json.loads(row["vote_json"])
        cp = verify_checkpoint(json.loads(row["checkpoint_json"]), self.issuer_keys, registry_id=self.registry_id)
        if cp.record_sha256 != row["record_sha256"] or cp.body["sequence"] != row["sequence"] or cp.body["state_sha256"] != row["state_sha256"]:
            raise RegistryCheckpointError("witness-vote-checkpoint-mismatch")
        _verify_vote(vote, {self.witness_id: self.private_key.public_key()}, cp)
        return vote

    def _verify_head_matches_vote_ledger(self, db, current_row) -> None:
        # Revalidate the retained chain from genesis, not only the final head.
        # A signed head whose parent chain is incomplete must not count toward quorum.
        rows = db.execute("SELECT * FROM votes WHERE registry_id=? ORDER BY sequence", (self.registry_id,)).fetchall()
        parent = None
        expected_sequence = 1
        latest = None
        for row in rows:
            vote = self._verify_vote_row(row)
            cp = verify_checkpoint(json.loads(row["checkpoint_json"]), self.issuer_keys, registry_id=self.registry_id)
            if row["sequence"] != expected_sequence or cp.body["sequence"] != expected_sequence:
                raise RegistryCheckpointError("witness-vote-chain-sequence-gap")
            if cp.body["previous_record_sha256"] != parent or row["previous_record_sha256"] != parent:
                raise RegistryCheckpointError("witness-vote-chain-parent-mismatch")
            latest = row
            parent = cp.record_sha256
            expected_sequence += 1
        if current_row is None:
            if latest is not None:
                raise RegistryCheckpointError("witness-head-behind-append-only-vote-ledger")
            return
        seq, rec_sha, state_sha = self._verify_current_row(current_row)
        if latest is None or latest["sequence"] != seq or latest["record_sha256"] != rec_sha or latest["state_sha256"] != state_sha:
            raise RegistryCheckpointError("witness-head-does-not-match-vote-ledger")

    def attest(self, checkpoint: Mapping[str, Any] | RegistryCheckpoint) -> dict[str, Any]:
        cp = verify_checkpoint(checkpoint, self.issuer_keys, registry_id=self.registry_id)
        rec = cp.to_dict(); rec_sha = cp.record_sha256; body = cp.body
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT * FROM current_head WHERE registry_id=?", (self.registry_id,)).fetchone()
            self._verify_head_matches_vote_ledger(db, current)
            cur_seq, cur_hash, cur_state = self._verify_current_row(current)
            if body["sequence"] == cur_seq:
                prior = db.execute("SELECT * FROM votes WHERE registry_id=? AND sequence=?", (self.registry_id, cur_seq)).fetchone()
                if prior is None or prior["record_sha256"] != rec_sha:
                    db.rollback(); raise RegistryCheckpointError("witness-equivocation-at-sequence")
                vote = self._verify_vote_row(prior); db.commit(); return vote
            if body["sequence"] != cur_seq + 1 or body["previous_record_sha256"] != cur_hash:
                db.rollback(); raise RegistryCheckpointError("witness-checkpoint-parent-mismatch")
            vote_body = _vote_body(self.witness_id, cp)
            vote_sig = self.private_key.sign(DOMAIN_VOTE + canonical(vote_body))
            vote = {"body": vote_body, "signature_b64": b64(vote_sig)}
            row_body = {"registry_id": self.registry_id, "sequence": body["sequence"],
                        "record_sha256": rec_sha, "state_sha256": body["state_sha256"],
                        "previous_record_sha256": body["previous_record_sha256"],
                        "checkpoint_json": canonical(rec).decode("utf-8"), "vote_json": canonical(vote).decode("utf-8")}
            db.execute("INSERT INTO votes VALUES(?,?,?,?,?,?,?,?)", (
                row_body["registry_id"], row_body["sequence"], row_body["record_sha256"], row_body["state_sha256"],
                row_body["previous_record_sha256"], row_body["checkpoint_json"], row_body["vote_json"], _head_tag(self.storage_key, row_body)))
            head_body = {"registry_id": self.registry_id, "sequence": body["sequence"],
                         "record_sha256": rec_sha, "state_sha256": body["state_sha256"]}
            tag = _head_tag(self.storage_key, head_body)
            if current is None:
                db.execute("INSERT INTO current_head VALUES(?,?,?,?,?)", (self.registry_id, body["sequence"], rec_sha, body["state_sha256"], tag))
            else:
                db.execute("UPDATE current_head SET sequence=?,record_sha256=?,state_sha256=?,row_hmac=? WHERE registry_id=?",
                           (body["sequence"], rec_sha, body["state_sha256"], tag, self.registry_id))
            db.commit()
            return vote

    def head_report(self, challenge_nonce: str) -> dict[str, Any]:
        if not isinstance(challenge_nonce, str) or not NONCE_RE.fullmatch(challenge_nonce):
            raise RegistryCheckpointError("head-challenge-invalid")
        # The witness samples its own clock; the verifier cannot nominate a time
        # for a witness to sign as though it observed that time itself.
        stamp = self.clock_ms()
        if type(stamp) is not int or stamp < 0:
            raise RegistryCheckpointError("head-report-time-invalid")
        with closing(self._db()) as db:
            row = db.execute("SELECT * FROM current_head WHERE registry_id=?", (self.registry_id,)).fetchone()
            self._verify_head_matches_vote_ledger(db, row)
            seq, rec_sha, state_sha = self._verify_current_row(row)
        body = {"version": VERSION, "witness_id": self.witness_id, "registry_id": self.registry_id,
                "challenge_nonce": challenge_nonce, "sequence": seq, "record_sha256": rec_sha,
                "state_sha256": state_sha, "observed_at_ms": stamp}
        sig = self.private_key.sign(DOMAIN_HEAD + canonical(body))
        return {"body": body, "signature_b64": b64(sig)}

    def get_checkpoint(self, sequence: int) -> dict[str, Any] | None:
        with closing(self._db()) as db:
            row = db.execute("SELECT * FROM votes WHERE registry_id=? AND sequence=?", (self.registry_id, sequence)).fetchone()
            if row is None: return None
            self._verify_vote_row(row)
            return json.loads(row["checkpoint_json"])


def _verify_vote(vote: Mapping[str, Any], witness_keys: Mapping[str, Ed25519PublicKey], cp: RegistryCheckpoint) -> str:
    if not isinstance(vote, Mapping) or set(vote) != {"body", "signature_b64"} or not isinstance(vote["body"], Mapping) or not isinstance(vote["signature_b64"], str):
        raise RegistryCheckpointError("witness-vote-envelope-invalid")
    b = vote["body"]
    if set(b) != {"version", "witness_id", "registry_id", "sequence", "record_sha256", "state_sha256", "previous_record_sha256"}:
        raise RegistryCheckpointError("witness-vote-fields-invalid")
    wid = b["witness_id"]
    if not isinstance(wid, str) or wid not in witness_keys or b["version"] != VERSION:
        raise RegistryCheckpointError("witness-vote-identity-invalid")
    expected = _vote_body(wid, cp)
    if dict(b) != expected:
        raise RegistryCheckpointError("witness-vote-checkpoint-mismatch")
    try: witness_keys[wid].verify(unb64(vote["signature_b64"]), DOMAIN_VOTE + canonical(dict(b)))
    except (InvalidSignature, ValueError, TypeError) as exc: raise RegistryCheckpointError("witness-vote-signature-invalid") from exc
    return wid


def make_certificate(checkpoint: Mapping[str, Any] | RegistryCheckpoint, votes: Sequence[Mapping[str, Any]],
                     issuer_keys: Mapping[str, Ed25519PublicKey], witness_keys: Mapping[str, Ed25519PublicKey],
                     *, max_byzantine: int = 1) -> dict[str, Any]:
    cp = verify_checkpoint(checkpoint, issuer_keys)
    _key_registry(witness_keys); threshold = quorum_threshold(len(witness_keys), max_byzantine)
    accepted = {}; errors = []
    for vote in votes:
        try:
            wid = _verify_vote(vote, witness_keys, cp)
            if wid in accepted: raise RegistryCheckpointError("duplicate-witness-vote")
            accepted[wid] = dict(vote)
        except RegistryCheckpointError as exc: errors.append(str(exc))
    if len(accepted) < threshold:
        raise RegistryQuorumUnavailable(f"registry-checkpoint-quorum-unavailable:{len(accepted)}/{threshold}; {','.join(errors)}")
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    roster = {wid: hashlib.sha256(key.public_bytes(Encoding.Raw, PublicFormat.Raw)).hexdigest() for wid,key in sorted(witness_keys.items())}
    body = {"version": VERSION, "checkpoint": cp.to_dict(), "votes": [accepted[k] for k in sorted(accepted)],
            "threshold": threshold, "max_byzantine": max_byzantine, "roster_sha256": _sha_json(roster)}
    return body


def verify_certificate(certificate: Mapping[str, Any], issuer_keys: Mapping[str, Ed25519PublicKey],
                       witness_keys: Mapping[str, Ed25519PublicKey], *, max_byzantine: int | None = None) -> RegistryCheckpoint:
    if not isinstance(certificate, Mapping) or set(certificate) != {"version", "checkpoint", "votes", "threshold", "max_byzantine", "roster_sha256"} or certificate["version"] != VERSION:
        raise RegistryCheckpointError("registry-certificate-envelope-invalid")
    if not isinstance(certificate["votes"], list): raise RegistryCheckpointError("registry-certificate-votes-invalid")
    f = certificate["max_byzantine"]
    if type(f) is not int or (max_byzantine is not None and f != max_byzantine): raise RegistryCheckpointError("registry-certificate-fault-budget-invalid")
    cp = verify_checkpoint(certificate["checkpoint"], issuer_keys)
    rebuilt = make_certificate(cp, certificate["votes"], issuer_keys, witness_keys, max_byzantine=f)
    if rebuilt != dict(certificate): raise RegistryCheckpointError("registry-certificate-noncanonical-or-invalid")
    return cp


def verify_head_quorum(reports: Sequence[Mapping[str, Any]], witness_keys: Mapping[str, Ed25519PublicKey],
                       *, registry_id: str, challenge_nonce: str, max_byzantine: int = 1,
                       max_age_ms: int = 30_000, now_ms: int | None = None) -> dict[str, Any]:
    _key_registry(witness_keys); threshold = quorum_threshold(len(witness_keys), max_byzantine)
    now = _now_ms() if now_ms is None else now_ms
    if type(now) is not int or now < 0 or type(max_age_ms) is not int or max_age_ms < 1:
        raise RegistryCheckpointError("head-validation-time-invalid")
    seen = set(); groups: dict[tuple[Any,...], list[str]] = {}
    for report in reports:
        if not isinstance(report, Mapping) or set(report) != {"body", "signature_b64"} or not isinstance(report["body"], Mapping):
            continue
        b = report["body"]; wid = b.get("witness_id")
        if wid in seen or wid not in witness_keys: continue
        fields = {"version", "witness_id", "registry_id", "challenge_nonce", "sequence", "record_sha256", "state_sha256", "observed_at_ms"}
        if set(b) != fields or b.get("version") != VERSION or b.get("registry_id") != registry_id or b.get("challenge_nonce") != challenge_nonce:
            continue
        if type(b.get("sequence")) is not int or b["sequence"] < 0 or type(b.get("observed_at_ms")) is not int:
            continue
        if abs(now - b["observed_at_ms"]) > max_age_ms: continue
        if b["sequence"] == 0:
            if b.get("record_sha256") is not None or b.get("state_sha256") is not None: continue
        elif not _valid_digest(b.get("record_sha256")) or not _valid_digest(b.get("state_sha256")):
            continue
        try: witness_keys[wid].verify(unb64(report["signature_b64"]), DOMAIN_HEAD + canonical(dict(b)))
        except (InvalidSignature, ValueError, TypeError): continue
        seen.add(wid)
        group = (b["sequence"], b.get("record_sha256"), b.get("state_sha256"))
        groups.setdefault(group, []).append(wid)
    winners = [(key, ids) for key, ids in groups.items() if len(ids) >= threshold]
    if len(winners) != 1: raise RegistryQuorumUnavailable("no-unique-fresh-registry-head-quorum")
    (seq, record_sha, state_sha), ids = winners[0]
    return {"registry_id": registry_id, "sequence": seq, "record_sha256": record_sha,
            "state_sha256": state_sha, "witness_ids": tuple(sorted(ids)), "threshold": threshold,
            "challenge_nonce": challenge_nonce}


def fresh_head(witnesses: Sequence[RegistryCheckpointWitness], witness_keys: Mapping[str, Ed25519PublicKey],
               registry_id: str, *, max_byzantine: int = 1, now_ms: int | None = None) -> dict[str, Any]:
    nonce = secrets.token_urlsafe(32)
    now = _now_ms() if now_ms is None else now_ms
    reports = []
    for witness in witnesses:
        try: reports.append(witness.head_report(nonce))
        except Exception: continue
    return verify_head_quorum(reports, witness_keys, registry_id=registry_id,
                              challenge_nonce=nonce, max_byzantine=max_byzantine, now_ms=now)


def fingerprint_sqlite_state(path: str | Path, *, tables: Sequence[str] = ("challenges", "request_nonces", "clock_state")) -> str:
    """Fingerprint logical registry tables and relevant SQL schema, not file bytes/WAL headers."""
    db = sqlite3.connect(Path(path).resolve(), timeout=5)
    db.row_factory = sqlite3.Row
    try:
        actual = {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        required = set(tables)
        if actual != required:
            raise RegistryCheckpointError("registry-state-table-set-unexpected")
        schema = [tuple(r) for r in db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('table','index','trigger') AND name NOT LIKE 'sqlite_%' ORDER BY type,name")]
        rows = {}
        for table in tables:
            cols = [r["name"] for r in db.execute(f"PRAGMA table_info('{table}')")]
            if not cols: raise RegistryCheckpointError("registry-state-schema-missing")
            sql = "SELECT " + ",".join('"' + c.replace('"','""') + '"' for c in cols) + f' FROM "{table}"'
            data = [list(row) for row in db.execute(sql).fetchall()]
            data.sort(key=lambda row: canonical(row))
            rows[table] = {"columns": cols, "rows": data}
        return _sha_json({"schema": schema, "rows": rows})
    except sqlite3.Error as exc:
        raise RegistryCheckpointError("registry-state-fingerprint-failed") from exc
    finally:
        db.close()


class RegistryQuorumAnchor:
    """Anchor the *actual live registry database* to a separately stored quorum.

    All protected mutations must go through `dispatch()`. It checks the current
    state, persists an intent, invokes the registry service, fingerprints the live
    state, requires a quorum checkpoint, and only then returns the service result.
    This is a local reference composition, not a deployed independent service.
    """
    def __init__(self, *, registry_id: str, registry_db_path: str | Path,
                 path: str | Path, issuer_private_key: Ed25519PrivateKey,
                 issuer_keys: Mapping[str, Ed25519PublicKey],
                 witnesses: Sequence[RegistryCheckpointWitness],
                 witness_keys: Mapping[str, Ed25519PublicKey], storage_key: bytes,
                 max_byzantine: int = 1, clock_ms=None):
        if not isinstance(registry_id, str) or not VALID_ID.fullmatch(registry_id):
            raise RegistryCheckpointError("registry-id-invalid")
        if not isinstance(issuer_private_key, Ed25519PrivateKey):
            raise RegistryCheckpointError("issuer-private-key-invalid")
        if not isinstance(storage_key, bytes) or len(storage_key) < MIN_KEY_BYTES:
            raise RegistryCheckpointError("client-storage-key-invalid")
        if len(witnesses) != len(witness_keys) or {w.witness_id for w in witnesses} != set(witness_keys):
            raise RegistryCheckpointError("witness-list-keyset-mismatch")
        _key_registry(witness_keys)
        self.threshold = quorum_threshold(len(witness_keys), max_byzantine)
        if not isinstance(issuer_keys, Mapping) or len(issuer_keys) != 1 or any(not isinstance(k, str) or not isinstance(v, Ed25519PublicKey) for k,v in issuer_keys.items()):
            raise RegistryCheckpointError("issuer-keyset-invalid")
        self.registry_id = registry_id
        self.registry_db_path = Path(registry_db_path).resolve()
        if not self.registry_db_path.is_file():
            raise RegistryCheckpointError("registry-database-missing")
        self.path = Path(path).resolve(); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.issuer_private_key, self.issuer_keys = issuer_private_key, dict(issuer_keys)
        self.witnesses, self.witness_keys = tuple(witnesses), dict(witness_keys)
        self.storage_key, self.max_byzantine = bytes(storage_key), max_byzantine
        self.clock_ms = clock_ms or _now_ms
        with closing(self._db()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS local_head(
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), registry_id TEXT NOT NULL,
                sequence INTEGER NOT NULL, record_sha256 TEXT, state_sha256 TEXT,
                record_json TEXT, certificate_json TEXT, row_hmac TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS pending(
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), phase TEXT NOT NULL CHECK(phase IN ('PREPARED','READY')),
                mutation_id TEXT NOT NULL, client_key_id TEXT NOT NULL, method TEXT NOT NULL, path TEXT NOT NULL,
                request_fingerprint TEXT NOT NULL, parent_sequence INTEGER NOT NULL,
                parent_record_sha256 TEXT, parent_state_sha256 TEXT NOT NULL,
                state_sha256 TEXT, checkpoint_json TEXT, response_status INTEGER,
                response_json TEXT, response_dropped INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL,
                row_hmac TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS response_cache(
                client_key_id TEXT NOT NULL, request_id TEXT NOT NULL, request_fingerprint TEXT NOT NULL,
                response_status INTEGER NOT NULL, response_json TEXT NOT NULL, expires_at_ms INTEGER NOT NULL,
                row_hmac TEXT NOT NULL, PRIMARY KEY(client_key_id, request_id))""")
            _assert_schema(db, "local_head", [("singleton","INTEGER",1),("registry_id","TEXT",0),("sequence","INTEGER",0),("record_sha256","TEXT",0),("state_sha256","TEXT",0),("record_json","TEXT",0),("certificate_json","TEXT",0),("row_hmac","TEXT",0)])
            _assert_schema(db, "pending", [("singleton","INTEGER",1),("phase","TEXT",0),("mutation_id","TEXT",0),("client_key_id","TEXT",0),("method","TEXT",0),("path","TEXT",0),("request_fingerprint","TEXT",0),("parent_sequence","INTEGER",0),("parent_record_sha256","TEXT",0),("parent_state_sha256","TEXT",0),("state_sha256","TEXT",0),("checkpoint_json","TEXT",0),("response_status","INTEGER",0),("response_json","TEXT",0),("response_dropped","INTEGER",0),("expires_at_ms","INTEGER",0),("row_hmac","TEXT",0)])
            _assert_schema(db, "response_cache", [("client_key_id","TEXT",1),("request_id","TEXT",2),("request_fingerprint","TEXT",0),("response_status","INTEGER",0),("response_json","TEXT",0),("expires_at_ms","INTEGER",0),("row_hmac","TEXT",0)])
            db.commit()

    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _locked(self):
        # POSIX advisory lock serializes all gateway instances sharing this outbox.
        import fcntl
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.lock_path.open("a+b")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return handle

    def _unlock(self, handle):
        import fcntl
        try: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally: handle.close()

    def live_state_sha256(self) -> str:
        return fingerprint_sqlite_state(self.registry_db_path)

    def _local_head_body(self, seq, rec, state, record_json, certificate_json):
        return {"registry_id": self.registry_id, "sequence": seq, "record_sha256": rec,
                "state_sha256": state, "record_json": record_json, "certificate_json": certificate_json}

    def _read_local(self, db):
        row = db.execute("SELECT * FROM local_head WHERE singleton=1").fetchone()
        if row is None: return None
        body = self._local_head_body(row["sequence"], row["record_sha256"], row["state_sha256"], row["record_json"], row["certificate_json"])
        if row["registry_id"] != self.registry_id or type(body["sequence"]) is not int or body["sequence"] < 1 or not _valid_digest(body["record_sha256"]) or not _valid_digest(body["state_sha256"]) or not isinstance(body["record_json"], str) or not isinstance(body["certificate_json"], str):
            raise RegistryCheckpointError("local-head-state-invalid")
        if not hmac.compare_digest(_head_tag(self.storage_key, body), row["row_hmac"]):
            raise RegistryCheckpointError("local-head-integrity-invalid")
        cp = verify_checkpoint(json.loads(body["record_json"]), self.issuer_keys, registry_id=self.registry_id)
        verify_certificate(json.loads(body["certificate_json"]), self.issuer_keys, self.witness_keys, max_byzantine=self.max_byzantine)
        if cp.record_sha256 != body["record_sha256"] or cp.body["state_sha256"] != body["state_sha256"] or cp.body["sequence"] != body["sequence"]:
            raise RegistryCheckpointError("local-head-checkpoint-mismatch")
        return body

    def _pending(self, db):
        row = db.execute("SELECT * FROM pending WHERE singleton=1").fetchone()
        if row is None: return None
        keys = ("phase", "mutation_id", "client_key_id", "method", "path", "request_fingerprint",
                "parent_sequence", "parent_record_sha256", "parent_state_sha256", "state_sha256",
                "checkpoint_json", "response_status", "response_json", "response_dropped", "expires_at_ms")
        body = {k: row[k] for k in keys}
        if body["phase"] not in {"PREPARED", "READY"} or not isinstance(body["mutation_id"], str) or not VALID_ID.fullmatch(body["mutation_id"]):
            raise RegistryCheckpointError("pending-state-invalid")
        if not isinstance(body["client_key_id"], str) or not VALID_ID.fullmatch(body["client_key_id"]):
            raise RegistryCheckpointError("pending-client-key-id-invalid")
        if not isinstance(body["method"], str) or not isinstance(body["path"], str) or not _valid_digest(body["request_fingerprint"]):
            raise RegistryCheckpointError("pending-request-binding-invalid")
        if type(body["parent_sequence"]) is not int or body["parent_sequence"] < 0 or not _valid_digest(body["parent_state_sha256"]):
            raise RegistryCheckpointError("pending-parent-invalid")
        if body["parent_sequence"] == 0 and body["parent_record_sha256"] is not None:
            raise RegistryCheckpointError("pending-genesis-parent-invalid")
        if body["parent_sequence"] > 0 and not _valid_digest(body["parent_record_sha256"]):
            raise RegistryCheckpointError("pending-parent-record-invalid")
        if type(body["response_dropped"]) is not int or body["response_dropped"] not in (0,1) or type(body["expires_at_ms"]) is not int:
            raise RegistryCheckpointError("pending-control-field-invalid")
        if body["phase"] == "READY":
            if not _valid_digest(body["state_sha256"]) or not isinstance(body["checkpoint_json"], str) or type(body["response_status"]) is not int or not isinstance(body["response_json"], str):
                raise RegistryCheckpointError("pending-ready-fields-invalid")
            cp = verify_checkpoint(json.loads(body["checkpoint_json"]), self.issuer_keys, registry_id=self.registry_id)
            if cp.body["sequence"] != body["parent_sequence"]+1 or cp.body["previous_record_sha256"] != body["parent_record_sha256"] or cp.body["state_sha256"] != body["state_sha256"] or cp.body["request_id"] != body["mutation_id"]:
                raise RegistryCheckpointError("pending-checkpoint-mismatch")
        else:
            if body["state_sha256"] is not None or body["checkpoint_json"] is not None or body["response_status"] is not None or body["response_json"] is not None:
                raise RegistryCheckpointError("pending-prepared-fields-invalid")
        if not hmac.compare_digest(_head_tag(self.storage_key, body), row["row_hmac"]):
            raise RegistryCheckpointError("pending-integrity-invalid")
        return body

    @staticmethod
    def _request_headers(headers: Mapping[str, str]) -> dict[str, str]:
        if not isinstance(headers, Mapping): raise RegistryCheckpointError("request-headers-invalid")
        return {str(k).lower(): str(v) for k,v in headers.items()}

    def _request_identity(self, method: str, path: str, raw_body: bytes, headers: Mapping[str,str], service) -> tuple[str,str,int,str]:
        h = self._request_headers(headers)
        kid = h.get("x-lyc-registry-key-id", "")
        rid = h.get("x-lyc-registry-request-id", "")
        ts_text = h.get("x-lyc-registry-timestamp-ms", "")
        signature = h.get("x-lyc-registry-signature", "")
        if not isinstance(raw_body, bytes) or len(raw_body) > 128*1024 or not VALID_ID.fullmatch(kid) or not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", rid) or not re.fullmatch(r"[0-9]{10,16}", ts_text):
            raise RegistryCheckpointError("request-envelope-invalid")
        stamp = int(ts_text); now = service.clock_ms()
        if type(now) is not int or abs(now-stamp) > service.max_clock_skew_ms:
            raise RegistryCheckpointError("request-timestamp-invalid")
        key = service.client_keys.get(kid)
        if key is None: raise RegistryCheckpointError("request-client-key-unknown")
        body_sha = _sha256(raw_body)
        signed = {"method":method,"path":path,"timestamp_ms":stamp,"request_id":rid,"body_sha256":body_sha}
        expected = hmac.new(key, b"lycheetah-spent-challenge-request-v3.6\n"+canonical(signed), hashlib.sha256).hexdigest()
        if not isinstance(signature,str) or not hmac.compare_digest(expected, signature):
            raise RegistryCheckpointError("request-client-signature-invalid")
        request_fingerprint = _sha_json({"method":method,"path":path,"body_sha256":body_sha,"client_key_id":kid})
        return kid, rid, stamp, request_fingerprint

    def current_quorum_head(self) -> dict[str, Any]:
        return fresh_head(self.witnesses, self.witness_keys, self.registry_id,
                          max_byzantine=self.max_byzantine, now_ms=self.clock_ms())

    def check_current(self) -> dict[str, Any]:
        current_state = self.live_state_sha256()
        with closing(self._db()) as db:
            if self._pending(db) is not None: raise RegistryCheckpointError("checkpoint-pending-recovery-required")
            local = self._read_local(db)
        quorum = self.current_quorum_head()
        if local is None:
            if quorum["sequence"] == 0: return {"status":"UNINITIALIZED", "quorum_head":quorum, "state_sha256":current_state}
            raise RegistryRollbackDetected("local-head-missing-or-rolled-back")
        if (quorum["sequence"],quorum["record_sha256"],quorum["state_sha256"]) != (local["sequence"],local["record_sha256"],local["state_sha256"]):
            if quorum["sequence"] > local["sequence"]: raise RegistryRollbackDetected("external-quorum-ahead-of-local-head")
            raise RegistryCheckpointError("local-head-and-quorum-disagree")
        if current_state != local["state_sha256"]:
            raise RegistryRollbackDetected("registry-state-diverges-from-current-quorum-checkpoint")
        return {"status":"CURRENT", "quorum_head":quorum, "local_head":local}

    def bootstrap(self, service, *, request_id: str = "registry.bootstrap") -> dict[str, Any]:
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            if self._read_local(db) is not None or self._pending(db) is not None:
                db.rollback(); raise RegistryCheckpointError("local-anchor-already-initialized")
            q = self.current_quorum_head()
            if q["sequence"] != 0: db.rollback(); raise RegistryRollbackDetected("cannot-bootstrap-over-existing-external-head")
            state_sha = self.live_state_sha256()
            cp = RegistryCheckpoint.issue(registry_id=self.registry_id, sequence=1, state_sha256=state_sha,
                previous_record_sha256=None, request_id=request_id, private_key=self.issuer_private_key, issued_at_ms=self.clock_ms())
            body = {"phase":"READY","mutation_id":request_id,"client_key_id":"bootstrap.key","method":"BOOTSTRAP","path":"/bootstrap",
                "request_fingerprint":_sha_json({"bootstrap":state_sha}),"parent_sequence":0,"parent_record_sha256":None,
                "parent_state_sha256":state_sha,"state_sha256":state_sha,"checkpoint_json":canonical(cp.to_dict()).decode(),
                "response_status":200,"response_json":canonical({"status":"BOOTSTRAPPED"}).decode(),"response_dropped":0,"expires_at_ms":self.clock_ms()+60_000}
            self._store_pending_body(db, body)
            db.commit()
        return self._complete_pending(service, current_state_sha256=self.live_state_sha256())

    def _store_pending_body(self, db, body: Mapping[str, Any]) -> None:
        tag = _head_tag(self.storage_key, dict(body))
        fields = ("phase","mutation_id","client_key_id","method","path","request_fingerprint","parent_sequence","parent_record_sha256","parent_state_sha256","state_sha256","checkpoint_json","response_status","response_json","response_dropped","expires_at_ms")
        data = [body[k] for k in fields]
        if db.execute("SELECT 1 FROM pending WHERE singleton=1").fetchone():
            db.execute("UPDATE pending SET phase=?,mutation_id=?,client_key_id=?,method=?,path=?,request_fingerprint=?,parent_sequence=?,parent_record_sha256=?,parent_state_sha256=?,state_sha256=?,checkpoint_json=?,response_status=?,response_json=?,response_dropped=?,expires_at_ms=?,row_hmac=? WHERE singleton=1", data+[tag])
        else:
            db.execute("INSERT INTO pending(singleton,phase,mutation_id,client_key_id,method,path,request_fingerprint,parent_sequence,parent_record_sha256,parent_state_sha256,state_sha256,checkpoint_json,response_status,response_json,response_dropped,expires_at_ms,row_hmac) VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data+[tag])

    def _prepare_request(self, kid, rid, method, path, request_fp, expires_at_ms):
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            if self._pending(db) is not None:
                db.rollback(); raise RegistryCheckpointError("checkpoint-already-pending")
            local = self._read_local(db)
            if local is None: db.rollback(); raise RegistryCheckpointError("local-anchor-not-bootstrapped")
            current_state = self.live_state_sha256()
            q = self.current_quorum_head()
            if (q["sequence"],q["record_sha256"],q["state_sha256"]) != (local["sequence"],local["record_sha256"],local["state_sha256"]):
                db.rollback(); raise RegistryRollbackDetected("pre-mutation-quorum-mismatch")
            if current_state != local["state_sha256"]:
                db.rollback(); raise RegistryRollbackDetected("pre-mutation-state-mismatch")
            body = {"phase":"PREPARED","mutation_id":rid,"client_key_id":kid,"method":method,"path":path,
                "request_fingerprint":request_fp,"parent_sequence":local["sequence"],"parent_record_sha256":local["record_sha256"],
                "parent_state_sha256":local["state_sha256"],"state_sha256":None,"checkpoint_json":None,
                "response_status":None,"response_json":None,"response_dropped":0,"expires_at_ms":expires_at_ms}
            self._store_pending_body(db, body); db.commit()
        return body

    def _request_nonce_exists(self, kid: str, rid: str) -> bool:
        with closing(sqlite3.connect(self.registry_db_path)) as db:
            return db.execute("SELECT 1 FROM request_nonces WHERE key_id=? AND request_id=?", (kid,rid)).fetchone() is not None

    def _cache_tag(self, body: Mapping[str, Any]) -> str:
        return _head_tag(self.storage_key, dict(body))

    def _get_cached(self, kid: str, rid: str, request_fp: str, now: int):
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            # Expired results cannot be replayed after the registry's signed request window.
            db.execute("DELETE FROM response_cache WHERE expires_at_ms < ?", (now,))
            row = db.execute("SELECT * FROM response_cache WHERE client_key_id=? AND request_id=?", (kid,rid)).fetchone()
            db.commit()
        if row is None: return None
        body = {k:row[k] for k in ("client_key_id","request_id","request_fingerprint","response_status","response_json","expires_at_ms")}
        if not hmac.compare_digest(self._cache_tag(body), row["row_hmac"]): raise RegistryCheckpointError("response-cache-integrity-invalid")
        if body["request_fingerprint"] != request_fp: raise RegistryCheckpointError("request-id-payload-conflict")
        return int(body["response_status"]), json.loads(body["response_json"]), False

    def _stage_result(self, kid, rid, status, envelope, dropped, service):
        state_sha = self.live_state_sha256()
        nonce_present = self._request_nonce_exists(kid, rid)
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            pending = self._pending(db)
            if pending is None or pending["phase"] != "PREPARED" or pending["client_key_id"] != kid or pending["mutation_id"] != rid:
                db.rollback(); raise RegistryCheckpointError("pending-request-binding-mismatch")
            if state_sha == pending["parent_state_sha256"]:
                if nonce_present:
                    db.rollback(); raise RegistryCheckpointError("nonce-without-registry-state-change")
                db.execute("DELETE FROM pending WHERE singleton=1"); db.commit()
                return {"status":"NO_STATE_CHANGE","response":(status,envelope,dropped)}
            if not nonce_present:
                db.rollback(); raise RegistryRollbackDetected("registry-changed-without-authenticated-request-nonce")
            cp = RegistryCheckpoint.issue(registry_id=self.registry_id,sequence=pending["parent_sequence"]+1,
                state_sha256=state_sha,previous_record_sha256=pending["parent_record_sha256"],request_id=rid,
                private_key=self.issuer_private_key,issued_at_ms=self.clock_ms())
            if dropped or envelope is None:
                status = 503
                envelope = service._sign(503,{"error":"registry-operation-outcome-unknown","request_id":rid,"reconciliation_required":True},rid)
                dropped = True
            ready = {**pending,"phase":"READY","state_sha256":state_sha,
                "checkpoint_json":canonical(cp.to_dict()).decode("utf-8"),"response_status":status,
                "response_json":canonical(envelope).decode("utf-8"),"response_dropped":1 if dropped else 0}
            self._store_pending_body(db,ready); db.commit()
        return {"status":"READY","state_sha256":state_sha}

    def _complete_pending(self, service, *, current_state_sha256: str) -> dict[str, Any]:
        with closing(self._db()) as db:
            pending = self._pending(db)
            local = self._read_local(db)
        if pending is None or pending["phase"] != "READY": raise RegistryCheckpointError("ready-checkpoint-not-pending")
        if pending["state_sha256"] != current_state_sha256:
            raise RegistryRollbackDetected("pending-state-does-not-match-live-registry")
        if local is not None and (local["sequence"] != pending["parent_sequence"] or local["record_sha256"] != pending["parent_record_sha256"] or local["state_sha256"] != pending["parent_state_sha256"]):
            raise RegistryRollbackDetected("pending-parent-does-not-match-local-head")
        cp = RegistryCheckpoint.from_dict(json.loads(pending["checkpoint_json"]))
        votes, errors = [], []
        for witness in self.witnesses:
            try: votes.append(witness.attest(cp))
            except Exception as exc: errors.append(f"{witness.witness_id}:{type(exc).__name__}:{exc}")
        certificate = make_certificate(cp, votes, self.issuer_keys, self.witness_keys, max_byzantine=self.max_byzantine)
        cp = verify_certificate(certificate, self.issuer_keys, self.witness_keys, max_byzantine=self.max_byzantine)
        q = self.current_quorum_head()
        if (q["sequence"],q["record_sha256"],q["state_sha256"]) != (cp.body["sequence"],cp.record_sha256,cp.body["state_sha256"]):
            raise RegistryQuorumUnavailable("certificate-not-current-at-fresh-quorum-head")
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            latest = self._pending(db)
            if latest is None or latest["checkpoint_json"] != canonical(cp.to_dict()).decode("utf-8"):
                db.rollback(); raise RegistryCheckpointError("pending-changed-during-quorum-publish")
            head_body = self._local_head_body(cp.body["sequence"],cp.record_sha256,cp.body["state_sha256"],
                canonical(cp.to_dict()).decode("utf-8"),canonical(certificate).decode("utf-8"))
            tag = _head_tag(self.storage_key,head_body)
            db.execute("INSERT INTO local_head(singleton,registry_id,sequence,record_sha256,state_sha256,record_json,certificate_json,row_hmac) VALUES(1,?,?,?,?,?,?,?) ON CONFLICT(singleton) DO UPDATE SET registry_id=excluded.registry_id,sequence=excluded.sequence,record_sha256=excluded.record_sha256,state_sha256=excluded.state_sha256,record_json=excluded.record_json,certificate_json=excluded.certificate_json,row_hmac=excluded.row_hmac",
                (self.registry_id,cp.body["sequence"],cp.record_sha256,cp.body["state_sha256"],head_body["record_json"],head_body["certificate_json"],tag))
            # Response cache and local head advance atomically. The cache row has
            # a freshness-limited life and is not allowed to outlive request auth.
            response_body = {"client_key_id":latest["client_key_id"],"request_id":latest["mutation_id"],
                "request_fingerprint":latest["request_fingerprint"],"response_status":latest["response_status"],
                "response_json":latest["response_json"],"expires_at_ms":latest["expires_at_ms"]}
            response_tag = self._cache_tag(response_body)
            db.execute("INSERT OR REPLACE INTO response_cache VALUES(?,?,?,?,?,?,?)", (
                response_body["client_key_id"],response_body["request_id"],response_body["request_fingerprint"],
                response_body["response_status"],response_body["response_json"],response_body["expires_at_ms"],response_tag))
            db.execute("DELETE FROM pending WHERE singleton=1")
            db.commit()
        return {"status":"ANCHORED","sequence":cp.body["sequence"],"record_sha256":cp.record_sha256,
                "state_sha256":cp.body["state_sha256"],"votes":len(certificate["votes"]),
                "threshold":certificate["threshold"],"witness_ids":sorted(v["body"]["witness_id"] for v in certificate["votes"]),
                "warnings":errors}

    def _recover_pending_locked(self, service):
        current_state = self.live_state_sha256()
        with closing(self._db()) as db:
            pending = self._pending(db)
            local = self._read_local(db)
        if pending is None: return None
        if local is None: raise RegistryRollbackDetected("pending-without-local-head")
        if pending["phase"] == "READY":
            if pending["state_sha256"] != current_state:
                raise RegistryRollbackDetected("pending-state-does-not-match-live-registry")
            if (local["sequence"] != pending["parent_sequence"] or local["record_sha256"] != pending["parent_record_sha256"] or local["state_sha256"] != pending["parent_state_sha256"]):
                raise RegistryRollbackDetected("pending-parent-does-not-match-local-head")
            # This path also repairs a 2/2 partial publication: the two early votes
            # reissue the same vote, while the remaining witnesses may advance.
            return self._complete_pending(service,current_state_sha256=current_state)
        q = self.current_quorum_head()
        if (q["sequence"],q["record_sha256"],q["state_sha256"]) != (local["sequence"],local["record_sha256"],local["state_sha256"]):
            raise RegistryRollbackDetected("pending-recovery-quorum-parent-mismatch")
        if pending["phase"] == "PREPARED":
            if current_state == pending["parent_state_sha256"] and not self._request_nonce_exists(pending["client_key_id"],pending["mutation_id"]):
                with closing(self._db()) as db:
                    db.execute("BEGIN IMMEDIATE"); db.execute("DELETE FROM pending WHERE singleton=1"); db.commit()
                return {"status":"NO_MUTATION_TO_RECOVER"}
            if current_state != pending["parent_state_sha256"] and self._request_nonce_exists(pending["client_key_id"],pending["mutation_id"]):
                # Mutation committed before crash, but response staging did not.
                # Preserve uncertainty rather than reconstructing a success claim.
                state_sha = current_state
                cp = RegistryCheckpoint.issue(registry_id=self.registry_id,sequence=pending["parent_sequence"]+1,
                    state_sha256=state_sha,previous_record_sha256=pending["parent_record_sha256"],
                    request_id=pending["mutation_id"],private_key=self.issuer_private_key,issued_at_ms=self.clock_ms())
                unknown = service._sign(503,{"error":"registry-operation-committed-response-lost","request_id":pending["mutation_id"],"reconciliation_required":True},pending["mutation_id"])
                ready = {**pending,"phase":"READY","state_sha256":state_sha,"checkpoint_json":canonical(cp.to_dict()).decode(),
                    "response_status":503,"response_json":canonical(unknown).decode(),"response_dropped":0}
                with closing(self._db()) as db:
                    db.execute("BEGIN IMMEDIATE"); self._store_pending_body(db,ready); db.commit()
                return self._complete_pending(service,current_state_sha256=state_sha)
            raise RegistryRollbackDetected("prepared-operation-state-ambiguous")
        if pending["phase"] == "READY":
            if pending["state_sha256"] != current_state: raise RegistryRollbackDetected("pending-state-does-not-match-live-registry")
            return self._complete_pending(service,current_state_sha256=current_state)
        raise RegistryCheckpointError("pending-phase-invalid")

    def recover_pending(self, service) -> dict[str, Any] | None:
        handle = self._locked()
        try: return self._recover_pending_locked(service)
        finally: self._unlock(handle)

    def dispatch(self, service, method: str, path: str, raw_body: bytes, headers: Mapping[str,str]):
        """Serialize, preflight, persist intent, invoke actual service, anchor state, then reply.

        Returns the underlying `(status,envelope,dropped)` shape. A post-commit
        failure to reach quorum returns a signed 503 while leaving a recoverable
        READY outbox entry; callers must not treat this as successful consumption.
        """
        lock = self._locked()
        try:
            self._recover_pending_locked(service)
            try:
                kid,rid,stamp,request_fp = self._request_identity(method,path,raw_body,headers,service)
            except RegistryCheckpointError as exc:
                rid = "invalid-request-id"
                return 401, service._sign(401,{"error":str(exc)},rid), False
            self.check_current()
            try:
                cached = self._get_cached(kid,rid,request_fp,service.clock_ms())
            except RegistryCheckpointError as exc:
                if str(exc) == "request-id-payload-conflict":
                    return 409, service._sign(409,{"error":"request-id-payload-conflict"},rid), False
                raise
            if cached is not None: return cached
            # Same key/request ID but a different fingerprint is a conflict, never
            # an opportunity to reuse a prior authorization/result.
            with closing(self._db()) as db:
                conflict = db.execute("SELECT 1 FROM response_cache WHERE client_key_id=? AND request_id=?",(kid,rid)).fetchone()
            if conflict:
                return 409, service._sign(409,{"error":"request-id-payload-conflict"},rid), False
            self._prepare_request(kid,rid,method,path,request_fp,stamp+service.max_clock_skew_ms)
            status,envelope,dropped = service.handle(method,path,raw_body,headers)
            staged = self._stage_result(kid,rid,status,envelope,dropped,service)
            if staged["status"] == "NO_STATE_CHANGE":
                return staged["response"]
            try:
                self._complete_pending(service,current_state_sha256=staged["state_sha256"])
            except RegistryQuorumUnavailable as exc:
                return 503, service._sign(503,{"error":"registry-checkpoint-quorum-unavailable","request_id":rid,"reconciliation_required":True},rid), False
            with closing(self._db()) as db:
                row = db.execute("SELECT response_status,response_json FROM response_cache WHERE client_key_id=? AND request_id=?",(kid,rid)).fetchone()
            if row is None: raise RegistryCheckpointError("anchored-response-cache-missing")
            return int(row["response_status"]), json.loads(row["response_json"]), bool(dropped)
        except RegistryCheckpointError as exc:
            try:
                h = self._request_headers(headers)
                rid = h.get("x-lyc-registry-request-id", "invalid-request-id")
                if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", rid): rid = "invalid-request-id"
            except Exception:
                rid = "invalid-request-id"
            reason = re.sub(r"[^A-Za-z0-9._:-]", "-", str(exc))[:96] or "guard-failed"
            return 503, service._sign(503,{"error":"registry-checkpoint-failed-closed","reason_code":reason,"reconciliation_required":True},rid), False
        except Exception:
            # An unforeseen handler/storage failure may occur after the registry
            # commits but before it returns. Keep PREPARED intent for recovery and
            # never leak exception details or imply success to the caller.
            try:
                h = self._request_headers(headers)
                rid = h.get("x-lyc-registry-request-id", "invalid-request-id")
                if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", rid): rid = "invalid-request-id"
            except Exception:
                rid = "invalid-request-id"
            return 503, service._sign(503,{"error":"registry-checkpoint-failed-closed","reason_code":"unexpected-dispatch-exception","reconciliation_required":True},rid), False
        finally:
            self._unlock(lock)


def _assert_current_for_test(anchor: RegistryQuorumAnchor) -> bool:
    return anchor.check_current()["status"] == "CURRENT"


class AnchoredRegistryHTTPServer(ThreadingHTTPServer):
    """Loopback-only HTTP composition that exposes only the quorum-guarded dispatcher.

    Production deployment would need separate, authenticated remote witness services;
    the local test harness keeps witnesses in-process while preserving separate stores.
    """
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, *, service, anchor):
        host, _port = address
        try:
            bind_ip = ipaddress.ip_address(host)
        except ValueError as exc:
            raise RegistryCheckpointError("anchored-http-server-requires-numeric-loopback") from exc
        if not bind_ip.is_loopback:
            raise RegistryCheckpointError("anchored-http-server-loopback-only")
        self.service = service
        self.anchor = anchor
        super().__init__(address, AnchoredRegistryRequestHandler)


class AnchoredRegistryRequestHandler(BaseHTTPRequestHandler):
    server: AnchoredRegistryHTTPServer
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        # Do not log signed request headers or request bodies.
        return

    def _dispatch(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > 128 * 1024:
            rid = self.headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")
            status, envelope, dropped = 413, self.server.service._sign(413,{"error":"request-body-too-large"},rid), False
        else:
            raw = self.rfile.read(length) if self.command in {"POST", "PUT", "PATCH"} else b""
            status, envelope, dropped = self.server.anchor.dispatch(
                self.server.service, self.command, self.path, raw, dict(self.headers.items())
            )
        if dropped or envelope is None:
            self.close_connection = True
            try: self.connection.shutdown(2)
            except OSError: pass
            self.connection.close()
            return
        payload = canonical(envelope)
        if len(payload) > 128 * 1024:
            status = 500
            payload = canonical(self.server.service._sign(500,{"error":"response-too-large"},
                self.headers.get("X-Lyc-Registry-Request-Id","invalid-request-id")))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.close_connection = True

    do_GET = _dispatch
    do_POST = _dispatch
    do_PUT = _dispatch
    do_PATCH = _dispatch
    do_DELETE = _dispatch
