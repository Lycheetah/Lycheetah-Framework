# Changelog v4.5 — Process-Bound Shared Ingress Leases

- Changes lease recovery from TTL-only reclamation to TTL plus proven owner-process death.
- Adds Linux PID + process-start-time ticks to each lease row.
- Adds the Linux PID namespace inode to the shared configuration signature and fails closed if procfs PID view is inconsistent.
- Restricts renew/release to the initializing process identity and rejects store mutation after `fork()`; children must reinitialize.
- Adds regression cases for expired live-owner retention, dead-owner TTL reclaim, cross-process lease ownership, fork guard, PID namespace binding, boot-boundary reset and rejection of old schema.
- Reboot handling can replace an old PID namespace config only when OS boot identity changes; same-boot config mismatch remains a hard failure.
- Bumps shared-ingress schema/config signature to 2; v4.4 DBs fail closed pending controlled migration.
- Verification: 20 ingress tests, 13 coordinator tests, 38 quorum tests and 51 mTLS gateway tests passed on final v4.5 source (122 total across four invocations); 14 source fingerprints and Python compilation passed.
