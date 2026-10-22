"""Source-checkout bridge to the canonical implementation tree."""

from pathlib import Path

_CANONICAL = Path(__file__).resolve().parents[2] / "12_IMPLEMENTATIONS" / "core"
if _CANONICAL.is_dir() and str(_CANONICAL) not in __path__:
    __path__.append(str(_CANONICAL))

# Re-export from the canonical ``core.*`` modules, the names the implementation tree
# imports itself by. A relative import here loaded a second copy of each module under
# ``lycheetah.core.*``, so ``report.tes_status == lycheetah.core.MetricStatus.PASS``
# was False for a PASS (RV01 review, 2026-10-23).
from .._bootstrap import ensure_implementation_on_path  # noqa: E402

ensure_implementation_on_path()

from core.semantic_extractor import (  # noqa: E402 -- canonical path must be registered first
    Extraction,
    SemanticExtractor,
    Signal,
)
from core.tri_axial_checker import (  # noqa: E402 -- canonical path must be registered first
    MetricStatus,
    TriAxialChecker,
)

__all__ = [
    "Extraction",
    "MetricStatus",
    "SemanticExtractor",
    "Signal",
    "TriAxialChecker",
]
