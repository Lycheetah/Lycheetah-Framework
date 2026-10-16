import unittest
from witness_provenance_probe import run_probe

class WitnessProvenanceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = run_probe()
        cls.cases = {item["case"]: item for item in cls.data["cases"]}

    def test_honest_current_witness_is_accepted(self):
        self.assertEqual(self.cases["honest_witness"]["observed"], "ACCEPT")

    def test_rehashed_forged_current_witness_is_accepted_by_source_equivalent_gate(self):
        self.assertEqual(self.cases["unkeyed_digest_witness_with_substituted_evidence_requirement_and_fake_receipt_digest"]["observed"], "ACCEPT")

    def test_authenticated_candidate_accepts_genuine_witness(self):
        self.assertEqual(self.cases["strict_authenticated_witness"]["observed"], "ACCEPT")

    def test_authenticated_candidate_rejects_mutated_witness(self):
        self.assertEqual(self.cases["strict_candidate_with_mutated_evidence_and_public_hash_substitution"]["observed"], "REJECT")

    def test_authenticated_candidate_rejects_replay(self):
        self.assertEqual(self.cases["strict_candidate_replay_after_consumption"]["observed"], "REJECT")

if __name__ == "__main__":
    unittest.main(verbosity=2)
