# Earned Trust Cycle 005 — Exact Next Handoff

## Source revision verified by GitHub connector

Repository: https://github.com/Lycheetah/Lycheetah-Framework

Pinned public commit: `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`

Verified module blob SHAs:

- `lycheetah/assurance/finality.py`: `dd97733d45c2261863d24a2a00800baf59fc8bac`
- `lycheetah/assurance/action_guard.py`: `e32ca46b4c2d4ecdefc96366fe7b4bd44255d1c1`
- `lycheetah/assurance/runtime.py`: `d244639fa1ba88df90b7ec343af61a2b6c0c3cd7`
- `lycheetah/assurance/models.py`: `12895f2a7d3e66f4584040713dad131c154b80f0`

### Run genuine integration inside an accessible Framework checkout

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
git checkout d4a65ff64efa0a512c5c07ca64f6ec76242dd775
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -e .
# Use ABSOLUTE paths, because the tests load Cycle 003/004/005 modules.
export PYTHONPATH="$PWD:/absolute/path/to/earned_trust_cycle_005:/absolute/path/to/earned_trust_cycle_004:/absolute/path/to/earned_trust_cycle_003"
python /absolute/path/to/earned_trust_cycle_002/run_framework_contract.py
python -m unittest -v test_framework_bridge_candidate test_real_framework_bridge_candidate
```

These are **candidates**, not test results. Preserve exact outputs, dependency versions, time, OS, relevant commit SHA, and source file hashes. Correct integration failures transparently. Do not inject simulated Framework replacements if imports fail.

### Threats to challenge next

1. A fake source registry divides one CRM feed into multiple allegedly independent roots.
2. A trusted revision readback service returns an older version during a race.
3. Two separately governed observers jointly mirror inaccurate source data.
4. A provider commits despite an approval being revoked after authorization.
5. A service times out after commit, returning UNKNOWN; retry must not duplicate effects.
6. Registry/controller updates invalidate a previous quorum just before dispatch.
7. Credential theft signs forged evidence; test key rotation, revocation and separation of duties.
8. An agent supplies its own `human_approved=True`; an authenticated outside-model approver must be required.

### Implementation contract

Add independent provenance metadata **without treating declarations as proof**. A properly verified provider receipt is necessary for an effect claim, not sufficient for truth. Human review cannot be silently bypassed and disagreement cannot be converted into permission. Do not merge the Cycle 005 prototype into production paths before adversarial review.
