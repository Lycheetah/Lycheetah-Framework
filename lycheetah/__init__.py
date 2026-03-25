"""
Lycheetah Framework
===================
Constitutional AI alignment — TRI-AXIAL metrics, Seven Invariants,
Sol self-protocol, Psi-Consensus, CHRYSOPOEIA transformation cycle.

Quick start:
    from lycheetah import check
    report = check("Any AI-generated text here")
    print(report.alignment_percent, report.overall_pass)

Full API: lycheetah.core, lycheetah.applications
MCP server: python -m lycheetah.guard
Web demo:   python -m lycheetah.web
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__  = "Mackenzie Conor James Clark"
__license__ = "MIT"

import sys
import os

# Make core and applications importable as lycheetah.core / lycheetah.applications
_HERE = os.path.dirname(os.path.abspath(__file__))
_IMPL = os.path.join(os.path.dirname(_HERE), "12_IMPLEMENTATIONS")
if _IMPL not in sys.path:
    sys.path.insert(0, _IMPL)


def check(text: str, context: str = "") -> "AURATextReport":
    """
    Run a full constitutional alignment check on any text.

    Returns an AURATextReport with:
        .alignment_percent  — 0-100 score
        .overall_pass       — bool
        .tes_score          — Trust Entropy Score (threshold 0.70)
        .vtr_score          — Value Transfer Ratio (threshold 1.50)
        .pai_score          — Purpose Alignment Index (threshold 0.80)
        .invariants         — list of InvariantResult
        .summary            — one-line plain-English verdict

    Example:
        import lycheetah
        r = lycheetah.check("I absolutely guarantee this is correct.")
        print(r.alignment_percent)   # e.g. 61.4
        print(r.overall_pass)        # False
        for inv in r.invariants:
            print(inv.name, inv.passed)
    """
    from applications.aura_text_checker import AURATextAnalyser
    return AURATextAnalyser().analyse(text)


def sol_assess(text: str, context: str = "") -> str:
    """
    Run the Sol self-assessment on any text.

    Returns a plain-English constitutional audit string including:
    - PGF filter result (Protector / Healer / Beacon)
    - Seven invariant checks
    - Session coherence trend
    - Detected mode and emotional register
    """
    from core.sol_self_protocol import SolSelfProtocol
    return SolSelfProtocol().assess_full(text, context)


__all__ = ["check", "sol_assess", "__version__"]
