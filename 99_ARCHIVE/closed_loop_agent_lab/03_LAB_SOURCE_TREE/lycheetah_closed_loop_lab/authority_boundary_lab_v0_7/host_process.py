"""Separate-process authority/host coordinator for the crash-recovery lab.

Test scaffold only. Reviewer identity is supplied by test fixtures; no real UI,
identity provider, OS privilege boundary, or external provider is implemented.
"""
from __future__ import annotations
import argparse, base64, hashlib, hmac, json, math, os, secrets, sqlite3, subprocess, sys, time
from contextlib import closing
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROVIDER = HERE / "provider_process.py"
SCHEMA = "lycheetah-separated-authority/0.1"
AUDIENCE = "lab-host-1"
MAX_TTL = 300


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def b64u(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def unb64u(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def open_db(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15, isolation_level=None)
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize_authority_db(path: str, initial_policy_sha256: str) -> None:
    # Schema creation is a one-time setup operation, not performed on every
    # concurrent request. The durable policy row is the authority used by the
    # claim transaction; editing a JSON file alone does not silently change it.
    with closing(open_db(path)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS approvals (nonce TEXT PRIMARY KEY, operation_id TEXT NOT NULL UNIQUE, token_sha256 TEXT NOT NULL, action_sha256 TEXT NOT NULL, policy_sha256 TEXT NOT NULL, issued_at REAL NOT NULL, expires_at REAL NOT NULL, reviewer_id TEXT NOT NULL, approval_ref TEXT NOT NULL, revoked_at REAL, consumed_at REAL)")
        db.execute("CREATE TABLE IF NOT EXISTS operations (operation_id TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE, action_sha256 TEXT NOT NULL, action_json TEXT NOT NULL, policy_sha256 TEXT NOT NULL, state TEXT NOT NULL, last_error TEXT, result_json TEXT, updated_at REAL NOT NULL, FOREIGN KEY(nonce) REFERENCES approvals(nonce))")
        db.execute("CREATE TABLE IF NOT EXISTS policy_state (singleton INTEGER PRIMARY KEY CHECK(singleton=1), sha256 TEXT NOT NULL, policy_json TEXT NOT NULL, revision INTEGER NOT NULL)")
        db.execute("INSERT OR IGNORE INTO policy_state(singleton,sha256,policy_json,revision) VALUES(1,?,?,1)",
                   (initial_policy_sha256, "{}"))


def load_key(path: str) -> bytes:
    key = Path(path).read_bytes()
    if len(key) < 32: raise ValueError("key must be at least 32 bytes")
    return key


def policy_digest(path: str) -> str:
    return sha(json.loads(Path(path).read_text(encoding="utf-8")))


def load_action(path: str) -> dict[str, Any]:
    action = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"agent_id","operation_id","tool_name","arguments","scopes","workspace_id","dispatcher_id","dispatcher_version","side_effect"}
    if not isinstance(action, dict) or set(action) != required: raise ValueError("invalid action schema")
    if action["tool_name"] != "refund_order" or action["dispatcher_id"] != "fake-provider.refund" or action["dispatcher_version"] != "1":
        raise ValueError("unregistered tool route")
    if not isinstance(action["arguments"], dict) or not isinstance(action["scopes"], list): raise ValueError("invalid action arguments/scopes")
    if action["side_effect"] is not True: raise ValueError("this lab gates consequential actions only")
    return action


def token_issue(key: bytes, action: dict[str, Any], pol_sha: str, ttl: int, reviewer_id: str, approval_ref: str) -> tuple[str, dict[str, Any]]:
    if type(ttl) is not int or not 1 <= ttl <= MAX_TTL: raise ValueError("invalid ttl")
    now = time.time()
    if not math.isfinite(now): raise ValueError("invalid clock")
    payload = {
      "schema":SCHEMA,"audience_id":AUDIENCE,"nonce":secrets.token_hex(16),
      "operation_id":action["operation_id"],"action_sha256":sha(action),"policy_sha256":pol_sha,
      "issued_at":now,"expires_at":now+ttl,"reviewer_id":reviewer_id,"approval_ref":approval_ref,
    }
    body = canonical(payload); sig = hmac.new(key, body, hashlib.sha256).digest()
    return f"{b64u(body)}.{b64u(sig)}", payload


def token_verify(key: bytes, token: str) -> dict[str, Any]:
    if not isinstance(token, str) or token.count(".") != 1: raise ValueError("invalid-token-format")
    body_part, sig_part = token.split(".", 1)
    try: body, sig = unb64u(body_part), unb64u(sig_part); payload = json.loads(body.decode("utf-8"))
    except Exception as exc: raise ValueError("invalid-token-encoding") from exc
    if not hmac.compare_digest(hmac.new(key, body, hashlib.sha256).digest(), sig): raise ValueError("bad-token-signature")
    required={"schema","audience_id","nonce","operation_id","action_sha256","policy_sha256","issued_at","expires_at","reviewer_id","approval_ref"}
    if not isinstance(payload,dict) or set(payload)!=required: raise ValueError("invalid-token-schema")
    if payload["schema"]!=SCHEMA or payload["audience_id"]!=AUDIENCE: raise ValueError("wrong-token-audience-or-schema")
    for field in ("issued_at","expires_at"):
        if type(payload[field]) not in (int,float) or not math.isfinite(payload[field]): raise ValueError("invalid-token-time")
    if payload["issued_at"]>time.time(): raise ValueError("token-not-yet-valid")
    if payload["expires_at"]<=time.time() or payload["expires_at"]-payload["issued_at"]>MAX_TTL: raise ValueError("token-expired-or-invalid-lifetime")
    return payload


def call_provider(provider_db: str, mode: str, action: dict[str, Any] | None = None, fault: str = "none", operation_id: str | None = None, authority_db: str | None = None, expected_policy_sha256: str | None = None, approval_nonce: str | None = None, ready_marker: str | None = None) -> subprocess.CompletedProcess[str]:
    if mode == "commit":
        req = {"operation_id": action["operation_id"], "approval_nonce": approval_nonce, "action_sha256": sha(action), "action": action}
        cmd=[sys.executable,"-S",str(PROVIDER),"commit","--db",provider_db,"--authority-db",str(authority_db),"--expected-policy-sha256",str(expected_policy_sha256),"--fault",fault]
        if ready_marker: cmd += ["--ready-marker",ready_marker]
        return subprocess.run(cmd, input=json.dumps(req), capture_output=True, text=True, timeout=10)
    return subprocess.run([sys.executable,"-S",str(PROVIDER),"lookup","--db",provider_db,"--operation-id",str(operation_id)], capture_output=True, text=True, timeout=10)


def issue(args) -> int:
    key=load_key(args.key_file); action=load_action(args.action_file); file_policy_sha=policy_digest(args.policy_file)
    initialize_authority_db(args.authority_db, file_policy_sha)
    with closing(open_db(args.authority_db)) as db:
        row = db.execute("SELECT sha256 FROM policy_state WHERE singleton=1").fetchone()
    if row is None or row[0] != file_policy_sha:
        raise ValueError("policy-file-differs-from-authoritative-policy; commit it with set-policy first")
    pol_sha = row[0]
    if not isinstance(args.reviewer_id, str) or not args.reviewer_id.strip(): raise ValueError("reviewer_id must be non-empty")
    if not isinstance(args.approval_ref, str) or not args.approval_ref.strip(): raise ValueError("approval_ref must be non-empty")
    token,payload=token_issue(key,action,pol_sha,args.ttl,args.reviewer_id,args.approval_ref)
    token_sha=hashlib.sha256(token.encode()).hexdigest(); action_sha=sha(action)
    with closing(open_db(args.authority_db)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("INSERT INTO approvals(nonce,operation_id,token_sha256,action_sha256,policy_sha256,issued_at,expires_at,reviewer_id,approval_ref) VALUES(?,?,?,?,?,?,?,?,?)",
                       (payload["nonce"],action["operation_id"],token_sha,action_sha,pol_sha,payload["issued_at"],payload["expires_at"],args.reviewer_id,args.approval_ref))
            db.execute("INSERT INTO operations(operation_id,nonce,action_sha256,action_json,policy_sha256,state,updated_at) VALUES(?,?,?,?,?,'APPROVED',?)",
                       (action["operation_id"],payload["nonce"],action_sha,json.dumps(action,sort_keys=True),pol_sha,time.time()))
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK"); raise
    Path(args.token_file).write_text(token,encoding="utf-8")
    print(json.dumps({"status":"approved-in-test-fixture","operation_id":action["operation_id"],"action_sha256":action_sha,"policy_sha256":pol_sha,"expires_at":payload["expires_at"]},sort_keys=True)); return 0


def execute(args) -> int:
    key=load_key(args.key_file); action=load_action(args.action_file); token=Path(args.token_file).read_text(encoding="utf-8").strip()
    try: payload=token_verify(key,token)
    except ValueError as exc: print(json.dumps({"status":"denied","reason":str(exc)})); return 2
    action_sha=sha(action)
    if action_sha != payload["action_sha256"] or action["operation_id"] != payload["operation_id"]:
        print(json.dumps({"status":"denied","reason":"action-mismatch"})); return 2
    with closing(open_db(args.authority_db)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            policy_row = db.execute("SELECT sha256 FROM policy_state WHERE singleton=1").fetchone()
            current_pol = policy_row[0] if policy_row else None
            if current_pol is None or current_pol != payload["policy_sha256"]:
                db.execute("ROLLBACK"); print(json.dumps({"status":"denied","reason":"policy-changed"})); return 2
            row=db.execute("SELECT token_sha256,action_sha256,policy_sha256,revoked_at,consumed_at FROM approvals WHERE nonce=? AND operation_id=?",(payload["nonce"],action["operation_id"])).fetchone()
            op=db.execute("SELECT state FROM operations WHERE operation_id=?",(action["operation_id"],)).fetchone()
            if row is None or op is None or row[0] != hashlib.sha256(token.encode()).hexdigest() or row[1] != action_sha or row[2] != current_pol:
                db.execute("ROLLBACK"); print(json.dumps({"status":"denied","reason":"approval-record-mismatch"})); return 2
            if row[4] is not None or op[0] != "APPROVED":
                db.execute("ROLLBACK"); print(json.dumps({"status":"denied","reason":"approval-already-consumed"})); return 2
            if row[3] is not None:
                db.execute("ROLLBACK"); print(json.dumps({"status":"denied","reason":"revoked-before-claim"})); return 2
            now=time.time()
            if now >= payload["expires_at"]:
                db.execute("ROLLBACK"); print(json.dumps({"status":"denied","reason":"token-expired"})); return 2
            db.execute("UPDATE approvals SET consumed_at=? WHERE nonce=?",(now,payload["nonce"]))
            db.execute("UPDATE operations SET state='CLAIMED', updated_at=? WHERE operation_id=?",(now,action["operation_id"]))
            db.execute("COMMIT")
        except Exception:
            try: db.execute("ROLLBACK")
            except sqlite3.Error: pass
            raise
    if args.crash_point == "after_claim": os._exit(81)
    provider=call_provider(args.provider_db,"commit",action=action,fault=args.provider_fault,authority_db=args.authority_db,expected_policy_sha256=payload["policy_sha256"],approval_nonce=payload["nonce"],ready_marker=args.provider_ready_marker)
    if args.crash_point == "after_provider_response" and provider.returncode == 0: os._exit(82)
    if provider.returncode != 0:
        _set_operation_state(args.authority_db,action["operation_id"],"UNKNOWN",f"provider-process-exit-{provider.returncode}")
        print(json.dumps({"status":"unknown-needs-reconciliation","operation_id":action["operation_id"],"provider_exit":provider.returncode},sort_keys=True)); return 0
    try: response=json.loads(provider.stdout)
    except Exception:
        _set_operation_state(args.authority_db,action["operation_id"],"UNKNOWN","provider-response-unreadable")
        print(json.dumps({"status":"unknown-needs-reconciliation","operation_id":action["operation_id"]},sort_keys=True)); return 0
    if not response.get("ok"):
        _set_operation_state(args.authority_db,action["operation_id"],"NEEDS_REVIEW",response.get("error","provider-error"))
        print(json.dumps({"status":"needs-review","provider_error":response.get("error")},sort_keys=True)); return 0
    _set_operation_state(args.authority_db,action["operation_id"],"COMPLETED",None,response["provider_result"])
    print(json.dumps({"status":"completed","provider_result":response["provider_result"],"idempotent_replay":response["idempotent_replay"]},sort_keys=True)); return 0


def _set_operation_state(db_path: str, operation_id: str, state: str, error: str | None, result: dict[str, Any] | None = None) -> None:
    with closing(open_db(db_path)) as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE operations SET state=?,last_error=?,result_json=COALESCE(?,result_json),updated_at=? WHERE operation_id=?",
                   (state,error,json.dumps(result,sort_keys=True) if result is not None else None,time.time(),operation_id))
        db.execute("COMMIT")


def revoke(args) -> int:
    key=load_key(args.key_file); token=Path(args.token_file).read_text(encoding="utf-8").strip()
    try: payload=token_verify(key,token)
    except ValueError as exc: print(json.dumps({"status":"denied","reason":str(exc)})); return 2
    with closing(open_db(args.authority_db)) as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE approvals SET revoked_at=? WHERE nonce=? AND token_sha256=?",(time.time(),payload["nonce"],hashlib.sha256(token.encode()).hexdigest()))
        changed=db.execute("SELECT changes()").fetchone()[0]
        db.execute("COMMIT")
    print(json.dumps({"status":"revoked" if changed else "not-found"},sort_keys=True)); return 0 if changed else 2


def recover(args) -> int:
    with closing(open_db(args.authority_db)) as db:
        row=db.execute("SELECT o.action_sha256,o.action_json,o.policy_sha256,o.state,o.nonce,a.revoked_at FROM operations o JOIN approvals a USING(nonce) WHERE o.operation_id=?",(args.operation_id,)).fetchone()
        policy_row = db.execute("SELECT sha256 FROM policy_state WHERE singleton=1").fetchone()
    if row is None: print(json.dumps({"status":"not-found"})); return 2
    action_sha,action_json,stored_policy,state,nonce,revoked_at=row; action=json.loads(action_json)
    current_policy = policy_row[0] if policy_row else ""
    lookup=call_provider(args.provider_db,"lookup",operation_id=args.operation_id)
    try: provider_state=json.loads(lookup.stdout) if lookup.returncode==0 else {"error":"provider-lookup-failed"}
    except Exception: provider_state={"error":"provider-lookup-unreadable"}
    if not provider_state.get("found") and "error" not in provider_state:
        # Never let a recovery query dispatch an action that was only APPROVED
        # but never durably claimed. Likewise, absence after COMPLETED indicates
        # ledger inconsistency, not permission to replay a completed operation.
        if state not in {"CLAIMED", "UNKNOWN"}:
            reason = "completed-operation-missing-provider-record" if state == "COMPLETED" else f"operation-state-not-retryable:{state}"
            _set_operation_state(args.authority_db,args.operation_id,"NEEDS_REVIEW",reason)
            print(json.dumps({"status":"needs-review","reason":reason},sort_keys=True)); return 0
        # The fake provider is a strongly consistent SQLite ledger. If the action
        # has no provider record, retry the SAME operation ID and payload only if
        # authoritative policy still matches and this operation has not been revoked.
        if revoked_at is not None:
            _set_operation_state(args.authority_db,args.operation_id,"NEEDS_REVIEW","revoked-after-claim-before-effect")
            print(json.dumps({"status":"needs-review","reason":"revoked-after-claim-before-effect"},sort_keys=True)); return 0
        if current_policy != stored_policy:
            _set_operation_state(args.authority_db,args.operation_id,"NEEDS_REVIEW","policy-changed-before-retry")
            print(json.dumps({"status":"needs-review","reason":"policy-changed-before-retry"},sort_keys=True)); return 0
        provider=call_provider(args.provider_db,"commit",action=action,authority_db=args.authority_db,expected_policy_sha256=stored_policy,approval_nonce=nonce)
        if args.crash_point == "after_provider_response" and provider.returncode == 0: os._exit(83)
        if provider.returncode != 0:
            _set_operation_state(args.authority_db,args.operation_id,"UNKNOWN","recovery-dispatch-uncertain")
            print(json.dumps({"status":"unknown-needs-reconciliation","operation_id":args.operation_id},sort_keys=True)); return 0
        response=json.loads(provider.stdout)
        provider_state={"found":True,"action_sha256":action_sha,"provider_result":response["provider_result"]}
    if "error" in provider_state:
        _set_operation_state(args.authority_db,args.operation_id,"NEEDS_REVIEW",provider_state["error"])
        print(json.dumps({"status":"needs-review","reason":provider_state["error"]},sort_keys=True)); return 0
    if state == "APPROVED":
        _set_operation_state(args.authority_db,args.operation_id,"CONFLICT","provider-effect-without-durable-claim")
        print(json.dumps({"status":"conflict","reason":"provider-effect-without-durable-claim"},sort_keys=True)); return 3
    if provider_state.get("action_sha256") != action_sha:
        _set_operation_state(args.authority_db,args.operation_id,"CONFLICT","provider-action-digest-conflict")
        print(json.dumps({"status":"conflict","reason":"provider-action-digest-conflict"},sort_keys=True)); return 3
    _set_operation_state(args.authority_db,args.operation_id,"COMPLETED",None,provider_state["provider_result"])
    print(json.dumps({"status":"reconciled-completed","operation_id":args.operation_id,"provider_result":provider_state["provider_result"]},sort_keys=True)); return 0


def set_policy(args) -> int:
    file_sha = policy_digest(args.policy_file)
    initialize_authority_db(args.authority_db, file_sha)
    policy_json = Path(args.policy_file).read_text(encoding="utf-8")
    with closing(open_db(args.authority_db)) as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE policy_state SET sha256=?, policy_json=?, revision=revision+1 WHERE singleton=1", (file_sha, policy_json,))
        revision = db.execute("SELECT revision FROM policy_state WHERE singleton=1").fetchone()[0]
        db.execute("COMMIT")
    print(json.dumps({"status":"policy-updated","policy_sha256":file_sha,"revision":revision},sort_keys=True)); return 0


def status(args) -> int:
    with closing(open_db(args.authority_db)) as db:
        row=db.execute("SELECT state,last_error,result_json,action_sha256,policy_sha256 FROM operations WHERE operation_id=?",(args.operation_id,)).fetchone()
    if not row: print(json.dumps({"status":"not-found"})); return 2
    print(json.dumps({"state":row[0],"last_error":row[1],"result":json.loads(row[2]) if row[2] else None,"action_sha256":row[3],"policy_sha256":row[4]},sort_keys=True)); return 0


def main() -> int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    i=sub.add_parser("issue"); i.add_argument("--authority-db",required=True); i.add_argument("--policy-file",required=True); i.add_argument("--key-file",required=True); i.add_argument("--action-file",required=True); i.add_argument("--token-file",required=True); i.add_argument("--ttl",type=int,default=120); i.add_argument("--reviewer-id",default="fixture-reviewer"); i.add_argument("--approval-ref",default="fixture-approval")
    e=sub.add_parser("execute"); e.add_argument("--authority-db",required=True); e.add_argument("--provider-db",required=True); e.add_argument("--key-file",required=True); e.add_argument("--action-file",required=True); e.add_argument("--token-file",required=True); e.add_argument("--crash-point",choices=["none","after_claim","after_provider_response"],default="none"); e.add_argument("--provider-fault",choices=["none","before_commit","after_commit","pause_after_policy_lock"],default="none"); e.add_argument("--provider-ready-marker")
    r=sub.add_parser("recover"); r.add_argument("--authority-db",required=True); r.add_argument("--provider-db",required=True); r.add_argument("--operation-id",required=True); r.add_argument("--crash-point",choices=["none","after_provider_response"],default="none")
    v=sub.add_parser("revoke"); v.add_argument("--authority-db",required=True); v.add_argument("--key-file",required=True); v.add_argument("--token-file",required=True)
    s=sub.add_parser("status"); s.add_argument("--authority-db",required=True); s.add_argument("--operation-id",required=True)
    u=sub.add_parser("set-policy"); u.add_argument("--authority-db",required=True); u.add_argument("--policy-file",required=True)
    args=p.parse_args()
    try:
        return {"issue":issue,"execute":execute,"recover":recover,"revoke":revoke,"status":status,"set-policy":set_policy}[args.cmd](args)
    except Exception as exc:
        print(json.dumps({"status":"error","error":type(exc).__name__,"detail":str(exc)},sort_keys=True)); return 1

if __name__ == "__main__":
    raise SystemExit(main())
