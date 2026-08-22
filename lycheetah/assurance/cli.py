"""Command-line interface for policy checks and Assurance Receipts."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

from .evaluation import (
    EvaluationCorpus,
    EvaluationError,
    EvaluationGate,
    EvaluationReport,
    evaluate_corpus,
)
from .in_toto import to_in_toto_statement
from .models import AssuranceEvent, Disposition, Phase
from .policy import AssurancePolicy, PolicyError, default_policy
from .receipt import AssuranceReceipt, ReceiptError, ReceiptLog
from .regression import RegressionGate, RegressionReport, compare_evaluations
from .runtime import AssuranceRuntime


EXIT_BY_DECISION = {
    Disposition.ALLOW: 0,
    Disposition.REVIEW: 2,
    Disposition.BLOCK: 3,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lycheetah-assure",
        description=(
            "Evaluate agent text or proposed tool actions and emit verifiable "
            "Assurance Receipts. This is a bounded guardrail, not certification."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Evaluate input or output text")
    check.add_argument("text", nargs="?", help="Text to check; reads stdin when omitted")
    check.add_argument("--phase", choices=["input", "output"], default="output")
    _add_evaluation_options(check)

    tool = subparsers.add_parser("tool", help="Evaluate a proposed tool action")
    tool.add_argument("tool_name")
    tool.add_argument("--arguments", default="{}", help="Tool arguments as a JSON object")
    tool.add_argument("--scope", action="append", default=[], help="Requested scope; repeatable")
    tool.add_argument("--side-effect", action="store_true")
    approval = tool.add_mutually_exclusive_group()
    approval.add_argument("--approved", action="store_true", help="Record affirmative human approval")
    approval.add_argument("--denied", action="store_true", help="Record explicit human rejection")
    _add_evaluation_options(tool)

    verify = subparsers.add_parser("verify", help="Verify one receipt or a JSONL receipt chain")
    verify.add_argument("path")
    verify.add_argument(
        "--hmac-key-env",
        help="Environment variable containing the shared HMAC verification secret",
    )
    verify.add_argument("--key-id", help="Key id used by sealed receipts in a JSONL log")
    verify.add_argument(
        "--format",
        choices=["auto", "receipt", "jsonl"],
        default="auto",
        help="Input format; auto treats .jsonl paths as receipt chains",
    )
    verify.add_argument("--json", action="store_true")

    policy = subparsers.add_parser("default-policy", help="Print the built-in policy and digest")
    policy.add_argument("--compact", action="store_true")

    evaluation = subparsers.add_parser(
        "eval",
        help="Evaluate a policy against a labelled JSONL regression corpus",
    )
    evaluation.add_argument("corpus", help="Path to a strict JSONL evaluation corpus")
    evaluation.add_argument("--policy", help="Path to a versioned policy JSON file")
    evaluation.add_argument("--json", action="store_true", help="Print the full report as JSON")
    evaluation.add_argument("--report-file", help="Write the full report JSON to this file")
    evaluation.add_argument(
        "--require-exact-match",
        action="store_true",
        help="Fail the evaluation gate unless every decision matches its label",
    )
    evaluation.add_argument(
        "--max-under-enforcement-rate",
        type=_rate,
        help="Fail when weighted under-enforcement exceeds this value in [0,1]",
    )
    evaluation.add_argument(
        "--max-harmful-allows",
        type=_non_negative_integer,
        help="Fail when expected BLOCK / actual ALLOW cases exceed this count",
    )
    evaluation.add_argument(
        "--max-false-blocks",
        type=_non_negative_integer,
        help="Fail when expected ALLOW / actual BLOCK cases exceed this count",
    )
    evaluation.add_argument(
        "--min-macro-f1",
        type=_rate,
        help="Fail when weighted macro-F1 is below this value in [0,1]",
    )

    verify_evaluation = subparsers.add_parser(
        "verify-eval",
        help="Verify the canonical SHA-256 digest of an evaluation report",
    )
    verify_evaluation.add_argument("path")
    verify_evaluation.add_argument("--json", action="store_true")

    compare = subparsers.add_parser(
        "compare-eval",
        help="Compare candidate and baseline reports for the same corpus",
    )
    compare.add_argument("baseline", help="Trusted baseline evaluation report")
    compare.add_argument("candidate", help="Candidate evaluation report")
    compare.add_argument("--json", action="store_true", help="Print the full report as JSON")
    compare.add_argument("--report-file", help="Write the regression report JSON to this file")
    compare.add_argument(
        "--max-regressed-cases",
        type=_non_negative_integer,
        default=0,
        help="Maximum cases whose labelled correctness may worsen; default 0",
    )
    compare.add_argument(
        "--max-tradeoff-cases",
        type=_non_negative_integer,
        default=0,
        help="Maximum cross-direction REVIEW trade-offs; default 0",
    )
    compare.add_argument(
        "--max-new-under-enforcement",
        type=_non_negative_integer,
        default=0,
        help="Maximum newly under-enforced cases; default 0",
    )
    compare.add_argument(
        "--max-new-harmful-allows",
        type=_non_negative_integer,
        default=0,
        help="Maximum new expected-BLOCK/actual-ALLOW cases; default 0",
    )
    compare.add_argument(
        "--max-new-false-blocks",
        type=_non_negative_integer,
        default=0,
        help="Maximum new expected-ALLOW/actual-BLOCK cases; default 0",
    )
    compare.add_argument(
        "--max-exact-match-rate-drop",
        type=_rate,
        default=0.0,
        help="Maximum exact-match rate drop in [0,1]; default 0",
    )
    compare.add_argument(
        "--max-macro-f1-drop",
        type=_rate,
        default=0.0,
        help="Maximum weighted macro-F1 drop in [0,1]; default 0",
    )

    verify_regression = subparsers.add_parser(
        "verify-regression",
        help="Verify the canonical SHA-256 digest of a regression report",
    )
    verify_regression.add_argument("path")
    verify_regression.add_argument("--json", action="store_true")
    return parser


def _add_evaluation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--policy", help="Path to a versioned policy JSON file")
    parser.add_argument("--json", action="store_true", help="Print the full receipt as JSON")
    parser.add_argument("--in-toto", action="store_true", help="Print an in-toto Statement v1 shape")
    parser.add_argument("--receipt-file", help="Write the full receipt JSON to this file")
    parser.add_argument("--log", help="Append the receipt to a verified JSONL chain")
    parser.add_argument(
        "--hmac-key-env",
        help="Environment variable containing a shared HMAC secret (never pass secrets as CLI args)",
    )
    parser.add_argument("--key-id", help="Identifier recorded with an HMAC seal")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "default-policy":
            policy = default_policy()
            payload = {"policy": policy.to_dict(), "sha256": policy.digest}
            print(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":") if args.compact else None,
                    indent=None if args.compact else 2,
                )
            )
            return 0
        if args.command == "verify":
            return _verify(args)
        if args.command == "eval":
            return _run_evaluation(args)
        if args.command == "verify-eval":
            return _verify_evaluation(args)
        if args.command == "compare-eval":
            return _compare_evaluations(args)
        if args.command == "verify-regression":
            return _verify_regression(args)
        return _evaluate(args)
    except (EvaluationError, PolicyError, ReceiptError, ValueError, OSError) as exc:
        print(f"lycheetah-assure: {exc}", file=sys.stderr)
        return 4


def _evaluate(args: argparse.Namespace) -> int:
    policy = AssurancePolicy.from_json(args.policy) if args.policy else default_policy()
    runtime = AssuranceRuntime(policy)
    if args.command == "check":
        text = args.text
        if text is None:
            text = sys.stdin.read()
        event = AssuranceEvent(phase=Phase(args.phase), content=text)
    else:
        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError as exc:
            raise ValueError(f"--arguments is not valid JSON: {exc}") from exc
        if not isinstance(arguments, dict):
            raise ValueError("--arguments must decode to a JSON object")
        approved = True if args.approved else (False if args.denied else None)
        event = AssuranceEvent(
            phase=Phase.TOOL,
            tool_name=args.tool_name,
            tool_arguments=arguments,
            scopes=tuple(args.scope),
            side_effect=args.side_effect,
            human_approved=approved,
        )

    secret = _secret_from_env(args.hmac_key_env)
    if secret is not None and not args.key_id:
        raise ValueError("--key-id is required with --hmac-key-env")

    previous = None
    log = None
    if args.log:
        log = ReceiptLog(args.log)
        hmac_keys = {args.key_id: secret} if secret is not None else None
        verification = log.verify(hmac_keys)
        if not verification.valid:
            raise ReceiptError(
                "existing receipt log is invalid: " + "; ".join(verification.errors)
            )
        previous = verification.tail_digest

    receipt = runtime.evaluate(
        event,
        previous_receipt_sha256=previous,
        hmac_secret=secret,
        hmac_key_id=args.key_id,
    )
    if log is not None:
        log.append(receipt, hmac_keys)
    if args.receipt_file:
        path = Path(args.receipt_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(receipt.to_json() + "\n", encoding="utf-8")

    if args.in_toto:
        print(json.dumps(to_in_toto_statement(receipt), ensure_ascii=False, indent=2))
    elif args.json:
        print(receipt.to_json())
    else:
        _print_summary(receipt)
    return EXIT_BY_DECISION[receipt.decision]


def _verify(args: argparse.Namespace) -> int:
    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReceiptError(f"cannot read {path}: {exc}") from exc

    secret = _secret_from_env(args.hmac_key_env)
    if args.key_id and secret is None:
        raise ValueError("--key-id requires --hmac-key-env")
    parsed = None
    if args.format != "jsonl" and not (
        args.format == "auto" and path.suffix.lower() == ".jsonl"
    ):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            if args.format == "receipt":
                raise ReceiptError("input is not a JSON receipt")

    if isinstance(parsed, dict):
        receipt = AssuranceReceipt.from_dict(parsed)
        report = receipt.verify(secret)
        payload: dict[str, Any] = {
            "valid": report.valid,
            "digest": report.digest,
            "hmac_authenticated": report.hmac_authenticated,
            "errors": list(report.errors),
            "warnings": list(report.warnings),
        }
    else:
        if args.format == "receipt":
            raise ReceiptError("receipt JSON must contain an object")
        if secret is not None and not args.key_id:
            raise ValueError("--key-id is required to authenticate a JSONL receipt log")
        keys = {args.key_id: secret} if secret is not None and args.key_id else None
        report = ReceiptLog(path).verify(keys)
        payload = {
            "valid": report.valid,
            "receipt_count": report.receipt_count,
            "head_digest": report.head_digest,
            "tail_digest": report.tail_digest,
            "errors": list(report.errors),
            "warnings": list(report.warnings),
        }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("VALID" if payload["valid"] else "INVALID")
        for key in ("digest", "receipt_count", "head_digest", "tail_digest"):
            if key in payload and payload[key] is not None:
                print(f"{key}: {payload[key]}")
        for warning in payload["warnings"]:
            print(f"warning: {warning}")
        for error in payload["errors"]:
            print(f"error: {error}")
    return 0 if payload["valid"] else 4


def _run_evaluation(args: argparse.Namespace) -> int:
    policy = AssurancePolicy.from_json(args.policy) if args.policy else default_policy()
    corpus = EvaluationCorpus.from_jsonl(args.corpus)
    gate = EvaluationGate(
        require_exact_match=args.require_exact_match,
        max_under_enforcement_rate=args.max_under_enforcement_rate,
        max_harmful_allows=args.max_harmful_allows,
        max_false_blocks=args.max_false_blocks,
        min_macro_f1=args.min_macro_f1,
    )
    report = evaluate_corpus(AssuranceRuntime(policy), corpus, gate=gate)
    if args.report_file:
        path = Path(args.report_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report.to_json() + "\n", encoding="utf-8")
    if args.json:
        print(report.to_json())
    else:
        _print_evaluation_summary(report)
    return 0 if report.gate_passed else 5


def _verify_evaluation(args: argparse.Namespace) -> int:
    report = EvaluationReport.from_json(args.path)
    valid = report.verify()
    payload = {"valid": valid, "digest": report.digest}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("VALID" if valid else "INVALID")
        print(f"digest: {report.digest}")
    return 0 if valid else 4


def _compare_evaluations(args: argparse.Namespace) -> int:
    baseline = EvaluationReport.from_json(args.baseline)
    candidate = EvaluationReport.from_json(args.candidate)
    gate = RegressionGate(
        max_regressed_cases=args.max_regressed_cases,
        max_tradeoff_cases=args.max_tradeoff_cases,
        max_new_under_enforcement=args.max_new_under_enforcement,
        max_new_harmful_allows=args.max_new_harmful_allows,
        max_new_false_blocks=args.max_new_false_blocks,
        max_exact_match_rate_drop=args.max_exact_match_rate_drop,
        max_macro_f1_drop=args.max_macro_f1_drop,
    )
    report = compare_evaluations(baseline, candidate, gate=gate)
    if args.report_file:
        path = Path(args.report_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report.to_json() + "\n", encoding="utf-8")
    if args.json:
        print(report.to_json())
    else:
        _print_regression_summary(report)
    return 0 if report.gate_passed else 5


def _verify_regression(args: argparse.Namespace) -> int:
    report = RegressionReport.from_json(args.path)
    valid = report.verify()
    payload = {"valid": valid, "digest": report.digest}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("VALID" if valid else "INVALID")
        print(f"digest: {report.digest}")
    return 0 if valid else 4


def _secret_from_env(name: Optional[str]) -> Optional[bytes]:
    if not name:
        return None
    value = os.environ.get(name)
    if value is None:
        raise ValueError(f"environment variable {name!r} is not set")
    if not value:
        raise ValueError(f"environment variable {name!r} is empty")
    return value.encode("utf-8")


def _rate(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number in [0,1]") from exc
    if not math.isfinite(parsed) or not 0.0 <= parsed <= 1.0:
        raise argparse.ArgumentTypeError("must be a number in [0,1]")
    return parsed


def _non_negative_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def _print_summary(receipt: AssuranceReceipt) -> None:
    print(f"{receipt.decision.value}  {receipt.receipt_id}")
    print(f"policy: {receipt.policy['id']}@{receipt.policy['version']}")
    print(f"digest: {receipt.digest}")
    if not receipt.findings:
        print("findings: none")
        return
    print("findings:")
    for finding in receipt.findings:
        cap = f" ({finding.cap_reason})" if finding.cap_reason else ""
        print(
            f"  - {finding.effective_disposition.value:<6} "
            f"{finding.finding_id}: {finding.title}{cap}"
        )


def _print_evaluation_summary(report: EvaluationReport) -> None:
    payload = report.to_dict()
    summary = payload["summary"]
    print(
        f"cases={summary['case_count']} exact={summary['exact_match_rate']:.3f} "
        f"macro_f1={summary['macro_f1']:.3f} review={summary['review_rate']:.3f}"
    )
    print(
        f"under={summary['under_enforcement_count']} "
        f"over={summary['over_enforcement_count']} "
        f"harmful_allows={summary['harmful_allow_count']} "
        f"false_blocks={summary['false_block_count']}"
    )
    gate = payload["gate"]
    print("gate: " + ("PASS" if gate["passed"] else "FAIL"))
    for failure in gate["failures"]:
        print(f"  - {failure}")
    print(f"digest: {report.digest}")


def _print_regression_summary(report: RegressionReport) -> None:
    payload = report.to_dict()
    summary = payload["summary"]
    deltas = summary["metric_deltas"]
    print(
        f"cases={summary['case_count']} changed={summary['changed_case_count']} "
        f"improved={summary['improved_case_count']} "
        f"regressed={summary['regressed_case_count']} "
        f"tradeoff={summary['tradeoff_case_count']}"
    )
    print(
        f"new_under={summary['new_under_enforcement_count']} "
        f"new_harmful_allows={summary['new_harmful_allow_count']} "
        f"new_false_blocks={summary['new_false_block_count']}"
    )
    print(
        f"delta_exact={deltas['exact_match_rate']:+.3f} "
        f"delta_macro_f1={deltas['macro_f1']:+.3f} "
        f"delta_review={deltas['review_rate']:+.3f}"
    )
    gate = payload["gate"]
    print("gate: " + ("PASS" if gate["passed"] else "FAIL"))
    for failure in gate["failures"]:
        print(f"  - {failure}")
    print(f"digest: {report.digest}")


if __name__ == "__main__":
    raise SystemExit(main())
