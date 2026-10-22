"""Retained local evidence, read-only inspection and known corruptions.

These checks use a trusted fixture writer and declared approval metadata; they
do not establish external identity, consent or independent filesystem observation.
"""

from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from examples import guarded_handoff_risk_demo as demo
from lycheetah.assurance import AssuranceReceipt


@pytest.fixture
def bundle(tmp_path):
    directory = tmp_path / "handoff-evidence"
    report = demo.run_demo(directory)
    return directory, report


def _reseal_manifest(directory: Path) -> None:
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    for name in demo.BUNDLE_FILES:
        payload = (directory / name).read_bytes()
        manifest["files"][name] = {"bytes": len(payload), "sha256": sha256(payload).hexdigest()}
    path.write_bytes(demo._json_bytes(manifest))


def test_default_demo_remains_disposable():
    report = demo.run_demo()
    assert report["executor_calls"] == 1
    assert report["temporary_workspace_removed_on_exit"] is True
    assert "export" not in report
    assert report["risk_downgrade"]["provider_called"] is False
    assert report["action_substitution"]["provider_called"] is False
    assert report["replay"]["provider_called"] is False


def test_bundle_retains_full_receipt_and_observed_bytes_without_private_keys(bundle):
    directory, report = bundle
    assert {p.name for p in directory.iterdir()} == {*demo.BUNDLE_FILES, "manifest.json"}
    assert report["export"]["files"] == 8
    assert report["export"]["private_keys_exported"] is False
    assert (
        sha256((directory / "manifest.json").read_bytes()).hexdigest()
        == report["export"]["manifest_sha256"]
    )
    receipt = AssuranceReceipt.from_dict(
        json.loads((directory / "assurance-receipt.json").read_text())
    )
    assert receipt.verify().valid
    assert receipt.event["scope"] == "artifact:create"
    assert (
        directory / "handoff.txt"
    ).read_bytes() == b"One declared demo action, carried through a protected context packet.\n"
    result = demo.verify_bundle(directory)
    assert result["valid"] is True
    assert result["status"] == "SELF_CONSISTENT"
    assert result["retained_digest_supplied"] is False
    assert result["checks"] >= 25


def test_retained_manifest_digest_is_checked(bundle):
    directory, report = bundle
    digest = report["export"]["manifest_sha256"]
    assert demo.verify_bundle(directory, digest)["status"] == "MATCHES_RETAINED_DIGEST"
    result = demo.verify_bundle(directory, "0" * 64)
    assert result["valid"] is False
    assert "manifest differs from the retained digest" in result["errors"]


def test_existing_export_is_refused_before_starting_a_gateway(tmp_path, monkeypatch):
    directory = tmp_path / "existing"
    directory.mkdir()
    sentinel = directory / "keep-me"
    sentinel.write_bytes(b"existing user work")

    def unexpected_gateway(*args, **kwargs):
        pytest.fail("existing export should be refused before any gateway is opened")

    monkeypatch.setattr(demo, "SovereignExecutionHarness", unexpected_gateway)
    with pytest.raises(FileExistsError):
        demo.run_demo(directory)
    assert sentinel.read_bytes() == b"existing user work"
    assert len(list(directory.iterdir())) == 1


def test_dangling_export_symlink_is_refused(tmp_path):
    directory = tmp_path / "link"
    directory.symlink_to(tmp_path / "absent")
    with pytest.raises(FileExistsError):
        demo.run_demo(directory)
    assert not (tmp_path / "absent").exists()


@pytest.mark.parametrize(
    "name",
    ["handoff.txt", "assurance-receipt.json", "packet.json", "completed-task.json", "context.l1"],
)
def test_changed_evidence_fails_without_rewriting_manifest(bundle, name):
    directory, _ = bundle
    path = directory / name
    path.write_bytes(path.read_bytes() + b"changed")
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert f"{name} size or digest mismatch" in result["errors"]


@pytest.mark.parametrize("name", ["manifest.json", "assurance-receipt.json", "handoff.txt"])
def test_missing_evidence_cannot_report_success(bundle, name):
    directory, _ = bundle
    (directory / name).unlink()
    assert demo.verify_bundle(directory)["valid"] is False


def test_empty_directory_does_not_pass_a_zero_item_scan(tmp_path):
    result = demo.verify_bundle(tmp_path)
    assert result["valid"] is False
    assert result["checks"] == 0


def test_unsupported_manifest_paths_are_not_followed(bundle, tmp_path):
    directory, _ = bundle
    external = tmp_path / "outside"
    external.write_bytes(b"private outside fixture")
    manifest = json.loads((directory / "manifest.json").read_text())
    manifest["files"]["../outside"] = {"bytes": external.stat().st_size, "sha256": "0" * 64}
    (directory / "manifest.json").write_bytes(demo._json_bytes(manifest))
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert "missing or unexpected manifest files" in result["errors"]
    assert external.read_bytes() == b"private outside fixture"


