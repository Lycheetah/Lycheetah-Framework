# X post drafts — reversible compression

**Every number below was verified on 2026-08-07 by:**

```bash
python3 33_APPLICATIONS/compression_vs_gzip.py
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
python3 src/benchmark.py && python3 -m unittest discover -s tests
```

**Mac fires launches.** These are drafts.

---

## ⚠ READ FIRST — what changed about the pitch

The package's existing `article/X_POST.md` leads with:

> 33.8% smaller than minified JSON

**Do not post that as the headline.** Measured today on the same 36 packets:

```text
gzip -9, per packet          54.7% smaller than JSON
LAMAGUE L1D alone            34.8% smaller than JSON
```

**gzip beats the codec by ~20 points using a standard-library call from 1992.**
That reply arrives within ten minutes and it is correct.

The good news is that the real result is stronger, and it is two things:

```text
LAMAGUE L1D + gzip -9        67.0% smaller than JSON
JSON + gzip -9               54.7% smaller than JSON
                             -> L1D+gzip is 27.0% smaller than JSON+gzip
```

The format is **a preprocessing step that makes gzip work better**, not a rival to
it. The schema removes redundancy gzip would otherwise have to discover.

And the part no compressor does at any ratio: **324/324 protected-field deletions
detected.**

---

## SHORT POST (the one to fire)

> Most compression asks: how many bytes can I remove?
>
> For a decision record that's the wrong question. A shorter version can look
> efficient while quietly dropping the parts that made the decision accountable —
> who dissented, who's affected, what's still unknown, how to undo it.
>
> So we built a codec that treats those fields as protected, and tested whether
> deleting them is *detectable*.
>
> 36 structured packets. 9 deletion attacks each:
> drop dissent · drop affected parties · drop unknowns · drop authority ·
> drop recovery · drop value flow · unprotect an unknown · remove a guard ·
> change an invariant
>
> **324/324 caught. 36/36 exact round trips.**
>
> On size, the honest numbers: gzip alone beats our codec alone (54.7% vs 34.8%).
> But they compose — codec + gzip hits 67.0%, which is 27% better than gzip on
> raw JSON.
>
> Compression was never the interesting part. gzip will happily compress a record
> with the dissent deleted and tell you nothing.
>
> Corpus is synthetic, n=36, structured packets not free prose. Limits are in the
> repo, written before the result.

---

## LONG-FORM ARTICLE

### Compression that refuses to forget

Every summary loses something. The interesting question is which losses you can
detect.

Send a decision up three levels of an organisation and watch what evaporates
first. Not the conclusion — that survives. What goes is the dissent. The list of
people affected. The things nobody had worked out yet. The rollback plan. By the
time it reaches the top it reads as clean and settled, and the parts that would
have made someone hesitate are gone. Nobody lied. It just got shorter.

General-purpose compression is indifferent to this. gzip optimises bytes and has
no opinion about which bytes. Delete the dissent field and gzip compresses the
result slightly better and reports nothing wrong, because nothing is wrong by its
standards.

So we tried a different design. Declare a fixed set of fields that make a
decision accountable — purpose, claim, risk, evidence with provenance, protected
unknowns, invariants, authority, participants, affected parties, dissent, value
flow, recovery, horizon, yield — and build a codec where removing one of them is
a detectable event rather than an editorial choice.

**The test.** We froze 36 structured packets across 18 domains, trained a
dictionary on 24, and held 12 back. Then we constructed nine deletion attacks and
ran every one against every packet:

```text
DROP_DISSENT             DROP_AFFECTED_PARTIES    DROP_UNKNOWNS
DROP_AUTHORITY           DROP_RECOVERY            DROP_VALUE_FLOW
UNPROTECT_UNKNOWN        REMOVE_GUARD_OPERATION   CHANGE_INVARIANT
```

**324 of 324 were classified as expected.** Eight collapse the packet's safety
and are refused; changing an invariant is flagged as divergent rather than
collapsed, because it is a different failure. Round-trip fidelity held at 36/36
exact, with the critical-field hash preserved on all 36.

**Now the size numbers, including the one that doesn't flatter us.**

```text
canonical minified JSON       76,482 bytes        —
LAMAGUE L1D (codec alone)     49,850           34.8%
gzip -9, per packet           34,631           54.7%
LAMAGUE L1D + gzip -9         25,272           67.0%
```

gzip alone beats our codec alone by about twenty points. If the pitch were
"better compression", the pitch would be over — and anyone could establish that
in one line of Python.

But the codec and gzip remove *different* redundancy. The schema strips field
names and repeated record shapes before gzip runs; gzip then finds byte patterns
in what remains. Composed, they reach 67.0%, which is **27% smaller than gzip on
raw JSON**. That is the honest compression claim: this is a preprocessing step
that makes a general compressor work better, not a replacement for one.

Held-out packets — the twelve the dictionary never saw — come in at 33.8% for the
codec alone with a warm dictionary, 30.7% once the codebook's own bytes are
charged against it. The codebook pays for itself after three packets.

**What this does not earn.** The corpus is synthetic and n=36. The codec operates
on declared structured packets and does *not* infer them from free prose. The
mutations are constructed, not adversarial — nobody has attacked this who wanted
it to fail. Nothing here proves the protected field set is complete, and no human
has rated whether a decoded packet means the same thing to a reader. Those limits
were written into the package's `CLAIM_BOUNDARY.md` before the benchmark ran, and
they are the reason the numbers above are worth anything.

**Why bother.** Because "we compressed the record" and "we compressed the record
and can prove the uncomfortable parts survived" are different sentences, and only
one of them is checkable. Everything in the first sentence is a promise.

Reproduce it:

```bash
git clone <repo>
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
python3 src/benchmark.py
python3 -m unittest discover -s tests     # 19 tests
```

---

## THINGS NOT TO SAY

- ❌ "Beats gzip." It does not. It composes with gzip.
- ❌ "33.8% compression" as a headline. True, and beaten by a 1992 standard-library call.
- ❌ "Semantic compression" without qualification — it compresses *declared
  structured packets*, not meaning in general.
- ❌ "Tamper-proof" / "cryptographic". It detects *constructed* deletions under a
  declared schema. It is not a security guarantee and nobody adversarial has tried.
- ❌ Any claim about LAMAGUE as a language. This package earns nothing about that,
  and its own lineage note says the operator sets here and in the core line are
  disjoint.

## THINGS YOU CAN SAY WITHOUT FLINCHING

- ✅ 324/324 constructed protected-field mutations correctly classified, 9 classes
- ✅ 36/36 exact round trips, 36/36 critical-hash preserved
- ✅ L1D + gzip is 27.0% smaller than JSON + gzip on the frozen corpus
- ✅ Held-out 33.8% warm / 30.7% cold including codebook cost
- ✅ 19/19 tests pass; reproduced from a cold clone on a second machine today
- ✅ Limits published before the result, in the package
