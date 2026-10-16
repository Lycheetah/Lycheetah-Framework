# Changelog v4.7 — Absolute HTTP Socket Deadline

- Added an absolute wall-clock socket watchdog to the HTTP exchange after TLS; it covers slow request-line/header/body reads and also closes the transport if the deadline passes during dispatch/response.
- Default `request_deadline_seconds` is 1.5× the configured per-I/O request timeout; coordinator and shared-ingress quota TTLs must exceed the relevant deadline budget.
- Added paired v4.6/v4.7 header slow-drip probe, plus HTTP header/body tests which verify no registry mutation.
- Preserved a partial TLS-record control and removed the unsupported claim that v4.7 improves the existing OpenSSL handshake timeout.
- Documented that socket closure does not cancel in-progress application/quorum work or make remote side effects atomic.
