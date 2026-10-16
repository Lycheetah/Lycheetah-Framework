# Lycheetah Remote Witness mTLS Reference Pack v3.9

This pack extends the v3.8 remote-witness process harness from loopback HTTP/HMAC to HTTPS with mutual TLS, retaining HMAC replay protection and Ed25519 witness signatures.

## Verify

From this directory:

```sh
python verify_source_pins_v3.9.py
python -m py_compile *.py
python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
python -W error::ResourceWarning -m unittest -v test_remote_witness_process
```

The tests run in separate Python processes. This matches the retained harness convention and avoids the previously observed same-interpreter hang around process lifecycle tests.

## Tested

- 38 inherited quorum test methods.
- 24 remote witness/mTLS test methods.
- No hosted services, no upstream source edits.

## Key limitations

The test certificates and CA are generated at runtime and exist only under a temporary test directory. Four witness processes still share one host and administrator; the coordinator-facing registry harness remains a separate local loopback HTTP component. Non-loopback witness binding requires explicit opt-in but has not been tested on independent hosts. This is not production-certified infrastructure.

See `API_CONTRACT_v3.9.md`, `THREAT_MODEL_v3.9.md`, `RESULTS_v3.9.md`, and `UPSTREAM_INTEGRATION_PLAN_v3.9.md`.
