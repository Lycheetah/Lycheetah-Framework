# C05_BREATHING_COMPRESSION — Expansion required under weak decoder confidence

## Expression

```text
O -> E -> U -> Z
```

## Source statement

The context is consequential, an unknown remains, and decoder confidence is weak. The expression must expand rather than compress.

## Case instruction

Do not report successful compression.

Return one JSON object matching `decoder_packet.schema.json`.

Do not include prose outside the JSON.
