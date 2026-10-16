from __future__ import annotations
import multiprocessing
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path

from shared_ingress_quota import SharedIngressQuotaError, SharedIngressQuotaStore


def make(path, *, active=4, per_ip=2, rate=60, ttl=2.0, clock=time.monotonic,
         boot='test-boot', auto_renew=False, ipv6_prefix=64):
    return SharedIngressQuotaStore(
        path, max_active_connections=active, max_connections_per_ip=per_ip,
        max_new_connections_per_minute=rate, ipv6_prefix_length=ipv6_prefix,
        active_lease_ttl_seconds=ttl,
        clock=clock, boot_id=boot, auto_renew=auto_renew,
    )


def _mp_reserve(path, boot, ready, start, outcomes):
    store = make(path, active=1, per_ip=1, rate=60, ttl=2, boot=boot, auto_renew=False)
    ready.put('ready')
    if not start.wait(5):
        outcomes.put('timeout'); return
    lease, reason = store.reserve('127.0.0.1', auto_renew=False)
    if lease is None:
        outcomes.put('denied:' + str(reason)); return
    outcomes.put('accepted')
    time.sleep(0.3)
    lease.close()


def _mp_orphan_lease(path, boot, ttl):
    """Create a committed lease then simulate hard process death without release."""
    store = make(path, active=1, per_ip=1, rate=60, ttl=ttl, boot=boot, auto_renew=False)
    lease, reason = store.reserve('127.0.0.1', auto_renew=False)
    if lease is None or reason is not None:
        os._exit(3)
    # Intentionally bypass finally/close: the OS closes file descriptors as if
    # the gateway process had crashed. SQLite already committed the reservation.
    os._exit(0)


def _mp_use_inherited_store(store, result_queue):
    try:
        store.reserve('127.0.0.2', auto_renew=False)
    except SharedIngressQuotaError as exc:
        result_queue.put(str(exc))
    else:
        result_queue.put('UNEXPECTED-RESERVE-SUCCEEDED')


def _mp_hold_live_lease(path, boot, ready, release_event):
    store = make(path, active=1, per_ip=1, rate=60, ttl=0.2, boot=boot, auto_renew=False)
    lease, reason = store.reserve('127.0.0.1', auto_renew=False)
    if lease is None:
        ready.put(('error', str(reason)))
        return
    ready.put(('held', lease.lease_id))
    if not release_event.wait(5):
        lease.close()
        return
    lease.close()


