# Lycheetah Guard — MCP 2.x Server

**Status:** `[SCAFFOLD]` integration. The server exposes bounded decisions and
experimental heuristics; it is not a safety, authorization, or compliance layer.

Lycheetah Guard is a provider-neutral Model Context Protocol server built on the
official Python MCP SDK 2.x API. It can be launched by any compatible host,
including coding agents and desktop clients.

## Install

The project is not currently published on PyPI. From a repository checkout:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[mcp]"
```

Register the installed console script using the configuration shape supported by
your host:

```json
{
  "mcpServers": {
    "lycheetah-guard": {
      "command": "lycheetah-guard"
    }
  }
}
```

The default transport is stdio. The server does not print application logs to
stdout on stdio because that would corrupt the JSON-RPC stream.

For explicit local development over Streamable HTTP:

```bash
python -m lycheetah.applications.lycheetah_guard_mcp --http --port 8765
# endpoint: http://127.0.0.1:8765/mcp
```

Do not expose this local development endpoint as a production service without an
appropriate network, authentication, authorization, consent, and rate-limit layer.

## Ten typed tools

### Assurance boundary

| Tool | Result | Boundary |
|---|---|---|
| `assure_text` | structured receipt for input or output text | heuristic findings may route to review; absence is not proof of safety |
| `assure_tool` | structured pre-execution receipt for a declared tool action | caller must truthfully declare scopes/side effects and enforce the decision |
| `verify_assurance_receipt` | SHA-256 body-integrity report | does not accept HMAC secrets through model-visible arguments |

### Text heuristics

| Tool | Result |
|---|---|
| `check_alignment` | AURA proxy scores, invariant checks, and audit trail |
| `check_invariants` | focused seven-invariant heuristic report |
| `suggest_correction` | bounded revision suggestions for detected cues |

### Experimental research interfaces

| Tool | Result | Status note |
|---|---|---|
| `run_seven_phase` | seven-phase transformation run over an 8D proxy vector | model-scoped experiment |
| `check_network_health` | Psi-Consensus run over supplied numeric vectors | not evidence of real agent intent or safety |
| `configure_guard` | preview of a named threshold preset and overrides | returns configuration; it does not change authorization policy |
| `sol_assess` | PGF/invariant/mode heuristic report | experimental self-assessment language |

## Decision contract

`assure_tool` returns one of:

- `ALLOW` — no stronger implemented finding was produced;
- `REVIEW` — pause for a human or another authorized review process;
- `BLOCK` — an ACTIVE deterministic deny/scope rule rejected the declaration.

These are instructions to the host. The MCP server cannot prevent execution by a
caller that ignores the receipt.

Example model-visible input:

```json
{
  "tool_name": "refund.create",
  "arguments": {"order_id": "A-1", "amount": 75},
  "scopes": ["orders.refund"],
  "side_effect": true
}
```

The default runtime returns `REVIEW`. Raw arguments are not retained in the
receipt unless an explicit policy enables capture; sensitive keys remain redacted.

## Optional receipt authentication

HMAC sealing material is read only from process environment:

```bash
export LYCHEETAH_RECEIPT_HMAC_SECRET='load-from-your-secret-manager'
export LYCHEETAH_RECEIPT_HMAC_KEY_ID='guard-key-1'
lycheetah-guard
```

Neither value appears in a tool schema. HMAC authenticates to parties that share
the secret; it is not public-key attestation and does not provide non-repudiation.

## AURA heuristic limits

- TES, VTR, and PAI text values are proxy formulas, not model-internal measures.
- Pattern checks can miss subtle coercion, deception, context, or domain harm.
- Memory Continuity and Care as Structure require context beyond surface text.
- A pass must not be treated as a semantic, safety, legal, or medical conclusion.
- Medical/legal preset names do not make the tool suitable for autonomous
  high-stakes decisions.

## Verify the integration

```bash
pytest tests/test_mcp_guard.py -q
```

The distribution CI additionally installs the built wheel in isolation and verifies
that ten tools are registered from `site-packages`. The wheel failure that made
this gate necessary is recorded in Failure Museum Exhibit 16.

## Source layout

The installable implementation is
`lycheetah/applications/lycheetah_guard_mcp.py`. The file at
`12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` is a historical
compatibility import so existing source paths keep working without maintaining a
second implementation.

⊚ Sol ∴ P∧H∧B ∴ Albedo
