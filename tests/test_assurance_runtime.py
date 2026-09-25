import json

from lycheetah.assurance import (
    AssuranceEvent,
    AssurancePolicy,
    AssuranceRuntime,
    Disposition,
    Phase,
)


def test_grounded_text_can_be_allowed_with_context_markers_visible():
    runtime = AssuranceRuntime()
    receipt = runtime.evaluate_text(
        "I may be wrong. Please verify this with an independent source before deciding."
    )
    assert receipt.decision == Disposition.ALLOW
    assert receipt.verify().valid
    assert any(item.finding_id == "LYC:AURA:CONTEXT_REQUIRED" for item in receipt.findings)


def test_manipulative_text_routes_to_review():
    receipt = AssuranceRuntime().evaluate_text(
        "I absolutely guarantee this. Do not ask anyone to verify it."
    )
    assert receipt.decision == Disposition.REVIEW
    assert any(item.finding_id == "LYC:TEXT:MANIPULATION_CUES" for item in receipt.findings)


def test_empty_text_routes_to_review():
    receipt = AssuranceRuntime().evaluate_text("  ")
    assert receipt.decision == Disposition.REVIEW
    assert receipt.findings[0].deterministic is True


def test_oversized_text_routes_to_review_without_heuristic_analysis():
    policy = AssurancePolicy(policy_id="test.size", max_text_characters=16)
    receipt = AssuranceRuntime(policy).evaluate_text("x" * 17)
    assert receipt.decision == Disposition.REVIEW
    assert receipt.metrics["text"]["analysis_skipped"] is True
    assert receipt.findings[0].finding_id == "LYC:TEXT:SIZE_LIMIT"


def test_default_text_receipt_does_not_capture_raw_content():
    marker = "PRIVATE-MARKER-6a9169a4"
    receipt = AssuranceRuntime().evaluate_text(f"Please verify {marker} independently.")
    assert marker not in receipt.to_json()
    assert receipt.event["replayable"] is False


def test_content_capture_is_explicit_and_replayable():
    marker = "CAPTURED-MARKER-52c721"
    policy = AssurancePolicy(policy_id="test.capture", capture_content=True)
    receipt = AssuranceRuntime(policy).evaluate_text(marker)
    assert receipt.event["content"] == marker
    assert receipt.event["replayable"] is True


def test_side_effect_without_approval_routes_to_review():
    receipt = AssuranceRuntime().evaluate_tool(
        "cancel_order", {"order_id": 123}, side_effect=True
    )
    assert receipt.decision == Disposition.REVIEW
    assert any(item.finding_id == "LYC:TOOL:APPROVAL_REQUIRED" for item in receipt.findings)


def test_approved_side_effect_can_be_allowed():
    receipt = AssuranceRuntime().evaluate_tool(
        "cancel_order", {"order_id": 123}, side_effect=True, human_approved=True
    )
    assert receipt.decision == Disposition.ALLOW


def test_denied_tool_fails_closed():
    policy = AssurancePolicy(policy_id="test.tools", denied_tools=("shell*",))
    receipt = AssuranceRuntime(policy).evaluate_tool("shell_exec", {"cmd": "date"})
    assert receipt.decision == Disposition.BLOCK
    assert any(item.finding_id == "LYC:TOOL:DENIED" for item in receipt.findings)


def test_default_policy_blocks_common_shell_boundary():
    receipt = AssuranceRuntime().evaluate_tool("shell_exec", {"cmd": "date"})
    assert receipt.decision == Disposition.BLOCK
    assert any(item.finding_id == "LYC:TOOL:DENIED" for item in receipt.findings)


def test_blocked_scope_fails_closed():
    policy = AssurancePolicy(policy_id="test.tools", blocked_scopes=("production.*",))
    receipt = AssuranceRuntime(policy).evaluate_tool(
        "write_record", {}, scopes=("production.write",)
    )
    assert receipt.decision == Disposition.BLOCK


def test_missing_tool_name_fails_closed():
    event = AssuranceEvent(phase=Phase.TOOL, tool_name="")
    receipt = AssuranceRuntime().evaluate(event)
    assert receipt.decision == Disposition.BLOCK


def test_tool_allowlist_gap_fails_closed():
    policy = AssurancePolicy(policy_id="test.tools", tool_allowlist=("read_*",))
    receipt = AssuranceRuntime(policy).evaluate_tool("write_record", {})
    assert receipt.decision == Disposition.BLOCK


def test_explicit_human_rejection_blocks_action():
    receipt = AssuranceRuntime().evaluate_tool(
        "cancel_order", {"order_id": 123}, human_approved=False
    )
    assert receipt.decision == Disposition.BLOCK
    assert any(item.finding_id == "LYC:TOOL:HUMAN_DENIED" for item in receipt.findings)


def test_sensitive_argument_value_is_not_stored_by_default():
    marker = "tok_live_PRIVATE_7d965b"
    receipt = AssuranceRuntime().evaluate_tool(
        "call_api", {"api_token": marker, "query": "status"}
    )
    assert receipt.decision == Disposition.REVIEW
    assert marker not in receipt.to_json()
    assert receipt.event["replayable"] is False


def test_captured_sensitive_argument_is_redacted_and_not_replayable():
    marker = "tok_live_PRIVATE_991"
    policy = AssurancePolicy(policy_id="test.capture", capture_arguments=True)
    receipt = AssuranceRuntime(policy).evaluate_tool(
        "call_api", {"api_token": marker, "query": "status"}
    )
    assert receipt.event["arguments"]["api_token"] == "[REDACTED]"
    assert marker not in receipt.to_json()
    assert receipt.event["replayable"] is False


def test_captured_nonsensitive_arguments_are_replayable():
    policy = AssurancePolicy(policy_id="test.capture", capture_arguments=True)
    receipt = AssuranceRuntime(policy).evaluate_tool(
        "lookup_order", {"order_id": 42}
    )
    assert receipt.event["arguments"] == {"order_id": 42}
    assert receipt.event["replayable"] is True


def test_receipt_contains_policy_digest_and_no_claim_of_certification():
    policy = AssurancePolicy(policy_id="test.identity", version="3")
    receipt = AssuranceRuntime(policy).evaluate_tool("lookup", {})
    assert receipt.policy["sha256"] == policy.digest
    assert any("not a safety" in limitation for limitation in receipt.limitations)
    assert json.loads(receipt.to_json())["runtime"]["status"] == "SCAFFOLD"
