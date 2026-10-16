"""Generate the source-equivalent wire-type normalization comparison."""
from __future__ import annotations
import json
from pathlib import Path
from source_equivalent_wire_fixture import (
    WireError, baseline_control_reference, baseline_finding, baseline_receipt_parse,
    canonical_sha256, strict_control_reference, strict_finding, strict_receipt_parse,
)

OUT = Path(__file__).resolve().parent

body = {"schema_version":"0.1", "receipt_id":"urn:uuid:fixture", "issued_at":"2026-10-16T00:00:00Z", "runtime":{"name":"fixture"}}
receipt_valid = {**body, "integrity":{"digest":canonical_sha256(body)}}
receipt_mut = {**receipt_valid, "schema_version":0.1}

cases=[]
def evaluate(name, baseline_fn, candidate_fn, valid, mutated):
    try:
        base_valid=baseline_fn(valid)
        base_mut=baseline_fn(mutated)
        baseline_accepted=True
        normalized_equal=(base_valid==base_mut)
    except Exception as exc:
        baseline_accepted=False; normalized_equal=False; baseline_error=f"{type(exc).__name__}: {exc}"
    try:
        candidate_fn(mutated)
        candidate_rejected=False; candidate_error=None
    except Exception as exc:
        candidate_rejected=True; candidate_error=f"{type(exc).__name__}: {exc}"
    cases.append({"case":name,"baseline_accepts_mutation":baseline_accepted,"mutation_normalizes_to_same_value":normalized_equal,"strict_candidate_rejects_mutation":candidate_rejected,"candidate_error":candidate_error})

evaluate("receipt schema_version string-to-number",baseline_receipt_parse,strict_receipt_parse,receipt_valid,receipt_mut)
control_valid={"framework":"F","control_id":"X-1","title":"False","url":""}
control_mut={**control_valid,"title":False}
evaluate("ControlReference title string-to-boolean",baseline_control_reference,strict_control_reference,control_valid,control_mut)
finding_valid={"id":"TEST:FINDING:001","title":"False","description":"d","evaluator":"e","confidence":1.0,"status_basis":"None","evidence":["17"]}
finding_mut={**finding_valid,"title":False,"confidence":True,"status_basis":None,"evidence":[17]}
evaluate("Finding text/confidence/evidence coercion bundle",baseline_finding,strict_finding,finding_valid,finding_mut)
# Individual finding type transformations to diagnose which field drives normalization.
for name, key, valid_value, bad_value in [
 ("Finding title string-to-boolean","title","False",False),
 ("Finding confidence float-to-boolean","confidence",1.0,True),
 ("Finding status_basis string-to-null","status_basis","None",None),
 ("Finding evidence string-to-integer","evidence",["17"],[17]),
 ("Finding evaluator string-to-integer","evaluator","42",42),
]:
 v={**finding_valid,key:valid_value}; m={**finding_valid,key:bad_value}
 evaluate(name,baseline_finding,strict_finding,v,m)
result={
 "status":"SOURCE_EQUIVALENT_FIXTURE_NOT_UPSTREAM_PACKAGE_TEST",
 "inspected_commit":"8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65",
 "source_blobs":{"models.py":"12895f2a7d3e66f4584040713dad131c154b80f0","receipt.py":"91f9ec4d7177480d259240a0899b8b54aff6f0e5"},
 "cases":cases,
 "mutations_accepted_and_normalized":sum(c["baseline_accepts_mutation"] and c["mutation_normalizes_to_same_value"] for c in cases),
 "strict_rejections":sum(c["strict_candidate_rejects_mutation"] for c in cases),
 "case_count":len(cases),
}
(OUT/"wire_type_results_v1_3.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ("status","case_count","mutations_accepted_and_normalized","strict_rejections")},indent=2))
