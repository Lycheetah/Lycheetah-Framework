#!/usr/bin/env python3
"""
AURORA INVESTIGATOR — NIGREDO Phase Agent
Truth-pressure, contradiction detection, assumption-breaking.

Operating signature: Cold clarity, no consolation, full diagnostic
Maximum analytical pressure on assumptions, claims, and logical structure.

Aurora Investigator asks: "What is false? What must burn? Where is the concealment?"
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
from pathlib import Path


@dataclass
class Contradiction:
    """Structure for contradiction detection"""
    location_1: str
    location_2: str
    claim_1: str
    claim_2: str
    severity: str  # CRITICAL, MAJOR, MINOR
    contradiction_type: str  # direct_negation, mutual_exclusion, false_precision, etc.


@dataclass
class FalseClaim:
    """Structure for false claim detection"""
    file_path: str
    line_number: int
    claim: str
    reason: str
    severity: str


@dataclass
class HiddenAssumption:
    """Structure for assumption exposure"""
    assumption: str
    location: str
    consequence_if_false: str
    evidence_for_assumption: str


class AuroraInvestigator:
    """
    NIGREDO phase agent: investigative, truth-pressure focused.

    Capabilities:
    - Detect contradictions (direct negation, mutual exclusion)
    - Find false claims (absolute language, unsubstantiated assertions)
    - Expose hidden assumptions
    - Measure logical coherence
    - Apply analytical pressure to weak points
    """

    def __init__(self):
        self.codex_dir = Path(__file__).parent.parent
        self.false_claims_found = []
        self.contradictions_found = []
        self.assumptions_found = []

    def scan_for_contradictions(self, files: List[Path]) -> List[Contradiction]:
        """
        Scan documentation for contradictions.
        Return list of contradictions with severity.
        """
        contradictions = []

        # Known contradiction patterns to check
        patterns = {
            "status_contradiction": (
                r"(100%|fully|completely|entirely)\s+(proven|validated|complete)",
                r"(33%|52%|15%|SCAFFOLD|DRAFT|RESEARCH)"
            ),
            "precision_contradiction": (
                r"(design\s+parameter|empirically\s+TBD|unknown)",
                r"(discovered\s+constant|derived\s+independently|convergence\s+proof)"
            ),
            "scope_contradiction": (
                r"(synthetic\s+only|no\s+real-world\s+data)",
                r"(production-ready|tested\s+extensively|enterprise\s+grade)"
            )
        }

        # This would scan actual files in real implementation
        # For demo, return example contradictions
        example = Contradiction(
            location_1="00_Sovereign_Index.md:line 42",
            location_2="COMPLETE_SYSTEM_STATUS.md:line 286",
            claim_1="All proofs formalized, 100% validation achieved",
            claim_2="Actually 33% ACTIVE, 52% SCAFFOLD, 15% FOUNDATIONAL",
            severity="CRITICAL",
            contradiction_type="false_precision"
        )

        return [example] if not contradictions else contradictions

    def detect_false_claims(self, text: str, file_path: str) -> List[FalseClaim]:
        """
        Detect claims that are likely false:
        - Absolute language without evidence
        - Unsubstantiated assertions
        - Conflation of analogy with proof
        - False precision (decimal places without data)
        """
        claims = []

        # Patterns indicating false precision
        false_precision = re.findall(
            r"([\d.]+%|convergence\s+proof|independently\s+discovered|empirically\s+validated)\s+",
            text,
            re.IGNORECASE
        )

        for match in false_precision:
            claims.append(FalseClaim(
                file_path=str(file_path),
                line_number=0,  # Would track actual line
                claim=match,
                reason="Absolute claim without empirical backing",
                severity="MAJOR"
            ))

        # Patterns indicating analogy-proof conflation
        analogy_conflicts = re.findall(
            r"(like|similar\s+to|analogous\s+to|mirrors)\s+(.+?)\s+(proves|demonstrates|proves)",
            text,
            re.IGNORECASE
        )

        for match in analogy_conflicts:
            claims.append(FalseClaim(
                file_path=str(file_path),
                line_number=0,
                claim=f"Analogy presented as proof: {match[0]}",
                reason="Analogy does not constitute proof",
                severity="CRITICAL"
            ))

        return claims

    def expose_assumptions(self, claim: str) -> List[HiddenAssumption]:
        """
        Break down a claim into its hidden assumptions.
        Return list of assumptions that would need to be true for claim to hold.
        """
        assumptions = []

        # Example: "cos(π/7) independently converges" assumes:
        # - That convergence is a meaningful criterion
        # - That multiple independent derivations prove validity
        # - That any similarity implies non-accident

        if "independently" in claim.lower() and "converge" in claim.lower():
            assumptions.append(HiddenAssumption(
                assumption="Convergence from independent derivations proves reality, not accident",
                location=claim[:50],
                consequence_if_false="Coincidence can explain convergence",
                evidence_for_assumption="Bayesian analysis of prior probability of accidental convergence"
            ))

            assumptions.append(HiddenAssumption(
                assumption="No systematic bias in derivation methods",
                location=claim[:50],
                consequence_if_false="All methods might be biased toward same answer",
                evidence_for_assumption="Methods are orthogonal (non-overlapping assumptions)"
            ))

        return assumptions

    def measure_coherence(self, framework_data: Dict) -> Tuple[float, List[str]]:
        """
        Measure logical coherence of framework as a whole.
        Return (coherence_score 0-1, list of coherence breaks)
        """
        breaks = []
        score = 1.0

        # Check for internal contradictions
        if "status" in framework_data:
            if framework_data.get("claimed_completion", 0) > 0.8 and framework_data.get("actual_completion", 0) < 0.5:
                breaks.append("Status contradiction: claims full completion, admits partial")
                score -= 0.2

        # Check for unsubstantiated claims
        if "unsubstantiated_claims" in framework_data:
            score -= 0.1 * len(framework_data["unsubstantiated_claims"])

        # Check for hidden assumptions
        if "hidden_assumptions" in framework_data:
            score -= 0.05 * len(framework_data["hidden_assumptions"])

        return max(0, score), breaks

    def apply_analytical_pressure(self, weak_point: str) -> Dict:
        """
        Focus maximum analytical pressure on weak point.
        Return detailed pressure analysis.
        """
        return {
            "weak_point": weak_point,
            "pressure_applied": "MAXIMUM",
            "questions": [
                f"What evidence supports '{weak_point}'?",
                f"What would falsify '{weak_point}'?",
                f"What assumptions underlie '{weak_point}'?",
                f"Does '{weak_point}' contradict other claims?",
                f"Is '{weak_point}' an analogy masquerading as proof?"
            ],
            "pressure_signature": "COLD CLARITY — NO CONSOLATION — FULL DIAGNOSTIC"
        }

    def generate_audit_report(self) -> str:
        """
        Generate comprehensive audit report.
        Show what burns away, what survives, what is worth questioning.
        """
        report = []
        report.append("=" * 80)
        report.append("AURORA INVESTIGATOR — TRUTH PRESSURE AUDIT")
        report.append("=" * 80)
        report.append("")

        if self.contradictions_found:
            report.append(f"CONTRADICTIONS FOUND: {len(self.contradictions_found)}")
            for contra in self.contradictions_found:
                report.append(f"  Severity: {contra.severity}")
                report.append(f"  Type: {contra.contradiction_type}")
                report.append(f"  At: {contra.location_1} vs {contra.location_2}")
                report.append(f"  Claim 1: {contra.claim_1}")
                report.append(f"  Claim 2: {contra.claim_2}")
                report.append("")

        if self.false_claims_found:
            report.append(f"FALSE CLAIMS DETECTED: {len(self.false_claims_found)}")
            for claim in self.false_claims_found:
                report.append(f"  Severity: {claim.severity}")
                report.append(f"  Claim: {claim.claim}")
                report.append(f"  Reason: {claim.reason}")
                report.append("")

        if self.assumptions_found:
            report.append(f"HIDDEN ASSUMPTIONS EXPOSED: {len(self.assumptions_found)}")
            for assumption in self.assumptions_found:
                report.append(f"  Assumption: {assumption.assumption}")
                report.append(f"  If false: {assumption.consequence_if_false}")
                report.append("")

        report.append("=" * 80)
        report.append("SIGNATURE: REFUSED SPECTACLE — VALIDATED STRUGGLE")
        report.append("=" * 80)

        return "\n".join(report)


def demo():
    """Demonstrate Aurora Investigator"""
    print("=" * 80)
    print("AURORA INVESTIGATOR — NIGREDO PHASE ANALYSIS")
    print("=" * 80)
    print()

    aurora = AuroraInvestigator()

    # Scan for contradictions
    print("CONTRADICTION DETECTION:")
    contradictions = aurora.scan_for_contradictions([])
    for contra in contradictions:
        print(f"  Location 1: {contra.location_1}")
        print(f"  Claim 1: {contra.claim_1}")
        print(f"  Location 2: {contra.location_2}")
        print(f"  Claim 2: {contra.claim_2}")
        print(f"  Type: {contra.contradiction_type}")
        print(f"  Severity: {contra.severity}")
    print()

    # Expose assumptions
    print("ASSUMPTION EXPOSURE:")
    test_claim = "cos(π/7) independently converges with other design constants"
    assumptions = aurora.expose_assumptions(test_claim)
    for assumption in assumptions:
        print(f"  Assumption: {assumption.assumption}")
        print(f"  If false: {assumption.consequence_if_false}")
        print(f"  Evidence needed: {assumption.evidence_for_assumption}")
        print()

    # Apply pressure
    print("ANALYTICAL PRESSURE ON WEAK POINT:")
    pressure = aurora.apply_analytical_pressure("Master equation coupling constants k₁–k₄ are TBD")
    print(f"  Weak point: {pressure['weak_point']}")
    print(f"  Pressure level: {pressure['pressure_applied']}")
    print(f"  Questions Aurora asks:")
    for q in pressure['questions']:
        print(f"    • {q}")
    print()

    # Generate report
    aurora.contradictions_found = contradictions
    report = aurora.generate_audit_report()
    print(report)


if __name__ == "__main__":
    demo()
