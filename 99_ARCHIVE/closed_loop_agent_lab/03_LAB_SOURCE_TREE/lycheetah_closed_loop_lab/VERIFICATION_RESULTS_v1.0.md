# Verification Results — v1.0 R2 microtask

## Completed commands

`python r2_policy_parser_audit/run_comparison.py`

- 20 malformed-type probes generated.
- Source-equivalent baseline accepted 17/20.
- Strict candidate rejected 20/20.

`python r2_policy_parser_audit/test_policy_parser.py`

- 7 unit tests passed.
- The principal parameter-like loop includes 20 subcases, recorded as subtests.

`unzip -t lycheetah_closed_loop_lab_v1.0.zip`

- Archive integrity check passed.

## Limitations

The source-equivalent baseline recreates the relevant behavior from the inspected source, rather than importing the entire upstream package. The public repository was not modified. The proposed pytest file was not run against the complete repository because the repository could not be cloned into this runtime (DNS resolution failed). Historical test counts for v0.1–v0.9 remain separate records; they are not aggregated into this v1.0 result.
