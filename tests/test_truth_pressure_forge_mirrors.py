"""The Truth Pressure forge ships every bundle twice.

Each bundle exists as a zip under TRUTH_PRESSURE/FORGE_2026-08-02/ and expanded
under TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/. Two copies of frozen evidence are
one truth only while they stay byte-identical, so this pins the mirror in both
directions and verifies the forge's own SHA-256 manifest.
"""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORGE = Path("TRUTH_PRESSURE/FORGE_2026-08-02")
EXPANDED = Path("TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED")


def mirror_mismatches(root: Path) -> list[str]:
    problems: list[str] = []
    zips = sorted((root / FORGE).rglob("*.zip"))
    if not zips:
        return ["no forge zips found"]
    bundles = set()
    for zip_path in zips:
        bundle = zip_path.stem
        bundles.add(bundle)
        with zipfile.ZipFile(zip_path) as archive:
            members = {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
        expanded = root / EXPANDED / bundle
        if not expanded.is_dir():
            problems.append(f"{bundle}: zip has no expanded copy")
            continue
        on_disk = {
            path.relative_to(root / EXPANDED).as_posix(): path
            for path in expanded.rglob("*") if path.is_file()
        }
        for name, data in members.items():
            if name not in on_disk:
                problems.append(f"{name}: in zip, missing from expanded tree")
            elif on_disk[name].read_bytes() != data:
                problems.append(f"{name}: zip and expanded bytes differ")
        problems.extend(f"{name}: in expanded tree, missing from zip" for name in sorted(on_disk.keys() - members.keys()))
    problems.extend(
        f"{path.name}: expanded bundle has no zip"
        for path in sorted((root / EXPANDED).iterdir()) if path.is_dir() and path.name not in bundles
    )
    return problems


def manifest_mismatches(root: Path) -> list[str]:
    base = root / FORGE
    problems: list[str] = []
    entries = [line for line in (base / "SHA256_MANIFEST.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not entries:
        return ["forge manifest is empty"]
    for line in entries:
        digest, rel = line.split(maxsplit=1)
        rel = rel[2:] if rel.startswith("./") else rel
        target = base / rel
        if not target.is_file():
            problems.append(f"{rel}: listed in manifest, missing")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            problems.append(f"{rel}: sha256 differs from manifest")
    return problems


def test_forge_zips_mirror_the_expanded_tree_byte_for_byte():
    assert mirror_mismatches(ROOT) == []


def test_forge_sha256_manifest_verifies():
    assert manifest_mismatches(ROOT) == []
