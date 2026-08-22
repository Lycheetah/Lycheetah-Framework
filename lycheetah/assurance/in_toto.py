"""Lossless Assurance Receipt export into an in-toto Statement v1 shape."""

from __future__ import annotations

from typing import Any

from .receipt import AssuranceReceipt


STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = (
    "https://github.com/Lycheetah/Lycheetah-Framework/blob/master/"
    "34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md"
)


def to_in_toto_statement(receipt: AssuranceReceipt) -> dict[str, Any]:
    """Return a Statement, not a signed/authenticated envelope."""

    subject = receipt.event.get("subject", {})
    name = str(subject.get("name", "unknown"))
    digest = str(subject.get("sha256", ""))
    return {
        "_type": STATEMENT_TYPE,
        "subject": [{"name": name, "digest": {"sha256": digest}}],
        "predicateType": PREDICATE_TYPE,
        "predicate": {"receipt": receipt.to_dict()},
    }
