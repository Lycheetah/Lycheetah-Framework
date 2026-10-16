#!/usr/bin/env python3
"""Read-only compatibility inventory for proposed strict assurance contracts.

Run from the research pack against a clean Lycheetah-Framework checkout after
installing its test dependencies. The script does not edit repository files.
It uses the checkout's *current* parser plus candidate schemas/guards to show
which discovered or explicitly supplied records would need review.
"""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema

HERE = Path(__file__).resolve().parent
POLICY_CURRENT_SNAPSHOT = json.loads((HERE / "policy.schema.current-snapshot.json").read_text(encoding="utf-8"))
RECEIPT_CURRENT_SNAPSHOT = json.loads((HERE / "receipt.schema.current-snapshot.json").read_text(encoding="utf-8"))
POLICY_CANDIDATE = json.loads((HERE / "policy.schema.strict-candidate.json").read_text(encoding="utf-8"))
RECEIPT_CANDIDATE = json.loads((HERE / "receipt.schema.strict-candidate.json").read_text(encoding="utf-8"))
BASE_COMMIT = "8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65"
BASE_BLOBS = {
    "lycheetah/assurance/models.py": "12895f2a7d3e66f4584040713dad131c154b80f0",
    "lycheetah/assurance/receipt.py": "91f9ec4d7177480d259240a0899b8b54aff6f0e5",
    "lycheetah/assurance/policy.py": "913006991327ac40bf34e96fce591ca100334ca9",
    "lycheetah/assurance/schemas/policy.schema.json": "669f21b9f2c800f15e93116d1b9cbeb1bd84e128",
    "lycheetah/assurance/schemas/receipt.schema.json": "eeb1306040a17ce530f42f74966b185fece9a41e",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def policy_wire_issues(data: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["policy root is not an object"]
    text = data.get("text", {})
    if not isinstance(text, dict):
        return ["policy.text is not an object"]
    rules = text.get("rules", [])
    if not isinstance(rules, list):
        return ["policy.text.rules is not an array"]
    for i, rule in enumerate(rules):
        path = f"text.rules[{i}]"
        if not isinstance(rule, dict):
            issues.append(f"{path} is not an object")
            continue
        for key in ("id", "pattern"):
            if key in rule and not isinstance(rule[key], str):
                issues.append(f"{path}.{key} must be a string")
        if "id" not in rule:
            issues.append(f"{path}.id is missing")
        if "pattern" not in rule:
            issues.append(f"{path}.pattern is missing")
        for key in ("title", "description", "status_basis"):
            if key in rule and not isinstance(rule[key], str):
                issues.append(f"{path}.{key} must be a string")
    return issues


def receipt_wire_issues(data: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["receipt root is not an object"]
    if not isinstance(data.get("schema_version"), str):
        issues.append("schema_version must be a string")
    policy = data.get("policy")
    if isinstance(policy, dict):
        digest = policy.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            issues.append("policy.sha256 must be 64 lowercase hexadecimal characters")
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        issues.append("findings must be an array")
        findings = []
    required_finding = {
        "id", "title", "description", "severity", "requested_disposition",
        "effective_disposition", "claim_status", "deterministic", "evaluator",
        "confidence", "evidence", "controls",
    }
    allowed_finding = required_finding | {"status_basis", "cap_reason"}
    for i, finding in enumerate(findings):
        path = f"findings[{i}]"
        if not isinstance(finding, dict):
            issues.append(f"{path} is not an object")
            continue
        for key in sorted(required_finding - set(finding)):
            issues.append(f"{path}.{key} is missing")
        for key in sorted(set(finding) - allowed_finding):
            issues.append(f"{path}.{key} is unknown")
        for key in ("id", "title", "description", "evaluator"):
            if key in finding and not isinstance(finding[key], str):
                issues.append(f"{path}.{key} must be a string")
        if "status_basis" in finding and not isinstance(finding["status_basis"], str):
            issues.append(f"{path}.status_basis must be a string")
        if "cap_reason" in finding and not isinstance(finding.get("cap_reason"), str):
            issues.append(f"{path}.cap_reason must be a string when present")
        confidence = finding.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(float(confidence)):
            issues.append(f"{path}.confidence must be a finite number")
        evidence = finding.get("evidence")
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            issues.append(f"{path}.evidence must be an array of strings")
        controls = finding.get("controls")
        if not isinstance(controls, list):
            issues.append(f"{path}.controls must be an array")
            continue
        for j, control in enumerate(controls):
            cpath = f"{path}.controls[{j}]"
            if not isinstance(control, dict):
                issues.append(f"{cpath} is not an object")
                continue
            for key in ("framework", "control_id", "title"):
                if key not in control:
                    issues.append(f"{cpath}.{key} is missing")
                elif not isinstance(control[key], str):
                    issues.append(f"{cpath}.{key} must be a string")
            if "url" in control and not isinstance(control["url"], str):
                issues.append(f"{cpath}.url must be a string")
            for key in sorted(set(control) - {"framework", "control_id", "title", "url"}):
                issues.append(f"{cpath}.{key} is unknown")
    return issues


def _validate(validator: jsonschema.Draft202012Validator, data: Any) -> tuple[bool, list[str]]:
    errors = sorted(validator.iter_errors(data), key=lambda err: list(map(str, err.absolute_path)))
    return not errors, [f"/{'/'.join(str(x) for x in e.absolute_path)}: {e.message}" for e in errors[:30]]


def _git(repo: Path, *args: str) -> str:
    import subprocess
    p = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()


def _blob_sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _assert_clean_base_checkout(repo: Path) -> None:
    head = _git(repo, "rev-parse", "HEAD")
    if head != BASE_COMMIT:
        raise RuntimeError(
            f"compatibility inventory must run against untouched base {BASE_COMMIT}; checkout is {head}. "
            "Use a second clean worktree if patches have already been applied."
        )
    dirty = _git(repo, "status", "--porcelain")
    if dirty:
        raise RuntimeError("compatibility inventory requires a clean, unmodified base checkout; run it before applying patches.")
    for rel, expected in BASE_BLOBS.items():
        p = repo / rel
        if not p.is_file() or _blob_sha(p.read_bytes()) != expected:
            raise RuntimeError(f"source mismatch at {rel}; use the expected clean base and re-inspect changes.")
    for rel, expected in (("lycheetah/assurance/schemas/policy.schema.json", POLICY_CURRENT_SNAPSHOT), ("lycheetah/assurance/schemas/receipt.schema.json", RECEIPT_CURRENT_SNAPSHOT)):
        actual = json.loads((repo / rel).read_text(encoding="utf-8"))
        if actual != expected:
            raise RuntimeError(f"{rel} differs semantically from bundled current-schema snapshot; do not compare mismatched contracts.")


def _import_current_parser(repo: Path):
    sys.path.insert(0, str(repo))
    try:
        from lycheetah.assurance.policy import AssurancePolicy, PolicyError
        from lycheetah.assurance.receipt import AssuranceReceipt, ReceiptError
    except Exception as exc:
        raise RuntimeError(
            "could not import current Lycheetah assurance parsers; run after installing project dependencies"
        ) from exc
    return AssurancePolicy, AssuranceReceipt


def _load_json_records(path: Path, kind: str):
    if path.suffix.lower() == ".jsonl":
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    yield line_no, json.loads(line), None
                except json.JSONDecodeError as exc:
                    yield line_no, None, f"invalid JSON on line {line_no}: {exc}"
    else:
        try:
            yield None, json.loads(path.read_text(encoding="utf-8")), None
        except json.JSONDecodeError as exc:
            yield None, None, f"invalid JSON: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="local checkout of Lycheetah-Framework")
    parser.add_argument("--policy", action="append", default=[], help="policy JSON path; repeatable, relative to repo or absolute")
    parser.add_argument("--receipt", action="append", default=[], help="receipt JSON/JSONL path; repeatable")
    parser.add_argument("--out", type=Path, default=Path("/tmp/lycheetah_migration_compat_v1_6.json"))
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        parser.error(f"not a Git checkout: {repo}")
    try:
        _assert_clean_base_checkout(repo)
    except Exception as exc:
        parser.error(str(exc))
    policy_paths = [Path(x) if Path(x).is_absolute() else repo / x for x in args.policy]
    receipt_paths = [Path(x) if Path(x).is_absolute() else repo / x for x in args.receipt]
    if not args.policy and not args.receipt:
        example_dir = repo / "examples" / "assurance"
        if example_dir.exists():
            policy_paths = sorted(p for p in example_dir.rglob("*policy*.json") if "schema" not in p.parts)
            receipt_paths = sorted(p for p in example_dir.rglob("*receipt*.json") if "schema" not in p.parts)
            receipt_paths += sorted(p for p in example_dir.rglob("*receipt*.jsonl") if "schema" not in p.parts)
    for path in policy_paths + receipt_paths:
        if not path.is_file():
            parser.error(f"input file does not exist: {path}")
    if not policy_paths and not receipt_paths:
        parser.error("no policy or receipt files found; supply --policy and/or --receipt")
    try:
        AssurancePolicy, AssuranceReceipt = _import_current_parser(repo)
    except RuntimeError as exc:
        parser.error(str(exc))
    # Use bundled semantic snapshots to keep the comparator immutable and to
    # prevent accidentally treating already-replaced upstream schemas as "old".
    current_policy_schema = POLICY_CURRENT_SNAPSHOT
    current_receipt_schema = RECEIPT_CURRENT_SNAPSHOT
    p_current = jsonschema.Draft202012Validator(current_policy_schema)
    r_current = jsonschema.Draft202012Validator(current_receipt_schema)
    p_candidate = jsonschema.Draft202012Validator(POLICY_CANDIDATE)
    r_candidate = jsonschema.Draft202012Validator(RECEIPT_CANDIDATE)
    report: dict[str, Any] = {"tool": "lycheetah_migration_compat_v1.6", "read_only": True, "base_commit": BASE_COMMIT, "records": []}

    def analyze(path: Path, kind: str):
        for line_no, data, parse_error in _load_json_records(path, kind):
            rec: dict[str, Any] = {"path": str(path), "line": line_no, "kind": kind}
            if parse_error:
                rec.update({"json_valid": False, "parse_error": parse_error})
                report["records"].append(rec)
                continue
            rec["json_valid"] = True
            current_schema = p_current if kind == "policy" else r_current
            candidate_schema = p_candidate if kind == "policy" else r_candidate
            current_schema_ok, current_schema_errors = _validate(current_schema, data)
            candidate_schema_ok, candidate_schema_errors = _validate(candidate_schema, data)
            rec["current_schema_accepts"], rec["current_schema_errors"] = current_schema_ok, current_schema_errors
            rec["candidate_schema_accepts"], rec["candidate_schema_errors"] = candidate_schema_ok, candidate_schema_errors
            try:
                if kind == "policy":
                    AssurancePolicy.from_dict(data)
                else:
                    AssuranceReceipt.from_dict(data)
                current_parser_ok, current_parser_error = True, None
            except Exception as exc:
                current_parser_ok, current_parser_error = False, f"{type(exc).__name__}: {exc}"
            rec["current_parser_accepts"], rec["current_parser_error"] = current_parser_ok, current_parser_error
            wire_issues = policy_wire_issues(data) if kind == "policy" else receipt_wire_issues(data)
            rec["candidate_wire_guard_issues"] = wire_issues
            rec["candidate_parser_accepts"] = bool(candidate_schema_ok and current_parser_ok and not wire_issues)
            rec["needs_review"] = bool(current_parser_ok and not rec["candidate_parser_accepts"])
            report["records"].append(rec)

    for path in policy_paths:
        analyze(path, "policy")
    for path in receipt_paths:
        analyze(path, "receipt")
    rows = report["records"]
    report["summary"] = {
        "count": len(rows),
        "current_parser_accepts": sum(bool(r.get("current_parser_accepts")) for r in rows),
        "candidate_parser_accepts": sum(bool(r.get("candidate_parser_accepts")) for r in rows),
        "needs_review": sum(bool(r.get("needs_review")) for r in rows),
        "schema_disagreements": sum(bool(r.get("current_schema_accepts") != r.get("current_parser_accepts")) for r in rows),
    }
    out = args.out.resolve()
    try:
        out.relative_to(repo)
    except ValueError:
        pass
    else:
        parser.error("report output must be outside the repository so the scan remains read-only")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Read-only input scan complete. Report written to {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
