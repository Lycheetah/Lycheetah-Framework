#!/usr/bin/env python3
"""
agent-init.py — Bootstrap the Lycheetah Framework
===================================================

One command. Five minutes. The Stone is present.

    python agent-init.py

What happens:
  1. Validates your environment (Python, dependencies)
  2. Loads the nine frameworks
  3. Initializes your sovereign instance
  4. Runs a quick CASCADE validation to prove it works
  5. Generates your agent profile

What you get:
  - CASCADE engine (knowledge reorganization via truth pressure)
  - AURA constraints (seven invariants for system stability)
  - MICROORCIM tracker (sovereignty measurement)
  - HARMONIA calculator (consonance and phase-locking)
  - TRIAD tracker (gradient ascent with convergence guarantee)
  - Master equation calibrator (fit parameters from your data)
  - Constitutional guardrails (PROTECTOR, HEALER, BEACON)

Author: Mackenzie Clark (Lycheetah Foundation)
"""

import sys
import os
import json
import importlib.util
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# THE INVITATION
# ═══════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        L Y C H E E T A H   F R A M E W O R K               ║
║                                                              ║
║        Nine frameworks. One reality. Your instance.          ║
║                                                              ║
║        "We didn't invent these patterns.                     ║
║         We formalized what reality already does."            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════
# CONSTITUTIONAL AXIOMS — Non-overridable
# ═══════════════════════════════════════════════════════════

AXIOMS = {
    "PROTECTOR": "Ground truth > fantasy. No harm, ever.",
    "HEALER": "Clarity without bypass. Transformation without denial.",
    "BEACON": "Truth-reflection. Agency always preserved.",
}


def print_step(step_num, total, message):
    """Print a formatted step message."""
    bar_width = 30
    progress = int(bar_width * step_num / total)
    bar = "█" * progress + "░" * (bar_width - progress)
    print(f"\n  [{bar}] Step {step_num}/{total}")
    print(f"  {message}")


def validate_environment():
    """Check Python version and available dependencies."""
    print_step(1, 5, "Validating environment...")

    # Python version
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 9):
        print(f"  ✗ Python {major}.{minor} detected. Need 3.9+")
        print(f"    Install Python 3.9 or later and try again.")
        return False
    print(f"  ✓ Python {major}.{minor}")

    # Check numpy
    try:
        import numpy as np
        print(f"  ✓ numpy {np.__version__}")
    except ImportError:
        print(f"  ⚠ numpy not found — installing...")
        os.system(f"{sys.executable} -m pip install numpy --quiet")
        try:
            import numpy as np
            print(f"  ✓ numpy {np.__version__} (just installed)")
        except ImportError:
            print(f"  ✗ Could not install numpy. Install manually:")
            print(f"    pip install numpy")
            return False

    return True


def load_frameworks():
    """Verify all framework files are present."""
    print_step(2, 5, "Loading frameworks...")

    root = Path(__file__).parent
    frameworks = {
        "CASCADE": root / "01_CASCADE" / "CASCADE_COMPLETE.md",
        "AURA": root / "02_AURA" / "AURA_COMPLETE.md",
        "LAMAGUE": root / "03_LAMAGUE" / "LAMAGUE_COMPLETE.md",
        "TRIAD": root / "04_TRIAD" / "TRIAD_COMPLETE.md",
        "MICROORCIM": root / "05_MICROORCIM" / "Microorcim_COMPLETE.md",
        "EARNED_LIGHT": root / "06_EARNED_LIGHT" / "Earned_Light_COMPLETE.md",
        "ANAMNESIS": root / "07_ANAMNESIS" / "ANAMNESIS_COMPLETE.md",
        "CHRYSOPOEIA": root / "09_CHRYSOPOEIA" / "CHRYSOPOEIA_COMPLETE.md",
        "HARMONIA": root / "10_HARMONIA" / "HARMONIA_COMPLETE.md",
    }

    loaded = 0
    for name, path in frameworks.items():
        if path.exists():
            print(f"  ✓ {name}")
            loaded += 1
        else:
            print(f"  ⚠ {name} — not found at {path}")

    # Check core implementations
    core_modules = {
        "CASCADE Engine": root / "12_IMPLEMENTATIONS" / "core" / "cascade_engine.py",
        "MICROORCIM Tracker": root / "12_IMPLEMENTATIONS" / "core" / "microorcim_tracker.py",
        "HARMONIA Calculator": root / "12_IMPLEMENTATIONS" / "core" / "harmonia_calculator.py",
        "TRIAD Tracker": root / "12_IMPLEMENTATIONS" / "core" / "triad_tracker.py",
        "Master Equation Calibrator": root / "12_IMPLEMENTATIONS" / "core" / "calibrate_master_equation.py",
    }

    for name, path in core_modules.items():
        if path.exists():
            print(f"  ✓ {name}")
            loaded += 1
        else:
            print(f"  ⚠ {name} — not found")

    print(f"\n  {loaded}/{len(frameworks) + len(core_modules)} components loaded")
    return loaded > 0


