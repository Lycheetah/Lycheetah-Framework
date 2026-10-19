"""Do not infer human free will or consent from operational compliance telemetry."""
from dataclasses import dataclass

@dataclass(frozen=True)
class EvidenceAssessment:
    plan_adherence: bool
    grant_recorded: bool
    observed_execution_authorised: bool
    comprehension_verified: str
    coercion_absent: str
    metaphysical_free_will: str
    human_worth_score: None = None


def assess(*, followed_original_plan: bool, current_grant_valid: bool,
           action_inside_grant: bool, identity_verified: bool) -> EvidenceAssessment:
    return EvidenceAssessment(
        plan_adherence=followed_original_plan,
        grant_recorded=current_grant_valid,
        observed_execution_authorised=bool(current_grant_valid and action_inside_grant
                                           and identity_verified),
        comprehension_verified="UNKNOWN (needs user evidence)",
        coercion_absent="UNKNOWN (no inference from compliance)",
        metaphysical_free_will="UNRESOLVED",
    )
