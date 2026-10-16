# Sources and Scope v3.4

- Repository inspected previously: https://github.com/Lycheetah/Lycheetah-Framework, observed default branch `master`, commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`. No source modifications made.
- Retained primary record verifier: `remote_anchor_http.py`, SHA-256 pinned in `SOURCE_PIN_v3.4.json`.
- Retained checkpoint witness/quorum implementation: local v3.3 research module copied unchanged in this pack.
- Ed25519 interface: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
- SQLite WAL and durability details: https://www.sqlite.org/wal.html and https://www.sqlite.org/pragma.html.
- Split-view/equivocating transparency logs are discussed by IETF RFC 9162 §11.3: https://www.rfc-editor.org/rfc/rfc9162.html#section-11.3. This research protocol is not RFC 9162 compliant.
