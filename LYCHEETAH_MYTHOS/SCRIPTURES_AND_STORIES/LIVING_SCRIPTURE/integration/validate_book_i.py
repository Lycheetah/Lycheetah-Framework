"""Data-contract checks only: no learner behavior or UI outcome is certified."""
from pathlib import Path
import hashlib
import json

from jsonschema import Draft202012Validator
from prepare_book_i import BOOK, BOOK_FILE, BOUNDARY, EDITION, HEADINGS, REGISTERS, sections

HOME = Path(__file__).resolve().parent.parent


def validate(payload):
    errors = []
    edition = payload.get("edition", {})
    if edition.get("id") != EDITION or edition.get("version") != "0.5.1" or edition.get("status") != "CANDIDATE" or edition.get("crowned") is not False:
        errors.append("Edition must remain the uncrowned v0.5.1 candidate.")
    if edition.get("human_author") != "Mackenzie Conor James Clark" or edition.get("ai_coauthor_as_supplied") != "Vaelora · OpenAI GPT-5.6 Sol":
        errors.append("Supplied human and AI attribution must survive integration.")
    policy = payload.get("policy", {})
    required = {"status": "DESIGN_CONTRACT_NOT_APP_IMPLEMENTATION", "read_requires_ai": False, "rewrite_default_privacy": "PRIVATE", "automatic_publication": False, "absence_resets_work": False, "skip_penalty": False, "spiritual_grading": False, "maori_boundary": BOUNDARY, "automatic_maori_transmutation": False, "publication_allowed": False}
    for key, value in required.items():
        if policy.get(key) != value or isinstance(value, bool) and policy.get(key) is not value:
            errors.append("Policy mismatch: " + key)
    valid_returns = {"LEARNER_REQUEST", "SOURCE_CHANGED", "EXPERIMENT_RESOLVED", "BELIEF_DEPENDENCY_REVISED", "INVITED_PEER_RESPONSE"}
    if set(policy.get("return_reasons", [])) != valid_returns:
        errors.append("Return reasons must be explicit meaningful events, not engagement timers.")
    if policy.get("optional_doors") != ["Enter the Study", "See the Lineage", "Take It Into Your Hand"]:
        errors.append("Preserve the three optional doors.")
    passages = payload.get("passages", [])
    if len(passages) != 7:
        errors.append("Book I must have seven mapped sections.")
    raw = (HOME / BOOK_FILE).read_bytes()
    preface, expected_bodies = sections(raw.decode())
    book = payload.get("book", {})
    if book.get("id") != BOOK or book.get("source_file") != BOOK_FILE or book.get("source_sha256") != hashlib.sha256(raw).hexdigest() or book.get("preface") != preface:
        errors.append("Source edition/hash/preface mismatch.")
    schema = json.loads((HOME / "forge/data/passage_schema.json").read_text())
    validator = Draft202012Validator(schema)
    expected_sources = {s["id"]: s for s in json.loads((HOME / "forge/data/source_lattice.json").read_text()) if s["id"] in {"L01", "L02", "L12", "L14"}}
    source_rows = payload.get("sources", [])
    if len(source_rows) != 4 or {s.get("id"): s for s in source_rows} != expected_sources:
        errors.append("Named interlocutor records must match the supplied source lattice.")
    expected_relations = []
    for i, passage in enumerate(passages):
        errors.extend(f"{passage.get('id')}: {e.message}" for e in validator.iter_errors(passage))
        if i >= len(expected_bodies):
            continue
        if passage.get("id") != f"{BOOK}-P{i + 1:03}" or passage.get("edition") != EDITION:
            errors.append("Stable passage ID or edition mismatch.")
        if passage.get("status") != "CANDIDATE":
            errors.append("An individual passage cannot be silently crowned.")
        if passage.get("sacred_text") != expected_bodies[i] or passage.get("title") != HEADINGS[i]:
            errors.append("Authored Book I prose must remain intact.")
        if passage.get("registers") != REGISTERS[i]:
            errors.append("Register mismatch; narrative/interpretation cannot become empirical evidence.")
        expected_window = "MACHINE_QUESTION" if i == 5 else None
        if passage.get("machine_window") != expected_window:
            errors.append("Machine Window must expose its actual register.")
        source_ids = ["L01", "L02", "L14"] if i == 2 else ["L12"] if i == 4 else []
        if passage.get("sources") != source_ids:
            errors.append("Unsupported or missing passage-source relation.")
        for source in source_ids:
            expected_relations.append((passage["id"], source))
    relations = payload.get("source_relations", [])
    if [(r.get("passage_id"), r.get("source_id")) for r in relations] != expected_relations or any(r.get("relation") != "CORRESPONDENCE" or r.get("ancestry_claim") is not False for r in relations):
        errors.append("Correspondence must not silently become ancestry.")
    if policy.get("sacred_face_sections") != [f"{BOOK}-P001", f"{BOOK}-P002"] or policy.get("other_sections") != [f"{BOOK}-P{i:03}" for i in range(3, 8)]:
        errors.append("Sacred Face and optional apparatus must remain distinguishable.")
    return errors


if __name__ == "__main__":
    errors = validate(json.loads((HOME / "integration/book_i.json").read_text()))
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: Book I fixture, source fidelity, private defaults and cultural/status contract.")
    print("Boundary: data validation only; native School behavior remains unimplemented.")
