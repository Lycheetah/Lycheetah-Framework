"""Test fixtures are author-written: no independent audit or real payment calls."""
import copy
import tempfile
import unittest
from pathlib import Path

from independent_witness import IndependentObserver, OutcomeVerifier
from authenticated_provider import SignedSQLiteProvider, TrustedIssuer, hash_obj

AUTH = b"test authority key" + b"a"*32
PROVIDER = b"test provider key" + b"p"*32
OBSERVER = b"test observer key" + b"o"*32

class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        self.p = SignedSQLiteProvider(home / "provider.db", authority_secret=AUTH, provider_secret=PROVIDER)
        self.o = IndependentObserver(home / "observer.db", secret=OBSERVER)
        self.v = OutcomeVerifier(self.p, self.o)
        self.action = {"actor":"agent", "subject":"fictional-order-88", "amount_cents":1200, "scope":"refund:create"}
        self.p.seed(self.action)
        v1, p1 = self.p.snapshot(self.action["subject"])
        self.token = TrustedIssuer(AUTH).issue(action=self.action, effect_id="e1", approval_id="a1",
                                               subject_version=v1, policy_version=p1,
                                               now=100, expires_at=200, nonce="n1")
    def commit(self):
        outcome = self.p.commit(self.action,self.token,now=110)
        self.assertEqual(outcome.code,"COMMITTED")
        return outcome
    def obs(self, status="COMMITTED", correctness="TRUE", **kwargs):
        return self.o.observe(effect_id="e1", token_sha256=hash_obj(self.token),
                              action_sha256=hash_obj(self.action), status=status,
                              correctness=correctness, observed_at=kwargs.get("at",120))
    def check(self, witness=None):
        return self.v.reconcile(effect_id="e1",token=self.token,action=self.action,supplied_witness=witness)
    def test_signed_receipt_baseline_true(self):
        r=self.commit()
        self.assertTrue(self.p.verify_proof(r.receipt, token=self.token,action=self.action))
    def test_true_independent_observation_confirms(self):
        self.commit(); self.obs()
        self.assertEqual(self.check().result,"CONFIRMED")
    def test_missing_observer_pauses(self):
        self.commit(); self.assertEqual(self.check().result,"REVIEW")
    def test_missing_provider_record_unknown(self):
        self.obs(); self.assertEqual(self.check().result,"UNKNOWN")
    def test_false_evidence_signed_provider_caught_by_external_fixture(self):
        self.p.change(subject=self.action["subject"], truth=False)
        fresh_version, pol = self.p.snapshot(self.action["subject"])
        self.token=TrustedIssuer(AUTH).issue(action=self.action,effect_id="e1",approval_id="a1",
                                            subject_version=fresh_version,policy_version=pol,
                                            now=100,expires_at=200,nonce="new")
        provider=self.commit()
        self.assertTrue(self.p.verify_proof(provider.receipt,token=self.token,action=self.action))
        self.obs(correctness="FALSE")
        self.assertEqual(self.check().result,"CONFLICT")
    def test_unknown_truth_pauses(self):
        self.commit();self.obs(correctness="UNKNOWN")
        self.assertEqual(self.check().result,"REVIEW")
    def test_observer_denies_write(self):
        self.commit();self.obs(status="NOT_COMMITTED")
        self.assertEqual(self.check().result,"CONFLICT")
    def test_observer_unknown_write(self):
        self.commit();self.obs(status="UNKNOWN")
        self.assertEqual(self.check().result,"REVIEW")
    def test_different_effect_id_rejected(self):
        self.commit();w=self.obs();w=copy.deepcopy(w)
        w["body"]["effect_id"]="e2"
        self.assertEqual(self.check(w).result,"REVIEW")
    def test_bad_mac_rejected(self):
        self.commit();w=copy.deepcopy(self.obs())
        w["auth"]["mac"]="0"*64
        self.assertEqual(self.check(w).result,"REVIEW")
    def test_cross_source_action_disagreement(self):
        self.commit()
        self.o.observe(effect_id="e1",token_sha256=hash_obj(self.token),action_sha256="b"*64,
                       status="COMMITTED",correctness="TRUE",observed_at=120)
        self.assertEqual(self.check().result,"CONFLICT")
    def test_cross_source_token_disagreement(self):
        self.commit()
        self.o.observe(effect_id="e1",token_sha256="f"*64,action_sha256=hash_obj(self.action),
                       status="COMMITTED",correctness="TRUE",observed_at=120)
        self.assertEqual(self.check().result,"CONFLICT")
    def test_older_signed_observation_replay_rejected(self):
        self.commit();old=self.obs()
        self.o.observe(effect_id="e1",token_sha256=hash_obj(self.token),action_sha256=hash_obj(self.action),
                       status="COMMITTED",correctness="FALSE",observed_at=140)
        self.assertEqual(self.check(old).reason,"observer-evidence-not-current")
        self.assertEqual(self.check().result,"CONFLICT")
    def test_observer_reopen_keeps_current(self):
        self.commit();w=self.obs()
        reopened=IndependentObserver(self.o.db_path,secret=OBSERVER)
        self.assertEqual(reopened.current("e1"),w)
    def test_observer_earlier_clock_denied(self):
        self.commit();self.obs()
        with self.assertRaises(ValueError):self.obs(at=119)
    def test_observer_same_clock_denied(self):
        self.commit();self.obs()
        with self.assertRaises(ValueError):self.obs(at=120)
    def test_cannot_use_same_signing_key_as_provider(self):
        with self.assertRaises(ValueError):
            OutcomeVerifier(self.p,IndependentObserver(Path(self.tmp.name)/"bad.db",secret=PROVIDER))
    def test_cannot_use_same_signing_key_as_authority(self):
        with self.assertRaises(ValueError):
            OutcomeVerifier(self.p,IndependentObserver(Path(self.tmp.name)/"bad.db",secret=AUTH))
    def test_provider_proof_tamper_refuses(self):
        self.commit();self.obs()
        import sqlite3
        with sqlite3.connect(self.p.path) as db:
            db.execute("UPDATE effects SET receipt_json='{}' WHERE effect_id='e1'")
        self.assertEqual(self.check().result,"REVIEW")
    def test_provider_action_tamper_refuses(self):
        self.commit();self.obs()
        import sqlite3
        with sqlite3.connect(self.p.path) as db:
            db.execute("UPDATE effects SET action_json='{}' WHERE effect_id='e1'")
        self.assertEqual(self.check().result,"REVIEW")
    def test_proof_mismatch_token_refuses(self):
        self.commit();self.obs()
        token=copy.deepcopy(self.token)
        token["auth"]["mac"]="f"*64
        self.assertEqual(self.v.reconcile(effect_id="e1",token=token,action=self.action).result,"REVIEW")
    def test_duplicate_observed_effect_different_action_conflicts(self):
        self.commit();self.obs()
        changed={**self.action,"amount_cents":999}
        self.assertEqual(self.v.reconcile(effect_id="e1",token=self.token,action=changed).result,"REVIEW")
    def test_separate_sqlite_files(self):
        self.assertNotEqual(self.p.path,self.o.db_path)
    def test_malformed_provider_json_routes_to_review(self):
        self.commit(); self.obs()
        import sqlite3
        with sqlite3.connect(self.p.path) as db:
            db.execute("UPDATE effects SET receipt_json='{' WHERE effect_id='e1'")
        self.assertEqual(self.check().result, "REVIEW")

    def test_invalid_observer_schema_in_database_routes_to_review(self):
        self.commit(); self.obs()
        import sqlite3
        with sqlite3.connect(self.o.db_path) as db:
            db.execute("UPDATE observations SET revision='garbled' WHERE effect_id='e1'")
        self.assertEqual(self.check().result, "REVIEW")

    def test_missing_observer_database_after_proof_routes_to_review(self):
        self.commit(); self.obs()
        import sqlite3
        with sqlite3.connect(self.o.db_path) as db:
            db.execute("DROP TABLE observations")
        self.assertEqual(self.check().result, "REVIEW")

    def test_removed_provider_audit_row_routes_to_review(self):
        self.commit(); self.obs()
        import sqlite3
        with sqlite3.connect(self.p.path) as db:
            db.execute("DELETE FROM audit")
        self.assertEqual(self.check().result, "REVIEW")

    def test_correlated_false_oracle_defeats_reconciliation(self):
        # Negative control: signer authentication is NOT source truth.
        self.p.change(subject=self.action["subject"], truth=False)
        v, pol = self.p.snapshot(self.action["subject"])
        self.token=TrustedIssuer(AUTH).issue(action=self.action,effect_id="e1",approval_id="a1",
                                            subject_version=v,policy_version=pol,now=100,expires_at=200,nonce="new")
        self.commit()
        self.obs(correctness="TRUE")  # observer is wrong or colluding
        self.assertFalse(self.p.recorded_truth(self.action["subject"]))
        self.assertEqual(self.check().result,"CONFIRMED")

    def test_schema_unknowns_not_trusted(self):
        self.commit();w=self.obs();w=copy.deepcopy(w)
        w["body"]["blessing"]="valid"
        self.assertFalse(self.o.verify(w))
    def test_observer_fake_source_rejected(self):
        self.commit();w=copy.deepcopy(self.obs())
        w["body"]["source_id"]="local-provider"
        self.assertEqual(self.check(w).result,"REVIEW")

if __name__ == "__main__": unittest.main()
