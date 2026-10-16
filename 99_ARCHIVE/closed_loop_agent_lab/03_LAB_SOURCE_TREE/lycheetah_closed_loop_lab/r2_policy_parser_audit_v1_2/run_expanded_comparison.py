"""Compare the prior source-equivalent string-coercion behavior with v1.2."""
from __future__ import annotations
import json
from pathlib import Path
from source_equivalent_baseline import TextRule as BaselineRule
from strict_candidate import TextRule as CandidateRule, PolicyError

OUT = Path(__file__).resolve().parent
BASE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_VALUES = [None, True, 17, 3.5, ["x"], {"x": "y"}]
FIELDS = ("id", "pattern", "title", "description", "status_basis")
rows=[]
for field in FIELDS:
  for value in BAD_VALUES:
    data=dict(BASE); data[field]=value
    row={"field":field,"value_repr":repr(value)}
    for label, parser in (("source_equivalent_baseline",BaselineRule),("strict_candidate_v1_2",CandidateRule)):
      try:
        parser.from_dict(data); row[label]="ACCEPT"
      except Exception as exc:
        row[label]=f"REJECT:{type(exc).__name__}"
    rows.append(row)
# Valid field/default probes
valid_payloads=[dict(BASE),{**BASE,"title":"Title","description":"Description","status_basis":"Approved basis"}]
valid=[]
for payload in valid_payloads:
  for label,parser in (("source_equivalent_baseline",BaselineRule),("strict_candidate_v1_2",CandidateRule)):
    try:
      obj=parser.from_dict(payload)
      valid.append({"payload":payload,"parser":label,"status":"ACCEPT","title":obj.title,"description":obj.description,"status_basis":obj.status_basis})
    except Exception as exc:
      valid.append({"payload":payload,"parser":label,"status":f"REJECT:{type(exc).__name__}"})
result={
  "status":"SOURCE_EQUIVALENT_FIXTURE_NOT_UPSTREAM_INTEGRATION",
  "source_url":"https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/policy.py",
  "source_git_blob_sha":"913006991327ac40bf34e96fce591ca100334ca9",
  "invalid_type_cases":len(rows),
  "baseline_accepted_invalid_types":sum(x["source_equivalent_baseline"]=="ACCEPT" for x in rows),
  "candidate_rejected_invalid_types":sum(x["strict_candidate_v1_2"].startswith("REJECT:") for x in rows),
  "cases":rows,
  "valid_compatibility_cases":valid,
  "baseline_invalid_accept_rate":sum(x["source_equivalent_baseline"]=="ACCEPT" for x in rows)/len(rows),
  "candidate_invalid_reject_rate":sum(x["strict_candidate_v1_2"].startswith("REJECT:") for x in rows)/len(rows),
}
(OUT/"comparison_results_v1_2.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:result[k] for k in ("status","invalid_type_cases","baseline_accepted_invalid_types","candidate_rejected_invalid_types","baseline_invalid_accept_rate","candidate_invalid_reject_rate")},indent=2))
