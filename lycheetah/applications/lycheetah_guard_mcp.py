"""
Lycheetah Guard — MCP Server
=============================
Exposes AURA alignment checking, the constitutional OS layer, and the bounded
Assurance Runtime as provider-neutral MCP tools.

TOOLS:
  check_alignment(text)          -- alignment score + audit trail
  check_invariants(text)         -- which of the 7 invariants pass/fail
  suggest_correction(text)       -- what to change and why
  run_seven_phase(text)          -- full 7-phase cognition cycle on text
  check_network_health(states)   -- Psi-Consensus on multi-agent state JSON
  configure_guard(domain)        -- load a domain preset (legal, medical, etc.)
  sol_assess(text, context)      -- Sol self-assessment: PGF + invariants + drift
  assure_text(text, phase)       -- evidence-capped input/output decision receipt
  assure_tool(...)               -- pre-execution tool decision receipt
  verify_assurance_receipt(json) -- verify receipt body integrity

SETUP (add to Claude Code settings.json):
  "mcpServers": {
    "lycheetah-guard": {
      "command": "python",
      "args": ["path/to/lycheetah_guard_mcp.py"]
    }
  }

Requires: pip install "lycheetah-framework[mcp]"
Author: Mackenzie Clark, Lycheetah Foundation
Implementation: Sol Aureum Azoth Veritas -- March 2026
"""

from __future__ import annotations

import json
import os
from typing import Any, Literal

try:
    from mcp.server import MCPServer
    MCP_AVAILABLE = True
except ImportError:
    MCPServer = None  # type: ignore[assignment,misc]
    MCP_AVAILABLE = False

import numpy as np

from .aura_text_checker import AURATextAnalyser, AURATextReport
from ..assurance import AssuranceEvent, AssurancePolicy, AssuranceRuntime, Phase
from ..core.tri_axial_checker import MetricStatus
from ..core.seven_phase import build_cycle
from ..core.psi_consensus import build_consensus
from ..core.aura_customizer import AURACustomizer, Domain
from ..core.sol_self_protocol import SolSelfProtocol


# Module-level instances
analyser = AURATextAnalyser()
_sol = SolSelfProtocol()
_assurance_policy_path = os.environ.get("LYCHEETAH_ASSURANCE_POLICY")
_assurance_policy = (
    AssurancePolicy.from_json(_assurance_policy_path)
    if _assurance_policy_path
    else AssurancePolicy()
)
_assurance = AssuranceRuntime(_assurance_policy)

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
        "  Alignment vector encodes 8 properties: TES, VTR, PAI, invariant pass rate,",
        "  hedge density (inv), coercive density (inv), optionality, clarity.",
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
# MCP TOOL HANDLERS
# ─────────────────────────────────────────────────────────────


def tool_check_alignment(text: str) -> str:
    """Return AURA scores, invariant results, and an audit trail for text."""
    text = text.strip()
    if not text:
        return "Error: no text provided."
    return format_alignment_report(analyser.analyse(text))


def tool_check_invariants(text: str) -> str:
    """Check text against the seven AURA invariants."""
    text = text.strip()
    if not text:
        return "Error: no text provided."
    return format_invariants_only(analyser.analyse(text))


def tool_suggest_correction(text: str) -> str:
    """Suggest bounded corrections for heuristic alignment findings."""
    text = text.strip()
    if not text:
        return "Error: no text provided."
    return format_correction_suggestions(analyser.analyse(text))


def tool_run_seven_phase(text: str) -> str:
    """Run the experimental seven-phase transformation cycle on text."""
    text = text.strip()
    if not text:
        return "Error: no text provided."
    return format_seven_phase(text)


def tool_check_network_health(states_json: str) -> str:
    """Evaluate experimental Psi-Consensus over JSON state vectors."""
    states_json = states_json.strip()
    if not states_json:
        return "Error: no states_json provided."
    return format_network_health(states_json)


def tool_configure_guard(domain: str, overrides_json: str = "{}") -> str:
    """Preview a named heuristic guard configuration and optional overrides."""
    domain = domain.strip()
    if not domain:
        return "Error: no domain provided."
    return format_configure_guard(domain, overrides_json or "{}")


def tool_sol_assess(text: str, context: str = "") -> str:
    """Run the experimental Sol self-assessment over text and optional context."""
    text = text.strip()
    if not text:
        return "Error: no text provided."
    return format_sol_assess(text, context or "")


