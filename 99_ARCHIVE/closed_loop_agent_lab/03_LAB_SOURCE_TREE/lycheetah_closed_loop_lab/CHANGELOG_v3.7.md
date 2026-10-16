# Closed-Loop Agent Lab Changelog v3.7

- Added R27: Registry External Quorum.
- Bound live spent-challenge registry SQLite state/schema to signed, parent-linked checkpoints and fresh four-witness quorum reports.
- Added guarded loopback HTTP dispatch and persistence/recovery handling around actual registry service mutations.
- Added 37 focused regression methods; retained the 82-method v3.6 suite in a separately verified run (120 methods across both local suite invocations).
- Preserved the all-witness coordinated rollback as an explicit negative control and documented the missing requirement for genuinely independent operational trust domains.
- No upstream repository content was changed and no hosted service was contacted.
- Added the fail-closed unexpected-handler-exception-after-commit regression; it verifies no exception details leak and recovery returns outcome-unknown rather than success.
