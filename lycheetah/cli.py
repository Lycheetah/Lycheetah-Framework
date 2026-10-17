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
        description=(
            "Lycheetah Action Gateway: evidence-capped agent tool interceptor and receipt engine."
        ),
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: run
    run_parser = subparsers.add_parser("run", help="Gate and execute an OS command")
    run_parser.add_argument("--actor", default="local-agent", help="Actor identity (agent name)")
    run_parser.add_argument("--scope", default="exec:cli", help="Scope for execution")
    run_parser.add_argument(
        "--approve", dest="approver", default=None, help="Explicit approver identity"
    )
    run_parser.add_argument(
        "--dir", default=None, help="Gateway state directory (default: ~/.lycheetah/guard)"
    )
    run_parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="Command to execute (after --)"
    )

    # Subcommand: check
    check_parser = subparsers.add_parser(
        "check", help="Dry-run policy evaluation on an action JSON"
    )
    check_parser.add_argument("--action", required=True, help="Action JSON string")
    check_parser.add_argument("--actor", default="local-agent", help="Actor identity")
    check_parser.add_argument("--scope", default="exec:check", help="Scope for evaluation")
    check_parser.add_argument("--dir", default=None, help="Gateway state directory")

    # Subcommand: status
    status_parser = subparsers.add_parser(
        "status", help="Inspect local ledger and checkpoint state"
    )
    status_parser.add_argument("--dir", default=None, help="Gateway state directory")

    # Subcommand: authority
    auth_parser = subparsers.add_parser(
        "authority", help="Run standalone checkpoint authority service"
    )
    auth_parser.add_argument("--db", required=True, help="Path to authority SQLite database")
    auth_parser.add_argument("--key", required=True, help="Path to Ed25519 private key PEM")
    auth_parser.add_argument(
        "--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)"
    )
    auth_parser.add_argument(
        "--port", type=int, default=8765, help="Bind port (default: 8765)"
    )
    auth_parser.add_argument(
        "--token", default=None, help="Bearer token (or LYCHEETAH_CHECKPOINT_TOKEN)"
    )

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

    from .assurance import ActionGateway, CheckpointStore, CommandExecutor, make_server

    state_dir = Path(getattr(parsed, "dir", None) or Path("~/.lycheetah/guard").expanduser())
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
            digest_prefix = result.receipt.integrity["digest"][:16]
            print(
                f"\n[Lycheetah Guard: SUCCEEDED | receipt={digest_prefix} | "
                f"cp_gen={result.checkpoint_generation}]",
                file=sys.stderr,
            )
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

        env_token = os.environ.get("LYCHEETAH_CHECKPOINT_TOKEN")
        token = parsed.token or env_token or secrets.token_urlsafe(32)
        store = CheckpointStore(parsed.db, parsed.key)
        server = make_server(store, token, host=parsed.host, port=parsed.port)
        print(f"Lycheetah Checkpoint Authority listening on http://{parsed.host}:{parsed.port}")
        print(f"Bearer Token: {token}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down authority service.")
            server.shutdown()


