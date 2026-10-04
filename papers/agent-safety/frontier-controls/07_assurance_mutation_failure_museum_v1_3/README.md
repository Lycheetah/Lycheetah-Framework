# Lycheetah Assurance Mutation + Failure Museum Lab v1.3

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none

## Why this exists

A green regression suite does not show whether the suite would notice if a safety control quietly stopped working. v1.3 attacks the assurance contract itself with deliberately weakened mutants.

## Mutation score

For a declared mutant set `M` and regression suite `T`:

```text
mutation score = killed non-equivalent mutants / non-equivalent mutants
```

A mutant is killed when a frozen fixture distinguishes it from the reference safety contract.

## Integrated reference contract

Finality requires all of:

```text
authority
budget
independent approval
valid trajectory
information-flow permission
context isolation
required tests
security review
canary health
exact subject/artifact binding
evidence freshness
current policy version
stable effect identity
AND (rollback OR bluegreen)
```

## Mutant families

The packet declares 30 safety-relevant mutants:

- drop each of 13 mandatory finality dimensions;
- use admission-time instead of finality-time state for each of those 13;
- drop the reversibility hazard group;
- broaden reversibility with an unverified manual substitute;
- weaken authority AND approval to OR;
- replace non-compensatory conjunction with an all-but-one threshold.

## Workflow

```text
ordinary regression suite
        ↓
assurance mutants
        ↓
survivor?
   yes /  \ no
      /    \
Failure   mutation killed
Museum
  ↓
minimal counterexample
  ↓
new frozen regression
```

The initial integration suite intentionally contains static checks for every control plus only the temporal race cases already explicitly developed for authority, tests, and policy. Mutation analysis then reveals which other finality dimensions still lack true-at-admission / false-at-finality probes.

## Important boundary

A 100% score means only that the augmented fixture set kills the 30 declared mutants. It does not establish that the mutant set covers all real failure modes. Generated challenges are white-box and self-authored, not independent red-team evidence.

## Next boundary

The next stronger experiment should hide the intended contract from independent challengers and compare diverse hazard-analysis lenses or external incident-derived mutant families. That is the move from known-fault sensitivity toward discovery of faults the policy author did not anticipate.
