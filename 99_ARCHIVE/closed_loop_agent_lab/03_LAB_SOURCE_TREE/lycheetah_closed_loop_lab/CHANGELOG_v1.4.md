# Changelog — v1.4

- Added R4 differential audit of assurance receipt schema, parser normalization, and HMAC digest verification.
- Added 20-row matrix: eight normalizable wire substitutions (unsigned and HMAC-sealed), plus malformed policy-hash and unknown-finding records (unsigned and HMAC-sealed).
- Results: source-equivalent parser accepts 18/20, the current schema rejects 10/20, strict parser and schema candidates reject 20/20.
- Identified mismatches in both directions: parser normalization accepted some malformed control-field types, while the current schema accepted unknown finding fields that the parser rejects.
- Added strict-candidate JSON Schema, patch guide, and proposed upstream regression tests.
- Six local test methods passed. No upstream files were changed; real-package tests and CI remain outstanding.
