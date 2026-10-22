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


CODEC = Path(__file__).resolve().parents[1] / "03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/src/lamague_codec.py"


def field_row(record, field):
    return {row["field"]: row for row in checker.check(record)}[field]


def test_protected_fields_are_the_codec_critical_fields():
    spec = importlib.util.spec_from_file_location("lamague_codec_fields", CODEC)
    codec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(codec)
    assert set(checker.FIELDS) == set(codec.CRITICAL_FIELDS)


@pytest.mark.parametrize("value", [False, True, ["TBD", ""], {"who": "", "why": None}, [None]])
def test_values_that_carry_no_content_are_gaps(value):
    assert field_row({"dissent": value}, "dissent")["status"] == "EMPTY"


@pytest.mark.parametrize("key, field", [("no_rollback", "recovery"), ("without_dissent", "dissent"),
                                        ("disclaim", "claim")])
def test_negated_or_part_word_keys_do_not_carry_the_field(key, field):
    assert field_row({key: "something"}, field)["status"] == "MISSING"


@pytest.mark.parametrize("key, field", [("customer_affected_parties", "affectedParties"),
                                        ("postmortemRollback", "recovery")])
def test_whole_word_suffixes_still_match(key, field):
    assert field_row({key: "something"}, field)["status"] == "PRESENT"


def test_the_records_own_field_beats_a_nested_placeholder():
    row = field_row({"meta": {"owner": ""}, "owner": "alice"}, "authority")
    assert (row["status"], row["found_as"]) == ("PRESENT", "owner")


def test_built_in_demo_still_carries_six_fields():
    assert sum(row["status"] == "PRESENT" for row in checker.check(checker.DEMO)) == 6
