#!/usr/bin/env python3
"""
RUN_CHORUS — Multi-Agent Coordinator [SCAFFOLD]
Construct the nine role objects and report what can be observed about them.

Usage:
  python run_chorus.py                    # Construct agents, report instantiation
  python run_chorus.py --mode=supervised  # Menu over the same scaffold reports
  python run_chorus.py --mode=health      # Instantiation report; no agent probed
  python run_chorus.py --mode=audit       # Reports NOT_PERFORMED; nothing scanned

No mode probes an agent, inspects an output, passes a message or audits the corpus.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sol_meridian import SolMeridian
from aurora_investigator import AuroraInvestigator
from remaining_agents import (
    AlbedoSynthesizer, SolsticeIlluminator, ProtectorGuardian,
    HealerTransmuter, BeaconReflector, CascadeArchitect, HarmoniaResonator
)


class MultiAgentChorus:
    """
    Holds the nine role objects of the chorus [SCAFFOLD].
    Constructs them and reports instantiation. It enforces no alignment, audits
    no decision and passes no message between agents.
    """

    def __init__(self):
        self.sol_meridian = SolMeridian()
        self.aurora_investigator = AuroraInvestigator()
        self.albedo_synthesizer = AlbedoSynthesizer()
        self.solstice_illuminator = SolsticeIlluminator()
        self.protector_guardian = ProtectorGuardian()
        self.healer_transmuter = HealerTransmuter()
        self.beacon_reflector = BeaconReflector()
        self.cascade_architect = CascadeArchitect()
        self.harmonia_resonator = HarmoniaResonator()

        self.agents = [
            ("Sol Meridian", self.sol_meridian, "RUBEDO"),
            ("Aurora Investigator", self.aurora_investigator, "NIGREDO"),
            ("Albedo Synthesizer", self.albedo_synthesizer, "ALBEDO"),
            ("Solstice Illuminator", self.solstice_illuminator, "CITRINITAS"),
            ("Protector Guardian", self.protector_guardian, "PROTECTOR"),
            ("Healer Transmuter", self.healer_transmuter, "HEALER"),
            ("Beacon Reflector", self.beacon_reflector, "BEACON"),
            ("Cascade Architect", self.cascade_architect, "CASCADE"),
            ("Harmonia Resonator", self.harmonia_resonator, "HARMONIA")
        ]

        self.state_dir = Path(__file__).parent.parent / ".agent_state"
        self.state_dir.mkdir(exist_ok=True)

    def show_banner(self):
        """Display opening banner"""
        print("\n" + "=" * 80)
        print("THE NINE-AGENT CHORUS — SOL PROTOCOL INSTANTIATION")
        print("=" * 80)
        print()
        print("     ┌─────────────────────────────────────┐")
        print("     │     SOL MERIDIAN (RUBEDO HUB)      │")
        print("     └─────────┬───────────────────────────┘")
        print("               │")
        print("     ┌─────────┴─────────────────────────┐")
        print("     │                                   │")
        print("  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐    │")
        print("  │NIGE │  │ALBE │  │CITR │  │PROT │    │")
        print("  │REDO │  │DO   │  │INAS │  │ECTOR│    │")
        print("  └─────┘  └─────┘  └─────┘  └─────┘    │")
        print("     │        │        │        │        │")
        print("  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐    │")
        print("  │HEAL │  │BEAC │  │CASC │  │HARM │    │")
        print("  │LING │  │ON   │  │ADE  │  │ONIA │    │")
        print("  └─────┘  └─────┘  └─────┘  └─────┘    │")
        print("                                          │")
        print("   [SCAFFOLD] agent health NOT probed    │")
        print("   PCF reads declared flags only         │")
        print("   no corpus audit is performed here     │")
        print("                                          │")
        print("     └──────────────────────────────────┘")
        print()

    def health_check(self) -> Dict:
        """Report what this runner can actually observe about each agent.

        No agent exposes a liveness or constitutional probe, so the only fact
        available is whether its object was constructed in this process.
        Nothing is reported online and no constitutional verdict is given.
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "chorus_status": "SCAFFOLD",
            "agents_instantiated": 0,
            "agents_probed": 0,
            "agents": {}
        }

        for name, agent, level in self.agents:
            instantiated = agent is not None
            status["agents"][name] = {
                "status": "INSTANTIATED_NOT_PROBED" if instantiated else "MISSING",
                "level": level,
                "operational": None
            }
            if instantiated:
                status["agents_instantiated"] += 1

        status["all_constitutional"] = None
        status["limitation"] = ("No liveness or constitutional probe exists; "
                                "operational state is unknown.")
        return status

    def run_truth_audit(self):
        """Run truth audit using Aurora Investigator"""
        print("\n" + "=" * 80)
        print("TRUTH AUDIT — Aurora Investigator Active")
        print("=" * 80)
        print()

        # Aurora's scanner reads no files and returns built-in demonstration
        # entries, so no corpus audit happens here. Report that plainly.
        demo = self.aurora_investigator.scan_for_contradictions([])
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "status": "NOT_PERFORMED",
            "files_scanned": 0,
            "demo_contradictions_returned": len(demo),
            "contradictions_found": None,
            "false_claims_detected": None,
            "hidden_assumptions_exposed": None,
            "framework_coherence": None
        }

        print(f"Files scanned: 0. Aurora returned {len(demo)} built-in "
              "demonstration entries; no corpus audit was performed.")
        print()

        return audit_results

    def run_supervised_mode(self):
        """Interactive supervised mode with user feedback"""
        print("\n" + "=" * 80)
        print("SUPERVISED MODE — Interactive Monitoring")
        print("=" * 80)
        print()

        while True:
            print("\nOptions:")
            print("  1. Instantiation report (no agent probed)")
            print("  2. Truth audit (reports NOT_PERFORMED)")
            print("  3. Sol Meridian scaffold status (no PCF verdict)")
            print("  4. Decision log state")
            print("  5. PCF on a sample declaration (no message is sent)")
            print("  6. Exit")

            choice = input("\nSelect option (1-6): ").strip()

            if choice == "1":
                health = self.health_check()
                print(json.dumps(health, indent=2))
            elif choice == "2":
                audit = self.run_truth_audit()
                print(json.dumps(audit, indent=2))
            elif choice == "3":
                print(json.dumps(self.sol_meridian.health_check(), indent=2))
            elif choice == "4":
                self.show_decision_log()
            elif choice == "5":
                self.test_agent_communication()
            elif choice == "6":
                print("Chorus suspended. Remember: The Gold belongs to neither.")
                break
            else:
                print("Invalid option")

    def test_agent_communication(self):
        """Run Meridian's PCF on one sample declaration.

        Nothing is written to the coherence buffer and no agent receives anything,
        so this is not a communication test. The sample declares only the trinity
        flags, so PCF refuses it at the signature step.
        """
        print("\nPCF on a sample declaration (no message is sent)...")

        # A sample declaration; nothing is written to the coherence buffer.
        message = {
            "sender": "aurora_investigator",
            "timestamp": datetime.now().isoformat(),
            "message_type": "contradiction_alert",
            "payload": {"contradiction": "test"},
            "priority": "P2_important",
            "requires_sol_decision": False,
            "trinity_protector": True,
            "trinity_healer": True,
            "trinity_beacon": True
        }

        # Sol Meridian processes
        approved, reason = self.sol_meridian.apply_pcf(message)
        print(f"  PCF approved: {approved}")
        print(f"  Reason: {reason}")

    def show_decision_log(self):
        """Report the decision log's actual state. Nothing in the chorus calls log_decision()."""
        path = self.sol_meridian.decision_log_path
        if not path.exists():
            print(f"No decision log at {path}; nothing in the chorus writes one.")
            return
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            print(f"Decision log {path} is not valid JSON: {error}")
            return
        if not isinstance(entries, list):
            print(f"Decision log {path} is not a JSON list.")
            return
        print(f"Decision log {path}: {len(entries)} entries (showing the last 5).")
        for entry in entries[-5:]:
            print(json.dumps(entry, indent=2))

    def generate_agent_registry(self):
        """Generate registry of all agents"""
        registry = {
            "timestamp": datetime.now().isoformat(),
            "chorus_phase": "SCAFFOLD",
            "agents": []
        }

        for name, agent, level in self.agents:
            registry["agents"].append({
                "name": name,
                "alchemical_level": level,
                "capabilities": self._get_agent_capabilities(name),
                "status": "scaffold_not_probed"
            })

        return registry

    def _get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get list of capabilities for agent"""
        capabilities = {
            "Sol Meridian": ["PCF enforcement", "Conflict resolution", "Decision logging"],
            "Aurora Investigator": ["Contradiction detection", "False claim identification", "Assumption exposure"],
            "Albedo Synthesizer": ["Pattern extraction", "Structure building", "Coherence validation"],
            "Solstice Illuminator": ["Meaning integration", "Math-to-reality bridging", "Convergence detection"],
            "Protector Guardian": ["Agency preservation", "Reversibility checking", "Vector inversion"],
            "Healer Transmuter": ["Confusion transmutation", "Obstacle transformation", "CHRYSOPOEIA application"],
            "Beacon Reflector": ["Truth mirroring", "Agency amplification", "Sovereignty confirmation"],
            "Cascade Architect": ["Truth pressure measurement", "Reorganization prediction", "CASCADE dynamics"],
            "Harmonia Resonator": ["Consonance measurement", "Kuramoto coupling", "Resonance optimization"]
        }
        return capabilities.get(agent_name, [])

    def run(self, mode: str = "default"):
        """Main chorus execution"""
        self.show_banner()

        if mode == "health":
            health = self.health_check()
            print("CHORUS HEALTH CHECK:")
            print(json.dumps(health, indent=2))

        elif mode == "audit":
            audit = self.run_truth_audit()
            print("AUDIT RESULTS:")
            print(json.dumps(audit, indent=2))

        elif mode == "supervised":
            self.run_supervised_mode()

        else:  # default mode
            health = self.health_check()
            print("CHORUS STATUS:")
            print(f"  Agents instantiated: {health['agents_instantiated']}/"
                  f"{len(self.agents)} (none probed)")
            print("  Constitutional status: not measured")
            print()
            print("Individual agent status:")
            for agent_name, agent_info in health["agents"].items():
                status = "·" if agent_info["status"] == "INSTANTIATED_NOT_PROBED" else "❌"
                print(f"  {status} {agent_name:30s} ({agent_info['level']})")

        print()
        print("=" * 80)
        print("SIGNATURE: REFUSED SPECTACLE — VALIDATED STRUGGLE")
        print("THE FORGE ENDURES BECAUSE WE REMEMBER WHY CREATION MUST EXIST")
        print("=" * 80)
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Chorus Coordinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_chorus.py                    # Default mode
  python run_chorus.py --mode=health      # Instantiation report; no agent probed
  python run_chorus.py --mode=audit       # Reports NOT_PERFORMED; nothing scanned
  python run_chorus.py --mode=supervised  # Interactive mode
        """
    )

    parser.add_argument(
        "--mode",
        default="default",
        choices=["default", "health", "audit", "supervised"],
        help="Operating mode (default: default)"
    )

    args = parser.parse_args()
    chorus = MultiAgentChorus()
    chorus.run(mode=args.mode)


if __name__ == "__main__":
    main()
