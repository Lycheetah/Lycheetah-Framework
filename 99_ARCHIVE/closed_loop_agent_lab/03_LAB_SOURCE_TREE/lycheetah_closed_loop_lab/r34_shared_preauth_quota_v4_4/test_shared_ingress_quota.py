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
         boot='test-boot', auto_renew=False):
    return SharedIngressQuotaStore(
        path, max_active_connections=active, max_connections_per_ip=per_ip,
        max_new_connections_per_minute=rate, active_lease_ttl_seconds=ttl,
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

    def test_crashed_lease_expiry_releases_global_and_peer_slots(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'; now = [10.0]
            store = make(path, active=1, per_ip=1, ttl=2, clock=lambda: now[0])
            lease, reason = store.reserve('127.0.0.1'); self.assertIsNone(reason)
            now[0] += 2.1
            got, reason = store.reserve('127.0.0.2')
            self.assertIsNone(reason); got.close(); lease.close()

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
            new = make(path, rate=1, boot='boot-b')
            lease2, reason = new.reserve('127.0.0.1')
            self.assertIsNone(reason); self.assertIsNotNone(lease2)
            lease2.close(); lease.close()

    def test_config_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'ingress.sqlite3'
            make(path, active=4, per_ip=2, rate=60)
            with self.assertRaises(SharedIngressQuotaError):
                make(path, active=5, per_ip=2, rate=60)

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
