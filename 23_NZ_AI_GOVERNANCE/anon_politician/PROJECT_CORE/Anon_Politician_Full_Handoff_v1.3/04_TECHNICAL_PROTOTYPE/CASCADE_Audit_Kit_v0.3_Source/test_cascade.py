import unittest
from cascade import KnowledgeBlock, KnowledgeGraph


class TestCascadeSafetyProperties(unittest.TestCase):
    def setUp(self):
        self.graph = KnowledgeGraph([
            KnowledgeBlock("F1", "A foundational commitment", "normative_commitment", status="source_asserted"),
            KnowledgeBlock("T1", "A testable hypothesis", "empirical_hypothesis", dependencies=["F1"], status="pending_review"),
            KnowledgeBlock("E1", "A proposal", "policy_proposal", dependencies=["T1"], status="pending_review"),
            KnowledgeBlock("T2", "A competing hypothesis", "empirical_hypothesis", contradicts=["T1"], status="pending_review"),
            KnowledgeBlock("E2", "A proposal depending on the competing hypothesis", "policy_proposal", dependencies=["T2"], status="pending_review"),
            KnowledgeBlock("U1", "An unrelated hypothesis", "empirical_hypothesis", status="pending_review"),
        ])

    def test_dependency_change_marks_transitive_dependents(self):
        affected = self.graph.propose_cascade("F1", "New evidence challenges F1").affected_block_ids
        self.assertIn("T1", affected)
        self.assertIn("E1", affected)

    def test_contradiction_partner_and_its_dependents_are_reviewed(self):
        review = self.graph.propose_cascade("F1", "New evidence challenges F1")
        self.assertIn("T2", review.affected_block_ids)
        self.assertIn("E2", review.affected_block_ids)

    def test_unrelated_block_is_not_reviewed(self):
        review = self.graph.propose_cascade("F1", "New evidence challenges F1")
        self.assertNotIn("U1", review.affected_block_ids)
        self.assertFalse(self.graph.blocks["U1"].review_required)

    def test_no_automatic_status_changes(self):
        before = {k: b.status for k, b in self.graph.blocks.items()}
        review = self.graph.propose_cascade("F1", "Test change")
        after = {k: b.status for k, b in self.graph.blocks.items()}
        self.assertEqual(before, after)
        self.assertEqual(review.automatic_status_changes, [])

    def test_conflicting_hypothesis_is_not_deleted(self):
        self.graph.propose_cascade("F1", "Test change")
        self.assertIn("T2", self.graph.blocks)
        self.assertIn(("T2", "T1"), self.graph.conflicts())

    def test_decision_is_audited(self):
        self.graph.record_decision("T1", "mixed_evidence", "Evidence is mixed", "2026-10-14T00:00:00Z", "reviewer-1")
        block = self.graph.blocks["T1"]
        self.assertEqual(block.status, "mixed_evidence")
        self.assertEqual(len(block.history), 1)
        self.assertEqual(block.history[0]["prior_status"], "pending_review")
        self.assertEqual(block.history[0]["new_status"], "mixed_evidence")

    def test_missing_dependency_fails_fast(self):
        with self.assertRaises(ValueError):
            KnowledgeGraph([KnowledgeBlock("X", "Broken", "empirical_claim", dependencies=["MISSING"])])

    def test_empty_rationale_is_rejected(self):
        with self.assertRaises(ValueError):
            self.graph.record_decision("T1", "mixed_evidence", "  ", "2026-10-14T00:00:00Z", "reviewer-1")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            self.graph.record_decision("T1", "definitely_true", "Unsupported status test", "2026-10-14T00:00:00Z", "reviewer-1")

    def test_dependency_cycle_terminates_and_does_not_review_start_as_affected(self):
        cyclic = KnowledgeGraph([
            KnowledgeBlock("A", "A claim", "empirical_hypothesis", dependencies=["B"]),
            KnowledgeBlock("B", "B claim", "empirical_hypothesis", dependencies=["A"]),
        ])
        review = cyclic.propose_cascade("A", "Cycle termination test")
        self.assertEqual(review.affected_block_ids, ["B"])

    def test_self_dependency_rejected(self):
        with self.assertRaises(ValueError):
            KnowledgeBlock("SELF", "Invalid self-link", "empirical_claim", dependencies=["SELF"])


if __name__ == "__main__":
    unittest.main()
