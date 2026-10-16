# Threat Model v3.8 — Process-Separated Witness Quorum

## Security question

Does moving witness operations out of the coordinator's Python process change the evidence available to the checkpoint quorum, and what fails across a real transport boundary?

## Implemented controls

- Four independent subprocesses, each with a unique Ed25519 witness key and SQLite vote ledger file.
- Coordinator uses an HTTP client adapter rather than direct witness object calls.
- Loopback-only numeric binding and client configuration; redirects disabled.
- HMAC request authentication binds method, path, timestamp, unique request ID, and exact body digest.
- Timestamp freshness and durable replay-ID rejection.
- Witness-signed report/vote validation remains the source of quorum identity.
- Exact route/body allowlist, 1 MiB body limit, generic server errors.
- Restart tests exercise retained checkpoint/vote state from disk.
- One witness outage is tolerated by the configured 3-of-4 quorum; two unavailable witnesses fail closed.
- A witness can commit a vote then drop the HTTP response; coordinator still completes if the remaining/current signed quorum is valid.

## Adversary scenarios tested

- Wrong API secret or tampered body.
- Duplicate transport request ID.
- Stale/invalid witness challenge input.
- Oversized Content-Length before body transfer.
- Unknown route.
- Process stop/restart preserving durable witness head.
- One or two witness process outages.
- Lost vote response after witness commit.
- Attempt to replace absent witnesses with a duplicate/aliased roster identity.

## Not established

- Four witness processes are not four independent machines, administrators, backup systems, or key-management domains.
- Test config files hold keys locally; root/process-memory access can compromise them.
- HTTP/HMAC over loopback is not production TLS or mTLS.
- All local witness DBs, configs, client state, and registry DB can still be restored together by a sufficiently privileged same-host operator; no external system can detect that coordinated restoration here.
- No Byzantine-fault proof, formal verification, upstream CI, or actual external service deployment is claimed.
- POSIX `fcntl.flock` remains in inherited registry wrapper; Windows portability is not established.

## Operational rule

Treat this package as an executable transport-composition prototype. Use a real remote witness deployment only after TLS/mTLS, independently administered persistence and keys, backup/restore controls, monitoring, rate limits, incident recovery, and an external adversarial review are complete.
