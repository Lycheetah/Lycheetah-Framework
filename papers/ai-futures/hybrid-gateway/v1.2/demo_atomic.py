"""Whole-batch SQLite revision with a trusted operator; fictional evidence."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hybrid_gateway import (SQLiteLedger, ScriptedNeuralAdapter,
    TrustedContractRegistry, ExtractionPlan, CoverageAuditor)
from run_coverage_eval import SOURCE, CLAUSES, propose

KNOW='2026-10-04T00:00:00Z'

with TemporaryDirectory() as temp:
    path=Path(temp)/'gateway.sqlite3'
    store=SQLiteLedger(path)
    store.register_source(SOURCE)
    registry=TrustedContractRegistry([SOURCE],CLAUSES)
    plan=ExtractionPlan.create(registry,SOURCE.source_id)
    model=ScriptedNeuralAdapter('explicit-fixture-not-a-model', {
        SOURCE.source_id:[propose('refund','R-1')]})
    audit=CoverageAuditor(store.snapshot(registry=registry),model,registry,plan)
    partial=audit.audit(SOURCE)
    print('Partial extraction:',partial.receipt.disposition,
          '| stages:',len(partial.stages))
    print('Cannot commit partial:',store.commit_batch(partial,registry=registry,plan=plan,
          recorded_at=KNOW,reviewer_approved=True).disposition)
    model.candidates[SOURCE.source_id]=[
        propose('refund','R-1'),propose('loyalty','L-1')]
    complete=audit.audit(SOURCE)
    print('Complete extraction:',complete.receipt.disposition)
    print('Without reviewer:',store.commit_batch(complete,registry=registry,plan=plan,
          recorded_at=KNOW,reviewer_approved=False).disposition)
    decision=store.commit_batch(complete,registry=registry,plan=plan,
          recorded_at=KNOW,reviewer_approved=True)
    print('One batch, two claims:',decision.disposition)
    print('Stale replay:',store.commit_batch(complete,registry=registry,plan=plan,
          recorded_at=KNOW,reviewer_approved=True).disposition)
    fresh=SQLiteLedger(path).snapshot(registry=registry,anchored_head=decision.event_hash)
    print('After restart:',len(fresh.events),'batch events,',len(fresh.claims),'claims')
    q=fresh.query(tenant=SOURCE.tenant,subject='refunds',predicate='window_days',
       scope='in_store',effective_at=KNOW,known_at=KNOW)
    print('Policy answer:',q.value,'evidence receipts:',len(q.citations))
    print('No external actions performed; fixture claims only.')
