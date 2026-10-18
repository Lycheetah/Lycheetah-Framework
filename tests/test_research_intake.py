"""Known failures exercise the preservation gate on disposable source copies."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("intake_gate", ROOT / "tools/verify_research_intake.py")
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


@pytest.fixture
def sample(tmp_path):
    folder = tmp_path / "research/source"
    folder.mkdir(parents=True)
    (folder / "record.txt").write_text("retained counterexample\n")
    (tmp_path / "research/README.md").write_text("**[SCAFFOLD] Experimental research**\n")
    manifest = {"schema": "lycheetah.research-intake.v1", "sources": [{
        "destination": "research/source", "file_count": 1,
        "files_sha256": {"record.txt": hashlib.sha256((folder / "record.txt").read_bytes()).hexdigest()},
    }]}
    (tmp_path / GATE.MANIFEST).parent.mkdir(parents=True)
    (tmp_path / GATE.MANIFEST).write_text(json.dumps(manifest))
    return tmp_path, manifest, {"research/source": (1, "research/README.md")}


def test_all_incoming_files_have_their_original_bytes():
    report = GATE.verify(ROOT)
    assert report["releases_checked"] == 4
    assert report["files_checked"] == 444
    assert report["bytes_checked"] > 50_000_000


def test_benign_source_copy_passes(sample):
    root, _, config = sample
    assert GATE.verify(root, config)["files_checked"] == 1


@pytest.mark.parametrize("change", ["changed", "missing", "extra", "symlink"])
def test_known_source_failures_are_detected(sample, change):
    root, _, config = sample
    record = root / "research/source/record.txt"
    if change == "changed":
        record.write_text("negative result erased")
    elif change == "missing":
        record.unlink()
    elif change == "extra":
        (record.parent / "unreviewed.txt").write_text("new claim")
    else:
        record.unlink()
        record.symlink_to(root / "research/README.md")
    with pytest.raises(ValueError):
        GATE.verify(root, config)


@pytest.mark.parametrize("change", ["zero_count", "duplicate", "traversal", "bad_hash", "schema"])
def test_malformed_manifest_refused(sample, change):
    root, original, config = sample
    manifest = deepcopy(original)
    source = manifest["sources"][0]
    if change == "zero_count":
        source["file_count"] = 0
    elif change == "duplicate":
        manifest["sources"].append(deepcopy(source))
    elif change == "traversal":
        source["destination"] = "../research/source"
    elif change == "bad_hash":
        source["files_sha256"]["record.txt"] = "not-sha256"
    else:
        manifest["schema"] = "unknown"
    (root / GATE.MANIFEST).write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        GATE.verify(root, config)


def test_wrapper_must_declare_research_footing(sample):
    root, _, config = sample
    (root / "research/README.md").write_text("Everything is proven.")
    with pytest.raises(ValueError, match="footing"):
        GATE.verify(root, config)
