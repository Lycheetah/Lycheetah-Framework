# Upstream Integration Plan v4.5

1. Apply on a clean, non-default branch after reviewing the observed base commit.
2. Add owner PID/start ticks and PID-namespace inode to the lease schema/config contract. Existing v4.4 stores should fail closed; use a new DB path or perform an explicit drained migration.
3. Add a service-manager rule: after `fork`, each worker must reopen its own store. Deploy all quota participants in the same Linux PID namespace and with the same configuration/DB path.
4. Run the 20-method ingress suite and retained coordinator/quorum suites on the full package.
5. The final local source completed the full 51-method remote-witness/gateway suite with a clean lifecycle summary. Repeat all suites on the clean upstream checkout and CI runner before promotion.
6. Add a real-process test that pauses the reservation owner past TTL while a competing gateway tries admission; verify the contender is denied until owner death/release.
7. Review operator recovery for wedged processes. A stuck lease is a visible availability issue, not something to clear by manually editing SQLite.
8. Keep the shared SQLite feature opt-in and document same-host/same-PID-namespace scope.

No upstream source, pull request, or upstream CI was changed in v4.5 local work.
