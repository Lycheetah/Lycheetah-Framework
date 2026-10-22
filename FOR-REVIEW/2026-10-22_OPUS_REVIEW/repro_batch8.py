"""RV09 probes: build fresh bundles, mutate and reseal, report the verifier's verdict."""
import copy, json, shutil, sys, tempfile
from hashlib import sha256
from pathlib import Path
sys.dont_write_bytecode = True
REPO = Path(sys.argv[1]); sys.path.insert(0, str(REPO))
from examples import guarded_handoff_risk_demo as demo

work = Path(tempfile.mkdtemp(prefix="rv09_"))
base = work / "base"; report0 = demo.run_demo(base)
print("base:", demo.verify_bundle(base)["status"], "checks", demo.verify_bundle(base)["checks"])

def reseal(d):
    m = json.loads((d / "manifest.json").read_text())
    for n in demo.BUNDLE_FILES:
        p = (d / n).read_bytes(); m["files"][n] = {"bytes": len(p), "sha256": sha256(p).hexdigest()}
    (d / "manifest.json").write_bytes(demo._json_bytes(m))

def run(label, mutate):
    d = work / label; shutil.copytree(base, d)
    mutate(d); reseal(d)
    try:
        r = demo.verify_bundle(d); out = f"{r['status']:<16} errors={r['errors'][:2]}"
    except BaseException as e:
        out = f"RAISED {type(e).__module__}.{type(e).__name__}: {str(e)[:80]}"
    print(f"{label:<34} {out}")

def edit_json(name, fn):
    def m(d):
        p = d / name; v = json.loads(p.read_text()); fn(v); p.write_bytes(demo._json_bytes(v))
    return m

def rewitness(rec):
    rec["witness_digest"] = demo._recorded_witness_digest(rec)

run("R1_report_limits_emptied", edit_json("run-report.json", lambda r: r.__setitem__("limits", [])))
run("R2_report_mode_production", edit_json("run-report.json", lambda r: r.__setitem__("mode", "PRODUCTION_ATTESTED")))
run("R3_report_bound_risk_LOW", edit_json("run-report.json", lambda r: r.__setitem__("bound_risk", "LOW")))
run("R4_report_extra_claim", edit_json("run-report.json", lambda r: r.__setitem__("authenticated_human_approval", True)))
run("R5_report_hash_unchanged_false", edit_json("run-report.json", lambda r: r.__setitem__("critical_hash_unchanged_by_risk_downgrade", False)))
run("R6_report_workspace_kept", edit_json("run-report.json", lambda r: r.__setitem__("temporary_workspace_removed_on_exit", False)))
def c1(r):
    r["replay"]["permit"]["permit_digest"] = "0" * 64; rewitness(r["replay"])
run("C1_replay_other_permit", edit_json("run-report.json", c1))
def c2(r):
    r["risk_downgrade"]["live_action_hash"] = "0" * 64; rewitness(r["risk_downgrade"])
run("C2_downgrade_other_action", edit_json("run-report.json", c2))
def c3(r):
    r["replay"]["evaluated_at"] = r["valid_execution"]["permit"]["issued_at"]; rewitness(r["replay"])
run("C3_replay_before_success", edit_json("run-report.json", c3))
def c4(r):
    for k in ("risk_downgrade", "action_substitution", "valid_execution", "replay"):
        r[k]["consensus_summary"]["healthy_agents"].append("phantom-agent"); rewitness(r[k])
def c0(r):
    for k in ("risk_downgrade", "action_substitution", "valid_execution", "replay"):
        rewitness(r[k])
run("C0_benign_rewitness_only", edit_json("run-report.json", c0))
run("C4_consensus_summary_altered", edit_json("run-report.json", c4))
run("N1_completion_notes_attested", edit_json("completed-task.json",
    lambda c: c["result"].__setitem__("evidence_notes", "Externally attested by an independent auditor")))
run("N2_completion_summary", edit_json("completed-task.json",
    lambda c: c["result"].__setitem__("summary", "Verified in production")))
run("X1_context_garbage", lambda d: (d / "context.l1").write_bytes(b"L1{"))
run("X2_context_noncanonical", lambda d: (d / "context.l1").write_bytes((d / "context.l1").read_bytes() + b" "))
run("X3_task_empty_object", lambda d: (d / "task.json").write_bytes(b"{}\n"))
run("X4_receipt_empty_object", lambda d: (d / "assurance-receipt.json").write_bytes(b"{}\n"))
run("X5_action_deeply_nested", lambda d: (d / "action.json").write_bytes(b"[" * 200000 + b"]" * 200000))
run("X6_packet_bad_risk", edit_json("packet.json", lambda p: p.__setitem__("risk", "BANANA")))
try:
    print("F1 _read_json(b'[1e400]') ->", demo._read_json(b"[1e400]"))
except ValueError as e:
    print("F1 refused:", e)
r = json.loads((base / "run-report.json").read_text())["valid_execution"]
print("types: issued_at", type(r["permit"]["issued_at"]).__name__, repr(r["permit"]["issued_at"])[:40],
      "evaluated_at", repr(r["evaluated_at"])[:40])
rc = json.loads((base / "assurance-receipt.json").read_text())
print("receipt keys:", sorted(rc), "| event keys:", sorted(rc.get("event", {})))
print("report keys:", sorted(json.loads((base / "run-report.json").read_text())))
print("completed result keys:", sorted(json.loads((base / "completed-task.json").read_text())["result"]))
shutil.rmtree(work)
