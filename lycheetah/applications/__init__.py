"""Source-checkout bridge to the canonical application implementation tree."""

from pathlib import Path

_CANONICAL = Path(__file__).resolve().parents[2] / "12_IMPLEMENTATIONS" / "applications"
if _CANONICAL.is_dir() and str(_CANONICAL) not in __path__:
    __path__.append(str(_CANONICAL))

from .aura_text_checker import AURATextAnalyser, AURATextReport, InvariantResult

__all__ = ["AURATextAnalyser", "AURATextReport", "InvariantResult"]
