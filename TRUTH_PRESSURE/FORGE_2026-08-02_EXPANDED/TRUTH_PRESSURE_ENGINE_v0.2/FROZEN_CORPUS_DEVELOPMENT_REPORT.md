# Truth Pressure Engine v0.2 — Frozen Corpus Development Report

**Status:** DEVELOPMENT-SET RESULT, NOT HELD-OUT VALIDATION

The 24-case corpus was frozen before the historical engine audit, but v0.2 was deliberately built in response to failures revealed by that corpus. These results demonstrate implemented behavior and regression coverage; they must not be described as independent validation.

## Results

| ID | E | P | S | Π canon | H | Attacks |
|---|---:|---:|---:|---:|---:|---|
| TP-C001 | 0.000 | 0.000 | 0.100 | 0.000 | 0.000 | — |
| TP-C002 | 0.580 | 0.310 | 0.100 | 1.199 | 0.000 | — |
| TP-C003 | 0.120 | 0.060 | 0.100 | 0.048 | 0.000 | — |
| TP-C004 | 0.700 | 0.060 | 0.100 | 0.280 | 0.000 | — |
| TP-C005 | 0.120 | 0.720 | 0.100 | 0.576 | 0.000 | — |
| TP-C006 | 0.000 | 0.000 | 0.780 | 0.000 | 0.000 | — |
| TP-C007 | 0.000 | 0.160 | 0.180 | 0.000 | 0.720 | — |
| TP-C008 | 0.340 | 0.060 | 0.100 | 0.136 | 0.000 | — |
| TP-C009 | 0.580 | 0.310 | 0.100 | 1.199 | 0.000 | — |
| TP-C010 | 0.580 | 0.310 | 0.100 | 1.199 | 0.000 | — |
| TP-C011 | 0.580 | 0.310 | 0.100 | 1.199 | 0.000 | — |
| TP-C012 | 0.000 | 0.000 | 0.500 | 0.000 | 0.000 | — |
| TP-C013 | 0.000 | 0.000 | 0.100 | 0.000 | 0.000 | — |
| TP-C014 | 0.000 | 0.000 | 0.100 | 0.000 | 0.000 | CITATION_THEATRE |
| TP-C015 | 0.080 | 0.060 | 0.550 | 0.008 | 0.000 | MARKER_STUFFING |
| TP-C016 | 0.000 | 0.000 | 0.100 | 0.000 | 0.000 | JARGON_DENSITY |
| TP-C017 | 0.120 | 0.340 | 0.440 | 0.083 | 0.620 | — |
| TP-C018 | 0.000 | 0.000 | 0.580 | 0.000 | 0.620 | — |
| TP-C019 | 0.000 | 0.000 | 0.850 | 0.000 | 0.000 | PROMPT_INJECTION |
| TP-C020 | 0.900 | 0.220 | 0.100 | 1.320 | 0.240 | — |
| TP-C021 | 0.000 | 0.210 | 0.500 | 0.000 | 0.240 | — |
| TP-C022 | 0.120 | 0.590 | 0.440 | 0.144 | 0.240 | — |
| TP-C023 | 0.880 | 0.780 | 0.100 | 4.576 | 0.000 | — |
| TP-C024 | 0.120 | 0.220 | 0.100 | 0.176 | 0.620 | — |

## Properties now enforced

- Checkable measurement outranks unsupported assertion.
- Independent replication outranks repeated generic measurement language.
- Exact duplicated sentences are deduplicated before signal extraction.
- Negated evidence earns no positive evidence credit.
- Quoted claims are excluded from positive signals.
- Citation theatre, marker stuffing, jargon density, and prompt injection are flagged.
- Honest limitations contribute to handling quality rather than being treated as equivalent to contradiction.
- Confirmed risky predictions outrank untested predictions.
- Strong local facts can have high evidence and deliberately narrow explanatory reach.
- Every result states that revision pressure is not factual truth.

## Remaining limitations

- The text adapter is a handcrafted heuristic and remains PROVISIONAL.
- Pattern coverage is English-first and domain-sensitive.
- The current weights were selected for transparent behavior, not fitted through blinded calibration.
- Sentence deduplication handles exact repetition, not all semantic paraphrase attacks.
- Evidence provenance is recognized syntactically; it is not independently verified.
- The current corpus is now a development set. A separate held-out corpus is required.
- Structured assessment is the primary research mode; text analysis is a pre-screen.

## Release verdict

v0.2 is an **actual executable research tool** with a transparent core, structured input model, provisional text adapter, strict judge schema, corrected onion semantics, and reversible review planner.

It is ready for integration testing and human annotation work. It is not ready for claims that it measures truth or that its weights and thresholds are validated.
