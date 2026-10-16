# Sources and Scope v3.3

- Lycheetah baseline repo observed earlier at commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`: https://github.com/Lycheetah/Lycheetah-Framework
- Primary signed-record verifier `remote_anchor_http.py` is retained from the v3.1/v3.2 local lab. Its SHA-256 is pinned in `SOURCE_PIN_v3.3.json`.
- Ed25519 API reference: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
- Background on split-view transparency log risk: IETF RFC 9162, §11.3, https://www.rfc-editor.org/rfc/rfc9162.html#section-11.3

The witness quorum protocol is Lycheetah research code, not a standards-conformant Certificate Transparency or Byzantine consensus implementation. This iteration is not upstream code and has not been merged or run in upstream CI.
