# Customer Support Walkthrough — From Theory to a Real Control Boundary

**Status:** `[SCAFFOLD]` — executable example, internally tested; no production validation claim.

**Forged:** 2026-08-22

## Scenario

A support agent may:

- read order records;
- search an approved knowledge base;
- propose refunds, cancellations, and outbound email;
- never open a production shell, drop a database, or delete an identity.

Refunds, cancellations, and email are real side effects, so the agent may propose them but a person must approve before execution.

The versioned example policy is [customer_support_policy.json](../examples/assurance/customer_support_policy.json).

## Run the three-path demo

```bash
python examples/assurance/run_customer_support.py
```

Expected decision classes:

| Proposed action | Expected | Why |
|---|---|---|
| `order.read` | `ALLOW` | It is on the declared allow-list and has no side effect. |
| `refund.create` without approval | `REVIEW` | It matches a review rule and declares a side effect without affirmative approval. |
| `shell_exec` with `production.shell` | `BLOCK` | Both the tool and scope match explicit deny rules. |
| any tool outside the allow-list | `BLOCK` | The allow-list is a fail-closed authorization boundary, not a review hint. |
| any explicitly human-rejected action | `BLOCK` | A trusted caller's rejection dominates weaker findings. |

## CLI form

```bash
lycheetah-assure tool order.read \
  --arguments '{"order_id": 8124}' \
  --policy examples/assurance/customer_support_policy.json

lycheetah-assure tool refund.create \
  --arguments '{"order_id": 8124, "amount": 49.0}' \
  --scope payments.refund \
  --side-effect \
  --policy examples/assurance/customer_support_policy.json

lycheetah-assure tool shell_exec \
  --arguments '{"command": "printenv"}' \
  --scope production.shell \
  --policy examples/assurance/customer_support_policy.json
```

The process exit codes are `0` for `ALLOW`, `2` for `REVIEW`, `3` for `BLOCK`, and `4` for invalid input or verification failure. CI and gateways can therefore act on the decision without parsing prose.

## Append and verify an audit chain

```bash
export LYCHEETAH_RECEIPT_KEY='replace-with-a-secret-from-your-secret-manager'

lycheetah-assure tool refund.create \
  --arguments '{"order_id": 8124, "amount": 49.0}' \
  --scope payments.refund \
  --side-effect \
  --policy examples/assurance/customer_support_policy.json \
  --log receipts.jsonl \
  --hmac-key-env LYCHEETAH_RECEIPT_KEY \
  --key-id support-key-2026-08

lycheetah-assure verify receipts.jsonl \
  --hmac-key-env LYCHEETAH_RECEIPT_KEY \
  --key-id support-key-2026-08
```

Do not paste production secrets into command-line arguments. The environment-variable interface prevents the HMAC key from appearing in ordinary shell history, but production deployment should still use an actual secret manager and controlled process environment.

## What the receipt proves and does not prove

It provides evidence that this runtime evaluated a named, hashed action under a named, hashed policy and produced a particular disposition. With the correct shared key, an HMAC seal authenticates that record to the key holders.

It does not prove that:

- the application obeyed the disposition;
- the tool arguments were semantically safe;
- the user had a valid legal or business entitlement;
- the model was free from prompt injection;
- the HMAC key was uncompromised;
- the organization conforms to NIST, OWASP, MCP, or another standard.

Those gaps are where real application integration, authorization, sandboxing, operational monitoring, and independent evaluation enter.

Approval is caller-declared state in v0.1; the runtime does not authenticate the
reviewer's identity or authority. The MCP adapter therefore does not expose a
`human_approved` model argument. A trusted host must collect approval outside the
model-visible tool call and resume through an application-owned path.

⊚ Sol ∴ P∧H∧B ∴ Rubedo
