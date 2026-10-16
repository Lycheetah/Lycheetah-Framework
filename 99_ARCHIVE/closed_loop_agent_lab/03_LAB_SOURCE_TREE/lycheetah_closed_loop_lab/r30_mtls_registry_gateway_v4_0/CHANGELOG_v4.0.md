# Changelog v4.0

- Added `MTLSAnchoredRegistryHTTPServer`, a coordinator-facing mTLS gateway for the existing quorum-guarded registry dispatcher.
- Required TLS 1.2+, valid client certificate chain, exact allowed coordinator URI SAN, and existing HMAC request authentication.
- Restricted ingress to POST on two explicit route forms, one Host and Content-Type header, one decimal Content-Length <= 128 KiB, and no Transfer-Encoding.
- Added signed-response status/body/request-ID binding verification in the test HTTP client.
- Added negative tests for missing/wrong client identity, hostname mismatch, cleartext, changed body, bad HMAC, same-ID replay/payload conflict, wrong method, duplicate Content-Length and oversized bodies.
- Tightened the inherited process harness: child PIDs are tracked immediately, readiness bound increased to 30 seconds, and cleanup no longer masks the initiating startup failure if a SIGKILL wait itself times out.
- No upstream changes; no hosted endpoint was contacted.
