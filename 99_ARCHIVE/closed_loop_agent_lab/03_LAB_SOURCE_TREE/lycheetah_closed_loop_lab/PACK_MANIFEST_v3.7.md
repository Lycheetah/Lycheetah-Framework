# Complete Research Pack Manifest v3.7

This archive contains the Lycheetah Closed-Loop Agent Lab history through R27 / v3.7. It includes the previous artifacts and a new standalone `r27_registry_external_quorum_v3_7/` folder with source-pinned helpers, a new quorum checkpoint wrapper, 38 focused tests, source pin checker, rollback demo, API contract, threat model, scenario matrix, upstream integration plan, logs and checksums.

Primary new features are described in `r27_registry_external_quorum_v3_7/README_v3.7.md`. The new local prototype is not production-certified. The four witness stores are local files in the experiment, not independent remote services; a coordinated rollback of all trust domains remains a negative control.

Current verification: 37 focused v3.7 tests and 82 retained v3.6 tests passed in separate invocations. Source pin checker, Python compilation, rollback demonstration, and archive checks passed. No upstream source was changed, no upstream CI was run, and no hosted endpoint was contacted.
