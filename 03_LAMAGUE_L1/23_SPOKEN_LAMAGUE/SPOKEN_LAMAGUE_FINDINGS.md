# Spoken LAMAGUE — first formal pass

**Status: MEASURED, 2026-08-07.** Reproduce:

```bash
python3 03_LAMAGUE_L1/23_SPOKEN_LAMAGUE/spl_phonology.py   # the survey
python3 03_LAMAGUE_L1/23_SPOKEN_LAMAGUE/spl.py verify      # the decodability proof
python3 03_LAMAGUE_L1/23_SPOKEN_LAMAGUE/spl.py corpus      # parse every attested sentence
```

A written language only has to be readable. A spoken one has to be **uniquely
decodable** — given a stream of syllables with no spaces, a listener must recover
exactly one morpheme sequence. That is a formal property with a classical
decision procedure (Sardinas & Patterson 1953), and it had never been run on SpL.

---

## First, the missing document

`03_LAMAGUE_L1/README.md` lists three files under **Extensions (June 2026)**:

```text
SpL-X_Spoken_LAMAGUE_Extended_v1.0.md
The_Ki-mi_Node_Research_Extensions_v1.0.md
LAMAGUE-XENOS_Operational_Mysticism_v1.0.md
```

**None of the three is in this repository.** Searched by filename and by content,
2026-08-07. `SpL-X` is referenced by six other documents, so the material existed;
what survives are the fragments those documents quote.

Everything below is therefore reconstructed from surviving sources into
`spl_registry_v0.1.json`, with each entry carrying its origin. If SpL-X v1.0 is
recovered it is authoritative and the registry must be reconciled to it.

## What SpL actually is, assembled

**79 distinct spoken forms** across 86 senses, from six documents:

| layer | count | source |
|---|---|---|
| core phonemes (∅→`vu`, A₀→`an`, Ψ→`sai`…) | 14 | `06_LAMAGUE_RAW_MATH.md` |
| lexical particles (`wi`, `ni`, `fu`, `li`, `na`) | 5 | inferred from dialogue — **never declared in any table** |
| prosodic (`-hi` whisper, `-lo` shout…) | 6 | `21_SOMA` §2.3 |
| breath (`-in`, `-ex`, `-ho`…) | 6 | `21_SOMA` §3.1 |
| gesture (`-cor`, `-pal`, `-fis`…) | 9 | `21_SOMA` §4.1 |
| spatial (`-cen`, `-edg`, `-hig`…) | 6 | `21_SOMA` §4.3 |
| death (`-ta` past, `-mem`, `-leg`, `-fro`) | 4 | `19_THANATOS` §9.1 |
| Native-36 spoken forms | 36 | `02_NATIVE36` registry, `spoken_form` field |

Plus **five attested utterances** — the only running text the language has.

## Finding 1 — Native-36's spoken layer is sound

```text
Native-36 spoken forms alone (36 glyphs)   uniquely decodable: TRUE
```

It carries two prefix relations — `di`(2) ⊂ `din`(8), `u`(Unknown) ⊂ `un`(1) —
and **survives anyway**, because prefix relations do not automatically break
decodability; only the Sardinas–Patterson test settles it. The 36-glyph spoken
alphabet is a well-formed code.

Worth stating plainly: that is careful design, and it held up under a test it was
never built to face.

The numerals are better than sound. `tan tun tin` (3,4,5) and `dan dun din`
(6,7,8) encode base-3 *phonologically* — a t-series and a d-series under vowel
gradation a/u/i, matching the registry's own "fused ternary" glosses. `taran` (9)
extends it. This is a genuine ternary phonology and no document in the corpus
points it out.

## Finding 2 — SpL core has exactly one flaw, and the source already fixes it

```text
SpL core phonemes alone (14)   uniquely decodable: FALSE   witness 'an'
```

One cause: `sai` (Ψ) is a prefix of `saian` (Ψ_inv), and the dangling remainder
`an` is itself a phoneme (A₀). So a listener hearing *saian* cannot tell
**Ψ_inv** from **Ψ then A₀**.

But `06_LAMAGUE_RAW_MATH.md` writes it `Ψ_inv → sai-an` — **with the hyphen.**
It was always a compound. Treating it as an atomic phoneme is what breaks the
code:

```text
SpL core with Ψ_inv read as the compound sai+an
   13 phonemes, uniquely decodable: TRUE
```

**The repair is to honour the hyphen already in the source.** Nothing is renamed,
added, or removed.

