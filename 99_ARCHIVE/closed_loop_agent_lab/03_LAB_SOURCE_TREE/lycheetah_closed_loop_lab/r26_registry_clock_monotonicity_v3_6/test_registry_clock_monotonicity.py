from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
import uuid
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import canonical
from spent_nonce_registry import (
    DOMAIN_REGISTRY_REQUEST,
    SpentChallengeRegistryService,
)


CLIENT_ID = "clock-test-client"
CLIENT_KEY = b"clock-test-client-key-material-minimum-32-bytes"
STORAGE_KEY = b"clock-test-storage-key-material-minimum-32-bytes"
SERVER_ID = "clock-test-server"


class RegistryClockMonotonicityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-registry-clock-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = [1_800_000_000_000]
        self.server_key = Ed25519PrivateKey.generate()
        self.service = self.make_service()

    def make_service(self):
        return SpentChallengeRegistryService(
            self.root / "registry.sqlite",
            client_keys={CLIENT_ID: CLIENT_KEY},
            storage_key=STORAGE_KEY,
            server_key_id=SERVER_ID,
            server_private_key=self.server_key,
            max_clock_skew_ms=30_000,
            clock_ms=lambda: self.now[0],
        )

    def challenge(self, *, issued=None, expires=None, nonce=None):
        issued = self.now[0] if issued is None else issued
        expires = self.now[0] + 60_000 if expires is None else expires
        return {
            "nonce": nonce or ("n_" + uuid.uuid4().hex + "x"),
            "database_id": "test.registry.clock",
            "issued_at_ms": issued,
            "expires_at_ms": expires,
            "policy_sha256": "a" * 64,
        }

    def signed_request(self, path, body, *, rid=None, stamp=None):
        raw = canonical(body)
        rid = rid or uuid.uuid4().hex
        stamp = self.now[0] if stamp is None else stamp
        signed = {
            "method": "POST",
            "path": path,
            "timestamp_ms": stamp,
            "request_id": rid,
            "body_sha256": hashlib.sha256(raw).hexdigest(),
        }
        signature = hmac.new(
            CLIENT_KEY,
            DOMAIN_REGISTRY_REQUEST + canonical(signed),
            hashlib.sha256,
        ).hexdigest()
        headers = {
            "X-Lyc-Registry-Key-Id": CLIENT_ID,
            "X-Lyc-Registry-Request-Id": rid,
            "X-Lyc-Registry-Timestamp-Ms": str(stamp),
            "X-Lyc-Registry-Signature": signature,
        }
        return self.service.handle("POST", path, raw, headers), (path, raw, headers)

    def register(self, challenge=None):
        challenge = challenge or self.challenge()
        return self.signed_request("/v1/challenges", challenge)

    @staticmethod
    def error_code(response):
        status, envelope, dropped = response
        assert not dropped
        assert envelope is not None
        return status, envelope["body"].get("error"), envelope["body"]

    def test_clock_floor_persists_and_detects_wall_clock_rollback(self):
        challenge = self.challenge()
        response, _ = self.register(challenge)
        self.assertEqual(response[0], 201)
        self.now[0] -= 5_000
        consume = {
            key: challenge[key]
            for key in ("database_id", "policy_sha256", "issued_at_ms", "expires_at_ms")
        }
        response, _ = self.signed_request(
            f"/v1/challenges/{challenge['nonce']}/consume", consume
        )
        self.assertEqual(self.error_code(response)[:2], (503, "registry-clock-rollback"))
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            row = db.execute("SELECT state FROM challenges WHERE nonce=?", (challenge["nonce"],)).fetchone()
            self.assertEqual(row[0], "PENDING")
        restarted = self.make_service()
        self.service = restarted
        response, _ = self.register(self.challenge())
        self.assertEqual(self.error_code(response)[:2], (503, "registry-clock-rollback"))

    def test_clock_high_water_tampering_fails_closed(self):
        response, _ = self.register()
        self.assertEqual(response[0], 201)
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            db.execute("UPDATE clock_state SET high_water_ms=high_water_ms+1,prune_before_ms=prune_before_ms+1 WHERE singleton=1")
            db.commit()
        response, _ = self.register()
        self.assertEqual(self.error_code(response)[:2], (503, "registry-clock-state-integrity-invalid"))

    def test_clock_state_cannot_be_deleted_through_normal_sql(self):
        self.register()
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM clock_state WHERE singleton=1")
            db.rollback()

    def test_stale_request_ids_are_pruned_and_old_signed_request_rejected_by_time(self):
        first_challenge = self.challenge()
        first_response, first_signed = self.register(first_challenge)
        self.assertEqual(first_response[0], 201)
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM request_nonces").fetchone()[0], 1)

        self.now[0] += self.service.max_clock_skew_ms + 1_000
        second_challenge = self.challenge()
        second_response, _ = self.register(second_challenge)
        self.assertEqual(second_response[0], 201)
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM request_nonces").fetchone()[0], 1)

        path, raw, headers = first_signed
        replay_response = self.service.handle("POST", path, raw, headers)
        self.assertEqual(self.error_code(replay_response)[:2], (401, "client-auth-timestamp-invalid"))

    def test_same_request_id_within_window_is_rejected(self):
        response, signed = self.register()
        self.assertEqual(response[0], 201)
        path, raw, headers = signed
        replay = self.service.handle("POST", path, raw, headers)
        self.assertEqual(self.error_code(replay)[:2], (401, "client-request-replay"))

    def test_live_request_id_cannot_be_deleted_or_rewritten_from_sql(self):
        response, signed = self.register()
        self.assertEqual(response[0], 201)
        _, _, headers = signed
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "DELETE FROM request_nonces WHERE key_id=? AND request_id=?",
                    (headers["X-Lyc-Registry-Key-Id"], headers["X-Lyc-Registry-Request-Id"]),
                )
            db.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "UPDATE request_nonces SET timestamp_ms=timestamp_ms-100000 WHERE key_id=? AND request_id=?",
                    (headers["X-Lyc-Registry-Key-Id"], headers["X-Lyc-Registry-Request-Id"]),
                )
            db.rollback()

    def test_replay_window_configuration_cannot_silently_widen(self):
        response, _ = self.register()
        self.assertEqual(response[0], 201)
        widened = SpentChallengeRegistryService(
            self.root / "registry.sqlite",
            client_keys={CLIENT_ID: CLIENT_KEY},
            storage_key=STORAGE_KEY,
            server_key_id=SERVER_ID,
            server_private_key=self.server_key,
            max_clock_skew_ms=60_000,
            clock_ms=lambda: self.now[0],
        )
        self.service = widened
        response, _ = self.register()
        self.assertEqual(self.error_code(response)[:2], (503, "registry-clock-window-config-changed"))

    def test_registered_future_challenge_is_not_valid_before_issue_time(self):
        challenge = self.challenge(issued=self.now[0] + 5_000, expires=self.now[0] + 20_000)
        response, _ = self.register(challenge)
        self.assertEqual(response[0], 201)
        consume = {key: challenge[key] for key in ("database_id", "policy_sha256", "issued_at_ms", "expires_at_ms")}
        response, _ = self.signed_request(f"/v1/challenges/{challenge['nonce']}/consume", consume)
        self.assertEqual(self.error_code(response)[:2], (409, "challenge-not-yet-valid"))

    def test_expired_challenge_cannot_be_resurrected_by_clock_rollback(self):
        challenge = self.challenge(expires=self.now[0] + 60_000)
        response, _ = self.register(challenge)
        self.assertEqual(response[0], 201)
        # Advance the durable clock beyond the challenge expiry using a valid
        # request, then roll the injected wall clock back into the old validity
        # window. The persisted floor must reject the consume attempt.
        self.now[0] = challenge["expires_at_ms"] + 1
        response, _ = self.register(self.challenge(expires=self.now[0] + 60_000))
        self.assertEqual(response[0], 201)
        self.now[0] = challenge["issued_at_ms"] + 1_000
        consume = {key: challenge[key] for key in ("database_id", "policy_sha256", "issued_at_ms", "expires_at_ms")}
        response, _ = self.signed_request(f"/v1/challenges/{challenge['nonce']}/consume", consume)
        self.assertEqual(self.error_code(response)[:2], (503, "registry-clock-rollback"))

    def test_request_handler_uses_one_clock_sample_per_transaction(self):
        values = [self.now[0], self.now[0] - 100_000]
        calls = []
        def changing_clock():
            calls.append(values[0] if len(calls) == 0 else values[1])
            return calls[-1]
        self.service.clock_ms = changing_clock
        challenge = self.challenge()
        response, _ = self.register(challenge)
        self.assertEqual(response[0], 201)
        # The transaction must use the single validated timestamp for auth,
        # high-water advance, registration, and expiry decisions.
        self.assertEqual(len(calls), 1)

    def test_honest_monotonic_advancement_is_accepted(self):
        first, _ = self.register()
        self.assertEqual(first[0], 201)
        self.now[0] += 10_000
        second, _ = self.register()
        self.assertEqual(second[0], 201)
        with closing(sqlite3.connect(self.root / "registry.sqlite")) as db:
            floor = db.execute("SELECT high_water_ms FROM clock_state WHERE singleton=1").fetchone()[0]
            self.assertEqual(floor, self.now[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
