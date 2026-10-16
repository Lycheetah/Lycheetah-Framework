# Proposed schema correction — v1.4

The source-derived experiment indicates the current schema and parser are not a single normative contract. Proposed changes should be applied together with the v1.3 parser patch and additional checks described below.

## 1. Replace the generic control object

Current shape in `$defs/finding.properties.controls.items`:

```json
{"type":"object"}
```

Proposed shape:

```json
{"$ref":"#/$defs/controlReference"}
```

Add this definition under `$defs`:

```json
"controlReference": {
  "type": "object",
  "required": ["framework", "control_id", "title"],
  "additionalProperties": false,
  "properties": {
    "framework": {"type":"string"},
    "control_id": {"type":"string"},
    "title": {"type":"string"},
    "url": {"type":"string"}
  }
}
```

Also set `additionalProperties: false` on `$defs/finding`, because `Finding.from_dict` already rejects unknown finding fields. Without this, schema and parser disagree in the opposite direction: the schema accepts unknown finding properties the parser rejects.

## 2. Parser checks that must ship with the schema

The v1.3 patch already rejects non-string ControlReference / Finding text, Boolean confidence, non-string evidence values, and non-string `schema_version`. The v1.4 delta should also:

- reject unknown keys in `ControlReference.from_dict` (allowed: `framework`, `control_id`, `title`, `url`);
- require `policy.sha256` to be a string matching `^[a-f0-9]{64}$` before accepting a receipt;
- keep the existing receipt body digest and optional HMAC verification semantics unchanged.

Do not change the HMAC algorithm or its covered representation as part of this patch. The current HMAC authenticates the canonical digest string. Exact-wire-byte authentication would be a separate, explicitly versioned protocol decision.

## 3. Compatibility gate

Before merging, inventory stored receipts and validate them against both old and candidate schemas. If unknown control properties were being used as informal extensions, a closed schema is a breaking change; either migrate those records or add a versioned extension mechanism rather than silently discarding fields.
