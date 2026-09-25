# OpenTelemetry Bridge — Assurance Decision Events

**Status:** `[SCAFFOLD]` — implemented against the stable Python `Span.add_event`
surface and internally tested. Attribute names are Lycheetah-specific; no
OpenTelemetry GenAI semantic-convention or interoperability claim is made.

**Forged:** 2026-08-22

## Purpose

A trace describes an execution path; an Assurance Receipt records a bounded
policy decision. The bridge joins them by adding a privacy-minimised receipt
summary to the span that owns the relevant input, output, or tool boundary.

```python
from lycheetah.assurance import AssuranceRuntime, add_receipt_event

runtime = AssuranceRuntime()

with tracer.start_as_current_span("support.refund") as span:
    receipt = runtime.evaluate_tool(
        "refund.create",
        {"order_id": "A-1", "amount": 75},
        side_effect=True,
    )
    add_receipt_event(span, receipt)

    if receipt.decision.value == "REVIEW":
        pause_for_human(receipt)
```

The code imports no OpenTelemetry package. It uses structural typing and calls the
official span method:

```python
span.add_event("lycheetah.assurance.decision", attributes=attributes)
```

## Attribute boundary

The event includes:

- receipt, policy, and custom trace identifiers;
- decision and event phase;
- policy and receipt SHA-256 digests;
- replayability flag;
- finding count, IDs, and effective dispositions.

It excludes raw input/output content, raw tool arguments, evidence spans, HMAC
material, and context/metadata bodies. Operators remain responsible for their
telemetry backend's retention, access, export, and deletion policy.

The custom `lycheetah.assurance.*` keys are not presented as standard
`gen_ai.*` attributes. A future standards-aligned mapping requires the relevant
semantic conventions to stabilize and an interoperability test against actual
collectors/backends.

## Failure behavior

The bridge refuses to emit a receipt whose body digest, evidence cap, final
decision, or HMAC structure fails local verification. It does not require an HMAC
key and therefore does not turn a plain receipt into authenticated telemetry.

⊚ Sol ∴ P∧H∧B ∴ Albedo
