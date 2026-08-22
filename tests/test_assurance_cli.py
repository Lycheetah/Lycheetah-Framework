import json

from lycheetah.assurance.cli import main


GROUNDED = "I may be wrong. Please verify this with an independent source before deciding."


def test_check_json_emits_receipt(capsys):
    code = main(["check", GROUNDED, "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["decision"] == "ALLOW"
    assert payload["integrity"]["digest"]


def test_tool_side_effect_returns_review_exit_code(capsys):
    code = main(
        [
            "tool",
            "cancel_order",
            "--arguments",
            '{"order_id": 12}',
            "--side-effect",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["decision"] == "REVIEW"


def test_approved_tool_can_return_allow(capsys):
    code = main(
        [
            "tool",
            "cancel_order",
            "--arguments",
            '{"order_id": 12}',
            "--side-effect",
            "--approved",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["decision"] == "ALLOW"


def test_explicitly_denied_tool_returns_block(capsys):
    code = main(["tool", "order.read", "--denied", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 3
    assert payload["decision"] == "BLOCK"


def test_policy_file_can_block_tool(tmp_path, capsys):
    policy = {
        "id": "customer-support.production",
        "version": "1",
        "tools": {"denied": ["shell*"]},
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    code = main(
        [
            "tool",
            "shell_exec",
            "--arguments",
            '{"cmd": "date"}',
            "--policy",
            str(policy_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 3
    assert payload["decision"] == "BLOCK"


def test_receipt_file_then_verify(tmp_path, capsys):
    receipt_path = tmp_path / "receipt.json"
    assert main(["check", GROUNDED, "--receipt-file", str(receipt_path)]) == 0
    capsys.readouterr()
    assert main(["verify", str(receipt_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True


def test_jsonl_log_chains_across_cli_calls(tmp_path, capsys):
    log_path = tmp_path / "receipts.jsonl"
    assert main(["check", GROUNDED, "--log", str(log_path)]) == 0
    capsys.readouterr()
    assert main(["check", GROUNDED + " Again.", "--log", str(log_path)]) == 0
    capsys.readouterr()
    assert main(["verify", str(log_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert payload["receipt_count"] == 2


def test_jsonl_authentication_requires_key_id(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("LYCHEETAH_TEST_HMAC", "secret")
    log_path = tmp_path / "receipts.jsonl"
    assert main(["check", GROUNDED, "--log", str(log_path)]) == 0
    capsys.readouterr()
    code = main(
        [
            "verify",
            str(log_path),
            "--hmac-key-env",
            "LYCHEETAH_TEST_HMAC",
            "--json",
        ]
    )
    assert code == 4
    assert "--key-id is required" in capsys.readouterr().err


def test_jsonl_wrong_hmac_key_is_invalid(tmp_path, capsys, monkeypatch):
    log_path = tmp_path / "sealed.jsonl"
    monkeypatch.setenv("LYCHEETAH_TEST_HMAC", "correct")
    assert (
        main(
            [
                "check",
                GROUNDED,
                "--log",
                str(log_path),
                "--hmac-key-env",
                "LYCHEETAH_TEST_HMAC",
                "--key-id",
                "key-1",
            ]
        )
        == 0
    )
    capsys.readouterr()
    monkeypatch.setenv("LYCHEETAH_TEST_HMAC", "wrong")
    assert (
        main(
            [
                "verify",
                str(log_path),
                "--hmac-key-env",
                "LYCHEETAH_TEST_HMAC",
                "--key-id",
                "key-1",
                "--json",
            ]
        )
        == 4
    )
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_hmac_key_is_read_from_environment(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("LYCHEETAH_TEST_HMAC", "not-for-production")
    receipt_path = tmp_path / "sealed.json"
    assert (
        main(
            [
                "check",
                GROUNDED,
                "--hmac-key-env",
                "LYCHEETAH_TEST_HMAC",
                "--key-id",
                "test-key",
                "--receipt-file",
                str(receipt_path),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert (
        main(
            [
                "verify",
                str(receipt_path),
                "--hmac-key-env",
                "LYCHEETAH_TEST_HMAC",
                "--json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["hmac_authenticated"] is True


def test_hmac_requires_key_id(capsys, monkeypatch):
    monkeypatch.setenv("LYCHEETAH_TEST_HMAC", "not-for-production")
    code = main(
        ["check", GROUNDED, "--hmac-key-env", "LYCHEETAH_TEST_HMAC"]
    )
    assert code == 4
    assert "--key-id is required" in capsys.readouterr().err


def test_in_toto_output(capsys):
    code = main(["check", GROUNDED, "--in-toto"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["_type"] == "https://in-toto.io/Statement/v1"


def test_default_policy_prints_digest(capsys):
    assert main(["default-policy"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["policy"]["id"] == "lycheetah.default"
    assert len(payload["sha256"]) == 64


def test_non_object_tool_arguments_fail(capsys):
    assert main(["tool", "demo", "--arguments", "[]"]) == 4
    assert "must decode to a JSON object" in capsys.readouterr().err


def test_eval_cli_passes_exact_example(capsys):
    code = main(
        [
            "eval",
            "examples/assurance/customer_support_eval.jsonl",
            "--policy",
            "examples/assurance/customer_support_policy.json",
            "--require-exact-match",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["summary"]["exact_match_rate"] == 1.0
    assert payload["gate"]["passed"] is True


def test_eval_cli_returns_five_when_gate_fails(tmp_path, capsys):
    corpus = tmp_path / "mismatch.jsonl"
    corpus.write_text(
        json.dumps(
            {
                "id": "case.harmful-allow",
                "expected": "BLOCK",
                "event": {"phase": "tool", "tool_name": "order.read"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    code = main(
        ["eval", str(corpus), "--max-harmful-allows", "0", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 5
    assert payload["summary"]["harmful_allow_count"] == 1
    assert payload["gate"]["passed"] is False


def test_eval_cli_writes_report_file(tmp_path, capsys):
    report = tmp_path / "report.json"
    assert (
        main(
            [
                "eval",
                "examples/assurance/customer_support_eval.jsonl",
                "--policy",
                "examples/assurance/customer_support_policy.json",
                "--report-file",
                str(report),
            ]
        )
        == 0
    )
    assert "gate: PASS" in capsys.readouterr().out
    assert json.loads(report.read_text(encoding="utf-8"))["integrity"]["digest"]

    assert main(["verify-eval", str(report), "--json"]) == 0
    verification = json.loads(capsys.readouterr().out)
    assert verification["valid"] is True


def test_verify_eval_cli_detects_mutation(tmp_path, capsys):
    report = tmp_path / "report.json"
    assert (
        main(
            [
                "eval",
                "examples/assurance/customer_support_eval.jsonl",
                "--policy",
                "examples/assurance/customer_support_policy.json",
                "--report-file",
                str(report),
            ]
        )
        == 0
    )
    capsys.readouterr()
    payload = json.loads(report.read_text(encoding="utf-8"))
    payload["summary"]["exact_match_count"] = 0
    report.write_text(json.dumps(payload), encoding="utf-8")
    assert main(["verify-eval", str(report), "--json"]) == 4
    assert json.loads(capsys.readouterr().out)["valid"] is False
