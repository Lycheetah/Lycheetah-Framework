"""Reproduce malformed-type comparison against a source-equivalent fixture."""
import csv, json
from pathlib import Path
from baseline_fixture import TextRule as LegacyRule
from policy_parser_candidate import TextRule as CandidateRule
OUT = Path(__file__).resolve().parent
BASE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_VALUES = [None, True, 17, 3.5, ["ordinary"], {"ordinary": "value"}]
FIELDS = ("id", "pattern", "title", "description")
rows=[]
for field in FIELDS:
    for value in BAD_VALUES:
        data=dict(BASE); data[field]=value
        row={"field":field,"value_repr":repr(value)}
        for label, parser in (("source_equivalent_baseline",LegacyRule),("strict_candidate",CandidateRule)):
            try: parser.from_dict(data); row[label]="ACCEPT"
            except Exception as exc: row[label]="REJECT:"+type(exc).__name__
        rows.append(row)
result={"status":"SOURCE_EQUIVALENT_FIXTURE_NOT_UPSTREAM_INTEGRATION","source_url":"https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/policy.py","source_git_blob_sha":"913006991327ac40bf34e96fce591ca100334ca9","invalid_type_cases":len(rows),"baseline_accepted_invalid_types":sum(r["source_equivalent_baseline"]=="ACCEPT" for r in rows),"candidate_rejected_invalid_types":sum(r["strict_candidate"].startswith("REJECT:") for r in rows),"cases":rows}
(OUT/"comparison_results.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
with (OUT/"comparison_results.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(json.dumps({k:result[k] for k in ("status","invalid_type_cases","baseline_accepted_invalid_types","candidate_rejected_invalid_types")},indent=2))
