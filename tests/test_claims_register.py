"""
The claim counts have one truth: the `claims` array in 28_DEFENSE/CLAIMS.json.
README.md, llms.txt, FIVE_MINUTE_BRIEF.md and ai-meta.json repeat those counts;
this test fails when any of them drifts.

Added 2026-10-03, after an outside reader found three different totals: 60 in the
README, 136 in the register's own total_claims field, and 67 actual records.
"""

import importlib.util
import os
import shutil

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
_spec = importlib.util.spec_from_file_location(
    "verify_claims", os.path.join(ROOT, "tools", "verify-claims.py"))
verify_claims = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify_claims)

MIRRORED = [verify_claims.CLAIMS_PATH, verify_claims.META_PATH, *verify_claims.MIRRORS]


@pytest.mark.active
def test_register_and_every_mirror_agree():
    _truth, errors = verify_claims.check_register()
    assert errors == [], "\n".join(errors)


@pytest.mark.active
def test_register_check_fails_on_a_drifted_mirror(tmp_path):
    """A gate means nothing until it has been seen to fail."""
    for rel in MIRRORED:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), dest)
    truth, _ = verify_claims.check_register(str(tmp_path))
    readme = tmp_path / "README.md"
    text = readme.read_text(encoding="utf-8")
    phrase = f"contains {truth['total']} structured claim records"
    assert phrase in text
    readme.write_text(text.replace(phrase, f"contains {truth['total'] + 1} structured claim records"),
                      encoding="utf-8")
    _truth, errors = verify_claims.check_register(str(tmp_path))
    assert any("README.md" in e and "total" in e for e in errors)
