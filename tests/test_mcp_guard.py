import asyncio
import json

import pytest


pytest.importorskip("mcp")
pytestmark = pytest.mark.scaffold


from lycheetah.applications.lycheetah_guard_mcp import (  # noqa: E402
    build_server,
    tool_assure_tool,
    tool_verify_assurance_receipt,
)


EXPECTED_TOOLS = {
    "check_alignment",
    "check_invariants",
    "suggest_correction",
    "run_seven_phase",
    "check_network_health",
    "configure_guard",
    "sol_assess",
    "assure_text",
    "assure_tool",
    "verify_assurance_receipt",
}


def run(coroutine):
    return asyncio.run(coroutine)


def test_mcp_v2_server_registers_ten_typed_tools():
    tools = run(build_server().list_tools())
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    assure_tool = next(tool for tool in tools if tool.name == "assure_tool")
    properties = assure_tool.input_schema["properties"]
    assert "tool_name" in assure_tool.input_schema["required"]
    assert "hmac_secret" not in properties
    assert "hmac_key" not in properties
    assert "human_approved" not in properties


def test_mcp_call_returns_structured_review_receipt():
    result = run(
        build_server().call_tool(
            "assure_tool",
            {
                "tool_name": "refund.create",
                "arguments": {"order_id": "A-1"},
                "side_effect": True,
            },
        )
    )
    assert result.is_error is False
    assert result.structured_content["decision"] == "REVIEW"
    assert result.structured_content["event"]["replayable"] is False


def test_mcp_receipt_verifier_detects_mutation():
    receipt = tool_assure_tool("order.read", {"order_id": "A-1"})
    valid = tool_verify_assurance_receipt(json.dumps(receipt))
    assert valid["valid"] is True

    receipt["event"]["tool_name"] = "shell_exec"
    invalid = tool_verify_assurance_receipt(json.dumps(receipt))
    assert invalid["valid"] is False
    assert "digest mismatch" in " ".join(invalid["errors"])


def test_mcp_side_effect_receipt_does_not_capture_raw_arguments():
    marker = "MCP-PRIVATE-ff942f"
    receipt = tool_assure_tool(
        "refund.create",
        {"customer_note": marker},
        side_effect=True,
    )
    assert marker not in json.dumps(receipt)


def test_mcp_server_rejects_incomplete_hmac_environment(monkeypatch):
    monkeypatch.setenv("LYCHEETAH_RECEIPT_HMAC_SECRET", "secret")
    monkeypatch.delenv("LYCHEETAH_RECEIPT_HMAC_KEY_ID", raising=False)
    with pytest.raises(RuntimeError):
        build_server()
