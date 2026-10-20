"""Unknown field names must not count as every protected accountability field."""

import importlib.util
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "03_LAMAGUE_L1/24_LAMAGUE_CHECK/lamague_check.py"
SPEC = importlib.util.spec_from_file_location("decision_record_checker", SOURCE)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


@pytest.mark.parametrize("key", ["", "☃", "p", "pose"])
def test_unknown_key_cannot_satisfy_protected_fields(key):
    assert all(row["status"] == "MISSING" for row in checker.check({key: "unrelated"}))


def test_supported_nested_aliases_still_match():
    rows = {row["field"]: row for row in checker.check({"incident": {"objective": "restore", "rollback": "undo"}})}
    assert rows["purpose"]["found_as"] == "incident.objective"
    assert rows["recovery"]["found_as"] == "incident.rollback"
    assert sum(row["status"] == "PRESENT" for row in rows.values()) == 2


def test_populated_single_field_is_not_a_complete_record():
    rows = checker.check({"purpose": "a real stated purpose"})
    assert sum(row["status"] == "PRESENT" for row in rows) == 1


def test_empty_and_placeholder_values_are_reported_as_gaps():
    rows = {row["field"]: row for row in checker.check({"dissent": "TBD", "affectedParties": []})}
    assert rows["dissent"]["status"] == "EMPTY"
    assert rows["affectedParties"]["status"] == "EMPTY"
