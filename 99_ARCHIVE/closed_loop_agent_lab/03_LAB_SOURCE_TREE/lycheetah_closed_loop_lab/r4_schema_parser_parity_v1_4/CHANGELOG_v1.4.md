# Changelog — v1.4

## Receipt schema/parser parity

- Audited the inspected `receipt.schema.json`, `AssuranceReceipt.from_dict`, `Finding.from_dict`, and `ControlReference.from_dict` at repository commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`.
- Extended the differential test beyond the five earlier composite mutations: eight normalizable wire substitutions are tested unsigned and HMAC-sealed, plus digest-consistent malformed policy-hash and unknown-finding records.
- Confirmed 18 of 20 source-equivalent cases are accepted by the modeled parser, the current schema rejects 10, and the strict parser and strict candidate schema reject all 20.
- Demonstrated that eight original HMAC seals still validate after a wire mutation that normalizes to the same canonical body. This is canonical-body authentication, not HMAC forgery.
- Found schema/parser disagreement in both directions: current schema accepts some malformed control fields and unknown finding properties that are rejected or transformed by parser rules, while the parser normalizes several scalar type mismatches rejected by schema.
- Added a strict-candidate schema, patch guide, and upstream integration tests. The upstream tests are proposed only; full package execution is unavailable in this environment.
- No public repository changes were made.
