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


# ---- RV30 (2026-10-22): the later per-file intake and checksummed bundles ----

def test_later_intake_and_bundle_pin_their_unchanged_files():
    later = GATE.verify_later(ROOT)
    assert later["files_checked"] == 210
    assert later["entries_elsewhere"] == 14
    assert GATE.verify_sums_bundles(ROOT)["files_checked"] == 121 + 1788   # + RV31 lab archive
    assert GATE.verify_all(ROOT)["files_checked"] == 444 + 210 + 121 + 1788


def _entry(destination, data, changed=False):
    digest = hashlib.sha256(data).hexdigest()
    return {"destination": destination, "changed_since_import": changed,
            "import_sha256": digest, "current_sha256": digest if not changed else "0" * 64}


@pytest.fixture
def later(tmp_path):
    pack = tmp_path / "pack"
    (pack / "forge").mkdir(parents=True)
    (pack / "forge/RESULT.md").write_bytes(b"the comparator tied\n")
    (pack / "README.md").write_text("**[SCAFFOLD]** experimental archive\n")
    (tmp_path / "away").mkdir()
    entries = [_entry("pack/forge/RESULT.md", b"the comparator tied\n"),
               _entry("pack/README.md", b"original wrapper\n", changed=True),
               _entry("away/STORY.md", b"moved\n")]
    (tmp_path / GATE.LATER_MANIFEST).parent.mkdir(parents=True)
    manifest = {"schema": "lycheetah.research-intake.v1", "files": entries}
    (tmp_path / GATE.LATER_MANIFEST).write_text(json.dumps(manifest))
    return tmp_path, manifest, {"pack": (1, "pack/README.md", {"README.md"})}, {"away": 1}


def test_benign_later_copy_passes(later):
    root, _, packages, elsewhere = later
    report = GATE.verify_later(root, packages, elsewhere)
    assert report["files_checked"] == 1
    assert report["file_footing"] == {"pack/forge/RESULT.md": "pack/README.md"}


@pytest.mark.parametrize("change", ["changed", "extra", "missing", "no_home", "edited_source",
                                    "footing", "moved_count"])
def test_known_later_failures_are_detected(later, change):
    root, manifest, packages, elsewhere = later
    if change == "changed":
        (root / "pack/forge/RESULT.md").write_text("the comparator lost\n")
    elif change == "extra":
        (root / "pack/forge/NEW_CLAIM.md").write_text("proven\n")
    elif change == "missing":
        (root / "pack/forge/RESULT.md").unlink()
    elif change == "no_home":
        manifest["files"].append(_entry("elsewhere/UNTRACKED.md", b"x"))
    elif change == "edited_source":
        manifest["files"][0]["changed_since_import"] = True
    elif change == "footing":
        (root / "pack/README.md").write_text("Validated in production.\n")
    else:
        elsewhere = {"away": 2}
    (root / GATE.LATER_MANIFEST).write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        GATE.verify_later(root, packages, elsewhere)


@pytest.fixture
def bundle(tmp_path):
    base = tmp_path / "bundle"
    (base / "docs").mkdir(parents=True)
    (base / "docs/SPEC.md").write_bytes(b"hypothesis, untested\n")
    (base / "README.md").write_text("**[SCAFFOLD]** experimental bundle\n")
    digest = hashlib.sha256(b"hypothesis, untested\n").hexdigest()
    (base / "SHA256SUMS.txt").write_text(f"{digest}  docs/SPEC.md\n")
    return tmp_path, {"bundle": (1, "bundle/README.md", {"README.md", "SHA256SUMS.txt"})}


def test_benign_bundle_passes(bundle):
    root, config = bundle
    assert GATE.verify_sums_bundles(root, config)["files_checked"] == 1


@pytest.mark.parametrize("change", ["changed", "extra", "duplicate_line", "count", "footing"])
def test_known_bundle_failures_are_detected(bundle, change):
    root, config = bundle
    base = root / "bundle"
    if change == "changed":
        (base / "docs/SPEC.md").write_text("hypothesis, confirmed\n")
    elif change == "extra":
        (base / "docs/ADDED.md").write_text("unreviewed\n")
    elif change == "duplicate_line":
        sums = (base / "SHA256SUMS.txt").read_text()
        (base / "SHA256SUMS.txt").write_text(sums + sums)
    elif change == "count":
        config = {"bundle": (2, "bundle/README.md", {"README.md", "SHA256SUMS.txt"})}
    else:
        (base / "README.md").write_text("Everything here is proven.\n")
    with pytest.raises(ValueError):
        GATE.verify_sums_bundles(root, config)


# ---- RV31 (2026-10-22): the closed-loop lab archive must survive a clean clone ----

LAB = "99_ARCHIVE/closed_loop_agent_lab"


def test_lab_logs_pinned_by_its_sums_are_not_gitignored():
    import shutil
    import subprocess
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        pytest.skip("needs a git checkout")
    sums = (ROOT / LAB / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    logs = [f"{LAB}/{line.split('  ', 1)[1]}" for line in sums if line.endswith(".log")]
    assert len(logs) == 374
    # --no-index tests the ignore rules themselves, not whether the files happen to be tracked.
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=ROOT,
                             input="\n".join(logs), capture_output=True, text=True).stdout.split()
    assert not ignored, f"{len(ignored)} pinned lab logs are git-ignored, e.g. {ignored[:2]}"


def test_archive_bundle_pins_bytes_without_lending_footing(bundle):
    root, config = bundle
    (root / "bundle/README.md").write_text("Runnable lab suite\n")   # no footing words at all
    archive = {"bundle": (1, None, {"README.md", "SHA256SUMS.txt"})}
    report = GATE.verify_sums_bundles(root, archive)
    assert report["files_checked"] == 1 and report["file_footing"] == {}
    (root / "bundle/docs/SPEC.md").unlink()   # a clean clone without the ignored log
    with pytest.raises(ValueError):
        GATE.verify_sums_bundles(root, archive)

