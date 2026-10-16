# Source and protocol notes v3.5

## Retained source baseline

- Upstream repository: https://github.com/Lycheetah/Lycheetah-Framework
- Observed upstream commit: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`
- `remote_anchor_http.py` is source-pinned to the v3.3/v3.4 retained version.
- `checkpoint_witness_quorum.py` and `durable_freshness_verifier.py` are retained v3.3/v3.4 implementations, not modified upstream source.

## Relevant protocol material

- SQLite transactions: https://www.sqlite.org/lang_transaction.html
- SQLite backup API: https://www.sqlite.org/backup.html
- SQLite WAL behavior: https://www.sqlite.org/wal.html
- RFC 9162, Certificate Transparency v2, consistency and split-view considerations: https://www.rfc-editor.org/rfc/rfc9162.html

These references describe baseline technical mechanisms. They do not certify the Lycheetah design or the independent registry simulator.
