#!/usr/bin/env python3
"""
Lycheetah Framework Archive Compiler
Concatenates all 39 extraction files in session order into one document.
Usage: python3 compile_archive.py [--output OUTPUT_FILE]
"""

import os
import sys
import argparse

ARCHIVE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ordered file list — sessions 001 through 006
FILES = [
    "00_INDEX.md",
    "13_INDEX_SESSION_002.md",
    "13b_INDEX_SESSIONS_003_TO_006.md",
    "01_AURA_PROTOCOL_CORE.md",
    "02_VECTOR_INVERSION_PROTOCOL.md",
    "03_CASCADE_KNOWLEDGE_ARCHITECTURE.md",
    "04_CONSTRAINT_ALGEBRA.md",
    "05_LAMAHGUE_LANGUAGE.md",
    "06_AURA_LITE_AND_AVP.md",
    "07_EXTENSIONS.md",
    "08_LUMINOUS_TRINITY.md",
    "09_ARF_AND_LOCK_CHAIN_KEY.md",
    "10_AESTHETIC_ENCODING.md",
    "11_WORKED_EXAMPLES.md",
    "12_PHILOSOPHY_AND_PRINCIPLES.md",
    "14_SRS_FORMAL_SCIENCE.md",
    "15_VERITAS_AND_ETERNAL_FORGE.md",
    "16_QUANTUM_ETHICS_LAYER.md",
    "17_CONSTRAINT_OS.md",
    "18_SPIRITUAL_SCIENCE_PROTOCOL.md",
    "19_DISTRIBUTED_NETWORK_METRICS.md",
    "20_PROVEN_EXPERIMENTAL_THEORETICAL.md",
    "21_ARFs_BARFL_ADVANCED_COMPONENTS.md",
    "22_SEMANTIC_TURN_AND_LINGUISTIC_ENGINEERING.md",
    "23_CULTURAL_LAYER_AND_BRAND_MYTHOS.md",
    "24_COMPRESSION_STACK_FORGE_SHEET.md",
    "25_RETROCAUSAL_AND_PREDICTION_PARADOX.md",
    "26_ASS_FORMULA_AND_EDUCATIONAL_SIMPLES.md",
    "27_LOGOS_COMPENDIUM.md",
    "28_AURA_PRIME_OS_AND_VERITAS_MEMORY.md",
    "29_USP_SEA_MDAD_ANTI_FRAGILE_PROTOCOLS.md",
    "30_HEALTH_PROTOCOL_AND_GBI_CASCADE.md",
    "31_SELF_CORRECTION_AND_CANONICAL_DEFINITIONS-1.md",
    "32_CHIRAL_NARRATIVE_INTEGRATION.md",
    "33_REAL_TIME_SESSION_COMPONENTS.md",
    "34_DAILY_RESONANCE_REPORT_AND_SPIRITUAL_ARCHITECTURE.md",
    "35_EARNED_LIGHT_AND_LIVING_GLOSSARY.md",
    "36_MULTI_AI_STRESS_TEST.md",
    "37_CODE_IMPLEMENTATIONS_COMPLETE.md",
    "38_AURA_VS_CONSTITUTIONAL_AI.md",
    "39_FINAL_SUPPLEMENTARY.md",
]

SEPARATOR = "\n\n---\n\n"

HEADER = """# LYCHEETAH FRAMEWORK — COMPLETE ARCHIVE
## Compiled from 39 extraction files across 6 sessions
**Author:** Mackenzie Conor James Clark
**Source:** 1,404-page raw conversation PDF
**Compiled:** {date}
**Files:** 39 | **Sessions:** 6 | **Coverage:** Lines 1–59,200 (complete)

> *"Value creation > value capture. AI safety is too important to gatekeep."*

---

"""


def compile_archive(output_path):
    from datetime import date
    parts = [HEADER.format(date=date.today().isoformat())]
    missing = []

    for filename in FILES:
        filepath = os.path.join(ARCHIVE_DIR, filename)
        if not os.path.exists(filepath):
            missing.append(filename)
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        parts.append(content)

    output = SEPARATOR.join(parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    total_chars = len(output)
    total_kb = total_chars / 1024

    print(f"Compiled: {len(FILES) - len(missing)} files → {output_path}")
    print(f"Size: {total_kb:.1f} KB ({total_chars:,} characters)")
    if missing:
        print(f"Missing ({len(missing)}): {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Compile Lycheetah archive into one document")
    parser.add_argument(
        "--output",
        default=os.path.join(ARCHIVE_DIR, "LYCHEETAH_COMPLETE_ARCHIVE.md"),
        help="Output file path (default: LYCHEETAH_COMPLETE_ARCHIVE.md in this folder)"
    )
    args = parser.parse_args()
    compile_archive(args.output)


if __name__ == "__main__":
    main()
