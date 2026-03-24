"""
Test configuration and shared fixtures for the Lycheetah Framework test suite.

Claim-status tags on tests:
  @pytest.mark.active    — tests for [ACTIVE] claims (proven, computable)
  @pytest.mark.scaffold  — tests for [SCAFFOLD] claims (structure sound, parameters open)
  @pytest.mark.conjecture — tests for [CONJECTURE] claims (exploratory)

All tests use canonical data derived from cascade_real_results.json where applicable.
"""

import sys
import os
import pytest

# Add implementations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))


def pytest_configure(config):
    config.addinivalue_line("markers", "active: tests for [ACTIVE] formally proven claims")
    config.addinivalue_line("markers", "scaffold: tests for [SCAFFOLD] structural but unfinished claims")
    config.addinivalue_line("markers", "conjecture: tests for [CONJECTURE] exploratory claims")


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
