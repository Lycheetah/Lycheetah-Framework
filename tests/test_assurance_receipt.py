import json

import pytest

from lycheetah.assurance import (
    AssuranceReceipt,
    AssuranceRuntime,
    ReceiptError,
    ReceiptLog,
    to_in_toto_statement,
)
from lycheetah.assurance.jsonutil import sha256_json


def test_receipt_json_round_trip_verifies():
    original = AssuranceRuntime().evaluate_text("Please verify this independently.")
    restored = AssuranceReceipt.from_json(original.to_json())
    assert restored.to_dict() == original.to_dict()
    assert restored.verify().valid


def test_mutation_is_detected():
    receipt = AssuranceRuntime().evaluate_text("Please verify this independently.")
    data = receipt.to_dict()
    data["decision"] = "BLOCK"
    mutated = AssuranceReceipt.from_dict(data)
    report = mutated.verify()
    assert not report.valid
    assert "digest mismatch" in report.errors[0]


def test_recomputed_digest_cannot_hide_inconsistent_decision():
    receipt = AssuranceRuntime().evaluate_text("Please verify this independently.")
    data = receipt.to_dict()
    data["decision"] = "BLOCK"
    body = {key: value for key, value in data.items() if key != "integrity"}
    data["integrity"]["digest"] = sha256_json(body)
    report = AssuranceReceipt.from_dict(data).verify()
    assert not report.valid
    assert any("strongest effective finding" in error for error in report.errors)


def test_recomputed_digest_cannot_bypass_evidence_cap():
    receipt = AssuranceRuntime().evaluate_tool(
        "refund.create", {}, side_effect=True
    )
    data = receipt.to_dict()
    data["findings"][0]["claim_status"] = "CONJECTURE"
    body = {key: value for key, value in data.items() if key != "integrity"}
    data["integrity"]["digest"] = sha256_json(body)
    report = AssuranceReceipt.from_dict(data).verify()
    assert not report.valid
    assert any("violates evidence cap" in error for error in report.errors)


def test_hmac_correct_key_authenticates():
    receipt = AssuranceRuntime().evaluate_text(
        "Please verify this independently.",
        hmac_secret=b"correct horse battery staple",
        hmac_key_id="test-key",
    )
    report = receipt.verify(b"correct horse battery staple")
    assert report.valid
    assert report.hmac_authenticated


def test_hmac_wrong_key_is_rejected():
    receipt = AssuranceRuntime().evaluate_text(
        "Please verify this independently.",
        hmac_secret=b"correct",
        hmac_key_id="test-key",
    )
    report = receipt.verify(b"wrong")
    assert not report.valid
    assert "HMAC seal mismatch" in report.errors


def test_hmac_without_key_preserves_hash_verification_but_warns():
    receipt = AssuranceRuntime().evaluate_text(
        "Please verify this independently.",
        hmac_secret=b"correct",
        hmac_key_id="test-key",
    )
    report = receipt.verify()
    assert report.valid
    assert not report.hmac_authenticated
    assert report.warnings


def test_hmac_requires_key_id():
    with pytest.raises(ReceiptError):
        AssuranceRuntime().evaluate_text(
            "Please verify this independently.", hmac_secret=b"secret"
        )


def test_hmac_rejects_empty_secret():
    with pytest.raises(ReceiptError):
        AssuranceRuntime().evaluate_text(
            "Please verify this independently.",
            hmac_secret=b"",
            hmac_key_id="test-key",
        )


def test_valid_jsonl_chain(tmp_path):
    path = tmp_path / "receipts.jsonl"
    log = ReceiptLog(path)
    runtime = AssuranceRuntime()
    first = runtime.evaluate_text("First", previous_receipt_sha256=log.tail_digest)
    log.append(first)
    second = runtime.evaluate_text("Second", previous_receipt_sha256=log.tail_digest)
    log.append(second)
    report = log.verify()
    assert report.valid
    assert report.receipt_count == 2
    assert report.tail_digest == second.digest


