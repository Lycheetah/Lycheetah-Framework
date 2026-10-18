# ARGON — Independent adversarial audit of SXP-L v1.9

Your job is to **falsify unsupported claims**, not to promote the release.

1. Inspect the immutable v1.8 historical ZIP; verify its SHA-256 against the original shared artifact.
2. Run the exact commands in README, and recompute the 71-test tally. Review the 400 generated cases for grammar coverage and tautological checks.
3. Study `reference19.expand19` for viewpoint capture, silent binding changes, nested-scope smuggling, malformed names, old correction ownership, and unsupported third persons.
4. Independently implement viewpoint binding from the specification. **Do not import `reference19.py`.** Try to generate minimal counterexamples that the provided restricted reader misses.
5. Audit `conversation.sxp19`, the v1.8 expansion, legacy transcript and semantic sidecars for nonrecoverable information. Test mutually consistent forged files to demonstrate the limits of hashes.
6. Challenge whether `soraviko` and `tumerako` are learnable and acoustically distinguishable; compare explicit-name SXP-L, controlled English, and existing formal referent systems, not only a naive baseliner.
7. Evaluate whether three-verb simple clauses are representative. They probably are not. Report coverage explicitly.
8. Preserve `mi liva ti` and all legacy releases. Suggest a v2.0 path only after categorizing factual defects and design choices separately.

**Do not** claim 80/80 synthetic agreement proves human comprehension, actual listener advantage, authentication, or robust agent safety. No external actions are enabled by this software.
