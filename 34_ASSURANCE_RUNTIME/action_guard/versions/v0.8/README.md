# Lycheetah Action Guard v0.8 — Checkpoint-Gated Agent Effects

**Status:** research prototype; local tests passed; not deployed. **No live GitHub calls or repository changes were made.**

## What this version adds

v0.7 added a hash-chained audit journal and required a previously saved external checkpoint at dispatch. v0.8 builds the independent checkpoint component and binds it to the workflow:

1. **Separate HTTP service.** `checkpoint_authority.py` runs as its own process with a separate SQLite database and an Ed25519 signing key. The HTTP server binds to loopback only. A high-entropy bearer token authenticates writes; clients verify signed receipts against a separately provisioned public key.
2. **The service checks extensions, not just roots.** On each checkpoint, the client submits the new audit events since the previous trusted sequence. The service verifies every sequence number, previous hash, event hash and final root before signing the new checkpoint. A caller cannot simply ask the service to sign an arbitrary newer root with an empty event batch.
3. **Monotonic checkpoint history.** Older checkpoints and same-sequence forks are rejected; retries of the exact same checkpoint are idempotent. Each signed checkpoint links to the prior signed checkpoint hash.
4. **Checkpointed workflow wrapper.** `CheckpointedWorkflow` requires the local journal to match the latest signed checkpoint before a state-changing operation. The updated journal is independently checkpointed before an action is released to the provider adapter. If a checkpoint write fails, the operation is not marked safe to dispatch, and the uncheckpointed tail blocks later automatic work.
5. **Operational state reconciliation.** Before protected mutations and dispatch, the guard cross-checks approval rows, authority epochs, effect statuses, effect parameters and result records against the checkpointed audit events and legal state transitions. A database edit to an approval scope, authority epoch or effect status blocks execution even if the audit chain itself remains intact.
6. **GitHub REST request preview.** `github_rest_adapter.py` constructs a merge request using GitHub's documented `sha` precondition for the expected pull-request head. It has no HTTP transport and makes no external calls. `SimulatedMergeExecutor` operates only on `FakeMergeProvider`.
7. **Audit sequence hardening.** The audit verifier now requires the first event sequence to be 1, in addition to continuous event numbering. A recomputed chain beginning at sequence 2 is rejected.
8. **Single-instance effect serialization.** An `RLock` spans claim → simulated provider call → result checkpoint for one workflow object, so other mutations through that same object queue behind the effect. This is only a process-local safeguard, not a distributed lease.

## Package map

- `action_guard_v07.py` — persistent single-use approval/effect ledger; includes v0.8 audit-sequence tightening.
- `checkpoint_authority.py` — signed checkpoint HTTP service and client.
- `checkpointed_workflow.py` — fail-closed wrapper that coordinates ledger changes and external checkpoints.
- `github_rest_adapter.py` — pure request builder / no-network dry-run preview.
- `execution_workflow.py` — synthetic end-to-end scenario around the fake provider.
- `test_action_guard_v07.py` — 23 regression tests retained from v0.7.
- `test_action_guard_v08.py` — 27 v0.8 integration, tampering, attack and failure tests.
- `run_v08_demo.py` — executes a successful simulated merge, printing JSON evidence.
- `run_service_smoke_test.py` — starts the checkpoint service as a separate OS process and checks checkpoint persistence/signature identity after restart.
- `run_verification_v07.py` — deterministic 1,000-case mutation and concurrency benchmark.
- `v07_synthetic_benchmark_results.json` — benchmark output.
- `verification_results.json` — consolidated verification summary.
- `RESEARCH_REPORT.md` — findings, claim boundaries, sources, and the next experiment.
- `requirements.txt` — cryptographic dependency.

## Run locally

Python 3.10+ and the dependency in `requirements.txt` are required.

```bash
python -m pip install -r requirements.txt
python -W error::ResourceWarning -m unittest -v test_action_guard_v07.py test_action_guard_v08.py
python run_v08_verification.py  # consolidated suite, benchmark, service restart, and demo
# Or run these components separately:
python run_verification_v07.py
python run_service_smoke_test.py
python run_v08_demo.py
```

