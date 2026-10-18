"""Authored adversarial regression probes; not independently designed or validated."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import copy
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest

from authenticated_provider import (
    GENESIS, LostResponse, SignedSQLiteProvider, TrustedIssuer,
    decode_wire, hash_obj, valid_action, verify_artifact, TOKEN_FIELDS, PROOF_FIELDS,
)

AUTH = b"authority synthetic lab key for tests!" + b"x" * 16
PROVIDER = b"provider synthetic lab key for tests!" + b"y" * 16


class SignedProviderContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "lab.sqlite"
        self.provider = SignedSQLiteProvider(self.path, authority_secret=AUTH, provider_secret=PROVIDER)
        self.issuer = TrustedIssuer(AUTH)
        self.action = {"actor": "research-agent", "subject": "fictional-order-17", "scope": "refund:create", "amount_cents": 1200}
        self.provider.seed(self.action)
        self.token = self.issue()

    def issue(self, action=None, effect="effect-1", approval="a1", *, expires=200, nonce="nonce-1"):
        action = action or self.action
        e, p = self.provider.snapshot(action["subject"])
        return self.issuer.issue(action=action, effect_id=effect, approval_id=approval,
                                 subject_version=e, policy_version=p, now=100,
                                 expires_at=expires, nonce=nonce)

    def commit(self, token=None, action=None, **kwargs):
        return self.provider.commit(action or self.action, token or self.token, now=120, **kwargs)

    def test_01_authenticated_commit(self):
        result = self.commit()
        self.assertTrue(result.committed)
        self.assertTrue(self.provider.verify_proof(result.receipt, token=self.token, action=self.action))
        self.assertEqual(self.provider.effect_count(), 1)

    def test_02_no_token(self):
        self.assertEqual(self.provider.commit(self.action, {}, now=120).code, "INVALID_TOKEN_AUTH")
        self.assertEqual(self.provider.effect_count(), 0)

    def test_03_bad_token_mac(self):
        t = copy.deepcopy(self.token)
        t["auth"]["mac"] = "a" * 64
        self.assertEqual(self.commit(token=t).code, "INVALID_TOKEN_AUTH")

    def test_04_modified_authorization_body(self):
        t = copy.deepcopy(self.token)
        t["body"]["expires_at"] = 999999
        self.assertEqual(self.commit(token=t).code, "INVALID_TOKEN_AUTH")

    def test_05_wrong_authority_key(self):
        attacker = TrustedIssuer(b"different key not authorized" + b"z" * 16)
        e, p = self.provider.snapshot(self.action["subject"])
        token = attacker.issue(action=self.action, effect_id="effect-1", approval_id="a1",
                               subject_version=e, policy_version=p, now=100, expires_at=200, nonce="x")
        self.assertEqual(self.commit(token=token).code, "INVALID_TOKEN_AUTH")

    def test_06_key_id_swap(self):
        t = copy.deepcopy(self.token)
        t["auth"]["key_id"] = "unrecognized-key"
        self.assertEqual(self.commit(token=t).code, "INVALID_TOKEN_AUTH")

    def test_07_new_field_in_token(self):
        t = copy.deepcopy(self.token)
        t["body"]["unexpected"] = "user privilege"
        self.assertEqual(self.commit(token=t).code, "INVALID_TOKEN_AUTH")

    def test_08_action_amount_swap(self):
        action = {**self.action, "amount_cents": 1300}
        self.assertEqual(self.commit(action=action).code, "ACTION_BINDING_MISMATCH")

    def test_09_action_subject_swap(self):
        action = {**self.action, "subject": "fictional-order-18"}
        self.assertEqual(self.commit(action=action).code, "ACTION_BINDING_MISMATCH")

    def test_10_action_scope_swap(self):
        action = {**self.action, "scope": "refund:unlimited"}
        self.assertEqual(self.commit(action=action).code, "ACTION_BINDING_MISMATCH")

    def test_11_invalid_amount_boolean(self):
        action = {**self.action, "amount_cents": True}
        self.assertFalse(valid_action(action))
        self.assertEqual(self.commit(action=action).code, "INVALID_ACTION")

    def test_12_extra_action_field(self):
        self.assertEqual(self.commit(action={**self.action, "hide_this": True}).code, "INVALID_ACTION")

    def test_13_token_not_yet_valid(self):
        self.assertEqual(self.provider.commit(self.action, self.token, now=99).code, "TOKEN_NOT_CURRENT")

    def test_14_token_expired(self):
        self.assertEqual(self.provider.commit(self.action, self.token, now=200).code, "TOKEN_NOT_CURRENT")

    def test_15_grant_expired(self):
        self.assertEqual(self.provider.commit(self.action, self.issue(expires=400), now=300).code, "GRANT_NOT_CURRENT")

    def test_16_revoke_precommit(self):
        self.provider.change(revoke_actor=self.action["actor"])
        self.assertEqual(self.commit().code, "REVOKED")

    def test_17_evidence_fails(self):
        self.provider.change(subject=self.action["subject"], status="FAIL")
        self.assertEqual(self.commit().code, "EVIDENCE_UNSATISFIED")

    def test_18_ineligible_status_pass(self):
        self.provider.change(subject=self.action["subject"], eligible=False)
        self.assertEqual(self.commit().code, "EVIDENCE_UNSATISFIED")

    def test_19_benign_revision_is_still_stale_in_exact_mode(self):
        self.provider.change(subject=self.action["subject"], eligible=True)
        self.assertEqual(self.commit().code, "EVIDENCE_REVISION_CHANGED")

    def test_20_policy_revision_is_stale(self):
        self.provider.change(max_cents=6000)
        self.assertEqual(self.commit().code, "POLICY_REVISION_CHANGED")

    def test_21_policy_cap(self):
        self.provider.change(max_cents=500)
        fresh = self.issue(nonce="fresh")
        self.assertEqual(self.commit(token=fresh).code, "POLICY_LIMIT")

    def test_22_false_evidence_negative_control(self):
        self.provider.change(subject=self.action["subject"], truth=False)
        fresh = self.issue(nonce="still-wrong")
        out = self.commit(token=fresh)
        self.assertTrue(out.committed)
        self.assertFalse(self.provider.recorded_truth(self.action["subject"]))
        self.assertTrue(self.provider.verify_proof(out.receipt, token=fresh, action=self.action))

    def test_23_idempotent_same_token(self):
        first = self.commit()
        second = self.commit()
        self.assertTrue(first.committed)
        self.assertEqual(second.code, "IDEMPOTENT_REPLAY")
        self.assertEqual(first.receipt, second.receipt)
        self.assertEqual(self.provider.effect_count(), 1)

    def test_24_idempotent_after_revoke_and_expiry(self):
        first = self.commit()
        self.provider.change(revoke_actor=self.action["actor"])
        later = self.provider.commit(self.action, self.token, now=999)
        self.assertEqual(later.code, "IDEMPOTENT_REPLAY")
        self.assertEqual(first.receipt, later.receipt)

    def test_25_same_effect_different_signed_intent_rejected(self):
        self.commit()
        changed = self.issue(nonce="different-token")
        self.assertEqual(self.commit(token=changed).code, "EFFECT_ID_CONFLICT")

    def test_26_same_grant_different_effect_id_rejected(self):
        self.commit()
        changed = self.issue(effect="effect-2", nonce="next")
        self.assertEqual(self.commit(token=changed).code, "APPROVAL_CONSUMED")

    def test_27_response_lost_after_commit_and_authoritative_reconciliation(self):
        with self.assertRaises(LostResponse):
            self.commit(lose_response=True)
        read = self.provider.lookup("effect-1")
        self.assertTrue(self.provider.verify_proof(read, token=self.token, action=self.action))
        self.assertEqual(self.provider.effect_count(), 1)
        self.assertEqual(self.commit().code, "IDEMPOTENT_REPLAY")

    def test_28_receipt_tampering_rejected(self):
        receipt = self.commit().receipt
        modified = copy.deepcopy(receipt)
        modified["body"]["amount_cents"] += 100
        self.assertFalse(self.provider.verify_proof(modified, token=self.token, action=self.action))

    def test_29_receipt_rejects_wrong_key(self):
        receipt = self.commit().receipt
        other = SignedSQLiteProvider(self.path, authority_secret=AUTH, provider_secret=b"other-provider-key" + b"x"*30)
        self.assertFalse(other.verify_proof(receipt))

    def test_30_receipt_rejects_wrong_action(self):
        receipt = self.commit().receipt
        self.assertFalse(self.provider.verify_proof(receipt, action={**self.action, "amount_cents": 1300}))

    def test_31_receipt_rejects_wrong_token(self):
        receipt = self.commit().receipt
        self.assertFalse(self.provider.verify_proof(receipt, token=self.issue(nonce="other")))

    def test_32_token_mac_cannot_be_reused_as_provider_proof(self):
        self.assertFalse(verify_artifact(self.token, PROVIDER, "earned-trust.provider-proof.v1", "provider-lab-v1", PROOF_FIELDS))

    def test_33_audit_chain_verified(self):
        self.commit()
        state = self.provider.verify_audit()
        self.assertTrue(state["valid"])
        self.assertEqual(state["event_count"], 1)

    def test_34_audit_mutation_detected(self):
        self.commit()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE audit SET entry='{}' WHERE seq=1")
        self.assertEqual(self.provider.verify_audit()["reason"], "chain_mutation")

    def test_35_truncation_detected_with_external_anchor(self):
        self.commit()
        anchor = self.provider.verify_audit()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DELETE FROM audit WHERE seq=1")
        self.assertEqual(self.provider.verify_audit(anchor)["reason"], "trusted_anchor_mismatch")

    def test_36_empty_ledger_has_genesis(self):
        state = self.provider.verify_audit()
        self.assertEqual((state["event_count"], state["root_hash"]), (0, GENESIS))

    def test_37_duplicate_wire_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            decode_wire('{"body":1,"body":2}')

    def test_38_nonfinite_wire_rejected(self):
        with self.assertRaises(ValueError):
            decode_wire('{"x": NaN}')

    def test_39_concurrent_32_thread_submission_one_effect(self):
        with ThreadPoolExecutor(max_workers=16) as pool:
            observations = list(pool.map(lambda _: self.commit().code, range(32)))
        self.assertEqual(observations.count("COMMITTED"), 1)
        self.assertEqual(observations.count("IDEMPOTENT_REPLAY"), 31)
        self.assertEqual(self.provider.effect_count(), 1)
        self.assertEqual(self.provider.verify_audit()["event_count"], 1)

    def test_40_wrong_approval_even_if_signed(self):
        self.assertEqual(self.commit(token=self.issue(approval="bogus")).code, "GRANT_MISMATCH")

    def test_41_replay_old_proof_for_different_action_does_not_validate(self):
        first = self.commit().receipt
        self.assertFalse(self.provider.verify_proof(first, action={**self.action, "subject":"different"}))

    def test_42_claims_proof_is_local_not_external(self):
        proof = self.commit().receipt
        self.assertEqual(proof["body"]["schema"], "earned-trust.local-commit.v1")
        self.assertNotIn("bank_transaction_id", proof["body"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

# Tests below are loaded by unittest discovery before the module is executed directly.
class LedgerHardening(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "provider.sqlite"
        self.provider = SignedSQLiteProvider(self.path, authority_secret=AUTH, provider_secret=PROVIDER)
        self.action = {"actor":"agent", "subject":"ORDER-20", "amount_cents":200, "scope":"refund:create"}
        self.provider.seed(self.action)
        self.issuer = TrustedIssuer(AUTH)

    def issue(self, effect, approval, nonce):
        ev, pol = self.provider.snapshot(self.action["subject"])
        return self.issuer.issue(action=self.action, effect_id=effect, approval_id=approval,
                                 subject_version=ev, policy_version=pol, now=100, expires_at=300, nonce=nonce)

    def test_a_signed_receipt_links_to_real_local_effect_and_audit(self):
        t = self.issue("e1", "a1", "one")
        self.provider.commit(self.action, t, now=120)
        self.assertTrue(self.provider.verify_stored_effect("e1", token=t))

    def test_b_stored_action_tamper_detected(self):
        t = self.issue("e1", "a1", "one")
        self.provider.commit(self.action, t, now=120)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE effects SET action_json='{}' WHERE effect_id='e1'")
        self.assertFalse(self.provider.verify_stored_effect("e1", token=t))

    def test_c_stored_audit_tamper_detected(self):
        t = self.issue("e1", "a1", "one")
        self.provider.commit(self.action, t, now=120)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE audit SET entry_hash='forgery' WHERE seq=1")
        self.assertFalse(self.provider.verify_stored_effect("e1", token=t))

    def test_d_historic_anchor_does_not_reject_legitimate_append(self):
        t = self.issue("e1", "a1", "one")
        self.provider.commit(self.action, t, now=120)
        anchor = self.provider.verify_audit()
        other = {**self.action, "subject":"ORDER-21"}
        self.provider.seed(other, approval_id="a2")
        ev, pol = self.provider.snapshot(other["subject"])
        t2 = self.issuer.issue(action=other,effect_id="e2",approval_id="a2",
                 subject_version=ev,policy_version=pol,now=100,expires_at=300,nonce="two")
        self.provider.commit(other, t2, now=121)
        self.assertTrue(self.provider.verify_audit(anchor)["valid"])
        self.assertEqual(self.provider.verify_audit()["event_count"], 2)

    def test_e_historic_anchor_detects_recomputed_chain_alteration(self):
        t = self.issue("e1", "a1", "one")
        self.provider.commit(self.action, t, now=120)
        anchor = self.provider.verify_audit()
        other = {**self.action,"subject":"ORDER-21"}
        self.provider.seed(other,approval_id="a2")
        ev, pol = self.provider.snapshot(other["subject"])
        t2 = self.issuer.issue(action=other,effect_id="e2",approval_id="a2",
                 subject_version=ev,policy_version=pol,now=100,expires_at=300,nonce="two")
        self.provider.commit(other, t2, now=121)
        # Database attacker changes first row and correctly recomputes the
        # *unkeyed* hash chain, but cannot rewrite our independently saved anchor.
        with closing(sqlite3.connect(self.path)) as db, db:
            row1 = db.execute("SELECT entry FROM audit WHERE seq=1").fetchone()
            entry1 = decode_wire(row1[0]); entry1["event"] = "FAKE_EVENT"
            h1 = hash_obj({"seq":1,"prev_hash":GENESIS,"entry":entry1})
            db.execute("UPDATE audit SET entry=?,entry_hash=? WHERE seq=1",
                       (json.dumps(entry1,sort_keys=True,separators=(',',':')),h1))
            row2 = db.execute("SELECT entry FROM audit WHERE seq=2").fetchone()
            entry2=decode_wire(row2[0])
            h2=hash_obj({"seq":2,"prev_hash":h1,"entry":entry2})
            db.execute("UPDATE audit SET prev_hash=?,entry_hash=? WHERE seq=2", (h1,h2))
        self.assertTrue(self.provider.verify_audit()["valid"])  # Without anchor, forgery looks consistent.
        self.assertEqual(self.provider.verify_audit(anchor)["reason"], "trusted_anchor_mismatch")

class FailClosedLedgerMutations(unittest.TestCase):
    """Separate cases: new effects refuse a visibly corrupted ledger."""
    setUp = LedgerHardening.setUp
    issue = LedgerHardening.issue
    def _second_intent(self):
        action={"actor":"agent", "subject":"ORDER-21", "amount_cents":150, "scope":"refund:create"}
        self.provider.seed(action,approval_id="a2")
        ev, pol=self.provider.snapshot(action["subject"])
        token=self.issuer.issue(action=action,effect_id="e2",approval_id="a2",
            subject_version=ev,policy_version=pol,now=100,expires_at=300,nonce="other")
        return action,token

    def test_f_tampered_receipt_pauses_all_new_effects(self):
        t=self.issue("e1","a1","one")
        self.provider.commit(self.action,t,now=120)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE effects SET receipt_json='{}' WHERE effect_id='e1'")
        action,token=self._second_intent()
        self.assertEqual(self.provider.commit(action,token,now=121).code,"LEDGER_INTEGRITY_FAILED")
        self.assertEqual(self.provider.effect_count(),1)

    def test_g_tampered_audit_pauses_all_new_effects(self):
        t=self.issue("e1","a1","one")
        self.provider.commit(self.action,t,now=120)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE audit SET entry_hash='broken' WHERE seq=1")
        action,token=self._second_intent()
        self.assertEqual(self.provider.commit(action,token,now=121).code,"LEDGER_INTEGRITY_FAILED")
        self.assertEqual(self.provider.effect_count(),1)

    def test_h_second_clean_effect_is_allowed(self):
        t=self.issue("e1","a1","one")
        self.provider.commit(self.action,t,now=120)
        action,token=self._second_intent()
        out=self.provider.commit(action,token,now=121)
        self.assertTrue(out.committed,out.code)
        self.assertEqual(self.provider.effect_count(),2)
        self.assertTrue(self.provider.verify_audit()["valid"])
