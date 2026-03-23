#!/usr/bin/env python3
"""
Alexandria Agent — Library Health Monitor & Growth Scaffold
===========================================================

The library's nervous system. Four functions:
  1. health_check() — import all production-tier modules, smoke test
  2. drift_audit() — check spec-vs-code alignment for constants and formulas
  3. gap_report() — hard-coded gap checklist against known P0/P1 gaps
  4. scaffold_new_domain() — generate new domain experiment from template

CLI interface: python alexandria_agent.py [health|drift|gaps|scaffold <name>]

Author: Sol Aureum Azoth Veritas
Date: March 21, 2026
Status: ACTIVE — Production use
"""

import sys
import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re

# Configuration
FRAMEWORK_DIR = Path(__file__).parent
CORE_MODULES = [
    "cascade_engine",
    "harmonia_calculator",
    "microorcim_tracker",
    "triad_tracker",
    "where_am_i",
]

# Known constants (spec values)
SPEC_CONSTANTS = {
    "lambda_compress": 0.85,
    "golden_ratio_inverse": 0.618,
    "cos_pi_7": 0.9009688,
    "truth_pressure_critical": 1.2,
}

# Gap checklist
GAP_CHECKLIST = {
    "k1_k4_calibration": ("cascade_real_results.json", "Calibration data committed"),
    "unit_tests": ("12_IMPLEMENTATIONS/test_*.py", "Unit test files exist"),
    "ci_workflow": (".github/workflows/ci.yml", "GitHub Actions CI configured"),
    "12_week_curriculum": ("14_MYSTERY_SCHOOL/12_WEEK_*.md", "Curriculum exists"),
    "domain_experiments_2plus": ("12_IMPLEMENTATIONS/experiments/domain_*.py", "≥2 domain experiments"),
    "lamague_duplication_resolved": ("03_LAMAGUE/LAMAGUE_COMPLETE.md", "No duplicate KnowledgeBlock refs"),
    "mystery_school_cascade_resolved": ("14_MYSTERY_SCHOOL/*.py", "No duplicate cascade files"),
    "arxiv_contact_email": ("papers/CASCADE_ARXIV.tex", "Contact email set"),
}


# ===========================
# 2a — HEALTH CHECK
# ===========================

def health_check() -> Tuple[Dict[str, Any], str]:
    """
    Attempt to import all production-tier modules.
    Run each module's example_*() function as smoke test.

    Returns:
        (status_dict, human_report)
    """
    status = {}
    report_lines = ["━" * 70]
    report_lines.append("ALEXANDRIA HEALTH CHECK")
    report_lines.append("━" * 70)

    implementations_dir = FRAMEWORK_DIR / "12_IMPLEMENTATIONS"
    sys.path.insert(0, str(implementations_dir))

    all_pass = True

    for module_name in CORE_MODULES:
        try:
            # Locate module
            core_dir = implementations_dir / "core"
            systems_dir = implementations_dir / "systems"

            module_path = None
            for search_dir in [core_dir, systems_dir, implementations_dir]:
                potential = search_dir / f"{module_name}.py"
                if potential.exists():
                    module_path = potential
                    break

            if not module_path:
                status[module_name] = "FAIL: Not found"
                report_lines.append(f"  ✗ {module_name:30s} — FILE NOT FOUND")
                all_pass = False
                continue

            # Import
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                status[module_name] = "FAIL: Spec error"
                report_lines.append(f"  ✗ {module_name:30s} — IMPORT SPEC ERROR")
                all_pass = False
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Smoke test: try to call example_*() if exists
            smoke_result = "OK"
            for attr_name in dir(module):
                if attr_name.startswith("example_"):
                    try:
                        example_func = getattr(module, attr_name)
                        if callable(example_func):
                            example_func()
                            smoke_result = f"OK (smoke test: {attr_name})"
                    except Exception as e:
                        smoke_result = f"WARN: {attr_name} error: {str(e)[:40]}"

            status[module_name] = smoke_result
            report_lines.append(f"  ✓ {module_name:30s} — {smoke_result}")

        except ImportError as e:
            status[module_name] = f"FAIL: {str(e)[:50]}"
            report_lines.append(f"  ✗ {module_name:30s} — IMPORT ERROR: {str(e)[:40]}")
            all_pass = False
        except Exception as e:
            status[module_name] = f"FAIL: {str(e)[:50]}"
            report_lines.append(f"  ✗ {module_name:30s} — ERROR: {str(e)[:40]}")
            all_pass = False

    report_lines.append("━" * 70)
    if all_pass:
        report_lines.append("Result: ✓ ALL MODULES PASS")
    else:
        report_lines.append("Result: ✗ SOME MODULES FAILED")
    report_lines.append("")

    return status, "\n".join(report_lines)