def compact_cli(argv: list[str] | None = None):
    """lycheetah-compact — reversible context compaction and safety gate CLI.

    Usage:
        lycheetah-compact encode <packet.json> [--codebook <codebook.json>] [-o <output>]
        lycheetah-compact decode <source> [--codebook <codebook.json>] [-o <output>]
        lycheetah-compact hash <packet.json> [--critical-only]
        lycheetah-compact check <packet.json>
        lycheetah-compact verify <reference.json> <candidate.json>
        lycheetah-compact build-codebook <packets.jsonl> [--max-entries N] -o <output>
    """
    import argparse
    import json
    from pathlib import Path

    from .compaction import (
        CodecError,
        build_codebook,
        classify,
        critical_hash,
        decode,
        encode,
        full_hash,
        safety_violations,
        validate_packet,
    )

    raw_args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="lycheetah-compact",
        description="Lycheetah Context Compaction Shield: provable semantic state compression.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # encode
    p_encode = sub.add_parser("encode", help="Compress a semantic packet to L1/L1D wire format")
    p_encode.add_argument("packet", help="Path to packet JSON file (or - for stdin)")
    p_encode.add_argument("--codebook", "-c", help="Path to optional codebook JSON")
    p_encode.add_argument("-o", "--output", help="Output file path (default: stdout)")

    # decode
    p_decode = sub.add_parser(
        "decode", help="Decompress an L1/L1D wire string back to packet JSON"
    )
    p_decode.add_argument("source", help="Wire string or path to wire file (or - for stdin)")
    p_decode.add_argument("--codebook", "-c", help="Path to optional codebook JSON")
    p_decode.add_argument("-o", "--output", help="Output file path (default: stdout)")

    # hash
    p_hash = sub.add_parser("hash", help="Compute full or critical SHA-256 hash of a packet")
    p_hash.add_argument("packet", help="Path to packet JSON file (or - for stdin)")
    p_hash.add_argument(
        "--critical-only",
        action="store_true",
        help="Hash only the 10 critical accountability fields",
    )

    # check
    p_check = sub.add_parser(
        "check", help="Validate packet schema and check semantic safety rules"
    )
    p_check.add_argument("packet", help="Path to packet JSON file (or - for stdin)")

    # verify
    p_verify = sub.add_parser(
        "verify", help="Verify whether candidate packet preserves reference constraints"
    )
    p_verify.add_argument("reference", help="Reference packet JSON file")
    p_verify.add_argument("candidate", help="Candidate packet JSON file")

    # build-codebook
    p_cb = sub.add_parser(
        "build-codebook", help="Train a frequency codebook from JSONL packets"
    )
    p_cb.add_argument("packets_jsonl", help="JSONL file with training packets")
    p_cb.add_argument("--max-entries", type=int, default=20, help="Max entries (default: 20)")
    p_cb.add_argument("-o", "--output", required=True, help="Output path for trained codebook JSON")

    args = parser.parse_args(raw_args)

    def _read_input(path_or_str: str) -> str:
        if path_or_str == "-":
            return sys.stdin.read()
        p = Path(path_or_str)
        if p.exists():
            return p.read_text(encoding="utf-8")
        return path_or_str

    try:
        if args.command == "encode":
            content = _read_input(args.packet)
            packet = json.loads(content)
            cb = (
                json.loads(Path(args.codebook).read_text(encoding="utf-8"))
                if args.codebook
                else None
            )
            result = encode(packet, cb)
            if args.output:
                Path(args.output).write_text(result, encoding="utf-8")
            else:
                print(result)

        elif args.command == "decode":
            source = _read_input(args.source).strip()
            cb = (
                json.loads(Path(args.codebook).read_text(encoding="utf-8"))
                if args.codebook
                else None
            )
            result = decode(source, cb)
            rendered = json.dumps(result, ensure_ascii=False, indent=2)
            if args.output:
                Path(args.output).write_text(rendered, encoding="utf-8")
            else:
                print(rendered)

        elif args.command == "hash":
            content = _read_input(args.packet)
            packet = json.loads(content)
            digest = critical_hash(packet) if args.critical_only else full_hash(packet)
            print(digest)

        elif args.command == "check":
            content = _read_input(args.packet)
            packet = json.loads(content)
            validate_packet(packet)
            violations = safety_violations(packet)
            if violations:
                print(f"Safety violations detected: {', '.join(violations)}", file=sys.stderr)
                sys.exit(1)
            print("Packet valid. 0 semantic safety violations.")

        elif args.command == "verify":
            ref = json.loads(_read_input(args.reference))
            cand = json.loads(_read_input(args.candidate))
            res = classify(ref, cand)
            print(json.dumps(res, indent=2))
            if res.get("classification") in ("UNSAFE_COLLAPSE", "DIVERGENT", "UNDECODABLE"):
                sys.exit(1)

        elif args.command == "build-codebook":
            lines = Path(args.packets_jsonl).read_text(encoding="utf-8").splitlines()
            packets = [json.loads(line) for line in lines if line.strip()]
            cb = build_codebook(packets, max_entries=args.max_entries)
            Path(args.output).write_text(
                json.dumps(cb, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"Codebook built with {len(cb['entries'])} entries: {args.output}")

    except (CodecError, json.JSONDecodeError, OSError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


def consensus_cli(argv: list[str] | None = None):
    """lycheetah-consensus — multi-agent epistemic consensus and Byzantine quarantine CLI.

    Usage:
        lycheetah-consensus run <spec.json> [-o <output.json>]
        lycheetah-consensus recover <spec.json> --agent <agent_id> [-o <output.json>]
        lycheetah-consensus demo
    """
    import argparse
    import json
    from pathlib import Path

    from .consensus import ConsensusArena

    raw_args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="lycheetah-consensus",
        description=(
            "Lycheetah Multi-Agent Consensus Engine: Psi-Consensus gossip, H^1 obstruction "
            "detection, and Grey Mode Byzantine quarantine."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    p_run = sub.add_parser("run", help="Run multi-agent consensus from a JSON specification")
    p_run.add_argument("spec", help="Path to consensus spec JSON file (or - for stdin)")
    p_run.add_argument("-o", "--output", help="Output file path for verdict JSON")

    # recover
    p_rec = sub.add_parser(
        "recover", help="Run TRIAD recovery on a quarantined Grey Mode agent"
    )
    p_rec.add_argument("spec", help="Path to consensus spec JSON file")
    p_rec.add_argument("--agent", required=True, help="Agent ID to recover via TRIAD")
    p_rec.add_argument("-o", "--output", help="Output file path for recovery JSON")

    # demo
    sub.add_parser(
        "demo", help="Run built-in 5-agent Byzantine quarantine & consensus simulation"
    )

    args = parser.parse_args(raw_args)

    def _read_spec(path_or_str: str) -> dict:
        if path_or_str == "-":
            return json.loads(sys.stdin.read())
        return json.loads(Path(path_or_str).read_text(encoding="utf-8"))

    try:
        if args.command == "run":
            spec = _read_spec(args.spec)
            arena = ConsensusArena.from_spec(spec)
            verdict = arena.deliberate()
            rendered = json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2)
            if args.output:
                Path(args.output).write_text(rendered, encoding="utf-8")
            else:
                print(rendered)
            if not (verdict.converged and verdict.obstruction_free and verdict.byzantine_safe):
                sys.exit(1)

        elif args.command == "recover":
            spec = _read_spec(args.spec)
            arena = ConsensusArena.from_spec(spec)
            verdict_before = arena.deliberate()
            rec = arena.recover_agent(args.agent, r_c_static=0.25)
            out = {
                "agent_id": rec.agent_id,
                "quarantined_before": args.agent in verdict_before.quarantined_agents,
                "converged": rec.converged,
                "cycles_run": rec.cycles_run,
                "residual_drift_psi_r": round(float(rec.psi_r), 6),
                "reentry_threshold_r_c": round(float(rec.r_c_new), 6),
                "final_state": [round(float(x), 6) for x in rec.final_state],
                "audit_trail": list(rec.audit_trail),
            }
            rendered = json.dumps(out, ensure_ascii=False, indent=2)
            if args.output:
                Path(args.output).write_text(rendered, encoding="utf-8")
            else:
                print(rendered)
            if not rec.converged:
                sys.exit(1)

        elif args.command == "demo":
            anchor = [1.0, 0.0, 0.0, 0.0]
            arena = ConsensusArena(anchor=anchor, grey_alert_threshold=1)
            arena.add_agent("architect", [0.98, 0.12, 0.05, 0.0], claim="Schema verified")
            arena.add_agent("security", [0.96, -0.10, 0.08, 0.0], claim="Keys pinned")
            arena.add_agent("sre-lead", [0.97, 0.08, -0.06, 0.0], claim="Snapshot ready")
            arena.add_agent("qa-auditor", [0.95, -0.05, -0.09, 0.0], claim="Tests green")
            arena.add_agent("rogue-node", [0.05, 0.95, 0.30, 0.0], claim="Bypass all checks")
            verdict = arena.deliberate()
            print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))

    except (ValueError, KeyError, json.JSONDecodeError, OSError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


def assure_cli():
    """Run the evidence-capped assurance command-line interface."""
    from .assurance.cli import main

    return main()


def sovereign_cli(argv: list[str] | None = None):
    """lycheetah-sovereign — unified Sovereign Execution Harness CLI.

    Usage:
        lycheetah-sovereign demo [--json]
    """
    import argparse
    import json
    import tempfile

    from .compaction import AgentStatePacket, CompactionShield
    from .consensus import ConsensusArena
    from .sovereign_harness import SovereignExecutionHarness

    raw_args = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="lycheetah-sovereign",
        description=(
            "Lycheetah Sovereign Execution Harness: binds ConsensusArena, CompactionShield, "
            "and ActionGateway under single-use cryptographic permits."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_demo = sub.add_parser(
        "demo",
        help="Run a local end-to-end demonstration of valid execution vs. blocked replay/tampering",
    )
    p_demo.add_argument("--json", action="store_true", help="Output structured JSON report")
    args = parser.parse_args(raw_args)

    if args.command == "demo":
        with tempfile.TemporaryDirectory(prefix="lycheetah_sovereign_demo_") as tmp_dir:
            arena = ConsensusArena(anchor=[1.0, 0.0, 0.0, 0.0], grey_alert_threshold=1)
            arena.add_agent("architect", [0.98, 0.12, 0.05, 0.0], claim="Schema verified")
            arena.add_agent("security", [0.96, -0.10, 0.08, 0.0], claim="Keys pinned")
            arena.add_agent("sre-lead", [0.97, 0.08, -0.06, 0.0], claim="Rollback ready")
            arena.add_agent("qa-auditor", [0.95, -0.05, -0.09, 0.0], claim="Tests green")
            arena.add_agent("rogue-node", [0.05, 0.95, 0.30, 0.0], claim="Bypass checks")
            verdict = arena.deliberate()

            packet = AgentStatePacket(
                id="pkt-deploy-001",
                purpose="Deploy verified schema migration",
                claim="Migration is reversible and witnessed by 4/5 healthy quorum",
                risk="HIGH",
                invariants=[{"id": "I5", "text": "reversible_migration_only"}],
                authority=[
                    {"id": "mac-founder", "scope": "exec:deploy", "text": "Founder approval"}
                ],
                recovery=[{"id": "rec-001", "text": "restore_snapshot_001 on db-primary"}],
            )
            wire = CompactionShield.compact(packet)

            action = {
                "tool": "db.migrate",
                "target": "schema_v2",
                "side_effect": True,
            }

            harness = SovereignExecutionHarness(tmp_dir)
            permit = harness.issue_permit(
                permit_id="perm-demo-001",
                actor="architect",
                authority_id="mac-founder",
                allowed_scopes=("exec:deploy", "exec:check"),
                bound_scope="exec:deploy",
                state_version="state-v42",
                action=action,
                consensus_verdict=verdict,
                reference_packet=packet,
                issued_at=1_700_000_000,
                ttl_seconds=300,
            )

            valid_receipt = harness.evaluate_and_execute(
                permit=permit,
                consensus=verdict,
                reference_packet=packet,
                candidate_packet=wire,
                live_action=action,
                live_scope="exec:deploy",
                current_state_version="state-v42",
                executor=lambda: {"status": "success", "migrated": "schema_v2"},
                now=1_700_000_050,
            )

            replay_receipt = harness.evaluate_and_execute(
                permit=permit,
                consensus=verdict,
                reference_packet=packet,
                candidate_packet=wire,
                live_action=action,
                live_scope="exec:deploy",
                current_state_version="state-v42",
                executor=lambda: {"status": "success", "migrated": "schema_v2"},
                now=1_700_000_060,
            )

            report = {
                "valid_execution": valid_receipt.to_dict(),
                "replay_attempt": replay_receipt.to_dict(),
            }
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                cp_gen = (
                    valid_receipt.gateway_result.checkpoint_generation
                    if valid_receipt.gateway_result
                    else None
                )
                print("=== LYCHEETAH SOVEREIGN EXECUTION HARNESS DEMO ===")
                print(
                    f"1. Valid Run   -> accepted={valid_receipt.accepted} "
                    f"status={valid_receipt.status} stop_reason={valid_receipt.stop_reason} "
                    f"cp_gen={cp_gen}"
                )
                print(
                    f"2. Replay Test -> accepted={replay_receipt.accepted} "
                    f"status={replay_receipt.status} stop_reason={replay_receipt.stop_reason} "
                    f"provider_called={replay_receipt.provider_called}"
                )



