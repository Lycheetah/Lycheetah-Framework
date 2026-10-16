# Changelog v3.9

- Added TLS 1.2+ server transport with mutual TLS client certificates.
- Added coordinator URI SAN identity check after CA validation.
- Added per-witness IP SAN validation through client hostname verification.
- Kept request HMAC freshness and persistent request-ID replay protection, with a v3.9 domain-separated signature string.
- Added explicit opt-in for a specific non-loopback IPv4 bind; rejected wildcard bind addresses and DNS names in server bind config.
- Moved TLS handshakes into per-request worker threads with a timeout to prevent a slow TLS handshake from stalling the accept loop.
- Added tests for absent/wrong client identity, certificate/address mismatch, cleartext downgrade, slow handshakes, and bind configuration.
- No upstream files changed. This remains a same-host reference prototype.
