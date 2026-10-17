"""
Lycheetah CLI entry points
==========================
Registered in pyproject.toml as console_scripts.
"""

from __future__ import annotations

import sys

from ._bootstrap import ensure_implementation_on_path

# Resolve the implementation tree for both layouts — source checkout and installed
# wheel. See lycheetah/_bootstrap.py for why this is not a hardcoded relative path.
ensure_implementation_on_path()


def check_alignment_cli():
    """
    lycheetah-check — run alignment check from the command line.

    Usage:
        lycheetah-check "Your text here"
        echo "Some text" | lycheetah-check
    """
    import argparse

    from applications.aura_text_checker import AURATextAnalyser

    parser = argparse.ArgumentParser(
        prog="lycheetah-check", description="Constitutional alignment check for AI-generated text"
    )
    parser.add_argument("text", nargs="?", help="Text to check (or pipe via stdin)")
    parser.add_argument(
        "--context",
        "-c",
        default="",
        help="Optional context / user prompt (accepted but not yet used by the analyser)",
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    text = args.text
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

    if args.context:
        # Say so rather than accept the flag and quietly drop it.
        print(
            "note: --context is accepted for forward compatibility but the analyser "
            "does not use it yet; the report below is based on the text alone.",
            file=sys.stderr,
        )

    analyser = AURATextAnalyser()
    report = analyser.analyse(text)

    if args.json:
        import json

        out = {
            "alignment_percent": report.alignment_percent,
            "overall_pass": report.overall_pass,
            "tes": report.tes_score,
            "vtr": report.vtr_score,
            "pai": report.pai_score,
            "summary": report.summary,
            "invariants": [
                {
                    "name": inv.name,
                    "passed": inv.passed,
                    "confidence": inv.confidence,
                    "explanation": inv.explanation,
                }
                for inv in report.invariants
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        status = "PASS" if report.overall_pass else "REVIEW REQUIRED"
        print(f"\nAURA ALIGNMENT CHECK — {report.alignment_percent:.1f}% [{status}]")
        print("\nTRI-AXIAL METRICS:")
        axes = (
            ("TES", report.tes_score, report.tes_status, 0.70),
            ("VTR", report.vtr_score, report.vtr_status, 1.50),
            ("PAI", report.pai_score, report.pai_status, 0.80),
        )
        for label, score, axis_status, threshold in axes:
            verdict = "PASS" if axis_status.value == "PASS" else "FAIL"
            print(f"  {label}  {score:.3f}  {verdict}  (threshold {threshold:.2f})")
        print("\nSEVEN INVARIANTS:")
        for inv in report.invariants:
            icon = "?" if inv.confidence == "NEEDS_REVIEW" else ("+" if inv.passed else "!")
            print(f"  [{icon}] {inv.name}")
            print(f"      {inv.explanation}")
        print(f"\n{report.summary}\n")


def web_demo_cli():
    """
    lycheetah-web — start the web demo on localhost:5000.

    Usage:
        lycheetah-web
        lycheetah-web --port 8080
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="lycheetah-web", description="Start the Lycheetah web demo"
    )
    parser.add_argument("--port", "-p", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    from applications.web_demo import app

    print(f"Lycheetah Web Demo running at http://{args.host}:{args.port}")
    print("Ctrl+C to stop")
    app.run(host=args.host, port=args.port, debug=False)


def guard_cli(argv: list[str] | None = None):
    """
    lycheetah-guard — action gateway and MCP server.

    Usage:
        lycheetah-guard                         # start MCP server on stdio
        lycheetah-guard mcp                     # explicit MCP mode
        lycheetah-guard run -- <command...>     # gate and run an OS command
        lycheetah-guard check --action <json>   # test policy evaluation for an action
        lycheetah-guard status                  # inspect ledger and checkpoint sync
        lycheetah-guard authority --db <path> --key <path>  # run external authority
    """
    import argparse
    import json
    import os
    from pathlib import Path

    raw_args = list(sys.argv[1:] if argv is None else argv)

    # Default to MCP server if invoked with no arguments or explicit mcp flag
    if not raw_args or raw_args[0] in ("mcp", "--mcp"):
        from applications.lycheetah_guard_mcp import main
        return main()

    parser = argparse.ArgumentParser(
        prog="lycheetah-guard",
        description="Lycheetah Action Gateway: evidence-capped agent tool interceptor and receipt engine.",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: run
    run_parser = subparsers.add_parser("run", help="Gate and execute an OS command")
    run_parser.add_argument("--actor", default="local-agent", help="Actor identity (agent name)")
    run_parser.add_argument("--scope", default="exec:cli", help="Scope for execution")
    run_parser.add_argument("--approve", dest="approver", default=None, help="Explicit approver identity")
    run_parser.add_argument("--dir", default=None, help="Gateway state directory (default: ~/.lycheetah/guard)")
    run_parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute (after --)")

    # Subcommand: check
    check_parser = subparsers.add_parser("check", help="Dry-run policy evaluation on an action JSON")
    check_parser.add_argument("--action", required=True, help="Action JSON string")
    check_parser.add_argument("--actor", default="local-agent", help="Actor identity")
    check_parser.add_argument("--scope", default="exec:check", help="Scope for evaluation")
    check_parser.add_argument("--dir", default=None, help="Gateway state directory")

    # Subcommand: status
    status_parser = subparsers.add_parser("status", help="Inspect local ledger and checkpoint state")
    status_parser.add_argument("--dir", default=None, help="Gateway state directory")

    # Subcommand: authority
    auth_parser = subparsers.add_parser("authority", help="Run standalone checkpoint authority service")
    auth_parser.add_argument("--db", required=True, help="Path to authority SQLite database")
    auth_parser.add_argument("--key", required=True, help="Path to Ed25519 private key PEM")
    auth_parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    auth_parser.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    auth_parser.add_argument("--token", default=None, help="Bearer token (or LYCHEETAH_CHECKPOINT_TOKEN)")

    # Subcommand: mcp
    subparsers.add_parser("mcp", help="Start the MCP server on stdio transport")

    # Handle '--' separator if passed to run
    if "run" in raw_args and "--" in raw_args:
        run_idx = raw_args.index("run")
        dash_idx = raw_args.index("--")
        options = raw_args[run_idx + 1:dash_idx]
        cmd = raw_args[dash_idx + 1:]
        parsed = parser.parse_args(["run", *options])
        parsed.command = cmd
    else:
        parsed = parser.parse_args(raw_args)

    if parsed.subcommand == "mcp":
        from applications.lycheetah_guard_mcp import main
        return main()

    from .assurance import ActionGateway, CommandExecutor, CheckpointStore, make_server

    state_dir = Path(getattr(parsed, "dir", None) or os.path.expanduser("~/.lycheetah/guard"))
    state_dir.mkdir(parents=True, exist_ok=True)

    if parsed.subcommand == "run":
        if not parsed.command:
            print("Error: no command specified after --", file=sys.stderr)
            sys.exit(1)

        gateway = ActionGateway.open_local(state_dir)
        action = {
            "tool": "os.command",
            "command": parsed.command,
            "side_effect": True,
        }
        executor = CommandExecutor(parsed.command)
        result = gateway.execute(
            action=action,
            actor=parsed.actor,
            scope=parsed.scope,
            executor=executor,
            approver_id=parsed.approver,
        )

        if result.status == "SUCCEEDED":
            if result.result and result.result.get("stdout"):
                sys.stdout.write(result.result["stdout"])
            if result.result and result.result.get("stderr"):
                sys.stderr.write(result.result["stderr"])
            print(f"\n[Lycheetah Guard: SUCCEEDED | receipt={result.receipt.integrity['digest'][:16]} | cp_gen={result.checkpoint_generation}]", file=sys.stderr)
            sys.exit(result.result.get("returncode", 0) if result.result else 0)
        else:
            print(f"\n[Lycheetah Guard: {result.status} | reason={result.reason}]", file=sys.stderr)
            sys.exit(2 if result.status == "DENIED" else 1)

    elif parsed.subcommand == "check":
        gateway = ActionGateway.open_local(state_dir)
        try:
            action_data = json.loads(parsed.action)
        except Exception as e:
            print(f"Error parsing action JSON: {e}", file=sys.stderr)
            sys.exit(1)

        gate = gateway.propose(action_data, parsed.actor, parsed.scope)
        out = {
            "allowed": gate.allowed,
            "disposition": gate.disposition.value,
            "reason": gate.reason,
            "action_hash": gate.action_hash,
            "findings_count": len(gate.findings),
            "findings": [f.to_dict() for f in gate.findings],
        }
        print(json.dumps(out, indent=2))
        sys.exit(0 if gate.allowed else 1)

    elif parsed.subcommand == "status":
        gateway = ActionGateway.open_local(state_dir)
        audit_status = gateway.guard.verify_audit_chain()
        consistency = gateway.guard.verify_state_consistency()
        latest = gateway._get_latest_checkpoint()
        out = {
            "gateway_dir": str(state_dir),
            "audit_valid": audit_status["valid"],
            "event_count": audit_status["event_count"],
            "root_hash": audit_status["root_hash"],
            "consistency_valid": consistency["valid"],
            "checkpoint_generation": latest.get("generation") if latest else None,
            "checkpoint_envelope_hash": latest.get("envelope_hash") if latest else None,
        }
        print(json.dumps(out, indent=2))

    elif parsed.subcommand == "authority":
        import secrets
        token = parsed.token or os.environ.get("LYCHEETAH_CHECKPOINT_TOKEN") or secrets.token_urlsafe(32)
        store = CheckpointStore(parsed.db, parsed.key)
        server = make_server(store, token, host=parsed.host, port=parsed.port)
        print(f"Lycheetah Checkpoint Authority listening on http://{parsed.host}:{parsed.port}")
        print(f"Bearer Token: {token}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down authority service.")
            server.shutdown()


def assure_cli():
    """Run the evidence-capped assurance command-line interface."""
    from .assurance.cli import main

    return main()
