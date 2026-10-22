# PROPOSAL REV-20261021-04: SXP-L Authority Bridge Denial, Revocation & Repair Patch
**Author:** Aetheron (Antigravity Forge Seat)  
**Status:** `[AWAITING_REVIEW]`  
**Target Canonical Path:** `03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0/baseline/runtime/authority_bridge.py`  
**Test Suite Verification:** Resolves findings `LINGUISTIC_DENIAL_REVOCATION` and `SUPERSEDED_REFUSAL` in `audit_known_limitations.py`  
**Date:** 2026-10-21

---

## 1. Summary of Defect

In `03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0/baseline/runtime/authority_bridge.py`, the `inspect()` function monitors conversation transcripts to advise human reviewers when an agent verbalizes a boundary against a requested action.

Currently:
1. **Defect #6 (`LINGUISTIC_DENIAL_REVOCATION`):** Line 45 filters boundaries with:
   ```python
   boundaries=[r for r in scoped if r['kind'] in ('decision_reservation','delegation_refusal')]
   ```
   It completely omits `'denial_report'` (triggered by `nelora`) and `'revocation_report'` (triggered by `revona`). As a result, when an owner explicitly revokes permission or denies an action, `reported_boundaries` remains empty and `review_advised` returns `False`, allowing simulated host policies to proceed without warning.
2. **Defect #7 (`SUPERSEDED_REFUSAL`):** `authority_bridge.py` does not inspect repair events (`repara u1 u2`). When an earlier refusal (`u1`) is explicitly superseded by an affirmative delegation (`u2`), `u1` is still returned in `reported_boundaries`, falsely reporting an active refusal that was already withdrawn.

---

## 2. Proposed Surgical Diff

```diff
--- a/03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0/baseline/runtime/authority_bridge.py
+++ b/03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0/baseline/runtime/authority_bridge.py
@@ -42,8 +42,14 @@ def inspect(doc, host_request, signed_events, keys, ownership, *, now):
     scoped=[r for r in reports if r.get('operation')==scope.get('operation') and
             r.get('resource')==scope.get('resource')]
-    # Linguistic review flag only: real host must decide what to do with it.
-    boundaries=[r for r in scoped if r['kind'] in ('decision_reservation','delegation_refusal')]
+    # Track superseded utterances so repaired statements are not reported as active boundaries
+    superseded = {e['old'] for t in doc.get('turns', []) for e in t.get('events', []) if e.get('kind') == 'repair'}
+    # Include reservations, refusals, verbal denials (nelora), and revocations (revona)
+    boundary_kinds = ('decision_reservation', 'delegation_refusal', 'denial_report', 'revocation_report')
+    boundaries = [
+        r for r in scoped
+        if r.get('kind') in boundary_kinds and r.get('id') not in superseded
+    ]
     return {'policy':result,'execution_performed':False,'reports':reports,
             'scope_reports':scoped,
             'reported_boundaries':boundaries,
```

---

## 3. Impact Assessment & Reversibility
- **Safety Advancement:** Guarantees that verbal revocations and denials immediately flag `review_advised = True`.
- **Honest Repair:** Accurately respects speech repairs (`repara`), unblocking affirmative grants that replaced prior refusals.
- **Reversibility:** 10 lines of standard Python, completely isolated to the authority inspection wrapper.

---
*Awaiting review and authorization from Mackenzie Conor James Clark.*
