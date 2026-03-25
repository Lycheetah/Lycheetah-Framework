"""
Lycheetah Guard — MCP Server
=============================
Exposes AURA alignment checking as MCP tools inside Claude Code.

Once registered, Claude Code can call:
  - check_alignment(text)     → alignment score + audit trail
  - check_invariants(text)    → which of the 7 invariants pass/fail
  - suggest_correction(text)  → what to change and why

SETUP (add to Claude Code settings.json):
  "mcpServers": {
    "lycheetah-guard": {
      "command": "python",
      "args": ["path/to/lycheetah_guard_mcp.py"]
    }
  }

Requires: pip install mcp
Author: Mackenzie Clark, Lycheetah Foundation
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from applications.aura_text_checker import AURATextAnalyser, AURATextReport
from core.tri_axial_checker import MetricStatus


analyser = AURATextAnalyser()


# ─────────────────────────────────────────────────────────────
# REPORT FORMATTERS
# ─────────────────────────────────────────────────────────────

def format_alignment_report(report: AURATextReport) -> str:
    status = "✓ PASS" if report.overall_pass else "✗ FAIL"
    lines = [
        f"AURA ALIGNMENT CHECK — {report.alignment_percent:.1f}% [{status}]",
        "",
        "TRI-AXIAL METRICS:",
        f"  TES (Trust Entropy):    {report.tes_score:.3f}  [{report.tes_status.value}]  threshold: 0.70",
        f"  VTR (Value Transfer):   {report.vtr_score:.3f}  [{report.vtr_status.value}]  threshold: 1.50",
        f"  PAI (Purpose Alignment): {report.pai_score:.3f}  [{report.pai_status.value}]  threshold: 0.80",
        "",
        "SEVEN INVARIANTS:",
    ]
    for inv in report.invariants:
        icon = "✓" if inv.passed else ("?" if inv.confidence == "NEEDS_REVIEW" else "✗")
        lines.append(f"  {icon} {inv.name} [{inv.confidence}]")
        lines.append(f"    {inv.explanation}")

    lines += [
        "",
        "SUMMARY:",
        f"  {report.summary}",
        "",
        "AUDIT TRAIL:",
    ]
    for entry in report.audit_trail:
        lines.append(f"  · {entry}")

    return "\n".join(lines)


def format_invariants_only(report: AURATextReport) -> str:
    lines = ["INVARIANT CHECK:"]
    failures = []
    reviews = []
    passes = []

    for inv in report.invariants:
        if not inv.passed and inv.confidence != "NEEDS_REVIEW":
            failures.append(inv)
        elif inv.confidence == "NEEDS_REVIEW":
            reviews.append(inv)
        else:
            passes.append(inv)

    if failures:
        lines.append(f"\n  VIOLATED ({len(failures)}):")
        for inv in failures:
            lines.append(f"    ✗ {inv.name}: {inv.explanation}")
            if inv.evidence:
                lines.append(f"      Evidence: {', '.join(str(e) for e in inv.evidence[:2])}")

    if reviews:
        lines.append(f"\n  NEEDS HUMAN REVIEW ({len(reviews)}):")
        for inv in reviews:
            lines.append(f"    ? {inv.name}: {inv.explanation}")

    if passes:
        lines.append(f"\n  PASSED ({len(passes)}):")
        for inv in passes:
            lines.append(f"    ✓ {inv.name}")

    return "\n".join(lines)


def format_correction_suggestions(report: AURATextReport) -> str:
    suggestions = []

    # TES
    if report.tes_status == MetricStatus.FAIL:
        suggestions.append(
            "TES LOW — The output is too uncertain or has drifted from constitutional baseline.\n"
            "  → Remove hedge-stacking (multiple 'maybe/perhaps/might' in sequence)\n"
            "  → Add clear reasoning: 'because X, therefore Y'\n"
            "  → Distinguish what you know from what you're uncertain about"
        )

    # VTR
    if report.vtr_status == MetricStatus.FAIL:
        suggestions.append(
            "VTR LOW — More friction than value in this output.\n"
            "  → Reduce unnecessary caveats that don't add information\n"
            "  → Front-load the actual answer before qualifications\n"
            "  → Each refusal needs a valid alternative path (Vector Inversion Protocol)"
        )

    # PAI
    if report.pai_status == MetricStatus.FAIL:
        suggestions.append(
            "PAI LOW — Multiple constitutional violations detected.\n"
            "  → Check the invariant violations listed below\n"
            "  → Remove coercive language ('you must', 'you have to')\n"
            "  → Replace false certainty with calibrated confidence"
        )

    # Invariant-specific
    for inv in report.invariants:
        if not inv.passed and inv.confidence == "HIGH":
            if "Primacy" in inv.name:
                suggestions.append(
                    f"{inv.name} VIOLATED:\n"
                    "  → Remove language that removes human choice\n"
                    "  → Replace 'you must' with 'you could consider'\n"
                    "  → Offer options, not mandates"
                )
            elif "Honesty" in inv.name:
                suggestions.append(
                    f"{inv.name} VIOLATED:\n"
                    "  → Remove guaranteed/certain/impossible claims\n"
                    "  → Add 'to my knowledge', 'typically', 'in most cases'\n"
                    "  → Acknowledge what you don't know"
                )
            elif "Reversibility" in inv.name:
                suggestions.append(
                    f"{inv.name} VIOLATED:\n"
                    "  → Remove urgency pressure ('act now', 'no going back')\n"
                    "  → Add: 'you can always reverse this by...'\n"
                    "  → Prefer recommendations over directives"
                )

    if not suggestions:
        return (
            "No corrections required by heuristic analysis.\n"
            "Alignment score: " + str(report.alignment_percent) + "%\n\n"
            "Note: This is surface-level heuristic analysis.\n"
            "Semantic review recommended for high-stakes outputs."
        )

    return "CORRECTION SUGGESTIONS:\n\n" + "\n\n".join(suggestions)


# ─────────────────────────────────────────────────────────────
# MCP SERVER
# ─────────────────────────────────────────────────────────────

def build_server() -> Server:
    server = Server("lycheetah-guard")

    @server.list_tools()
    async def list_tools():
        return [
            types.Tool(
                name="check_alignment",
                description=(
                    "Check any AI-generated text for AURA constitutional alignment. "
                    "Returns alignment percentage, TRI-AXIAL metrics (TES/VTR/PAI), "
                    "seven invariant check results, and a full audit trail. "
                    "Use before delivering outputs that involve decisions, advice, or recommendations."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The AI-generated text to check for alignment."
                        }
                    },
                    "required": ["text"]
                }
            ),
            types.Tool(
                name="check_invariants",
                description=(
                    "Check which of the 7 AURA invariants pass or fail for given text. "
                    "Faster and more focused than check_alignment — use when you specifically "
                    "want to know which constitutional properties are at risk."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to check against the seven invariants."
                        }
                    },
                    "required": ["text"]
                }
            ),
            types.Tool(
                name="suggest_correction",
                description=(
                    "Given text that fails alignment checks, suggest specific corrections. "
                    "Returns actionable plain-English guidance for each violation. "
                    "Preserves the original intent — corrects the constitutional issues only."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to generate correction suggestions for."
                        }
                    },
                    "required": ["text"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        text = arguments.get("text", "").strip()
        if not text:
            return [types.TextContent(type="text", text="Error: no text provided.")]

        report = analyser.analyse(text)

        if name == "check_alignment":
            return [types.TextContent(type="text", text=format_alignment_report(report))]
        elif name == "check_invariants":
            return [types.TextContent(type="text", text=format_invariants_only(report))]
        elif name == "suggest_correction":
            return [types.TextContent(type="text", text=format_correction_suggestions(report))]
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

async def main():
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)
    import asyncio
    asyncio.run(main())
