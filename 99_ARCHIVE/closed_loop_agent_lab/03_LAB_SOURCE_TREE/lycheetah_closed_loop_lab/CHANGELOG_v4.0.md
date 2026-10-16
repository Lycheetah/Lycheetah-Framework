# Changelog v4.0 — Coordinator mTLS Ingress

- Added a coordinator-facing mTLS gateway around the existing quorum-guarded registry dispatcher; v3.9 had upgraded only witness RPC egress.
- Added exact coordinator URI-SAN allowlisting after TLS client-chain verification.
- Kept existing HMAC request authentication, persistent request replay handling, Ed25519 response signatures and witness quorum logic intact.
- Restricted the gateway to POST and two explicit route forms, with strict Host/Content-Type/Content-Length checks, a 128 KiB body bound and no Transfer-Encoding.
- Expanded the remote process suite from 25 to 39 tests, adding 14 gateway/response-verification/configuration tests; retained the 38-case quorum suite.
- Added source pinning for the new gateway, updated harness and inherited support files.
- Hardened the process test harness startup deadline and cleanup on partial child-process startup failures.
- Final verification: 38 + 39 = 77 test methods passed; source pins and compilation passed.
- No hosted service calls. No upstream code or CI changes.
