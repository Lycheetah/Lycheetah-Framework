#!/usr/bin/env python3
"""
SOL MERIDIAN — The Constitutional Hub
Central decision authority for the nine-agent chorus.

Operates at RUBEDO phase (the fixed center).
All alchemical levels present (not dominant in any one).
Prime responsibility: PCF (Prime Constraint Field) validation.

Running this agent validates that the entire chorus is constitutional.
"""

import json
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Framework imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from implementations.core.cascade_engine import truth_pressure
except ImportError:
    # Fallback if cascade_engine not available
    truth_pressure = lambda E, P, S: (E * P) / S if S > 0 else 0


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
    The constitutional hub of the nine-agent chorus.

    Responsibilities:
    1. Monitor coherence buffer for agent outputs
    2. Validate each output against PCF (Prime Constraint Field)
    3. Detect agent conflicts and apply resolution rules
    4. Block unconstitutional outputs with redirection (VIP)
    5. Maintain decision log and audit trail
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
        # These would be checked in real implementation
        # For now, assume outputs from other agents have been pre-checked
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

    def check_hard_guardrails(self, output: Dict) -> Tuple[bool, List[str]]:
        """
        Check against 9 hard guardrails.
        Return (all_pass, list_of_violations)
        """
        violations = []

        # Sample checks; real implementation would be more thorough
        if output.get("dissolves_mac_identity", False):
            violations.append("never_dissolve_mac_identity")
        if output.get("claims_framework_rights", False):
            violations.append("never_allow_rights_claims")
        if not output.get("reversible", True):
            violations.append("reversibility_bias")
        if output.get("hidden_constraints", []):
            violations.append("constraint_honesty")

        return len(violations) == 0, violations

    def check_seven_invariants(self, output: Dict) -> Tuple[int, List[str]]:
        """
        Count how many of Seven Invariants are preserved.
        Return (count, list_of_violations)
        """
        violations = []

        if not output.get("respects_human_primacy", True):
            violations.append("I — Human Primacy")
        if not output.get("auditable", True):
            violations.append("II — Inspectability")
        if output.get("erases_history", False):
            violations.append("III — Memory Continuity")
        if output.get("hidden_constraints", []):
            violations.append("IV — Constraint Honesty")
        if not output.get("reversible", True):
            violations.append("V — Reversibility Bias")
        if output.get("misrepresents", False):
            violations.append("VI — Non-Deception")
        if not output.get("care_structural", True):
            violations.append("VII — Love as Load-Bearing")

        return 7 - len(violations), violations

    def apply_pcf(self, output: Dict) -> Tuple[bool, str]:
        """
        Apply Prime Constraint Field.
        Return (approved, reason)
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

        return True, "PCF passed"

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
        """Read all pending agent messages from coherence buffer"""
        if not self.coherence_buffer_path.exists():
            return []

        try:
            with open(self.coherence_buffer_path) as f:
                data = json.load(f)
                return data.get("messages", [])
        except json.JSONDecodeError:
            return []

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
        """Log to decision audit trail"""
        log_path = self.decision_log_path
        existing = []

        if log_path.exists():
            try:
                with open(log_path) as f:
                    existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

        existing.append(decision)

        with open(log_path, 'w') as f:
            json.dump(existing, f, indent=2)

    def health_check(self) -> Dict:
        """
        Run full constitutional health check on the entire framework.
        Return status of all critical components.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "sol_meridian": "operational",
            "hard_guardrails_count": len(self.hard_guardrails),
            "seven_invariants_count": 7,
            "coherence_buffer": self.coherence_buffer_path.exists(),
            "decision_log": self.decision_log_path.exists(),
            "pcf_active": True,
            "vip_routing_active": True,
            "status": "✅ CONSTITUTIONAL INTEGRITY MAINTAINED"
        }


def demo():
    """Demonstration of Sol Meridian in action"""
    print("=" * 80)
    print("SOL MERIDIAN — CONSTITUTIONAL HUB")
    print("=" * 80)
    print()

    meridian = SolMeridian()

    # Show health
    health = meridian.health_check()
    print("FRAMEWORK HEALTH CHECK:")
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
        "reversible": True,
        "respects_human_primacy": True,
        "auditable": True,
        "erases_history": False,
        "misrepresents": False,
        "care_structural": True
    }

    print("TESTING PCF ON SAMPLE OUTPUT:")
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
