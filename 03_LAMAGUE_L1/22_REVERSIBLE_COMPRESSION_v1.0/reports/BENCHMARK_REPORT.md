# LAMAGUE Reversible Compression Benchmark — Measured Report

## Result

```text
Corpus                                      36 packets
Dictionary training split                   24 packets
Untouched held-out split                    12 packets
Domains                                     18
Codebook entries                            20
Codebook wire cost                          784 bytes

Exact full-packet round trips               36 / 36
Critical-hash preservation                  36 / 36

Constructed unsafe/divergent mutations      324
Expected mutation classifications matched  324 / 324
Safe evidence extensions classified partial 36 / 36
```

## Compression against canonical minified JSON

```text
All packets — L1 compact schema              21.7%
All packets — L1D warm dictionary            34.8%
All packets — L1D cold including codebook    33.8%

Held-out — L1 compact schema                 21.7%
Held-out — L1D warm dictionary               33.8%
Held-out — L1D cold including codebook       30.7%
Held-out per-packet warm range               31.8% to 35.8%
```

## Codebook break-even

Against the already compact `L1` representation, the one-time dictionary cost
is recovered after:

```text
3 held-out packets
```

Against canonical minified JSON, the cold-start dictionary stream becomes
smaller after:

```text
2 held-out packet(s)
```

## Interpretation

This benchmark establishes a working **reversible structured semantic codec**.

The strongest result is not the percentage reduction by itself. It is the
combination:

```text
smaller wire representation
+
exact deterministic round trip
+
full and critical hash preservation
+
explicit codebook cost
+
fail-visible protected-field mutation checks
```

## Limits

- The packets are synthetic and structured.
- The held-out split is held out from dictionary construction, not from codec design.
- Mutation cases are deliberately constructed.
- The benchmark does not test unrestricted prose, humans, external AI decoders,
  other languages, or unknown attacks.
