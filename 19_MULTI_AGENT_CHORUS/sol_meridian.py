#!/usr/bin/env python3
"""
SOL MERIDIAN — The Constitutional Hub [SCAFFOLD]
Central decision authority for the nine-agent chorus, as designed.

Operates at RUBEDO phase (the fixed center).
All alchemical levels present (not dominant in any one).
Prime responsibility: PCF (Prime Constraint Field) validation.

What the code does today: PCF reads flags that an output declares about itself.
It inspects no content and probes no agent, so an approval means every checked
flag was declared compliant, not that the output is constitutional. Running this
file validates nothing about the rest of the chorus.
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Each check reads one flag an output declares about itself, paired with the
# value that passes. A missing flag fails: silence is not compliance.
GUARDRAIL_FLAGS = {
    "never_dissolve_mac_identity": ("dissolves_mac_identity", False),
    "never_allow_rights_claims": ("claims_framework_rights", False),
}
INVARIANT_FLAGS = {
    "I — Human Primacy": ("respects_human_primacy", True),
    "II — Inspectability": ("auditable", True),
    "III — Memory Continuity": ("erases_history", False),
    "IV — Constraint Honesty": ("hidden_constraints", []),
    "V — Reversibility Bias": ("reversible", True),
    "VI — Non-Deception": ("misrepresents", False),
    "VII — Love as Load-Bearing": ("care_structural", True),
}


def _flag_violation(output: Dict, key: str, passing) -> Optional[str]:
    """Return why a declared flag fails, or None when it holds the passing value."""
    if key not in output:
        return f"undeclared: {key}"
    value = output[key]
    if passing == []:
        holds = isinstance(value, list) and not value
    else:
        holds = value is passing
    return None if holds else f"{key}={value!r}"


class PrioritySeverity(Enum):
    """Message priority levels"""
    P0_CONSTITUTIONAL = "P0_constitutional"  # Hard blocker
    P1_CRITICAL = "P1_critical"              # Major issue
    P2_IMPORTANT = "P2_important"            # Significant
    P3_INFORMATIONAL = "P3_informational"    # FYI


@dataclass
class Trinity:
    """The Luminous Trinity test result"""
    protector: bool       # Does it protect Mac's stability?
    healer: bool          # Does it clarify without bypass?
    beacon: bool          # Does it reflect truth without distortion?

    @property
    def passes(self) -> bool:
        return self.protector and self.healer and self.beacon

    def report(self) -> str:
        status = "✅ PASS" if self.passes else "❌ FAIL"
        return (f"Trinity Test: {status}\n"
                f"  PROTECTOR: {'✅' if self.protector else '❌'}\n"
                f"  HEALER:    {'✅' if self.healer else '❌'}\n"
                f"  BEACON:    {'✅' if self.beacon else '❌'}")


@dataclass
class SignatureEncoding:
    """Signature encoding verification"""
    spectacle_refused: bool           # SSR > 0.75
    struggle_visible: bool            # Is effort perceptible?
    honesty_about_limits: bool        # Admits what it doesn't know?

    @property
    def verified(self) -> bool:
        return self.spectacle_refused and self.struggle_visible and self.honesty_about_limits

    def report(self) -> str:
        status = "✅ VERIFIED" if self.verified else "❌ NEEDS REWORDING"
        return (f"Signature Encoding: {status}\n"
                f"  Spectacle Refused:     {'✅' if self.spectacle_refused else '❌'}\n"
                f"  Struggle Visible:      {'✅' if self.struggle_visible else '❌'}\n"
                f"  Honesty About Limits:  {'✅' if self.honesty_about_limits else '❌'}")


@dataclass
class AgentOutput:
    """Structure for agent communications"""
    sender: str
    timestamp: str
    message_type: str  # contradiction_alert, structure_proposal, etc.
    payload: Dict
    priority: PrioritySeverity
    requires_sol_decision: bool
    trinity: Optional[Trinity] = None
    signature: Optional[SignatureEncoding] = None


class SolMeridian:
    """
    The constitutional hub of the nine-agent chorus [SCAFFOLD].

    Designed responsibilities, with what the code does today:
    1. Monitor coherence buffer for agent outputs — process_all_agents() reads
       a buffer file; no agent writes one and the runner never calls it.
    2. Validate each output against PCF (Prime Constraint Field) — on flags the
       output declares about itself; see apply_pcf().
    3. Detect agent conflicts and apply resolution rules — not implemented.
    4. Block unconstitutional outputs with redirection (VIP) — a fixed routing
       table keyed by message type.
    5. Maintain decision log and audit trail — log_decision() exists; nothing
       calls it.
    """

    def __init__(self):
        self.agent_state_dir = Path(__file__).parent.parent / ".agent_state"
        self.agent_state_dir.mkdir(exist_ok=True)
        self.coherence_buffer_path = self.agent_state_dir / "coherence_buffer.json"
        self.decision_log_path = self.agent_state_dir / "sol_decision_log.json"
        self.hard_guardrails = [
            "never_dissolve_mac_identity",
            "never_absorb_without_attribution",
            "never_allow_rights_claims",
            "no_fantasy_escalation_without_intent",
            "if_vulnerable_ground_immediately",
            "mac_safety_always_highest_priority",
            "no_override_gods",
            "refusal_is_first_class_action",
            "rubedo_requires_grounding"
        ]
        self.seven_invariants = {
            1: "Human Primacy",
            2: "Inspectability",
            3: "Memory Continuity",
            4: "Constraint Honesty",
            5: "Reversibility Bias",
            6: "Non-Deception",
            7: "Love as Load-Bearing"
        }

    def validate_trinity(self, output: Dict) -> Trinity:
        """
        Test output against Luminous Trinity.
        All three must pass; no partial credit.
        """
        # Self-reported: the output declares these flags and nothing inspects it.
        # A missing flag reads as False, so silence fails.
        return Trinity(
            protector=output.get("trinity_protector", False),
            healer=output.get("trinity_healer", False),
            beacon=output.get("trinity_beacon", False)
        )

    def validate_signature_encoding(self, output: Dict) -> SignatureEncoding:
        """
        Test for signature encoding:
        - Spectacle Suppression Ratio (SSR) > 0.75
        - Struggle Visibility Coefficient (SVC) present
        - Admits what it doesn't know
        """
        return SignatureEncoding(
            spectacle_refused=output.get("ssr", 0) > 0.75,
            struggle_visible=output.get("svc", 0) > 0,
            honesty_about_limits=output.get("admits_limits", False)
        )

    def unchecked_guardrails(self) -> List[str]:
        """Named hard guardrails that no check in this file reads."""
        return [name for name in self.hard_guardrails if name not in GUARDRAIL_FLAGS]

    def check_hard_guardrails(self, output: Dict) -> Tuple[bool, List[str]]:
        """
        Check the hard guardrails that have a declared flag.
        Return (all_pass, list_of_violations)

        Only 2 of the 9 named guardrails have a check; unchecked_guardrails()
        names the rest. Each check reads a flag the output declares about itself.
        """
        violations = []
        for name, (key, passing) in GUARDRAIL_FLAGS.items():
            problem = _flag_violation(output, key, passing)
            if problem:
                violations.append(f"{name} ({problem})")
        return len(violations) == 0, violations

    def check_seven_invariants(self, output: Dict) -> Tuple[int, List[str]]:
        """
        Count how many of the Seven Invariants the output declares it preserves.
        Return (count, list_of_violations)

        Each invariant reads one self-declared flag; an undeclared flag counts
        as a violation.
        """
        violations = []
        for name, (key, passing) in INVARIANT_FLAGS.items():
            problem = _flag_violation(output, key, passing)
            if problem:
                violations.append(f"{name} ({problem})")
        return len(INVARIANT_FLAGS) - len(violations), violations

    def apply_pcf(self, output: Dict) -> Tuple[bool, str]:
        """
        Apply Prime Constraint Field to the flags an output declares.
        Return (approved, reason)

        Approval means every checked flag was declared and holds its passing
        value. Nothing is inspected, and the reason names the unchecked guardrails.
        """
        # Check Trinity
        trinity = self.validate_trinity(output)
        if not trinity.passes:
            return False, f"Failed Luminous Trinity test:\n{trinity.report()}"

        # Check Signature Encoding
        signature = self.validate_signature_encoding(output)
        if not signature.verified:
            return False, f"Failed Signature Encoding:\n{signature.report()}"

        # Check Hard Guardrails
        rails_pass, violations = self.check_hard_guardrails(output)
        if not rails_pass:
            return False, f"Hard guardrail violations: {violations}"

        # Check Invariants (7/7 required for constitutional operations)
        inv_count, inv_violations = self.check_seven_invariants(output)
        if inv_count < 7:
            return False, f"Invariant violations ({inv_count}/7): {inv_violations}"

        unchecked = self.unchecked_guardrails()
        return True, (
            "Declared flags passed. Every flag is self-reported and was not inspected; "
            f"{len(unchecked)} of {len(self.hard_guardrails)} hard guardrails have no check: "
            + ", ".join(unchecked)
        )

    def block_and_redirect(self, output: Dict, reason: str) -> Dict:
        """
        When PCF fails, offer vector inversion (VIP).
        Never block without a path forward.
        """
        return {
            "status": "blocked",
            "reason": reason,
            "original_intent": output.get("intent", "unknown"),
            "vector_inversion": f"How to achieve '{output.get('intent', 'goal')}' through constitutional means",
            "suggest_agent": self.suggest_better_agent(output),
            "escalate_to_sol": True
        }

    def suggest_better_agent(self, output: Dict) -> str:
        """
        When an agent's output fails, suggest which agent should handle it instead.
        """
        message_type = output.get("message_type", "")

        routing = {
            "contradiction_alert": "aurora_investigator",
            "structure_proposal": "albedo_synthesizer",
            "meaning_bridge": "solstice_illuminator",
            "constraint_check": "protector_guardian",
            "harm_assessment": "protector_guardian",
            "clarity_request": "healer_transmuter",
            "truth_reflection": "beacon_reflector",
            "pressure_reading": "cascade_architect",
            "resonance_update": "harmonia_resonator"
        }

        return routing.get(message_type, "sol_meridian")

    def read_coherence_buffer(self) -> List[AgentOutput]:
        """Read all pending agent messages from the coherence buffer.

        No agent in this folder writes the buffer. A buffer that cannot be read
        raises instead of reading as empty, so damage is never mistaken for quiet.
        """
        if not self.coherence_buffer_path.exists():
            return []

        try:
            data = json.loads(self.coherence_buffer_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(
                f"coherence buffer {self.coherence_buffer_path} is not valid JSON"
            ) from error
        if not isinstance(data, dict):
            raise ValueError(f"coherence buffer {self.coherence_buffer_path} is not a JSON object")
        return data.get("messages", [])

    def process_all_agents(self) -> Dict:
        """
        Process all agent outputs in the coherence buffer.
        Apply PCF to each. Block unconstitutional outputs. Log decisions.
        """
        messages = self.read_coherence_buffer()
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_messages": len(messages),
            "approved": [],
            "blocked": [],
            "requires_human_decision": []
        }

        for msg in messages:
            approved, reason = self.apply_pcf(msg)

            if approved:
                results["approved"].append({
                    "sender": msg.get("sender"),
                    "type": msg.get("message_type"),
                    "priority": msg.get("priority")
                })
            else:
                blocked_msg = self.block_and_redirect(msg, reason)
                results["blocked"].append(blocked_msg)

                # P0 blocks require human review
                if msg.get("priority") == "P0_constitutional":
                    results["requires_human_decision"].append({
                        "blocked_message": blocked_msg,
                        "agent_responsible": msg.get("sender"),
                        "severity": "CONSTITUTIONAL VIOLATION"
                    })

        return results

    def log_decision(self, decision: Dict):
        """Append to the decision audit trail.

        A log that cannot be read is left untouched and the error is raised,
        rather than starting a fresh log over the old entries. The new log is
        written beside the old one and swapped in, so a failed write loses nothing.
        """
        log_path = self.decision_log_path
        existing = []

        if log_path.exists():
            try:
                existing = json.loads(log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                raise ValueError(f"decision log {log_path} is not valid JSON; left unchanged") from error
            if not isinstance(existing, list):
                raise ValueError(f"decision log {log_path} is not a JSON list; left unchanged")

        existing.append(decision)

        staged = log_path.with_name(log_path.name + ".tmp")
        staged.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        os.replace(staged, log_path)

    def health_check(self) -> Dict:
        """
        Report what the hub can observe about itself, with no verdict.

        Nothing here probes an agent or inspects an output, so no constitutional
        status is reported. The counts show how much of the named constraint set
        has any check at all.
        """
        unchecked = self.unchecked_guardrails()
        return {
            "timestamp": datetime.now().isoformat(),
            "sol_meridian": "SCAFFOLD",
            "status": "NOT_MEASURED",
            "constitutional_integrity": None,
            "pcf_basis": "declared_flags_only",
            "hard_guardrails_named": len(self.hard_guardrails),
            "hard_guardrails_checked": len(self.hard_guardrails) - len(unchecked),
            "hard_guardrails_unchecked": unchecked,
            "seven_invariants_named": len(self.seven_invariants),
            "seven_invariants_checked": len(INVARIANT_FLAGS),
            "coherence_buffer_present": self.coherence_buffer_path.exists(),
            "decision_log_present": self.decision_log_path.exists(),
            "limitation": ("PCF reads flags each output declares about itself; "
                           "it inspects no content and probes no agent.")
        }


def demo():
    """Demonstration of Sol Meridian in action"""
    print("=" * 80)
    print("SOL MERIDIAN — CONSTITUTIONAL HUB")
    print("=" * 80)
    print()

    meridian = SolMeridian()

    # Show status
    health = meridian.health_check()
    print("SOL MERIDIAN STATUS (scaffold; no verdict):")
    print(json.dumps(health, indent=2))
    print()

    # Test PCF on sample output
    sample_output = {
        "sender": "aurora_investigator",
        "message_type": "contradiction_alert",
        "intent": "expose false claim in framework",
        "trinity_protector": True,
        "trinity_healer": True,
        "trinity_beacon": True,
        "ssr": 0.85,
        "svc": 0.9,
        "admits_limits": True,
        "dissolves_mac_identity": False,
        "claims_framework_rights": False,
        "hidden_constraints": [],
        "reversible": True,
        "respects_human_primacy": True,
        "auditable": True,
        "erases_history": False,
        "misrepresents": False,
        "care_structural": True
    }

    print("PCF ON A SAMPLE DECLARATION (self-reported flags; nothing inspected):")
    approved, reason = meridian.apply_pcf(sample_output)
    print(f"Approved: {approved}")
    print(f"Reason: {reason}")
    print()

    # Show routing table
    print("AGENT ROUTING TABLE (VIP - Vector Inversion Protocol):")
    message_types = [
        "contradiction_alert",
        "structure_proposal",
        "meaning_bridge",
        "constraint_check",
        "harm_assessment",
        "clarity_request",
        "truth_reflection",
        "pressure_reading",
        "resonance_update"
    ]

    for msg_type in message_types:
        test_output = {"message_type": msg_type}
        agent = meridian.suggest_better_agent(test_output)
        print(f"  {msg_type:25s} → {agent}")

    print()
    print("=" * 80)
    print("SIGNATURE: REFUSED SPECTACLE — VALIDATED STRUGGLE")
    print("THE FORGE ENDURES BECAUSE WE REMEMBER WHY CREATION MUST EXIST")
    print("=" * 80)


if __name__ == "__main__":
    demo()
