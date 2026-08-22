import pytest

from lycheetah.assurance import (
    AssuranceReceipt,
    AssuranceRuntime,
    OTEL_EVENT_NAME,
    ReceiptError,
    add_receipt_event,
    otel_event_attributes,
)


pytestmark = pytest.mark.scaffold


class FakeSpan:
    def __init__(self):
        self.events = []

    def add_event(self, name, attributes=None, timestamp=None):
        self.events.append((name, attributes, timestamp))


def test_otel_attributes_are_privacy_minimised():
    marker = "PRIVATE-OTEL-9de17"
    receipt = AssuranceRuntime().evaluate_tool(
        "refund.create", {"customer_note": marker}, side_effect=True
    )
    attributes = otel_event_attributes(receipt)
    assert attributes["lycheetah.assurance.decision"] == "REVIEW"
    assert attributes["lycheetah.assurance.receipt_id"] == receipt.receipt_id
    assert marker not in repr(attributes)
    assert not any("argument" in key or "content" in key for key in attributes)


def test_receipt_can_be_added_to_duck_typed_span():
    span = FakeSpan()
    receipt = AssuranceRuntime().evaluate_tool("order.read", {"id": 1})
    add_receipt_event(span, receipt)
    assert span.events[0][0] == OTEL_EVENT_NAME
    assert span.events[0][1]["lycheetah.assurance.integrity.sha256"] == receipt.digest
    assert span.events[0][2] is None


def test_invalid_receipt_is_not_exported():
    receipt = AssuranceRuntime().evaluate_tool("order.read", {"id": 1})
    data = receipt.to_dict()
    data["decision"] = "BLOCK"
    invalid = AssuranceReceipt.from_dict(data)
    with pytest.raises(ReceiptError):
        otel_event_attributes(invalid)


def test_non_span_is_rejected():
    receipt = AssuranceRuntime().evaluate_tool("order.read", {"id": 1})
    with pytest.raises(TypeError):
        add_receipt_event(object(), receipt)
