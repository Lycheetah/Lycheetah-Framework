# Lycheetah Registry External Quorum v3.7

**Status:** local reference prototype; not production-certified. The work composes the existing spent-challenge registry with an append-only checkpoint vote ledger, a fresh 3-of-4 head quorum, and an HTTP boundary that sends every protected registry request through the anchored dispatcher.

## Run

```bash
python -m pip install -r requirements.txt
python verify_source_pins_v3.7.py
python -m py_compile *.py
python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
python demo_external_quorum_rollback_v3_7.py
```

The focused suite contains 38 test methods. The retained v3.6 regression suite contributes another 82 methods. The two suites are intentionally run separately because each version directory contains its own modules; 120 test methods passed across the respective successful invocations.

## What this prototype adds

- Fingerprints the actual logical state of the registry's `challenges`, `request_nonces`, and `clock_state` tables, including SQLite schema objects.
- Records signed monotonic checkpoints, including previous checkpoint, exact state digest, request ID, and issuance timestamp.
- Uses a four-witness roster with one tolerated faulty witness and a 3-of-4 certificate/head quorum.
- Requires fresh nonce-bound witness head reports before trusting the latest known checkpoint.
- Stores prepared/pending mutation intent and authenticated response-cache records before surfacing results.
- Routes protected requests through one guarded, loopback-only HTTP dispatcher; unguarded database writes are detected at next preflight.
- Keeps partial quorum publication recoverable through the same pending checkpoint; ambiguous outcomes fail closed.

## Critical trust boundary

The four witness objects and their SQLite databases are separate local test stores, not independently administered remote services. The quorum is a useful protocol experiment but **does not establish real distributed independence**. If the registry DB, client anchor DB, and all witness stores are rolled back to coordinated snapshots, the negative-control test still accepts the old state. An attacker who can control every witness storage/key/backup domain can defeat this local model.

This is a Linux/POSIX reference implementation because dispatch serialization uses `fcntl.flock`. No hosted service is contacted. No upstream files were changed and upstream CI was not run.
