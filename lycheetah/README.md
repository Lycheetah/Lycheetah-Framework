# Python package — public interfaces and bounded controls

**Guide updated:** 19 October 2026. **Source version:** 1.3.0 in
[pyproject.toml](../pyproject.toml). Component contracts and research packets have
their own versions.

This directory owns the public Python wrappers and the assurance, compaction,
consensus, sovereign-control and handoff modules. Foundational engines live in
[12_IMPLEMENTATIONS](../12_IMPLEMENTATIONS/README.md): the package configuration
maps those sources into `lycheetah.core`, `.applications` and `.experiments`.
Edit the owning source rather than creating a second engine copy.

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
