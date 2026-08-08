# lamague-codec

### Lossy compaction with a provable floor

Compression optimises bytes and is indifferent to which bytes. This codec is
indifferent to bytes and opinionated about which fields.

It compacts a structured record while making it **structurally impossible** to
drop the parts that make a decision accountable — what remains unknown, who holds
authority, who is affected, who dissented, how to recover the prior state — and
gives you a hash that proves to a third party they survived.

```python
from lamague_codec import encode, decode, critical_hash, safety_violations

encode(packet)            # refuses if a protected unknown has no recovery path
critical_hash(packet)     # proof the ten accountability fields survived
decode(encode(packet))    # == packet, exactly
```

A protected unknown with no recovery path is a **validation error**, not a
warning. The packet will not encode at all.

---

## Why this is not a compressor

The headline number below is 33.8% against minified JSON. That is modest, and
nobody is short of compressors. The number that matters is the other one:

```text
exact full-packet round trips                36 / 36
critical-hash preserved                      36 / 36
constructed protected-loss mutations caught  324 / 324
```

Ten fields form the *critical projection* — the subset that must survive:

```text
purpose · claim · unknowns · invariants · authority
participants · affectedParties · dissent · valueFlow · recovery
```

`critical_hash()` hashes canonical JSON of that projection alone, so a consumer
who never sees the original record can still verify the projection came through
compaction unchanged, without trusting whatever did the compacting.

### Who has this problem

- **Agent context compaction.** Every long-running agent summarises its own
  history to fit a window, and the fields most worth keeping are the ones a
  summariser finds least quotable. See `examples/agent_state_compaction.py`.
- **Regulated record-keeping.** EU AI Act Art. 12 requires lifetime logging;
  Art. 11 requires documentation that stays accurate. Logs get rotated,
  summarised and tiered to cold storage, and nothing in the usual toolchain
  distinguishes a byte you may drop from one you may not.
- **Clinical and incident trails.** The differential considered and rejected,
  the consent boundary, the escalation declined.

---

## Install

```bash
pip install ./03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
```

**No runtime dependencies.** Stdlib only, by design — a guarantee that ships
with a dependency tree is a guarantee with someone else's failure modes in it.

```bash
python3 examples/agent_state_compaction.py    # the invariant, the proof, the boundary
```

---

## Measured headline

```text
Structured packets                           36
Dictionary training                          24
Held-out packets                             12
Exact round trips                            36 / 36
Constructed mutation matches                 324 / 324
Held-out warm reduction vs minified JSON     33.8%
Held-out cold reduction including codebook   30.7%
Dictionary break-even vs compact L1          3 packets
```

## Run

```bash
python src/benchmark.py
python -m unittest discover -s tests -v
```

## Encode

```bash
python src/cli.py encode packet.json --codebook corpus/codebook.json -o packet.lmgc
```

## Decode

```bash
python src/cli.py decode packet.lmgc --codebook corpus/codebook.json -o restored.json
```

## Read first

1. `reports/BENCHMARK_REPORT.md`
2. `docs/CLAIM_BOUNDARY.md`
3. `article/ARTICLE_DRAFT.md`

## Status

```text
Reversible structured codec        WORKING
Training-only dictionary            WORKING
Held-out benchmark                  COMPLETE
Exact full and critical receipts    COMPLETE
Protected-loss mutation suite       COMPLETE
Unrestricted prose compression      NOT CLAIMED
External human/model validation     NOT YET RUN
```

**The last two lines are load-bearing.** The codec operates on *declared*
structured packets — it does not infer a packet from unrestricted natural
language, the benchmark corpus is synthetic and structured, and mutation
accuracy is measured on constructed deletions rather than adversarial model
output. `docs/CLAIM_BOUNDARY.md` states the limits in the module's own words.

---

## Licence and attribution

MIT. Author: Mackenzie Conor James Clark, Ōtepoti / Dunedin, Aotearoa New
Zealand. Part of the [Lycheetah Framework](https://github.com/Lycheetah/Lycheetah-Framework),
though this package depends on nothing in it.
