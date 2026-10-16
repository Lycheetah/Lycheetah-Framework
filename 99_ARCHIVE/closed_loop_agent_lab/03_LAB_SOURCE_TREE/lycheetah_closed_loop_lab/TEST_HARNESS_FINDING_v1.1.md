# Test-harness finding v1.1 — Base64URL pad-bit mutation

## Observation

A fresh isolated run failed `authority_boundary_lab_v0_5/test_authority_gate_v0_5.py::test_hmac_tampering_is_denied`. The test changed the last character of an unpadded Base64URL HMAC token (`A` ↔ `B`) and expected verification to fail.

A SHA-256 HMAC is 32 bytes. Its unpadded Base64URL representation ends with a character whose lower two bits are padding bits rather than decoded data. If the encoded ending is `A`, changing it to `B` can change only those ignored bits; decoding yields the same signature. The test therefore did not always actually tamper with the signature. This was a test-method defect, not a demonstrated flaw in HMAC authentication.

## Correction

The test and demo now decode the signature segment, flip a significant byte (`raw[0] ^= 0x01`), re-encode it, and assert the altered token is rejected before any effect callback. A regression test verifies that the decoded signature bytes differ.

## Verification

- The v0.1-v0.6 legacy suites passed after correction: **66 tests**.
- The v0.5 test specifically asserting that the helper changes a decoded signature byte passed.
- The standalone v0.4 demo reported `tampered-token` as `DENY` with `token-authentication-failed` and zero candidate effect calls.
- This corrects test methodology. It does not establish the security of a production host or provider.
