from __future__ import annotations
import copy,json
from pathlib import Path
from schema_parser_parity import *
ROOT=Path(__file__).resolve().parent
current=jsonschema.Draft202012Validator(json.loads((ROOT/"receipt.schema.json").read_text()))
strict_schema=jsonschema.Draft202012Validator(json.loads((ROOT/"receipt.schema.strict-candidate.json").read_text()))
wire_cases=[("schema_version_number","schema_version string -> JSON number"),("finding_title_boolean","finding.title string -> Boolean"),("confidence_boolean","finding.confidence 1.0 -> Boolean true"),("evidence_integer","finding.evidence string -> integer"),("control_title_boolean","control.title string -> Boolean"),("control_url_boolean","control.url string -> Boolean"),("control_framework_number","control.framework string -> Boolean"),("control_unknown_field","extra nested control property")]
base=seal(base_body(),None); signed=seal(base_body(),SECRET)
valid_schema=schema_accepts(base,current)[0]; valid_unsigned=baseline_accepts(base,None)[1]; valid_signed=baseline_accepts(signed,SECRET)[1] and baseline_accepts(signed,SECRET)[2]
rows=[]
for name,desc in wire_cases:
 for auth,payload,key in (("unsigned",base,None),("hmac-sealed",signed,SECRET)):
  bad=mutate(payload,name); digest_ok,baseline_ok,hmac_ok=baseline_accepts(bad,key); strict_ok,strict_reason=strict_candidate_accepts(bad); current_ok,current_reason=schema_accepts(bad,current); strict_schema_ok,strict_schema_reason=schema_accepts(bad,strict_schema)
  rows.append({"case":name,"kind":"wire_mutation_preserving_normalized_body","description":desc,"authentication":auth,"normalized_digest_ok":digest_ok,"source_equivalent_parser_accepts":baseline_ok,"hmac_verifies":hmac_ok if key else None,"current_schema_accepts":current_ok,"strict_parser_candidate_accepts":strict_ok,"strict_candidate_schema_accepts":strict_schema_ok,"strict_parser_reason":strict_reason,"current_schema_reason":current_reason,"strict_schema_reason":strict_schema_reason})
for kind, mutate_body in (("policy_digest_invalid",lambda body: body["policy"].update(sha256="not-a-digest")),("finding_unknown_field",lambda body: body["findings"][0].update(extension="unexpected"))):
 for auth,key in (("unsigned",None),("hmac-sealed",SECRET)):
  body=base_body(); mutate_body(body); issued=seal(body,key); digest_ok,baseline_ok,hmac_ok=baseline_accepts(issued,key); strict_ok,strict_reason=strict_candidate_accepts(issued); current_ok,current_reason=schema_accepts(issued,current); strict_schema_ok,strict_schema_reason=schema_accepts(issued,strict_schema)
  rows.append({"case":kind,"kind":"digest_consistent_malformed_issued_record","description":"issuer creates a self-consistent record with malformed schema value","authentication":auth,"normalized_digest_ok":digest_ok,"source_equivalent_parser_accepts":baseline_ok,"hmac_verifies":hmac_ok if key else None,"current_schema_accepts":current_ok,"strict_parser_candidate_accepts":strict_ok,"strict_candidate_schema_accepts":strict_schema_ok,"strict_parser_reason":strict_reason,"current_schema_reason":current_reason,"strict_schema_reason":strict_schema_reason})
results={"status":"SOURCE_EQUIVALENT_DIFFERENTIAL_ONLY","repository_commit":"8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65","source_schema_blob_sha":"eeb1306040a17ce530f42f74966b185fece9a41e","schema_fixture_valid":valid_schema,"baseline_unsigned_valid":valid_unsigned,"baseline_signed_digest_and_hmac_valid":valid_signed,"case_count":len(rows),"source_equivalent_parser_accepts":sum(r["source_equivalent_parser_accepts"] for r in rows),"current_schema_rejects":sum(not r["current_schema_accepts"] for r in rows),"strict_parser_rejects":sum(not r["strict_parser_candidate_accepts"] for r in rows),"strict_candidate_schema_rejects":sum(not r["strict_candidate_schema_accepts"] for r in rows),"original_hmac_still_verifies_after_normalizable_mutation":sum(r["kind"]=="wire_mutation_preserving_normalized_body" and r["hmac_verifies"] is True for r in rows),"rows":rows}
(ROOT/"differential_results.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps({k:v for k,v in results.items() if k!="rows"},indent=2))
assert valid_schema and valid_unsigned and valid_signed
assert sum(r["source_equivalent_parser_accepts"] for r in rows)==18
assert all(not r["strict_parser_candidate_accepts"] for r in rows)
assert all(not r["strict_candidate_schema_accepts"] for r in rows)
