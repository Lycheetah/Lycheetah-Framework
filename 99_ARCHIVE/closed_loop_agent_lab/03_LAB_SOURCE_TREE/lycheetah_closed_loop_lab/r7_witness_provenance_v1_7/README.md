# Lycheetah Closed-Loop Agent Lab v1.7 — Witness Provenance

This research iteration probes a specific trust-boundary property in the upstream `FinalityGate`: whether a public SHA-256 self-digest authenticates who issued an `AdmissionWitness` and whether required evidence is bound to trusted configuration.

Start here:

1. `WITNESS_PROVENANCE_AUDIT_v1.7.md` — finding, threat model, source, recommendations, boundaries.
2. `witness_provenance_probe.py` — standard-library source-equivalent reproduction and strict reference defense.
3. `test_witness_provenance_probe.py` — local test suite.
4. `witness_provenance_results.json` — machine-readable output.
5. `DEFENSE_BLUEPRINT.md` — ledger/token options and action-broker requirements.

Run:

```bash
python -m unittest -v test_witness_provenance_probe.py
python witness_provenance_probe.py
```

**Evidence level:** Source-inspected, source-equivalent probe. No complete upstream checkout; no production exploit; no upstream test run; no source modifications. See the audit's limits section.
