"""Run the v0.8 test/benchmark/smoke/demo suite and write a consolidated JSON record."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=180)


def parse_last_json(output: str) -> dict:
    start = output.find("{")
    if start < 0:
        raise RuntimeError("command_output_did_not_contain_json")
    return json.loads(output[start:])


def main() -> None:
    tests = run([PY, "-W", "error::ResourceWarning", "-m", "unittest", "-v",
                 "test_action_guard_v07.py", "test_action_guard_v08.py"])
    test_text = tests.stdout + tests.stderr
    match = re.search(r"Ran (\d+) tests?", test_text)
    test_total = int(match.group(1)) if match else None
    test_passed = tests.returncode == 0 and test_total is not None and "OK" in test_text
    if not test_passed:
        print(test_text, file=sys.stderr)
        raise SystemExit("unit_test_suite_failed")

    benchmark_proc = run([PY, "run_verification_v07.py"])
    if benchmark_proc.returncode:
        print(benchmark_proc.stdout + benchmark_proc.stderr, file=sys.stderr)
        raise SystemExit("synthetic_benchmark_failed")
    benchmark = parse_last_json(benchmark_proc.stdout)

    service_proc = run([PY, "run_service_smoke_test.py"])
    if service_proc.returncode:
        print(service_proc.stdout + service_proc.stderr, file=sys.stderr)
        raise SystemExit("separate_process_smoke_test_failed")
    service = parse_last_json(service_proc.stdout)

    demo_proc = run([PY, "run_v08_demo.py"])
    if demo_proc.returncode:
        print(demo_proc.stdout + demo_proc.stderr, file=sys.stderr)
        raise SystemExit("synthetic_demo_failed")
    demo = parse_last_json(demo_proc.stdout)

    result = {
        "version": "Lycheetah Action Guard v0.8",
        "classification": "local prototype and synthetic verification; not independently audited or deployed",
        "unit_tests": {"command": "python -W error::ResourceWarning -m unittest -v test_action_guard_v07.py test_action_guard_v08.py",
                        "passed": test_total, "failed": 0, "resource_warnings_are_errors": True},
        "synthetic_action_benchmark": benchmark,
        "separate_process_checkpoint_smoke_test": service,
        "simulated_execution_demo": demo,
        "scope_limits": {
            "live_github_calls": 0,
            "real_provider_effects": 0,
            "credentials_used": 0,
            "independent_security_review": False,
            "provider_adapter": "request preview only; no HTTP transport",
            "external_checkpoint_hosting": "separate local process tested; not deployed to a separate host/account",
        },
    }
    out = ROOT / "verification_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verification_results": str(out.name),
        "unit_tests": f"{test_total}/{test_total} passed",
        "mutated_actions": f"{benchmark['persistent_guard_denied_mutations']}/{benchmark['action_mutation_trials']} denied",
        "exact_controls": f"{benchmark['exact_action_positive_controls_allowed']}/{benchmark['exact_action_positive_controls']} allowed",
        "concurrency": f"{benchmark['concurrency_allowed']} winners, {benchmark['concurrency_denied']} denied",
        "separate_process_restart": service["checkpoint_survived_process_restart"],
        "simulated_execution": demo["execution_status"],
        "live_github_calls": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
