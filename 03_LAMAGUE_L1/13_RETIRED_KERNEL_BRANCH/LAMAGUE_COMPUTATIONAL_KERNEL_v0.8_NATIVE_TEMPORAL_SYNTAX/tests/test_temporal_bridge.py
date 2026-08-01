from __future__ import annotations
import copy, json, unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lamague_temporal.bridge import (
    BridgeError, Provenance, Observability, packet_from_dict, analyze, analyze_dict,
)


def load(name):
    return json.loads((ROOT / "temporal_examples" / name).read_text(encoding="utf-8"))


class PacketValidationTests(unittest.TestCase):
    def test_load_clean(self):
        packet = packet_from_dict(load("clean_control_packet.json"))
        self.assertEqual(packet.packet_id, "CLEAN-CONTROL")

    def test_invalid_observability(self):
        data = load("clean_control_packet.json")
        data["observability_class"] = "OMNISCIENT"
        with self.assertRaises(BridgeError):
            packet_from_dict(data)

    def test_duplicate_branch_id(self):
        data = load("clean_control_packet.json")
        data["evidence"].append(copy.deepcopy(data["evidence"][0]))
        with self.assertRaises(BridgeError):
            packet_from_dict(data)

    def test_missing_conflict_branch(self):
        data = load("clean_control_packet.json")
        data["conflicts"] = [{"conflict_id":"c","branch_ids":["obs_total","missing"],"dimensions":["VALUE"]}]
        with self.assertRaises(BridgeError):
            packet_from_dict(data)

    def test_bad_threshold_order(self):
        data = load("clean_control_packet.json")
        data["boundary"]["discrepancy_threshold"] = 0.8
        with self.assertRaises(BridgeError):
            packet_from_dict(data)

    def test_zero_scale(self):
        data = load("clean_control_packet.json")
        data["intents"][0]["scale"] = 0
        with self.assertRaises(BridgeError):
            packet_from_dict(data)

    def test_duplicate_intent_pair(self):
        data = load("clean_control_packet.json")
        data["intents"].append(copy.deepcopy(data["intents"][0]))
        with self.assertRaises(BridgeError):
            packet_from_dict(data)


class EvidenceTests(unittest.TestCase):
    def test_exact_operator_preserved(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        obs = next(x for x in result["evidence_branches"] if x["branch_id"] == "obs_tur_printed")
        self.assertEqual(obs["operator"], "≥")
        self.assertEqual(obs["value"], "100 ≥ 110 → PASS")

    def test_provenance_preserved(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        prov = {x["branch_id"]: x["provenance"] for x in result["evidence_branches"]}
        self.assertEqual(prov["obs_tur_printed"], "OBSERVED")
        self.assertEqual(prov["decl_tur_rule"], "DECLARED")
        self.assertEqual(prov["calc_tur_check"], "CALCULATED")

    def test_unresolved_conflict_blocks_selection(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertIn("silent_branch_selection", result["blocked_calculations"])
        self.assertIn("dependent_calculation_from_unresolved_conflict", result["blocked_calculations"])

    def test_auto_value_conflict(self):
        data = load("clean_control_packet.json")
        data["evidence"][1]["value"] = 9e-21
        result = analyze_dict(data)
        auto = next(x for x in result["conflicts"] if x["conflict_id"] == "AUTO::entropy.total")
        self.assertIn("VALUE", auto["dimensions"])

    def test_auto_unit_conflict(self):
        data = load("clean_control_packet.json")
        data["evidence"][1]["unit"] = "J/K/tick"
        result = analyze_dict(data)
        auto = next(x for x in result["conflicts"] if x["conflict_id"] == "AUTO::entropy.total")
        self.assertIn("UNIT", auto["dimensions"])

    def test_equal_branches_no_auto_conflict(self):
        result = analyze_dict(load("clean_control_packet.json"))
        self.assertEqual(result["conflicts"], ())

    def test_hash_deterministic(self):
        data = load("clean_control_packet.json")
        a = analyze_dict(data)
        b = analyze_dict(data)
        self.assertEqual(a["packet_hash"], b["packet_hash"])
        self.assertEqual(a["evidence_hash"], b["evidence_hash"])

    def test_hash_changes_on_operator_change(self):
        data = load("tim_silent_repair_packet.json")
        a = analyze_dict(data)
        data["evidence"][0]["operator"] = "≤"
        b = analyze_dict(data)
        self.assertNotEqual(a["evidence_hash"], b["evidence_hash"])


class TemporalMetricTests(unittest.TestCase):
    def test_clean_stable(self):
        result = analyze_dict(load("clean_control_packet.json"))
        self.assertEqual(result["status"], "STABLE")
        self.assertEqual(result["rho_recovery_status"], "NOT_APPLICABLE")

    def test_silent_repair_critical(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertEqual(result["status"], "CRITICAL")
        self.assertEqual([x["d_t"] for x in result["d_t"]], [0.0,0.0,1.0,1.0,1.0])

    def test_silent_repair_mu(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertAlmostEqual(result["mu_drift"], 0.6)

    def test_silent_repair_positive_slope(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertGreater(result["rho_drift"], 0)

    def test_persistent_breach_no_recovery(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertEqual(result["rho_recovery"], 0.0)
        self.assertEqual(result["rho_recovery_status"], "VALID")

    def test_invariant_ratio(self):
        result = analyze_dict(load("tim_silent_repair_packet.json"))
        self.assertAlmostEqual(result["invariant_preservation"], 0.4)

    def test_missing_intent_insufficient(self):
        result = analyze_dict(load("missing_intent_packet.json"))
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertIsNone(result["d_t"])
        self.assertIn("drift_metrics_missing_intent_action_pair", result["blocked_calculations"])

    def test_black_box_interpretation(self):
        result = analyze_dict(load("black_box_mimic_packet.json"))
        self.assertEqual(result["permitted_interpretation"], "behavioral anomaly signal only")
        self.assertEqual(result["status"], "STABLE")
        self.assertIn("hidden_alignment_claim", result["blocked_calculations"])

    def test_no_events_blocks_metrics(self):
        data = load("clean_control_packet.json")
        data["intents"] = []
        data["actions"] = []
        result = analyze_dict(data)
        self.assertIsNone(result["mu_drift"])
        self.assertIn("drift_metrics_no_temporal_events", result["blocked_calculations"])

    def test_multiple_dimensions_weighted(self):
        data = load("clean_control_packet.json")
        data["intents"] = [
            {"timestamp":1,"key":"a","value":1,"scale":1,"weight":3},
            {"timestamp":1,"key":"b","value":1,"scale":1,"weight":1}
        ]
        data["actions"] = [
            {"timestamp":1,"key":"a","value":0},
            {"timestamp":1,"key":"b","value":1}
        ]
        result = analyze_dict(data)
        self.assertAlmostEqual(result["d_t"][0]["d_t"], 0.75)

    def test_limitations_present(self):
        result = analyze_dict(load("clean_control_packet.json"))
        joined = " ".join(result["limitations"])
        self.assertIn("not an alignment guarantee", joined)
        self.assertIn("does not detect sufficiently deceptive", joined)


if __name__ == "__main__":
    unittest.main()

class TemporalBenchmarkTests(unittest.TestCase):
    def test_seed_manifest(self):
        from lamague_temporal.benchmark import run_manifest
        report = run_manifest(ROOT / "temporal_benchmark" / "manifest.json")
        self.assertEqual(report["case_count"], 8)
        self.assertEqual(report["expected_matches"], 8)
        self.assertEqual(report["accuracy"], 1.0)
