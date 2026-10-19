"""Fixed-fixture tests for proposal audit, not validation of human autonomy."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"code"))
from choice_surface import ChoiceSurface

class ChoiceSurfaceTests(unittest.TestCase):
    def test_missing_evidence_not_scored_as_failure_or_success(self):
        a=ChoiceSurface().audit()
        self.assertEqual(len(a["unknowns"]),9)
        self.assertIsNone(a["human_free_will_score"])
        self.assertFalse(a["identity_or_consent_proven"])
    def test_hidden_refusal_red_flag(self):
        a=ChoiceSurface(meaningful_no_action="absent").audit()
        self.assertIn("meaningful_no_action", a["red_flags"])
    def test_coercive_dependency_red_flag(self):
        a=ChoiceSurface(dependency_pressure="present").audit()
        self.assertIn("dependency_pressure", a["red_flags"])
    def test_user_defined_alternative_is_distinct_from_multiple_choices(self):
        a=ChoiceSurface(meaningful_no_action="present",custom_alternative="absent").audit()
        self.assertIn("custom_alternative",a["red_flags"])
        self.assertIn("meaningful_no_action",a["observed_supports"])
    def test_good_fixture_still_not_proof_of_consent(self):
        a=ChoiceSurface(**{k:"absent" if k=="dependency_pressure" else "present"
                           for k in ChoiceSurface.__dataclass_fields__}).audit()
        self.assertFalse(a["identity_or_consent_proven"])
        self.assertEqual(a["red_flags"],[])
        self.assertEqual(a["unknowns"],[])
        self.assertIsNone(a["human_free_will_score"])
    def test_invalid_evidence_state_is_rejected(self):
        with self.assertRaises(ValueError):ChoiceSurface(accurate_purpose="verified")
    def test_exit_with_penalty_flagged(self):
        a=ChoiceSurface(nonpunitive_exit="absent",accurate_purpose="present").audit()
        self.assertIn("nonpunitive_exit",a["red_flags"])
if __name__=="__main__": unittest.main()
