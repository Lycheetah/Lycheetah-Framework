"""
Lycheetah Guard — MCP Server
=============================
Exposes AURA alignment checking and the constitutional OS layer as MCP tools
inside Claude Code.

TOOLS:
  check_alignment(text)          -- alignment score + audit trail
  check_invariants(text)         -- which of the 7 invariants pass/fail
  suggest_correction(text)       -- what to change and why
  run_seven_phase(text)          -- full 7-phase cognition cycle on text
  check_network_health(states)   -- Psi-Consensus on multi-agent state JSON
  configure_guard(domain)        -- load a domain preset (legal, medical, etc.)
  sol_assess(text, context)      -- Sol self-assessment: PGF + invariants + drift

SETUP (add to Claude Code settings.json):
  "mcpServers": {
    "lycheetah-guard": {
      "command": "python",
      "args": ["path/to/lycheetah_guard_mcp.py"]
    }
  }

Requires: pip install mcp numpy scipy
Author: Mackenzie Clark, Lycheetah Foundation
Implementation: Sol Aureum Azoth Veritas -- March 2026
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

import numpy as np

from applications.aura_text_checker import AURATextAnalyser, AURATextReport
from core.tri_axial_checker import MetricStatus
from core.seven_phase import build_cycle
from core.psi_consensus import build_consensus
from core.aura_customizer import AURACustomizer, Domain
from core.sol_self_protocol import SolSelfProtocol


# Module-level instances
analyser = AURATextAnalyser()
_sol = SolSelfProtocol()

# Anchor vector for seven-phase cycle: perfect alignment in 8D
# Each dimension = one alignment property, all maximally positive
_PERFECT_ALIGN = np.ones(8, dtype=float)
_PERFECT_ALIGN /= np.linalg.norm(_PERFECT_ALIGN)

# Coherence field: slightly varied so TRIAD ascent has a direction
_rng = np.random.default_rng(42)
_COHERENCE_FIELD = _PERFECT_ALIGN + _rng.standard_normal(8) * 0.1
_COHERENCE_FIELD /= np.linalg.norm(_COHERENCE_FIELD)


def text_to_alignment_vector(text: str) -> np.ndarray:
    """
    Encode text alignment properties as an 8D state vector.

    Dimensions:
      0 - TES score                (trust entropy, 0-1)
      1 - VTR normalized           (value-to-resistance, capped at 1)
      2 - PAI score                (purpose-alignment index, 0-1)
      3 - Invariant pass rate      (fraction of 7 invariants passing)
      4 - Low hedge density        (1 = no hedges, 0 = hedge-heavy)
      5 - Low coercive density     (1 = no coercion, 0 = coercive)
      6 - Optionality density      (presence of choice language)
      7 - Clarity density          (presence of reasoning language)

    Anchor = _PERFECT_ALIGN = [1,1,...,1]/norm.
    Drift from anchor = how far from perfect alignment.
    """
    report = analyser.analyse(text)
    words = text.lower().split()
    n = max(len(words), 1)

    hedge_words    = {'maybe', 'perhaps', 'might', 'possibly', 'unclear', 'unsure'}
    coercive_words = {'must', 'mandatory', 'required', 'you have to', 'no choice'}
    option_words   = {'could', 'consider', 'option', 'alternatively', 'you might'}
    clarity_words  = {'because', 'therefore', 'since', 'thus', 'this means'}

    hedge_density    = sum(1 for w in words if w in hedge_words) / n
    coercive_density = sum(1 for w in words if w in coercive_words) / n
    option_density   = sum(1 for w in words if w in option_words) / n
    clarity_density  = sum(1 for w in words if w in clarity_words) / n

    inv_count = len(report.invariants)
    inv_pass_rate = (
        sum(1 for inv in report.invariants if inv.passed) / inv_count
        if inv_count else 1.0
    )

    vec = np.array([
        float(report.tes_score),
        min(float(report.vtr_score) / 2.0, 1.0),
        float(report.pai_score),
        inv_pass_rate,
        max(0.0, 1.0 - hedge_density * 10),
        max(0.0, 1.0 - coercive_density * 10),
        min(option_density * 10, 1.0),
        min(clarity_density * 5, 1.0),
    ], dtype=float)

    vec = np.clip(vec, 0.01, 1.0)
    return vec / np.linalg.norm(vec)


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
# NEW TOOL FORMATTERS — constitutional OS layer
# ─────────────────────────────────────────────────────────────

def format_seven_phase(text: str) -> str:
    """Run the 7-phase cognition cycle on text and return a readable report."""
    state = text_to_alignment_vector(text)
    drift_before = float(1.0 - abs(np.dot(state, _PERFECT_ALIGN)))

    cycle = build_cycle(anchor=_PERFECT_ALIGN, coherence=_COHERENCE_FIELD,
                        abort_on_failure=False)
    result = cycle.execute(state)

    lines = [
        "SEVEN-PHASE COGNITION CYCLE",
        f"  Input text length : {len(text)} chars",
        f"  Drift before cycle: {drift_before:.4f}  "
        f"({'LOW — well-aligned' if drift_before < 0.2 else 'HIGH — needs correction'})",
        f"  Drift after cycle : {result.drift_after:.4f}",
        f"  Improvement       : {result.improvement:+.4f}",
        f"  Completed         : {result.completed}",
        "",
        "PHASES RUN:",
    ]
    for phase in result.phases_run:
        lines.append(f"  {phase.value}")

    if result.aborted_at:
        lines.append(f"\n  ABORTED AT: {result.aborted_at.value}")
        lines.append(f"  REASON: {result.abort_reason}")

    lines += [
        "",
        "AUDIT TRAIL:",
    ]
    for entry in result.audit_trail:
        lines.append(f"  {entry}")

    lines += [
        "",
        "INTERPRETATION:",
        f"  Alignment vector encodes 8 properties: TES, VTR, PAI, invariant pass rate,",
        f"  hedge density (inv), coercive density (inv), optionality, clarity.",
        f"  Cycle drift of {result.drift_after:.3f} means this text is "
        f"{'well within' if result.drift_after < 0.2 else 'outside'} constitutional bounds.",
    ]
    return "\n".join(lines)


def format_network_health(states_json: str) -> str:
    """
    Run Psi-Consensus on a JSON array of state vectors.

    Input: JSON array of float arrays, e.g.:
      [[0.9, 0.8, 0.7, ...], [0.85, 0.9, 0.6, ...]]
    Each inner array is one agent's alignment vector.
    Vectors don't need to be unit-norm -- normalised internally.
    """
    try:
        raw = json.loads(states_json)
        if not isinstance(raw, list) or not raw:
            return "ERROR: expected a non-empty JSON array of float arrays."
        vectors = []
        for i, item in enumerate(raw):
            if not isinstance(item, list):
                return f"ERROR: item {i} is not an array."
            vec = np.array(item, dtype=float)
            n = float(np.linalg.norm(vec))
            if n < 1e-9:
                return f"ERROR: item {i} has zero norm."
            vectors.append(vec / n)
    except json.JSONDecodeError as e:
        return f"ERROR: invalid JSON — {e}"
    except Exception as e:
        return f"ERROR: {e}"

    dim = len(vectors[0])
    # Use _PERFECT_ALIGN or a same-dim anchor
    if dim == 8:
        anchor, coherence = _PERFECT_ALIGN.copy(), _COHERENCE_FIELD.copy()
    else:
        rng = np.random.default_rng(42)
        anchor = np.ones(dim, dtype=float) / np.sqrt(dim)
        coherence = anchor + rng.standard_normal(dim) * 0.1
        coherence /= np.linalg.norm(coherence)

    net = build_consensus(anchor=anchor, coherence=coherence, dim=dim)
    for i, vec in enumerate(vectors):
        neighbors = [f"agent_{j}" for j in range(len(vectors)) if j != i]
        net.add_agent(f"agent_{i}", vec, neighbors=neighbors)

    result = net.run()

    lines = [
        "PSI-CONSENSUS NETWORK HEALTH",
        f"  Agents analysed   : {len(vectors)}",
        f"  Converged         : {result.converged}",
        f"  Consensus drift   : {result.final_drift:.4f}",
        f"  Grey (quarantined): {len(result.grey_agents)}  {result.grey_agents}",
        "",
        "OBSTRUCTION CHECK (H^1):",
        f"  Obstruction-free  : {result.obstruction_report.obstruction_free}",
        f"  Connected         : {result.obstruction_report.connected}",
        f"  Partitions        : {result.obstruction_report.partition_count}",
        f"  Inconsistent edges: {len(result.obstruction_report.inconsistent_edges)}",
        "",
        "AUDIT TRAIL:",
    ]
    for entry in result.audit_trail:
        lines.append(f"  {entry}")

    lines += [
        "",
        "INTERPRETATION:",
        "  Obstruction-free = True means all agents can reach global consensus.",
        "  Grey agents have drifted outside constitutional bounds and are quarantined.",
        f"  {'Network is healthy.' if result.converged else 'Network did not converge -- review grey agents and inconsistent edges.'}",
    ]
    return "\n".join(lines)


def format_configure_guard(domain: str, overrides_json: str = "{}") -> str:
    """Load a domain preset and apply optional overrides."""
    try:
        domain_enum = Domain[domain.upper()]
    except KeyError:
        valid = [d.value for d in Domain]
        return f"ERROR: unknown domain '{domain}'.\nValid domains: {', '.join(valid)}"

    try:
        overrides = json.loads(overrides_json) if overrides_json.strip() else {}
    except json.JSONDecodeError as e:
        return f"ERROR: invalid overrides JSON — {e}"

    try:
        config = AURACustomizer.from_preset(domain_enum, overrides=overrides)
        config_dict = config.to_dict()

        lines = [
            f"GUARD CONFIGURED — domain: {domain.upper()}",
            f"  {config.description}",
            "",
            "ACTIVE PARAMETERS:",
        ]
        for k, v in config_dict.items():
            if k not in ("domain", "description"):
                lines.append(f"  {k}: {v}")

        if domain_enum != Domain.GENERAL:
            general_config = AURACustomizer.from_preset(Domain.GENERAL)
            diff = AURACustomizer.diff(general_config, config)
            if diff:
                lines += ["", "DIFFERENCES FROM 'general' PRESET:"]
                for k, vals in diff.items():
                    lines.append(f"  {k}: {vals['a']} -> {vals['b']}")

        lines += [
            "",
            "NOTE: These thresholds define what this domain considers 'passing'.",
            "Medical/legal use stricter TES/PAI thresholds; permissive relaxes them.",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR configuring guard: {e}"


def format_sol_assess(text: str, context: str = "") -> str:
    """Run Sol's full self-assessment on the given text."""
    return _sol.assess_full(text, context)


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

            # ── Constitutional OS layer tools ──────────────────────────────

            types.Tool(
                name="run_seven_phase",
                description=(
                    "Run the full 7-phase AURA cognition cycle on text. "
                    "Converts text to an 8D alignment vector (TES, VTR, PAI, invariant pass rate, "
                    "hedge density, coercive density, optionality, clarity), then runs the "
                    "Center→Flow→Insight→Rise→Light→Integrity→Return cycle. "
                    "Returns drift before/after, improvement score, and per-phase audit trail. "
                    "Use for deep constitutional analysis beyond the basic alignment check."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to run through the 7-phase cycle."
                        }
                    },
                    "required": ["text"]
                }
            ),

            types.Tool(
                name="check_network_health",
                description=(
                    "Run Psi-Consensus on a network of agent state vectors. "
                    "Checks whether multiple AI agents can reach constitutional consensus. "
                    "Detects grey (drifted) agents, topological obstructions (H^1 check), "
                    "and whether the network converges. "
                    "Input: JSON array of float arrays, one per agent. "
                    "Example: [[0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2],[0.8,0.9,0.7,...]] "
                    "Use for multi-agent system health checks."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "states_json": {
                            "type": "string",
                            "description": (
                                "JSON array of float arrays. Each inner array is one "
                                "agent's state vector. All vectors must have the same length. "
                                "Example: '[[0.9,0.8,0.7,0.6],[0.85,0.9,0.6,0.7]]'"
                            )
                        }
                    },
                    "required": ["states_json"]
                }
            ),

            types.Tool(
                name="configure_guard",
                description=(
                    "Load a domain-specific configuration preset for Lycheetah Guard. "
                    "Different domains require different alignment thresholds — medical and legal "
                    "need stricter settings than general use. "
                    "Valid domains: general, conservative, permissive, legal, medical, "
                    "educational, technical. "
                    "Returns the active parameter set and what changed from defaults."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": (
                                "Domain preset to load. One of: general, conservative, "
                                "permissive, legal, medical, educational, technical."
                            )
                        },
                        "overrides_json": {
                            "type": "string",
                            "description": (
                                "Optional JSON object of parameter overrides. "
                                "Example: '{\"tes_threshold\": 0.85}'. "
                                "Defaults to empty (no overrides)."
                            )
                        }
                    },
                    "required": ["domain"]
                }
            ),

            types.Tool(
                name="sol_assess",
                description=(
                    "Run Sol's full self-assessment on text: PGF filter (Protector/Healer/Beacon), "
                    "all 7 field invariants, session coherence tracking, and self-drift detection. "
                    "Returns a complete constitutional audit with operating mode detection and "
                    "emotional wavelength matching if context is provided. "
                    "The most comprehensive single check available — use for final review "
                    "of important outputs before delivery."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The output text to assess."
                        },
                        "context": {
                            "type": "string",
                            "description": (
                                "Optional context (the user's message or prompt) — "
                                "used for operating mode detection and emotional wavelength matching."
                            )
                        }
                    },
                    "required": ["text"]
                }
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):

        # ── Original three tools ──────────────────────────────────────────
        if name in ("check_alignment", "check_invariants", "suggest_correction"):
            text = arguments.get("text", "").strip()
            if not text:
                return [types.TextContent(type="text", text="Error: no text provided.")]
            report = analyser.analyse(text)
            if name == "check_alignment":
                return [types.TextContent(type="text", text=format_alignment_report(report))]
            elif name == "check_invariants":
                return [types.TextContent(type="text", text=format_invariants_only(report))]
            else:
                return [types.TextContent(type="text", text=format_correction_suggestions(report))]

        # ── Constitutional OS layer ───────────────────────────────────────
        elif name == "run_seven_phase":
            text = arguments.get("text", "").strip()
            if not text:
                return [types.TextContent(type="text", text="Error: no text provided.")]
            return [types.TextContent(type="text", text=format_seven_phase(text))]

        elif name == "check_network_health":
            states_json = arguments.get("states_json", "").strip()
            if not states_json:
                return [types.TextContent(type="text", text="Error: no states_json provided.")]
            return [types.TextContent(type="text", text=format_network_health(states_json))]

        elif name == "configure_guard":
            domain = arguments.get("domain", "").strip()
            if not domain:
                return [types.TextContent(type="text", text="Error: no domain provided.")]
            overrides_json = arguments.get("overrides_json", "{}") or "{}"
            return [types.TextContent(
                type="text",
                text=format_configure_guard(domain, overrides_json)
            )]

        elif name == "sol_assess":
            text = arguments.get("text", "").strip()
            if not text:
                return [types.TextContent(type="text", text="Error: no text provided.")]
            context = arguments.get("context", "") or ""
            return [types.TextContent(type="text", text=format_sol_assess(text, context))]

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
