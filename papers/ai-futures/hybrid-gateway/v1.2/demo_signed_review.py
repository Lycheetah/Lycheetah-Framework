"""Cycle 9: test-only demonstration of an operator-key authorization boundary.

No live AI model or human identity is involved. The deliberately generated
32-byte secret is ephemeral and never suitable for production deployment.
"""
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
from hybrid_gateway import SQLiteLedger
from hybrid_gateway.authorization import ReviewKeyring, issue_approval
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW


def run():
    with TemporaryDirectory() as folder:
        ledger=SQLiteLedger(Path(folder)/'review.sqlite3',require_signed_approval=True)
        registry,plan,batch=prepare(ledger)
        key=secrets.token_bytes(32)  # Demo-only; a real signing key must be separately managed.
        keys=ReviewKeyring({'demo-operator-key':key})
        unsigned=ledger.commit_batch(batch,registry=registry,plan=plan,
            recorded_at=KNOW,reviewer_approved=True)
        assert unsigned.disposition=='REVIEW'
        permit=issue_approval(batch,plan,key_id='demo-operator-key',secret=key,
                              recorded_at=KNOW,ledger_id=ledger.ledger_id)
        decision=ledger.commit_batch(batch,registry=registry,plan=plan,
            recorded_at=KNOW,authorization=permit,trusted_keys=keys)
        assert decision.disposition=='ALLOW'
        again=SQLiteLedger(ledger.path)
        replay=again.commit_batch(batch,registry=registry,plan=plan,
            recorded_at=KNOW,authorization=permit,trusted_keys=keys)
        audit=again.audit_persisted_approvals(keys)
        assert replay.disposition!='ALLOW'
        assert audit['valid_approval_count']==1 and not audit['batch_events_without_verified_approval']
        snapshot=again.snapshot(anchored_head=decision.event_hash)
        assert len(snapshot.events)==1 and len(snapshot.claims)==2
        print('No signature:',unsigned.disposition)
        print('Signed exact batch:',decision.disposition,'| claims:',len(snapshot.claims))
        print('Replayed permit:',replay.disposition)
        print('Audit after restart:',audit['valid_approval_count'],'valid signature/event binding')
        print('NOTE: a demo operator key is not a real person or production identity.')

if __name__=='__main__':run()
