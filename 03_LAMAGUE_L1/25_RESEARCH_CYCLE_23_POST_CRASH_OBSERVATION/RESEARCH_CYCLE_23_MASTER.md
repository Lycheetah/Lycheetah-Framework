# LAMAGUE Cycle 23 — From claimed commits to evidenced outcomes

**Research status:** local controlled Linux experiment, 18 October 2026. Not production-grade, not independently audited.

## Research question
After an actual namespaced publisher dies between the first and second file commit, can we bind separately observed file outcomes to the original signed grant, preserve them in a tamper-evident journal, and have a witness reject rollback?

## Five distinct states (do not collapse them)
1. **Intended** — what the human's purpose or final-state description said. Cycle 23 does not independently resolve semantic intent.
2. **Authorized** — the exact two-file plan signed in an Ed25519 execution grant. The witness verifies the original grant signature, binding and expiry.
3. **Attempted** — the Cycle 13 process was started under its experimental namespace execution controls. Attempted does not imply success.
4. **Observed** — a trusted *post-run recovery observer* opens each approved destination without following symlinks and checks size and SHA-256. Distinguishes MATCH, ABSENT, MISMATCH and unsafe path/type.
5. **Independently evidenced** — HMAC-chain integrity and a separate-key checkpoint are verified for the observer's report. The witness independently checks the *report's integrity* but does not independently see or attest the filesystem commit. It is a witness of reported observations, not the actual commit.

## Implementation
`src/cycle23.py` creates an authenticated append-only **per-file observation** record set bound to `digest(binding)` of the original signed grant and exact plan. Records carry a sequence number, prior-record hash, approved relative path and observation result. The local witness `witness_action()` first verifies the original Ed25519 grant, expiry and plan binding, then checks journal HMACs and anchors its head to a separately keyed checkpoint using inherited Cycle 17 storage helpers. A rollback of the valid first-record prefix is recognized after the full two-record head has been anchored.

The transaction uses Cycle 22's real test-only `publisher_after_first_commit` injected `os._exit(92)`, inside the previously tested namespace publisher. The observer runs **only after the execution returns**, with the publisher stopped; it does not modify the original publisher. No automatic retry is permitted.

## Actual results
The local regression suite has **8/8 passing tests**. The real crash output in `reports/actual_crash_observed.json` reports one approved file `MATCH`, one `ABSENT`, a non-success execution status, an authenticated witness anchor, a matching witness check, and `auto_retry=false`. The normal case has two `MATCH` files. Additional tests refuse changes to an authenticated observation, altered signature, duplicate/unapproved records, truncated events, and rollback of a valid authenticated prefix.

**Interpretation:** We can now report a separately anchored, per-file **post-execution observation history**, reducing reliance on a single transaction-level label. This does not close the gap between real-world commit and witness registration.

## Conventional baseline
The crypto (Ed25519, HMAC-SHA256), filename-safe observation, fsync and witness checkpoint are conventional mechanisms. A conventional system can adopt precisely the same code and produce the same outcomes. No controlled comparative advantage for LAMAGUE has been established in this cycle.

## Trust boundaries / limitations
- The observer runs in trusted local Python; the witness is called in-process in this experiment, not independently deployed as a separate user-owned persistent service.
- Journal key and witness key are supplied by the local test controller; the test controller could forge or erase records.
- The journal attests **what the observer wrote**, not that the publisher itself committed at the claimed instant. Observation must run after publisher quiescence; concurrent hostile mutation and TOCTOU remain untested.
- HMAC does not prove independence or prevent a key holder from rewriting history. Checkpoint separation helps only while its key and storage remain protected.
- Post-crash observation may itself be interrupted, leaving incomplete evidence; full outage and re-observation protocol remain unspecified.
- This is NOT atomic multi-file publication, a tested power-loss durability guarantee, arbitrary hostile-code containment, complete production security, or independent validation.
- Do not use executable source or injected fault hooks for production files.

## Cycle 24: the sharp next experiment
Move the recovery observer and witness to separately owned long-running services, give the witness independently obtained filesystem observation capabilities, test the crash window between *actual commit* and *receipt acknowledgment*, and compare the complete workflow against an equivalent conventional policy/audit stack. A clean final result must label exactly which process saw which event and who could forge its evidence.

## Reproduction
From the archive root, run `python -m unittest discover -s tests -v`. Run `PYTHONPATH=src python src/cycle23.py` for a new disposable real-crash example. The frozen latest local examples are in `reports/`. Verify `SHA256SUMS.txt` with `sha256sum -c SHA256SUMS.txt`.
