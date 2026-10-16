# Verification Results v1.7

- `python -m unittest -v test_witness_provenance_probe.py`: **5 tests passed**.
- `python witness_provenance_probe.py`: output generated and JSON parseable.
- Reference current semantics accepted the honest witness.
- Reference current semantics also accepted a witness whose evidence requirement was substituted and whose digest was recomputed, under the probe's explicit attacker-modifiable-witness model.
- Proposed HMAC + trusted requirement + issuance registry reference accepted a genuine witness, rejected a mutated token even when the attacker replaced the HMAC field with a public hash, and rejected a second use of the same witness ID.

This is not a test of the complete upstream package. The new harness mirrors a bounded section of `finality.py`; it is not an upstream exploit claim. The defensive path uses an in-memory registry and is only a design demonstrator, not production-ready replay protection.
