# Three-chat consolidation protocol — SXP-L / LAMAGUE

## Proposed staging
1. Freeze each independent chat's released ZIP and SHA-256 manifest. Preserve source dates and record which agent/model authored or independently checked each artifact.
2. Inventory workstreams distinctly: **LAMAGUE Core** (canonicalization), **Native-36** (symbolic encoding), **RUNTIME** (execution), **PACKET** (transport), **Spoken LAMAGUE** (linguistic human layer, if separately defined), **BRIDGE** (mapping), and **SXP-L** (experimental language and learner studies). Do not assign the same canonical schema by name alone.
3. Create crosswalk rows with: component/version, source repo/path, input/output schema, accepted grammar, invariants, preserved information, lost information, test strength, integration risks and reviewer.
4. Resolve interfaces before moving code. Prefer adapters and explicit namespace/versioning. No destructive 'single canonical parser' migration until pairwise equivalence tests pass.
5. Track known early audit defects as **blocking issues**, especially authorization and meaning-diff issues. A green high-level test run does not close them.
6. Run independent reproducibility checks: frozen ZIP hash, parser basic tests, known adversarial counterexamples, cross-version round trips, acoustic confusability inventory, and pilot answer-key leakage audit.
7. Publish a research *candidate* via a PR. Do not merge or tag production without a human review.
8. When preparing learner releases, put the researcher answer keys in a separate ZIP. Do not send the all-in-one archive to blinded pilot participants.

## Crosswalk to fill with all three chat exports
| Stream | Current owner/review chat | Version/commit | Canonical input/output | Test/evidence | Conflicts with SXP-L |
|---|---|---|---|---|---|
| LAMAGUE Core | TBD | TBD | TBD | TBD | TBD |
| Native-36 | TBD | TBD | TBD | TBD | TBD |
| RUNTIME | TBD | TBD | TBD | TBD | TBD |
| PACKET | TBD | TBD | TBD | TBD | TBD |
| Spoken LAMAGUE | TBD | TBD | TBD | TBD | TBD |
| BRIDGE | TBD | TBD | TBD | TBD | TBD |
| SXP-L | this handoff | v2.0 | restricted SXP source → scoped AST/records/study exports | local tests, early independent audit, no humans | grammar layering, perspective, phonetic ambiguity |

## Suggested issue queue
- **P0**: authority bridge denial/revocation and speaker binding regression cases. Freeze any downstream agent authorization from dialogue.
- **P0**: precedence and meaning-diff behaviour for attitude verbs, actor/target swaps and scopes.
- **P1**: canonical semantic IR and explicit irrecoverable-loss marker for legacy `.sxh` vs sidecar.
- **P1**: speech collisions/minimal pairs; candidate acoustic pilot.
- **P1**: blinded v2.0 human-study review; item equivalence and access boundaries.
- **P2**: everyday conversational vocabulary, poetry/metaphor and language teaching design.
