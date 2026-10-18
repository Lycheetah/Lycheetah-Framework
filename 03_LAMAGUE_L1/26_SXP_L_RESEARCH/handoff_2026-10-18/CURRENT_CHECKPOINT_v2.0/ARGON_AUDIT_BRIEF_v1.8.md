# Argon — adversarial SXP-L v1.8 audit

Treat v1.8 as unverified language research. Preserve `history/RELEASE_v1.7_ORIGINAL.zip` byte-for-byte. Challenge each claim; do not silently revise `mi liva ti` or historical grammar.

## Reproduce

Run `python run_v18.py examples/three_turns.sxp18 --out output` and the documented unittest invocation. Verify generated `.sxp18`, `.studio`, `.sxh`, v1.7 sidecar and v1.8 sidecar. Run the browser learner separately. Inspect the checksum manifest and compare historical archive bytes.

## Attempt to break

- Place `mi`, `ti`, `sivena` inside proposed clarifications; look for viewpoint leakage.
- Have one speaker correct another person's turn, and have an original speaker correct an earlier message addressed to someone else.
- Forge a non-prior turn ID, multiple corrections to one target, duplicate names, invalid grammar, unclosed nested scopes, long inputs, and mismatched sidecars.
- Compare the main parser against `independent_reader18.py` on cases it explicitly supports, but recognize both are local synthetic checks.
- Verify an agent cannot convert the words *trust*, *grant*, or *correct* into an actual host capability.
- Re-run v1.7 regression tests from their historical environment; do not extrapolate a full historical pass from v1.8's focused suite.

## Recommended next milestone

Design a learnable free-form clarification grammar with *explicit binding* of the viewpoint whose meaning is being proposed, without mandatory proper-name repetition. Then test its spoken intelligibility, scope confusion, and independent learner comprehension.
