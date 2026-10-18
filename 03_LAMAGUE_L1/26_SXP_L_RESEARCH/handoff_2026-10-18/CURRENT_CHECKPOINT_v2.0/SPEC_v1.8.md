# SXP-L × LAMAGUE v1.8 — Conversational Repair Forge

**Status:** Experimental, bounded language extension. No independent human or acoustic validation. No claim of superior comprehension or agent safety.

## Aim

v1.7 had two authoring shortcuts: `?k` for requesting clarification and `~k` for self-correction. Those shortcuts were **not spoken SXP-L**. v1.8 proposes two pronounceable speech-act roots with explicit scopes, carrying the distinction through reversible artifacts without changing any v1.7 historical files.

The inherited `mi liva ti` remains untouched.

## New provisional roots

| Root | CV syllables | Provisional IPA | Speech act |
|---|---|---|---|
| `kelunaro` | ke-lu-na-ro | /ke.luˈna.ɾo/ | Speaker asks the original speaker to clarify a prior turn; embedded content is a suggested interpretation, **not asserted** |
| `remakivo` | re-ma-ki-vo | /ɾe.maˈki.vo/ | Speaker declares a correction to **their own** prior turn; the new content is speaker-asserted, and the original remains in history |

Both pass the existing CV word-shape parser and a one-edit-distance screen against previously implemented root inventories. No spoken listening study has tested whether these are distinguishable.

## Controlled utterance grammar

The `people` and `speaker > addressee :` notation is **authoring/document metadata**, not an alleged spontaneous spoken SXP-L phrase. Within it, the repair *utterance* is comprised of pronounceable SXP-L tokens.

```ebnf
native_document = "people", 2..16 distinct declared names, NEWLINE, 1..35 turns;
turn            = speaker, " > ", addressee, " : ", utterance;
utterance       = inherited_v1_4_leaf | clarification | correction;
clarification   = "mi kelunaro gonape", prior_turn_id, "dimotu bakumo",
                  explicit_name_proposition, "tesavo devora";
correction      = "mi remakivo gonape", prior_turn_id, "dimotu bakumo",
                  inherited_v1_4_leaf, "tesavo devora";
```

`prior_turn_id` uses the unchanged inherited spoken ID mapping (`taba` = turn 1). The nested proposition is itself terminated with `devora`. `bakumo` and `tesavo` delimit its scope. Whitespace and line layout are canonical.

### Scope safeguards

- **Clarification:** the questioner must be distinct from the original speaker and must address the original speaker. **The proposed inner interpretation must use explicit named participants instead of `mi` or `ti`.** This prevents those pronouns from silently changing viewpoint from the quoted earlier speaker to the questioner. The clarification does not assert that the proposed interpretation is true or was actually said.
- **Correction:** only the original speaker can correct a still-active, uncorrected prior turn. The correction must address the same addressee as that prior turn so `ti` stays bound to the same person. It appends a new turn and marks the original superseded; it never deletes the original or authenticates the speaker.
- **Unresolved third person:** inherited v1.4 `sivena` ambiguity logic remains active. No recency guessing.
- **Authorization:** utterances, including permission words, do not create verified capabilities or execute tools.

### Example

```text
people maka nara
maka > nara : mi liva ti devora
nara > maka : mi kelunaro gonape taba dimotu bakumo gonape maka dimotu luma gonape nara dimotu devora tesavo devora
maka > nara : mi remakivo gonape taba dimotu bakumo mi rava ti devora tesavo devora
```

Interpretation: Maka says *I love you*. Nara asks whether Maka meant *Maka misses Nara* (proposed, not established). Maka later declares a correction of their first turn to *I reconnect with you* (reported correction, not an objective state change). The example deliberately challenges whether a repair can change the content while retaining its conversational history; it is **not** a natural conversation quality benchmark.

## Round-trip artifacts and meaning-loss ledger

The authoritative v1.8 executable produces:

1. `conversation.sxp18` — canonical native utterances with actual repair roots.
2. `conversation.studio` — v1.7 shorthand projection; a `kelunaro` line becomes `?k`, and a `remakivo` line becomes `~k`.
3. `conversation.sxh` — canonical v1.4 transcript, **not sufficient by itself to reconstruct repair intentions**.
4. `conversation.sxpl17.json` — inherited v1.7 semantic sidecar with same SHA-256-bound `.sxh`.
5. `conversation.sxpl18.json` — explicit new roots, reference IDs, speaker-attribution status, and source digests.

`verify_bundle()` regenerates all artifacts from the native source and rejects any mismatch. Hashes detect accidental or unsanctioned edits **within a trusted application context**, not identity forgery; an attacker controlling all files can replace them together. No signatures are issued.

## Known gaps / v1.9 questions

- The native utterance form is still long; outer speaker metadata is not a natural spoken conversation.
- v1.8 does not yet permit free pronouns within proposed clarification content. This is a deliberate fail-closed restriction until we implement explicitly bound hypothetical viewpoints.
- Embedded full discourse, quotation, partial self-interruption, hedging, sarcasm, prosody and gesture remain unsupported.
- Meaning checks are deterministic code tests; no participants or independent human comprehension results exist for v1.8.
- `kelunaro` and `remakivo` are **proposed**, not permanently canonized roots. A human listening study and phoneme confusion audit could overturn them.
- The grammar inherits the limitations of v1.4: this is not a universal human conversational parser.
