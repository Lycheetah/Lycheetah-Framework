from __future__ import annotations

import multiprocessing
import tempfile
import threading
import time
import unittest
from pathlib import Path

from shared_coordinator_quota import SharedCoordinatorQuotaStore, SharedQuotaError

PRINCIPAL_A = "spiffe://lycheetah.local/coordinator-a"
PRINCIPAL_B = "spiffe://lycheetah.local/coordinator-b"


def _store(path, *, active=1, rate=60, ttl=2.0, clock=time.monotonic, boot_id="test-boot", auto_renew=True):
    return SharedCoordinatorQuotaStore(
        str(path), max_active_per_coordinator=active,
        max_requests_per_minute=rate, active_lease_ttl_seconds=ttl,
        clock=clock, boot_id=boot_id, auto_renew=auto_renew,
    )


def _process_reserve(path: str, boot_id: str, ready, start, results):
    store = SharedCoordinatorQuotaStore(
        path, max_active_per_coordinator=1, max_requests_per_minute=60,
        active_lease_ttl_seconds=2.0, boot_id=boot_id, auto_renew=False,
    )
    ready.put("ready")
    if not start.wait(5):
        results.put("timeout")
        return
    lease, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
    if lease is None:
        results.put("denied:" + str(reason))
        return
    results.put("accepted")
    # Hold the winner open while the other process attempts the same identity.
    time.sleep(0.5)
    lease.close()


class SharedCoordinatorQuotaTests(unittest.TestCase):
    def test_active_limit_is_shared_between_independent_store_instances(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            first = _store(path, active=1)
            second = _store(path, active=1)
            lease, reason = first.reserve(PRINCIPAL_A)
            self.assertIsNone(reason)
            denied, reason = second.reserve(PRINCIPAL_A)
            self.assertIsNone(denied)
            self.assertEqual(reason, "coordinator-active-request-limit")
            lease.close()
            after, reason = second.reserve(PRINCIPAL_A)
            self.assertIsNone(reason)
            after.close()

    def test_rate_bucket_persists_across_store_reconstruction(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            first = _store(path, active=2, rate=1)
            lease, reason = first.reserve(PRINCIPAL_A)
            self.assertIsNone(reason)
            lease.close()
            second = _store(path, active=2, rate=1)
            blocked, reason = second.reserve(PRINCIPAL_A)
            self.assertIsNone(blocked)
            self.assertEqual(reason, "coordinator-request-rate-limit")

    def test_identities_have_independent_shared_buckets_and_slots(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            a = _store(path, active=1, rate=1)
            b = _store(path, active=1, rate=1)
            lease_a, reason_a = a.reserve(PRINCIPAL_A)
            lease_b, reason_b = b.reserve(PRINCIPAL_B)
            self.assertIsNone(reason_a)
            self.assertIsNone(reason_b)
            self.assertEqual(a.snapshot()["active_leases"], 2)
            self.assertNotIn(PRINCIPAL_A, str(a.snapshot()))
            lease_a.close()
            lease_b.close()

    def test_active_lease_heartbeat_keeps_live_request_reserved_past_ttl(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            first = _store(path, active=1, rate=60, ttl=0.15, auto_renew=True)
            second = _store(path, active=1, rate=60, ttl=0.15, auto_renew=True)
            lease, reason = first.reserve(PRINCIPAL_A)
            self.assertIsNone(reason)
            time.sleep(0.35)
            denied, reason = second.reserve(PRINCIPAL_A)
            self.assertIsNone(denied)
            self.assertEqual(reason, "coordinator-active-request-limit")
            lease.close()

    def test_database_mode_is_owner_only(self):
        import os
        import stat
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            _store(path)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode) & 0o077, 0)

    def test_group_or_world_writable_parent_directory_is_rejected(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / "unsafe"
            parent.mkdir(mode=0o700)
            parent.chmod(0o777)
            try:
                with self.assertRaises(ValueError):
                    _store(parent / "quota.sqlite3")
            finally:
                parent.chmod(0o700)

    def test_database_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "actual.sqlite3"
            _store(target)
            alias = root / "alias.sqlite3"
            alias.symlink_to(target)
            with self.assertRaises(ValueError):
                _store(alias)

    def test_principal_must_be_nonempty_and_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            store = _store(Path(td) / "quota.sqlite3")
            for value in ("", 7, "x" * 513):
                with self.subTest(value_type=type(value).__name__, length=len(value) if isinstance(value, str) else None):
                    with self.assertRaises(ValueError):
                        store.reserve(value)

    def test_config_mismatch_across_replicas_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            _store(path, active=2, rate=10)
            with self.assertRaises(SharedQuotaError):
                _store(path, active=3, rate=10)

    def test_crashed_lease_expires_and_frees_slot(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            now = [10.0]
            store = _store(path, active=1, rate=60, ttl=5.0, clock=lambda: now[0], auto_renew=False)
            lease, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertIsNone(reason)
            denied, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertEqual(reason, "coordinator-active-request-limit")
            now[0] += 5.1
            recovered, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertIsNone(reason)
            recovered.close()
            lease.close()

    def test_os_boot_id_change_resets_monotonic_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            first = _store(path, active=1, rate=1, boot_id="boot-A", auto_renew=False)
            lease, reason = first.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertIsNone(reason)
            second = _store(path, active=1, rate=1, boot_id="boot-B", auto_renew=False)
            fresh, reason = second.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertIsNone(reason)
            self.assertIsNotNone(fresh)
            fresh.close()

    def test_monotonic_clock_backstep_does_not_refill_rate_bucket(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "quota.sqlite3"
            now = [100.0]
            store = _store(path, active=3, rate=1, clock=lambda: now[0], auto_renew=False)
            lease, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertIsNone(reason)
            lease.close()
            now[0] = 50.0
            denied, reason = store.reserve(PRINCIPAL_A, auto_renew=False)
            self.assertEqual(reason, "coordinator-request-rate-limit")

    def test_multiprocess_race_allows_only_one_active_slot(self):
        # Separate OS processes use separate SQLite connections against the same
        # file. Spawn avoids inheriting unrelated test-suite threads.
        if "spawn" not in multiprocessing.get_all_start_methods():
            self.skipTest("spawn multiprocessing context unavailable")
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / "quota.sqlite3")
            boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
            _store(path, active=1, rate=60, ttl=2.0, boot_id=boot_id)
            ctx = multiprocessing.get_context("spawn")
            ready = ctx.Queue()
            results = ctx.Queue()
            start = ctx.Event()
            processes = [ctx.Process(target=_process_reserve, args=(path, boot_id, ready, start, results)) for _ in range(2)]
            for proc in processes:
                proc.start()
            self.assertEqual(ready.get(timeout=5), "ready")
            self.assertEqual(ready.get(timeout=5), "ready")
            start.set()
            outcomes = [results.get(timeout=5), results.get(timeout=5)]
            for proc in processes:
                proc.join(timeout=5)
                if proc.is_alive():
                    proc.terminate()
                    proc.join(timeout=2)
                self.assertEqual(proc.exitcode, 0)
            self.assertEqual(outcomes.count("accepted"), 1, outcomes)
            self.assertEqual(sum(x.startswith("denied:coordinator-active-request-limit") for x in outcomes), 1, outcomes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
