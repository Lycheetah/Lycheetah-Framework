"""
Tests for LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES — one editable home for the collected texts.

The collection's own rule (SOURCE_MANIFEST.json "home_rule"): edit collected texts there;
original paths keep provenance. rebuild.py reports drift in VERIFICATION.json but fails
nothing, and nothing ran it automatically. These tests make the rule visible.

Claim coverage:
  [ACTIVE] originals outside the collection still match the bytes that were imported
  [ACTIVE] every collected text matches the hash its manifest records (no edit without rebuild)
  [ACTIVE] the generated reading editions match the receipt (no hand edits to outputs)
"""

import hashlib
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOME = REPO / "LYCHEETAH_MYTHOS" / "SCRIPTURES_AND_STORIES"
MANIFEST = json.loads((HOME / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
RECEIPT = json.loads((HOME / "VERIFICATION.json").read_text(encoding="utf-8"))

# Navigation pages that already point to the collection; their drift is recorded by rebuild.py.
NAVIGATION = {"LYCHEETAH_MYTHOS/00_INDEX.md", "LYCHEETAH_MYTHOS/README.md"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_originals_unchanged_since_import():
    changed = [e["origin"] for e in MANIFEST["texts"]
               if e.get("origin") and e["origin"] not in NAVIGATION
               and sha(REPO / e["origin"]) != e["import_sha256"]]
    assert not changed, (
        "Edited at the old path instead of the collection: %s. Make the revision under "
        "SCRIPTURES_AND_STORIES/ and run rebuild.py, or record Mac's decision to move "
        "that text's home. (LYCHEETAH_EPIC/tools/build-listening-edition.mjs still reads "
        "the Epic originals.)" % changed)


def test_collected_texts_match_manifest():
    stale = [e["file"] for e in MANIFEST["texts"] if sha(HOME / e["file"]) != e["current_sha256"]]
    assert not stale, "Collected text edited without rebuild.py: %s" % stale


@pytest.mark.parametrize("name", sorted(RECEIPT["outputs"]))
def test_generated_outputs_match_receipt(name):
    assert sha(HOME / name) == RECEIPT["outputs"][name], (
        "%s differs from VERIFICATION.json; edit sources and run rebuild.py" % name)
