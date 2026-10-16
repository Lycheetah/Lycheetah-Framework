# Verification results v1.4

## Executed locally

- `python run_differential.py`: passed all fixture assertions.
- `python -m unittest -v test_schema_parser_parity.py`: **6 test methods passed**. The suite includes 50-plus subtest combinations across unsigned and HMAC-sealed inputs.
- `python -m py_compile schema_parser_parity.py run_differential.py test_schema_parser_parity.py build_schema_snapshot.py`: passed.
- Current and strict-candidate JSON Schemas parse and validate with the local `jsonschema` package.

## Differential matrix

The 20-row matrix contains eight normalizable wire substitutions in unsigned and HMAC-sealed form, plus two malformed but self-consistent issuer records (policy digest shape and unknown finding property), each unsigned and HMAC-sealed.

- Source-equivalent parser behavior accepts 18/20 rows. It accepts all eight normalizable mutation pairs and the malformed policy-digest records, but rejects an unknown Finding property as the actual `Finding.from_dict` code does.
- Current schema rejects 10/20 rows and accepts 10/20. It rejects schema/finding scalar type mismatches and invalid policy hash shape, but its open nested control schema and permissive finding shape accept the rest.
- Strict parser candidate rejects 20/20 rows.
- Strict candidate schema rejects 20/20 rows.
- The original HMAC remains valid for 8/8 normalizable wire substitutions because the normalized canonical body and digest remain unchanged. This does **not** demonstrate an HMAC forgery; it demonstrates that the scheme authenticates the normalized digest rather than exact input JSON bytes.

## Not executed

The local tests use the source-equivalent parser model, not the full upstream package. `PROPOSED_UPSTREAM_TESTS_v1.4.py` is syntax-checked only; it has not been run inside a clean Lycheetah-Framework checkout. No upstream CI, installed wheel, issue, branch, or pull request was produced. The schema snapshot is a semantic reconstruction of the fetched JSON Schema, reformatted for readable local use, not a byte-for-byte snapshot.
