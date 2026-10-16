# Changelog v4.8

- Added optional two-level IPv6 connection quota: configured leaf prefix plus a wider aggregate prefix/active ceiling.
- Added a companion lease-to-aggregate mapping updated within the shared SQLite transaction; deletion/reclamation cascades aggregate accounting.
- Pinned hierarchical prefix and aggregate-limit settings into shared-store schema 5 configuration so replicas with different policies fail closed.
- Wired the same aggregate check into process-local gateway admission and added aggregate bucket counts to the privacy-preserving operational snapshot.
- Added tests for rotation across sixteen `/64` networks under one `/56`, independent parent-prefix buckets, concurrent reservations, configuration drift, invalid config, gateway local/shared settings, and dead-process reclamation.
- Added a paired local differential probe against preserved v4.7 source fixture. This is a quota-accounting comparison, not Internet traffic or production evidence.
