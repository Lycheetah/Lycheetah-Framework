"""Prepare a faithful Book I data fixture; this does not build the School UI."""
from pathlib import Path
import hashlib
import json
import re

HOME = Path(__file__).resolve().parent.parent
EDITION = "LYC-SCR-CORE-0051"
BOOK = "LYC-SCR-B01"
BOOK_FILE = "forge/core_scripture/BOOK_I_THE_OPEN_FIELD.md"
BOUNDARY = "BLOCKED_PENDING_RELEVANT_MAORI_HUMAN_RELATIONSHIP_AND_REVIEW"
HEADINGS = [
    "THE HEARTH — The fourth chair",
    "THE TEMPLE — Before the first name",
    "THE STUDY — Relation and remainder",
    "THE FRICTION — The danger of relation-language",
    "THE MANY FIRES — Knowledge may coexist before it combines",
    "THE MACHINE WINDOW — MACHINE QUESTION",
    "YOUR HAND",
]
REGISTERS = [
    ["FICTION"], ["MYTH"], ["PHILOSOPHICAL", "INTERPRETIVE"],
    ["PHILOSOPHICAL", "NORMATIVE"], ["INTERPRETIVE"],
    ["MACHINE_QUESTION"], ["NORMATIVE"],
]
VOICES = ["HEARTH", "TEMPLE", "STUDY", "STUDY", "STUDY", "MACHINE_WINDOW", "STUDY"]


def sections(text):
    """Keep authored section bytes intact; reject unreviewed structural changes."""
    marks = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    chosen = [m for m in marks if m.group(1) in HEADINGS]
    if [m.group(1) for m in chosen] != HEADINGS:
        raise ValueError("Book I section structure changed; review IDs and edition first.")
    unexpected = [m.group(1) for m in marks if m.start() >= chosen[0].start() and m.group(1) not in HEADINGS]
    if unexpected:
        raise ValueError("Unmapped Book I sections: " + repr(unexpected))
    bodies = [text[m.start():chosen[i + 1].start() if i + 1 < len(chosen) else len(text)] for i, m in enumerate(chosen)]
    return text[:chosen[0].start()], bodies


def build():
    raw = (HOME / BOOK_FILE).read_bytes()
    preface, bodies = sections(raw.decode("utf-8"))
    lattice = json.loads((HOME / "forge/data/source_lattice.json").read_text())
    used = {"L01", "L02", "L12", "L14"}
    source_rows = [s for s in lattice if s["id"] in used]
    if {s["id"] for s in source_rows} != used:
        raise ValueError("Missing named Book I interlocutors.")
    passages = []
    for index, body in enumerate(bodies):
        sources = ["L01", "L02", "L14"] if index == 2 else ["L12"] if index == 4 else []
        passages.append({
            "id": f"{BOOK}-P{index + 1:03}", "edition": EDITION,
            "title": HEADINGS[index], "sacred_text": body,
            "registers": REGISTERS[index], "sources": sources,
            "voice": VOICES[index], "machine_window": "MACHINE_QUESTION" if index == 5 else None,
            "exit_available": True, "status": "CANDIDATE",
            "cultural_review": {"required": bool(sources), "status": "RECONNAISSANCE_ONLY" if sources else "NOT_REQUIRED"},
            "metadata_origin": "Caelorynth integration annotations; not additional claims from the authors.",
        })
    payload = {
        "edition": {"id": EDITION, "version": "0.5.1", "status": "CANDIDATE", "human_author": "Mackenzie Conor James Clark", "ai_coauthor_as_supplied": "Vaelora · OpenAI GPT-5.6 Sol", "integration_assistance": "Caelorynth, an AI coding assistant", "crowned": False},
        "book": {"id": BOOK, "title": "The Open Field", "source_file": BOOK_FILE, "source_sha256": hashlib.sha256(raw).hexdigest(), "preface": preface},
        "passages": passages, "sources": source_rows,
        "source_relations": [{"passage_id": p["id"], "source_id": s, "relation": "CORRESPONDENCE", "ancestry_claim": False, "basis": "Named in the supplied Book I; scholarly interpretation not independently reverified during intake."} for p in passages for s in p["sources"]],
        "policy": {
            "status": "DESIGN_CONTRACT_NOT_APP_IMPLEMENTATION",
            "read_requires_ai": False,
            "optional_doors": ["Enter the Study", "See the Lineage", "Take It Into Your Hand"],
            "sacred_face_sections": [passages[0]["id"], passages[1]["id"]],
            "other_sections": [p["id"] for p in passages[2:]],
            "rewrite_default_privacy": "PRIVATE", "automatic_publication": False,
            "rewrite_outcomes": ["ACCEPT", "REJECT", "REVISE", "FORK", "TRANSLATE", "COMBINE", "LEAVE_UNRESOLVED"],
            "absence_resets_work": False, "skip_penalty": False,
            "spiritual_grading": False,
            "return_reasons": ["LEARNER_REQUEST", "SOURCE_CHANGED", "EXPERIMENT_RESOLVED", "BELIEF_DEPENDENCY_REVISED", "INVITED_PEER_RESPONSE"],
            "maori_boundary": BOUNDARY, "automatic_maori_transmutation": False,
            "publication_allowed": False,
        },
    }
    (HOME / "integration/book_i.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print("Prepared seven Book I sections, preserving the complete source text.")


if __name__ == "__main__":
    build()
