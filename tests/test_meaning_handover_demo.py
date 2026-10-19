"""Full-record changes, independent baseline decoding and user-visible demo receipts."""

from __future__ import annotations

import base64
import copy
import gzip
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples/meaning_handover/demo.py"
spec = importlib.util.spec_from_file_location("meaning_handover_demo", SCRIPT)
assert spec and spec.loader
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
PACKET = json.loads((SCRIPT.parent / "case.json").read_text(encoding="utf-8"))["packet"]


@pytest.mark.parametrize("field", demo.REQUIRED_FIELDS)
def test_each_missing_declared_field_is_rejected(field):
    candidate = copy.deepcopy(PACKET)
    del candidate[field]
    result = demo.compare_records(PACKET, candidate)
    assert result["status"] == "MALFORMED_RECORD"
    assert result["record_match"] is False
    assert result["fields_examined"] == 17
    assert [change["field"] for change in result["changes"]] == [field]
    assert result["changes"][0]["after_present"] is False


def test_reordered_keys_pass_without_false_alarm_and_do_not_mutate_inputs():
    candidate = dict(reversed(list(copy.deepcopy(PACKET).items())))
    candidate["authority"][0] = dict(reversed(list(candidate["authority"][0].items())))
    snapshot = copy.deepcopy(candidate)
    result = demo.compare_records(PACKET, candidate)
    assert result["record_match"] is True
    assert result["unchanged_fields"] == 17
    assert candidate == snapshot


@pytest.mark.parametrize("field,new_value", [
    ("risk", "LOW"),
    ("evidence", [{"id": "false", "text": "All tests passed.", "provenance": "invented"}]),
    ("horizon", "Act immediately."),
    ("yield", "Publish immediately."),
])
def test_full_check_rejects_changes_that_the_critical_projection_does_not(field, new_value):
    candidate = copy.deepcopy(PACKET)
    candidate[field] = new_value
    result = demo.compare_records(PACKET, candidate)
    assert result["codec_classification"]["classification"] == "PARTIAL_EQUIVALENT"
    assert result["record_match"] is False
    assert result["status"] == "CHANGED_RECORD"
    assert result["changes"][0]["field"] == field


def test_reattributing_an_objection_is_a_change_even_when_list_lengths_match():
    candidate = copy.deepcopy(PACKET)
    candidate["dissent"][0]["party"] = "Mira"
    result = demo.compare_records(PACKET, candidate)
    assert result["record_match"] is False
    assert result["changes"][0]["before"][0]["party"] == "Jules"
    assert result["changes"][0]["after"][0]["party"] == "Mira"


def test_permission_expansion_and_lost_unknowns_are_visible():
    cases = {item["id"]: item for item in demo.controls(PACKET)}
    assert cases["permission"]["comparison"]["record_match"] is False
    assert cases["unknowns"]["comparison"]["record_match"] is False
    assert cases["unknowns"]["comparison"]["changes"][0]["after"] == []
    assert len(cases) == 12
    assert sum(row["expected_exact"] for row in cases.values()) == 2
    assert all(row["comparison"]["record_match"] == row["expected_exact"] for row in cases.values())


@pytest.mark.parametrize("candidate", [None, [], "not a packet", {**PACKET, "risk": []}])
def test_malformed_candidate_never_gets_an_exact_result(candidate):
    result = demo.compare_records(PACKET, candidate)
    assert result["status"] == "MALFORMED_RECORD"
    assert result["record_match"] is False


def test_baselines_restore_independently_and_pay_for_complete_text_messages():
    rows = {row["id"]: row for row in demo.formats(PACKET)}
    assert json.loads(rows["json"]["wire"]) == PACKET
    gzip_wire = rows["gzip-json"]["wire"]
    assert gzip_wire.startswith("GZ1")
    assert json.loads(gzip.decompress(base64.b64decode(gzip_wire[3:]))) == PACKET
    assert demo.decode(rows["lamague"]["wire"]) == PACKET
    for row in rows.values():
        assert row["bytes"] == len(row["wire"].encode("utf-8"))
        assert row["fields_preserved"] == 17
        for budget in (1024, 2048, 4096):
            assert row["budget_fit"][str(budget)] == (row["bytes"] <= budget)


def test_unicode_uses_utf8_bytes_not_character_count():
    packet = copy.deepcopy(PACKET)
    packet["purpose"] = "Review in Ōtepoti. 保留疑问。"
    for row in demo.formats(packet):
        assert row["exact_roundtrip"] is True
        assert row["bytes"] == len(row["wire"].encode("utf-8"))


@pytest.mark.parametrize("change,expected", [("same", 0), ("scope", 1), ("missing", 2), ("invalid-json", 2)])
def test_cli_exit_codes_distinguish_exact_changed_and_malformed(tmp_path, change, expected):
    reference = tmp_path / "reference.json"
    candidate_file = tmp_path / "candidate.json"
    reference.write_text(json.dumps(PACKET), encoding="utf-8")
    candidate = copy.deepcopy(PACKET)
    if change == "scope":
        candidate["authority"][0]["scope"] = "Publish immediately."
    if change == "missing":
        del candidate["authority"]
    candidate_file.write_text(
        "{" if change == "invalid-json" else json.dumps(candidate), encoding="utf-8"
    )
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--reference", str(reference), "--candidate", str(candidate_file)],
        capture_output=True, text=True, timeout=15,
    )
    assert run.returncode == expected, run.stdout + run.stderr
    if change == "scope":
        assert "changed: authority" in run.stdout
    assert sorted(path.name for path in tmp_path.iterdir()) == ["candidate.json", "reference.json"]


def test_page_data_cannot_close_its_script_element():
    report = demo.build_report()
    report["case"]["title"] = "</script><script>alert('injected')</script>"
    page = demo.render_page(report)
    assert "</script><script>alert('injected')</script>" not in page
    assert "\\u003c/script>" in page
    assert "__HANDOVER_REPORT_JSON__" not in page


def test_committed_reading_copies_match_current_source():
    report = demo.build_report()
    saved = json.loads((ROOT / "docs/lamague-handover-report.json").read_text(encoding="utf-8"))
    # Compression may vary with Python/zlib versions. The frozen artifact remains
    # inspectable; require identical output only in its recorded environment.
    assert saved["source_sha256"] == report["source_sha256"]
    assert saved["summary"] == report["summary"]
    if saved["environment"] == report["environment"]:
        assert saved == report
    page = (ROOT / "docs/lamague-handover.html").read_text(encoding="utf-8")
    assert page == demo.render_page(saved)
