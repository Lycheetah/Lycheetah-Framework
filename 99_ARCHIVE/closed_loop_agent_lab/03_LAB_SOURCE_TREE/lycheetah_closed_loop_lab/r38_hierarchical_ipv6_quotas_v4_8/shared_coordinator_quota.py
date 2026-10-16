"""Shared, transactional coordinator quotas for same-host gateway replicas.

This is a reference component, not a distributed quota service. Multiple Python
processes on one host can share the SQLite ledger. Monotonic timestamps are valid
only during one OS boot; a detected boot-ID change resets rate buckets and removes
old active leases. Configure all gateway replicas with the same DB path and quota
settings. The parent directory and database must be writable only by the trusted
service identity.
"""
from __future__ import annotations

import os
import sqlite3
import stat
import threading
import time
import uuid
from pathlib import Path
from typing import Callable


class SharedQuotaError(RuntimeError):
    """Shared quota authority unavailable or configured inconsistently."""


def _linux_boot_id() -> str:
    try:
        value = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
    except OSError as exc:
        raise SharedQuotaError(
            "cannot-determine-os-boot-id; pass an explicit stable boot_id"
        ) from exc
    if not value or len(value) > 128:
        raise SharedQuotaError("os-boot-id-invalid")
    return value


class SharedCoordinatorQuotaStore:
    """SQLite-backed token bucket and active-request leases shared across processes.

    `clock` and `boot_id` are injectable for deterministic tests. Production use
    should use the system monotonic clock and detected OS boot ID. `active_lease_ttl`
    must exceed the bounded request/dispatch duration; active leases are renewed
    while a handler is in progress and expire after a process crash.
    """

    def __init__(
        self,
        database_path: str | os.PathLike[str],
        *,
        max_active_per_coordinator: int,
        max_requests_per_minute: int,
        active_lease_ttl_seconds: float = 120.0,
        clock: Callable[[], float] = time.monotonic,
        boot_id: str | None = None,
        busy_timeout_seconds: float = 5.0,
        auto_renew: bool = True,
    ):
        path = Path(database_path)
        if not path.is_absolute():
            raise ValueError("shared-quota-database-path-must-be-absolute")
        if path.exists() and path.is_symlink():
            raise ValueError("shared-quota-database-must-not-be-symlink")
        for value, name in (
            (max_active_per_coordinator, "max-active-per-coordinator"),
            (max_requests_per_minute, "max-requests-per-minute"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"shared-quota-{name}-invalid")
        if (isinstance(active_lease_ttl_seconds, bool)
                or not isinstance(active_lease_ttl_seconds, (float, int))
                or active_lease_ttl_seconds <= 0 or not float(active_lease_ttl_seconds) < float("inf")):
            raise ValueError("shared-quota-active-lease-ttl-invalid")
        if (isinstance(busy_timeout_seconds, bool)
                or not isinstance(busy_timeout_seconds, (int, float))
                or busy_timeout_seconds <= 0 or not float(busy_timeout_seconds) < float("inf")):
            raise ValueError("shared-quota-busy-timeout-invalid")
        if not callable(clock):
            raise ValueError("shared-quota-clock-must-be-callable")
        self.path = path
        self.max_active_per_coordinator = max_active_per_coordinator
        self.max_requests_per_minute = max_requests_per_minute
        self.active_lease_ttl_seconds = float(active_lease_ttl_seconds)
        self.clock = clock
        self.boot_id = boot_id if boot_id is not None else _linux_boot_id()
        if not isinstance(self.boot_id, str) or not self.boot_id or len(self.boot_id) > 128:
            raise ValueError("shared-quota-boot-id-invalid")
        self.busy_timeout_seconds = float(busy_timeout_seconds)
        self.auto_renew = bool(auto_renew)
        self._config_json = (
            f"max_active={self.max_active_per_coordinator};"
            f"rate_per_minute={self.max_requests_per_minute};"
            f"lease_ttl={self.active_lease_ttl_seconds!r}"
        )
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        parent_stat = self.path.parent.stat()
        if parent_stat.st_uid != os.geteuid() or (parent_stat.st_mode & 0o022):
            raise ValueError("shared-quota-parent-directory-must-be-owned-and-not-group-or-world-writable")
        # Create the main DB with owner-only permissions. Refuse symlinks where
        # supported, then keep WAL and shared-memory files under the same directory.
        flags = os.O_CREAT | os.O_RDWR
        flags |= getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("shared-quota-database-not-regular-file")
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(
                self.path, timeout=self.busy_timeout_seconds,
                isolation_level=None, check_same_thread=False,
            )
            conn.execute(f"PRAGMA busy_timeout={int(self.busy_timeout_seconds * 1000)}")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA synchronous=FULL")
            return conn
        except sqlite3.Error as exc:
            raise SharedQuotaError("shared-quota-database-connect-failed") from exc

    def _initialize(self) -> None:
        conn = self._connect()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS shared_quota_meta (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    config TEXT NOT NULL,
                    boot_id TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS coordinator_rate_bucket (
                    principal TEXT PRIMARY KEY,
                    tokens REAL NOT NULL CHECK(tokens >= 0),
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS coordinator_active_lease (
                    lease_id TEXT PRIMARY KEY,
                    principal TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS active_lease_principal_idx
                    ON coordinator_active_lease(principal);
                CREATE INDEX IF NOT EXISTS active_lease_expiry_idx
                    ON coordinator_active_lease(expires_at);
            """)
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT config, boot_id FROM shared_quota_meta WHERE singleton=1"
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO shared_quota_meta(singleton, config, boot_id) VALUES(1, ?, ?)",
                    (self._config_json, self.boot_id),
                )
            else:
                stored_config, stored_boot = row
                if stored_config != self._config_json:
                    raise SharedQuotaError("shared-quota-config-mismatch-across-replicas")
                if stored_boot != self.boot_id:
                    # monotonic clock origin changed after OS reboot. Clear stale
                    # active leases and buckets; process restart alone does not reset.
                    conn.execute("DELETE FROM coordinator_active_lease")
                    conn.execute("DELETE FROM coordinator_rate_bucket")
                    conn.execute(
                        "UPDATE shared_quota_meta SET boot_id=? WHERE singleton=1",
                        (self.boot_id,),
                    )
            conn.commit()
            os.chmod(self.path, 0o600)
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedQuotaError("shared-quota-database-initialize-failed") from exc
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def _prepare_boot(self, conn: sqlite3.Connection, now: float) -> None:
        row = conn.execute(
            "SELECT config, boot_id FROM shared_quota_meta WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise SharedQuotaError("shared-quota-meta-missing")
        config, stored_boot = row
        if config != self._config_json:
            raise SharedQuotaError("shared-quota-config-mismatch-across-replicas")
        if stored_boot != self.boot_id:
            conn.execute("DELETE FROM coordinator_active_lease")
            conn.execute("DELETE FROM coordinator_rate_bucket")
            conn.execute(
                "UPDATE shared_quota_meta SET boot_id=? WHERE singleton=1", (self.boot_id,)
            )
        conn.execute("DELETE FROM coordinator_active_lease WHERE expires_at <= ?", (now,))

    def reserve(self, principal: str, *, auto_renew: bool | None = None):
        """Reserve rate token and active slot atomically.

        Returns `(QuotaLease, None)` on success, or `(None, reason)` when denied.
        Database errors raise SharedQuotaError; callers should fail closed.
        """
        if not isinstance(principal, str) or not principal or len(principal) > 512:
            raise ValueError("shared-quota-principal-invalid")
        now = self.clock()
        lease_id = uuid.uuid4().hex
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._prepare_boot(conn, now)
            active = conn.execute(
                "SELECT count(*) FROM coordinator_active_lease WHERE principal=?", (principal,)
            ).fetchone()[0]
            if active >= self.max_active_per_coordinator:
                conn.commit()
                return None, "coordinator-active-request-limit"
            row = conn.execute(
                "SELECT tokens, updated_at FROM coordinator_rate_bucket WHERE principal=?",
                (principal,),
            ).fetchone()
            if row is None:
                tokens = float(self.max_requests_per_minute)
                updated = now
            else:
                previous_tokens, previous_at = float(row[0]), float(row[1])
                elapsed = max(0.0, now - previous_at)
                tokens = min(
                    float(self.max_requests_per_minute),
                    previous_tokens + elapsed * self.max_requests_per_minute / 60.0,
                )
                updated = max(now, previous_at) if now < previous_at else now
            if tokens < 1.0:
                conn.execute(
                    "INSERT INTO coordinator_rate_bucket(principal,tokens,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(principal) DO UPDATE SET tokens=excluded.tokens,updated_at=excluded.updated_at",
                    (principal, tokens, updated),
                )
                conn.commit()
                return None, "coordinator-request-rate-limit"
            conn.execute(
                "INSERT INTO coordinator_rate_bucket(principal,tokens,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(principal) DO UPDATE SET tokens=excluded.tokens,updated_at=excluded.updated_at",
                (principal, tokens - 1.0, updated),
            )
            conn.execute(
                "INSERT INTO coordinator_active_lease(lease_id,principal,created_at,expires_at) VALUES(?,?,?,?)",
                (lease_id, principal, now, now + self.active_lease_ttl_seconds),
            )
            conn.commit()
        except SharedQuotaError:
            if conn.in_transaction:
                conn.rollback()
            raise
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedQuotaError("shared-quota-reservation-failed") from exc
        finally:
            conn.close()
        renew = self.auto_renew if auto_renew is None else auto_renew
        return QuotaLease(self, lease_id, principal, auto_renew=renew), None

    def renew(self, lease_id: str) -> bool:
        now = self.clock()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._prepare_boot(conn, now)
            cur = conn.execute(
                "UPDATE coordinator_active_lease SET expires_at=? "
                "WHERE lease_id=? AND expires_at > ?",
                (now + self.active_lease_ttl_seconds, lease_id, now),
            )
            conn.commit()
            return cur.rowcount == 1
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedQuotaError("shared-quota-lease-renewal-failed") from exc
        finally:
            conn.close()

    def release(self, lease_id: str) -> None:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM coordinator_active_lease WHERE lease_id=?", (lease_id,))
            conn.commit()
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedQuotaError("shared-quota-lease-release-failed") from exc
        finally:
            conn.close()

    def snapshot(self) -> dict[str, int | str]:
        now = self.clock()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._prepare_boot(conn, now)
            active = conn.execute("SELECT count(*) FROM coordinator_active_lease").fetchone()[0]
            principals = conn.execute("SELECT count(DISTINCT principal) FROM coordinator_active_lease").fetchone()[0]
            buckets = conn.execute("SELECT count(*) FROM coordinator_rate_bucket").fetchone()[0]
            conn.commit()
            return {
                "mode": "shared-sqlite-same-host",
                "active_leases": int(active),
                "active_principal_count": int(principals),
                "rate_bucket_count": int(buckets),
            }
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedQuotaError("shared-quota-snapshot-failed") from exc
        finally:
            conn.close()


class QuotaLease:
    """Active request lease with background heartbeat and idempotent release."""

    def __init__(self, store: SharedCoordinatorQuotaStore, lease_id: str, principal: str, *, auto_renew: bool):
        self.store = store
        self.lease_id = lease_id
        self.principal = principal
        self._stop = threading.Event()
        self._released = False
        self._lock = threading.Lock()
        self._renewal_error: str | None = None
        self._thread: threading.Thread | None = None
        if auto_renew:
            interval = max(0.01, min(10.0, store.active_lease_ttl_seconds / 3.0))
            self._thread = threading.Thread(
                target=self._heartbeat, args=(interval,), daemon=True,
                name="coordinator-quota-lease-heartbeat",
            )
            self._thread.start()

    @property
    def renewal_error(self) -> str | None:
        return self._renewal_error

    def _heartbeat(self, interval: float) -> None:
        while not self._stop.wait(interval):
            try:
                if not self.store.renew(self.lease_id):
                    self._renewal_error = "lease-expired-or-revoked"
                    return
                self._renewal_error = None
            except SharedQuotaError:
                # Retry on the next heartbeat; lease expiry and backend health remain
                # explicit operational concerns if the store is unavailable too long.
                self._renewal_error = "renewal-backend-unavailable"

    def close(self) -> None:
        with self._lock:
            if self._released:
                return
            self._released = True
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(1.0, self.store.active_lease_ttl_seconds / 3.0 + 0.1))
        self.store.release(self.lease_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
