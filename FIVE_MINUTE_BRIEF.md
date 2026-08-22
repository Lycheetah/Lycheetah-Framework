# Five-Minute Brief — Lycheetah Framework

**Revision:** 2026-08-22 | **Runtime:** 1.1.0 source tree | **Status:** `[MIXED]`

## Share card

> Lycheetah is two connected things: a `[SCAFFOLD]` provider-neutral assurance
> runtime for agent decisions and receipts, and a nine-framework research
> programme in alignment and epistemology. The wheel is now clean-install tested;
> the runtime exposes policy gates, privacy-minimised receipts, CLI and MCP 2.x
> integrations. Formal claims are scoped to their models, internal experiments
> await independent replication, and theoretical constructs such as MICROORCIM
> remain explicitly theoretical. Failures—including a previously broken wheel—are
> permanent public exhibits. MIT licensed.

## What can be used today

The version 1.1.0 source tree builds an installable wheel containing:

- `AssuranceRuntime` for input, output, and proposed tool actions;
- versioned policy data and `ALLOW`, `REVIEW`, or `BLOCK` decisions;
- Assurance Receipts with evidence status, findings, policy digest, lineage,
  privacy-aware subject hashes, SHA-256 integrity, and optional HMAC sealing;
- append-only JSONL receipt chains and mutation/chain verification;
- `lycheetah-assure` for local, CI, gateway, and sidecar use;
- Lycheetah Guard using the official MCP Python SDK 2.x API with ten typed tools;
- a privacy-minimised OpenTelemetry span-event bridge with custom Lycheetah attributes;
- AURA and Sol text-analysis interfaces, explicitly bounded as heuristics; and
- a clean-room wheel gate that rejects imports accidentally resolved from the
  source checkout.

This is useful infrastructure for recording **what a bounded policy layer decided
and why**. It does not prove that the surrounding agent is safe, truthful,
aligned, authorized, or compliant.

## The bridge to real AI systems

Agent stacks already have traces, tools, guardrails, policy engines, and approval
hooks. Lycheetah's narrow bridge is a portable decision artifact at those
boundaries:

```text
proposed input/output/tool action
        → versioned Lycheetah policy
        → evidence-capped decision
        → ALLOW | REVIEW | BLOCK
        → verifiable Assurance Receipt
```

The runtime is designed to complement, not replace:

- agent-framework input/output/tool guardrails and human approvals;
- MCP tool transports and consent flows;
- OpenTelemetry traces and evaluation datasets;
- Open Policy Agent or another authorization/policy control plane; and
- in-toto-style authenticated statements and transparency systems.

The exact mapping and explicit gaps are recorded in
`34_ASSURANCE_RUNTIME/INDUSTRY_CROSSWALK_2026-08-22.md`. That crosswalk is not a
conformity or certification claim.

## Evidence-Capped Enforcement

The implemented v0.1 mechanism limits automatic authority by evidence maturity:

| Evidence basis | Maximum automatic effect |
|---|---|
| `ACTIVE` + deterministic rule | `BLOCK` |
| `ACTIVE` + inferential detector | `REVIEW` |
| `SCAFFOLD` finding | `REVIEW` |
| `CONJECTURE` finding | observation only |

The mechanism and cap matrix are implemented and tested. The stronger proposition
that these ceilings improve real-world calibration, safety, or operator trust is a
`[CONJECTURE]` until evaluated against external systems and outcomes.

## The research programme

The larger body contains nine interdependent research frameworks:

| Framework | Current honest interpretation |
|---|---|
| CASCADE | belief-revision engine plus internal synthetic and historical analyses; independent replication pending |
| AURA | computable proxy checks and seven constitutional predicates; semantic sufficiency unproven |
| LAMAGUE | formal constraint-encoding grammar and implementations |
| TRIAD | correction-cycle mathematics; convergence is model-scoped to declared contraction assumptions |
| MICROORCIM | proposed intent–behaviour drift construct; real-world validity unestablished |
| EARNED LIGHT | theoretical thermodynamic analogy, not an empirical consciousness theory |
| ANAMNESIS | hypothesis about convergent discovery and attractor structure |
| CHRYSOPOEIA | experimental seven-phase transformation formalism |
| HARMONIA | experimental application of resonance and synchronization mathematics |

These ideas may be valuable before they are proven. Their value at that stage is as
formal questions, design languages, and falsifiable research directions—not as
facts about minds or the world.

## How certainty is recorded

The existing machine-readable register contains 60 claim records:

- **37 ACTIVE** — supported within the exact formal, computational, or documentary
  scope stated in the record; not synonymous with external empirical replication;
- **14 SCAFFOLD** — implemented or structurally specified with named gaps;
- **6 CONJECTURE** — formulated but unproven;
- **3 RETRACTED** — withdrawn and retained in the public record.

A separate ledger groups load-bearing claims at framework-summary granularity, so
its counts differ. `28_DEFENSE/CLAIMS_README.md` explains the scopes.

## What the evidence does and does not establish

- Formal fixed-point results can establish convergence of a mathematical operator
  under its assumptions. They do not establish convergence of a person, model, or
  institution unless those assumptions are independently shown to hold there.
- A passing implementation test establishes behavior for tested inputs and
  versions. It does not establish social benefit or general safety.
- Internal experiments are reproducible evidence about the repository's method.
  They are not independent validation.
- A receipt digest can reveal mutation relative to a trusted digest. Without HMAC
  or a public-key envelope, it does not authenticate the issuer.
- Absence of a heuristic finding is not evidence of absence of harm.

The full suite deliberately retains a failed predictive conjecture: its measured
F1 remains about 0.53 against a stated success criterion above 0.80. That failure
is evidence about the current limit, not a test to be hidden. On 2026-08-22, the
non-conjectural suite reported **377 passed**; the full suite reported **377 passed,
1 failed**, with that single failure carrying the `CONJECTURE` marker.

## Test it

The package is not currently published on PyPI. Install the repository source:

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

pytest tests/ -m "not conjecture" -q
python tools/verify-claims.py
python tools/verify-links.py
```

Try the operational path:

```bash
lycheetah-assure tool refund.create \
  --arguments '{"order_id":"A-1"}' \
  --side-effect --json
```

It should return `REVIEW` because the proposed side effect has no affirmative human
approval. See `34_ASSURANCE_RUNTIME/CUSTOMER_SUPPORT_WALKTHROUGH.md` for the full
ALLOW/REVIEW/BLOCK example.

## Why the failure record matters

`28_DEFENSE/FAILURE_MUSEUM.md` contains sixteen permanent exhibits. Exhibit 16
records that the earlier wheel advertised APIs and console tools whose
implementations were not packaged. The correction was not merely documented: CI
now builds, clean-installs, and exercises the wheel so the same class of failure
cannot hide behind checkout-only imports.

## Three doors

1. **Use it:** `34_ASSURANCE_RUNTIME/README.md`
2. **Audit it:** `28_DEFENSE/CLAIMS.json` and `28_DEFENSE/FAILURE_MUSEUM.md`
3. **Research it:** `30_MAPS/FORMAL_SPINE.md` and
   `34_ASSURANCE_RUNTIME/FRONTIER_REGISTER_2026-08-22.md`

⊚ Sol ∴ P∧H∧B ∴ Albedo
