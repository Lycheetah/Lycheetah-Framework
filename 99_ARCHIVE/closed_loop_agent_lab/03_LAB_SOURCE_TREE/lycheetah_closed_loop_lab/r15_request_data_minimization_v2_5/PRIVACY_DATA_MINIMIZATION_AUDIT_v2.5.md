# Privacy and Local-Ledger Data Minimisation Audit — v2.5

**Date:** 2026-10-17  
**Scope:** local reference adapter derived from the v2.4 Stripe Refund test-mode contract harness  
**Status:** local reference change and test suite passed; not upstream-integrated or production-certified

## Finding

The v2.4 adapter already reduced provider responses to an allow-list before storage, omitting fields such as PaymentIntent `client_secret`, arbitrary provider metadata, and provider error messages. However, its durable intent log retained the exact outbound request body. The builder accepted caller-supplied Stripe metadata, which meant custom values could be copied into the payload JSON stored in SQLite. Since arbitrary metadata is not required to recover or correlate this operation—the adapter's internal `lycheetah_operation_id` is sufficient for this reference contract—this was unnecessary retention at the sensitive operation boundary.

Stripe's metadata documentation warns against storing sensitive information in metadata and describes metadata as structured key-value data rather than an authorization mechanism. See the official references in `SOURCE_LOG_v2.5.md`.

## Change

- `build_payload()` now permits only the adapter's internal operation-correlation metadata. Any non-empty caller-supplied metadata is rejected before the durable record is created or any HTTP call can occur.
- Non-object metadata is rejected explicitly.
- Tests prove that attempted email, token-like and free-text metadata values create no operation row, issue no provider POST, and do not appear in the SQLite database.
- Existing success-path tests prove the outbound and stored payload carry only `lycheetah_operation_id` in metadata.
- The SQLite database is opened/created as a regular filesystem file, not the connection-local `:memory:` database. Existing DB permissions are restricted to owner read/write on POSIX (`0600`); symlink paths are refused. The database remains integrity-authenticated with an externally supplied HMAC key.

## Why not encrypt in this pass?

This adapter is deliberately standard-library-only. It does not attempt to implement encryption itself. HMAC authenticates integrity; it does not conceal contents. The remaining operational identifiers (target Charge/PaymentIntent ID, amount, idempotency key, timestamps and state) remain in the local SQLite ledger because they're needed to recover the exact operation. On a host with a stronger threat model, use an encrypted volume or a reviewed authenticated-encryption layer with key management separate from the database, and consider a separate service account for the broker.

## Compatibility

The adapter has a deliberately narrower request contract than Stripe's full API: caller metadata is unsupported; business metadata must be managed in the business system and must not be silently copied into this recovery ledger. Only the internal opaque operation ID is sent to Stripe as metadata for reconciliation. Existing callers that relied on arbitrary metadata must migrate explicitly rather than silently losing values.

## Threat boundary

This change helps reduce accidental local persistence and limits who can read the SQLite file on POSIX. It does not protect against process compromise, OS administrator access, theft of the HMAC key, logs or backups copied elsewhere, or PII encoded into the caller's `operation_id`. Operation IDs must be opaque, stable, non-PII identifiers.
