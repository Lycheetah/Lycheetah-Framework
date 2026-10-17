#!/usr/bin/env python3
"""Cycle 10 descriptor-anchored experimental file-copy executor.

POSIX-only, intended for private temporary test directories. This is NOT a
hostile-user sandbox, distributed queue, or production authorization gateway.
All control types here are conventional engineering, not novel cryptography.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import sqlite3
import stat
from typing import Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from bridge_v0_2 import BridgeError, digest_obj, verify_plan_integrity, parse_time, utc_now, _verify_authority_now

PROTOCOL = "LAMAGUE-EXECUTION-BOUNDARY-EXPERIMENT-1"
DIRECTIONS = {"source": "PRESENT_UNCHANGED", "destination": "CREATE_ONLY_IF_ABSENT", "intent": "YES"}
O_DIR = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
O_REG = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
REQUIRED_OS = os.name == "posix" and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY") and (os.open in os.supports_dir_fd) and (os.link in os.supports_dir_fd)


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def ztime(t: dt.datetime) -> str:
    if t.utcoffset() != dt.timedelta(0):
        raise ValueError("timestamp must be UTC-aware")
    return t.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_z(s: str) -> dt.datetime:
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("expected UTC Z")
    return dt.datetime.fromisoformat(s[:-1] + "+00:00")


def identity_fd(fd: int) -> list[int]:
    st = os.fstat(fd)
    if not stat.S_ISDIR(st.st_mode):
        raise BridgeError("not a directory")
    return [st.st_dev, st.st_ino]


def open_root(path: str) -> int:
    if not REQUIRED_OS:
        raise BridgeError("POSIX directory-fd and nofollow operations required; fail closed")
    return os.open(path, O_DIR)


def open_parent(rootfd: int, rel: str) -> int:
    """Walk each component without following symlinks; parent is an owned fd."""
    p = PurePosixPath(rel)
    if p.is_absolute() or not p.parts or any(x in (".", "..") for x in p.parts):
        raise BridgeError("invalid relative path")
    fd = os.dup(rootfd)
    try:
        for part in p.parts[:-1]:
            nxt = os.open(part, O_DIR, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def same_parent(rootfd: int, rel: str, previous: int) -> bool:
    try:
        fd = open_parent(rootfd, rel)
        try:
            return identity_fd(fd) == identity_fd(previous)
        finally:
            os.close(fd)
    except OSError:
        return False


def read_hash(fd: int, max_bytes: int) -> tuple[str, int]:
    h, n = hashlib.sha256(), 0
    while True:
        chunk = os.read(fd, 1 << 18)
        if not chunk:
            break
        n += len(chunk)
        if n > max_bytes:
            raise BridgeError("file grew beyond approved size")
        h.update(chunk)
    return h.hexdigest(), n


def check_source(fd: int, expected_hash: str, expected_size: int) -> None:
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        raise BridgeError("source must be regular file")
    h, n = read_hash(fd, expected_size)
    if (h, n) != (expected_hash, expected_size):
        raise BridgeError("source changed from approved plan")


def root_fingerprints(plan: dict) -> dict:
    """Capture actual root inode identities to sign, prior to execution."""
    verify_plan_integrity(plan)
    a = open_root(plan["source_root"])
    try:
        b = open_root(plan["destination_root"])
        try:
            return {"source": identity_fd(a), "destination": identity_fd(b)}
        finally:
            os.close(b)
    finally:
        os.close(a)


def draft_grant(plan: dict, *, signer_id: str, now: dt.datetime | None = None, ttl: int = 300) -> dict:
    """Draft for a reviewer to inspect; does NOT independently infer their intent."""
    if not isinstance(signer_id, str) or not (1 <= len(signer_id) <= 128) or not (1 <= ttl <= 600):
        raise ValueError("invalid signer or TTL")
    now = now or dt.datetime.now(dt.timezone.utc)
    return {"protocol": PROTOCOL, "plan_sha256": plan["plan_sha256"],
            "packet_sha256": plan["packet_sha256"], "roots": root_fingerprints(plan),
            "signer_id": signer_id, "nonce": secrets.token_hex(32),
            "issued_at": ztime(now), "expires_at": ztime(now + dt.timedelta(seconds=ttl)),
            "assertion": DIRECTIONS.copy()}


def sign_grant(grant: dict, key: Ed25519PrivateKey) -> dict:
    return {"grant": grant, "signature_ed25519_b64": base64.b64encode(key.sign(canonical(grant))).decode("ascii")}


def verify_grant(plan: dict, envelope: dict, trusted_keys: dict[str, bytes], *, now: dt.datetime | None = None) -> dict:
    verify_plan_integrity(plan)
    # Approval expiry does not extend authority beyond the original plan grant.
    _verify_authority_now(plan["authority"], Path(plan["source_root"]), Path(plan["destination_root"]))
    if not isinstance(envelope, dict) or set(envelope) != {"grant", "signature_ed25519_b64"}:
        raise BridgeError("approval envelope invalid")
    g = envelope["grant"]
    expected = {"protocol", "plan_sha256", "packet_sha256", "roots", "signer_id", "nonce", "issued_at", "expires_at", "assertion"}
    if not isinstance(g, dict) or set(g) != expected:
        raise BridgeError("approval grant shape invalid")
    if g["protocol"] != PROTOCOL or g["plan_sha256"] != plan["plan_sha256"] or g["packet_sha256"] != plan["packet_sha256"]:
        raise BridgeError("approval not bound to exact plan and packet")
    if g["assertion"] != DIRECTIONS:
        raise BridgeError("final-state not affirmed")
    if not isinstance(g["nonce"], str) or len(g["nonce"]) != 64 or any(c not in "0123456789abcdef" for c in g["nonce"]):
        raise BridgeError("invalid nonce")
    try:
        issued, expiry = parse_z(g["issued_at"]), parse_z(g["expires_at"])
        now = now or dt.datetime.now(dt.timezone.utc)
        if not (issued <= now < expiry) or not 0 < (expiry-issued).total_seconds() <= 600:
            raise BridgeError("approval expired, future dated or oversized")
    except (ValueError, TypeError, OverflowError) as e:
        raise BridgeError("invalid UTC expiry") from e
    key = trusted_keys.get(g["signer_id"]) if isinstance(g["signer_id"], str) else None
    if key is None:
        raise BridgeError("signer not enrolled")
    try:
        signature = base64.b64decode(envelope["signature_ed25519_b64"], validate=True)
        if len(signature) != 64:
            raise ValueError("signature size")
        Ed25519PublicKey.from_public_bytes(key).verify(signature, canonical(g))
    except (InvalidSignature, ValueError, TypeError) as e:
        raise BridgeError("invalid approval signature") from e
    if g["roots"] != root_fingerprints(plan):
        raise BridgeError("approved root identity no longer matches")
    return g


def copy_descriptor_anchored(plan: dict, grant: dict, *, before_commit: Callable[[dict, dict], None] | None = None) -> dict:
    """Copy with directory fd anchors. before_commit is a TEST-ONLY injection hook."""
    verify_plan_integrity(plan)
    actions, failures = [], []
    root_src = open_root(plan["source_root"])
    try:
        root_dst = open_root(plan["destination_root"])
        try:
            if {"source": identity_fd(root_src), "destination": identity_fd(root_dst)} != grant["roots"]:
                raise BridgeError("root directory identity changed after grant validation")
            for action in plan["actions"]:
                rec = {"action_id": action["action_id"], "source": action["source_relative"],
                       "destination": action["destination_relative"], "status": "NOT_STARTED"}
                sp, dp, stage = -1, -1, None
                committed = False
                try:
                    srel, drel = action["source_relative"], action["destination_relative"]
                    sp = open_parent(root_src, srel)
                    dp = open_parent(root_dst, drel)
                    sr = os.open(PurePosixPath(srel).name, O_REG, dir_fd=sp)
                    try:
                        if not stat.S_ISREG(os.fstat(sr).st_mode):
                            raise BridgeError("source not regular")
                        stage = ".cycle10-" + secrets.token_hex(16) + ".stage"
                        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
                        staged_fd = os.open(stage, flags, 0o600, dir_fd=dp)
                        staged_id = (os.fstat(staged_fd).st_dev, os.fstat(staged_fd).st_ino)
                        try:
                            h, n = hashlib.sha256(), 0
                            while True:
                                buf = os.read(sr, 1 << 18)
                                if not buf:
                                    break
                                n += len(buf)
                                if n > action["source_bytes"]:
                                    raise BridgeError("source grew during staging")
                                h.update(buf)
                                offset = 0
                                while offset < len(buf):
                                    written = os.write(staged_fd, buf[offset:])
                                    if written <= 0:
                                        raise BridgeError("incomplete staging write")
                                    offset += written
                            os.fsync(staged_fd)
                        finally:
                            os.close(staged_fd)
                        if (h.hexdigest(), n) != (action["source_sha256"], action["source_bytes"]):
                            raise BridgeError("source staged bytes differ from plan")
                    finally:
                        os.close(sr)
                    if before_commit is not None:
                        before_commit(plan, action)
                    # Catch swaps that have already occurred (not a global rename lock).
                    if not same_parent(root_src, srel, sp) or not same_parent(root_dst, drel, dp):
                        raise BridgeError("source or destination parent replaced since opening")
                    staged_now = os.stat(stage, dir_fd=dp, follow_symlinks=False)
                    if not stat.S_ISREG(staged_now.st_mode) or (staged_now.st_dev, staged_now.st_ino) != staged_id:
                        raise BridgeError("staging inode was replaced after creation")
                    # No-clobber hardlink within the already-open directory inode.
                    os.link(stage, PurePosixPath(drel).name, src_dir_fd=dp, dst_dir_fd=dp, follow_symlinks=False)
                    committed = True
                    dfd = os.open(PurePosixPath(drel).name, O_REG, dir_fd=dp)
                    try:
                        check_source(dfd, action["source_sha256"], action["source_bytes"])
                    finally:
                        os.close(dfd)
                    sfd = os.open(PurePosixPath(srel).name, O_REG, dir_fd=sp)
                    try:
                        check_source(sfd, action["source_sha256"], action["source_bytes"])
                    finally:
                        os.close(sfd)
                    if not same_parent(root_src, srel, sp) or not same_parent(root_dst, drel, dp):
                        raise BridgeError("namespace moved during commit; cannot verify approved path")
                    try:
                        os.fsync(dp)
                    except OSError:
                        pass  # Filesystem dependent; no durability claim is made.
                    rec["status"] = "VERIFIED"
                except Exception as exc:
                    rec["status"] = "FAILED_POSTCOMMIT" if committed else "FAILED_NO_COMMIT"
                    rec["error"] = f"{type(exc).__name__}: {exc}"
                    failures.append(rec["error"])
                finally:
                    if stage is not None and dp != -1:
                        try:
                            os.unlink(stage, dir_fd=dp)
                        except OSError:
                            rec["staging_cleanup_warning"] = True
                    if sp != -1:
                        os.close(sp)
                    if dp != -1:
                        os.close(dp)
                actions.append(rec)
                if failures:
                    break
        finally:
            os.close(root_dst)
    finally:
        os.close(root_src)
    status = "COMPLETED_VERIFIED" if not failures and len(actions) == len(plan["actions"]) else "FAILED_CONTAINED_OR_PARTIAL"
    return {"status": status, "plan_sha256": plan["plan_sha256"], "actions": actions,
            "failures": failures, "limitations": "Receipt is not a signed proof of global namespace confinement or persistence"}


def authorized_execute(plan: dict, envelope: dict, keys: dict[str, bytes], db_path: Path,
                       *, before_commit: Callable[[dict, dict], None] | None = None,
                       now: dt.datetime | None = None) -> dict:
    """One-use signed authorization + execution, with durable claim reservation first.

    Crash between reservation and outcome leaves IN_PROGRESS and must NOT be retried
    automatically. The SQLite DB and directory roots must be controlled separately.
    """
    grant = verify_grant(plan, envelope, keys, now=now)
    with sqlite3.connect(db_path, timeout=5.0, isolation_level=None) as conn:
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("CREATE TABLE IF NOT EXISTS executions (signer TEXT, nonce TEXT, plan_sha256 TEXT, state TEXT, receipt_json TEXT, PRIMARY KEY(signer,nonce))")
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO executions(signer,nonce,plan_sha256,state,receipt_json) VALUES(?,?,?,'IN_PROGRESS',NULL)",
                         (grant["signer_id"], grant["nonce"], plan["plan_sha256"]))
            conn.execute("COMMIT")
        except sqlite3.IntegrityError as e:
            conn.execute("ROLLBACK")
            raise BridgeError("approval already consumed, replay denied") from e
    try:
        receipt = copy_descriptor_anchored(plan, grant, before_commit=before_commit)
    except BaseException as e:
        receipt = {"status": "INDETERMINATE_EXCEPTION", "plan_sha256": plan["plan_sha256"],
                   "error": f"{type(e).__name__}: {e}"}
    receipt["approval_nonce"] = grant["nonce"]
    receipt["receipt_sha256"] = digest_obj(receipt)
    # If this database write fails, the committed nonce remains IN_PROGRESS; no replay.
    with sqlite3.connect(db_path, timeout=5.0, isolation_level=None) as conn:
        conn.execute("UPDATE executions SET state=?,receipt_json=? WHERE signer=? AND nonce=? AND state='IN_PROGRESS'",
                     (receipt["status"], json.dumps(receipt, sort_keys=True), grant["signer_id"], grant["nonce"]))
    return receipt