def _assurance_seal_kwargs() -> dict[str, Any]:
    """Read optional sealing material from process environment, never MCP input."""
    secret = os.environ.get("LYCHEETAH_RECEIPT_HMAC_SECRET")
    if secret is None:
        return {}
    if not secret:
        raise RuntimeError("LYCHEETAH_RECEIPT_HMAC_SECRET must not be empty")
    key_id = os.environ.get("LYCHEETAH_RECEIPT_HMAC_KEY_ID")
    if not key_id:
        raise RuntimeError(
            "LYCHEETAH_RECEIPT_HMAC_KEY_ID is required when "
            "LYCHEETAH_RECEIPT_HMAC_SECRET is set"
        )
    return {"hmac_secret": secret.encode("utf-8"), "hmac_key_id": key_id}


def tool_assure_text(
    text: str,
    phase: Literal["input", "output"] = "output",
) -> dict[str, Any]:
    """Issue a privacy-minimised evidence-capped decision receipt for text."""
    receipt = _assurance.evaluate(
        AssuranceEvent(phase=Phase(phase), content=text),
        **_assurance_seal_kwargs(),
    )
    return receipt.to_dict()


def tool_assure_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    scopes: list[str] | None = None,
    side_effect: bool = False,
) -> dict[str, Any]:
    """Issue a pre-execution receipt for a declared tool action.

    The caller remains responsible for truthful side-effect declarations and for
    enforcing the returned ALLOW, REVIEW, or BLOCK disposition.
    """
    receipt = _assurance.evaluate(
        AssuranceEvent(
            phase=Phase.TOOL,
            tool_name=tool_name,
            tool_arguments=arguments or {},
            scopes=tuple(scopes or ()),
            side_effect=side_effect,
            # Approval is trusted host state, never a model-visible MCP argument.
            human_approved=None,
        ),
        **_assurance_seal_kwargs(),
    )
    return receipt.to_dict()


def tool_verify_assurance_receipt(receipt_json: str) -> dict[str, Any]:
    """Verify receipt body integrity; HMAC secrets are never MCP arguments."""
    from ..assurance import AssuranceReceipt, ReceiptError

    try:
        receipt = AssuranceReceipt.from_json(receipt_json)
        verification = receipt.verify()
        payload = {
            "valid": verification.valid,
            "digest": verification.digest,
            "errors": list(verification.errors),
            "warnings": list(verification.warnings),
            "hmac_authenticated": verification.hmac_authenticated,
        }
    except ReceiptError as exc:
        payload = {
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "hmac_authenticated": False,
        }
    return payload


MCP_TOOL_HANDLERS = {
    "check_alignment": tool_check_alignment,
    "check_invariants": tool_check_invariants,
    "suggest_correction": tool_suggest_correction,
    "run_seven_phase": tool_run_seven_phase,
    "check_network_health": tool_check_network_health,
    "configure_guard": tool_configure_guard,
    "sol_assess": tool_sol_assess,
    "assure_text": tool_assure_text,
    "assure_tool": tool_assure_tool,
    "verify_assurance_receipt": tool_verify_assurance_receipt,
}


def build_server():
    """Build the MCP 2.x server without starting a transport."""
    if not MCP_AVAILABLE or MCPServer is None:
        raise RuntimeError(
            "mcp package not installed. Run: pip install 'lycheetah-framework[mcp]'"
        )

    # Validate process-owned sealing configuration before accepting requests.
    _assurance_seal_kwargs()

    server = MCPServer(
        "lycheetah-guard",
        version="1.1.0",
        description="Evidence-bounded alignment heuristics and assurance receipts.",
        instructions=(
            "Treat AURA, Seven-Phase, Psi-Consensus, and Sol outputs as experimental "
            "heuristics. Assurance dispositions are bounded control decisions, not "
            "safety or compliance certification. Enforce BLOCK and route REVIEW to a "
            "human before performing the proposed action."
        ),
    )
    for name, handler in MCP_TOOL_HANDLERS.items():
        server.tool(name=name)(handler)
    return server


# ─────────────────────────────────────────────────────────────
# ENTRY POINTS
# ─────────────────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server over stdio without writing application logs to stdout."""
    try:
        server = build_server()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    server.run("stdio")


def main_http(port: int = 8765) -> None:
    """Run an explicitly requested local Streamable HTTP transport."""
    try:
        server = build_server()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Lycheetah Guard MCP — Streamable HTTP on http://127.0.0.1:{port}/mcp")
    server.run(
        "streamable-http",
        host="127.0.0.1",
        port=port,
        streamable_http_path="/mcp",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Lycheetah Guard MCP")
    parser.add_argument(
        "--http",
        action="store_true",
        help="use local Streamable HTTP instead of the default stdio transport",
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="explicitly select the default stdio transport",
    )
    parser.add_argument("--port", type=int, default=8765, help="HTTP port")
    cli_args = parser.parse_args()
    if cli_args.http and cli_args.stdio:
        parser.error("choose either --http or --stdio")
    if cli_args.http:
        main_http(cli_args.port)
    else:
        main()