def test_swapped_chain_members_are_detected(tmp_path):
    path = tmp_path / "receipts.jsonl"
    runtime = AssuranceRuntime()
    first = runtime.evaluate_text("First")
    second = runtime.evaluate_text("Second", previous_receipt_sha256=first.digest)
    path.write_text(second.to_json(indent=None) + "\n" + first.to_json(indent=None) + "\n")
    report = ReceiptLog(path).verify()
    assert not report.valid
    assert any("chain link mismatch" in item for item in report.errors)


def test_removed_interior_member_is_detected(tmp_path):
    path = tmp_path / "receipts.jsonl"
    runtime = AssuranceRuntime()
    first = runtime.evaluate_text("First")
    second = runtime.evaluate_text("Second", previous_receipt_sha256=first.digest)
    third = runtime.evaluate_text("Third", previous_receipt_sha256=second.digest)
    path.write_text(first.to_json(indent=None) + "\n" + third.to_json(indent=None) + "\n")
    report = ReceiptLog(path).verify()
    assert not report.valid


def test_append_rejects_wrong_parent(tmp_path):
    log = ReceiptLog(tmp_path / "receipts.jsonl")
    runtime = AssuranceRuntime()
    log.append(runtime.evaluate_text("First"))
    with pytest.raises(ReceiptError):
        log.append(runtime.evaluate_text("Wrong parent"))


def test_jsonl_hmac_verification_rejects_wrong_or_missing_key(tmp_path):
    path = tmp_path / "sealed.jsonl"
    log = ReceiptLog(path)
    receipt = AssuranceRuntime().evaluate_text(
        "First",
        hmac_secret=b"correct",
        hmac_key_id="key-1",
    )
    log.append(receipt, {"key-1": b"correct"})
    assert log.verify({"key-1": b"correct"}).valid
    assert not log.verify({"key-1": b"wrong"}).valid
    missing = log.verify({"different-key": b"correct"})
    assert not missing.valid
    assert any("no HMAC key" in error for error in missing.errors)


def test_authenticated_append_rejects_unsealed_receipt(tmp_path):
    log = ReceiptLog(tmp_path / "sealed.jsonl")
    with pytest.raises(ReceiptError):
        log.append(
            AssuranceRuntime().evaluate_text("Unsealed"),
            {"key-1": b"correct"},
        )


def test_in_toto_statement_binds_subject_digest():
    receipt = AssuranceRuntime().evaluate_tool("lookup_order", {"id": 7})
    statement = to_in_toto_statement(receipt)
    assert statement["_type"] == "https://in-toto.io/Statement/v1"
    assert statement["subject"][0]["digest"]["sha256"] == receipt.event["subject"]["sha256"]
    assert statement["predicate"]["receipt"]["receipt_id"] == receipt.receipt_id


def test_receipt_rejects_missing_fields():
    with pytest.raises(ReceiptError):
        AssuranceReceipt.from_dict({"schema_version": "0.1"})


def test_receipt_rejects_unknown_top_level_fields():
    data = AssuranceRuntime().evaluate_text("Review this.").to_dict()
    data["untrusted_extension"] = {"decision": "ALLOW"}
    with pytest.raises(ReceiptError):
        AssuranceReceipt.from_dict(data)


def test_malformed_hmac_seal_is_invalid_without_verification_key():
    data = AssuranceRuntime().evaluate_text("Review this.").to_dict()
    data["integrity"]["seal"] = {
        "algorithm": "hmac-sha256",
        "key_id": "test",
        "value": "not-a-mac",
    }
    body = {key: value for key, value in data.items() if key != "integrity"}
    data["integrity"]["digest"] = sha256_json(body)
    report = AssuranceReceipt.from_dict(data).verify()
    assert not report.valid
    assert any("HMAC seal value" in error for error in report.errors)


def test_compact_json_is_one_line_and_parseable():
    receipt = AssuranceRuntime().evaluate_text("Please verify this independently.")
    compact = receipt.to_json(indent=None)
    assert "\n" not in compact
    assert json.loads(compact)["integrity"]["digest"] == receipt.digest
