# Changelog v1.7

- Added a source-equivalent witness-provenance experiment based on the inspected `finality.py` at commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`.
- Added an explicit conditional threat model for attacker-modifiable persisted/RPC witness values.
- Added a re-hashed witness mutation that substitutes the required evidence requirement and admission-receipt digest.
- Added a reference defense using HMAC authentication, trusted configured requirements, issuer tracking, expiry and one-use replay detection.
- Documented how actual production finality needs a durable ledger and action broker, and why local in-memory consumption does not offer remote atomicity.
- No upstream repository modifications made; complete upstream checkout and CI remain unavailable.
