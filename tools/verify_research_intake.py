#!/usr/bin/env python3
"""Check exact research-intake bytes and their explicit wrapper footing.

This is an integrity check, not a truth, licensing or security certification.
The raw candidates remain frozen so dated integration corrections can coexist
with reproducible historical failures.

Three kinds of preserved source are checked (RV30, 2026-10-22):
- the 2026-10-18 intake (444 files, one manifest entry per release folder);
- the 2026-10-19 intake (225 entries, one per file), whose unchanged files in the
  two agent-safety folders are pinned and whose remaining entries must be accounted
  for by a named home;
- supplied bundles that carry their own `SHA256SUMS.txt`.
A maintained wrapper beside each source declares its footing. Documents inside the
source inherit that footing only after their exact bytes verify.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

MANIFEST = "28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json"
RELEASES = {
    "papers/agent-safety/earned-trust/cycles_001_009":
        (148, "papers/agent-safety/earned-trust/README.md"),
    "papers/ai-futures/hybrid-gateway/v1.2":
        (138, "papers/ai-futures/hybrid-gateway/README.md"),
    "03_LAMAGUE_L1/26_SXP_L_RESEARCH/handoff_2026-10-18":
        (46, "03_LAMAGUE_L1/26_SXP_L_RESEARCH/README.md"),
    "03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0":
        (112, "03_LAMAGUE_L1/26_SXP_L_RESEARCH/README.md"),
}

LATER_MANIFEST = "28_DEFENSE/RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json"
# folder: (unchanged files pinned, footing wrapper, maintained files beside them).
# Maintained files are integration additions or edited wrappers; they are not pinned.
LATER = {
    "papers/agent-safety/earned-light":
        (91, "papers/agent-safety/earned-light/README.md",
         {"README.md", "verify.py",
          # pointer stubs left where moved files used to be
          "intake/research_archive/Earned_Light_Full_Handoff/START_HERE_FORGE07.md",
          "intake/story/THE_LAST_LIGHTHOUSE_OF_ETERNITY_EXPANDED.md",
          "intake/story/THE_LAST_LIGHTHOUSE_OF_ETERNITY_ORIGINAL.md"}),
    "papers/agent-safety/sovereign-choice-research":
        (119, "papers/agent-safety/sovereign-choice-research/README.md",
         {"README.md", "verify.py"}),
}
# Entries that left the pinned folders, and where they are checked instead.
LATER_ELSEWHERE = {
    # pinned by tests/test_scripture_collection_one_home.py against the collection manifest
    "LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/TEXTS/ORIGINAL_NARRATIVES": 3,
    # maintained integration documents; dated corrections are expected here
    "35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL": 11,
}

# folder: (files listed in its SHA256SUMS.txt, footing wrapper, files beside them)
SUMS_BUNDLES = {
    "23_NZ_AI_GOVERNANCE/anon_politician":
        (121, "23_NZ_AI_GOVERNANCE/anon_politician/README.md",
         {"README.md", "SHA256SUMS.txt"}),
    # RV31 (2026-10-22): an archive, so no footing is inherited (review None). Its sums pin 374
    # logs that `.gitignore` used to drop, so a clean clone failed them; they are now unignored.
    "99_ARCHIVE/closed_loop_agent_lab":
        (1788, None, {"README.md", "SHA256SUMS.txt"}),
}


def relative_path(value: str) -> PurePosixPath:
    if (not isinstance(value, str) or not value or "\\" in value
            or value.startswith("/") or ".." in value.split("/")
            or PurePosixPath(value).as_posix() != value):
        raise ValueError("manifest path must be normalized and relative")
    return PurePosixPath(value)


def verify(root: Path, releases=None) -> dict:
    """Return all checked file identities; any mismatch fails visibly."""
    root = root.resolve()
    releases = RELEASES if releases is None else releases
    raw = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if raw.get("schema") != "lycheetah.research-intake.v1":
        raise ValueError("unrecognized intake schema")
    sources = raw.get("sources")
    if not isinstance(sources, list) or len(sources) != len(releases):
        raise ValueError("unexpected number of source releases")
    seen = set()
    files = {}
    bytes_checked = 0
    for source in sources:
        destination = source["destination"]
        relative_path(destination)
        if destination not in releases or destination in seen:
            raise ValueError("unknown or duplicate source destination")
        seen.add(destination)
        expected_count, review = releases[destination]
        hashes = source["files_sha256"]
        if (not isinstance(hashes, dict) or not expected_count
                or len(hashes) != expected_count or source["file_count"] != expected_count):
            raise ValueError("source file count mismatch")
        require_footing(root, review)
        folder = root / destination
        if disk_files(folder) != set(hashes):
            raise ValueError(f"source tree membership changed: {destination}")
        for name, digest in hashes.items():
            bytes_checked += check_file(root, folder, name, digest, f"{destination}/{name}")
            files[f"{destination}/{name}"] = review
    return {"releases_checked": len(seen), "files_checked": len(files),
            "bytes_checked": bytes_checked, "file_footing": files}


def require_footing(root: Path, review: str) -> None:
    footing = (root / review).read_text(encoding="utf-8")
    if "**[SCAFFOLD]" not in footing or "experimental" not in footing.lower():
        raise ValueError(f"source wrapper lacks explicit experimental footing: {review}")


def disk_files(folder: Path) -> set:
    if not folder.is_dir():
        raise ValueError(f"source folder missing: {folder.name}")
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
            and ".pytest_cache" not in p.parts and p.suffix != ".pyc"}


def check_file(root: Path, folder: Path, name: str, digest, label: str) -> int:
    relative_path(name)
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("invalid SHA-256 value")
    target = folder / name
    if target.is_symlink() or root not in target.resolve().parents:
        raise ValueError("source escapes repository or contains a symlink")
    data = target.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"source bytes changed: {label}")
    return len(data)


def verify_later(root: Path, packages=None, elsewhere=None) -> dict:
    """Pin the unchanged files of the 2026-10-19 intake; account for every entry."""
    root = root.resolve()
    packages = LATER if packages is None else packages
    elsewhere = LATER_ELSEWHERE if elsewhere is None else elsewhere
    raw = json.loads((root / LATER_MANIFEST).read_text(encoding="utf-8"))
    if raw.get("schema") != "lycheetah.research-intake.v1":
        raise ValueError("unrecognized intake schema")
    entries = raw.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("later intake lists no files")
    pinned = {folder: {} for folder in packages}
    edited = {folder: set() for folder in packages}
    away = {folder: 0 for folder in elsewhere}
    seen = set()
    for entry in entries:
        destination = entry["destination"]
        relative_path(destination)
        if destination in seen:
            raise ValueError("duplicate destination in later intake")
        seen.add(destination)
        home = [f for f in packages if destination.startswith(f + "/")]
        if not home:
            other = [f for f in elsewhere if destination.startswith(f + "/")]
            if not other:
                raise ValueError(f"later intake entry has no named home: {destination}")
            away[other[0]] += 1
            continue
        name = destination[len(home[0]) + 1:]
        if entry["changed_since_import"] is False and entry["import_sha256"] == entry["current_sha256"]:
            pinned[home[0]][name] = entry["import_sha256"]
        else:
            edited[home[0]].add(name)
    if away != dict(elsewhere):
        raise ValueError(f"later intake entries moved: {away}")
    files, bytes_checked = {}, 0
    for folder, (expected, review, maintained) in packages.items():
        if len(pinned[folder]) != expected:
            raise ValueError(f"later intake pinned count changed: {folder}")
        if not edited[folder] <= maintained:
            raise ValueError(f"edited import file is not a named wrapper: {folder}")
        require_footing(root, review)
        base = root / folder
        if disk_files(base) != set(pinned[folder]) | maintained:
            raise ValueError(f"source tree membership changed: {folder}")
        for name, digest in pinned[folder].items():
            bytes_checked += check_file(root, base, name, digest, f"{folder}/{name}")
            files[f"{folder}/{name}"] = review
    return {"files_checked": len(files), "bytes_checked": bytes_checked,
            "entries_elsewhere": sum(away.values()), "file_footing": files}


def verify_sums_bundles(root: Path, bundles=None) -> dict:
    """Pin supplied bundles against their own SHA256SUMS.txt (`sha256sum -c` format).

    A bundle whose review path is None is an archive: its bytes are pinned, but it lends no
    footing to the claim gate."""
    root = root.resolve()
    bundles = SUMS_BUNDLES if bundles is None else bundles
    files, checked, bytes_checked = {}, 0, 0
    for folder, (expected, review, beside) in bundles.items():
        relative_path(folder)
        base = root / folder
        sums = {}
        for line in (base / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, _, name = line.partition("  ")
            name = name.removeprefix("*")
            if not name or name in sums:
                raise ValueError(f"malformed or duplicate checksum line: {folder}")
            sums[name] = digest
        if len(sums) != expected:
            raise ValueError(f"bundle file count mismatch: {folder}")
        if review is not None:
            require_footing(root, review)
        if disk_files(base) != set(sums) | beside:
            raise ValueError(f"source tree membership changed: {folder}")
        for name, digest in sums.items():
            bytes_checked += check_file(root, base, name, digest, f"{folder}/{name}")
            checked += 1
            if review is not None:
                files[f"{folder}/{name}"] = review
    return {"bundles_checked": len(bundles), "files_checked": checked,
            "bytes_checked": bytes_checked, "file_footing": files}


def verify_all(root: Path) -> dict:
    """Every preserved source this gate knows; any failure fails the whole check."""
    parts = [verify(root), verify_later(root), verify_sums_bundles(root)]
    footing = {}
    for part in parts:
        footing.update(part["file_footing"])
    return {"releases_checked": parts[0]["releases_checked"],
            "later_files_checked": parts[1]["files_checked"],
            "later_entries_elsewhere": parts[1]["entries_elsewhere"],
            "bundles_checked": parts[2]["bundles_checked"],
            "files_checked": sum(part["files_checked"] for part in parts),
            "bytes_checked": sum(part["bytes_checked"] for part in parts),
            "file_footing": footing}


def main() -> int:
    try:
        report = verify_all(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"RESEARCH INTAKE FAILED: {error}", file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in report.items() if k != "file_footing"}))
    print("SHA-256 consistency and research footing only; no truth claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
