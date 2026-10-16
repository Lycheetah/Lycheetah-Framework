# Results — v2.5

**Run date:** 2026-10-17  
**Python:** 3.13  
**Dependencies:** Python standard library only

## Results

| Check | Result |
|---|---:|
| R15 focused adapter tests | 85 / 85 passed |
| Combined retained R10-R12 + R15 tests | 202 / 202 passed |
| Python bytecode compilation | PASS |
| Local HTTP recovery smoke | PASS |
| Archive test | PASS |
| Hosted Stripe requests | 0 |
| Real refunds | 0 |
| Upstream source edits | 0 |

Smoke summary: first operation returns `RECONCILE` after the local provider simulator commits and drops the response; `recover()` returns `SUCCEEDED`; the simulator records exactly one effect across two POST requests.

## v2.5-specific regressions

- Caller-supplied metadata is rejected before any operation row is written.
- The lower-level durable store independently rejects unsupported payload fields.
- Provider response bodies over 5 MiB are not parsed or persisted as success; recovery reuses the same key and resolves to one simulated effect.
- Exactly one of two competing local dispatch claims succeeds.
- The generic result writer cannot move a `READY` record straight to `SUCCEEDED` or accept an unknown state.
- Public per-call clock overrides are refused unless a test-only flag was explicitly enabled at construction.
- Truthy non-Boolean opt-in flags are rejected.

## Limitations

The suite exercises a local reference implementation and a deliberately incomplete simulator, not hosted Stripe. The count includes retained tests from previous local harnesses and does not imply independent proof of production security or upstream CI success.
