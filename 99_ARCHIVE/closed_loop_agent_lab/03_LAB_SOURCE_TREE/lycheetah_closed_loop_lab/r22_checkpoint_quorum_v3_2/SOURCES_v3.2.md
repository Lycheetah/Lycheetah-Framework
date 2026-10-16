# Sources and Scope v3.2

## Standards and background

- IETF RFC 9162, *Certificate Transparency Version 2.0*, especially the use of append-only logs, consistency auditing, monitors, and the documented limitation that a signed log can present inconsistent views to different clients. https://www.rfc-editor.org/rfc/rfc9162.html
- The witness/quorum protocol here is original Lycheetah research code; it is not an implementation of RFC 9162, a Merkle transparency log, or a standardized Byzantine consensus protocol.

## Repository baseline

- Repository: https://github.com/Lycheetah/Lycheetah-Framework
- Observed default branch commit for v3.0/v3.1: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`
- Exact `remote_anchor_http.py` source copy used as the signed primary-record verifier: `r21_remote_anchor_protocol_v3_1/remote_anchor_http.py` (the hash is recorded in `SOURCE_PIN_v3.2.json`).
- The witness quorum implementation is new local reference code. No upstream file was modified.

## Cryptographic library

- Python `cryptography` Ed25519 APIs: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/

## How the source informs this protocol

RFC 9162 explicitly describes inconsistent views presented by a misbehaving transparency log and identifies comparison among clients/monitors (often called gossip) as relevant to detecting inconsistent views. This is motivating background only. Lycheetah v3.2 uses signed witness votes and nonce-fresh quorum head reports; it does not implement the RFC's Merkle-tree construction, inclusion proofs, or consistency proofs, and it is not claimed to be RFC 9162 conformant. See [RFC 9162 §11.3](https://www.rfc-editor.org/rfc/rfc9162.html#section-11.3).
