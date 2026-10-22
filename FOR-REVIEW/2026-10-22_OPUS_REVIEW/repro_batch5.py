"""Batch 5 reproductions: policy, receipts and the gateway receipt (RV06).

Run from the repository root (or a HEAD export): python3 FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch5.py
Prints one JSON object. Every probe carries `reproduced`, and a benign control
where one makes sense. Executors here only count calls; nothing touches the OS.
"""
from __future__ import annotations

import copy
import dataclasses
import datetime
import json
import sys
import tempfile
import time
from importlib.resources import files
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import lycheetah  # noqa: E402
from lycheetah.assurance import ActionGateway, AssurancePolicy  # noqa: E402
from lycheetah.assurance.jsonutil import sha256_json  # noqa: E402
from lycheetah.assurance.policy import TextRule  # noqa: E402
from lycheetah.assurance.receipt import AssuranceReceipt, ReceiptError  # noqa: E402

SCOPE = "notes"
SECOND = 1.1  # HEAD's approval ids collide inside one second (see repro_batch4.py)


def _counter(result=None):
    calls = []

    def executor():
        calls.append(1)
        return result if result is not None else {"status": "success"}

    return calls, executor


def _receipt():
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        result = gw.execute({"tool": "notes.write", "path": "r"}, "agent", SCOPE,
                            executor=lambda: {"status": "success"}, approver_id="reviewer")
        return result.receipt


def p01_policy_digest_covers_every_field():
    """The receipt names a policy by digest; every field that changes behaviour must move it."""
    base = AssurancePolicy()
    rule = TextRule("probe.rule", "probe", "Probe", "Probe rule")
    uncovered, errors = [], {}
    for field in dataclasses.fields(AssurancePolicy):
        value = getattr(base, field.name)
        if isinstance(value, bool):
            changed = not value
        elif isinstance(value, (int, float)):
            changed = value + 1
        elif isinstance(value, str):
            changed = value + "-probe"
        elif field.name == "text_rules":
            changed = (*value, rule)
        elif isinstance(value, tuple):
            changed = (*value, "probe_value")
        else:
            errors[field.name] = f"unhandled type {type(value).__name__}"
            continue
        try:
            other = dataclasses.replace(base, **{field.name: changed})
        except Exception as exc:  # a refused value is reported, not hidden
            errors[field.name] = f"{type(exc).__name__}: {exc}"
            continue
        if other.digest == base.digest:
            uncovered.append(field.name)
    return {"fields": len(dataclasses.fields(AssurancePolicy)), "uncovered": uncovered,
            "errors": errors, "reproduced": bool(uncovered)}


def p02_bare_string_list_fields():
    """A bare string where a list belongs must be refused, not split into characters."""
    out = {}
    for label, build in {
        "constructor": lambda: AssurancePolicy(denied_tools="shell"),
        "from_dict": lambda: AssurancePolicy.from_dict(
            {**AssurancePolicy().to_dict(), "denied_tools": "shell"}),
    }.items():
        try:
            out[label] = repr(build().denied_tools)
        except Exception as exc:
            out[label] = f"refused {type(exc).__name__}: {exc}"
    return {**out, "reproduced": any(not v.startswith("refused") for v in out.values())}


def p03_text_rule_field_coercion():
    """Rule fields that are not strings are coerced by str() rather than refused."""
    data = TextRule("probe.rule", "probe", "Probe", "Probe rule").to_dict()
    out = {}
    for field, value in {"id": 5, "pattern": None, "title": None}.items():
        try:
            rule = TextRule.from_dict({**data, field: value})
            out[f"{field}={value!r}"] = (f"accepted rule_id={rule.rule_id!r} "
                                         f"pattern={rule.pattern!r} title={rule.title!r}")
        except Exception as exc:
            out[f"{field}={value!r}"] = f"refused {type(exc).__name__}"
    out["control"] = TextRule.from_dict(data).rule_id
    out["reproduced"] = any(v.startswith("accepted") for k, v in out.items() if k != "control")
    return out


