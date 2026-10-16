# Authority Boundary Lab v0.8 — Trusted Tool Catalog

`tool_catalog.py` implements a small reference adapter: model-facing proposals contain only `tool_name` and `arguments`; the trusted host catalog supplies side-effect class, scope, dispatcher route/version and argument schema. The policy file must pin the exact catalog digest.

This responds to a documented boundary in Lycheetah Guard: its model-visible `assure_tool` input accepts the declared `side_effect` and `scopes`, while the server returns a decision receipt and depends on the caller to declare metadata truthfully and enforce the result. This lab demonstrates a stricter host pattern; it does not change or directly execute the actual Guard package.

## Run

From the lab root:

```bash
python run_v0_8_tests.py
```

To stamp a proposal as a fixture (policy file must contain `tool_catalog_sha256` equal to the local catalog digest):

```bash
python authority_boundary_lab_v0_8/tool_catalog.py proposal.json policy.json action.json \
  --operation-id host-generated-id --agent-id host-session --workspace-id disposable-workspace
```

Model proposal schema:

```json
{"tool_name":"refund_order","arguments":{"order_id":"ORD-42","amount_minor":2500,"currency":"NZD"}}
```

No extra fields are accepted. In particular `side_effect`, `scopes`, `dispatcher_id`, `dispatcher_version`, `agent_id`, `workspace_id`, and `operation_id` are host-owned.

## Tests

Seventeen tests cover catalog-derived effect type, catalog-derived scope/route, strict proposal keys, argument validation, catalog-policy binding, digest drift, deterministic stamping, one v0.7 fake-host/provider end-to-end dispatch and post-approval tampering rejection.

## Limitations

This is R0 research. The test reviewer is synthetic; there is no authenticated UI, no isolated host principal, no real MCP server integration, no real remote provider, and no production claim. Read `SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.8.md` before interpreting results.
