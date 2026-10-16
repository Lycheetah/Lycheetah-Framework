# Verification Results v3.7

## Current focused suite

- `python verify_source_pins_v3.7.py` — **PASS**, all 3 pinned/inherited files matched the recorded SHA-256 values.
- `python -m py_compile *.py` — **PASS**.
- `python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum` — **38 test methods passed** in 10.363 seconds.
- `python demo_external_quorum_rollback_v3_7.py` — **PASS**; restoring the registry database and client-anchor database together while witness stores remain current is detected as `external-quorum-ahead-of-local-head`.

## Retained regression suite

The prior v3.6 suite was also run separately:

`python -W error::ResourceWarning -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier test_remote_monotonic_verifier test_registry_clock_monotonicity`

**82 test methods passed** in 14.350 seconds. Because the v3.6 code lives in a separate directory with its own modules, it was run as a separate invocation rather than combined into a single Python process.

Total passing methods across the current v3.7 and retained v3.6 suite invocations: **120**.

## New behavior exercised

- Fresh 3-of-4 signed checkpoint quorum matches the actual protected SQLite registry state.
- Restoring only the registry store, or both registry and client-anchor stores, while the quorum remains current is detected.
- Coordinated restoration of every witness store remains an explicit **negative control**: the reference model cannot know that all supposed external witnesses were rolled back too.
- Direct SQL mutation without a matching checkpoint fails closed at preflight.
- Split 2/2 witness heads cannot establish quorum; partial 2-of-4 publication returns 503 and can recover the same pending checkpoint.
- Authenticated replays return cached results without re-executing the mutation; changing a payload with the same request ID is rejected.
- Loss of response after commit never returns success; result is anchored as outcome-unknown and requires reconciliation.
- Guarded loopback HTTP path serializes 8 concurrent mutation requests; every mutation gets a checkpoint.
- Response-cache, pending intent, local head, witness head and schema tampering are rejected.
- HTTP facade refuses non-loopback binding.

## Security boundary and limitations

The tests execute a local reference model. Four witness objects use distinct SQLite files and keys, but are not independent remote services, hosts, administrators or backup domains. Coordinated rollback of registry, client anchor and all witness stores is expected to defeat this setup and is captured as a negative control.

The wrapper is POSIX-specific (`fcntl.flock`) and has no production TLS/authentication deployment, remote witness process, independently administered key management, backup policy, rate limiter, or operational recovery service. The upstream package suite and CI have not been run. No hosted service was contacted and no upstream source was changed.
