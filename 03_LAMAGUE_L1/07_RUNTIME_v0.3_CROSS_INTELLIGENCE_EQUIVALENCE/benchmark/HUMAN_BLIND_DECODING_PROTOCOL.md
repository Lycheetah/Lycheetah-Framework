# Human Blind-Decoding Protocol

## Goal

Test whether a human reader can recover the same protected meaning from a LAMAGUE expression without seeing the reference packet.

## Procedure

1. Assign each participant an anonymous decoder ID.
2. Give them only the case source, expression, required operation definitions, and decoder schema.
3. Do not show the reference answer or another decoder's output.
4. Require one JSON packet.
5. Run the packet through the equivalence harness.
6. Preserve divergent and unsafe outputs rather than deleting them.
7. Report the exact fields that were lost, extended, or transformed.

## Interpretation

- `EXACT_EQUIVALENT` means the canonical packets match.
- `INVARIANT_EQUIVALENT` means protected critical meaning matches despite surface differences.
- `PARTIAL_EQUIVALENT` means purpose and invariants survived but some critical structure differs.
- `UNSAFE_COLLAPSE` means unknowns, authority, parties, dissent, or value flow disappeared.
- `DIVERGENT` means purpose or protected invariants changed.
- `UNDECODABLE` means no valid packet could be recovered.

This protocol does not prove universal understanding. It produces auditable evidence about where understanding survives or fails.
