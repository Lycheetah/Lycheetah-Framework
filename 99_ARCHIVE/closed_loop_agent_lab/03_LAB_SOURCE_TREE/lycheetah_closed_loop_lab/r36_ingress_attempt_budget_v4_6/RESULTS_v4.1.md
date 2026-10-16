# Verification Results v4.1 — Bounded mTLS Ingress

## Final run

- Source pin: **PASS**, 8 source/reference file fingerprints.
- Python compilation: **PASS** (`python -m py_compile *.py`).
- Retained registry/quorum suite: **PASS**, 38 tests in ~7 seconds.
- mTLS witness + coordinator gateway suite: **PASS**, 44 tests in ~29 seconds.
- Combined unique test methods across separate invocations: **82 passed**.
- Hosted services called: **No**.
- Upstream repository changed: **No**.
- Archive CRC checks: **PASS** for standalone and complete archive.

## v4.1-specific coverage

The 44-test gateway/witness suite includes the inherited TLS client/server identity, HMAC, response signature, request framing, replay prevention, four-process witness quorum and restart coverage, plus these v4.1 cases:

1. Excess connection closed before TLS handshake when global concurrency is full.
2. Per-direct-IP active connection limit enforced while global capacity remains.
3. Global process-local new-connection token bucket rejects a new connection before TLS handshake after its burst is consumed.
4. A 24-client incomplete-header burst stays within a configured four-active-connection ceiling and does not mutate registry state.
5. Invalid resource configuration is rejected, including Boolean-valued integer limits, zero/negative values, NaN timeout, and a per-IP limit greater than global concurrency.

## Runtime observation

The stress fixture creates 24 concurrent local clients, with a 4-slot server cap. It records active-connection snapshots while peers hold partial HTTP headers. The observed maximum never exceeded the configured ceiling; excess peers were closed and no registry checkpoint/challenge mutation occurred from the incomplete requests.

## Harness note

An earlier invocation reached the inherited witness restart/oversized-body phase and hit the command deadline without an assertion traceback. Each implicated test passed in isolation and the subsequent full 44-test gateway invocation completed cleanly in ~29 seconds. We retain that transient run as a harness timeout rather than a passing test; the final verification result is based on the completed clean run.

## Boundary / residual risks

- The global token bucket is local to one process and does not ensure fairness; one source may exhaust it.
- Per-IP concurrent limits do not solve distributed-source flooding or authenticated identity-level quotas.
- No independent hosts or administrative trust domains, production CA revocation/rotation, OS resource caps, proxy controls or live deployment was tested.
- This is a local executable reference composition, not formal verification or production certification.
- The actual upstream Lycheetah repository and its CI were not changed or run.
