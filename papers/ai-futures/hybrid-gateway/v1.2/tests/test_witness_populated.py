"""Cycle 12 release gate: external anchors against populated, real decision journals."""
from dataclasses import replace
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from hybrid_gateway.external_witness import issue_witness, verify_witness
from hybrid_gateway.review_desk import ReviewDesk
from hybrid_gateway.authorization import ReviewKeyring
from hybrid_gateway.durable import SQLiteLedger
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW

KEY=b'cycle-twelve-release-fixture-key-do-not-use'
WITNESS_KEY=b'cycle-twelve-external-independent-test-key'
PASS='review-test-password-long-enough'

class PopulatedWitnessTest(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'journal.db'
        self.db=SQLiteLedger(self.path,require_review_journal=True)
        self.registry,self.plan,self.batch=prepare(self.db)
        self.keys=ReviewKeyring({'reviewer':KEY})
    def reject(self):
        desk=ReviewDesk(ledger=self.db,registry=self.registry,plan=self.plan,
                        batch=self.batch,recorded_at=KNOW,key_id='reviewer',
                        signing_secret=KEY,password=PASS)
        token,csrf=desk.login(PASS)
        desk.start_review(token)
        outcome=desk.submit(token,csrf=csrf,presented_digest=desk.view_digest,decision='reject')
        self.assertEqual(outcome.disposition,'REJECTED')
    def issue(self):
        with self.db._connect() as conn:
            return issue_witness(conn,ledger_id=self.db.ledger_id,journal_keys=self.keys,
                                 witness_secret=WITNESS_KEY)
    def verify(self,w):
        with self.db._connect() as conn:
            return verify_witness(conn,witness=w,ledger_id=self.db.ledger_id,
                                  journal_keys=self.keys,witness_secret=WITNESS_KEY)
    def test_signed_populated_rejection_survives_restart(self):
        self.reject()
        w=self.issue()
        self.assertEqual(w.count,1)
        self.assertTrue(self.verify(w))
        reopened=SQLiteLedger(self.path)
        with reopened._connect() as conn:
            self.assertTrue(verify_witness(conn,witness=w,ledger_id=reopened.ledger_id,
                                          journal_keys=self.keys,witness_secret=WITNESS_KEY))
    def test_journal_tail_truncation_detected(self):
        self.reject(); w=self.issue()
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM review_decisions')
        self.assertFalse(self.verify(w))
    def test_journal_record_mutation_detected(self):
        self.reject(); w=self.issue()
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE review_decisions SET entry_hash=?",('sha256:'+'e'*64,))
        self.assertFalse(self.verify(w))
    def test_witness_head_substitution_detected(self):
        self.reject(); w=self.issue()
        self.assertFalse(self.verify(replace(w,head='sha256:'+'e'*64)))
    def test_invalid_journal_cannot_be_witnessed(self):
        self.reject()
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE review_decisions SET entry_hash=?",('sha256:'+'e'*64,))
        with self.assertRaises(ValueError): self.issue()
if __name__=='__main__': unittest.main()
