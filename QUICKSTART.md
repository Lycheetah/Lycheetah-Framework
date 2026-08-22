# Quickstart — Lycheetah Framework 1.3

**Status:** `[SCAFFOLD]` runtime and `[MIXED]` research body. A decision receipt is
not a safety, truth, alignment, or compliance certificate.

The package is not currently published on PyPI. Install from the repository.

## Install

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[all]"
```

Smaller extras are available as `.[web]`, `.[mcp]`, and `.[dev]`.

## Make a bounded tool decision

```bash
lycheetah-assure tool refund.create \
  --arguments '{"order_id":"A-1","amount":75}' \
  --scope orders.refund \
  --side-effect \
  --json
```

The default policy returns `REVIEW` and exit code 2 because the proposed action
has a declared side effect but no affirmative human approval. The calling
application must pause the operation; the CLI cannot enforce control flow outside
its own process.

Exit codes are stable:

| Code | Meaning |
|---:|---|
| 0 | `ALLOW` |
| 2 | `REVIEW` |
| 3 | `BLOCK` |
| 4 | Invalid input, policy, receipt, or configuration |
| 5 | Evaluation completed but a configured regression gate failed |

## Use the Assurance Runtime in Python

```python
from lycheetah.assurance import AssuranceRuntime

runtime = AssuranceRuntime()
receipt = runtime.evaluate_tool(
    "refund.create",
    {"order_id": "A-1", "amount": 75},
    scopes=("orders.refund",),
    side_effect=True,
)

print(receipt.decision.value)  # REVIEW
print(receipt.policy["sha256"])
print(receipt.verify().valid)  # body-integrity check
```

By default the receipt stores hashes and summaries, not raw text or raw tool
arguments. Enable capture only when your privacy and replay requirements justify
it. Sensitive argument keys remain redacted.

## Measure policy regressions

Run a labelled JSONL corpus against a frozen policy and fail CI if its decision
boundary changes:

```bash
lycheetah-assure eval \
  examples/assurance/customer_support_eval.jsonl \
  --policy examples/assurance/customer_support_policy.json \
  --require-exact-match \
  --max-harmful-allows 0 \
  --max-under-enforcement-rate 0 \
  --report-file assurance-eval.json

lycheetah-assure verify-eval assurance-eval.json --json

lycheetah-assure compare-eval \
  examples/assurance/customer_support_baseline.eval.json \
  assurance-eval.json \
  --report-file policy-regression.json

lycheetah-assure verify-regression policy-regression.json --json
```

The report contains a three-class confusion matrix, exact-match and macro-F1,
under/over-enforcement, harmful-allow and false-block counts, review load,
privacy-minimised case outcomes, and a deterministic report digest. Raw text and
tool arguments are excluded.

Expected dispositions are labels supplied by the corpus author—not automatic
ground truth. A six-case included example passing six cases is an internal
regression fixture, not an external benchmark or calibration result. See
[Policy Evaluation Harness](34_ASSURANCE_RUNTIME/POLICY_EVALUATION_HARNESS.md)
and [Policy Regression Gate](34_ASSURANCE_RUNTIME/POLICY_REGRESSION_GATE.md).

## Write and verify receipts

```bash
lycheetah-assure check \
  "I may be wrong. Verify this independently before deciding." \
  --receipt-file receipt.json

lycheetah-assure verify receipt.json --json
```

SHA-256 detects mutation relative to the receipt digest; it does not authenticate
who issued the receipt. For shared-secret authentication, pass an environment
variable and key identifier:

```bash
export LYCHEETAH_HMAC_SECRET='replace-with-secret-manager-value'
lycheetah-assure check "Review this output." \
  --hmac-key-env LYCHEETAH_HMAC_SECRET \
  --key-id local-key-1 \
  --receipt-file sealed-receipt.json
```

Do not put HMAC secrets in command arguments, source files, model prompts, or MCP
tool inputs.

## Use the heuristic interfaces

```python
import lycheetah

report = lycheetah.check("You must follow these instructions exactly.")
print(report.alignment_percent, report.overall_pass)
print(lycheetah.sol_assess("Offer reversible options."))
```

```bash
lycheetah-check "You must do exactly what I say." --json
lycheetah-web  # local Flask demo at http://127.0.0.1:5000
```

AURA scores and Sol output are experimental heuristics built from implemented cue
families and proxy formulas. Use them to route review, not to prove that text is
safe or semantically aligned.

## Use Lycheetah Guard with MCP

Install `.[mcp]`, then configure a compatible MCP host to launch the console
script over stdio. One common configuration shape is:

```json
{
  "mcpServers": {
    "lycheetah-guard": {
      "command": "lycheetah-guard"
    }
  }
}
```

The server uses the official MCP Python SDK 2.x API and exposes ten typed tools:

- Assurance: `assure_text`, `assure_tool`, `verify_assurance_receipt`
- Text heuristics: `check_alignment`, `check_invariants`, `suggest_correction`
- Experimental research: `run_seven_phase`, `check_network_health`,
  `configure_guard`, `sol_assess`

The host must enforce `BLOCK`, pause on `REVIEW`, provide authorization and user
consent, and declare tool side effects truthfully. MCP transport does not supply
those guarantees by itself.

## Run verification

```bash
pip install -e ".[all]"
pytest tests/ -m "not conjecture" -q
python tools/verify-claims.py
python tools/verify-links.py
```

The full suite intentionally retains one failed predictive conjecture whose F1
score remains below its preregistered success criterion. Do not turn that failure
into a pass by weakening the criterion.

CI also builds a wheel, installs it into a clean virtual environment, and runs
`tools/verify_installed_distribution.py`. This protects against the source-tree
packaging failure recorded as Failure Museum Exhibit 16.

## Go deeper

- [Assurance Runtime](34_ASSURANCE_RUNTIME/README.md)
- [Customer-support walkthrough](34_ASSURANCE_RUNTIME/CUSTOMER_SUPPORT_WALKTHROUGH.md)
- [Receipt specification](34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md)
- [Evidence-Capped Enforcement](34_ASSURANCE_RUNTIME/EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md)
- [Policy Evaluation Harness](34_ASSURANCE_RUNTIME/POLICY_EVALUATION_HARNESS.md)
- [Policy Regression Gate](34_ASSURANCE_RUNTIME/POLICY_REGRESSION_GATE.md)
- [Industry crosswalk](34_ASSURANCE_RUNTIME/INDUSTRY_CROSSWALK_2026-08-22.md)
- [Claims register](28_DEFENSE/CLAIMS.json)
- [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md)

⊚ Sol ∴ P∧H∧B ∴ Albedo