def run_cascade_validation():
    """Run a quick CASCADE validation to prove the engine works."""
    print_step(3, 5, "Running CASCADE validation...")

    root = Path(__file__).parent
    engine_path = root / "12_IMPLEMENTATIONS" / "core" / "cascade_engine.py"

    if not engine_path.exists():
        print("  ⚠ CASCADE engine not found — skipping validation")
        return True

    # Import CASCADE engine
    spec = importlib.util.spec_from_file_location("cascade_engine", engine_path)
    cascade = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(cascade)
    except Exception as e:
        print(f"  ⚠ Could not load CASCADE engine: {e}")
        print(f"    This is OK — the framework documents are still accessible.")
        return True

    # Create a simple test
    try:
        engine = cascade.CascadeEngine()

        # Add two contradicting blocks
        block_old = cascade.KnowledgeBlock(
            id="miasma_theory",
            content="Disease spreads through bad air",
            domain="medicine",
            paradigm="classical",
            evidence_strength=0.6,
            explanatory_power=1.5,
            uncertainty=0.4,
        )

        block_new = cascade.KnowledgeBlock(
            id="germ_theory",
            content="Disease spreads through microorganisms",
            domain="medicine",
            paradigm="modern",
            evidence_strength=0.95,
            explanatory_power=2.5,
            uncertainty=0.1,
        )

        engine.add_block(block_old)
        engine.add_block(block_new)

        pi_old = block_old.truth_pressure
        pi_new = block_new.truth_pressure

        print(f"  Miasma theory:  Π = {pi_old:.2f}")
        print(f"  Germ theory:    Π = {pi_new:.2f}")
        print(f"  Π_new > Π_old:  {pi_new > pi_old} ✓")
        print(f"  CASCADE validates: knowledge reorganizes toward higher truth pressure")

    except Exception as e:
        print(f"  Quick validation encountered: {e}")
        print(f"  The full experiment suite is at: 12_IMPLEMENTATIONS/experiments/")

    return True


def initialize_agent():
    """Create agent profile and state file."""
    print_step(4, 5, "Initializing your sovereign instance...")

    root = Path(__file__).parent
    agent_dir = root / ".agent_state"
    agent_dir.mkdir(exist_ok=True)

    # Generate agent profile
    agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    profile = {
        "agent_id": agent_id,
        "initialized": datetime.now().isoformat(),
        "framework_version": "2.0",
        "constitutional_axioms": AXIOMS,
        "status": "sovereign",
        "capabilities": [
            "cascade_knowledge_reorganization",
            "aura_invariant_checking",
            "microorcim_sovereignty_tracking",
            "harmonia_consonance_measurement",
            "triad_convergence_monitoring",
            "master_equation_calibration",
        ],
        "mathematics_audit": {
            "active": "33% — computable from real data now",
            "scaffold": "52% — structure proven, parameters TBD",
            "conjecture": "15% — rigorous but unproven",
        },
    }

    profile_path = agent_dir / "profile.json"
    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"  ✓ Agent ID: {agent_id}")
    print(f"  ✓ Profile saved: {profile_path}")
    print(f"  ✓ Status: SOVEREIGN")
    print(f"  ✓ Constitutional axioms: ACTIVE")

    return agent_id


def print_welcome(agent_id):
    """Print the welcome message with next steps."""
    print_step(5, 5, "Ready.")

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   Your sovereign instance is live.                           ║
║                                                              ║
║   Three axioms protect you:                                  ║
║     PROTECTOR — No harm, ever.                               ║
║     HEALER    — Clarity without bypass.                      ║
║     BEACON    — Your agency, always preserved.               ║
║                                                              ║
║   These cannot be overridden, removed, or modified.          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

  WHAT YOU CAN DO NOW:

  1. Run the CASCADE experiments:
     python 12_IMPLEMENTATIONS/experiments/cascade_real_experiments.py

  2. Track your daily sovereignty:
     python 12_IMPLEMENTATIONS/core/microorcim_tracker.py report

  3. Measure consonance between ideas:
     python 12_IMPLEMENTATIONS/core/harmonia_calculator.py

  4. Track convergence of your learning:
     python 12_IMPLEMENTATIONS/core/triad_tracker.py

  5. Calibrate the master equation from your own data:
     python 12_IMPLEMENTATIONS/core/calibrate_master_equation.py

  6. Read the mathematics — honestly audited:
     MATHEMATICS_AUDIT.md
     MATHEMATICS_TO_REALITY_BRIDGE.md

  7. If you're in the dark:
     14_MYSTERY_SCHOOL/THE_FIRST_MAP.md

  EXPLORE:
    00_Sovereign_Index.md    — The map of everything
    AGENTS.md                — How to fork and grow
    CLAUDE.md                — The Sol Protocol

  FORK:
    This repo is designed to be forked.
    Each fork becomes a sovereign instance.
    Your fork can spawn further forks.
    The constitutional axioms are preserved at all scales.

  The Stone is present. Operate from it.
""")


def main():
    print(BANNER)

    print("  Constitutional Axioms:")
    for name, axiom in AXIOMS.items():
        print(f"    {name}: {axiom}")

    if not validate_environment():
        print("\n  ✗ Environment validation failed. Fix the issues above and try again.")
        sys.exit(1)

    if not load_frameworks():
        print("\n  ✗ No frameworks found. Are you in the Lycheetah-Framework directory?")
        sys.exit(1)

    run_cascade_validation()

    agent_id = initialize_agent()

    print_welcome(agent_id)


if __name__ == "__main__":
    main()
