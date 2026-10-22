"""The agent-safety continuations keep their maintained manifests and stay outside the runtime.

`tests/test_research_intake.py` already pins Earned Trust cycles and Hybrid Gateway
against the 2026-10-18 intake. Nothing pinned the other continuations: Frontier
Controls, Compensation Race, Earned Light and Sovereign Choice. Each carries its own
maintained manifest; these tests verify them. Historical source manifests that
describe incoming bytes (`SOURCE_SHA256SUMS.json`, the v0.3 simulator manifest, the
superseded Hybrid Gateway `SHA256SUMS_v0.*`) are deliberately not checked here: they
are not meant to verify the current tree.

Integrity only. A matching digest says the bytes are the ones recorded, not that the
research is right.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAFETY = Path("papers/agent-safety")
FRONTIER = SAFETY / "frontier-controls"
EARNED_LIGHT = SAFETY / "earned-light"
SOVEREIGN_FORGES = SAFETY / "sovereign-choice-research/forges"
# The two Earned Light stories were moved out of the intake into the Mythos library;
# earned-light/README.md links them there.
STORY_HOME = Path("LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/TEXTS/ORIGINAL_NARRATIVES")
# Continuation code that must not be imported by the installed package.
CONTINUATION_MARKERS = ("agent-safety", "hybrid-gateway", "hybrid_gateway", "earned_trust_cycle",
                        "sovereign-choice", "SOVEREIGN_WILL", "frontier-controls")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(base: Path, digests: dict[str, str], label: str) -> list[str]:
    problems = []
    if not digests:
        return [f"{label}: manifest is empty"]
    for rel, digest in digests.items():
        target = base / rel.removeprefix("./")
        if not target.is_file():
            problems.append(f"{label}: {rel} listed, missing")
        elif _sha(target) != digest:
            problems.append(f"{label}: {rel} sha256 differs")
    return problems


def _text_manifest(path: Path) -> dict[str, str]:
    digests = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, rel = line.split(maxsplit=1)
            digests[rel.lstrip("*")] = digest
    return digests


def maintained_manifest_problems(root: Path) -> list[str]:
    problems = []
    frontier = root / FRONTIER
    integration = json.loads((frontier / "INTEGRATION_MANIFEST.json").read_text(encoding="utf-8"))
    problems += _check(frontier, integration["files"], "frontier INTEGRATION_MANIFEST")
    for sums in sorted(frontier.glob("0*/SHA256SUMS.json")):
        problems += _check(sums.parent, json.loads(sums.read_text(encoding="utf-8")), sums.parent.name)
    comp = root / SAFETY / "compensation-race-benchmark"
    problems += _check(comp, _text_manifest(comp / "MANIFEST.sha256"), "compensation MANIFEST")
    for sums in sorted((root / EARNED_LIGHT / "forges_01_07").glob("Forge_*/SHA256SUMS.txt")):
        problems += _check(sums.parent, _text_manifest(sums), sums.parent.name)
    return problems


def earned_light_intake_problems(root: Path) -> list[str]:
    """The intake manifest names pre-import paths; every recorded byte-string must still exist."""
    present = {_sha(p) for base in (root / EARNED_LIGHT, root / STORY_HOME)
               for p in base.rglob("*") if p.is_file()}
    intake = _text_manifest(root / EARNED_LIGHT / "intake/SHA256SUMS.txt")
    if not intake:
        return ["earned-light intake manifest is empty"]
    return [f"earned-light intake: {rel} bytes found nowhere" for rel, digest in intake.items()
            if digest not in present]


def _forge_digests(data: dict) -> dict[str, str]:
    """Each forge wrote its manifest in its own shape; an unknown shape is refused, not skipped."""
    for key in ("digests", "entries", "files"):
        if key in data:
            body = data[key]
            break
    else:
        body = data
    if isinstance(body, list):
        return {entry["path"]: entry["sha256"] for entry in body}
    digests = {}
    for rel, value in body.items():
        digest = value["sha256"] if isinstance(value, dict) else value
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"unrecognised forge manifest entry: {rel}")
        digests[rel] = digest
    return digests


def sovereign_forge_problems(root: Path) -> list[str]:
    """Forge manifests verify, except `lineage/` archives the README says were omitted."""
    problems = []
    manifests = sorted((root / SOVEREIGN_FORGES).glob("forge_*/*.json"))
    manifests = [m for m in manifests if re.search(r"MANIFEST", m.name)]
    if len(manifests) != 7:
        problems.append(f"expected 7 forge manifests, found {len(manifests)}")
    for manifest in manifests:
        digests = _forge_digests(json.loads(manifest.read_text(encoding="utf-8")))
        kept = {rel: d for rel, d in digests.items() if not rel.startswith("lineage/")}
        problems += _check(manifest.parent, kept, manifest.parent.name)
    return problems


def runtime_imports_of_continuations(root: Path) -> list[str]:
    hits = []
    for source in sorted((root / "lycheetah").rglob("*.py")):
        text = source.read_text(encoding="utf-8")
        hits += [f"{source.relative_to(root)}: {marker}" for marker in CONTINUATION_MARKERS if marker in text]
    return hits


def test_maintained_continuation_manifests_verify():
    assert maintained_manifest_problems(ROOT) == []


def test_earned_light_intake_bytes_all_survive_the_import():
    assert earned_light_intake_problems(ROOT) == []


def test_sovereign_choice_forge_manifests_verify_apart_from_omitted_lineage():
    assert sovereign_forge_problems(ROOT) == []


def test_installed_package_does_not_import_frozen_continuations():
    assert runtime_imports_of_continuations(ROOT) == []
