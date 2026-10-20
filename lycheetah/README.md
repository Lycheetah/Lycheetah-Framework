# Python package — public interfaces and bounded controls

**Guide updated:** 21 October 2026. **Source version:** 1.3.0 in
[pyproject.toml](../pyproject.toml). Component contracts and research packets have
their own versions.

This directory owns the public Python wrappers and the assurance, compaction,
consensus, sovereign-control and handoff modules. Foundational engines live in
[12_IMPLEMENTATIONS](../12_IMPLEMENTATIONS/README.md): the package configuration
maps those sources into `lycheetah.core`, `.applications` and `.experiments`.
Edit the owning source rather than creating a second engine copy.

**20 October 2026 review:** the consensus execution binding is corrected and
uses the `lycheetah.consensus-verdict.v2` digest profile. The digest binds the
anchor and complete outcome and is recomputed at issuance/execution. Old
unverifiable verdicts and their permits require re-deliberation and reissue;
copying an old digest into new flags does not migrate it. This is integrity
binding, not external issuer authentication. The legacy `obstruction_free` and
`byzantine_safe` fields describe a connectivity/consistency proxy and a quarantine
budget, respectively. See the [full review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md)
and [regressions](../tests/test_consensus_integrity.py).

**21 October gateway correction:** proposal, dispatch claim and result recording
now use the checkpoint-gated workflow. Opening or using a journal with an
uncheckpointed tail blocks; a later action does not silently publish that history.
Recovering an affected journal requires separate reconciliation, not an automatic
retry. Dispatch rechecks the current policy and distinguishes an omitted live
action from an explicitly empty one. Receipts identify the policy evaluated
before the executor call. If result checkpointing fails after the call, the
outcome is `UNKNOWN` with no success receipt. See the
[gateway regressions](../tests/test_gateway_boundaries.py).

**Consent preservation:** the maintained compaction codec rejects literal input
consent values `R`, `I` and `N`, which collide with its wire abbreviations. Supply
the explicit intended value; existing ambiguous inputs require author review.
The frozen supplied codec retains its original bytes and documented counterexample.
Canonical consent values and other unreserved strings round-trip with identical
protected hashes in both wire modes. See the
[consent regressions](../tests/test_compaction_consent_roundtrip.py).

| Area | Source / documentation | Scope |
|---|---|---|
| Public imports and commands | [__init__.py](__init__.py), [cli.py](cli.py), [package configuration](../pyproject.toml) | Public interfaces and eleven declared command entry points. |
| Assurance | [assurance/](assurance/), [runtime guide](../34_ASSURANCE_RUNTIME/README.md) | Versioned policy decisions, evidence caps, receipts, guards and finality. |
| Compaction | [compaction/](compaction/), [handover example](../examples/meaning_handover/README.md) | Restricted record preservation and inspectable changes; no human comprehension result. |
| Consensus | [consensus/](consensus/), [arena example](../examples/consensus_arena_demo.py) | Bounded agreement and recovery mechanisms; not proof that agreement is true. |
| Sovereign controls | [sovereign_harness.py](sovereign_harness.py), [guard.py](guard.py) | Scoped local permission and action mechanisms. |
| Handoff | [handoff.py](handoff.py), [risk example](../examples/guarded_handoff_risk_demo.py) | Explicit transfer and admission boundaries. |

From the repository root:

```sh
python3 -m pip install -e .
lycheetah-assure --help
lycheetah-compact --help
lycheetah-handoff --help
```

Optional integrations and developer dependencies are declared separately in the
package configuration. A successful import or policy decision does not establish
that a surrounding application is safe or that its external effects occurred.
Use the [test guide](../tests/README.md), [capability guide](../33_APPLICATIONS/README.md)
and component evidence to assess the precise claim.

Created by Mackenzie Conor James Clark / Lycheetah Framework. Code terms:
[MIT licence](../LICENSE).
