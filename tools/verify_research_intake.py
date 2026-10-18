#!/usr/bin/env python3
"""Check exact research-intake bytes and their explicit wrapper footing.

This is an integrity check, not a truth, licensing or security certification.
The raw candidates remain frozen so dated integration corrections can coexist
with reproducible historical failures.
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
        footing = (root / review).read_text(encoding="utf-8")
        if "**[SCAFFOLD]" not in footing or "experimental" not in footing.lower():
            raise ValueError("source wrapper lacks explicit experimental footing")
        folder = root / destination
        disk = {p.relative_to(folder).as_posix() for p in folder.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
                and ".pytest_cache" not in p.parts and p.suffix != ".pyc"}
        if disk != set(hashes):
            raise ValueError(f"source tree membership changed: {destination}")
        for name, digest in hashes.items():
            relative_path(name)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("invalid SHA-256 value")
            target = folder / name
            if target.is_symlink() or root not in target.resolve().parents:
                raise ValueError("source escapes repository or contains a symlink")
            data = target.read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"source bytes changed: {destination}/{name}")
            files[f"{destination}/{name}"] = review
            bytes_checked += len(data)
    return {"releases_checked": len(seen), "files_checked": len(files),
            "bytes_checked": bytes_checked, "file_footing": files}


def main() -> int:
    try:
        report = verify(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"RESEARCH INTAKE FAILED: {error}", file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in report.items() if k != "file_footing"}))
    print("SHA-256 consistency and research footing only; no truth claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
