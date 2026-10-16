"""Differential check: packaged JSON Schema vs inspected normalization behavior.

This is a source-equivalent model, not an import of the upstream package.
The schema structure was fetched from the repository's inspected master commit and reconstructed in readable formatting.
"""
from __future__ import annotations
import copy, hashlib, hmac, json, math, re
from pathlib import Path
from typing import Any, Mapping
import jsonschema

ROOT = Path(__file__).resolve().parent
SECRET = b"fixture-only-signing-key-not-for-production"

class WireError(ValueError): pass

def canonical_bytes(v: Any) -> bytes:
    return json.dumps(v, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
def sha(v: Any) -> str: return hashlib.sha256(canonical_bytes(v)).hexdigest()

def base_body() -> dict[str, Any]:
    return {
      "schema_version":"0.1", "receipt_id":"urn:uuid:fixture-0001", "issued_at":"2026-10-16T00:00:00Z",
      "runtime":{"name":"fixture-runtime","status":"SCAFFOLD"},
      "policy":{"id":"fixture.policy","version":"1","sha256":"a"*64},
      "event":{"event_id":"event-1","phase":"output","subject":{"name":"text:output","sha256":"b"*64},"replayable":False},
      "decision":"ALLOW",
      "findings":[{"id":"TEST:FINDING:001","title":"False","description":"Fixture finding","severity":"MEDIUM","requested_disposition":"ALLOW","effective_disposition":"ALLOW","claim_status":"ACTIVE","deterministic":True,"evaluator":"test/1","confidence":1.0,"evidence":["17"],"controls":[{"framework":"False","control_id":"CTRL-1","title":"False","url":"False"}],"status_basis":"Fixture-only basis"}],
      "metrics":{}, "limitations":["fixture-only"], "lineage":{"trace_id":"trace-fixture","previous_receipt_sha256":None}
    }

def seal(body: Mapping[str, Any], key: bytes|None) -> dict[str, Any]:
    payload=copy.deepcopy(dict(body)); digest=sha(body)
    signature = hmac.new(key,digest.encode("ascii"),hashlib.sha256).hexdigest() if key else None
    payload["integrity"]={"algorithm":"sha256","canonicalization":"lycheetah-json-v1","digest":digest,"seal":({"algorithm":"hmac-sha256","key_id":"fixture-key","value":signature} if key else None)}
    return payload

def normalized_body(raw: Mapping[str, Any]) -> dict[str, Any]:
    # Mirrors targeted fields as parsed by receipt.py / models.py / nested model to_dict().
    finding_out=[]
    for f in raw["findings"]:
        controls=[]
        for c in f["controls"]:
            item={"framework":str(c["framework"]),"control_id":str(c["control_id"]),"title":str(c["title"])}
            url=str(c.get("url",""))
            if url: item["url"]=url
            controls.append(item)
        fo={"id":str(f["id"]),"title":str(f["title"]),"description":str(f["description"]),"severity":f["severity"],"requested_disposition":f["requested_disposition"],"effective_disposition":f["effective_disposition"],"claim_status":f["claim_status"],"deterministic":f["deterministic"],"evaluator":str(f["evaluator"]),"confidence":float(f["confidence"]),"evidence":[str(x) for x in f["evidence"]],"controls":controls}
        if f.get("status_basis"): fo["status_basis"]=str(f["status_basis"])
        if f.get("cap_reason"): fo["cap_reason"]=f["cap_reason"]
        finding_out.append(fo)
    out={"schema_version":str(raw["schema_version"]),"receipt_id":str(raw["receipt_id"]),"issued_at":str(raw["issued_at"]),"runtime":copy.deepcopy(raw["runtime"]),"policy":copy.deepcopy(raw["policy"]),"event":copy.deepcopy(raw["event"]),"decision":raw["decision"],"findings":finding_out,"metrics":copy.deepcopy(raw["metrics"]),"limitations":[str(x) for x in raw["limitations"]],"lineage":copy.deepcopy(raw["lineage"])}
    return out

def baseline_accepts(raw: Mapping[str, Any], key: bytes|None) -> tuple[bool,bool,bool]:
    # Actual Finding.from_dict rejects unknown fields; ControlReference.from_dict does not.
    finding_fields={"id","title","description","severity","requested_disposition","effective_disposition","claim_status","deterministic","evaluator","confidence","evidence","controls","status_basis","cap_reason"}
    shape_ok = not any(not isinstance(f, Mapping) or set(f)-finding_fields for f in raw.get("findings", []))
    try:
        body=normalized_body(raw)
        digest_ok=sha(body)==raw.get("integrity",{}).get("digest")
    except Exception:
        digest_ok=False
    integrity=raw.get("integrity",{})
    seal=integrity.get("seal") if isinstance(integrity,Mapping) else None
    hmac_ok=False
    if key and isinstance(seal,Mapping) and seal.get("algorithm")=="hmac-sha256":
        expected=hmac.new(key,str(integrity.get("digest","")).encode("ascii"),hashlib.sha256).hexdigest()
        hmac_ok=hmac.compare_digest(expected,str(seal.get("value","")))
    parser_accepts = shape_ok and digest_ok and (key is None or hmac_ok)
    return digest_ok, parser_accepts, hmac_ok

def strict_candidate_accepts(raw: Mapping[str, Any]) -> tuple[bool,str]:
    try:
        if not isinstance(raw.get("schema_version"),str): raise WireError("schema_version must be string")
        if raw.get("schema_version")!="0.1": raise WireError("unsupported schema version")
        if not isinstance(raw.get("receipt_id"),str) or not raw["receipt_id"]: raise WireError("receipt_id must be non-empty string")
        if not isinstance(raw.get("issued_at"),str): raise WireError("issued_at must be string")
        policy=raw.get("policy", {})
        if not isinstance(policy, Mapping) or not isinstance(policy.get("sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", policy["sha256"]): raise WireError("policy.sha256 must be 64 lowercase hexadecimal characters")
        finding_fields={"id","title","description","severity","requested_disposition","effective_disposition","claim_status","deterministic","evaluator","confidence","evidence","controls","status_basis","cap_reason"}
        for f in raw.get("findings",[]):
            if set(f)-finding_fields: raise WireError("finding contains unknown fields")
            for name in ("id","title","description","evaluator"):
                if not isinstance(f.get(name),str): raise WireError(f"finding.{name} must be string")
            confidence=f.get("confidence")
            if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(float(confidence)): raise WireError("finding.confidence must be finite number")
            if not isinstance(f.get("evidence"),list) or any(not isinstance(x,str) for x in f.get("evidence",[])): raise WireError("finding.evidence must be string array")
            for c in f.get("controls",[]):
                if not isinstance(c,Mapping): raise WireError("control must be object")
                for name in ("framework","control_id","title"):
                    if not isinstance(c.get(name),str): raise WireError(f"control.{name} must be string")
                if "url" in c and not isinstance(c["url"],str): raise WireError("control.url must be string")
                if set(c)-{"framework","control_id","title","url"}: raise WireError("control contains unknown fields")
        return True,"accepted"
    except (KeyError,TypeError,ValueError) as e: return False,str(e)

def schema_accepts(raw: Mapping[str,Any], validator: jsonschema.Draft202012Validator) -> tuple[bool,str|None]:
    errors=list(validator.iter_errors(raw))
    return (not errors, None if not errors else errors[0].message)

def mutate(raw: Mapping[str,Any], case: str) -> dict[str,Any]:
    out=copy.deepcopy(dict(raw))
    if case=="schema_version_number": out["schema_version"]=0.1
    elif case=="finding_title_boolean": out["findings"][0]["title"]=False
    elif case=="confidence_boolean": out["findings"][0]["confidence"]=True
    elif case=="evidence_integer": out["findings"][0]["evidence"][0]=17
    elif case=="control_title_boolean": out["findings"][0]["controls"][0]["title"]=False
    elif case=="control_url_boolean": out["findings"][0]["controls"][0]["url"]=False
    elif case=="control_framework_number": out["findings"][0]["controls"][0]["framework"]=False
    elif case=="control_unknown_field": out["findings"][0]["controls"][0]["extension"]="unexpected"
    elif case=="finding_unknown_field": out["findings"][0]["extension"]="unexpected"
    elif case=="policy_digest_invalid": out["policy"]["sha256"]="not-a-digest"
    else: raise ValueError(case)
    return out
