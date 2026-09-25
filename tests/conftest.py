"""
Test configuration and shared fixtures for the Lycheetah Framework test suite.

Claim-status tags on tests:
  @pytest.mark.active    — tests for [ACTIVE] claims (proven, computable)
  @pytest.mark.scaffold  — tests for [SCAFFOLD] claims (structure sound, parameters open)
  @pytest.mark.conjecture — tests for [CONJECTURE] claims (exploratory)

All tests use canonical data derived from cascade_simulation_results.json where applicable.
"""

import sys
import os
import pytest

# Add implementations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

# ── LAMAGUE shelf runtime import paths (active, non-colliding packages) ───────
# lamague_runtime (v0.3) · lamague_core (operator algebra v0.3) · lamague_codec
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LAMAGUE_SHELF_ROOTS = [
    os.path.join(_REPO_ROOT, '03_LAMAGUE_L1', '07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE'),
    os.path.join(_REPO_ROOT, '03_LAMAGUE_L1', '12_CORE_LANGUAGE_LINE', 'LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3'),
    os.path.join(_REPO_ROOT, '03_LAMAGUE_L1', '22_REVERSIBLE_COMPRESSION_v1.0', 'src'),
]
for _root in reversed(LAMAGUE_SHELF_ROOTS):
    if _root not in sys.path:
        sys.path.insert(0, _root)



def pytest_configure(config):
    config.addinivalue_line("markers", "active: tests for [ACTIVE] formally proven claims")
    config.addinivalue_line("markers", "scaffold: tests for [SCAFFOLD] structural but unfinished claims")
    config.addinivalue_line("markers", "conjecture: tests for [CONJECTURE] exploratory claims")
    config.addinivalue_line("markers", "lamague_shelf: tests collected from 03_LAMAGUE_L1 shelf runtimes")


# ── Shared fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def simple_blocks():
    """Two contradicting paradigms — minimal cascade test case."""
    from cascade_engine import KnowledgeBlock
    return [
        KnowledgeBlock(
            id="old_claim",
            content="The old explanation",
            domain="mechanics",
            paradigm="classical",
            evidence_strength=0.5,
            explanatory_power=1.2,
            uncertainty=0.6,
        ),
        KnowledgeBlock(
            id="new_claim",
            content="The new explanation",
            domain="mechanics",
            paradigm="modern",
            evidence_strength=0.9,
            explanatory_power=2.5,
            uncertainty=0.2,
        ),
    ]


@pytest.fixture
def physics_blocks():
    """Newtonian → Relativistic paradigm shift — canonical cascade test."""
    from cascade_engine import KnowledgeBlock
    return [
        KnowledgeBlock(
            id="newtonian_mechanics",
            content="F = ma — forces cause accelerations",
            domain="mechanics",
            paradigm="newtonian",
            evidence_strength=0.85,
            explanatory_power=2.0,
            uncertainty=0.15,
        ),
        KnowledgeBlock(
            id="special_relativity",
            content="Space-time curvature — E = mc²",
            domain="mechanics",
            paradigm="relativistic",
            evidence_strength=0.97,
            explanatory_power=2.8,
            uncertainty=0.05,
        ),
    ]


@pytest.fixture
def cascade_engine():
    from cascade_engine import CascadeEngine
    return CascadeEngine()


@pytest.fixture
def aura_checker():
    from aura_checker import AURAChecker
    return AURAChecker()
