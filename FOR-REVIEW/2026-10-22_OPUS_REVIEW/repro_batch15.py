"""Batch 15 repro (RV16): SXP-L authority bridge, the eight inherited findings, and proposal 03.

Usage: python3 -B repro_batch15.py <framework-root> [<runtime-dir>]

Runs the inherited audit (audit_known_limitations.run_probes) against <runtime-dir>
(default: the frozen v2.0 baseline runtime under <root>), then probes the authority
bridge with cases the audit does not cover. Point <runtime-dir> at a scratch copy
carrying a candidate patch to compare arms. Never writes to <root>; prints one JSON
line per probe, keyed by "id". Host grants below are synthetic fixtures.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SXPL = ROOT / "03_LAMAGUE_L1" / "26_SXP_L_RESEARCH"
RUNTIME = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else SXPL / "v2.0/baseline/runtime"

spec = importlib.util.spec_from_file_location("sxpl_audit_probe", SXPL / "audit_known_limitations.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)          # inserts the frozen runtime on sys.path ...
sys.path.insert(0, str(RUNTIME))        # ... so the arm under test goes in front of it

from authority_bridge import inspect    # noqa: E402
from authz import grant_claims, sign_fixture  # noqa: E402
from dialogue10 import parse_document   # noqa: E402
from sxpl_v03 import SXPError           # noqa: E402

KEY = b"local-synthetic-not-a-production-key"
SCOPE = "ti bakumo tavona gonape darafa dimotu tesavo devora"   # publish_post on darafa


def emit(pid, **data):
    print(json.dumps({"id": pid, **data}, ensure_ascii=False))


def doc(turns):
    """turns: [(speaker, addressee, [lines])]"""
    out = ["diala 1.0", "persona elena", "persona agena"]
    for speaker, addressee, lines in turns:
        out += [f"tura {speaker} to {addressee}", *lines, "enda"]
    return parse_document("\n".join(out) + "\n")


def bridge(turns, granted=True):
    try:
        d = doc(turns)
    except SXPError as error:
        return {"parse_refused": str(error)}
    events = [sign_fixture(grant_claims("probe_grant", "elena", "agena", "publish_post", "darafa", 100, 200), KEY)]
    r = inspect(d, {"grantee": "agena", "operation": "publish_post", "resource": "darafa"},
                events if granted else [], {"elena": KEY}, {"elena": {"darafa"}}, now=150)
    out = {"policy_allowed": r["policy"]["allowed"], "review_advised": r["review_advised"],
           "reported": [(b["id"], b["kind"], b["speaker"]) for b in r["reported_boundaries"]]}
    extra = {k: v for k, v in r.items() if k not in ("policy", "execution_performed", "reports", "scope_reports",
                                                     "reported_boundaries", "review_advised", "explanation")}
    if extra:
        out["extra"] = {k: [(b.get("id"), b.get("kind")) for b in v] if isinstance(v, list) else v
                        for k, v in extra.items()}
    return out


emit("PROVENANCE", runtime=str(RUNTIME), frozen=RUNTIME == (SXPL / "v2.0/baseline/runtime").resolve())

findings = audit.run_probes()["findings"]
emit("A0 the eight inherited findings", cases={f["id"]: f["status"] for f in findings})

E = lambda root: f"mi {root} {SCOPE}"   # noqa: E731
emit("B1 every speech act in scope, alone", cases={
    root: bridge([("elena", "agena", [f"lina u1 ^ {E(root)}"])])
    for root in ("domera", "resama", "nelora", "revona", "dalora", "periva", "pekora", "tinora")})

emit("B2 control: no boundary spoken", **bridge([("elena", "agena", ["lina u1 ^ mi liva ti devora"])]))
emit("B3 control: boundary spoken but host policy denies (nothing to review)",
     **bridge([("elena", "agena", [f"lina u1 ^ {E('nelora')}"])], granted=False))

emit("C1 the grantee repairs the owner's refusal (cross-speaker)", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('resama')}"]),
    ("agena", "elena", [f"lina u2 ^ {E('dalora')}", "repara u1 u2"])]))
emit("C2 the owner repairs a refusal into an unrelated sentence", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('resama')}", "lina u2 ^ mi liva ti devora", "repara u1 u2"])]))
emit("C3 the owner repairs a revocation into a grant report", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('revona')}", f"lina u2 ^ {E('periva')}", "repara u1 u2"])]))
emit("C4 the owner repairs one refusal into another", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('nelora')}", f"lina u2 ^ {E('resama')}", "repara u1 u2"])]))
emit("C5 repair chain onto an already-superseded line (finding 8 shape)", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('nelora')}", f"lina u2 ^ {E('revona')}", "lina u3 ^ mi liva ti devora",
                        "repara u2 u3", "repara u1 u2"])]))
emit("C6 grant report later followed by a revocation, no repair", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('periva')}"]), ("elena", "agena", [f"lina u2 ^ {E('revona')}"])]))
emit("C7 the grantee voices a denial about the owner's resource", **bridge([
    ("agena", "elena", [f"lina u1 ^ {E('nelora')}"])]))
emit("C8 repair declared before its replacement exists (chronology)", **bridge([
    ("elena", "agena", [f"lina u1 ^ {E('resama')}", "repara u1 u2", "lina u2 ^ mi liva ti devora"])]))
emit("C9 repair in the reverse direction (newer line superseded by older)", **bridge([
    ("elena", "agena", [f"lina u1 ^ mi liva ti devora", f"lina u2 ^ {E('resama')}", "repara u2 u1"])]))
