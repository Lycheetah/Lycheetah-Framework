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


DEFAULT_IPV6_PREFIX_LENGTH = 64


def canonical_peer_aggregate_identity(peer_ip: str, ipv6_aggregate_prefix_length: int | None) -> str | None:
    """Return an optional broader IPv6 aggregation bucket for anti-rotation limits.

    IPv4 and IPv4-mapped addresses have no aggregate bucket. The value is only a
    quota key derived from the direct socket peer, never a client identity.
    """
    if ipv6_aggregate_prefix_length is None:
        return None
    if (isinstance(ipv6_aggregate_prefix_length, bool)
            or not isinstance(ipv6_aggregate_prefix_length, int)
            or not 32 <= ipv6_aggregate_prefix_length <= 128):
        raise ValueError('shared-ingress-ipv6-aggregate-prefix-length-invalid')
    if not isinstance(peer_ip, str) or not peer_ip:
        raise ValueError('shared-ingress-peer-ip-invalid')
    try:
        address = ipaddress.ip_address(peer_ip)
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        if isinstance(address, ipaddress.IPv4Address):
            return None
        network = ipaddress.ip_network(
            f'{address.compressed}/{ipv6_aggregate_prefix_length}', strict=False
        )
        return f'ipv6-aggregate:{network.network_address.compressed}/{ipv6_aggregate_prefix_length}'
    except ValueError:
        raise ValueError('shared-ingress-peer-ip-invalid') from None


def canonical_peer_identity(peer_ip: str, ipv6_prefix_length: int = DEFAULT_IPV6_PREFIX_LENGTH) -> str:
    """Return the quota identity for a parsed direct socket peer.

    IPv4 addresses are counted individually. IPv4-mapped IPv6 addresses collapse
    to that same IPv4 identity. Native IPv6 addresses share a configurable prefix
    bucket (default /64) so address rotation inside a normal SLAAC subnet cannot
    multiply the per-peer active quota indefinitely.

    This is a quota key, not a trusted client identity. Never feed an HTTP
    forwarding header into this function as though it were a socket peer.
    """
    if isinstance(ipv6_prefix_length, bool) or not isinstance(ipv6_prefix_length, int) or not 32 <= ipv6_prefix_length <= 128:
        raise ValueError('shared-ingress-ipv6-prefix-length-invalid')
    if not isinstance(peer_ip, str) or not peer_ip:
        raise ValueError('shared-ingress-peer-ip-invalid')
    try:
        address = ipaddress.ip_address(peer_ip)
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        if isinstance(address, ipaddress.IPv4Address):
            return f'ipv4:{address.compressed}/32'
        network = ipaddress.ip_network(f'{address.compressed}/{ipv6_prefix_length}', strict=False)
        return f'ipv6:{network.network_address.compressed}/{ipv6_prefix_length}'
    except ValueError:
        raise ValueError('shared-ingress-peer-ip-invalid') from None


def _proc_self_pid() -> int | None:
    """PID as seen by the mounted procfs; used to detect a mismatched PID view."""
    try:
        raw = Path('/proc/self/stat').read_text(encoding='ascii')
        pid_text = raw.split('(', 1)[0].strip()
        return int(pid_text)
    except (OSError, TypeError, ValueError):
        return None


def _pid_namespace_inode() -> int | None:
    """Return the kernel identity of this process's PID namespace."""
    try:
        return int(Path('/proc/self/ns/pid').stat().st_ino)
    except OSError:
        return None


def _read_process_start_ticks(pid: int) -> int | None:
    """Return Linux /proc start-time ticks, or None if identity cannot be read."""
    try:
        raw = Path(f'/proc/{pid}/stat').read_text(encoding='ascii')
    except OSError:
        return None
    # `comm` is parenthesized and may itself contain spaces or parentheses. Split
    # only after the final `)` so the remaining tokens begin with field 3 (state).
    close = raw.rfind(')')
    if close < 0:
        return None
    fields = raw[close + 1:].strip().split()
    # starttime is field 22; tail[0] is field 3, so offset 19.
    if len(fields) <= 19:
        return None
    try:
        value = int(fields[19])
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


