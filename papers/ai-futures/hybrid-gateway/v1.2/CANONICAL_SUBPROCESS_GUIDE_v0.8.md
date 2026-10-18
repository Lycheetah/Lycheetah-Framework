# CASCADE integration boundary — Cycle 8

Canonical Lycheetah CASCADE remains an *optional local external dependency*, not copied or renamed inside this package. The SHA-pinned file at `Lycheetah/Lycheetah-Framework/12_IMPLEMENTATIONS/core/cascade_engine.py` was inspected through the connected repository with Git blob SHA `bf90a47ab17da11c0266d078fc4d74a5d95c9235` (2026-10-18). No checkout from that upstream repository was available to execute in the Cycle 8 container. **No genuine canonical CASCADE run has been claimed**.

On a trusted operator machine with the checked-out repository and NumPy installed:

```bash
python demo_cascade_isolated.py --framework-root /path/to/Lycheetah-Framework
```

The gateway serializes only the ledger's time-visible claim IDs and values with explicitly supplied weight triples and exact scope labels. A child Python interpreter (`-I`) checks the Git blob identity before running original engine classes. It returns advisory event counts and coherence. The parent keeps ledger objects, quotes, source text, complete documents, source URIs and authority flags out of the packet. No action API is exposed to CASCADE.

**Important limitations:** This is ordinary process separation, NOT sandboxing. The child process still has the parent's OS user permissions and may read/write accessible files and make network calls if permitted by its environment. Git SHA-1 identity pinning does not authenticate authorship or code safety. Runtime resource limits use a timeout and input size cap, but no filesystem, network or memory sandbox. A trusted operator must inspect/approve the upstream code, dependencies and checkout. Don't load untrusted Python just because it matches a user-supplied hash. No trust weights are synthesized by this interface, and heuristic pressure cannot authorize writes.

Test doubles are allowed in tests only by an explicit *toy* SHA pin, labeled accordingly. They prove subprocess packet mechanics but do not validate the real CASCADE algorithm.
