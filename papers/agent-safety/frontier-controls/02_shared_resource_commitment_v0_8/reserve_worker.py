"""New public packaging adapter, not the missing original reserve_worker."""
from dataclasses import asdict
import json
import sys
from resource_ledger import SharedResourceLedger

if __name__ == "__main__":
    db, account, broker, effect, amount = sys.argv[1:6]
    decision = SharedResourceLedger(db).reserve(account, broker, effect, int(amount))
    print(json.dumps(asdict(decision), sort_keys=True))