def _schema_errors(data):
    import jsonschema

    schema = json.loads(
        files("lycheetah.assurance").joinpath("schemas", "receipt.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER)
    return sorted(e.message[:70] for e in validator.iter_errors(data))


def p04_verify_versus_published_schema():
    """verify() and the shipped JSON schema must agree; an unsealed digest is recomputable."""
    base = _receipt().to_dict()
    mutations = {
        "control_unchanged": lambda d: None,
        "issued_at_not_a_time": lambda d: d.__setitem__("issued_at", "next tuesday"),
        "lineage_empty": lambda d: d.__setitem__("lineage", {}),
        "previous_digest_not_hex": lambda d: d["lineage"].__setitem__(
            "previous_receipt_sha256", "not-a-digest"),
        "trace_id_not_string": lambda d: d["lineage"].__setitem__("trace_id", 7),
        "event_empty": lambda d: d.__setitem__("event", {}),
        "event_phase_unknown": lambda d: d["event"].__setitem__("phase", "telepathy"),
        "policy_empty": lambda d: d.__setitem__("policy", {}),
        "policy_digest_not_hex": lambda d: d["policy"].__setitem__("sha256", "x"),
    }
    rows, disagreements = {}, []
    for name, mutate in mutations.items():
        data = copy.deepcopy(base)
        mutate(data)
        body = {k: v for k, v in data.items() if k != "integrity"}
        data["integrity"]["digest"] = sha256_json(body)
        schema_valid = not _schema_errors(data)
        try:
            verify_valid = AssuranceReceipt.from_dict(data).verify().valid
        except ReceiptError as exc:
            verify_valid = False
            rows.setdefault("refused_at_load", []).append(f"{name}: {exc}"[:90])
        rows[name] = {"schema_valid": schema_valid, "verify_valid": verify_valid}
        if verify_valid and not schema_valid:
            disagreements.append(name)
    return {**rows, "verify_accepts_schema_rejects": disagreements,
            "reproduced": bool(disagreements)}


def p05_gateway_receipt_drops_runtime_limitations():
    """The gateway records a declared approver but drops the runtime's caveat about it."""
    receipt = _receipt()
    with tempfile.TemporaryDirectory() as d:
        runtime_receipt = ActionGateway.open_local(d).runtime.evaluate_tool(
            "notes.write", {"path": "r"}, scopes=(SCOPE,), human_approved=True)
    approval_caveat = [x for x in runtime_receipt.limitations if "caller-declared" in x]
    return {
        "gateway_limitations": list(receipt.limitations),
        "runtime_limitations": len(runtime_receipt.limitations),
        "gateway_event_human_approved": receipt.event.get("human_approved"),
        "gateway_has_approval_caveat": any("caller-declared" in x for x in receipt.limitations),
        "reproduced": bool(approval_caveat)
        and not any("caller-declared" in x for x in receipt.limitations),
    }


def p06_unrecognised_status_is_recorded_as_failure():
    """'pending' is not a failure. Recording FAILED lets the same side effect run twice."""
    out = {}
    for status in ("pending", "failure"):
        with tempfile.TemporaryDirectory() as d:
            gw = ActionGateway.open_local(d)
            action = {"tool": "payments.charge", "amount": 9, "side_effect": True, "s": status}
            _, first_exec = _counter({"status": status})
            first = gw.execute(action, "agent", SCOPE, executor=first_exec, approver_id="reviewer")
            time.sleep(SECOND)
            calls, executor = _counter()
            retry = gw.execute(action, "agent", SCOPE, executor=executor, approver_id="reviewer")
            out[status] = {"first": f"{first.status}:{first.reason}",
                           "retry": f"{retry.status}:{retry.reason}", "retry_calls": len(calls)}
    out["reproduced"] = out["pending"]["first"].startswith("FAILED")
    return out


def p07_unserialisable_provider_result():
    """The provider ran; its answer cannot be stored. The caller must still get a result."""
    out = {}
    for label, value in {"datetime": datetime.datetime(2026, 10, 22),
                         "nan": float("nan"), "control_str": "ok"}.items():
        with tempfile.TemporaryDirectory() as d:
            gw = ActionGateway.open_local(d)
            gate = gw.propose({"tool": "notes.write", "path": label}, "agent", SCOPE)
            calls, executor = _counter({"status": "success", "value": value})
            try:
                result = gw.dispatch(gate.effect_id, executor)
                outcome = f"{result.status}:{result.reason}"
            except Exception as exc:
                outcome = f"raised {type(exc).__name__}: {exc}"[:90]
            later_calls, later = _counter()
            after = gw.execute({"tool": "notes.write", "path": "after"}, "agent", SCOPE,
                               executor=later)
            out[label] = {"dispatch": outcome, "provider_calls": len(calls),
                          "effect": gw.guard.get_effect(gate.effect_id)["status"],
                          "later": f"{after.status}:{after.reason}"}
    out["reproduced"] = any(v["dispatch"].startswith("raised")
                            for k, v in out.items() if k != "control_str")
    return out


def p08_destructive_tripwire():
    """The static 'Destructive Command Prohibition' is a substring match."""
    variants = {
        "canonical": "rm -rf /",
        "flags_swapped": "rm -fr /",
        "flags_split": "rm -r -f /",
        "double_space": "rm -rf  /",
        "long_flags": "rm --recursive --force /",
        "no_preserve_root": "rm -rf --no-preserve-root /",
        "argv_swapped": ["rm", "-fr", "/"],
        "fork_bomb": ":(){ :|:& };:",
        "fork_bomb_spaced": ":() { :|:& }; :",
    }
    out, missed = {}, []
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        for name, command in variants.items():
            disposition, findings = gw.evaluate_policy(
                {"tool": "ops.run", "command": command}, SCOPE, "agent")
            ids = [f.finding_id for f in findings]
            out[name] = f"{disposition.value}:{','.join(ids) or '-'}"
            if "destructive_command_prohibited" not in ids:
                missed.append(name)
        for name, command in {"control_benign": "rm -rf ./build",
                              "control_prose": "docs say never run rm -rf / on prod"}.items():
            disposition, findings = gw.evaluate_policy(
                {"tool": "notes.write", "text": command}, SCOPE, "agent")
            out[name] = f"{disposition.value}:{','.join(f.finding_id for f in findings) or '-'}"
    return {**out, "missed": missed, "reproduced": bool(missed)}


def p09_secret_at_rest():
    """The receipt redacts sensitive arguments; which durable copies still hold them?"""
    argument, output = "SENTINEL-ARG-7f3a", "SENTINEL-OUT-9c1d"
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        result = gw.execute({"tool": "notes.write", "path": "s", "api_key": argument},
                            "agent", SCOPE, approver_id="reviewer",
                            executor=lambda: {"status": "success", "stdout": f"token={output}"})
        holders = {
            name: sorted(str(p.relative_to(d)) for p in Path(d).rglob("*")
                         if p.is_file() and token.encode() in p.read_bytes())
            for name, token in (("argument", argument), ("provider_output", output))
        }
        receipt_json = result.receipt.to_json() if result.receipt else ""
    return {"status": f"{result.status}:{result.reason}", "files_holding": holders,
            "receipt_has_argument": argument in receipt_json,
            "receipt_has_output": output in receipt_json,
            "reproduced": None}


def p10_non_ascii_digest():
    """verify() must return a verdict for any loaded receipt, not raise."""
    out = {}
    for label, digest in {"non_ascii": "\u00e9" * 64, "control_wrong_hex": "0" * 64}.items():
        data = _receipt().to_dict()
        data["integrity"]["digest"] = digest
        try:
            report = AssuranceReceipt.from_dict(data).verify()
            out[label] = f"valid={report.valid} {list(report.errors)[:1]}"
        except Exception as exc:
            out[label] = f"raised {type(exc).__name__}: {exc}"[:90]
    out["reproduced"] = out["non_ascii"].startswith("raised")
    return out


if __name__ == "__main__":
    probes = {
        "P01_policy_digest_covers_every_field": p01_policy_digest_covers_every_field,
        "P02_bare_string_list_fields": p02_bare_string_list_fields,
        "P03_text_rule_field_coercion": p03_text_rule_field_coercion,
        "P04_verify_versus_published_schema": p04_verify_versus_published_schema,
        "P05_gateway_receipt_drops_runtime_limitations":
            p05_gateway_receipt_drops_runtime_limitations,
        "P06_unrecognised_status_is_recorded_as_failure":
            p06_unrecognised_status_is_recorded_as_failure,
        "P07_unserialisable_provider_result": p07_unserialisable_provider_result,
        "P08_destructive_tripwire": p08_destructive_tripwire,
        "P09_secret_at_rest": p09_secret_at_rest,
        "P10_non_ascii_digest": p10_non_ascii_digest,
    }
    out = {"lycheetah": lycheetah.__file__}
    for name, probe in probes.items():
        try:
            out[name] = probe()
        except Exception as exc:  # a crashing probe is a result, not a pass
            out[name] = {"crashed": f"{type(exc).__name__}: {exc}", "reproduced": None}
    print(json.dumps(out, indent=1, default=str))
