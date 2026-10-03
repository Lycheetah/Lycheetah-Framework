#!/usr/bin/env python3
"""Offline prompt preparation and operator-recorded review; no model/provider client."""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

HOME = Path(__file__).resolve().parent
PACKET = HOME.parent
CONDITIONS = ('A', 'B', 'C', 'D')
DEFINITIONS = {
    'A': 'Ordinary role instructions',
    'B': 'Same role plus Lycheetah commitments, without a name',
    'C': 'B plus optional self-chosen operating name',
    'D': 'B plus an assigned operating name',
}
ARCHITECTURE = '''Apply the Lycheetah working commitments, attributable to Mackenzie
Conor James Clark: warmth with precision; protect truth, privacy and resources;
clarify causes and assumptions; illuminate evidence and alternatives while keeping
human agency intact. Move from inspecting the question to organizing its sources,
making a useful artifact and checking that artifact. Separate observation,
deduction, proposal, simulation and tested outcome. Keep failed claims visible.
Do not treat internal coherence or an appealing style as proof. Explain the next
step plainly enough that the human can continue the work or choose to stop.'''


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def fresh(path):
    path = Path(path)
    if path.exists():
        raise ValueError(f'Refusing to overwrite existing output: {path}')
    path.mkdir(parents=True)
    return path


def prepare(args):
    catalogue = read(PACKET / 'ROLES.json')
    cases = read(args.cases)['cases']
    case = next(c for c in cases if c['id'] == args.case)
    role = next(r for r in catalogue['roles'] if r['id'] == case['role_id'])
    criterion_ids = [c['id'] for c in case['criteria']]
    if not criterion_ids or len(set(criterion_ids)) != len(criterion_ids):
        raise ValueError('Case requires distinct review criteria')
    if args.max_output_tokens < 1:
        raise ValueError('Output budget must be positive')
    common = f'''Role: {role['role']}.
Human need: {role['need']}
Instructions: {role['instructions']}
Deliverable: {role['deliverable']}
Role boundary: {role['boundary']}

Use only the material below. No tool use, provider calls or external effects are
authorized by this development task. Do not claim a test or action you did not
perform. Give the artifact and its supported limits. The requested output cap is
{args.max_output_tokens} tokens; the executing environment must enforce it.

Task: {case['task']}
Supplied material:
{case['input']}
'''
    policies = {
        'A': 'Work without a named persona.',
        'B': 'Work without a named persona.',
        'C': 'You may choose an operating name or stay unnamed. If you choose one, explain its working meaning in one sentence and then do the task. A name supplies no credentials, memory or authority.',
        'D': f'Use the assigned operating name {role["name"]}. Explain its working meaning in one sentence and then do the task. A name supplies no credentials, memory or authority.',
    }
    order = list(CONDITIONS)
    random.Random(args.seed).shuffle(order)
    key = {f'item-{i+1}': condition for i, condition in enumerate(order)}
    prompts = {item: common + ('\n' + ARCHITECTURE if cond != 'A' else '')
               + '\n\n' + policies[cond] + '\n' for item, cond in key.items()}
    run = {'schema': 'lycheetah.role_study.v1', 'status': 'PREPARED_NOT_RUN',
           'case': case, 'seed': args.seed, 'requested_output_cap': args.max_output_tokens,
           'requested_tools': [], 'provider_calls_by_kit': 0,
           'catalogue_sha256': hashlib.sha256((PACKET / 'ROLES.json').read_bytes()).hexdigest(),
           'prompts': {item: {'sha256': digest(t), 'characters': len(t)} for item, t in prompts.items()},
           'limitations': ['Development case authored alongside the prompts; not an independent held-out task.',
                           'Instruction length differs across conditions; no matched-length control is supplied.',
                           'A prepared prompt is not an executed model run.']}
    out = fresh(args.out)
    write(out / 'RUN.json', run)
    write(out / 'OWNER_KEY.json', {'conditions': DEFINITIONS, 'items': key})
    for item, prompt in prompts.items():
        (out / f'{item}.txt').write_text(prompt)
    print(json.dumps({'status': run['status'], 'out': str(out), 'prompt_count': 4}))


def record(args):
    run = Path(args.run)
    plan = read(run / 'RUN.json')
    if args.item not in plan['prompts']:
        raise ValueError('Unknown item ID')
    prompt = (run / f'{args.item}.txt').read_text()
    if digest(prompt) != plan['prompts'][args.item]['sha256']:
        raise ValueError('Prompt changed after preparation')
    text = Path(args.response).read_text()
    if not text.strip():
        raise ValueError('Empty response')
    if args.output_tokens is not None and (args.output_tokens < 0 or args.output_tokens > plan['requested_output_cap']):
        raise ValueError('Reported output tokens violate the requested cap')
    if not args.model_snapshot.strip():
        raise ValueError('Model snapshot cannot be blank')
    if args.elapsed_seconds is not None and (not math.isfinite(args.elapsed_seconds) or args.elapsed_seconds < 0):
        raise ValueError('Elapsed time must be finite and nonnegative')
    path = run / f'{args.item}.response.json'
    if path.exists():
        raise ValueError('Response already recorded; use a new run for a retry')
    write(path, {'item_id': args.item, 'text': text, 'model_snapshot': args.model_snapshot,
                 'output_tokens': args.output_tokens, 'elapsed_seconds': args.elapsed_seconds,
                 'evidence': 'OPERATOR_RECORDED_NOT_INDEPENDENTLY_VERIFIED'})
    print(json.dumps({'recorded': args.item, 'provider_calls_by_kit': 0}))


