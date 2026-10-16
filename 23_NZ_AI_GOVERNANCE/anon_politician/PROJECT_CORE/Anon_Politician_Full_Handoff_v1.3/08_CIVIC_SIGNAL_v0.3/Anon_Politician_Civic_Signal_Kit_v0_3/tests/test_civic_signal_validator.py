import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from civic_signal_validator import validate  # noqa: E402


def base(method="open_opt_in"):
    return {
        "study_id": "TEST-001",
        "topic": "Test policy",
        "recruitment": {
            "method": method,
            "target_population": "people who participated",
            "sampling_frame": "open link" if method == "open_opt_in" else "documented frame",
            "probability_selection": False,
            "sample_size": 100,
            "response_rate": None,
            "weighting_method": "",
            "weighting_plan": "none",
            "uncertainty_method": "none for population estimation",
        },
        "claims": ["participant_themes"],
        "survey_design": {
            "question_wording_published": True,
            "undecided_option": True,
            "evidence_brief_provided": False,
            "evidence_sources_published": False,
            "initial_response_collected": False,
            "post_information_response_collected": False,
        },
        "governance": {
            "personal_data_collected": False,
            "accessibility_plan": True,
            "maori_engagement_plan": True,
        },
        "decision_context": {
            "decision_owner": "Human decision owner",
            "open_to_change": "Defined scope",
            "response_commitment": "Publish response",
        },
        "te_tiriti_or_maori_relevance": True,
    }


def codes(findings):
    return {item["code"] for item in findings}


class CivicSignalValidatorTests(unittest.TestCase):
    def test_open_pulse_with_participant_claim_is_not_population_claim(self):
        f = validate(base())
        self.assertNotIn("UNSUPPORTED_POPULATION_CLAIM", codes(f))
        self.assertIn("DESCRIPTIVE_SCOPE", codes(f))

    def test_open_pulse_cannot_claim_national_consensus(self):
        r = base()
        r["claims"] = ["national_consensus"]
        self.assertIn("UNSUPPORTED_POPULATION_CLAIM", codes(validate(r)))

    def test_open_pulse_weighting_still_needs_caveat(self):
        r = base()
        r["recruitment"]["weighting_method"] = "age and region weights"
        self.assertIn("WEIGHTING_NOT_CERTIFICATION", codes(validate(r)))

    def test_stakeholder_submissions_cannot_claim_representativeness(self):
        r = base("stakeholder_submissions")
        r["claims"] = ["representative"]
        self.assertIn("UNSUPPORTED_POPULATION_CLAIM", codes(validate(r)))

    def test_deliberative_panel_cannot_claim_population_estimate(self):
        r = base("deliberative_panel")
        r["claims"] = ["population_estimate"]
        self.assertIn("PANEL_NOT_POPULATION_POLL", codes(validate(r)))

    def test_probability_sample_missing_frame_has_error(self):
        r = base("probability_sample")
        r["recruitment"]["sampling_frame"] = ""
        self.assertIn("SAMPLE_FRAME_MISSING", codes(validate(r)))

    def test_probability_sample_population_claim_needs_probability_selection(self):
        r = base("probability_sample")
        r["claims"] = ["population_estimate"]
        self.assertIn("PROBABILITY_SELECTION_UNDOCUMENTED", codes(validate(r)))
        self.assertIn("POPULATION_CLAIM_DESIGN_INCOMPLETE", codes(validate(r)))

    def test_complete_declared_probability_design_still_requires_human_review(self):
        r = base("probability_sample")
        r["claims"] = ["population_estimate"]
        r["recruitment"].update({
            "sampling_frame": "complete hypothetical list",
            "probability_selection": True,
            "response_rate": 0.62,
            "uncertainty_method": "design-based variance estimator",
            "weighting_plan": "calibrated to published population margins with sensitivity checks",
        })
        f = validate(r)
        self.assertIn("HUMAN_METHOD_REVIEW_REQUIRED", codes(f))
        self.assertNotIn("POPULATION_CLAIM_DESIGN_INCOMPLETE", codes(f))

    def test_informed_preference_claim_without_information_step_is_error(self):
        r = base()
        r["claims"] = ["informed_preference"]
        self.assertIn("INFORMED_PREFERENCE_UNSUPPORTED", codes(validate(r)))

    def test_personal_data_without_privacy_notice_errors(self):
        r = base()
        r["governance"]["personal_data_collected"] = True
        r["governance"]["privacy_notice_published"] = False
        self.assertIn("PRIVACY_NOTICE_MISSING", codes(validate(r)))

    def test_personal_data_requires_retention_policy(self):
        r = base()
        r["governance"].update({
            "personal_data_collected": True,
            "privacy_notice_published": True,
            "consent_or_lawful_basis_reviewed": True,
            "security_review_complete": True,
            "retention_policy_published": False,
        })
        self.assertIn("RETENTION_POLICY_MISSING", codes(validate(r)))

    def test_missing_decision_response_commitment_warns(self):
        r = base()
        r["decision_context"]["response_commitment"] = ""
        self.assertIn("RESPONSE_COMMITMENT_MISSING", codes(validate(r)))

    def test_unknown_method_fails_early(self):
        r = base("likes_on_social_media")
        self.assertIn("UNKNOWN_METHOD", codes(validate(r)))

    def test_invalid_sample_size_errors(self):
        r = base()
        r["recruitment"]["sample_size"] = "many"
        self.assertIn("INVALID_SAMPLE_SIZE", codes(validate(r)))

    def test_pre_post_comparison_requires_matched_steps(self):
        r = base()
        r["claims"] = ["changed_after_learning"]
        r["survey_design"]["initial_response_collected"] = True
        self.assertIn("INFORMED_PREFERENCE_UNSUPPORTED", codes(validate(r)))

    def test_missing_maori_engagement_plan_warns_when_relevant(self):
        r = base()
        r["governance"]["maori_engagement_plan"] = False
        self.assertIn("MAORI_ENGAGEMENT_REVIEW", codes(validate(r)))


if __name__ == "__main__":
    unittest.main()
