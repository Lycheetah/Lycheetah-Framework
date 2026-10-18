"""Cycle 11 offline example: compare v1.0 in-memory rejection with v1.1 durability.

Fictional clauses, automated test actor, ephemeral local keys; NOT a human study.
"""
import json
import secrets
from pathlib import Path
from tempfile import TemporaryDirectory

from hybrid_gateway.review_desk import ReviewDesk
from hybrid_gateway.authorization import ReviewKeyring
from hybrid_gateway.durable import SQLiteLedger
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW

PASSWORD='demo-only password that must not be used in production'

def review(path, *, journal, action, key):
    db=SQLiteLedger(path,require_review_journal=journal,require_signed_approval=True)
    registry,plan,batch=prepare(db)
    desk=ReviewDesk(ledger=db,registry=registry,plan=plan,batch=batch,
                    recorded_at=KNOW,key_id='demo-key',signing_secret=key,password=PASSWORD)
    token,csrf=desk.login(PASSWORD)
    desk.start_review(token)
    result=desk.submit(token,csrf=csrf,presented_digest=desk.view_digest,
                       decision=action,confirmation='YES_REVIEWED_EXACT_BATCH' if action=='approve' else '')
    restarted=SQLiteLedger(path)
    evidence=restarted.audit_review_decisions(ReviewKeyring({'demo-key':key}))
    return {'ui_disposition':result.disposition,'knowledge_events_after_restart':len(restarted.snapshot().events),
            'journal_entries_after_restart':evidence['total'],
            'journal_valid_approvals':evidence['verified_approvals'],
            'journal_valid_rejections':evidence['verified_rejections'],
            'journal_invalid_entries':list(evidence['invalid_entries']),
            'journal_head':evidence['journal_head']}

def main():
    with TemporaryDirectory() as folder:
        k=secrets.token_bytes(32)
        data={
            'v1_0_rejected':review(Path(folder)/'legacy.db',journal=False,action='reject',key=k),
            'v1_1_rejected':review(Path(folder)/'reject.db',journal=True,action='reject',key=k),
            'v1_1_approved':review(Path(folder)/'approve.db',journal=True,action='approve',key=k),
            'interpretation':'local software behavior, not model accuracy or observed human performance',
        }
        print(json.dumps(data,indent=2,sort_keys=True))
        return data

if __name__=='__main__':main()
