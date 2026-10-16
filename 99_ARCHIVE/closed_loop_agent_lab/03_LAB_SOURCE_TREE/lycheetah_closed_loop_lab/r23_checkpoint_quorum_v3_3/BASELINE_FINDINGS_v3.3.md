# Frozen v3.2 baseline findings reproduced by v3.3

The output is recorded in `baseline_v3_2_reproduction.json`. The script intentionally imports the frozen v3.2 module tree under `baseline_v3_2/`.

| Finding | Frozen v3.2 result | v3.3 control |
|---|---|---|
| Caller-constructed freshness summary passed as currentness evidence | `ACCEPTED_BY_V3_2` | `test_current_chain_rejects_caller_constructed_freshness_summary` rejects it |
| One public key aliased under four witness IDs counts as three votes | `ACCEPTED_BY_V3_2` | `test_witness_roster_rejects_aliased_public_keys` rejects registry |
| Boolean `sequence=True` accepted after recomputed public digest | `ACCEPTED_BY_V3_2` | `test_certificate_rejects_boolean_sequence_even_with_recomputed_digest` rejects it |
| Boolean `max_byzantine=True` accepted after recomputed public digest | `ACCEPTED_BY_V3_2` | `test_certificate_rejects_boolean_fault_budget_even_with_recomputed_digest` rejects it |
| Boolean sequence returned by the pluggable CAS guard | `ACCEPTED_BY_V3_2` | `test_attest_rejects_boolean_sequence_from_pluggable_guard` rejects it |

The certificate digest is a mutation-detection checksum, not an authentication secret; a caller can recompute it. Authenticity continues to come from the pinned primary anchor signature and distinct witness signatures.
