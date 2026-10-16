"""Separate-process durable fake provider for crash/restart tests.

This test double uses a host-policy revision fence and provider-side idempotency
in SQLite. Real remote services need an equivalent native fencing/idempotency
contract; sharing these local test databases is not a production architecture.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, sys, time
from contextlib import closing
from pathlib import Path
from typing import Any
from tool_catalog import DEFAULT_CATALOG, ProposalError, validate_policy_binding, validate_stamped_action


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15, isolation_level=None)
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("CREATE TABLE IF NOT EXISTS effects (operation_id TEXT PRIMARY KEY, action_sha256 TEXT NOT NULL, result_json TEXT NOT NULL, committed_at REAL NOT NULL)")
    return db


def commit(db_path: str, authority_db_path: str, expected_policy_sha256: str,
           request: dict[str, Any], fault: str = "none", ready_marker: str | None = None) -> int:
    operation_id = request["operation_id"]
    approval_nonce = request["approval_nonce"]
    action = request["action"]
    action_sha256 = request["action_sha256"]
    try:
        validate_stamped_action(action, DEFAULT_CATALOG, consequential_only=True)
    except (ProposalError, TypeError) as exc:
        print(json.dumps({"error":"catalog-action-validation-failed","detail":str(exc)})); return 3
    computed = hashlib.sha256(canonical(action)).hexdigest()
    if not isinstance(operation_id, str) or not operation_id:
        print(json.dumps({"error":"invalid-operation-id"})); return 2
    if not isinstance(approval_nonce, str) or not approval_nonce:
        print(json.dumps({"error":"invalid-approval-nonce"})); return 2
    if computed != action_sha256 or action.get("operation_id") != operation_id:
        print(json.dumps({"error":"action-digest-mismatch"})); return 2
    if action.get("tool_name") != "refund_order" or action.get("dispatcher_id") != "fake-provider.refund" or action.get("dispatcher_version") != "1":
        print(json.dumps({"error":"unregistered-provider-operation"})); return 3
    try:
        # The authority DB transaction acts as a local policy-revision fence.
        # The fake provider holds the writer lock while committing its own durable
        # effect record, so set-policy cannot linearize in the middle of dispatch.
        # A real remote provider needs a native equivalent; this is only a fixture.
        auth = sqlite3.connect(authority_db_path, timeout=15, isolation_level=None)
        auth.execute("PRAGMA synchronous=FULL")
        auth.execute("BEGIN IMMEDIATE")
        policy_row = auth.execute(
            "SELECT p.sha256,p.policy_json,a.revoked_at,a.operation_id,a.action_sha256,a.consumed_at "
            "FROM policy_state p LEFT JOIN approvals a ON a.nonce=? WHERE p.singleton=1",
            (approval_nonce,),
        ).fetchone()
        if policy_row is None or policy_row[0] != expected_policy_sha256:
            auth.execute("ROLLBACK")
            auth.close()
            print(json.dumps({"error":"policy-fence-rejected"})); return 6
        try:
            bound_policy = validate_policy_binding(json.loads(policy_row[1]), DEFAULT_CATALOG)
            if hashlib.sha256(canonical(bound_policy)).hexdigest() != policy_row[0]:
                raise ValueError("stored-policy-digest-mismatch")
        except (json.JSONDecodeError, ProposalError, TypeError, ValueError) as exc:
            auth.execute("ROLLBACK"); auth.close()
            print(json.dumps({"error":"policy-catalog-binding-rejected","detail":str(exc)})); return 6
        if policy_row[2] is not None:
            auth.execute("ROLLBACK"); auth.close()
            print(json.dumps({"error":"approval-revoked-at-provider-boundary"})); return 7
        if policy_row[3] != operation_id or policy_row[4] != action_sha256 or policy_row[5] is None:
            auth.execute("ROLLBACK"); auth.close()
            print(json.dumps({"error":"durable-claim-fence-rejected"})); return 8
        if ready_marker:
            Path(ready_marker).write_text("policy-fence-held", encoding="utf-8")
        if fault == "pause_after_policy_lock":
            # Deterministic race-test hook: hold the authority writer lock long
            # enough for a separate process to attempt a concurrent policy update.
            time.sleep(1.0)
        if fault == "before_commit":
            # Crash after checking the revision and acquiring the policy fence,
            # but before opening/committing the provider effect transaction.
            os._exit(71)
        with closing(connect(db_path)) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT action_sha256, result_json FROM effects WHERE operation_id=?", (operation_id,)).fetchone()
            if row:
                db.execute("COMMIT")
                auth.execute("COMMIT")
                auth.close()
                if row[0] != action_sha256:
                    print(json.dumps({"error":"idempotency-key-payload-conflict"})); return 4
                existing = json.loads(row[1])
                print(json.dumps({"ok":True,"provider_result":existing,"idempotent_replay":True},sort_keys=True)); return 0
            result = {
                "status":"committed", "operation_id":operation_id,
                "action_sha256":action_sha256,
                "tool_name":action["tool_name"], "arguments":action["arguments"],
                "committed_at":time.time(),
            }
            db.execute("INSERT INTO effects(operation_id, action_sha256, result_json, committed_at) VALUES (?, ?, ?, ?)",
                       (operation_id, action_sha256, json.dumps(result, sort_keys=True), result["committed_at"]))
            db.execute("COMMIT")
        auth.execute("COMMIT")
        auth.close()
        if fault == "after_commit":
            # Effect is durable, but caller receives no response.
            os._exit(72)
        print(json.dumps({"ok":True,"provider_result":result,"idempotent_replay":False},sort_keys=True))
        return 0
    except sqlite3.Error as exc:
        try: auth.execute("ROLLBACK")
        except Exception: pass
        try: auth.close()
        except Exception: pass
        print(json.dumps({"error":"provider-store-error","detail":type(exc).__name__})); return 5


def lookup(db_path: str, operation_id: str) -> int:
    try:
        with closing(connect(db_path)) as db:
            row = db.execute("SELECT action_sha256, result_json FROM effects WHERE operation_id=?", (operation_id,)).fetchone()
        if row:
            print(json.dumps({"found":True,"action_sha256":row[0],"provider_result":json.loads(row[1])},sort_keys=True))
        else:
            print(json.dumps({"found":False},sort_keys=True))
        return 0
    except sqlite3.Error as exc:
        print(json.dumps({"error":"provider-store-error","detail":type(exc).__name__})); return 5


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("commit"); c.add_argument("--db", required=True); c.add_argument("--authority-db", required=True); c.add_argument("--expected-policy-sha256", required=True); c.add_argument("--fault", choices=["none","before_commit","after_commit","pause_after_policy_lock"], default="none"); c.add_argument("--ready-marker")
    l = sub.add_parser("lookup"); l.add_argument("--db", required=True); l.add_argument("--operation-id", required=True)
    args = parser.parse_args()
    if args.command == "lookup": return lookup(args.db, args.operation_id)
    try: request = json.load(sys.stdin)
    except Exception: print(json.dumps({"error":"invalid-request-json"})); return 2
    return commit(args.db,args.authority_db,args.expected_policy_sha256,request,args.fault,args.ready_marker)

if __name__ == "__main__":
    raise SystemExit(main())
