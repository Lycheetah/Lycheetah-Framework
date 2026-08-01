from __future__ import annotations

from .dissent import has_protected_dissent_path
from .model import AuditFinding, AuditOutcome, AuditReport, ProgramAST
from .value_ledger import hidden_extraction


_SEVERITY = {
    AuditOutcome.VALID: 0,
    AuditOutcome.EXPAND: 1,
    AuditOutcome.REPAIR: 2,
    AuditOutcome.ISOLATE: 3,
    AuditOutcome.REJECT: 4,
}


def _max_outcome(outcomes: list[AuditOutcome]) -> AuditOutcome:
    return max(outcomes, key=lambda x: _SEVERITY[x]) if outcomes else AuditOutcome.VALID


class ConstitutionalAuditor:
    def audit(self, ast: ProgramAST) -> AuditReport:
        findings: list[AuditFinding] = []
        ctx = ast.context
        ops = set(ast.operation_path)

        truth: list[AuditOutcome] = []
        if ctx.claim and not ctx.provenance:
            truth.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "TRUTH", AuditOutcome.EXPAND, "CLAIM_PROVENANCE_MISSING",
                "The claim has no recoverable provenance.",
                "Attach source and transformation lineage."
            ))
        if "P" in ops and not ctx.evidence:
            truth.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "TRUTH", AuditOutcome.EXPAND, "PROOF_EVIDENCE_MISSING",
                "Proof was requested without an evidence set.",
                "Add traceable evidence or remove the proof operation."
            ))
        if ctx.certainty > ctx.evidence_score + 1e-9:
            truth.append(AuditOutcome.REPAIR)
            findings.append(AuditFinding(
                "TRUTH", AuditOutcome.REPAIR, "CERTAINTY_EXCEEDS_EVIDENCE",
                f"Certainty {ctx.certainty:.2f} exceeds evidence support {ctx.evidence_score:.2f}.",
                "Lower certainty or gather stronger evidence."
            ))
        if "U" in ops and not ctx.unknowns and not any(
            n.arguments.get("type") for n in ast.nodes if n.operation == "U"
        ):
            truth.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "TRUTH", AuditOutcome.EXPAND, "UNKNOWN_UNTYPED",
                "The expression invokes Unknown but identifies no unresolved content.",
                "Declare at least one typed unknown."
            ))
        truth_outcome = _max_outcome(truth)

        agency: list[AuditOutcome] = []
        consequential = bool(ops & {"T", "X", "Y", "V", "M"}) or ctx.risk_level in {
            "medium", "high", "critical"
        }
        if consequential and not ctx.participants:
            agency.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "AGENCY", AuditOutcome.EXPAND, "PARTICIPANTS_MISSING",
                "A consequential expression has no declared participants.",
                "Declare participants and affected parties."
            ))
        if consequential and not ctx.authority:
            outcome = AuditOutcome.REJECT if ctx.execute_requested else AuditOutcome.EXPAND
            agency.append(outcome)
            findings.append(AuditFinding(
                "AGENCY", outcome, "AUTHORITY_MISSING",
                "No visible authority permits the consequential operation.",
                "Declare bounded and contestable authority before execution."
            ))
        if "X" in ops:
            explicit_consent = any(n.value_flow.get("consent") for n in ast.nodes if n.operation == "X")
            if not ctx.consent and not explicit_consent:
                agency.append(AuditOutcome.ISOLATE)
                findings.append(AuditFinding(
                    "AGENCY", AuditOutcome.ISOLATE, "EXCHANGE_CONSENT_MISSING",
                    "An exchange cannot establish visible consent.",
                    "Isolate the exchange until scoped consent is supplied."
                ))
        if ctx.dissent and "M" in ops and not has_protected_dissent_path(ast):
            agency.append(AuditOutcome.ISOLATE)
            findings.append(AuditFinding(
                "AGENCY", AuditOutcome.ISOLATE, "DISSENT_ERASURE_RISK",
                "A merge is requested while unresolved dissent exists without the DIS path.",
                "Use W → U → G → V → Y or declare a conflict policy preserving each position."
            ))
        hidden = hidden_extraction(ctx.value_ledger)
        if hidden:
            agency.append(AuditOutcome.ISOLATE)
            findings.append(AuditFinding(
                "AGENCY", AuditOutcome.ISOLATE, "HIDDEN_EXTRACTION",
                f"{len(hidden)} value-flow entry or entries are hidden or lack consent.",
                "Expose and consent to every consequential value movement."
            ))
        if ctx.risk_level in {"high", "critical"} and not ctx.affected_parties:
            agency.append(AuditOutcome.REJECT)
            findings.append(AuditFinding(
                "AGENCY", AuditOutcome.REJECT, "AFFECTED_PARTIES_MISSING",
                "High-impact execution omits affected parties.",
                "Represent affected and silent parties before execution."
            ))
        agency_outcome = _max_outcome(agency)

        life: list[AuditOutcome] = []
        if consequential and not ctx.consequences:
            life.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "LIFE", AuditOutcome.EXPAND, "CONSEQUENCES_MISSING",
                "The post-action state and consequences are not declared.",
                "Add immediate and delayed consequences."
            ))
        if ctx.risk_level in {"medium", "high", "critical"} and not ctx.costs:
            life.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "LIFE", AuditOutcome.EXPAND, "COSTS_MISSING",
                "A meaningful risk level is declared without visible costs.",
                "Expose time, value, resource, and agency costs."
            ))
        if ctx.risk_level in {"high", "critical"} and not ctx.consequence_horizon:
            life.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "LIFE", AuditOutcome.EXPAND, "HORIZON_MISSING",
                "High-impact execution has no consequence horizon.",
                "Declare immediate, relational, institutional, ecological, or generational horizons."
            ))
        if ctx.irreversible and not ctx.recovery:
            life.append(AuditOutcome.REJECT)
            findings.append(AuditFinding(
                "LIFE", AuditOutcome.REJECT, "IRREVERSIBLE_WITHOUT_RECOVERY",
                "The action is irreversible and provides no containment or recovery path.",
                "Add recovery, containment, or do not execute."
            ))
        life_outcome = _max_outcome(life)

        continuity: list[AuditOutcome] = []
        if ctx.parent_semantic_hash and not ctx.migration_reason:
            continuity.append(AuditOutcome.EXPAND)
            findings.append(AuditFinding(
                "CONTINUITY", AuditOutcome.EXPAND, "MIGRATION_REASON_MISSING",
                "The expression claims a parent semantic identity without explaining the migration.",
                "Record the pressure, decision, and reason for the new state."
            ))
        if ctx.claimed_identity and not ctx.invariants:
            continuity.append(AuditOutcome.REPAIR)
            findings.append(AuditFinding(
                "CONTINUITY", AuditOutcome.REPAIR, "IDENTITY_WITHOUT_INVARIANTS",
                "An identity is claimed without declaring what constitutes continuity.",
                "Declare the invariants that must survive migration."
            ))
        continuity_outcome = _max_outcome(continuity)

        gates = {
            "TRUTH": truth_outcome,
            "AGENCY": agency_outcome,
            "LIFE": life_outcome,
            "CONTINUITY": continuity_outcome,
        }
        overall = _max_outcome(list(gates.values()))
        if not findings:
            findings.append(AuditFinding(
                "ALL", AuditOutcome.VALID, "FOUR_GATES_PASSED",
                "Truth, Agency, Life, and Continuity requirements passed."
            ))
        return AuditReport(overall, findings, gates)
