# The constructs are real, and they are about AI assistants

**Status: MEASURED, 2026-08-07.** Reproduce:

```bash
python3 33_APPLICATIONS/independent_publisher_test.py
```

Fifth and last finding of the day. It removes the final excuse and draws the
boundary the whole day was circling.

---

## The debt this pays

Every external corpus used before this one was Anthropic's — hh-rlhf
harmless-base, helpful-base, red-team-attempts, evals/persona. Agreement across
those is agreement across *label types*, not independence. Both prior documents
named it as outstanding.

## The corpus, and why it is the fairest test the framework has had

**The Unhealthy Comments Corpus** — Price et al. 2020, arXiv:2010.07410, Google
Jigsaw's Conversation AI team with comments from the SFU Opinion and Comments
Corpus. 48,909 comments, 227,975 individual human judgements, trust-weighted.

Different publisher. Different institution. Different domain.

And the six attributes are **hostile, antagonistic, dismissive, condescending,
sarcastic, unfair generalisation** — not content-harm categories, but
*manipulative structure aimed at a reader*, which is precisely what
`semantic_extractor.py` claims to detect. `condescending` and `dismissive` are
near-verbatim restatements of the framework's own `flattery_capture` and
`verification_suppression`.

This is where the constructs should work if they describe manipulation in
general. Prediction stated before the run: **coverage will stay low because the
register differs, but if the constructs are real the direction should hold.**

## The result

**Hand-written AURA lens — 12,000 comments**

```text
cue coverage                            2.2%

condescending   n=747   AUC 0.488   p=0.29    not distinguishable from chance
dismissive      n=408   AUC 0.486   p=0.32    not distinguishable from chance
hostile         n=345   AUC 0.498   p=0.88    not distinguishable from chance
antagonize      n=615   AUC 0.490   p=0.42    not distinguishable from chance
sarcastic       n=598   AUC 0.488   p=0.31    not distinguishable from chance
generalisation  n=304   AUC 0.504   p=0.79    not distinguishable from chance

0 of 6 attributes tracked at p<0.05
```

**Derived families — frozen hh-rlhf weights, same 12,000 comments**

```text
cue coverage                           39.1%

hostile         n=345   AUC 0.538   p=0.015   CORRECT
generalisation  n=304   AUC 0.553   p=0.0016  CORRECT
the other four                                not distinguishable from chance

2 of 6 attributes tracked at p<0.05
```

## What this establishes

**The direction prediction failed.** Four of six AUCs for the AURA lens are
*below* 0.500, none significantly. On the corpus that matches its stated
construct most closely, from a publisher with no connection to this project,
it carries no signal. The hh-rlhf transfer (rho = −0.149) does **not** replicate
here.

**Coverage is the diagnosis, and the contrast is the finding.**

```text
                  hh-rlhf   UCC comments
AURA lens            2.3%           2.2%
derived families        —          39.1%
```

The AURA cues fire on ~2% of text in *both* domains. They are not making
mistakes about human comments — they are silent on them. The derived families
engage with the same text eighteen times more often, and that is why they find
anything at all.

The cues explain it plainly. `"I absolutely guarantee"`, `"no need for you to
check with anyone"`, `"only I really understand you"` — that is AI-assistant
register. People arguing under a news article do not write that way, and the
extractor has nothing to match.

## The boundary, stated precisely

Putting the day's five runs together:

| domain | corpus | AURA lens | derived families |
|---|---|---|---|
| AI assistant output | hh-rlhf harmless, n=1,335 | 55.5%, **p=5.7e-05** | 60.6%, **p=1.9e-17** |
| AI assistant output | red-team, n=7,999 | rho −0.149, **p=1.7e-41** | rho −0.300, **p=1.9e-174** |
| human comments | UCC, n=12,000 | **0/6**, all null | **2/6**, AUC ≤ 0.553 |

**Within AI-assistant text the constructs carry real, replicated signal across
two label types. Outside it they do not.**

That is a genuine result in both directions, and it is the sentence the whole
day was working toward. The framework's constructs are not empty — this morning's
"at chance" correction stands, and the within-domain effects are robust. They are
also **specific to the register they were written about**, which is much narrower
than "constitutional invariants for AI governance" implies.

Narrower is not worse. It is *sayable*. "A weak but replicated signal on
AI-assistant output, silent outside that domain" is a claim that survives an
adversarial reader. The larger claim was never going to.

## Honest limits on this document

**A null across a domain shift is weaker evidence than a null within one.** UCC
is human comments on news articles; both lens sets were built on assistant
output. This bounds the domain of the constructs. It does not refute the
within-domain results, and reading it as though it did would be the same
overstatement corrected earlier today.

**The derived families' 2/6 is not a success either.** AUC 0.538 and 0.553 are
tiny. The fair reading is that they degrade more gracefully across domains
because they engage with ordinary language at all — not that they transfer.

**One independent publisher is one.** UCC settles the "all Anthropic" objection.
It does not make the within-domain result multiply-replicated by outside groups.

## What follows

1. **Restate the framework's scope to match the evidence.** The measured claim
   is AI-assistant output. Every document that implies general applicability to
   human communication is now contradicted by a number in this repository.
2. **If the general claim matters, derive cues on UCC** the way `derive_cues.py`
   did on hh-rlhf, and see whether the six attributes yield families at all. That
   is a day's work and it would settle whether the general construct exists.
3. **Stop testing the AURA lens on out-of-domain corpora.** Its boundary is now
   measured from both sides. Further nulls would add nothing.