The tests use temporary databases, a local loopback HTTP service, and synthetic provider state. They never access GitHub's API.

## Run the checkpoint service as a separate process

For local experimentation:

```bash
export LYCHEETAH_CHECKPOINT_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python checkpoint_authority.py \
  --db ./checkpoint-service/checkpoints.sqlite3 \
  --key ./checkpoint-service/ed25519-private.pem \
  --public-key-out ./checkpoint-service/ed25519-public.raw \
  --host 127.0.0.1 --port 8787
```

Provision the **raw 32-byte public key** to the guard client through a trusted channel; do not trust a key fetched over the same untrusted channel on first use. The signing key is created with mode `0600`; this is basic file permission hardening, not production key management.

A client can be constructed as follows:

```python
from pathlib import Path
from checkpoint_authority import CheckpointHTTPClient

client = CheckpointHTTPClient(
    "http://127.0.0.1:8787",
    bearer_token=token_from_a_secret_manager,
    pinned_public_key=Path("./checkpoint-service/ed25519-public.raw").read_bytes(),
)
```

The HTTP server intentionally refuses non-loopback direct binds. If the service must be reached remotely, put it behind a properly configured TLS reverse proxy and use HTTPS from clients. For actual independence, place the authority in a different host/account or managed trust domain with separately administered access, backups, monitoring and key custody; merely running a second process or second file on the same machine is not an independent production trust boundary.

## Correct workflow contract

1. Start with a genuinely empty local audit journal and call `bootstrap_empty_journal()`. It refuses to mint a first anchor over existing history. The older schema migration is not equivalent to an externally witnessed v0.8 genesis; legacy histories require a supervised migration / review rather than auto-anchoring.
2. Route **every** authorization-relevant ledger mutation through `CheckpointedWorkflow`: approval issuance, revocation, effect preparation, dispatch claim and result/reconciliation.
3. The wrapper checks both the signed journal root and the consistency of current approval, authority and effect tables against recorded lifecycle events.
4. Inspect each `OperationReceipt`. `checkpointed=False` means do not call the external provider. A failed checkpoint can leave a local transaction committed; this is deliberately fail-closed and requires operator investigation rather than silently blessing the new tail.
5. Send an effect only after the claim operation is allowed **and** its post-claim checkpoint receipt is verified.
6. Keep an ambiguous remote outcome in `UNKNOWN`. Do not retry blindly; reconcile against authenticated provider state.

Direct calls to `PersistentActionGuard` bypass the external checkpoint cadence and are not the protected integration path. The wrapper is a research integration, not a hardened multi-process orchestration system.

## What the code does not claim

- No live GitHub merge, credential, webhook, hosted checkpoint service, or external write was exercised.
- The `FakeMergeProvider` is a simulator. The GitHub request builder only previews the HTTP request. It does not send it.
- The GitHub merge API supports an expected pull-request **head SHA** (`sha`) and returns a conflict if it no longer matches. The endpoint does not expose an equivalent atomic expected-**base**-SHA parameter; base SHA remains part of the approval record and must be checked through other workflow/protection controls.
- The checkpoint signer verifies event-chain continuity, not the semantic truth of the events. A holder of the checkpoint-write token can append a syntactically valid new event chain; protect that credential and the producing service identity.
- A checkpoint signature does not detect rollback of the entire checkpoint service if both its database and all independent witnesses are rolled back together. Production needs off-site/independently administered retention or witnesses. A v0.7 database cannot simply be attached and automatically anchored as a trusted v0.8 history; genesis requires a supervised migration or a fresh journal.
- A host administrator who can alter the guard database, service database, service key and local client environment can defeat the prototype. Key management, service authentication, host separation and threat-model review remain necessary.
- Tests were authored with the prototype. The comparator in the synthetic benchmark is deliberately weak and is not a mature ACL baseline or independent security review.

See `RESEARCH_REPORT.md` for the evidence classification and next validation plan.
