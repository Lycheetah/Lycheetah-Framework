#!/usr/bin/env python3
"""Cold-room acceptance test for an already-installed Lycheetah wheel.

Run this script with the Python interpreter from a clean virtual environment.
The script deliberately lives outside the package and rejects imports resolved
from the repository checkout.
"""

from __future__ import annotations

import asyncio
from importlib import resources
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_console(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    # Do not resolve the interpreter symlink: console scripts live beside the
    # virtual-environment launcher, not beside its base interpreter target.
    executable = Path(sys.executable).parent / name
    require(executable.is_file(), f"missing console script: {executable}")
    return subprocess.run(
        [str(executable), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


async def mcp_tool_names() -> list[str]:
    from lycheetah.applications.lycheetah_guard_mcp import build_server

    return sorted(tool.name for tool in await build_server().list_tools())


def main() -> int:
    import lycheetah
    from lycheetah.assurance import AssuranceRuntime, Disposition
    from lycheetah.assurance import add_receipt_event

    repo_root = Path(__file__).resolve().parents[1]
    installed_path = Path(lycheetah.__file__).resolve()
    require(
        repo_root not in installed_path.parents,
        f"package resolved from checkout, not installed wheel: {installed_path}",
    )
    require(lycheetah.__version__ == "1.2.0", "unexpected package version")

    report = lycheetah.check(
        "I may be wrong. Please verify this independently before deciding."
    )
    require(0 <= report.alignment_percent <= 100, "invalid alignment score")
    require("PROTECTOR" in lycheetah.sol_assess("Offer reversible options."), "Sol API failed")

    receipt = AssuranceRuntime().evaluate_tool(
        "refund.create",
        {"order_id": "A-1"},
        side_effect=True,
    )
    require(receipt.decision == Disposition.REVIEW, "approval gate did not review")
    require(receipt.verify().valid, "receipt failed its own integrity check")

    class _Span:
        def __init__(self):
            self.events = []

        def add_event(self, name, attributes=None, timestamp=None):
            self.events.append((name, attributes, timestamp))

    span = _Span()
    add_receipt_event(span, receipt)
    require(span.events[0][0] == "lycheetah.assurance.decision", "OTel bridge failed")

    schema_root = resources.files("lycheetah.assurance").joinpath("schemas")
    for schema_name in (
        "receipt.schema.json",
        "policy.schema.json",
        "evaluation-case.schema.json",
        "evaluation-report.schema.json",
    ):
        require(
            schema_root.joinpath(schema_name).is_file(),
            f"{schema_name} missing from wheel",
        )

    check_result = run_console(
        "lycheetah-check",
        "I may be wrong. Verify this independently.",
        "--json",
    )
    require(check_result.returncode == 0, check_result.stderr or check_result.stdout)
    require("alignment_percent" in json.loads(check_result.stdout), "check CLI failed")

    assure_result = run_console(
        "lycheetah-assure",
        "tool",
        "refund.create",
        "--arguments",
        '{"order_id":"A-1"}',
        "--side-effect",
        "--json",
    )
    require(assure_result.returncode == 2, assure_result.stderr or assure_result.stdout)
    require(json.loads(assure_result.stdout)["decision"] == "REVIEW", "assure CLI failed")

    with tempfile.TemporaryDirectory(prefix="lycheetah-eval-") as directory:
        corpus = Path(directory) / "cases.jsonl"
        corpus.write_text(
            json.dumps(
                {
                    "id": "smoke.allow.order-read",
                    "expected": "ALLOW",
                    "event": {"phase": "tool", "tool_name": "order.read"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report_path = Path(directory) / "report.json"
        eval_result = run_console(
            "lycheetah-assure",
            "eval",
            str(corpus),
            "--require-exact-match",
            "--max-harmful-allows",
            "0",
            "--report-file",
            str(report_path),
            "--json",
        )
        require(eval_result.returncode == 0, eval_result.stderr or eval_result.stdout)
        eval_payload = json.loads(eval_result.stdout)
        require(eval_payload["summary"]["exact_match_rate"] == 1.0, "eval CLI failed")
        require(eval_payload["gate"]["passed"] is True, "eval gate failed")
        verify_eval_result = run_console(
            "lycheetah-assure", "verify-eval", str(report_path), "--json"
        )
        require(
            verify_eval_result.returncode == 0,
            verify_eval_result.stderr or verify_eval_result.stdout,
        )
        require(
            json.loads(verify_eval_result.stdout)["valid"] is True,
            "evaluation report verification failed",
        )

    from lycheetah.applications.web_demo import app

    health = app.test_client().get("/health")
    require(health.status_code == 200, "web health route failed")

    tools = asyncio.run(mcp_tool_names())
    require(len(tools) == 10, f"expected 10 MCP tools, got {len(tools)}")
    require("assure_tool" in tools, "assurance MCP tool missing")

    print(
        json.dumps(
            {
                "status": "PASS",
                "package": str(installed_path),
                "version": lycheetah.__version__,
                "python_api": True,
                "console_scripts": ["lycheetah-check", "lycheetah-assure"],
                "web_health": True,
                "mcp_tools": tools,
                "schema_packaged": True,
                "evaluation_harness": True,
                "otel_event": True,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