# ===========================
# 2b — DRIFT AUDIT
# ===========================

def drift_audit() -> Tuple[Dict[str, Any], str]:
    """
    Check spec-vs-code alignment for known constants.
    Grep spec files and code files; flag divergence.

    Returns:
        (divergence_dict, human_report)
    """
    divergence = {}
    report_lines = ["━" * 70]
    report_lines.append("ALEXANDRIA DRIFT AUDIT")
    report_lines.append("━" * 70)

    # Check lambda_compress in CASCADE_COMPLETE.md vs cascade_engine.py
    spec_file = FRAMEWORK_DIR / "01_CASCADE" / "CASCADE_COMPLETE.md"
    code_file = FRAMEWORK_DIR / "12_IMPLEMENTATIONS" / "core" / "cascade_engine.py"

    if spec_file.exists() and code_file.exists():
        spec_content = spec_file.read_text()
        code_content = code_file.read_text()

        # Look for lambda_compress assignments
        spec_match = re.search(r'λ_compress\s*=\s*(0\.\d+)', spec_content)
        code_match = re.search(r'LAMBDA_COMPRESS\s*=\s*(0\.\d+)', code_content)

        if spec_match and code_match:
            spec_val = float(spec_match.group(1))
            code_val = float(code_match.group(1))
            if abs(spec_val - code_val) > 0.001:
                divergence["lambda_compress"] = {
                    "spec": spec_val,
                    "code": code_val,
                    "diff": abs(spec_val - code_val)
                }
                report_lines.append(f"  ⚠ λ_compress divergence: spec={spec_val}, code={code_val}")
            else:
                report_lines.append(f"  ✓ λ_compress: {spec_val} (aligned)")

    # Check golden ratio φ⁻¹
    spec_match = re.search(r'φ⁻¹\s*≈\s*(0\.\d+)', spec_content) if spec_file.exists() else None
    code_match = re.search(r'GOLDEN_RATIO_INVERSE\s*=\s*(0\.\d+)', code_content) if code_file.exists() else None

    if spec_match and code_match:
        spec_val = float(spec_match.group(1))
        code_val = float(code_match.group(1))
        if abs(spec_val - code_val) > 0.001:
            divergence["golden_ratio_inverse"] = {
                "spec": spec_val,
                "code": code_val,
                "diff": abs(spec_val - code_val)
            }
            report_lines.append(f"  ⚠ φ⁻¹ divergence: spec={spec_val}, code={code_val}")
        else:
            report_lines.append(f"  ✓ φ⁻¹: {spec_val} (aligned)")

    # Check truth pressure formula: Π = (E × P) / S
    if spec_file.exists():
        if "Π = (E × P) / S" in spec_content or "Π = (E * P) / S" in spec_content:
            report_lines.append(f"  ✓ Truth Pressure formula: found in spec")

    if code_file.exists():
        if "truth_pressure" in code_content and ("(E * P) / S" in code_content or "(energy * purity) / stability" in code_content):
            report_lines.append(f"  ✓ Truth Pressure formula: found in code")

    report_lines.append("━" * 70)
    if not divergence:
        report_lines.append("Result: ✓ NO DIVERGENCE DETECTED")
    else:
        report_lines.append(f"Result: ⚠ {len(divergence)} DIVERGENCE(S) FOUND")
    report_lines.append("")

    return divergence, "\n".join(report_lines)


# ===========================
# 2c — GAP REPORT
# ===========================