def test_symlink_in_evidence_is_rejected_even_when_bytes_match(bundle, tmp_path):
    directory, _ = bundle
    original = directory / "handoff.txt"
    external = tmp_path / "external.txt"
    external.write_bytes(original.read_bytes())
    original.unlink()
    original.symlink_to(external)
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert any("bounded regular file" in error for error in result["errors"])


def test_duplicate_json_keys_are_not_silently_accepted(bundle):
    directory, _ = bundle
    path = directory / "manifest.json"
    text = path.read_text()
    path.write_text(text.replace('"schema":', '"schema": "duplicate", "schema":', 1))
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert any("duplicate JSON key" in error for error in result["errors"])


def test_rehashed_changed_output_still_fails_action_binding(bundle):
    directory, _ = bundle
    (directory / "handoff.txt").write_bytes(b"different bytes, with a fresh manifest")
    _reseal_manifest(directory)
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert "action does not bind the task, full context and observed bytes" in result["errors"]


def test_rehashed_receipt_mutation_fails_its_own_integrity_check(bundle):
    directory, _ = bundle
    path = directory / "assurance-receipt.json"
    receipt = json.loads(path.read_text())
    receipt["metrics"]["execution_status"] = "UNKNOWN"
    path.write_bytes(demo._json_bytes(receipt))
    _reseal_manifest(directory)
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert "assurance receipt integrity or decision mismatch" in result["errors"]


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("gateway_result", "status", "UNKNOWN"),
        ("gateway_result", "effect_id", "unrelated-effect"),
        ("gateway_result", "action_hash", "0" * 64),
        ("gateway_result", "checkpoint_generation", 999999),
        ("gateway_result", "result", {"status": "success", "sha256": "0" * 64}),
        ("permit", "bound_risk", "LOW"),
        ("permit", "compaction_critical_hash", "0" * 64),
        ("permit", "permit_digest", "0" * 64),
        (None, "witness_digest", "0" * 64),
        (None, "live_scope", "unrelated:scope"),
    ],
)
def test_rehashed_contradictory_run_report_does_not_pass(bundle, section, key, value):
    directory, _ = bundle
    path = directory / "run-report.json"
    report = json.loads(path.read_text())
    target = report["valid_execution"] if section is None else report["valid_execution"][section]
    target[key] = value
    path.write_bytes(demo._json_bytes(report))
    _reseal_manifest(directory)
    assert demo.verify_bundle(directory)["valid"] is False


def test_completion_cannot_omit_the_observed_write(bundle):
    directory, _ = bundle
    path = directory / "completed-task.json"
    completed = json.loads(path.read_text())
    completed["result"]["modified_files"] = []
    path.write_bytes(demo._json_bytes(completed))
    _reseal_manifest(directory)
    assert demo.verify_bundle(directory)["valid"] is False


def test_nonregular_manifest_is_rejected_before_reading(tmp_path, monkeypatch):
    path = tmp_path / "manifest.json"
    os.mkfifo(path)
    original_read = Path.read_bytes

    def guarded_read(self):
        if self == path:
            pytest.fail("a FIFO manifest must be rejected before opening it")
        return original_read(self)

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    result = demo.verify_bundle(tmp_path)
    assert result["valid"] is False
    assert any("bounded regular file" in error for error in result["errors"])


