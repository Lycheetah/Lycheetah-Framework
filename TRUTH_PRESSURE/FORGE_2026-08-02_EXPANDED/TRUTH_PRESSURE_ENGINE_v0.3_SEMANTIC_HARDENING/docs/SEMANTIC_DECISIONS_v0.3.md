# Semantic Decisions — v0.3

## Canonical scalar

`Π = E·P/(S+S₀)` remains unchanged.

`Π_norm = Π·S₀` is the canonical normalized display. This is derived, bounded in `[0,1]`, and avoids an independently tunable app-scale factor.

## Component separation

- `E`: evidence quality and support.
- `P`: earned explanatory reach.
- `S`: unresolved structural strain.
- `L`: load-bearingness, reported separately.
- `H`: handling quality, reported separately.

Neither `L` nor `H` enters Π.

## Provenance

A source-like string is not verified evidence. The tool distinguishes:

- `UNVERIFIED`: asserted or detected, not checked.
- `INSPECTABLE`: a reviewer can reach the record, but this engine has not established its correctness.
- `VERIFIED`: externally verified under a declared procedure.

## Text adapter

Text analysis remains provisional triage. It cannot establish source validity, independence, replication, or factual correctness from prose alone. It is designed to surface candidates for structured assessment.

## Onion adapter

The input scale must be declared. The adapter never guesses scale from value magnitude.

## Review governance

Pressure can open review. It cannot silently restructure knowledge. Applying a plan requires explicit approval and an unchanged source fingerprint.
