# Pack Manifest v4.0

## Current iteration

Coordinator-facing registry mTLS gateway added to the local remote witness quorum harness. See `r30_mtls_registry_gateway_v4_0/`.

## Verification

- 38 retained registry/quorum tests passed.
- 39 remote-witness + mTLS gateway tests passed.
- 77 unique test methods passed across two isolated invocations.
- 8 source fingerprints passed, Python compilation passed.
- No hosted endpoint called; no upstream source changed.

## Archives

- `lycheetah_mtls_registry_gateway_v4.0.zip`: standalone server/test harness and inherited local modules.
- `lycheetah_closed_loop_agent_lab_v4.0.zip`: full research history through v4.0.

## Boundary

The four witness services and coordinator registry run on a single test host. Production CA management, revocation, independent administrators/hosts, resource quotas, formal verification, a real deployment and upstream CI are not established.
