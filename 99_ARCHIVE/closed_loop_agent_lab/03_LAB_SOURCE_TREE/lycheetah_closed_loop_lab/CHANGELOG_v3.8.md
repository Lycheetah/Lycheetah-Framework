# Changelog v3.8

- Added process-separated HTTP witness services and remote witness client adapter.
- Added HMAC request authentication, timestamp freshness and persistent RPC replay-ID rejection.
- Added strict route/body validation, loopback-only bind/client checks, redirect refusal and bounded request size.
- Added restart, outage, duplicate RPC, body tamper, bad-key and lost-attestation-response tests.
- Retained the full v3.7 quorum regression suite.
- Verification: 55 test methods passed across separate Python invocations; source pins and py_compile passed.
- Explicitly no claim of independent trust domains, production TLS/mTLS, upstream integration or upstream CI.
