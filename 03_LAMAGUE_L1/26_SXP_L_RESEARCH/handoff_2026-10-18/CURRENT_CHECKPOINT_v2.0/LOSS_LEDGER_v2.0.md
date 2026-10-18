# SXP-L v2.0 — Meaning-Loss and Reversibility Ledger

The **canonical semantics** for the 32 fixtures are the result of the inherited restricted parser and an independently implemented limited binder reader. This is not external-world truth, nor a gold-standard semantics for arbitrary English.

| Representation | What is retained | What can be lost or obscured | Recovery path |
|---|---|---|---|
| Compact v1.9 (`.sxp19`) | Original spelling, speaker/addressee, explicit `soraviko` or `tumerako`, hypothetical clarification force | People unfamiliar with viewpoint markers may choose the wrong reference | Keep original source, formal rules and parsed sidecar |
| Expanded named v1.8 | Explicit names, action and clarification force | **Which compact binder was written** and short-form lexical history; the expansion is not invertible | Store original `.sxp19` and binder sidecar |
| Controlled English | Human-readable paraphrase with who and whom named, whether question is proposed | Original morphology, exact words, and some formal scope distinctions; natural pragmatic inference may still differ | Refer to canonical parsed source; independent human audit required |
| JSON semantic sketch | Typed fields `speaker`, `addressee`, `subject`, `object`, `status` | Surface syntax, speaker voice, original root choices, word order, original frame marker | Refer to original source and attached trace |
| Scored CSV | Case identifier, arm, response, approximate time | Stimulus itself, semantic explanation, source chain; no evidence of independent comprehension without key | Researcher file inventory + key; keep answer key private from participants |

## Negative authorization invariant

A clarification is a **proposed interpretation**, not an authenticated quotation, assertion of the embedded proposition, or executable grant. A direct reported utterance is not verified to be true. All four arms reflect that.

## Known open questions

- The paper English rendering is deliberately controlled, but not formally machine-checked as natural language.
- Auditory ambiguity and phoneme discrimination are not tested.
- Candidate words and speaker names are limited; no general dialogue resolution is shown.
- Data tampering checks in the CSV scorer are consistency checks, **not cryptographic proof of participant identity**.
- The participant HTML intentionally lacks the organizer key; giving a volunteer the complete release ZIP would compromise the intended blinding.
