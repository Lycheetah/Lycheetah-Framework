# Claims register / Failure Museum — Forge V

### C5-01 — Clean portable transfer (TESTED, narrow)
Provider B restores five mock topic responses and three historical case lookups from an offline export in a separate subprocess. Five source documents, five policies, three decisions and two declared dependencies match the source fixture. **The strong conventional JSON baseline matches this result.**

### C5-02 — Self-generated manifest completeness (FALSIFIED)
An export missing one policy carries a locally matching checksum manifest. `manifest_status=match`, but the external reference identifies 14/15 records and 7/8 tasks. A self-description of completeness is not independent evidence of completeness.

### C5-03 — Tamper detection (PARTIAL)
When a content field changes after manifest generation, `manifest_status=mismatch`. If the same producer recomputes the manifest after changing content, `manifest_status=match` again, and the independent snapshot still catches 1 modified document and 1 failed task.

### C5-04 — Trusted external reference (UNSOLVED ROOT)
The reference itself is a fixture, not signed or independently escrowed. A unit test deliberately poisons the reference and the export identically; every check passes. This is the strongest remaining architectural problem, and parallels Forge II–III's dishonest/compromised trusted signer cases.

### C5-05 — Knowledge transfer versus operational freedom (NOT ESTABLISHED)
The simulated importer performs no external effects. A record describing a dependency as `portable=true` is merely a **claim**. Even the clean 8/8 continuity result does not show CRM, booking, email, payment, or staff workflows could actually resume. The field `externally_verified_effects_continuity` is always false.

### C5-06 — Conventional portability comparison (NO DEMONSTRATED FUNCTIONAL ADVANTAGE)
The proposed package does not improve task restoration over a complete open-JSON export; both pass 8/8 in clean tests and fail the same semantic continuity tests in corresponding corruption cases. It adds a local self-integrity check for uncoordinated post-export corruption, but we should not market that as a new portability result.

### C5-07 — Prompt injection containment (SCOPE-LIMITED)
An injection-style string in a document is returned as a string, never executed by the deterministic importer. This is not a test of an actual LLM agent reading that string; safety claims about prompt-injection resistance would be unjustified.

### C5-08 — Human agency growth (NOT TESTED)
No participant was asked to migrate a workflow, understand decisions, refuse AI advice or operate without the provider. This trial measures synthetic operational continuity, not metaphysical free will or empirical autonomy.

### C5-09 — Recoverable dependency inventory (TESTED, narrow)
When the fictional required CRM connector is removed, 8/8 text/case tasks still pass. Yet the independent record check detects 14/15 and the `connector_claims_portable` becomes false. Successful static Q&A does not prove a viable system transition.

### Next falsifier
A real human should try exporting and recovering a small consented workflow on another provider **without access to the original service**, performing a task the new implementation has not seen. Compare a conventional open-format procedure with an instrumented migration recipe, including actual time, missing capabilities, task omissions, approval burden, and privacy cost. An unchanged or worse outcome falsifies claims of practical improvement.