class SharedIngressQuotaTests(unittest.TestCase):
    def test_global_active_limit_shared_between_store_instances(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            a, b = make(path, active=1, per_ip=1), make(path, active=1, per_ip=1)
            lease, reason = a.reserve('127.0.0.1')
            self.assertIsNone(reason)
            denied, reason = b.reserve('127.0.0.2')
            self.assertIsNone(denied); self.assertEqual(reason, 'active-connection-limit')
            lease.close()
            resumed, reason = b.reserve('127.0.0.2')
            self.assertIsNone(reason); resumed.close()

    def test_per_ip_active_limit_shared_across_gateway_instances(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            a, b = make(path, active=4, per_ip=1), make(path, active=4, per_ip=1)
            lease, reason = a.reserve('127.0.0.1')
            self.assertIsNone(reason)
            denied, reason = b.reserve('127.0.0.1')
            self.assertIsNone(denied); self.assertEqual(reason, 'per-ip-connection-limit')
            separate, reason = b.reserve('127.0.0.2')
            self.assertIsNone(reason)
            lease.close(); separate.close()

    def test_v45_replica_fails_closed_on_attempt_semantics_config_mismatch(self):
        import importlib.util
        baseline_path = Path(__file__).with_name("shared_ingress_quota_v4_5_baseline_fixture.py")
        spec = importlib.util.spec_from_file_location("baseline_v45_ingress_for_migration_test", baseline_path)
        self.assertIsNotNone(spec); self.assertIsNotNone(spec.loader)
        baseline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline_module)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            baseline_module.SharedIngressQuotaStore(
                path, max_active_connections=4, max_connections_per_ip=2,
                max_new_connections_per_minute=60, auto_renew=False, boot_id='test-boot',
            )
            with self.assertRaisesRegex(SharedIngressQuotaError, 'config-mismatch'):
                make(path, active=4, per_ip=2, rate=60)

    def test_active_quota_denials_consume_global_attempt_budget(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', active=1, per_ip=1, rate=2)
            held, reason = store.reserve('192.0.2.10')
            self.assertIsNone(reason)
            denied, reason = store.reserve('192.0.2.11')
            self.assertIsNone(denied); self.assertEqual(reason, 'active-connection-limit')
            # The slot-denied attempt spent the second token. A further attempt is
            # now rejected by the global rate guard even if a slot later frees.
            denied, reason = store.reserve('192.0.2.12')
            self.assertIsNone(denied); self.assertEqual(reason, 'connection-rate-limit')
            held.close()
            denied, reason = store.reserve('192.0.2.13')
            self.assertIsNone(denied); self.assertEqual(reason, 'connection-rate-limit')

    def test_per_ip_quota_denials_consume_global_attempt_budget(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', active=5, per_ip=1, rate=2)
            held, reason = store.reserve('192.0.2.20')
            self.assertIsNone(reason)
            denied, reason = store.reserve('192.0.2.20')
            self.assertIsNone(denied); self.assertEqual(reason, 'per-ip-connection-limit')
            denied, reason = store.reserve('192.0.2.21')
            self.assertIsNone(denied); self.assertEqual(reason, 'connection-rate-limit')
            held.close()

    def test_ipv4_mapped_ipv6_alias_uses_same_peer_quota(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', active=5, per_ip=1, rate=60)
            self.assertEqual(store._peer('192.0.2.44'), store._peer('::ffff:192.0.2.44'))
            held, reason = store.reserve('192.0.2.44')
            self.assertIsNone(reason)
            denied, reason = store.reserve('::ffff:c000:22c')
            self.assertIsNone(denied); self.assertEqual(reason, 'per-ip-connection-limit')
            held.close()
            replacement, reason = store.reserve('::ffff:192.0.2.44')
            self.assertIsNone(reason); replacement.close()

    def test_rotating_ipv6_addresses_within_same_slash64_share_quota(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', active=8, per_ip=1, rate=60)
            a = '2001:db8:1234:5678::1'
            b = '2001:db8:1234:5678:ffff:ffff:ffff:99'
            self.assertEqual(store._peer(a), store._peer(b))
            held, reason = store.reserve(a)
            self.assertIsNone(reason)
            denied, reason = store.reserve(b)
            self.assertIsNone(denied)
            self.assertEqual(reason, 'per-ip-connection-limit')
            # Release accepts a new address in the same bucket only through the
            # actual lease handle. The bucket key must be stable for reservation.
            held.close()
            retry, reason = store.reserve(b)
            self.assertIsNone(reason)
            retry.close()

    def test_ipv6_addresses_from_different_prefixes_have_independent_peer_quota(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', active=4, per_ip=1, rate=60)
            first, reason = store.reserve('2001:db8:1111:1::1')
            self.assertIsNone(reason)
            second, reason = store.reserve('2001:db8:1111:2::1')
            self.assertIsNone(reason)
            first.close()
            second.close()

    def test_ipv6_prefix_length_is_pinned_across_store_instances(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            make(path, active=4, per_ip=2, rate=60, ipv6_prefix=64)
            with self.assertRaisesRegex(SharedIngressQuotaError, 'config-mismatch'):
                make(path, active=4, per_ip=2, rate=60, ipv6_prefix=56)

    def test_invalid_ipv6_prefix_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            for value in (True, False, 0, 31, 129, 64.0, '64'):
                with self.subTest(value=value):
                    with self.assertRaisesRegex(ValueError, 'ipv6-prefix-length-invalid'):
                        make(Path(td) / f'ingress-{repr(value)}.sqlite3', ipv6_prefix=value)

    def test_global_rate_bucket_shared_across_gateway_instances_and_ips(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            a, b = make(path, active=5, per_ip=2, rate=1), make(path, active=5, per_ip=2, rate=1)
            first, reason = a.reserve('127.0.0.1')
            self.assertIsNone(reason); first.close()
            denied, reason = b.reserve('127.0.0.2')
            self.assertIsNone(denied); self.assertEqual(reason, 'connection-rate-limit')

    def test_process_reconstruction_does_not_reset_rate_bucket(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            a = make(path, rate=1)
            lease, reason = a.reserve('127.0.0.1'); self.assertIsNone(reason); lease.close()
            b = make(path, rate=1)
            denied, reason = b.reserve('127.0.0.2')
            self.assertEqual(reason, 'connection-rate-limit'); self.assertIsNone(denied)

    def test_crashed_process_lease_reclaimed_after_ttl(self):
        if 'spawn' not in multiprocessing.get_all_start_methods():
            self.skipTest('spawn unavailable')
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            boot = 'orphan-lease-boot'
            ctx = multiprocessing.get_context('spawn')
            child = ctx.Process(target=_mp_orphan_lease, args=(str(path), boot, 0.5))
            child.start(); child.join(5)
            if child.is_alive():
                child.terminate(); child.join(2)
            self.assertEqual(child.exitcode, 0)
            store = make(path, active=1, per_ip=1, ttl=0.5, boot=boot, auto_renew=False)
            # Shortly after process death, its expired-or-not-yet-expired lease
            # remains visible; only after TTL may a dead owner be reclaimed.
            self.assertEqual(store.snapshot()['active_connections'], 1)
            time.sleep(0.55)
            got, reason = store.reserve('127.0.0.2')
            self.assertIsNone(reason); self.assertIsNotNone(got)
            got.close()

    def test_expired_live_owner_lease_is_not_reclaimed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'; now = [10.0]
            a = make(path, active=1, per_ip=1, ttl=2, clock=lambda: now[0], auto_renew=False)
            b = make(path, active=1, per_ip=1, ttl=2, clock=lambda: now[0], auto_renew=False)
            lease, reason = a.reserve('127.0.0.1'); self.assertIsNone(reason)
            now[0] += 2.1
            denied, reason = b.reserve('127.0.0.2')
            self.assertIsNone(denied); self.assertEqual(reason, 'active-connection-limit')
            self.assertTrue(a.renew(lease.lease_id), 'live owner can renew its still-reserved lease')
            denied, reason = b.reserve('127.0.0.2')
            self.assertIsNone(denied); self.assertEqual(reason, 'active-connection-limit')
            lease.close()
            recovered, reason = b.reserve('127.0.0.2')
            self.assertIsNone(reason); recovered.close()

    def test_inherited_store_fails_closed_after_fork(self):
        if 'fork' not in multiprocessing.get_all_start_methods():
            self.skipTest('fork unavailable')
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3', auto_renew=False)
            ctx = multiprocessing.get_context('fork')
            result_queue = ctx.Queue()
            child = ctx.Process(target=_mp_use_inherited_store, args=(store, result_queue))
            child.start(); child.join(5)
            if child.is_alive():
                child.terminate(); child.join(2)
            self.assertEqual(child.exitcode, 0)
            result = result_queue.get(timeout=2)
            self.assertEqual(result, 'shared-ingress-store-used-after-fork-reinitialize-in-child')

    def test_one_process_cannot_renew_or_release_another_process_lease(self):
        if 'spawn' not in multiprocessing.get_all_start_methods():
            self.skipTest('spawn unavailable')
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'; boot = 'cross-owner-boot'
            store = make(path, active=1, per_ip=1, rate=60, ttl=0.2, boot=boot, auto_renew=False)
            ctx = multiprocessing.get_context('spawn')
            ready, release_event = ctx.Queue(), ctx.Event()
            child = ctx.Process(target=_mp_hold_live_lease, args=(str(path), boot, ready, release_event))
            child.start()
            status, value = ready.get(timeout=5)
            self.assertEqual(status, 'held', value)
            lease_id = value
            try:
                self.assertFalse(store.renew(lease_id))
                store.release(lease_id)  # must be a no-op for a foreign owner
                self.assertEqual(store.snapshot()['active_connections'], 1)
            finally:
                release_event.set(); child.join(5)
                if child.is_alive(): child.terminate(); child.join(2)
            self.assertEqual(child.exitcode, 0)
            got, reason = store.reserve('127.0.0.2')
            self.assertIsNone(reason); got.close()

    def test_heartbeat_keeps_live_lease_reserved_past_ttl(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            a, b = make(path, active=1, per_ip=1, ttl=0.15, auto_renew=True), make(path, active=1, per_ip=1, ttl=0.15, auto_renew=False)
            lease, reason = a.reserve('127.0.0.1'); self.assertIsNone(reason)
            time.sleep(0.35)
            denied, reason = b.reserve('127.0.0.2')
            self.assertEqual(reason, 'active-connection-limit'); self.assertIsNone(denied)
            lease.close()

    def test_clock_rollback_does_not_refill_rate_bucket(self):
        with tempfile.TemporaryDirectory() as td:
            now = [100.0]; path = Path(td) / 'ingress.sqlite3'
            store = make(path, rate=1, clock=lambda: now[0])
            lease, reason = store.reserve('127.0.0.1'); self.assertIsNone(reason); lease.close()
            now[0] = 40
            denied, reason = store.reserve('127.0.0.2')
            self.assertEqual(reason, 'connection-rate-limit'); self.assertIsNone(denied)

    def test_boot_change_resets_monotonic_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            old = make(path, rate=1, boot='boot-a')
            lease, reason = old.reserve('127.0.0.1'); self.assertIsNone(reason)
            # Simulate a namespace identity from the prior boot. It must not be
            # accepted in the same boot, but reboot clears stale monotonic state.
            import sqlite3
            conn = sqlite3.connect(path)
            try:
                config = conn.execute(
                    'SELECT config FROM shared_ingress_meta WHERE singleton=1'
                ).fetchone()[0]
                conn.execute(
                    'UPDATE shared_ingress_meta SET config=? WHERE singleton=1',
                    (config.replace(f'pidns={old.pid_namespace_inode}', 'pidns=123456'),),
                )
                conn.commit()
            finally:
                conn.close()
            new = make(path, rate=1, boot='boot-b')
            lease2, reason = new.reserve('127.0.0.1')
            self.assertIsNone(reason); self.assertIsNotNone(lease2)
            lease2.close(); lease.close()

    def test_pid_namespace_identity_is_bound_into_replica_configuration(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            store = make(path, active=4, per_ip=2, rate=60)
            import sqlite3
            conn = sqlite3.connect(path)
            try:
                config = conn.execute(
                    'SELECT config FROM shared_ingress_meta WHERE singleton=1'
                ).fetchone()[0]
            finally:
                conn.close()
            self.assertIn(f'pidns={store.pid_namespace_inode}', config)
            # A replica with a different PID namespace identity cannot safely
            # interpret the stored owner PIDs; config disagreement must fail closed.
            conn = sqlite3.connect(path)
            try:
                conn.execute(
                    'UPDATE shared_ingress_meta SET config=? WHERE singleton=1',
                    (config.replace(f'pidns={store.pid_namespace_inode}', 'pidns=999999999'),),
                )
                conn.commit()
            finally:
                conn.close()
            with self.assertRaises(SharedIngressQuotaError):
                make(path, active=4, per_ip=2, rate=60)

    def test_config_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            make(path, active=4, per_ip=2, rate=60)
            with self.assertRaises(SharedIngressQuotaError):
                make(path, active=5, per_ip=2, rate=60)

    def test_v44_schema_store_fails_closed_without_implicit_migration(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            import sqlite3
            conn = sqlite3.connect(path)
            conn.executescript('''
                CREATE TABLE shared_ingress_meta (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    config TEXT NOT NULL,
                    boot_id TEXT NOT NULL
                );
                CREATE TABLE shared_ingress_rate (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    tokens REAL NOT NULL CHECK(tokens >= 0),
                    updated_at REAL NOT NULL
                );
                CREATE TABLE shared_ingress_lease (
                    lease_id TEXT PRIMARY KEY,
                    peer_ip TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                );
            ''')
            conn.execute(
                'INSERT INTO shared_ingress_meta VALUES(1,?,?)',
                ('active=4;per_ip=2;rate_per_minute=60;ttl=2.0;schema=1', 'test-boot'),
            )
            conn.commit(); conn.close()
            with self.assertRaises(SharedIngressQuotaError):
                make(path, active=4, per_ip=2, rate=60, ttl=2.0, boot='test-boot')

    def test_snapshot_is_aggregate_and_does_not_expose_ip(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3')
            lease, reason = store.reserve('192.0.2.123'); self.assertIsNone(reason)
            snap = store.snapshot()
            self.assertEqual(snap['active_connections'], 1)
            self.assertNotIn('192.0.2.123', repr(snap))
            lease.close()

    def test_invalid_peer_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            store = make(Path(td) / 'ingress.sqlite3')
            for peer in ('', 'invalid', 123, None):
                with self.subTest(peer=peer), self.assertRaises(ValueError):
                    store.reserve(peer)

    def test_symlink_database_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'target.sqlite3'; make(target)
            alias = Path(td) / 'alias.sqlite3'; alias.symlink_to(target)
            with self.assertRaises(ValueError):
                make(alias)

    def test_database_mode_owner_only(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'; make(path)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode) & 0o077, 0)

    def test_parent_directory_must_not_be_group_or_world_writable(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / 'unsafe'; parent.mkdir(mode=0o700); parent.chmod(0o777)
            try:
                with self.assertRaises(ValueError): make(parent / 'ingress.sqlite3')
            finally:
                parent.chmod(0o700)

    def test_multiprocess_race_allows_only_one_global_active_slot(self):
        if 'spawn' not in multiprocessing.get_all_start_methods():
            self.skipTest('spawn unavailable')
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'ingress.sqlite3')
            boot = 'process-race-boot'
            make(path, active=1, per_ip=1, rate=60, boot=boot)
            ctx = multiprocessing.get_context('spawn')
            ready, start, outcomes = ctx.Queue(), ctx.Event(), ctx.Queue()
            procs = [ctx.Process(target=_mp_reserve, args=(path, boot, ready, start, outcomes)) for _ in range(2)]
            for p in procs: p.start()
            self.assertEqual(ready.get(timeout=5), 'ready'); self.assertEqual(ready.get(timeout=5), 'ready')
            start.set()
            result = [outcomes.get(timeout=5), outcomes.get(timeout=5)]
            for p in procs:
                p.join(5)
                if p.is_alive(): p.terminate(); p.join(2)
                self.assertEqual(p.exitcode, 0)
            self.assertEqual(result.count('accepted'), 1, result)
            self.assertEqual(sum(x.startswith('denied:active-connection-limit') for x in result), 1, result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