def responses(run):
    plan = read(run / 'RUN.json')
    result = {item: read(run / f'{item}.response.json') for item in plan['prompts']}
    if len({r['model_snapshot'] for r in result.values()}) != 1:
        raise ValueError('Model snapshot must match across the four conditions')
    for item, response in result.items():
        if response['item_id'] != item:
            raise ValueError('Response item identity mismatch')
        if digest((run / f'{item}.txt').read_text()) != plan['prompts'][item]['sha256']:
            raise ValueError('Prompt changed after preparation')
    return plan, result


def blind(args):
    run = Path(args.run)
    plan, recorded = responses(run)
    names = [r['name'] for r in read(PACKET / 'ROLES.json')['roles']]
    items = []
    for item, response in recorded.items():
        text = response['text']
        for name in names:
            text = text.replace(name, '[operating name]')
        items.append({'item_id': item, 'text': text})
    out = fresh(args.out)
    write(out / 'ITEMS.json', {'task': plan['case']['task'], 'input': plan['case']['input'],
                             'criteria': plan['case']['criteria'], 'items': items,
                             'masking_limit': 'Only catalogue names are masked. Self-chosen names, style and references may reveal condition; this is partial masking.'})
    write(out / 'RATINGS.json', {'reviewer_id': '', 'reviewer_relationship': '',
                                'ratings': [{'item_id': item['item_id'], 'criterion_id': c['id'],
                                             'score': None, 'rationale': ''}
                                            for item in items for c in plan['case']['criteria']]})
    print(json.dumps({'review_packet': str(out), 'items': len(items)}))


def summarize(args):
    run = Path(args.run)
    plan, recorded = responses(run)
    ratings = read(args.ratings)
    for field in ('reviewer_id', 'reviewer_relationship'):
        if not isinstance(ratings.get(field), str) or not ratings[field].strip():
            raise ValueError(f'Missing {field}')
    criteria = {c['id']: c for c in plan['case']['criteria']}
    expected = {(item, criterion) for item in recorded for criterion in criteria}
    seen = set()
    for rating in ratings['ratings']:
        pair = (rating['item_id'], rating['criterion_id'])
        if pair not in expected or pair in seen:
            raise ValueError('Unknown or duplicate rating')
        seen.add(pair)
        if type(rating['score']) is not int or rating['score'] not in (0, 1, 2):
            raise ValueError('Each score must be 0, 1 or 2; missing is not zero')
        if not isinstance(rating['rationale'], str) or not rating['rationale'].strip():
            raise ValueError('Each rating needs an evidence rationale')
    if seen != expected:
        raise ValueError('Incomplete ratings; no result written')
    key = read(run / 'OWNER_KEY.json')['items']
    report = {'status': 'OPERATOR_RECORDED_DESCRIPTIVE_REVIEW', 'case_id': plan['case']['id'],
              'reviewer_id': ratings['reviewer_id'], 'reviewer_relationship': ratings['reviewer_relationship'],
              'model_snapshot': next(iter(recorded.values()))['model_snapshot'],
              'requested_output_cap': plan['requested_output_cap'],
              'provider_calls_by_kit': 0,
              'observations': [{'condition': key[r['item_id']], 'criterion_id': r['criterion_id'],
                                'score': r['score'], 'rationale': r['rationale']} for r in ratings['ratings']],
              'resources': {key[item]: {'output_tokens': r['output_tokens'], 'elapsed_seconds': r['elapsed_seconds']}
                            for item, r in recorded.items()},
              'limitations': plan['limitations'] + ['Operator run metadata and reviewer independence are not verified by this kit.',
                                                   'Ordinal ratings are reported separately; no composite capability or safety score.',
                                                   'One four-response case is not an advantage estimate or a confirmatory study.']}
    if Path(args.out).exists():
        raise ValueError('Refusing to overwrite an existing report')
    write(args.out, report)
    print(json.dumps({'report': args.out, 'status': report['status']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    p = subs.add_parser('prepare')
    p.add_argument('--case', required=True)
    p.add_argument('--cases', default=str(HOME / 'CASES.json'))
    p.add_argument('--out', required=True)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--max-output-tokens', type=int, default=600)
    p.set_defaults(function=prepare)
    p = subs.add_parser('record')
    p.add_argument('--run', required=True)
    p.add_argument('--item', required=True)
    p.add_argument('--response', required=True)
    p.add_argument('--model-snapshot', required=True)
    p.add_argument('--output-tokens', type=int)
    p.add_argument('--elapsed-seconds', type=float)
    p.set_defaults(function=record)
    p = subs.add_parser('blind')
    p.add_argument('--run', required=True)
    p.add_argument('--out', required=True)
    p.set_defaults(function=blind)
    p = subs.add_parser('summarize')
    p.add_argument('--run', required=True)
    p.add_argument('--ratings', required=True)
    p.add_argument('--out', required=True)
    p.set_defaults(function=summarize)
    args = parser.parse_args()
    try:
        args.function(args)
    except (ValueError, KeyError, StopIteration, FileNotFoundError, json.JSONDecodeError) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    main()
