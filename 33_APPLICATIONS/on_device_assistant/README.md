# Lycheetah on-device assistant — skeleton

**`[SCAFFOLD]` · 2026-11-06 · PROPOSED.** Creator: Mackenzie Conor James Clark / Lycheetah Framework.

> The model thinks on your device. Lycheetah decides what may leave it, shows you exactly what
> that is, and keeps a receipt.

## Try it

```sh
pip install -e .                                   # from the repository root
cd 33_APPLICATIONS/on_device_assistant
python3 assistant.py --stand-in "What's the weather in Dunedin?"
```

With a real local model (needs [Ollama](https://ollama.com) running on your machine, and a model
pulled, e.g. a 3–4B one). **Not run in this session; UNVERIFIED:**

```sh
python3 assistant.py --model <ollama-model-name> "What's on at the Octagon this weekend?"
```

When the model wants the internet, you see the exact action, rendered from the bytes the gateway
hashes, with the model's own words labelled as unverified:

```
--- The assistant wants to leave your device ---
Tool: web.fetch
  url = "https://example.org/"
Side effect: yes
Agent says (not verified): 'look this up'
Action hash: 825029da2548dda5
Allow this? [y/N]
```

## What is real here

- `ApprovalLayer` is an Approval Integrity Suite adapter, and it is the layer the app uses, so
  `tests/test_on_device_assistant.py` runs the suite on the app's own code path: **10/10**.
- A refused request never reaches the network; an approved one runs once; a dropped connection is
  **UNKNOWN**, and the model is told not to assume it happened. MEASURED in this session: in a
  sandbox that blocks the fetch, the live demo returned UNKNOWN and the answer said so.
- Receipts and the ledger are written to a local workspace printed at the end.

## What is not

- No model is trained, bundled, or benchmarked. `--model` talks to Ollama; it was not run here.
- One tool (`web.fetch`, https only). Every outbound request is treated as a side effect, which is
  stricter than needed for reads: an UNKNOWN read also blocks its exact retry until reconciled.
- Terminal only. A phone app is a port (Swift/Kotlin + SQLite), not a resize.
- The NZ-hosted receipt witness (`CheckpointHTTPServer`) is not wired in yet.

## Next

The business plan for three jobs — writing, summaries and local logistics — is in
[VERTICALS_PLAN.md](VERTICALS_PLAN.md), with its own [pre-registered benchmark](BENCHMARK_PREREG_VERTICALS_2026-11-06.md).

1. Run the [pre-registered benchmark](BENCHMARK_PREREG.md): blind-rated quality on everyday NZ
   tasks against a frontier model.
2. Wire the checkpoint authority to an NZ-hosted witness that stores receipt hashes only.
3. A desktop UI on top of the same `Assistant` class; then a phone port.

Research behind the choices: [ON_DEVICE_NZ_RESEARCH_2026-11-06.md](../ON_DEVICE_NZ_RESEARCH_2026-11-06.md).
