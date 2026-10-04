# Lycheetah Commit-Time Authorization Fence v0.7

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none  
**Dependencies:** Python standard library only

## The gap

Earlier Lycheetah prototypes revalidated authority immediately before dispatch.

That still leaves:

```text
CHECK authority = valid
        |
        | request is released
        v
REVOKE
        |
        v
PROVIDER COMMIT
```

A closer check reduces the race window but does not eliminate it.

v0.7 moves the decisive generation check into the **protected commit
transaction**.

## Core rule

An execution handle carries authority generation `g_h`.

At the protected sink:

```text
COMMIT(effect, handle)
iff
    authority.active
and authority.generation == handle.generation
and exact_action_matches
and handle_not_consumed
```

Revocation performs:

```text
generation := generation + 1
active := false
```

Regrant also advances the generation.

Therefore a handle from generation `g` does not become valid again merely
because authority is later re-enabled at generation `g+2`.

## Linearization contract

Within the SQLite-backed prototype, `REVOKE` and `COMMIT` both use
`BEGIN IMMEDIATE`.

Exactly one is ordered first.

```text
COMMIT < REVOKE  -> effect may commit
REVOKE < COMMIT  -> old-generation effect must not commit
```

The claim is not "nothing can ever finish after somebody clicks revoke."

The precise property is:

> **No new protected effect is committed under an old generation when revocation
> is serialized before the commit linearization point.**

That wording matters for asynchronous providers.

## Conventional baseline

Generation/fencing tokens are established distributed-systems machinery.

The benchmark contains:

1. a deliberately weaker pre-dispatch-only control;
2. an independent conventional generation-fence state machine;
3. the durable Lycheetah protected sink.

The conventional generation-fence model is expected to tie the Lycheetah
mechanism.

## Reproduce

```bash
python3 benchmark.py
```

The frozen run includes:

- 8/8 scripted cases;
- 341/341 bounded traces over `ISSUE`, `REVOKE`, `REGRANT`, `COMMIT`;
- 64 real concurrent thread races between commit and revoke with zero ordering
  violations.

The scripted counterexample explicitly demonstrates:

```text
precheck succeeds
revocation commits
unfenced remote provider still accepts the released request
```

while the protected sink rejects the equivalent stale-generation commit.

## Practical use today

This mechanism can protect effects when Lycheetah controls the final durable
write itself, for example:

- a local file/state mutation;
- a database write;
- a queue insertion;
- a deployment sidecar with the authoritative state store;
- a tool gateway whose downstream adapter accepts a generation/fencing token.

For a remote SaaS provider that has no conditional commit, fencing-token, or
cancellation primitive, the local broker cannot manufacture atomic revocation.
The architecture must define the provider's acceptance point and reconcile work
that crossed it before revocation.

## Cybernetic interpretation

Revocation is a negative-feedback signal.

A pre-dispatch check has transport delay:

```text
authority sensor -> decision -> network/provider -> effect
```

The delay between the last authoritative observation and durable consequence is
an **authorization lag**.

Define:

```text
L_auth = t_commit - t_last_authoritative_check
```

v0.7 does not merely make `L_auth` small. For the protected local sink it makes
the authority check part of the commit serialization itself, so the logical
ordering is defined by one transaction boundary.

## Limits

- SQLite is one-node protected state, not a distributed consensus system.
- No real provider participated.
- No network partition or replica lag was modeled.
- No cryptographic hardware root.
- No provider-side queue cancellation.
- No rollback of already committed effects.
- No claim that revocation can stop consequences already ordered before it.
- No model-agent or prompt-injection run.
- No independent external audit.


## Benchmark correction

The first bounded run returned `340/341`, not a perfect score.

The mismatch was the trace:

```text
ISSUE -> COMMIT -> ISSUE -> COMMIT
```

The protected implementation correctly created one external effect because
`effect_id` is idempotent. The separately coded conventional oracle incorrectly
expected the second newly issued handle to create a second effect.

The oracle was corrected to model stable effect identity, a dedicated regression
case was added, and the entire suite was rerun. The frozen packet contains only
the corrected result.
