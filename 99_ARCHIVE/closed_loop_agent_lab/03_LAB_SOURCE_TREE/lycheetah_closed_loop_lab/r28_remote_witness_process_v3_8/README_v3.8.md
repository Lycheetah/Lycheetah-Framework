# Lycheetah Closed-Loop Agent Lab v3.8

## Purpose

Move the registry checkpoint quorum beyond in-process witness objects by exercising four witness service subprocesses over a guarded HTTP API.

## Contents

- `remote_witness_http.py` — loopback-only HTTP server and RPC client.
- `registry_checkpoint_quorum.py` — inherited v3.7 quorum coordinator.
- `spent_nonce_registry.py` — inherited local registry service harness.
- `remote_anchor_http.py`, `checkpoint_witness_quorum.py` — inherited, source-pinned helper modules.
- `test_remote_witness_process.py` — 17 transport/process-boundary tests.
- `test_registry_checkpoint_quorum.py` — 38 retained v3.7 tests.
- API contract, threat model, upstream integration plan, source pins and run logs.

## Run

```sh
./run_v3.8_tests.sh
```

The script intentionally executes the retained and remote-process test suites as separate Python invocations. See `RESULTS_v3.8.md` for exact totals and the recorded note on the combined-interpreter attempt.

## What this establishes

The coordinator can use remote-process HTTP transport and still validate witness-signed reports/votes. It tolerates one unavailable witness, fails closed with two unavailable witnesses for the 3-of-4 threshold, retains head state across process restart, and handles a committed vote whose HTTP response was lost.

## What it does not establish

The processes all run on one host and share one operator. Keys remain in local configuration files; loopback HTTP/HMAC is not TLS/mTLS; storage/backup/admin domains are not independent. Production deployment needs separate witness services, independently administered keys and backups, authenticated encrypted transport, monitoring, rate limits, and an incident recovery process.