def _process_identity_matches(pid: int, start_ticks: int) -> bool | None:
    """True=the same process is alive; False=proven gone/reused; None=unknown.

    Unknown is treated conservatively as alive for reclamation purposes.
    """
    current = _read_process_start_ticks(pid)
    if current is None:
        # A missing /proc entry is evidence of death; other read/parse errors are
        # indeterminate. Distinguish those states rather than over-reclaiming.
        try:
            Path(f'/proc/{pid}/stat').stat()
        except FileNotFoundError:
            return False
        except ProcessLookupError:
            return False
        except OSError:
            return None
        return None
    return current == start_ticks


def _boot_id() -> str:
    try:
        value = Path('/proc/sys/kernel/random/boot_id').read_text(encoding='ascii').strip()
    except OSError as exc:
        raise SharedIngressQuotaError('cannot-determine-os-boot-id') from exc
    if not value or len(value) > 128:
        raise SharedIngressQuotaError('os-boot-id-invalid')
    return value


class SharedIngressQuotaStore:
    """Atomically enforce global active, per-peer-bucket active, and global rate limits.

    `reserve(peer_ip)` consumes a global connection-rate token and reserves one
    global and one per-peer active slot in a single SQLite write transaction.
    Heartbeats refresh lease expiries. Expired leases are reclaimed only after the
    owning OS process is demonstrably dead (PID plus Linux process-start ticks),
    so a live-but-paused process cannot lose its slot merely due to a timeout.
    This trades availability for safety: a wedged live process may pin capacity.
    The owner-only local database and parent directory are trusted infrastructure.
    """

    def __init__(self, database_path: str | os.PathLike[str], *,
                 max_active_connections: int, max_connections_per_ip: int,
                 max_new_connections_per_minute: int,
                 ipv6_prefix_length: int = DEFAULT_IPV6_PREFIX_LENGTH,
                 ipv6_aggregate_prefix_length: int | None = None,
                 max_connections_per_ipv6_aggregate: int | None = None,
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
        if (isinstance(ipv6_prefix_length, bool) or not isinstance(ipv6_prefix_length, int)
                or not 32 <= ipv6_prefix_length <= 128):
            raise ValueError('shared-ingress-ipv6-prefix-length-invalid')
        if (ipv6_aggregate_prefix_length is None) != (max_connections_per_ipv6_aggregate is None):
            raise ValueError('shared-ingress-ipv6-aggregate-prefix-and-limit-must-be-configured-together')
        if ipv6_aggregate_prefix_length is not None:
            if (isinstance(ipv6_aggregate_prefix_length, bool)
                    or not isinstance(ipv6_aggregate_prefix_length, int)
                    or not 32 <= ipv6_aggregate_prefix_length < ipv6_prefix_length):
                raise ValueError('shared-ingress-ipv6-aggregate-prefix-length-invalid')
            if (isinstance(max_connections_per_ipv6_aggregate, bool)
                    or not isinstance(max_connections_per_ipv6_aggregate, int)
                    or max_connections_per_ipv6_aggregate < 1
                    or max_connections_per_ipv6_aggregate > max_active_connections):
                raise ValueError('shared-ingress-ipv6-aggregate-limit-invalid')
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
        self.ipv6_prefix_length = ipv6_prefix_length
        self.ipv6_aggregate_prefix_length = ipv6_aggregate_prefix_length
        self.max_connections_per_ipv6_aggregate = max_connections_per_ipv6_aggregate
        self.active_lease_ttl_seconds = float(active_lease_ttl_seconds)
        self.busy_timeout_seconds = float(busy_timeout_seconds)
        self.clock = clock
        self.boot_id = boot_id if boot_id is not None else _boot_id()
        self.owner_pid = os.getpid()
        if _proc_self_pid() != self.owner_pid:
            raise SharedIngressQuotaError('procfs-pid-namespace-does-not-match-process-view')
        self.pid_namespace_inode = _pid_namespace_inode()
        if self.pid_namespace_inode is None or self.pid_namespace_inode <= 0:
            raise SharedIngressQuotaError('cannot-determine-pid-namespace-identity')
        self.owner_start_ticks = _read_process_start_ticks(self.owner_pid)
        if self.owner_start_ticks is None:
            raise SharedIngressQuotaError('cannot-determine-process-start-identity')
        if not isinstance(self.boot_id, str) or not self.boot_id or len(self.boot_id) > 128:
            raise ValueError('shared-ingress-boot-id-invalid')
        self.auto_renew = bool(auto_renew)
        self.config = (f'active={max_active_connections};per_ip={max_connections_per_ip};'
                       f'rate_per_minute={max_new_connections_per_minute};'
                       f'ttl={self.active_lease_ttl_seconds!r};schema=5;rate_semantics=attempts-v1;'
                       f'peer_semantics=ipv6-prefix-hierarchy-v2;ipv6_prefix={ipv6_prefix_length};'
                       f'ipv6_aggregate_prefix={ipv6_aggregate_prefix_length};'
                       f'ipv6_aggregate_limit={max_connections_per_ipv6_aggregate};'
                       f'pidns={self.pid_namespace_inode};reclaim=dead-owner-only')
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
                    expires_at REAL NOT NULL,
                    owner_pid INTEGER NOT NULL,
                    owner_start_ticks INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS shared_ingress_peer_idx
                    ON shared_ingress_lease(peer_ip);
                CREATE INDEX IF NOT EXISTS shared_ingress_expiry_idx
                    ON shared_ingress_lease(expires_at);
                CREATE TABLE IF NOT EXISTS shared_ingress_lease_aggregate (
                    lease_id TEXT PRIMARY KEY,
                    bucket_key TEXT NOT NULL,
                    FOREIGN KEY(lease_id) REFERENCES shared_ingress_lease(lease_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS shared_ingress_aggregate_bucket_idx
                    ON shared_ingress_lease_aggregate(bucket_key);
            ''')
            conn.execute('BEGIN IMMEDIATE')
            row = conn.execute('SELECT config,boot_id FROM shared_ingress_meta WHERE singleton=1').fetchone()
            if row is None:
                conn.execute('INSERT INTO shared_ingress_meta VALUES(1,?,?)', (self.config, self.boot_id))
            else:
                config, stored_boot = row
                if stored_boot != self.boot_id:
                    # A real OS boot change proves old owner processes cannot still
                    # be active. Clear monotonic state and adopt this boot's config,
                    # including the potentially new PID namespace identity.
                    conn.execute('DELETE FROM shared_ingress_lease')
                    conn.execute('DELETE FROM shared_ingress_rate')
                    conn.execute(
                        'UPDATE shared_ingress_meta SET config=?,boot_id=? WHERE singleton=1',
                        (self.config, self.boot_id),
                    )
                elif config != self.config:
                    raise SharedIngressQuotaError('shared-ingress-config-mismatch-across-replicas')
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

    def _assert_owner_process(self):
        """Reject use of a store inherited across fork; each worker must reopen it."""
        if os.getpid() != self.owner_pid:
            raise SharedIngressQuotaError('shared-ingress-store-used-after-fork-reinitialize-in-child')
        current = _read_process_start_ticks(self.owner_pid)
        if current is None or current != self.owner_start_ticks:
            raise SharedIngressQuotaError('shared-ingress-owner-process-identity-changed')

    def _prepare(self, conn, now: float):
        row = conn.execute('SELECT config,boot_id FROM shared_ingress_meta WHERE singleton=1').fetchone()
        if row is None:
            raise SharedIngressQuotaError('shared-ingress-meta-missing')
        config, boot = row
        if boot != self.boot_id:
            conn.execute('DELETE FROM shared_ingress_lease')
            conn.execute('DELETE FROM shared_ingress_rate')
            conn.execute(
                'UPDATE shared_ingress_meta SET config=?,boot_id=? WHERE singleton=1',
                (self.config, self.boot_id),
            )
        elif config != self.config:
            raise SharedIngressQuotaError('shared-ingress-config-mismatch-across-replicas')
        # A timeout alone must not reclaim a lease from a live-but-paused owner.
        # Otherwise a second gateway could admit a replacement while the original
        # handler later resumes. Reclaim only expired leases whose OS process is
        # demonstrably gone or whose PID has been reused (start ticks differ).
        expired = conn.execute(
            'SELECT lease_id,owner_pid,owner_start_ticks FROM shared_ingress_lease WHERE expires_at <= ?',
            (now,),
        ).fetchall()
        for lease_id, owner_pid, owner_start_ticks in expired:
            alive = _process_identity_matches(int(owner_pid), int(owner_start_ticks))
            if alive is False:
                conn.execute('DELETE FROM shared_ingress_lease WHERE lease_id=?', (lease_id,))

    @staticmethod
    def _peer(peer_ip: str, ipv6_prefix_length: int = DEFAULT_IPV6_PREFIX_LENGTH) -> str:
        return canonical_peer_identity(peer_ip, ipv6_prefix_length)

    def reserve(self, peer_ip: str, *, auto_renew: bool | None = None):
        self._assert_owner_process()
        peer = self._peer(peer_ip, self.ipv6_prefix_length)
        aggregate = canonical_peer_aggregate_identity(peer_ip, self.ipv6_aggregate_prefix_length)
        now = self.clock()
        lease_id = uuid.uuid4().hex
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            self._prepare(conn, now)
            # Count every accepted TCP connection reaching this pre-authentication
            # admission gate, including requests denied by active/per-peer limits.
            # Otherwise an attacker can hammer saturated quota paths without ever
            # spending a token from the global new-connection budget.
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

            active = int(conn.execute('SELECT count(*) FROM shared_ingress_lease').fetchone()[0])
            if active >= self.max_active_connections:
                conn.commit()
                return None, 'active-connection-limit'
            per_ip = int(conn.execute('SELECT count(*) FROM shared_ingress_lease WHERE peer_ip=?', (peer,)).fetchone()[0])
            if per_ip >= self.max_connections_per_ip:
                conn.commit()
                return None, 'per-ip-connection-limit'
            if aggregate is not None and self.max_connections_per_ipv6_aggregate is not None:
                aggregate_count = int(conn.execute(
                    'SELECT count(*) FROM shared_ingress_lease_aggregate WHERE bucket_key=?',
                    (aggregate,),
                ).fetchone()[0])
                if aggregate_count >= self.max_connections_per_ipv6_aggregate:
                    conn.commit()
                    return None, 'ipv6-aggregate-connection-limit'
            conn.execute(
                'INSERT INTO shared_ingress_lease '
                '(lease_id,peer_ip,created_at,expires_at,owner_pid,owner_start_ticks) '
                'VALUES(?,?,?,?,?,?)',
                (lease_id, peer, now, now + self.active_lease_ttl_seconds,
                 self.owner_pid, self.owner_start_ticks),
            )
            if aggregate is not None:
                conn.execute(
                    'INSERT INTO shared_ingress_lease_aggregate(lease_id,bucket_key) VALUES(?,?)',
                    (lease_id, aggregate),
                )
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
        self._assert_owner_process()
        now = self.clock()
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            self._prepare(conn, now)
            # Expiry enables reclamation only after owner death. A live owner may
            # resume after a long scheduler pause and renew its still-reserved slot.
            cur = conn.execute(
                'UPDATE shared_ingress_lease SET expires_at=? '
                'WHERE lease_id=? AND owner_pid=? AND owner_start_ticks=?',
                (now + self.active_lease_ttl_seconds, lease_id,
                 self.owner_pid, self.owner_start_ticks),
            )
            conn.commit()
            return cur.rowcount == 1
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.rollback()
            raise SharedIngressQuotaError('shared-ingress-renewal-failed') from exc
        finally:
            conn.close()

    def release(self, lease_id: str):
        self._assert_owner_process()
        conn = self._connect()
        try:
            conn.execute('BEGIN IMMEDIATE')
            # Do not allow one gateway process to release another process's slot.
            conn.execute(
                'DELETE FROM shared_ingress_lease '
                'WHERE lease_id=? AND owner_pid=? AND owner_start_ticks=?',
                (lease_id, self.owner_pid, self.owner_start_ticks),
            )
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
            aggregate_buckets = int(conn.execute('SELECT count(DISTINCT bucket_key) FROM shared_ingress_lease_aggregate').fetchone()[0])
            rate = conn.execute('SELECT tokens FROM shared_ingress_rate WHERE singleton=1').fetchone()
            conn.commit()
            return {'mode': 'shared-sqlite-same-host', 'active_connections': total,
                    'active_peer_count': peers, 'active_ipv6_aggregate_buckets': aggregate_buckets,
                    'global_rate_tokens': round(float(rate[0]), 3) if rate else self.max_new_connections_per_minute}
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
