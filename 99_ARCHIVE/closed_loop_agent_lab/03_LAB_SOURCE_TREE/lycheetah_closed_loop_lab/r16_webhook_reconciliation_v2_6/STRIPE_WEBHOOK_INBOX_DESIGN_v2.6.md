# R16 design — authenticated webhook inbox and recovery signal

## Core rule

A webhook is an authenticated *signal*, not terminal proof that the action completed. A matching event returns `RETRIEVE_CURRENT_PROVIDER_STATE`; an authenticated API retrieval then determines the current state under the refund adapter's existing checks.

## Ingestion path

1. Bound the raw body and signature-header sizes before parsing.
2. Verify Stripe's `t`/`v1` signature over `timestamp + "." + raw body` with a configured endpoint secret. Verify the timestamp against a freshness tolerance. Support multiple labeled secrets during an explicitly managed rotation window.
3. Parse UTF-8 JSON only after signature validation. Reject duplicate JSON keys and nonstandard numeric constants to avoid parser differential ambiguity.
4. Enforce allow-listed snapshot event types (`refund.created`, `refund.updated`, `refund.failed`), event/refund identifiers, explicit test mode, configured Connect/platform scope, and basic refund field types.
5. Derive a minimal summary: event id/type/created, account scope, refund id, charge/PaymentIntent IDs, amount/currency/status, Lycheetah operation ID, payload digest, signature timestamp, safe secret label, receive time.
6. Do not persist raw body, arbitrary metadata, previous attributes, descriptions, receipt URLs, customer data or unknown provider fields.
7. Insert under a SQLite write transaction keyed on event ID. An identical duplicate is acknowledged as duplicate; the same event ID with a different payload digest is rejected. The local summary row is HMAC authenticated.
8. On lookup, verify the row HMAC and confirm that the row account scope equals the inbox's configured account scope before using it as a reconciliation hint.
9. Require current provider retrieval to confirm current refund state. Event `created` order and delivery order are not used to decide terminal success.

## Threats and mitigations

| Threat | Mitigation | Residual limit |
|---|---|---|
| Forged signature | HMAC-SHA256 verify with endpoint secret; `compare_digest` | Endpoint secret compromise defeats this boundary |
| Body changed after signing | Signature binds exact raw bytes; no JSON reserialization before verification | Reverse proxy/framework must preserve raw body |
| Old captured delivery replay | Signature timestamp tolerance + unique event ID inbox key | Duplicate event delivered with a fresh signature is still an event-ID duplicate; persistent event store/retention required |
| Duplicate concurrent delivery | `BEGIN IMMEDIATE` + primary key + content digest comparison | SQLite is single-host reference storage, not a distributed inbox |
| Event-ID payload conflict | Reject conflicting second payload; retain original record | Requires alert/manual review |
| Connected-account confusion | Verify configured `event.account` during ingest and again when routing old rows | Production must configure one database/tenant scope consistently |
| Event ordering confusion | Never decide success from webhook status; request current object through authenticated provider API | Provider retrieval and local policy still are not one distributed transaction |
| PII/secret retention | Do not store raw body; pick fields explicitly | Minimal identifiers and amounts still require retention/access policy |
| Local database tampering | HMAC-authenticated row checked on reads | No protection if attacker can obtain/execute with HMAC key; no confidentiality |
| Huge body / parser exhaustion | 1 MiB raw body cap; 16 KiB signature cap; loopback receiver checks Content-Length | Production edge must enforce limits before buffering body |

## Deliberate scope limits

This is a narrow snapshot-event contract, not an implementation for all Stripe event types, thin notifications, EventBridge/Event Grid envelopes, API event-version migration, or a distributed job queue. It is not a replacement for Stripe's official SDK. The test receiver accepts only bounded Content-Length framing, runs on loopback, and is not suitable as an exposed production server.
