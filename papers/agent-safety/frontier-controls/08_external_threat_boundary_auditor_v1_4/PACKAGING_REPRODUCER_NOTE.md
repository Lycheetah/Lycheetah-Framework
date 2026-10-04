# Packaging Reproducer Note

The standalone v1.4 directory available during the integration forge contained
the frozen report, auditor implementation, challenge corpus, manifests, and
hash ledger, but its original `benchmark.py` was not present.

This integration packet therefore does **not** pretend to preserve that missing
file. `reproduce_boundary_audit.py` is a newly authored independent reproducer
which reruns the copied auditor/challenge/manifests and checks the frozen
headline results:

- 12 external challenge packets;
- current modeled boundary: `0 FULL / 9 PARTIAL / 3 GAP`;
- proposed extended manifest: `12 FULL / 0 PARTIAL / 0 GAP`;
- single-required-control removal sensitivity `46/46`;
- finite classifier verification `64/64`.

The frozen standalone `reports/report.json` is preserved unchanged.
