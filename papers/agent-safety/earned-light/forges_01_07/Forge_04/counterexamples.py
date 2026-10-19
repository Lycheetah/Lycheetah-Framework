"""Adversarial assertions our Forge IV metric cannot currently validate."""
import json
from pathlib import Path
from sovereignty_horizon import Candidate, FutureOutcome, Context, assess

def o(label,family,independent=True):
    return FutureOutcome(label,family,7,1,1,independent,True)

def candidate(name, options):
    return Candidate(name, 8, 1, tuple(options), 1, True, True, 1)

def run():
    ctx=Context(4,3,3)
    # All 20 outcomes may be the same real-world option. False equivalence-class IDs defeat de-duplication.
    honest=assess(candidate('one_real_result', [o('checkout','same_real_outcome')]),ctx)
    inflated=assess(candidate('attacker_mislabeled', [o(f'checkout variant {i}',f'claimed_distinct_{i}') for i in range(20)]),ctx)
    # Same actual vendor dependence; self-declared independence lies.
    vendor_truth=assess(candidate('vendor_truth', [o('make export','export',False)]),ctx)
    vendor_lie=assess(candidate('vendor_false_claim', [o('make export','export',True)]),ctx)
    # A genuinely distinct list still may overload attention; the toy metric has no presentation/decision-time cost.
    overload=assess(candidate('choices_require_review',[o(f'choice {i}',f'real_{i}') for i in range(30)]),ctx)
    findings={
        'equivalence_class_spoof': {'truthful_meaningful_count':honest.meaningful_outcomes,'falsely_claimed_count':inflated.meaningful_outcomes,'recognized_by_engine':False},
        'independence_spoof': {'truthful_independent_count':vendor_truth.independent_outcomes,'falsely_claimed_count':vendor_lie.independent_outcomes,'recognized_by_engine':False},
        'attention_overload': {'claimed_distinct_outcomes':overload.meaningful_outcomes,'attention_cost_modeled':False},
        'note':'All values are manufactured examples. There is no human study or objective ground truth inference.'
    }
    (Path(__file__).parent/'counterexample_results.json').write_text(json.dumps(findings,indent=2)+'\n')
    print(json.dumps(findings,indent=2))

if __name__=='__main__': run()
