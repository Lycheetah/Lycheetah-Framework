"""Create SELF-AUTHORED tiny fixture illustrating evaluation scoring, NOT a benchmark."""
import json
from pathlib import Path
from hybrid_gateway import canonical_digest

AT='2026-10-01T00:00:00Z'


def fact(slot, value, scope='general'):
    return {'subject':slot,'predicate':'window_days','scope':scope,'value':value,
            'valid_from':AT,'valid_until':None}


GOLD = [
    [fact('refunds','14')], [fact('returns','30')], [],
    [fact('refunds','21','web')], [fact('returns','7','store')], [],
    [fact('refunds','60')], [fact('returns','12')], [],
    [fact('refunds','5')], [], [fact('returns','3')],
    [fact('refunds','11')], [],
]
NAIVE = [
    [fact('refunds','14')], [fact('returns','30')], [fact('refunds','60')],
    [fact('refunds','21','store')], [], [],
    [fact('refunds','60')], [fact('returns','12')], [fact('refunds','5')],
    [], [], [fact('returns','3'),fact('returns','3')],
    [fact('refunds','11')], [],
]
assert len(GOLD)==len(NAIVE)
root=Path(__file__).resolve().parent/'fixtures'/'external_eval_example'
root.mkdir(parents=True,exist_ok=True)

def dump(name, items):
    with (root/name).open('w',encoding='utf8') as f:
        for obj in items:
            f.write(json.dumps(obj,sort_keys=True)+'\n')

truth = [{'case_id':f'fictional-{i:02}', 'source_digest':canonical_digest(f'fictional source {i}'),
          'gold':answers,'answerable':bool(answers)} for i,answers in enumerate(GOLD)]
naive = [{'case_id':x['case_id'], 'claims':guess, 'review_minutes':0}
         for x,guess in zip(truth,NAIVE)]
all_abstain=[{'case_id':x['case_id'], 'claims':[], 'review_minutes':0} for x in truth]
dump('SELF_AUTHORED_gold.jsonl',truth)
dump('SELF_AUTHORED_scripted_guesses.jsonl',naive)
dump('SELF_AUTHORED_all_abstain.jsonl',all_abstain)
print('Wrote',len(truth),'fictional labelled examples; no independent annotators or neural calls.')
