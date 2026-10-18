# Integration Handoff — C006 to the Actual Lycheetah Assurance Boundary

Source repository: https://github.com/Lycheetah/Lycheetah-Framework
Pinned repo commit inspected: `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`.

## Installation/verification in a genuine checkout

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
git checkout d4a65ff64efa0a512c5c07ca64f6ec76242dd775
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -e .
# Set ET_ROOT to directory containing the six sibling cycle folders.
export ET_ROOT=/absolute/path/to/unpacked/earned_trust_archive
export PYTHONPATH="$PWD:$ET_ROOT/earned_trust_cycle_003:$ET_ROOT/earned_trust_cycle_004:$ET_ROOT/earned_trust_cycle_005:$ET_ROOT/earned_trust_cycle_006"
python "$ET_ROOT/earned_trust_cycle_002/run_framework_contract.py"
cd "$ET_ROOT/earned_trust_cycle_005"
python -m unittest -v test_real_framework_bridge_candidate
```

**DO NOT describe the above as already executed.** In this research container the bridge was run and raised `ModuleNotFoundError: No module named 'lycheetah'`. The C006 registry itself imports the byte-identical included C005 code, not any actual `lycheetah` module.

## Required implementation plan

1. Put genuine `FinalityGate`, `AssuranceRuntime` and `PersistentActionGuard` behind one *trusted*, outside-model execution boundary. Do not accept `human_approved=True` from an AI-controlled request.
2. Bind the exact `action_sha256`, `effect_id`, admitted/finalized evidence, governance `head`, and policy digest in the dispatch intent. Reject or pause any mismatch, stale challenge, untrusted anchor, or incomplete readback.
3. Persist governance transitions transactionally and append-only with trusted external head checkpoint; do not use C006's mutable, in-memory roster and signing secrets operationally.
4. Preserve uncertainty: state `UNKNOWN` after ambiguous remote writes; require provider reconciliation instead of blind retry. Remote provider atomicity is not supplied by local finality checks.
5. Add key rotation, compromise response, revocation, challenge rate limits and an independent appellate process. Avoid a single auditor causing indefinite denial-of-service.
6. Compare fairly against ordinary ACLs, signed approvals, conditional provider writes, database isolation and audited conventional policy rules. Only promote independently measured differences.

## Mandatory negative controls

- Independent signatures over one concealed CRM origin must not be mischaracterized as true independence.
- Two colluding reviewers approving a false link cannot count as a ground-truth test success.
- Signed challenge **after admission but before dispatch** must not be bypassed by cached admission status.
- Challenge after an already committed remote provider effect cannot magically cancel it.
- Stale registry `head`, missing trusted external checkpoint, forged revision, bad HMAC, reused permit and ambiguous provider result must all preserve explicit uncertainty.

No live effects were authorized by this handoff. This is research code and a test plan.
