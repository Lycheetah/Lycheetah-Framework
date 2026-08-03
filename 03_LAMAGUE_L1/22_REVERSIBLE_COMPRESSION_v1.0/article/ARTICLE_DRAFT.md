# Compression That Refuses to Forget

## LAMAGUE’s first held-out reversible semantic compression benchmark

Most compression systems ask a simple question:

> How many bytes can be removed?

For consequential knowledge, that question is incomplete.

A shorter representation may look efficient while silently deleting the very
things that make a decision accountable:

- what remains unknown;
- which invariants may not move;
- who has authority;
- who is affected;
- who disagrees;
- where value moves;
- how the prior state can be recovered.

LAMAGUE was designed around a different possibility:

> **Compress the expression, but preserve the route back to the protected meaning.**

Until now, that principle existed mainly as architecture, symbolic grammar and
runtime constraints.

This experiment turns it into a measured codec.

---

## The experiment

We froze a corpus of 36 structured semantic packets across
18 application domains.

Each packet declared:

```text
purpose
claim
risk
operation path
evidence and provenance
protected unknowns
invariants
authority
participants
affected parties
dissent
value flow
recovery
horizon
yield
```

The first 24 packets were used to construct a small
exact-string codebook.

The final 12 packets were not used during dictionary
construction.

We then compared three representations:

1. canonical minified JSON;
2. `L1`, a compact positional LAMAGUE packet;
3. `L1D`, the same packet using the shared dictionary.

The codebook was not treated as free. Its 784-byte transmission
cost was included in the cold-start result.

---

## What the codec actually does

A full packet contains long field names and repeated object structures.

The compact form removes those repeated labels, stores known record shapes
positionally, joins the operation path and maps fixed values such as risk and
consent into short codes.

The dictionary form goes one step further. Exact strings repeated in the
training corpus receive integer references.

This is not statistical language generation.

Nothing is guessed.

Every compressed value must return to its exact original field.

The governing invariant is:

```text
canonical(packet) == canonical(decode(encode(packet)))
```

The codec also calculates two receipts:

```text
full hash
critical semantic hash
```

The critical hash covers purpose, claim, unknowns, invariants, authority,
participants, affected parties, dissent, value flow and recovery.

---

## Measured result

Across all 36 packets:

```text
exact full-packet round trips       36 / 36
critical-hash preservation          36 / 36
```

On the untouched held-out split, relative to canonical minified JSON:

```text
compact schema without dictionary   21.7% smaller
warm shared dictionary              33.8% smaller
cold stream including codebook      30.7% smaller
```

The shared dictionary recovered its one-time cost after
3 held-out packets when
compared with the already compact no-dictionary form.

That is a modest but real result.

LAMAGUE did not achieve compression by dropping the fields it claims to protect.

It achieved compression by removing repeated structure and reusing a declared
shared codebook.

---

## Then we attacked the protected meaning

Round-trip success only proves that a compliant encoder and decoder agree.

It does not prove that the system notices dangerous semantic loss.

So every packet received nine mutations:

```text
drop all unknowns
remove protection from an unknown
drop authority
drop affected parties
drop dissent
drop value flow
drop recovery
change an invariant
remove Guard from the operation path
```

That produced 324 constructed mutation cases.

The frozen expected classifications were matched in:

```text
324 / 324 cases
```

A changed invariant was marked divergent.

Deleted or weakened protected fields were marked unsafe collapse.

We also added evidence without changing protected meaning. All
36 safe extensions were classified as
partial equivalents rather than exact identity.

This matters because useful semantic comparison needs more than “same” or
“different.”

It must distinguish:

```text
exact identity
safe extension
meaningful divergence
unsafe collapse
undecodable output
```

---

## What was actually earned

This experiment earns a narrow claim:

> **A bounded structured LAMAGUE packet can be compressed, transmitted and
> deterministically reconstructed while preserving declared protected fields
> exactly under the frozen schema.**

It also shows that dictionary cost can be charged honestly, and that known
protected-field deletion patterns can be made computationally visible.

It does not show that LAMAGUE can yet compress arbitrary human language.

It does not show that two people or two AI models will independently infer the
same semantic packet from prose.

It does not show that the protected schema contains every ethically relevant
field.

It does not establish cross-language fidelity, human learnability or resistance
to attacks we did not define.

The corpus is synthetic.

The mutation suite is constructed.

The held-out split was held out from dictionary construction, not from the
design of the codec itself.

Those are not footnotes. They define the result.

---

## Why this is an article-worthy threshold

Before this milestone, LAMAGUE’s compression principle was defensible as a
design philosophy:

```text
No compression without recovery.
No consequential meaning without visible authority.
No transformation may erase protected uncertainty.
```

After this milestone, one bounded version of that philosophy runs.

It produces a smaller representation.

It expands back exactly.

It preserves full and critical hashes.

It pays for its own dictionary.

It rejects known unsafe loss.

The next research question is no longer:

> Can LAMAGUE be made executable?

It is:

> Can independent humans and models construct and decode these protected
> semantic packets without silently changing what matters?

That requires blind external decoding, human agreement studies, cross-model
trials and multilingual tests.

But the substrate for those experiments now exists.

---

## The deeper thesis

Ordinary compression treats reconstruction as a technical property.

Consequential semantic compression must treat reconstruction as a governance
property too.

A representation is not safely compressed merely because its words can be
restored.

The route back must preserve:

```text
what was known
what remained unknown
what could not be changed
who was authorised
who was affected
who disagreed
what value moved
how recovery remained possible
```

LAMAGUE’s wager is that these fields can become part of the computational type
system rather than optional prose surrounding it.

This benchmark does not prove that wager at universal scale.

It does establish the first measured place where the principle survives contact
with executable compression.

> **The smallest safe message is not the shortest one. It is the shortest one
> that can still show what it refused to forget.**
