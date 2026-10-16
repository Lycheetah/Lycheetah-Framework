#!/usr/bin/env python3
"""Metadata-based safeguards for claims about civic participation evidence.

This validator checks declared study metadata and proposed claim language. It
cannot verify that the declared sampling method was actually followed, and it
is not a certification of representativeness or survey quality.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any

METHODS = {
    "open_opt_in",
    "probability_sample",
    "deliberative_panel",
    "targeted_consultation",
    "stakeholder_submissions",
}
POPULATION_CLAIMS = {
    "representative",
    "population_estimate",
    "national_consensus",
    "majority_of_new_zealanders",
    "public_mandate",
}


def finding(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def validate(record: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    recruitment = record.get("recruitment") or {}
    survey = record.get("survey_design") or {}
    governance = record.get("governance") or {}
    context = record.get("decision_context") or {}
    claims = set(record.get("claims", []) or [])
    method = recruitment.get("method")

    if not record.get("study_id"):
        out.append(finding("error", "MISSING_STUDY_ID", "Give the study a stable ID."))
    if method not in METHODS:
        out.append(finding("error", "UNKNOWN_METHOD", f"Recruitment method must be one of: {', '.join(sorted(METHODS))}."))
        return out

    n = recruitment.get("sample_size")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        out.append(finding("error", "INVALID_SAMPLE_SIZE", "sample_size must be a non-negative integer."))

    # Participation method sets the default inferential ceiling.
    if method in {"open_opt_in", "targeted_consultation", "stakeholder_submissions"}:
        forbidden = claims & POPULATION_CLAIMS
        if forbidden:
            out.append(finding("error", "UNSUPPORTED_POPULATION_CLAIM", f"{method} does not by itself support these claims: {', '.join(sorted(forbidden))}. Relabel as views of participating/responding people or provide a separate valid population-estimation design."))
        else:
            out.append(finding("info", "DESCRIPTIVE_SCOPE", "Report results as views/themes among the people who participated or submitted; do not infer prevalence in the whole population."))

    if method == "open_opt_in" and recruitment.get("weighting_method"):
        out.append(finding("warning", "WEIGHTING_NOT_CERTIFICATION", "Weighting an opt-in sample does not by itself establish representativeness; document what it corrects and residual selection risks."))

    if method == "probability_sample":
        requirements = [
            (bool(recruitment.get("sampling_frame")), "SAMPLE_FRAME_MISSING", "Document the target-population sampling frame."),
            (recruitment.get("probability_selection") is True, "PROBABILITY_SELECTION_UNDOCUMENTED", "Document how units were selected with known/non-zero selection probabilities."),
            (recruitment.get("response_rate") is not None or bool(recruitment.get("nonresponse_assessment")), "NONRESPONSE_UNASSESSED", "Report response rate or describe a documented nonresponse assessment."),
            (bool(recruitment.get("uncertainty_method")), "UNCERTAINTY_METHOD_MISSING", "Document the estimator and uncertainty method, including design effects where relevant."),
            (bool(recruitment.get("weighting_plan")), "WEIGHTING_PLAN_MISSING", "State whether weighting is used and why; if not used, explain why the design/estimand permits it."),
        ]
        for okay, code, msg in requirements:
            if not okay:
                out.append(finding("error", code, msg))
        if claims & POPULATION_CLAIMS and any(x[0] is False for x in requirements):
            out.append(finding("error", "POPULATION_CLAIM_DESIGN_INCOMPLETE", "Do not issue population-level claims until the sampling and estimation requirements are reviewed."))
        if claims & POPULATION_CLAIMS and all(x[0] for x in requirements):
            out.append(finding("warning", "HUMAN_METHOD_REVIEW_REQUIRED", "Declared metadata is necessary but not sufficient: a qualified reviewer must assess frame coverage, response/nonresponse, question wording, weights, design effects and actual execution before publication."))

    if method == "deliberative_panel":
        panel_claims = claims & {"representative", "population_estimate", "national_consensus", "majority_of_new_zealanders", "public_mandate"}
        if panel_claims:
            out.append(finding("error", "PANEL_NOT_POPULATION_POLL", "A deliberative panel may report the considered judgement of its participants; it is not automatically a population poll or national consensus."))
        if not recruitment.get("selection_and_stratification"):
            out.append(finding("warning", "PANEL_SELECTION_UNCLEAR", "Document recruitment/selection, stratification goals, attrition and who may have been missed."))
        if not survey.get("evidence_pack_version"):
            out.append(finding("warning", "PANEL_EVIDENCE_NOT_VERSIONED", "Record the balanced evidence pack and version used during deliberation."))
        if not survey.get("participant_questions_allowed"):
            out.append(finding("warning", "PANEL_QUESTIONING_NOT_DOCUMENTED", "Record how participants can question evidence and hear relevant perspectives."))

    # Preference quality and question design.
    if not survey.get("question_wording_published"):
        out.append(finding("warning", "WORDING_NOT_PUBLISHED", "Publish exact question wording and response options."))
    if not survey.get("undecided_option"):
        out.append(finding("warning", "NO_UNSURE_OPTION", "Consider an explicit 'not sure / need more information' option."))
    if survey.get("evidence_brief_provided") and not survey.get("evidence_sources_published"):
        out.append(finding("warning", "EVIDENCE_BRIEF_UNSOURCED", "If policy information is provided, publish sources and balance notes."))
    if survey.get("initial_response_collected") and not survey.get("post_information_response_collected"):
        out.append(finding("info", "NO_PRE_POST_COMPARISON", "The design records initial views only; do not describe them as post-deliberation or informed preferences."))
    if claims & {"informed_preference", "changed_after_learning"} and not (survey.get("initial_response_collected") and survey.get("post_information_response_collected") and survey.get("evidence_brief_provided")):
        out.append(finding("error", "INFORMED_PREFERENCE_UNSUPPORTED", "Claims about informed or changed preferences require a documented information exposure and comparable pre/post measure."))

    # Governance gates before real-world collection.
    if governance.get("personal_data_collected") is True:
        for field, code, message in [
            ("privacy_notice_published", "PRIVACY_NOTICE_MISSING", "Do not collect personal data without a clear published privacy notice."),
            ("retention_policy_published", "RETENTION_POLICY_MISSING", "Specify retention/deletion periods and access controls."),
            ("consent_or_lawful_basis_reviewed", "LEGAL_BASIS_UNREVIEWED", "Document consent or the reviewed lawful basis for processing."),
            ("security_review_complete", "SECURITY_REVIEW_MISSING", "Complete a proportionate security/threat review before collection."),
        ]:
            if not governance.get(field):
                out.append(finding("error", code, message))
    else:
        out.append(finding("info", "NO_PERSONAL_DATA_DECLARED", "No personal data is declared in this metadata; confirm this remains true for any free-text or contact fields."))

    if not governance.get("accessibility_plan"):
        out.append(finding("warning", "ACCESSIBILITY_PLAN_MISSING", "Document accessible and non-digital participation routes appropriate to the target audience."))
    if record.get("te_tiriti_or_maori_relevance") and not governance.get("maori_engagement_plan"):
        out.append(finding("warning", "MAORI_ENGAGEMENT_REVIEW", "Document appropriate Māori/iwi engagement and governance; do not treat a generic survey as a substitute."))

    for key, code, msg in [
        ("decision_owner", "DECISION_OWNER_MISSING", "State who is accountable for the decision."),
        ("open_to_change", "OPEN_SCOPE_MISSING", "State what is genuinely open to influence and what is fixed."),
        ("response_commitment", "RESPONSE_COMMITMENT_MISSING", "Commit to publishing how the input was considered, including reasons for not adopting suggestions."),
    ]:
        if not context.get(key):
            out.append(finding("warning", code, msg))

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="JSON participation metadata record")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    findings = validate(record)
    if args.json:
        print(json.dumps({"study_id": record.get("study_id"), "findings": findings, "error_count": sum(f["severity"] == "error" for f in findings), "warning_count": sum(f["severity"] == "warning" for f in findings)}, indent=2, ensure_ascii=False))
    else:
        print(f"Civic Signal Integrity Check — {record.get('study_id', '(missing ID)')}")
        for item in findings:
            print(f"[{item['severity'].upper()}] {item['code']}: {item['message']}")
        errors = sum(f["severity"] == "error" for f in findings)
        warnings = sum(f["severity"] == "warning" for f in findings)
        print(f"\nFindings: {errors} error(s), {warnings} warning(s), {len(findings)-errors-warnings} info item(s).")
        print("This checks declared metadata only; it does not certify data quality or representativeness.")
    return 1 if any(f["severity"] == "error" for f in findings) else 0

if __name__ == "__main__":
    raise SystemExit(main())
