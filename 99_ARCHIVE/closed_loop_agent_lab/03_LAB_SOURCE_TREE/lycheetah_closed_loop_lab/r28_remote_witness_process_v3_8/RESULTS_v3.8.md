# Verification Results v3.8 — Remote Witness Process Boundary

## Verified

- `python verify_source_pins_v3.8.py` — **PASS**, 4 inherited/local reference files matched their pinned fingerprints.
- `python -m py_compile *.py` — **PASS**.
- `python -u -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum` — **38 test methods passed** in 6.137 seconds.
- `python -u -W error::ResourceWarning -m unittest -v test_remote_witness_process` — **17 test methods passed** in 19.454 seconds.
- Total across separate test processes: **55 passing test methods**.
- Standalone archive was extracted into a fresh directory; source-pin verification, Python compilation, and all 17 remote-process tests passed from the extracted copy.
- Both archives passed `unzip -t`.
- No hosted services were contacted; no upstream source was changed.

## Remote process boundary exercised

Four witness services were started as four distinct OS processes, each with its own SQLite witness ledger and Ed25519 key. The coordinator exercised its existing bootstrap/current-head/attestation path through authenticated HTTP clients. Tests covered witness restarts, persistent head recovery, dropped attestation response after vote commit, one-witness outage tolerance, two-witness outage fail-closed behavior, HTTP HMAC body binding, duplicate RPC request IDs, noncanonical request-target rejection, oversized Content-Length rejection, malformed input, unknown route, and repeated signed reports being counted only once.

## Important reproducibility note

The two suites are intentionally invoked in separate Python processes. A combined same-interpreter run was attempted during development and appeared to hang during the subprocess lifecycle tests; the root cause was not established. The authoritative results are the two clean separate invocations above, matching the separate-invocation convention used in the previous research pack.

## Security boundary

This is a same-host reference prototype. Separate OS processes and HTTP RPC demonstrate an actual process/network boundary, but not independent hosts or administrative domains. Each service loads keys from a local configuration file; transport is HTTP bound to numeric loopback, not production TLS/mTLS. A root-level attacker could access all local stores and key files. Coordinated restoration of the primary registry, anchor, all witness databases, replay ledgers and key configs remains outside the protection provided here.

The upstream package tests/CI were not run as this is a local additive reference pack. The inherited wrapper is POSIX-specific (`fcntl.flock`). No cryptographic proof, formal verification, or production security certification is claimed.
