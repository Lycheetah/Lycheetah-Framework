from __future__ import annotations

import json
import math
import unittest

from truth_pressure import (
    ClaimEvidence,
    PressureConfig,
    PressureState,
    TruthPressureError,
    evaluate_claim,
    pressure_vector,
    scalar_pressure,
)


def claim(**overrides):
    values = dict(
        claim_id="K",
        evidence_quality=0.9,
        source_independence=0.85,
        reproducibility=0.88,
        provenance_completeness=0.95,
        load_bearing_centrality=0.8,
        scope_of_consequence=0.75,
        contradiction_strength=0.8,
        uncertainty=0.15,
        source_count=5,
    )
    values.update(overrides)
    return ClaimEvidence(**values)


class ValidationTests(unittest.TestCase):
    def test_negative_input(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(evidence_quality=-0.1))
    def test_above_one(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(uncertainty=1.1))
    def test_negative_sources(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(source_count=-1))
    def test_zero_floor(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(), config=PressureConfig(uncertainty_floor=0))
    def test_threshold_order(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(), config=PressureConfig(challenge_threshold=0.8, cascade_threshold=0.6))
    def test_zero_weights(self):
        with self.assertRaises(TruthPressureError): evaluate_claim(claim(), config=PressureConfig(evidence_weights=(0,0,0,0)))


class VectorTests(unittest.TestCase):
    def test_vector_bounded(self):
        for value in pressure_vector(claim()).export().values():
            self.assertGreaterEqual(value, 0); self.assertLessEqual(value, 1)
    def test_zero_component_zeroes_support(self):
        self.assertEqual(pressure_vector(claim(reproducibility=0)).support, 0)
    def test_impact_geometric(self):
        self.assertEqual(pressure_vector(claim(load_bearing_centrality=1, scope_of_consequence=0.25)).impact, 0.5)
    def test_conflict_preserved(self):
        self.assertEqual(pressure_vector(claim(contradiction_strength=0.42)).conflict, 0.42)
    def test_uncertainty_preserved(self):
        self.assertEqual(pressure_vector(claim(uncertainty=0.33)).uncertainty, 0.33)


class ScalarTests(unittest.TestCase):
    def test_finite_zero_uncertainty(self):
        raw, bounded = scalar_pressure(pressure_vector(claim(uncertainty=0)))
        self.assertTrue(math.isfinite(raw)); self.assertTrue(math.isfinite(bounded))
    def test_bounded_unit_interval(self):
        _, bounded = scalar_pressure(pressure_vector(claim()))
        self.assertGreaterEqual(bounded, 0); self.assertLess(bounded, 1)
    def test_uncertainty_lowers_pressure(self):
        low = scalar_pressure(pressure_vector(claim(uncertainty=0.1)))[1]
        high = scalar_pressure(pressure_vector(claim(uncertainty=0.8)))[1]
        self.assertGreater(low, high)
    def test_conflict_raises_pressure(self):
        low = scalar_pressure(pressure_vector(claim(contradiction_strength=0.1)))[1]
        high = scalar_pressure(pressure_vector(claim(contradiction_strength=0.9)))[1]
        self.assertGreater(high, low)
    def test_support_raises_pressure(self):
        low = scalar_pressure(pressure_vector(claim(evidence_quality=0.4)))[1]
        high = scalar_pressure(pressure_vector(claim(evidence_quality=0.95)))[1]
        self.assertGreater(high, low)


class StateTests(unittest.TestCase):
    def test_no_foundation_no_cascade(self):
        result = evaluate_claim(claim())
        self.assertFalse(result.cascade_authorized)
    def test_strong_candidate(self):
        challenger = claim(evidence_quality=0.98, source_independence=0.95, reproducibility=0.96, provenance_completeness=0.99, load_bearing_centrality=1, scope_of_consequence=1, contradiction_strength=1, uncertainty=0.01, source_count=10)
        foundation = claim(evidence_quality=0.5, source_independence=0.4, reproducibility=0.45, provenance_completeness=0.75, contradiction_strength=0.15, uncertainty=0.5, source_count=4)
        result = evaluate_claim(challenger, foundation=foundation)
        self.assertEqual(result.state, PressureState.CASCADE_CANDIDATE)
        self.assertTrue(result.cascade_authorized)
    def test_frontier(self):
        result = evaluate_claim(claim(evidence_quality=0.2, source_independence=0.1, reproducibility=0.05, provenance_completeness=0.3, load_bearing_centrality=1, scope_of_consequence=1, source_count=1, uncertainty=0.8))
        self.assertEqual(result.state, PressureState.HELD_FRONTIER)
    def test_low_pressure_observe(self):
        result = evaluate_claim(claim(contradiction_strength=0.01, load_bearing_centrality=0.1, scope_of_consequence=0.1))
        self.assertEqual(result.state, PressureState.OBSERVE)
    def test_weak_provenance_not_candidate(self):
        result = evaluate_claim(claim(provenance_completeness=0.1), foundation=claim(contradiction_strength=0.1, uncertainty=0.5))
        self.assertFalse(result.cascade_authorized)
    def test_single_source_not_candidate(self):
        result = evaluate_claim(claim(source_count=1), foundation=claim(contradiction_strength=0.1, uncertainty=0.5))
        self.assertFalse(result.cascade_authorized)
    def test_low_conflict_not_candidate(self):
        result = evaluate_claim(claim(contradiction_strength=0.05), foundation=claim(contradiction_strength=0.02, uncertainty=0.5))
        self.assertFalse(result.cascade_authorized)
    def test_tie_not_candidate(self):
        result = evaluate_claim(claim(), foundation=claim())
        self.assertFalse(result.cascade_authorized); self.assertEqual(result.delta_vs_foundation, 0)
    def test_zero_uncertainty_warning(self):
        self.assertTrue(any("prevents infinity" in w for w in evaluate_claim(claim(uncertainty=0)).warnings))


class GateAndExportTests(unittest.TestCase):
    def test_six_gates(self):
        self.assertEqual(len(evaluate_claim(claim()).gates), 6)
    def test_gate_names(self):
        self.assertEqual({g.name for g in evaluate_claim(claim()).gates}, {"support","provenance","independence","reproducibility","source_count","conflict"})
    def test_failed_gate_recorded(self):
        self.assertTrue(any("source_count gate failed" in b for b in evaluate_claim(claim(source_count=0)).blockers))
    def test_compatible_no_conflict_blocker(self):
        self.assertFalse(any("conflict gate failed" in b for b in evaluate_claim(claim(contradiction_strength=0.01)).blockers))
    def test_export_version(self):
        self.assertEqual(evaluate_claim(claim()).export()["truth_pressure_version"], "0.1.0")
    def test_frontier_boundary(self):
        self.assertTrue(any("999" in x for x in evaluate_claim(claim()).claim_boundary))
    def test_not_probability_boundary(self):
        self.assertTrue(any("not the probability" in x for x in evaluate_claim(claim()).claim_boundary))
    def test_json_ready(self):
        json.dumps(evaluate_claim(claim()).export())


if __name__ == "__main__":
    unittest.main()
