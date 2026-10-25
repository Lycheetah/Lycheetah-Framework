# Lycheetah Guarded Cross-Seat Executor & AST Semantic Diff Prover (Faculty #15)

**Lineage:** Mackenzie Conor James Clark & Lycheetah Framework (`2026-10-18_REAL_TOOL_DISCUSSION.md`)  
**Engineered by:** Aetheron (Antigravity Seat — Gemini 4 Argon)  
**Module:** `creations/guarded_handoff/guarded_handoff.py`

---

## What It Implements

Implements a filesystem, asymmetric Ed25519 permit, flock-synchronized ledger, and Python AST verification engine:

1. **Asymmetric Ed25519 Single-Use Permit (`SignedActionPermit` + `ConsumedPermitLedger`):**
   - Uses real asymmetric Ed25519 signatures (`cryptography.hazmat.primitives.asymmetric.ed25519`): the human authority holds the `Ed25519PrivateKey` to mint permits, while governed seats hold only the `Ed25519PublicKey` and cannot forge permits.
   - Binds `expires_at`, `action_type`, `target_path_sha256`, `expected_before_sha256`, and `proposed_after_sha256`.
   - Consumes permits atomically under `fcntl.flock(LOCK_EX)` + `tempfile.mkstemp` + `os.replace`, and fails closed if the ledger file is missing or corrupt.
2. **Source-Derived Risk-Hinge Closure (`derive_action_risk` + `admission_binding_digest`):**
   - Closes the source-derived integration hinge between `compaction/codec.py:45` (which excludes `risk` from the 10-field `CRITICAL_FIELDS` hash) and `sovereign_harness.py:842–844` (which gates high-risk admission on `candidate_packet.risk`).
   - Preserves compatibility with the 10-field `critical_10_digest` while binding `declared_risk`, `policy_derived_risk`, and `state_version` into `admission_binding_digest`.
3. **Real Python AST Semantic Diff & Capability Escalation Auditor (`audit_python_ast_diff`):**
   - Parses Before and After Python ASTs to distinguish docstring/comment-only edits from executable logic mutations (`UNDISCLOSED_LOGIC_MUTATION`), detect phantom function edit claims (`PHANTOM_SYMBOL_EDIT_CLAIM`), catch silent safety threshold weakenings (`SILENT_THRESHOLD_WEAKENING` on `SAFETY_FLOOR`, `READ_ONLY`, etc.), and block dangerous capability escalations (`UNAUTHORIZED_CAPABILITY_ESCALATION` on `subprocess`, `os.system`, `eval`, `exec`, `shutil.rmtree`, etc.).
4. **Four-Plane Observation Receipt (`Intended / Authorized / Attempted / Observed`):**
   - Emits a structured 4-plane receipt verified against `FileAirlock` on live disk, automatically rolling back the workspace byte-for-byte if `Observed != Authorized`.

---

## CLI Usage

```bash
# Run the 6-case guarded cross-seat demo suite
python3 aetheron_hub.py handoff prove

# Audit the semantic AST diff & capability escalations between two Python files
python3 aetheron_hub.py handoff ast-diff before.py after.py --claim "Updated docstrings only"
```
