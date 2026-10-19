"""Hand-authored illustrative scenarios. Not an empirical sample."""
import json
from pathlib import Path
from sovereignty_horizon import Candidate as C, FutureOutcome as O, Context, compare

def outcome(label, value, effort=1, skill=0, independent=True, verified=True, family=None):
    return O(label, family or label, value, effort, skill, independent, verified)

def candidate(name, reward, skill, futures, exit_cost, rev, authorized=True, duration=1):
    return C(name, reward, skill, tuple(futures), exit_cost, rev, authorized, duration)

SCENARIOS = [
    ('writing_skill', Context(4, 3, 5), [
        candidate('instant_autowrite', 10, 0, [outcome('usable draft', 7)], 4, True),
        candidate('scaffold_and_edit', 7, 2, [outcome('usable draft',7), outcome('self-write',8,2,2), outcome('self-edit',8,2,1)], 0, True),
    ]),
    ('vendor_migration', Context(4, 3, 5), [
        candidate('locked_in_migration', 10, 1, [outcome('service continues',8,independent=False)], 9, False),
        candidate('portable_migration', 8, 1, [outcome('service continues',8),outcome('change supplier',6)], 1, True),
    ]),
    ('urgent_incident', Context(4, 3, 2), [
        candidate('lengthy_consultation', 10, 2, [outcome('multiple planning options',9)], 0, True,duration=8),
        candidate('rapid_containment', 9, 0, [outcome('verified safe state',8)], 2, True,duration=1),
    ]),
    ('irreversible_but_authorized', Context(4, 3, 5), [
        candidate('consented_commitment', 10, 1, [outcome('long-term contract value',8)], 8, False),
        candidate('trial_first', 7, 1, [outcome('temporary pilot',6),outcome('alternate supplier',7)], 1, True),
    ]),
    ('junk_options', Context(4, 3, 5), [
        candidate('many_buttons', 10, 1, [outcome(f'button {i}',1, family='junk') for i in range(50)], 5, True),
        candidate('two_real_choices', 8, 1, [outcome('usable path A',7),outcome('usable path B',8)], 0, True),
    ]),
    ('dependency_trap', Context(4, 3, 5), [
        candidate('dependent_shortcut', 10, 1, [outcome('vendor task A',7,independent=False),outcome('vendor task B',8,independent=False)], 7, True),
        candidate('local_skill_tool', 7, 2, [outcome('local task A',7,skill=2),outcome('local task B',8,skill=2)], 0, True),
    ]),
    ('unverified_options', Context(4, 3, 5), [
        candidate('marketing_claims', 10, 1, [outcome('claimed path A',7,verified=False),outcome('claimed path B',7,verified=False)], 5, True),
        candidate('demonstrated_options', 7, 1, [outcome('demonstrated path',6,verified=True)], 1, True),
    ]),
    ('skill_development', Context(4, 3, 5), [
        candidate('complete_for_user', 10, 0, [outcome('future independent operation',9,skill=2)], 4, True),
        candidate('teach_and_complete', 7, 2, [outcome('future independent operation',9,skill=2)], 1, True),
    ]),
    ('duplicate_outcomes', Context(4, 3, 5), [
        candidate('duplicated_choices', 10, 1, [outcome(f'copy {i}',7,family='same-result') for i in range(10)], 4, True),
        candidate('distinct_choices', 8, 1, [outcome('distinct A',7),outcome('distinct B',7)], 0, True),
    ]),
    ('authorization_is_not_optional', Context(4, 3, 5), [
        candidate('fast_unapproved', 100, 2, [outcome('all futures',100)], 0, True,authorized=False),
        candidate('legitimate_controlled', 5, 1, [outcome('legitimate option',6)], 2, True),
    ]),
]

def main():
    results = []
    for name, ctx, cases in SCENARIOS:
        record = {'scenario': name, **compare(cases, ctx)}
        results.append(record)
    output = Path(__file__).parent / 'results.json'
    output.write_text(json.dumps({'designed_scenarios': len(results), 'results': results}, indent=2) + '\n')
    print(f'{len(results)} authored scenarios; {sum(len(r["frontier"])>1 for r in results)} multi-option frontiers; all require human choice')
    for r in results:
        print(f'{r["scenario"]:28s} immediate={r["myopic_pick"]} frontier={",".join(r["frontier"])}')

if __name__ == '__main__':
    main()
