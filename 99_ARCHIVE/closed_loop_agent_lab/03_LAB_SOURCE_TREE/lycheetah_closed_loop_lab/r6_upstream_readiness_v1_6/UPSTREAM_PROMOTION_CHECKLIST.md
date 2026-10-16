# Upstream promotion checklist — v1.6

## Scope

This pack consolidates three narrowly-scoped changes against the inspected Lycheetah-Framework source snapshot `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`:

1. Reject malformed wire types rather than normalizing them (`models.py`, `receipt.py`).
2. Close the receipt schema around the finding/control fields the parser already treats as closed, and validate the policy digest shape.
3. Reject malformed text-rule string fields before coercion; align the policy schema with parser-enforced pattern-length, non-blank active status-basis and non-empty string-array constraints.

The candidate is **not merged, not applied to upstream, and not package-tested**. It is an integration handoff plus a read-only compatibility inventory. The aim is to make the promotion decision evidence-led.

## Safe application sequence

1. Obtain a local checkout at the inspected base revision. Create a named, non-default review branch yourself.
2. Ensure `git status --porcelain` is empty.
3. Run `python preflight_upstream_integration.py /path/to/Lycheetah-Framework` from this pack. The script validates exact source blob hashes, checks the clean branch, simulates patch application in a temporary copy, syntax-compiles the changed Python modules and meta-validates both candidate schemas. It does not edit the checkout.
4. Before touching the checkout, run the read-only compatibility inventory against the untouched base:

   ```sh
   python /path/to/r6_upstream_readiness_v1_6/scan_migration_compat.py \
     --repo /path/to/Lycheetah-Framework \
     --out /tmp/lycheetah-migration-compat.json
   ```

   Supply repeated `--policy path.json` and/or `--receipt path.json` flags for persisted records outside `examples/assurance`. A `.jsonl` receipt log is read line by line. Review every `needs_review` record before applying stricter parsing; do not automatically rewrite authenticated/auditable history. The report must be written outside the repository. The script refuses non-base, dirty or already-patched checkouts so the current parser/schema side of the comparison remains the genuine base contract.
5. From the repository root, apply patches in this order:

   ```sh
   git apply /path/to/r6_upstream_readiness_v1_6/strict_assurance_wire_types_v1_3.patch
   git apply --check /path/to/r6_upstream_readiness_v1_6/receipt_contract_delta_v1_6.patch
   git apply /path/to/r6_upstream_readiness_v1_6/receipt_contract_delta_v1_6.patch
   git apply /path/to/r6_upstream_readiness_v1_6/policy_type_guard_v1_6.patch
   ```

6. Review and copy the candidate schemas to their existing schema paths, then add the new tests:

   ```sh
   cp /path/to/r6_upstream_readiness_v1_6/policy.schema.strict-candidate.json lycheetah/assurance/schemas/policy.schema.json
   cp /path/to/r6_upstream_readiness_v1_6/receipt.schema.strict-candidate.json lycheetah/assurance/schemas/receipt.schema.json
   cp /path/to/r6_upstream_readiness_v1_6/tests/test_assurance_wire_types.py tests/test_assurance_wire_types.py
   cp /path/to/r6_upstream_readiness_v1_6/tests/test_assurance_policy_wire_types.py tests/test_assurance_policy_wire_types.py
   cp /path/to/r6_upstream_readiness_v1_6/tests/test_assurance_candidate_schemas.py tests/test_assurance_candidate_schemas.py
   ```

7. Run the upstream test gate in the repository's normal test environment:

   ```sh
   python -m pytest \
     tests/test_assurance_wire_types.py \
     tests/test_assurance_policy_wire_types.py \
     tests/test_assurance_candidate_schemas.py \
     tests/test_assurance_models.py \
     tests/test_assurance_policy.py \
     tests/test_assurance_receipt.py \
     tests/test_assurance_runtime.py \
     tests/test_assurance_schemas.py -q
   ```

8. Run the entire repository suite and CI. Compare against a green base baseline, not only the proposed tests. Do not merge if existing tests fail without an explained, reviewed reason.

## Explicit contracts

- Wire-type guards and schema shape are intended to agree on what a record means before canonicalization.
- Parser-level semantics still own regular-expression compilation, duplicate rule IDs, evidence caps, receipt digest/HMAC verification and receipt-chain validation.
- The existing receipt HMAC continues to authenticate the canonical digest string. This patch does not redesign authentication or claim exact-wire-byte authentication.
- JSON Schema and Python may differ on integral numeric values such as `20.0`. The current parser rejects float objects for `max_text_characters`; this version does not silently broaden that behavior.
- Tightening receipt fields may reject historical extension fields. Inventory first; do not assume all old records are malformed merely because a candidate schema is stricter.

## Promotion decision criteria

Promote only when: (a) exact base check passes, (b) patched modules compile, (c) new and existing assurance tests pass, (d) schemas validate generated records, (e) persisted-record inventory is reviewed, and (f) full CI is green or all deviations are explicitly explained. A local differential pass is necessary evidence, not sufficient release evidence.
