# Lycheetah Closed-Loop Agent Lab v3.8 — Remote Witness Process Boundary

This round moves the v3.7 registry checkpoint quorum from in-process witness objects to four distinct OS processes with loopback HTTP RPC, per-witness HMAC API credentials, persistent API replay protection, and the retained Ed25519 witness signatures.

## What this establishes

- The coordinator can bootstrap and mutate the protected registry through four remote witness HTTP processes.
- Witness votes and head reports still feed the existing signature/quorum verification code.
- Process restart retains a witness's durable checkpoint history.
- Lost HTTP response after a witness commits its vote can be recovered if the live quorum remains sufficient.
- A single stopped witness is tolerated; two stopped witnesses fail closed for the 3-of-4 configuration.
- Unauthorized, altered, replayed, oversized, or malformed transport requests are rejected.

## Verification

Run from this directory:

```sh
python verify_source_pins_v3.8.py
python -m py_compile *.py
python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum test_remote_witness_process
```

The exact test counts and run log are captured in `RESULTS_v3.8.md` after verification.

## Critical limitations

This is **not** a real distributed deployment. All four processes run on one host under one test operator; key material is loaded from local JSON configuration; the service is HTTP loopback rather than TLS/mTLS; and backup/restore domains are not independent. The reference wrapper retains POSIX `fcntl.flock`. No hosted endpoint is contacted, no upstream repository is modified, and upstream CI is not run.

See `API_CONTRACT_v3.8.md`, `THREAT_MODEL_v3.8.md`, and `UPSTREAM_INTEGRATION_PLAN_v3.8.md`.