def test_verify_cli_is_read_only_and_does_not_execute(bundle, monkeypatch, capsys):
    directory, report = bundle
    before = {p.name: p.read_bytes() for p in directory.iterdir()}

    def unexpected_demo(*args, **kwargs):
        pytest.fail("--verify must not run the task")

    monkeypatch.setattr(demo, "run_demo", unexpected_demo)
    assert (
        demo.main(
            ["--verify", str(directory), "--expected-digest", report["export"]["manifest_sha256"]]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["valid"] is True
    assert before == {p.name: p.read_bytes() for p in directory.iterdir()}


def test_invalid_verify_cli_returns_nonzero_and_json(tmp_path, capsys):
    assert demo.main(["--verify", str(tmp_path)]) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_export_cli_returns_visible_error_without_overwriting(tmp_path, capsys):
    assert demo.main(["--export", str(tmp_path)]) == 2
    assert "already exists" in capsys.readouterr().err


@pytest.mark.parametrize(
    "args",
    [["--expected-digest", "0" * 64], ["--verify", ".", "--expected-digest", "not-a-digest"]],
)
def test_inapplicable_or_malformed_digest_is_a_usage_error(args):
    with pytest.raises(SystemExit) as error:
        demo.main(args)
    assert error.value.code == 2


RECORDS = ("risk_downgrade", "action_substitution", "valid_execution", "replay")


def _edit_report(directory: Path, change) -> None:
    path = directory / "run-report.json"
    report = json.loads(path.read_text())
    change(report)
    # Witness digests are public hashes, so a rewriter recomputes them too.
    for key in RECORDS:
        report[key]["witness_digest"] = demo._recorded_witness_digest(report[key])
    path.write_bytes(demo._json_bytes(report))
    _reseal_manifest(directory)


def test_rewitnessed_unchanged_report_still_verifies(bundle):
    directory, _ = bundle
    _edit_report(directory, lambda report: None)
    assert demo.verify_bundle(directory)["status"] == "SELF_CONSISTENT"


@pytest.mark.parametrize(
    "key,value",
    [
        ("limits", []),
        ("mode", "PRODUCTION_ATTESTED"),
        ("bound_risk", "LOW"),
        ("authenticated_human_approval", True),
        ("critical_hash_unchanged_by_risk_downgrade", False),
        ("temporary_workspace_removed_on_exit", False),
    ],
    ids=["limits_dropped", "mode_upgraded", "risk_contradicts_permit", "extra_claim",
         "risk_flag_contradicts_control", "workspace_kept"],
)
def test_resealed_report_cannot_claim_more_than_the_run(bundle, key, value):
    directory, _ = bundle
    _edit_report(directory, lambda report: report.__setitem__(key, value))
    assert demo.verify_bundle(directory)["valid"] is False


def _phantom_agent(report):
    for key in RECORDS:
        report[key]["consensus_summary"]["healthy_agents"].append("phantom-agent")


@pytest.mark.parametrize(
    "change",
    [
        lambda report: report["replay"]["permit"].__setitem__("permit_digest", "0" * 64),
        lambda report: report["risk_downgrade"].__setitem__("live_action_hash", "0" * 64),
        lambda report: report["action_substitution"].__setitem__(
            "live_action_hash", report["valid_execution"]["live_action_hash"]
        ),
        lambda report: report["replay"].__setitem__(
            "evaluated_at", report["valid_execution"]["evaluated_at"] - 1
        ),
        lambda report: report["risk_downgrade"]["compaction_summary"].__setitem__("risk", "HIGH"),
        lambda report: report["risk_downgrade"].__setitem__(
            "evaluated_at", report["risk_downgrade"]["permit"]["issued_at"] - 1
        ),
        _phantom_agent,
    ],
    ids=["replay_names_another_permit", "downgrade_names_another_action",
         "substitution_names_the_permitted_action", "replay_before_success",
         "downgrade_without_a_risk_change", "control_before_the_permit",
         "phantom_consensus_agent"],
)
def test_resealed_control_records_must_belong_to_this_run(bundle, change):
    directory, _ = bundle
    _edit_report(directory, change)
    assert demo.verify_bundle(directory)["valid"] is False


@pytest.mark.parametrize(
    "field,value",
    [("evidence_notes", "Externally attested by an independent auditor"),
     ("summary", "Verified in production")],
)
def test_resealed_completion_cannot_claim_outside_attestation(bundle, field, value):
    directory, _ = bundle
    path = directory / "completed-task.json"
    completed = json.loads(path.read_text())
    completed["result"][field] = value
    path.write_bytes(demo._json_bytes(completed))
    _reseal_manifest(directory)
    assert demo.verify_bundle(directory)["valid"] is False


def test_overflowing_number_is_not_read_as_infinity():
    with pytest.raises(ValueError, match="nonfinite"):
        demo._read_json(b"[1e400]")


def test_deeply_nested_json_is_an_invalid_bundle_not_a_crash(bundle):
    directory, _ = bundle
    (directory / "action.json").write_bytes(b"[" * 200_000 + b"]" * 200_000)
    _reseal_manifest(directory)
    assert demo.verify_bundle(directory)["valid"] is False


def test_evidence_swapped_for_a_fifo_after_the_type_check_is_not_read(bundle, monkeypatch):
    directory, _ = bundle
    fifo = directory / "handoff.txt"
    fifo.unlink()
    os.mkfifo(fifo)
    original_is_file, original_read = Path.is_file, Path.read_bytes

    # The earlier look saw a regular file; the FIFO arrived before the read.
    monkeypatch.setattr(Path, "is_file", lambda self: self == fifo or original_is_file(self))

    def guarded_read(self):
        if self == fifo:
            pytest.fail("a FIFO must be refused from the opened descriptor, not read")
        return original_read(self)

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    result = demo.verify_bundle(directory)
    assert result["valid"] is False
    assert "handoff.txt must be a bounded regular file" in result["errors"]
