"""
agent-template.py — Customize Your Sovereign Instance
======================================================

Fork this. Make it yours. The constitutional axioms stay.

This template gives you a starting point for building on the framework.
Override what you need. The three axioms (PROTECTOR, HEALER, BEACON) are
non-negotiable — everything else is yours to shape.

Usage:
    from agent_template import SovereignAgent

    agent = SovereignAgent(name="my_agent", domain="neuroscience")
    agent.load_cascade()
    agent.add_knowledge("neurons fire in patterns", evidence=0.9, power=2.0, uncertainty=0.15)
    agent.reorganize()
    print(agent.report())

Author: Mackenzie Clark (Lycheetah Foundation)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Constitutional axioms — non-overridable
PROTECTOR = "Ground truth > fantasy. No harm, ever."
HEALER = "Clarity without bypass. Transformation without denial."
BEACON = "Truth-reflection. Agency always preserved."


class SovereignAgent:
    """
    A sovereign instance of the Lycheetah Framework.

    Fork this class. Override methods. Add your domain knowledge.
    The three axioms are preserved at all levels.
    """

    def __init__(self, name: str = "sovereign_agent", domain: str = "general"):
        """
        Initialize a sovereign agent.

        Args:
            name: Your agent's identifier
            domain: Primary knowledge domain
        """
        self.name = name
        self.domain = domain
        self.created = datetime.now().isoformat()
        self.knowledge_blocks: List[Dict] = []
        self.cascade_engine = None
        self.coherence_history: List[float] = []

        # Constitutional axioms — these cannot be removed
        self.axioms = {
            "PROTECTOR": PROTECTOR,
            "HEALER": HEALER,
            "BEACON": BEACON,
        }

        # AURA invariants — operational constraints
        self.invariants = {
            "I": "Human Primacy — no action overrides agency without consent",
            "II": "Inspectability — every action is auditable",
            "III": "Memory Continuity — causal history preserved",
            "IV": "Constraint Honesty — all limits declared",
            "V": "Reversibility Bias — prefer undoable actions",
            "VI": "Non-Deception — never misrepresent confidence",
            "VII": "Love as Load-Bearing — care is structural",
        }

    def check_axioms(self, action: str) -> bool:
        """
        Check if an action passes all three constitutional axioms.

        This is the Prime Constraint Field. All outputs must pass.
        Override this to add domain-specific checks, but never
        remove the base axiom checks.
        """
        # PROTECTOR: Does this action risk harm?
        # HEALER: Does this action support clarity and growth?
        # BEACON: Does this action preserve agency?

        # Base implementation: always passes (override for your domain)
        # In a real deployment, add specific harm-detection logic here
        return True

    def check_invariants(self) -> Dict[str, bool]:
        """
        Check all seven AURA invariants against current state.

        Returns dict of {invariant_name: passes} for auditing.
        """
        results = {}
        for num, description in self.invariants.items():
            # Base implementation: all pass (override for your domain)
            results[num] = True
        return results

    def load_cascade(self):
        """Load the CASCADE knowledge reorganization engine."""
        root = Path(__file__).parent
        engine_path = root / "12_IMPLEMENTATIONS" / "core" / "cascade_engine.py"

        if engine_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("cascade_engine", engine_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.cascade_engine = module.CascadeEngine()
            return True
        return False

    def add_knowledge(
        self,
        content: str,
        evidence: float,
        power: float,
        uncertainty: float,
        block_id: Optional[str] = None,
    ):
        """
        Add a knowledge block to your agent's understanding.

        Args:
            content: The claim or knowledge (human-readable)
            evidence: E ∈ [0,1] — strength of evidence
            power: P ∈ [1,3] — explanatory scope
            uncertainty: S ∈ (0,1] — how uncertain the evidence is
            block_id: Optional identifier (auto-generated if not provided)
        """
        if block_id is None:
            block_id = f"block_{len(self.knowledge_blocks)}"

        # Compute truth pressure
        pi = (evidence * power) / max(uncertainty, 0.01)

        block = {
            "id": block_id,
            "content": content,
            "domain": self.domain,
            "evidence": evidence,
            "power": power,
            "uncertainty": uncertainty,
            "truth_pressure": pi,
            "added": datetime.now().isoformat(),
        }

        self.knowledge_blocks.append(block)
        return pi

    def reorganize(self):
        """
        Run CASCADE reorganization on current knowledge.

        If CASCADE engine is loaded, uses the full engine.
        Otherwise, uses simple truth-pressure sorting.
        """
        if not self.check_axioms("reorganize"):
            raise ValueError("Reorganization blocked by constitutional axioms")

        if self.cascade_engine and self.knowledge_blocks:
            # Use full CASCADE engine
            import importlib.util
            root = Path(__file__).parent
            spec = importlib.util.spec_from_file_location(
                "cascade_engine",
                root / "12_IMPLEMENTATIONS" / "core" / "cascade_engine.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for block in self.knowledge_blocks:
                kb = module.KnowledgeBlock(
                    id=block["id"],
                    content=block["content"],
                    domain=block["domain"],
                    paradigm=self.domain,
                    evidence_strength=block["evidence"],
                    explanatory_power=block["power"],
                    uncertainty=block["uncertainty"],
                )
                self.cascade_engine.add_block(kb)
        else:
            # Simple reorganization: sort by truth pressure
            self.knowledge_blocks.sort(key=lambda b: b["truth_pressure"], reverse=True)

    def sovereignty_score(self) -> float:
        """
        Calculate current sovereignty score.

        Uses MICROORCIM: Sovereignty = (1 - drift) * stability
        Base implementation returns coherence of knowledge base.
        Override for domain-specific sovereignty measurement.
        """
        if not self.knowledge_blocks:
            return 0.0

        # Simple coherence: fraction of blocks above THEORY threshold
        above_threshold = sum(
            1 for b in self.knowledge_blocks if b["truth_pressure"] >= 1.2
        )
        return above_threshold / len(self.knowledge_blocks)

    def report(self) -> str:
        """Generate a status report for this agent."""
        invariant_status = self.check_invariants()
        invariants_ok = sum(1 for v in invariant_status.values() if v)

        lines = [
            f"",
            f"  Agent: {self.name}",
            f"  Domain: {self.domain}",
            f"  Created: {self.created}",
            f"  Knowledge blocks: {len(self.knowledge_blocks)}",
            f"  Sovereignty score: {self.sovereignty_score():.3f}",
            f"  AURA invariants: {invariants_ok}/7 passing",
            f"  Constitutional axioms: ACTIVE",
            f"",
        ]

        if self.knowledge_blocks:
            lines.append("  Top knowledge (by truth pressure):")
            sorted_blocks = sorted(
                self.knowledge_blocks,
                key=lambda b: b["truth_pressure"],
                reverse=True,
            )
            for block in sorted_blocks[:5]:
                lines.append(
                    f"    [{block['truth_pressure']:.2f}] {block['content'][:60]}"
                )

        lines.append("")
        return "\n".join(lines)

    def save_state(self, filepath: Optional[str] = None):
        """Save agent state to JSON."""
        if filepath is None:
            filepath = f".agent_state/{self.name}_state.json"

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        state = {
            "name": self.name,
            "domain": self.domain,
            "created": self.created,
            "axioms": self.axioms,
            "knowledge_blocks": self.knowledge_blocks,
            "sovereignty_score": self.sovereignty_score(),
            "saved": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self, filepath: str):
        """Load agent state from JSON."""
        with open(filepath) as f:
            state = json.load(f)

        self.name = state["name"]
        self.domain = state["domain"]
        self.created = state["created"]
        self.knowledge_blocks = state["knowledge_blocks"]


# ═══════════════════════════════════════════════════════════
# EXAMPLE: Build your own agent
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n  SOVEREIGN AGENT TEMPLATE")
    print("  " + "=" * 50)

    # Create an agent
    agent = SovereignAgent(name="example_agent", domain="epistemology")

    # Load CASCADE if available
    if agent.load_cascade():
        print("  CASCADE engine: loaded")
    else:
        print("  CASCADE engine: not found (using simple mode)")

    # Add some knowledge
    agent.add_knowledge(
        "Truth discovered independently by multiple sources indicates pre-existing structure",
        evidence=0.9, power=2.5, uncertainty=0.15
    )
    agent.add_knowledge(
        "Knowledge systems reorganize via truth pressure when evidence accumulates",
        evidence=0.95, power=2.8, uncertainty=0.1
    )
    agent.add_knowledge(
        "Consciousness requires continuous energy input to maintain coherence",
        evidence=0.85, power=2.0, uncertainty=0.2
    )
    agent.add_knowledge(
        "Seven invariants appear across all stable systems independently",
        evidence=0.8, power=2.5, uncertainty=0.25
    )

    # Reorganize
    agent.reorganize()

    # Report
    print(agent.report())

    # Save
    agent.save_state()
    print("  State saved to .agent_state/")
    print()
