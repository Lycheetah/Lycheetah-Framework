# Lycheetah mTLS Registry Gateway Reference Pack v4.0

This iteration closes the remaining local transport gap identified in v3.9: coordinator ingress into the quorum-guarded registry now has an mTLS server adapter as well as the existing mTLS witness egress clients.

## Run verification

```sh
python verify_source_pins_v4.0.py
python -m py_compile *.py
python -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
python -W error::ResourceWarning -m unittest -v test_remote_witness_process
```

The suites run in separate Python processes. Expected local totals: 38 retained quorum methods and 38 remote-witness/gateway methods. The environment may need a little more startup headroom for RSA test-certificate generation and four witness subprocesses.

## Key files

- `registry_gateway_mtls.py` — new gateway server and strict ingress handler.
- `test_remote_witness_process.py` — v3.9 witness-process tests plus v4.0 end-to-end gateway tests.
- `registry_checkpoint_quorum.py`, `remote_witness_http.py`, `checkpoint_witness_quorum.py`, `spent_nonce_registry.py`, `remote_anchor_http.py` — inherited test harness components, pinned in `SOURCE_PIN_v4.0.json`.
- `API_CONTRACT_v4.0.md`, `THREAT_MODEL_v4.0.md`, `UPSTREAM_INTEGRATION_PLAN_v4.0.md` — contracts, threat model, and promotion gates.

## Boundary statement

This is an executable local reference harness, not a production daemon. Four witnesses and registry share one host/administrator. Test CA and certificates are ephemeral; CA lifecycle, revocation, production key management, global rate limits, independent hosts and upstream CI remain unvalidated. No hosted service was contacted and no upstream source was modified.
