"""Source-checkout bridge to the canonical implementation tree."""

from pathlib import Path

_CANONICAL = Path(__file__).resolve().parents[2] / "12_IMPLEMENTATIONS" / "core"
if _CANONICAL.is_dir() and str(_CANONICAL) not in __path__:
    __path__.append(str(_CANONICAL))

from .semantic_extractor import Extraction, SemanticExtractor, Signal
from .tri_axial_checker import MetricStatus, TriAxialChecker

__all__ = [
    "Extraction",
    "MetricStatus",
    "SemanticExtractor",
    "Signal",
    "TriAxialChecker",
]
