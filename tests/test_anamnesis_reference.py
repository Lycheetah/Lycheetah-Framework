"""
Tests for anamnesis_reference.py — REFERENCE/SCAFFOLD from shelf specs only.

Does not assert Platonic metaphysics. Does not invent TC scores.
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from anamnesis_reference import (
    PHI,
    PHI_INV,
    MISSING_SPEC,
    phi_map,
    is_phi_fixed_point,
    verify_phi_identities,
    heptagon_constant,
    Structure,
    AgentState,
    visible,
    discovery_event,
    anamnesis_recognize,
    anamnesis_idempotent,
    anamnesis_commutative,
)


class TestPhiCorollary331:
    """ANAMNESIS_FROM_ARCHIVE.md Corollary 3.3.1."""

    @pytest.mark.scaffold
    def test_phi_is_fixed_point_of_map(self):
        assert is_phi_fixed_point(PHI)

    @pytest.mark.scaffold
    def test_phi_map_identity(self):
        assert abs(phi_map(PHI) - PHI) < 1e-12

    @pytest.mark.scaffold
    def test_phi_inv_approx_0618(self):
        # README.md: φ⁻¹ ≈ 0.618
        assert abs(PHI_INV - 0.618) < 5e-4
        assert abs(PHI_INV - 1.0 / PHI) < 1e-12

    @pytest.mark.scaffold
    def test_verify_bundle(self):
        flags = verify_phi_identities()
        assert flags["fixed_point"] is True
        assert flags["phi_inv_matches"] is True
        assert flags["phi_inv_approx_0618"] is True


class TestHeptagonConstant:
    @pytest.mark.scaffold
    def test_cos_pi_over_7_approx_09010(self):
        # README.md: cos(π/7) ≈ 0.9010
        c = heptagon_constant()
        assert abs(c - 0.9010) < 5e-4
        assert abs(c - math.cos(math.pi / 7.0)) < 1e-15


class TestAgentAndVisibility:
    """Defs 3.2–3.3 / Theorem 3.2 — structural only; Scale supplied by caller."""

    @pytest.mark.scaffold
    def test_visible_threshold(self):
        agent = AgentState(knowledge=set(), resolution=2.0, capacity=10)
        # 1/R = 0.5 → structures with scale > 0.5 visible
        structs = [
            Structure("coarse", 2.0),
            Structure("fine", 0.2),
        ]
        vis = visible(agent, structs)
        assert "coarse" in vis
        assert "fine" not in vis

    @pytest.mark.scaffold
    def test_discovery_on_resolution_increase(self):
        structs = [Structure("S", 0.4)]
        before = AgentState(resolution=1.0, capacity=5)   # 1/R=1.0 → S hidden
        after = AgentState(resolution=4.0, capacity=5)    # 1/R=0.25 → S visible
        assert discovery_event(before, after, "S", structs) is True
        assert discovery_event(before, before, "S", structs) is False

    @pytest.mark.scaffold
    def test_agent_rejects_non_positive_resolution(self):
        with pytest.raises(ValueError):
            AgentState(resolution=0.0, capacity=1.0)

    @pytest.mark.scaffold
    def test_structure_rejects_non_positive_scale(self):
        with pytest.raises(ValueError):
            Structure("x", 0.0)


class TestAnamnesisOperator:
    """Definition 3.4 properties that are checkable without inventing M."""

    @pytest.mark.scaffold
    def test_monotonic_knowledge(self):
        a0 = AgentState(knowledge={"a"}, resolution=1.0, capacity=5)
        a1 = anamnesis_recognize(a0, "b")
        assert a1.knowledge >= a0.knowledge
        assert "b" in a1.knowledge

    @pytest.mark.scaffold
    def test_idempotent(self):
        a0 = AgentState(knowledge=set(), resolution=1.0, capacity=5)
        assert anamnesis_idempotent(a0, "S") is True

    @pytest.mark.scaffold
    def test_commutative(self):
        a0 = AgentState(knowledge=set(), resolution=1.0, capacity=5)
        assert anamnesis_commutative(a0, "S1", "S2") is True

    @pytest.mark.scaffold
    def test_capacity_guard(self):
        a0 = AgentState(knowledge={"a"}, resolution=1.0, capacity=1.0)
        with pytest.raises(ValueError):
            anamnesis_recognize(a0, "b")


class TestMissingSpecHonesty:
    @pytest.mark.scaffold
    def test_missing_spec_nonempty_and_mentions_tc(self):
        assert len(MISSING_SPEC) >= 5
        blob = " ".join(MISSING_SPEC).lower()
        assert "tc" in blob
        assert "scale" in blob
