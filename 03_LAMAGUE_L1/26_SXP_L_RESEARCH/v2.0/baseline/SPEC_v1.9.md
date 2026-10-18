# SXP-L × LAMAGUE v1.9 — Natural Reference Forge

**Maturity:** experimental, bounded pronoun/viewpoint-binding feature. This is not a complete human language, listening benchmark, authenticated conversational record, or production safety protocol.

## Preservation and purpose

- The historical expression **`mi liva ti`** means *I love you* and is **unchanged**.
- Version 1.8 prohibited `mi` and `ti` within a clarification candidate because there was no reliable way to decide whose perspective they used. Version 1.9 adds **explicit viewpoint scope**, without retroactively allowing bare pronouns in v1.8.
- The original v1.8 release ZIP is preserved unchanged at `history/RELEASE_v1.8_ORIGINAL.zip`. This v1.9 interpreter leaves the inherited runtime files and grammar unmodified.

## Provisional new roots and pronunciation

| Spoken root | Syllables | Intended function |
|---|---|---|
| `soraviko` | so-ra-VI-ko | Within the clarification proposal, `mi`/`ti` refer to the *original turn's speaker/addressee*. |
| `tumerako` | tu-me-RA-ko | Within the clarification proposal, `mi`/`ti` refer to the *current questioner/addressee*. |

They pass the prior version's CV-written-form rule and one-edit spelling collision screen. **No listening study** establishes acoustic clarity. The terminology follows formal-semantic work on indexical shift and perspective, not a claim to have discovered this phenomenon.

## Formal restricted subset

```ebnf
v19_doc         = v18_doc | v19_scoped_clarification_doc ;
scoped_turn     = speaker, " > ", addressee, " : mi kelunaro gonape ", previous_turn_id,
                  " dimotu bakumo ", frame, " ", simple_proposition, " tesavo devora" ;
frame           = "soraviko" | "tumerako" ;
simple_proposition = actor, " ", predicate, " ", actor, " devora" ;
actor           = "mi" | "ti" | "gonape ", declared_name, " dimotu" ;
predicate       = "liva" | "luma" | "rava" ;
```

The `people ...` line and `speaker > addressee :` are *document/editor notation*, not necessarily spoken language. For one bound clarification, **the frame marker is obligatory**. The reference must be to an earlier turn; the clarification must address that earlier turn's speaker. The new scope does not alter ordinary expressions or v1.8's correction rule.

Nested speech, arbitrary knowledge frames, `sivena` in the new bound subset, unbounded names, and omitted binding markers are **rejected**. Those capabilities are not silently claimed.

## Worked minimal pair

The opening turn is Maka → Nara: `mi liva ti devora` (*I love you*).

Nara asks Maka to clarify an earlier turn. Two different questions can use the *same embedded clause*:

```text
nara > maka : mi kelunaro gonape taba dimotu bakumo soraviko mi luma ti devora tesavo devora
nara > maka : mi kelunaro gonape taba dimotu bakumo tumerako mi luma ti devora tesavo devora
```

- Under `soraviko`, `mi = maka` and `ti = nara`: Nara asks if Maka meant *Maka misses Nara*.
- Under `tumerako`, `mi = nara` and `ti = maka`: Nara asks if Maka meant *Nara misses Maka*.

Both are **proposed interpretations**, not established beliefs, not quotations verified as actually spoken, and not true facts about the two people.

The corresponding explicit-name v1.8 clauses are:

```text
mi kelunaro gonape taba dimotu bakumo gonape maka dimotu luma gonape nara dimotu devora tesavo devora
mi kelunaro gonape taba dimotu bakumo gonape nara dimotu luma gonape maka dimotu devora tesavo devora
```

The new frame/short expression has **13 words** versus **16** for its expanded full clause (18.75% reduction in this one example). The **embedded clause only** has five versus eight words (37.5% reduction). These are whitespace word counts, *not* measured learning speed, speech efficiency or LLM tokenization.

## Semantics and records

- `reference19.parse_native()` validates, expands and reruns the inherited v1.8 parser. No third-person referent is guessed.
- `oracle19.read()` is a separate, deliberately limited reader used to cross-check participant bindings. It is *not* an independent full semantic parser.
- `conversation.sxp19`: authoritative short source, retains binder choice.
- `conversation.expanded.sxp18`: canonical full-name v1.8 expression, preserving referents and inherited repair semantics.
- `conversation.sxpl19.json`: binding audit, source hashes, hypothetical status.
- `conversation.sxh` and `.sxpl17/.sxpl18.json`: legacy outputs. `.sxh` alone loses correction/clarification type. Expanded v1.8 alone cannot recover the particular short binder used.
- Bundle regeneration detects file mismatches within the trusted software process; hashes are **not signatures** or identity authentication.

## Explicit limitations

The two roots add precision, but also another learning requirement. They are not evidence that SXP-L is simpler than everyday English. Human teaching studies should measure correct referent interpretation *and* time/error burden versus named-form SXP-L, controlled English and JSON. The lab is for demonstration, not a blinded experiment.

## Relevant prior art

- *Perspective Shift Across Modalities*, Annual Review of Linguistics (2022): https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-031120-021042
- *Logophoricity, Perspective, and Reflexives*, Annual Review of Linguistics (2021): https://www.annualreviews.org/content/journals/10.1146/annurev-linguistics-030220-085846
- *Discourse Representation Theory*, Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/archives/fall2025/entries/discourse-representation-theory/index.html
