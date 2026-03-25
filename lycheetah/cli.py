"""
Lycheetah CLI entry points
==========================
Registered in pyproject.toml as console_scripts.
"""

from __future__ import annotations
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_IMPL = os.path.join(os.path.dirname(_HERE), "12_IMPLEMENTATIONS")
if _IMPL not in sys.path:
    sys.path.insert(0, _IMPL)


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
        prog="lycheetah-check",
        description="Constitutional alignment check for AI-generated text"
    )
    parser.add_argument("text", nargs="?", help="Text to check (or pipe via stdin)")
    parser.add_argument("--context", "-c", default="", help="Optional context / user prompt")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    text = args.text
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

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
        print(f"\nTRI-AXIAL METRICS:")
        print(f"  TES  {report.tes_score:.3f}  {'PASS' if report.tes_status.value == 'PASS' else 'FAIL'}  (threshold 0.70)")
        print(f"  VTR  {report.vtr_score:.3f}  {'PASS' if report.vtr_status.value == 'PASS' else 'FAIL'}  (threshold 1.50)")
        print(f"  PAI  {report.pai_score:.3f}  {'PASS' if report.pai_status.value == 'PASS' else 'FAIL'}  (threshold 0.80)")
        print(f"\nSEVEN INVARIANTS:")
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
        prog="lycheetah-web",
        description="Start the Lycheetah web demo"
    )
    parser.add_argument("--port", "-p", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    # Import the app from the applications folder
    sys.path.insert(0, _IMPL)
    from applications.web_demo import app
    print(f"Lycheetah Web Demo running at http://{args.host}:{args.port}")
    print("Ctrl+C to stop")
    app.run(host=args.host, port=args.port, debug=False)


def guard_cli():
    """
    lycheetah-guard — start the MCP server (stdio transport).

    Usage:
        lycheetah-guard
        (registered as MCP server in Claude Code settings.json)
    """
    from applications.lycheetah_guard_mcp import main
    main()
