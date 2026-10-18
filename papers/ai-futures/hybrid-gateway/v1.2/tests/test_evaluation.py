import unittest
from run_eval import run


class EvaluationTests(unittest.TestCase):
    def test_scoring_dimensions_and_counts(self):
        result = run()
        self.assertEqual(len(result["cases"]), 22)
        self.assertTrue(result["ledger_chain_verified"])
        self.assertEqual(result["scores"]["B0"]["correct"], 8)
        self.assertEqual(result["scores"]["B1"]["correct"], 13)
        self.assertEqual(result["scores"]["H1"]["correct"], 22)

    def test_no_citation_unanchored_to_operator_source(self):
        result = run()
        for row in result["cases"]:
            for system in ("B0", "B1", "H1"):
                self.assertTrue(row[system]["citation_anchor_valid"], (row["id"], system))

    def test_retraction_is_worse_for_bitemporal_without_version_events(self):
        result = run()
        chosen = next(c for c in result["cases"] if c["id"] == "q11_retraction_known")
        self.assertFalse(chosen["B1"]["correct"])
        self.assertTrue(chosen["H1"]["correct"])


if __name__ == "__main__":
    unittest.main()
