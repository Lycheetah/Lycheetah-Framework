"""Run the fictional local reviewer browser, demonstrating signed atomic approval and durable decision journaling.

    export LYCHEETAH_REVIEW_PASSWORD='use a long private local-demo password'
    python demo_review_desk.py

No live model, real policy, identity attestation, TLS, or production secret custody.
"""
import os
import argparse
import json
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
from hybrid_gateway.review_desk import ReviewDesk, make_review_server
from hybrid_gateway.durable import SQLiteLedger
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report', help='Create a new privacy-minimized local session observation JSON file')
    args=ap.parse_args()
    pw=os.environ.get('LYCHEETAH_REVIEW_PASSWORD','')
    if len(pw)<16:
        raise SystemExit('Set LYCHEETAH_REVIEW_PASSWORD (16+ characters) before starting')
    with TemporaryDirectory() as folder:
        ledger=SQLiteLedger(Path(folder)/'fixture-review.sqlite3',require_review_journal=True)
        registry,plan,batch=prepare(ledger)
        desk=ReviewDesk(ledger=ledger,registry=registry,plan=plan,batch=batch,
            recorded_at=KNOW,key_id='local-demo-only',signing_secret=secrets.token_bytes(32),password=pw)
        with make_review_server(desk,port=0) as server:
            print('DEMO ONLY — fictional policy clauses, ephemeral DB and signing key')
            print(f'Open http://127.0.0.1:{server.server_port}/')
            print('Press Ctrl+C to stop. This is not an identity or production approval system.')
            try: server.serve_forever()
            except KeyboardInterrupt: pass
            print('Outcome:',desk.outcome)
            if args.report:
                # Exclusive creation refuses silent overwrite of trial records.
                fd=os.open(args.report,os.O_CREAT | os.O_EXCL | os.O_WRONLY,0o600)
                with os.fdopen(fd,'w',encoding='utf-8') as out:
                    json.dump(desk.observation(),out,indent=2)
                print('Privacy-minimized observation saved at:',args.report)

if __name__=='__main__':main()
