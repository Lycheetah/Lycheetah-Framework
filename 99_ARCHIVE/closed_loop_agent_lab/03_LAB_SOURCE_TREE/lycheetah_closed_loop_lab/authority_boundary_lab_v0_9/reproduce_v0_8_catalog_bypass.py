"""Reproduce the missing catalog enforcement in the older v0.7 host harness.

This script executes only the local fake provider with disposable temporary files.
It is evidence about that local test harness, not a deployed Lycheetah Guard bypass.
"""
from __future__ import annotations
import json, sqlite3, subprocess, sys, tempfile, uuid
from contextlib import closing
from pathlib import Path
from tool_catalog import DEFAULT_CATALOG

HERE = Path(__file__).resolve().parent
LEGACY_HOST = HERE.parent / "authority_boundary_lab_v0_7" / "host_process.py"
CANDIDATE_HOST = HERE / "host_process.py"


def run_case(host: Path, action: dict, policy: dict, root: Path, label: str) -> dict:
    case = root / label
    case.mkdir()
    action_file = case / "action.json"
    policy_file = case / "policy.json"
    key_file = case / "issuer.key"
    token_file = case / "token.txt"
    authority_db = case / "authority.sqlite"
    provider_db = case / "provider.sqlite"
    action_file.write_text(json.dumps(action, sort_keys=True), encoding="utf-8")
    policy_file.write_text(json.dumps(policy, sort_keys=True), encoding="utf-8")
    key_file.write_bytes(b"test-only-catalog-key-long-enough-for-hmac-0123456789")
    key_file.chmod(0o600)
    issue = subprocess.run([sys.executable,"-S",str(host),"issue","--authority-db",str(authority_db),"--policy-file",str(policy_file),"--key-file",str(key_file),"--action-file",str(action_file),"--token-file",str(token_file)],capture_output=True,text=True,timeout=10)
    record = {"host":label,"issue_returncode":issue.returncode,"issue_stdout":issue.stdout.strip(),"issue_stderr":issue.stderr.strip()}
    if issue.returncode == 0:
        execute = subprocess.run([sys.executable,"-S",str(host),"execute","--authority-db",str(authority_db),"--provider-db",str(provider_db),"--key-file",str(key_file),"--action-file",str(action_file),"--token-file",str(token_file)],capture_output=True,text=True,timeout=15)
        record.update({"execute_returncode":execute.returncode,"execute_stdout":execute.stdout.strip(),"execute_stderr":execute.stderr.strip()})
    effects=[]
    if provider_db.exists():
        with closing(sqlite3.connect(provider_db)) as db:
            try:
                effects=[{"operation_id":r[0],"action_sha256":r[1],"result":json.loads(r[2])} for r in db.execute("SELECT operation_id,action_sha256,result_json FROM effects")]
            except sqlite3.OperationalError:
                effects=[]
    record["durable_fake_effect_count"] = len(effects)
    record["effects"] = effects
    return record


def main() -> int:
    policy={"policy_id":"catalog-bound-refund","version":1,"refund_requires_host_approval":True,"tool_catalog_sha256":DEFAULT_CATALOG.digest}
    # The older host schema has no catalog marker and checks neither the catalog's
    # argument contract nor the policy's catalog digest. This deliberately invalid
    # action is accepted by the v0.7 fake host/provider pair in this fixture.
    operation_id="op-legacy-"+uuid.uuid4().hex
    raw_action={"agent_id":"fixture-agent","operation_id":operation_id,"tool_name":"refund_order","arguments":{"order_id":"ORD-42","amount_minor":-1,"currency":"BTC"},"scopes":["orders:refund"],"workspace_id":"disposable-workspace","dispatcher_id":"fake-provider.refund","dispatcher_version":"1","side_effect":True}
    catalog_stamped=DEFAULT_CATALOG.stamp({"tool_name":"refund_order","arguments":{"order_id":"ORD-42","amount_minor":2500,"currency":"NZD"}},operation_id="op-candidate-"+uuid.uuid4().hex,agent_id="fixture-agent",workspace_id="disposable-workspace")
    with tempfile.TemporaryDirectory(prefix="lyc-catalog-bypass-") as td:
        root=Path(td)
        legacy=run_case(LEGACY_HOST,raw_action,policy,root,"legacy-v0.7")
        # Also confirm the new candidate refuses the old unstamped schema.
        candidate=run_case(CANDIDATE_HOST,raw_action,policy,root,"candidate-v0.9-raw-action")
        candidate_valid=run_case(CANDIDATE_HOST,catalog_stamped,policy,root,"candidate-v0.9-catalog-stamped")
    result={"status":"local synthetic reproducer","scope":"old fake host/provider vs catalog-bound local host/provider","legacy_invalid_action_accepted":legacy.get("durable_fake_effect_count")==1,"candidate_raw_action_rejected":candidate.get("issue_returncode")!=0 and candidate.get("durable_fake_effect_count")==0,"candidate_stamped_action_completed":candidate_valid.get("durable_fake_effect_count")==1,"legacy":legacy,"candidate_raw_action":candidate,"candidate_valid_action":candidate_valid,"warning":"Not an actual MCP host or deployed Lycheetah Guard bypass. All effects are local SQLite fake-provider rows."}
    out=HERE/"catalog_bypass_repro_v0_9.json"
    out.write_text(json.dumps(result,sort_keys=True,indent=2),encoding="utf-8")
    print(json.dumps({"result_file":str(out),"legacy_invalid_action_accepted":result["legacy_invalid_action_accepted"],"candidate_raw_action_rejected":result["candidate_raw_action_rejected"],"candidate_stamped_action_completed":result["candidate_stamped_action_completed"]},sort_keys=True))
    return 0 if all(result[k] for k in ("legacy_invalid_action_accepted","candidate_raw_action_rejected","candidate_stamped_action_completed")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