## Finding 3 — the two systems have never been reconciled, and that is where it breaks

Native-36 and SpL assign spoken forms independently. Nobody has written down how
they relate. Merged, the combined inventory is **not** uniquely decodable, and
every prefix collision sits on the seam:

| collision | one side | other side |
|---|---|---|
| `ka` ⊂ `kas` | Native-36 C *Cycle* | SpL ∇cas *cascade* |
| `li` ⊂ `lim` | SpL *continuously* | Native-36 L *Limit* |
| `sa` ⊂ `sai` | Native-36 S *State* | SpL Ψ *fold* |

And six outright homophones, of which three are internal to SpL:

| form | sense A | sense B | sense C |
|---|---|---|---|
| **`ta`** | prosodic *slow* | death *past* | |
| **`ki`** | core ⇈ *rise* | prosodic *fast* | |
| **`in`** | core ∞ *infinity* | breath *inhale* | Native-36 I *Invariant* |
| `an` | core A₀ *anchor* | Native-36 A *Anchor* | *(these agree — harmless)* |
| `ex` | breath *exhale* | Native-36 X *Exchange* | |
| `ya` | breath *yawn* | Native-36 Y *Yield* | |

**`ta` is live in the attested corpus.** `19_THANATOS` §9.2 has:

> `"An. Wi fla ta. ∅."` — *"Anchored. We flared [past]. Void."*

Under the same registry that sentence equally reads *"We flared slowly."* The
language's own example sentence is ambiguous.

## Finding 4 — the (C)V(N) claim is half true

`README.md` line 89:

> The SpL phonological layer — (C)V(N) syllable structure, five vowels — maps to
> the most common syllable structure across all human language families. It was
> not designed for this. It was discovered.

Measured against the assembled inventory:

- **five vowels: confirmed.** Exactly `a e i o u` are attested, no more.
- **(C)V(N): 48 of 79 forms.** It holds for the core phonemes and breaks on the
  particle layer — `bre`, `clo`, `edg`, `fla`, `pra`, `qua`, `taran`, `vai`, and
  23 others carry clusters or codas outside {n, m, r}.

The claim is true of the layer it was written about and was later extended, by a
different document, past where it holds. The typological assertion — "most common
across all human language families" — carries no citation and is not tested here.
It should be marked UNVERIFIED rather than repeated.

## A repair I proposed, and the tool refused

My first move was to make the hyphen phonologically real — a glottal stop [ʔ]
before every bound particle, which is typologically ordinary and would cost the
language nothing.

`spl.py verify` computes decodability before and after and **rejected it**:

```text
BOUND inventory (particles carry ʔ)   uniquely decodable: False   witness 'an'
RESULT: STILL AMBIGUOUS. The repair is insufficient — do not publish it as a fix.
```

The glottal boundary separates particles from roots but does nothing about
root-to-root prefixes, which is where the real damage is. The tool was built to
check the author's claims and it caught its own author's first.

The boundary marker is still worth having — it is what makes `An-hi-ta`
pronounceable as `[anʔhiʔta]` and keeps particles from being mistaken for roots.
It is just not sufficient alone, and it is now recorded as insufficient.

## What is decided and what is Mac's call

**Decided by measurement, not opinion:**
- Native-36's spoken layer is a uniquely decodable code.
- SpL core becomes uniquely decodable the moment `Ψ_inv` is read as `sai`+`an`,
  which is how the source writes it.
- The merged inventory is not decodable, and the seam is where it fails.

**Mac's call, and not attempted here:**
- Whether `ta`, `ki`, `in`, `ex`, `ya` get disambiguated by renaming, by class
  marking, or by declaring that context resolves them.
- Whether Native-36 spoken forms and SpL phonemes are one system or two. Right
  now they are two systems sharing a name.
- Whether `wi`, `ni`, `fu`, `li`, `na` — used in every dialogue, declared in no
  table — get a real entry.

The language is Mac's. This pass measured it; it did not redesign it.

## What now exists

```text
23_SPOKEN_LAMAGUE/
  spl_registry_v0.1.json     every SpL form, consolidated, each with its source
  spl_phonology.py           collisions, decodability, the (C)V(N) test
  spl.py                     working parser + speaker + IPA + decodability proof
  SPOKEN_LAMAGUE_FINDINGS.md this file
```

`spl.py parse "An-hi-ta"` returns `[anʔhiʔta]` with each morpheme glossed and
sourced. It is the first thing in the corpus that can read Spoken LAMAGUE aloud.
