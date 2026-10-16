# Changelog v4.4 — Shared Pre-TLS Quotas

- Adds opt-in shared same-host SQLite quotas for global active connections, per-IP active connections and global connection-rate tokens.
- The store atomically reserves quota before TLS handshake or request-thread creation.
- Adds lease heartbeat, expiry and OS-boot-change handling; keeps local per-process v4.3 controls as an additional layer.
- Adds two mTLS gateway integration tests using distinct gateway instances and one shared database.
- Adds a 15-method ingress-store suite, including a two-OS-process competition for one global slot.
- Adds a lifecycle-checked gateway test runner that verifies all 51 methods and fails if non-main threads remain alive.
- Verification: 117 passing test methods across four separate invocations; 14 file fingerprints; Python compilation.
- Scope remains same-host local SQLite; no upstream changes, hosted calls, production deployment or distributed quota guarantee.
