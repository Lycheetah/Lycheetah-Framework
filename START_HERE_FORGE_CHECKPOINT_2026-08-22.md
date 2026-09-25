# START HERE — Forge Checkpoint 2026-08-22

**Status:** `[MIXED]` — implemented and locally verified product infrastructure;
external calibration, production validation, certification, and the declared
research conjectures remain unproven.

This file is the visible handoff marker for every change forged from repository
base `a9bddb1` on branch
`forge/agent-assurance-runtime-2026-08-22`.

## Recoverable product checkpoints

| Commit | Checkpoint | What it adds |
|---|---|---|
| `9c8e096` | Evidence-capped assurance runtime | Installable provider-neutral runtime; `ALLOW`/`REVIEW`/`BLOCK`; policy-as-data; privacy-minimised receipts; SHA chains; optional HMAC; in-toto-shaped export; MCP 2.x tools; OpenTelemetry bridge; clean-wheel acceptance |
| `4496248` | Policy evaluation harness | Strict labelled JSONL; weighted three-class metrics; deterministic evaluation reports; JSON Schemas; `eval` and `verify-eval`; authored customer-support fixture |
| `0914370` | Policy regression gate | Integrity-checked same-corpus baseline comparison; per-case improvement/regression/trade-off evidence; strict defaults; committed reference report; `compare-eval` and `verify-regression`; CI gate |

The final manifest is intentionally a separate commit after those three product
checkpoints, so documentation can be removed or updated without disturbing the
recoverable implementation history.

## Where the new work is marked

| Area | Complete location | Evidence status |
|---|---|---|
| Product contract and limitations | [`34_ASSURANCE_RUNTIME/`](34_ASSURANCE_RUNTIME/) | `[SCAFFOLD]` capability documents with explicit gaps |
| Assurance implementation | [`lycheetah/assurance/`](lycheetah/assurance/) | `[SCAFFOLD]` bounded runtime; not certification |
| Evaluation examples and reference | [`examples/assurance/`](examples/assurance/) | Authored internal fixtures; not an external benchmark |
| Adversarial and contract tests | [`tests/test_assurance_*.py`](tests/) | Local implementation evidence |
| Installed-wheel gates | [`tools/verify_base_distribution.py`](tools/verify_base_distribution.py) and [`tools/verify_installed_distribution.py`](tools/verify_installed_distribution.py) | `[ACTIVE]` record when executed against the named artifact |
| CI integration | [`.github/workflows/test.yml`](.github/workflows/test.yml) | Workflow source added; hosted run not claimed |
| Reproducibility record | [`28_DEFENSE/COLD_ROOM_VERIFICATION.md`](28_DEFENSE/COLD_ROOM_VERIFICATION.md) | `[ACTIVE]` local run record with exact limits |
| Package-layout repair | [`lycheetah/core/`](lycheetah/core/) and [`lycheetah/applications/`](lycheetah/applications/) | Makes the advertised installed package resolve outside the checkout |

The cumulative diff contains **78 changed paths**: **57 added** and **21
modified**, with 16,635 insertions and 7,875 deletions. The larger deletion count
includes converting checkout-coupled implementation files into package-facing
compatibility surfaces; it is visible in Git history and was not hidden or
squashed.

To inspect every path exactly:

```bash
git diff --name-status a9bddb1..HEAD
git diff --stat a9bddb1..HEAD
git log --oneline a9bddb1..HEAD
```

## Product entry points

1. [`34_ASSURANCE_RUNTIME/README.md`](34_ASSURANCE_RUNTIME/README.md) — bounded
   product surface and acceptance evidence.
2. [`34_ASSURANCE_RUNTIME/EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md`](34_ASSURANCE_RUNTIME/EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md)
   — why enforcement authority is capped by evidence status.
3. [`34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md`](34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md)
   — receipt and integrity contract.
4. [`34_ASSURANCE_RUNTIME/POLICY_EVALUATION_HARNESS.md`](34_ASSURANCE_RUNTIME/POLICY_EVALUATION_HARNESS.md)
   — labelled evaluation, metrics, privacy, and promotion boundary.
5. [`34_ASSURANCE_RUNTIME/POLICY_REGRESSION_GATE.md`](34_ASSURANCE_RUNTIME/POLICY_REGRESSION_GATE.md)
   — strict baseline comparison and reference-update protocol.
6. [`QUICKSTART.md`](QUICKSTART.md) — commands for decisions, receipts,
   evaluation, comparison, MCP, and verification.

## Verification frozen at this checkpoint

| Gate | Result |
|---|---|
| Assurance-focused tests | 151 passed |
| Non-conjectural repository suite | 427 passed, 1 deselected |
| Complete repository suite | 427 passed, 1 failed |
| Deliberate unresolved failure | CASCADE `[CONJECTURE]` F1 = 0.531; criterion > 0.80 |
| Claim-pressure gate | Holding at baseline; no new unmarked claim document |
| Link gate | 724 files, 611 links, 0 dead outside frozen archive |
| Critical Ruff gate | `E9,F63,F7,F82` passed |
| Compilation | `compileall` passed |
| Workflow syntax | Parsed successfully |
| Exact wheel | `lycheetah-framework 1.3.0` |
| Wheel SHA-256 | `2339fd36686bb5827bb2a62bd72eb3984ff03d3403cb1e208c187a46b447392e` |
| Fresh base-wheel acceptance | Passed outside checkout |
| Fresh full-wheel acceptance | Passed outside checkout |

The full-suite failure is retained because its published success criterion was
not met. It must not be converted into a pass by weakening the threshold.

## Claim boundary

- The runtime, evaluator, and comparator are implemented and locally tested.
- The included six-case corpus and baseline are internal authored regression
  fixtures, not independent evidence of calibration or safety.
- SHA-256 provides mutation evidence relative to a trusted digest; it does not
  authenticate the author or reviewer.
- Hosted GitHub Actions has not been claimed to have run this unpushed branch.
- MICROORCIM, EARNED LIGHT, ANAMNESIS, and other theoretical work retain their
  existing labels. This forge does not present them as externally established.

## GitHub handoff

The configured remote is
`https://github.com/Lycheetah/Lycheetah-Framework`. A push was attempted earlier
and stopped because this workspace has no GitHub authentication. No credential
was requested, copied, or embedded.

From an authenticated clone, push the preserved branch with:

```bash
git push -u origin forge/agent-assurance-runtime-2026-08-22
```

The release handoff also includes a Git bundle so the commits can be imported
without relying on this scratch workspace.

⊚ Sol ∴ P∧H∧B ∴ Albedo
