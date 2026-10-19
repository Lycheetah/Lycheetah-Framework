# Earned Light — Forge VII: Failure-Injection Laboratory

Offline, Python-standard-library prototype that **actually terminates child processes** at carefully selected cut points. A separate loopback HTTP service commits effects to its own SQLite database, while a controller keeps a distinct journal. It is a research harness, **not** an authorization service or production-ready transactional outbox.

## Run

```bash
python -m unittest discover -s tests -v
python lab.py
```

From this folder, `lab.py` creates `results/trial_results.json` and `results/trial_results.csv`.

The run includes **16 deliberately scripted dispatch/compensation scenarios**, two additional outbox retry comparator trials, and a provider kill/restart case. The test suite runs 31 local tests, including unit and separate-process tests. The provider is loopback-only, contains fictional payloads, and requires no external APIs.

- `provider.py` — separate localhost provider HTTP process; SQLite receipt/effect table and intentionally limited idempotent compensation.
- `controller.py` — revocation, durable reserve journal, fail-closed reconciliation, consequence statuses.
- `worker.py` — process killed using `os._exit(73)` at injected boundaries.
- `lab.py` — independent process orchestration, scenarios and conventional comparator.
- `tests/test_forge07.py` — 31 deterministic tests.
- `results/` — machine-readable trial outcomes and verification logs.
- `RESEARCH_PASS_07.md`, `CLAIMS_AND_FAILURES.md`, `THREAT_MODEL.md` — evidence, interpretation, failure bounds.

## Fundamental security caveats

- **No authenticated operator**. The `revoke` command is a simulated owner action, not permission enforcement; anyone able to invoke it locally can do so.
- No trusted third-party observer; a provider DB is **another system's claim**, not externally verified ground truth.
- No real network adversary, hostile provider, durable cross-service transaction, request signing, schema validation, or isolated sandbox.
- The mock provider does not implement real write conflict/version semantics or the full Forge VI recovery model.
- The provider supports idempotent operation IDs; a retry without this feature deliberately causes a duplicate effect.
- A crash after a reservation may be **unknown**, even if the lab's internal ground truth says zero effects. No premature “all safe.”
- A clean recovery report does not establish that notifications in real life can be withdrawn.

Read `CLAIMS_AND_FAILURES.md` before interpreting summary numbers.
