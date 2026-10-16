"""Shared same-host pre-authentication connection quotas for the mTLS gateway.

This reference component complements authenticated coordinator quotas. Its SQLite
ledger is shared by gateway processes on one host, before the TLS handshake and
before coordinator identity is known. It is not a distributed quota service.
"""
from __future__ import annotations

import os
import sqlite3
import stat
import threading
import time
import uuid
import ipaddress
from pathlib import Path
from typing import Callable


class SharedIngressQuotaError(RuntimeError):
    """Shared ingress quota authority unavailable or misconfigured."""


def _boot_id() -> str:
    try:
        value = Path('/proc/sys/kernel/random/boot_id').read_text(encoding='ascii').strip()
    except OSError as exc:
        raise SharedIngressQuotaError('cannot-determine-os-boot-id') from exc
    if not value or len(value) > 128:
        raise SharedIngressQuotaError('os-boot-id-invalid')
    return value


class SharedIngressQuotaStore:
    """Atomically enforce global active, per-IP active, and global rate limits.

    `reserve(peer_ip)` consumes a global connection-rate token and reserves one
    global and one per-peer active slot in a single SQLite write transaction.
    Expiring heartbeats recover slots after a crashed handler. The owner-only local
    database and parent directory are part of the trusted computing base.
    """

    def __init__(self, database_path: str | os.PathLike[str], *,
                 max_active_connections: int, max_connections_per_ip: int,
                 max_new_connections_per_minute: int,
                 active_lease_ttl_seconds: float = 120.0,
                 clock: Callable[[], float] = time.monotonic,
                 boot_id: str | None = None,
                 busy_timeout_seconds: float = 5.0,
                 auto_renew: bool = True):
        path = Path(database_path)
        if not path.is_absolute():
            raise ValueError('shared-ingress-database-path-must-be-absolute')
        if path.exists() and path.is_symlink():
            raise ValueError('shared-ingress-database-must-not-be-symlink')
        for value, name in (
            (max_active_connections, 'max-active-connections'),
            (max_connections_per_ip, 'max-connections-per-ip'),
            (max_new_connections_per_minute, 'max-new-connections-per-minute'),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f'shared-ingress-{name}-invalid')
        if max_connections_per_ip > max_active_connections:
            raise ValueError('shared-ingress-per-ip-limit-exceeds-global-limit')
        for value, name in ((active_lease_ttl_seconds, 'active-lease-ttl'),
                            (busy_timeout_seconds, 'busy-timeout')):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or value <= 0 or not float(value) < float('inf')):
                raise ValueError(f'shared-ingress-{name}-invalid')
        if not callable(clock):
            raise ValueError('shared-ingress-clock-must-be-callable')
        self.path = path
        self.max_active_connections = max_active_connections
        self.max_connections_per_ip = max_connections_per_ip
        self.max_new_connections_per_minute = max_new_connections_per_minute
        self.active_lease_ttl_seconds = float(active_lease_ttl_seconds)
        self.busy_timeout_seconds = float(busy_timeout_seconds)
        self.clock = clock
        self.boot_id = boot_id if boot_id is not None else _boot_id()
        if not isinstance(self.boot_id, str) or not self.boot_id or len(self.boot_id) > 128:
            raise ValueError('shared-ingress-boot-id-invalid')
        self.auto_renew = bool(auto_renew)
        self.config = (f'active={max_active_connections};per_ip={max_connections_per_ip};'
                       f'rate_per_minute={max_new_connections_per_minute};'
                       f'ttl={self.active_lease_ttl_seconds!r};schema=1')
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        parent_stat = self.path.parent.stat()
        if parent_stat.st_uid != os.geteuid() or (parent_stat.st_mode & 0o022):
            raise ValueError('shared-ingress-parent-must-be-owned-and-not-group-or-world-writable')
        flags = os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(self.path, flags, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('shared-ingress-database-not-regular-file')
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)
        self._initialize()

    def _connect(self):
        try:
            conn = sqlite3.connect(self.path, timeout=self.busy_timeout_seconds,
                                   isolation_level=None, check_same_thread=False)
            conn.execute(f'PRAGMA busy_timeout={int(self.busy_timeout_seconds * 1000)}')
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA synchronous=FULL')
            return conn
        except sqlite3.Error as exc:
            raise SharedIngressQuotaError('shared-ingress-connect-failed') from exc

    def _initialize(self):
        conn = self._connect()
        try:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS shared_ingress_meta (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    config TEXT NOT NULL,
                    boot_id TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS shared_ingress_rate (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    tokens REAL NOT NULL CHECK(tokens >= 0),
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS shared_ingress_lease (
                    lease_id TEXT PRIMARY KEY,
                    peer_ip TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS shared_ingress_peer_idx
                    ON shared_ingress_lease(peer_ip);
                CREATE INDEX IF NOT EXISTS shared_ingress_expiry_idx
                    ON shared_ingress_lease(expires_at);
            ''')
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT config,boot_id FROM shared_ingress_meta WHERE singleton=1').fetchone()
            if row is None:
                conn.execute('INSERT INTO shared_ingress_meta VALUES(1,?,?)', (self.config, self.boot_id))
            else:
                config, stored_boot = row
                if config != self.config:
                    raise SharedIngressQuotaError('shared-ingress-config-mismatch-across-replicas')
                if stored_boot != self.boot_id:
                    conn.execute('DELETE FROM shared_ingress_lease')
                    conn.execute('DELETE FROM shared_ingress_rate')
                    conn.execute('UPDATE shared_ingress_meta SET boot_id=? WHERE singleton=1', (self.boot_id,))
            conn.commit()
            os.chmod(self.path, 0o600)
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-initialize-failed') from exc
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def _prepare(self, conn, now: float):
        row = conn.execute('SELECT config,boot_id FROM shared_ingress_meta WHERE singleton=1').fetchone()
        if row is None:
            raise SharedIngressQuotaError('shared-ingress-meta-missing')
        config, boot = row
        if config != self.config:
            raise SharedIngressQuotaError('shared-ingress-config-mismatch-across-replicas')
        if boot != self.boot_id:
            conn.execute('DELETE FROM shared_ingress_lease')
            conn.execute('DELETE FROM shared_ingress_rate')
            conn.execute('UPDATE shared_ingress_meta SET boot_id=? WHERE singleton=1', (self.boot_id,))
        conn.execute('DELETE FROM shared_ingress_lease WHERE expires_at <= ?', (now,))

    @staticmethod
    def _peer(peer_ip: str) -> str:
        if not isinstance(peer_ip, str) or not peer_ip:
            raise ValueError('shared-ingress-peer-ip-invalid')
        try:
            return ipaddress.ip_address(peer_ip).compressed
        except ValueError:
            raise ValueError('shared-ingress-peer-ip-invalid') from None

    def reserve(self, peer_ip: str, *, auto_renew: bool | None = None):
        peer = self._peer(peer_ip)
        now = self.clock()
        lease_id = uuid.uuid4().hex
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            self._prepare(conn, now)
            active = int(conn.execute('SELECT count(*) FROM shared_ingress_lease').fetchone()[0])
            if active >= self.max_active_connections:
                conn.commit()
                return None, 'active-connection-limit'
            per_ip = int(conn.execute('SELECT count(*) FROM shared_ingress_lease WHERE peer_ip=?', (peer,)).fetchone()[0])
            if per_ip >= self.max_connections_per_ip:
                conn.commit()
                return None, 'per-ip-connection-limit'
            row = conn.execute('SELECT tokens,updated_at FROM shared_ingress_rate WHERE singleton=1').fetchone()
            if row is None:
                tokens, previous_at = float(self.max_new_connections_per_minute), now
            else:
                previous_tokens, previous_at = float(row[0]), float(row[1])
                elapsed = max(0.0, now - previous_at)
                tokens = min(float(self.max_new_connections_per_minute),
                             previous_tokens + elapsed * self.max_new_connections_per_minute / 60.0)
            # Never move the persisted clock backwards; this prevents a clock rollback
            # from creating tokens, while still allowing elapsed time to refill later.
            updated_at = max(now, previous_at)
            if tokens < 1.0:
                conn.execute('INSERT INTO shared_ingress_rate VALUES(1,?,?) ON CONFLICT(singleton) DO UPDATE SET tokens=excluded.tokens,updated_at=excluded.updated_at',
                             (tokens, updated_at))
                conn.commit()
                return None, 'connection-rate-limit'
            conn.execute('INSERT INTO shared_ingress_rate VALUES(1,?,?) ON CONFLICT(singleton) DO UPDATE SET tokens=excluded.tokens,updated_at=excluded.updated_at',
                         (tokens - 1.0, updated_at))
            conn.execute('INSERT INTO shared_ingress_lease VALUES(?,?,?,?)',
                         (lease_id, peer, now, now + self.active_lease_ttl_seconds))
            conn.commit()
        except SharedIngressQuotaError:
            if conn.in_transaction:
                conn.rollback()
            raise
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-reservation-failed') from exc
        finally:
            conn.close()
        renew = self.auto_renew if auto_renew is None else auto_renew
        return IngressConnectionLease(self, lease_id, peer, auto_renew=renew), None

    def renew(self, lease_id: str) -> bool:
        now = self.clock()
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            self._prepare(conn, now)
            cur = conn.execute('UPDATE shared_ingress_lease SET expires_at=? WHERE lease_id=? AND expires_at> ?',
                               (now + self.active_lease_ttl_seconds, lease_id, now))
            conn.commit()
            return cur.rowcount == 1
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-renewal-failed') from exc
        finally:
            conn.close()

    def release(self, lease_id: str):
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('DELETE FROM shared_ingress_lease WHERE lease_id=?', (lease_id,))
            conn.commit()
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-release-failed') from exc
        finally:
            conn.close()

    def snapshot(self) -> dict[str, int | str]:
        now = self.clock()
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            self._prepare(conn, now)
            total = int(conn.execute('SELECT count(*) FROM shared_ingress_lease').fetchone()[0])
            peers = int(conn.execute('SELECT count(DISTINCT peer_ip) FROM shared_ingress_lease').fetchone()[0])
            rate = conn.execute('SELECT tokens FROM shared_ingress_rate WHERE singleton=1').fetchone()
            conn.commit()
            return {'mode': 'shared-sqlite-same-host', 'active_connections': total,
                    'active_peer_count': peers, 'global_rate_tokens': round(float(rate[0]), 3) if rate else self.max_new_connections_per_minute}
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-snapshot-failed') from exc
        finally:
            conn.close()


class IngressConnectionLease:
    def __init__(self, store: SharedIngressQuotaStore, lease_id: str, peer_ip: str, *, auto_renew: bool):
        self.store, self.lease_id, self.peer_ip = store, lease_id, peer_ip
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._released = False
        self._renewal_error: str | None = None
        self._thread = None
        if auto_renew:
            interval = max(0.01, min(10.0, store.active_lease_ttl_seconds / 3.0))
            self._thread = threading.Thread(target=self._heartbeat, args=(interval,), daemon=True,
                                            name='shared-ingress-quota-heartbeat')
            self._thread.start()

    @property
    def renewal_error(self) -> str | None:
        return self._renewal_error

    def _heartbeat(self, interval: float):
        while not self._stop.wait(interval):
            try:
                if not self.store.renew(self.lease_id):
                    self._renewal_error = 'lease-expired-or-revoked'
                    return
                self._renewal_error = None
            except SharedIngressQuotaError:
                self._renewal_error = 'renewal-backend-unavailable'

    def close(self):
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