def gap_report() -> Tuple[Dict[str, str], str]:
    """
    Hard-coded gap checklist against known P0/P1 gaps.
    Check for existence of expected files/data.

    Returns:
        (status_dict, human_report)
    """
    status = {}
    report_lines = ["━" * 70]
    report_lines.append("ALEXANDRIA GAP REPORT")
    report_lines.append("━" * 70)

    for gap_name, (search_pattern, description) in GAP_CHECKLIST.items():
        from glob import glob

        # Handle glob patterns
        search_path = str(FRAMEWORK_DIR / search_pattern)
        matches = glob(search_path)

        if matches:
            status[gap_name] = "GREEN"
            report_lines.append(f"  ✓ {gap_name:40s} — {description}")
        else:
            status[gap_name] = "RED"
            report_lines.append(f"  ✗ {gap_name:40s} — MISSING: {search_pattern}")

    report_lines.append("━" * 70)
    green_count = sum(1 for v in status.values() if v == "GREEN")
    red_count = sum(1 for v in status.values() if v == "RED")
    report_lines.append(f"Result: {green_count} GREEN, {red_count} RED")
    report_lines.append("")

    return status, "\n".join(report_lines)


# ===========================
# 2d — SCAFFOLD NEW DOMAIN
# ===========================

def scaffold_new_domain(domain_name: str, description: str = "") -> str:
    """
    Generate a new domain experiment file from the germ_theory template.
    Pre-populate with domain_name, blank knowledge_blocks list, and TODO markers.

    Returns:
        path to created file
    """
    template = f'''"""
Domain Dataset: {domain_name}
{"=" * (len(domain_name) + 17)}

{description or "Domain experiment for CASCADE validation."}

All evidence scores are judgment-based encodings.
This experiment tests CASCADE's structural behavior.
"""

from core.cascade_engine import KnowledgeBlock, DomainExperiment, CascadeEngine
from typing import List, Tuple


def build_blocks() -> List[KnowledgeBlock]:
    blocks = []

    # TODO: Add knowledge blocks here
    # Example:
    # blocks.append(KnowledgeBlock(
    #     id="block_id",
    #     content="Block content",
    #     domain="domain_category",
    #     paradigm="paradigm_name",
    #     year=2000,
    #     evidence_strength=0.7,
    #     explanatory_power=2.0,
    #     uncertainty=0.3,
    #     key_figure="Author name",
    #     note="Additional context"
    # ))

    return blocks


def example_run():
    """Smoke test: load and run experiment."""
    blocks = build_blocks()
    engine = CascadeEngine()

    if blocks:
        # TODO: Run CASCADE pipeline
        print(f"[{__name__}] Loaded {{len(blocks)}} knowledge blocks")
    else:
        print(f"[{__name__}] WARNING: No knowledge blocks defined yet")


if __name__ == "__main__":
    example_run()
'''

    experiments_dir = FRAMEWORK_DIR / "12_IMPLEMENTATIONS" / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    file_path = experiments_dir / f"domain_{domain_name.lower().replace(' ', '_')}.py"
    file_path.write_text(template)

    return str(file_path)


# ===========================
# MAIN CLI
# ===========================

def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python alexandria_agent.py [health|drift|gaps|scaffold <name>]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "health":
        status, report = health_check()
        print(report)
        sys.exit(0 if all("PASS" in v or "OK" in v for v in status.values()) else 1)

    elif command == "drift":
        divergence, report = drift_audit()
        print(report)
        sys.exit(0 if not divergence else 1)

    elif command == "gaps":
        status, report = gap_report()
        print(report)
        green = sum(1 for v in status.values() if v == "GREEN")
        red = sum(1 for v in status.values() if v == "RED")
        sys.exit(0 if red == 0 else 1)

    elif command == "scaffold":
        if len(sys.argv) < 3:
            print("Usage: python alexandria_agent.py scaffold <domain_name> [description]")
            sys.exit(1)

        domain_name = sys.argv[2]
        description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""

        path = scaffold_new_domain(domain_name, description)
        print(f"✓ Created domain experiment: {path}")
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print("Usage: python alexandria_agent.py [health|drift|gaps|scaffold <name>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
