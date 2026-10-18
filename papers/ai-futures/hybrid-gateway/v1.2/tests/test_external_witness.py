import sqlite3
import unittest
from hybrid_gateway.authorization import ReviewKeyring
from hybrid_gateway.external_witness import issue_witness, verify_witness

class ExternalWitnessTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(":memory:")
        self.conn.row_factory=sqlite3.Row
        self.conn.execute("CREATE TABLE review_decisions(seq INTEGER PRIMARY KEY, batch_digest TEXT, entry_hash TEXT, payload TEXT)")
        self.conn.execute("CREATE TABLE events(payload TEXT)")
        self.ledger="a"*48
        self.keys=ReviewKeyring({"reviewer":b"r"*32})
        self.secret=b"w"*32
    def tearDown(self): self.conn.close()
    def issue(self):
        return issue_witness(self.conn,ledger_id=self.ledger,journal_keys=self.keys,witness_secret=self.secret)
    def verify(self,w,**kw):
        return verify_witness(self.conn,witness=w,ledger_id=self.ledger,journal_keys=self.keys,witness_secret=kw.get("secret",self.secret))
    def test_empty_checkpoint(self):
        self.assertTrue(self.verify(self.issue()))
    def test_wrong_key(self):
        self.assertFalse(self.verify(self.issue(),secret=b"x"*32))
    def test_wrong_ledger(self):
        from dataclasses import replace
        self.assertFalse(self.verify(replace(self.issue(),ledger_id="b"*48)))
    def test_forged_count(self):
        from dataclasses import replace
        self.assertFalse(self.verify(replace(self.issue(),count=1)))
    def test_short_key_refused(self):
        with self.assertRaises(ValueError): issue_witness(self.conn,ledger_id=self.ledger,journal_keys=self.keys,witness_secret=b"short")
