# Verification Results v4.0 — mTLS Registry Gateway

## Status

- Source-pin verification: **PASS** (8 files).
- Python compilation: **PASS** (`python -m py_compile *.py`).
- Retained registry/quorum suite: **PASS**, 38 tests in 10.960 seconds.
- Remote witness + coordinator mTLS gateway suite: **PASS**, 39 tests in 26.349 seconds.
- Combined unique test methods across both invocations: **77 passed**.
- Hosted services called: **No**.
- Upstream files modified: **No**.

## New v4.0 test coverage

The new gateway suite includes tests for:

1. Successful coordinator-authenticated mutation through the mTLS ingress and remote witness quorum.
2. Ed25519 response-signature validation and status/body/request-ID binding.
3. Missing client cert and trusted-CA certificate with an unauthorized coordinator URI SAN.
4. Server hostname mismatch and cleartext HTTP attempt.
5. Body modification after HMAC creation and wrong request HMAC.
6. Same-request replay returning the cached original result without a second checkpoint mutation.
7. Changed payload with an existing request ID rejected as conflict.
8. Non-POST method, duplicate Content-Length and oversized body rejected before registry dispatch.
9. Explicit non-loopback bind opt-in and wildcard/DNS/IPv6 bind rejection.
10. Existing witness restart, quorum outage, transport replay, timeouts, dropped response, and witness identity checks retained from v3.9.

The successful final logs are `source_pin_verify_v4.0.log`, `python_compile_v4.0.log`, `retained_quorum_test_v4.0.log`, and `mtls_registry_gateway_test_v4.0.log`.

## Negative findings and limits

- An earlier draft of the gateway integration had two tests fail because the existing dispatcher deliberately signs authentication failures with the generic request ID `invalid-request-id`. The tests and API contract now preserve that fail-closed behavior while still verifying the response signature; successful responses remain bound to the caller's request ID.
- A first full run hit a transient witness-readiness timeout during setup. The harness now tracks child PIDs immediately and allows 30 seconds for readiness. The final clean full run completed both suites.
- The gateway and four witness processes run on one host under one operator. This does not establish four independent trust domains.
- Local ephemeral test certificates do not validate production CA rotation, revocation, independent secret distribution or deployment topology.
- This is an executable reference/test composition, not a production service or formal verification result.
- The actual Lycheetah upstream repository was not modified and its CI was not run.
