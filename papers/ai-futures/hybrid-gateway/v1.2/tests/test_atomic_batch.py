"""v0.6 atomic multi-claim revision: deterministic unit tests, fictional policies."""
from dataclasses import replace
import json
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from hybrid_gateway import (HybridGateway, SQLiteLedger, AuditedBatch, CoverageAuditor,
    ScriptedNeuralAdapter, ExtractionPlan, TrustedContractRegistry)
from tests.test_contracts import (SRC, AT, KNOW, clause, candidate)
from tests.test_coverage import loyalty_clause, loyalty_candidate


def prepare(db, claims=None, contracts=None):
    contracts = contracts or [clause(), loyalty_clause()]
    registry = TrustedContractRegistry([SRC], contracts)
    db.register_source(SRC)
    g = db.snapshot(registry=registry)
    plan = ExtractionPlan.create(registry, SRC.source_id)
    model = ScriptedNeuralAdapter('fixture-only', {SRC.source_id: claims if claims is not None
                                   else [candidate(), loyalty_candidate()]})
    auditor = CoverageAuditor(g, model, registry, plan)
    return registry, plan, auditor.audit(SRC)


class AtomicInMemoryTests(unittest.TestCase):
    def setUp(self):
        self.g = HybridGateway()
        self.g.register_source(SRC)

    def test_batch_is_one_event_and_replayable(self):
        d = self.g.ingest_batch((loyalty_candidate(), candidate()), recorded_at=KNOW,
                                reviewer_approved=True)
        self.assertEqual(d.disposition, 'ALLOW')
        self.assertEqual(len(self.g.events), 1)
        self.assertEqual(self.g.events[0]['kind'], 'BATCH_ADMIT')
        self.assertEqual(len(self.g.claims), 2)
        restored = HybridGateway.restore(sources=[SRC], event_jsonl=self.g.export_events(),
                                         pinned_head=d.event_hash)
        self.assertEqual(restored.head_digest, d.event_hash)
        self.assertEqual(restored.claims, self.g.claims)
        refund = restored.query(tenant=SRC.tenant, subject='refunds', predicate='window_days',
                                scope='store', effective_at=KNOW, known_at=KNOW)
        self.assertEqual(refund.value, '14')
        old = restored.query(tenant=SRC.tenant, subject='refunds', predicate='window_days',
                              scope='store', effective_at=KNOW, known_at=AT)
        self.assertEqual(old.disposition, 'ABSTAIN_NO_EVIDENCE')

    def test_last_bad_claim_does_not_admit_earlier_claim(self):
        c = loyalty_candidate()
        invalid = replace(c, claim_id='bad', supersedes=('nonexistent',))
        d = self.g.ingest_batch([candidate(), invalid], recorded_at=KNOW,
                                reviewer_approved=True)
        self.assertEqual(d.disposition, 'BLOCK')
        self.assertEqual(self.g.events, [])
        self.assertEqual(self.g.claims, {})

    def test_bad_source_or_semantics_rollback_all(self):
        for wrong in [replace(loyalty_candidate(), tenant='B'),
                      replace(loyalty_candidate(), evidence_quote='not in source'),
                      replace(loyalty_candidate(), value='39')]:
            with self.subTest(wrong=wrong):
                d = self.g.ingest_batch([candidate(), wrong], recorded_at=KNOW,
                                        reviewer_approved=True)
                self.assertNotEqual(d.disposition, 'ALLOW')
                self.assertFalse(self.g.events)
                self.assertFalse(self.g.claims)

    def test_duplicate_empty_unapproved_and_cyclic_batches(self):
        c = candidate()
        self.assertEqual(self.g.ingest_batch([c, c], recorded_at=KNOW,
                         reviewer_approved=True).disposition, 'BLOCK')
        self.assertEqual(self.g.ingest_batch([], recorded_at=KNOW,
                         reviewer_approved=True).disposition, 'BLOCK')
        self.assertEqual(self.g.ingest_batch([c], recorded_at=KNOW,
                         reviewer_approved=False).disposition, 'REVIEW')
        a = replace(candidate(), claim_id='a', supersedes=('b',))
        b = replace(candidate(), claim_id='b', supersedes=('a',))
        self.assertEqual(self.g.ingest_batch([a,b], recorded_at=KNOW,
                         reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(self.g.events)

    def test_topological_supersession_unordered_and_replay(self):
        old = replace(candidate(), claim_id='earlier')
        next_ = replace(candidate(), claim_id='later', valid_from='2026-10-02T00:00:00Z',
                        supersedes=('earlier',))
        d = self.g.ingest_batch((next_,old), recorded_at=KNOW, reviewer_approved=True)
        self.assertEqual(d.disposition,'ALLOW')
        self.assertEqual([x['claim_id'] for x in self.g.events[0]['payload']['claims']], ['earlier','later'])
        restored=HybridGateway.restore(sources=[SRC],event_jsonl=self.g.export_events(),pinned_head=d.event_hash)
        self.assertEqual(restored.head_digest, self.g.head_digest)


class DurableAtomicTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'ledger.sqlite3'
        self.db = SQLiteLedger(self.path)

    def test_successful_atomic_commit_and_restart(self):
        registry, plan, batch = prepare(self.db)
        self.assertEqual(batch.receipt.disposition,'READY_FOR_REVIEW')
        self.assertEqual(self.db.commit_batch(batch, registry=registry, plan=plan,
                         recorded_at=KNOW).disposition,'REVIEW')
        self.assertEqual(self.db.snapshot().events, [])
        d = self.db.commit_batch(batch,registry=registry,plan=plan,recorded_at=KNOW,
                                 reviewer_approved=True)
        self.assertEqual(d.disposition,'ALLOW')
        fresh = SQLiteLedger(self.path).snapshot(registry=registry,anchored_head=d.event_hash)
        self.assertEqual(len(fresh.events), 1)
        self.assertEqual(len(fresh.claims), 2)
        self.assertTrue(fresh.verify_chain(anchored_head=d.event_hash))
        self.assertEqual(fresh.events[0]['kind'],'BATCH_ADMIT')

    def test_failing_second_claim_rolls_back_entire_transaction(self):
        # Both clauses are legitimately in plan, but the operator intentionally
        # allows a supersession to an unknown target. Coverage passes; commit fails.
        loy = replace(loyalty_clause(), permitted_supersedes=('missing-old-id',))
        wrong = replace(loyalty_candidate(), supersedes=('missing-old-id',))
        r,p,b = prepare(self.db, [candidate(), wrong], [clause(), loy])
        self.assertEqual(b.receipt.disposition,'READY_FOR_REVIEW')
        d = self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW, reviewer_approved=True)
        self.assertEqual(d.disposition,'BLOCK')
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_sql_insert_failure_rollback(self):
        r,p,b = prepare(self.db)
        with sqlite3.connect(self.path) as conn:
            conn.execute("""CREATE TRIGGER fail_insert BEFORE INSERT ON events
                            BEGIN SELECT RAISE(ABORT, 'synthetic disk failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,reviewer_approved=True)
        self.assertFalse(self.db.snapshot().claims)
        with sqlite3.connect(self.path) as conn:
            conn.execute('DROP TRIGGER fail_insert')
        self.assertEqual(self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,
                                              reviewer_approved=True).disposition,'ALLOW')

    def test_stale_head_and_replay_attempt_rejected(self):
        r,p,b = prepare(self.db)
        self.assertEqual(self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,
                         reviewer_approved=True).disposition,'ALLOW')
        self.assertEqual(self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,
                         reviewer_approved=True).disposition,'REVIEW')
        self.assertEqual(len(self.db.snapshot().events),1)

    def test_mutated_stage_and_forged_counts_rejected(self):
        r,p,b = prepare(self.db)
        variants = [
          AuditedBatch(replace(b.receipt, expected=1), b.stages),
          AuditedBatch(replace(b.receipt, stage_candidate_digests=()), b.stages),
          AuditedBatch(b.receipt, b.stages[:1]),
          AuditedBatch(b.receipt, (replace(b.stages[0],
                       staged=replace(b.stages[0].staged,
                         candidate=replace(b.stages[0].staged.candidate,claim_id='changed'))), b.stages[1])),
        ]
        for alt in variants:
            with self.subTest(variant=alt):
                self.assertEqual(self.db.commit_batch(alt,registry=r,plan=p,
                    recorded_at=KNOW,reviewer_approved=True).disposition,'BLOCK')
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_anchor_mismatch_fails_closed(self):
        r,p,b = prepare(self.db)
        with self.assertRaises(ValueError):
            self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,
                 independently_anchored_head='sha256:bogus', reviewer_approved=True)
        self.assertEqual(self.db.snapshot().events, [])

    def test_two_reviewers_with_same_snapshot_only_one_commits(self):
        r,p,b = prepare(self.db)
        def attempt(_):
            return SQLiteLedger(self.path).commit_batch(b,registry=r,plan=p,
                      recorded_at=KNOW,reviewer_approved=True).disposition
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(attempt, range(2)))
        self.assertCountEqual(results, ['ALLOW','REVIEW'])
        self.assertEqual(len(self.db.snapshot().events),1)

    def test_disconnected_external_anchor_mismatch_after_commit(self):
        r,p,b = prepare(self.db)
        d=self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,reviewer_approved=True)
        self.assertEqual(d.disposition,'ALLOW')
        with self.assertRaises(ValueError):
            self.db.snapshot(anchored_head='sha256:wrong')
        self.assertEqual(self.db.snapshot(anchored_head=d.event_hash).head_digest,d.event_hash)

    def test_uncommitted_other_process_is_rolled_back(self):
        # Illustrates SQLite rollback on abrupt process termination, not a
        # physical power-loss simulation or a security hardening test.
        self.db.register_source(SRC)
        script = "import sqlite3,os,sys; c=sqlite3.connect(sys.argv[1]); c.execute('BEGIN IMMEDIATE'); c.execute('INSERT INTO events(seq,payload) VALUES (?,?)',(1,'garbage')); os._exit(17)"
        result = subprocess.run([sys.executable, '-c', script, str(self.path)],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertEqual(self.db.snapshot().events,[])

    def test_corrupt_event_fails_replay(self):
        r,p,b = prepare(self.db)
        d=self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,reviewer_approved=True)
        self.assertEqual(d.disposition,'ALLOW')
        with sqlite3.connect(self.path) as conn:
            row = conn.execute('SELECT payload FROM events').fetchone()[0]
            event=json.loads(row)
            event['payload']['claims'][0]['claim']['value']='900'
            conn.execute('UPDATE events SET payload=? WHERE seq=1', (json.dumps(event),))
        with self.assertRaises(ValueError):
            self.db.snapshot()

    def test_changed_source_rejected_and_source_registry_persists(self):
        self.db.register_source(SRC)
        self.db.register_source(SRC)
        with self.assertRaises(ValueError):
            self.db.register_source(replace(SRC,body='another source'))
        self.assertEqual(len(self.db.snapshot().sources), 1)

    def test_empty_plan_never_commits_a_zero_event(self):
        registry = TrustedContractRegistry([SRC],[clause()])
        self.db.register_source(SRC)
        plan = ExtractionPlan.create(registry,SRC.source_id,selected=())
        model=ScriptedNeuralAdapter('fixture-only',{SRC.source_id:[]})
        b=CoverageAuditor(self.db.snapshot(registry=registry),model,registry,plan).audit(SRC)
        self.assertEqual(b.receipt.disposition,'READY_FOR_REVIEW')
        self.assertEqual(self.db.commit_batch(b,registry=registry,plan=plan,
                         recorded_at=KNOW,reviewer_approved=True).disposition,'BLOCK')

    def test_incomplete_batch_never_commits(self):
        r,p,b = prepare(self.db,[candidate()])
        self.assertEqual(b.receipt.disposition,'REVIEW_MISSING')
        self.assertEqual(self.db.commit_batch(b,registry=r,plan=p,recorded_at=KNOW,
                         reviewer_approved=True).disposition,'REVIEW')
        self.assertEqual(len(self.db.snapshot().events),0)


if __name__=='__main__':
    unittest.main()
