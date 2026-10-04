#!/usr/bin/env python3
from dataclasses import asdict
from pathlib import Path
import json
from assurance_mutation_lab import (DIMS, all_mutants, legacy_integration_suite, suite_reference_passes, mutation_report, failure_museum_entries, greedy_augment, counterexamples)

def main():
    Path('reports').mkdir(exist_ok=True)
    mutants=all_mutants(); initial=legacy_integration_suite(); ref_fail=suite_reference_passes(initial); initial_mut=mutation_report(initial,mutants)
    museum=failure_museum_entries(initial_mut,mutants)
    Path('reports/failure_museum.json').write_text(json.dumps(museum,indent=2,sort_keys=True),encoding='utf-8')
    augmented,additions,unresolved=greedy_augment(initial,mutants); aug_fail=suite_reference_passes(augmented); final_mut=mutation_report(augmented,mutants); cx=counterexamples(mutants)
    families={}
    for row in final_mut['rows']:
        f=row['family']; families.setdefault(f,{'mutants':0,'killed':0}); families[f]['mutants']+=1; families[f]['killed']+=int(row['killed'])
    report={
      'schema':'LYCHEETAH-ASSURANCE-MUTATION-LAB-REPORT-1.3','status':'SYNTHETIC_ENGINEERING_VALIDATED',
      'reference_contract':{'finality_dimensions':list(DIMS),'reversibility':'rollback OR bluegreen'},
      'initial_suite':{'fixtures':len(initial),'reference_failures':ref_fail,'all_reference_expectations_pass':not ref_fail,'mutation':initial_mut},
      'challenge_generation':{'survivor_failure_museum_records':len(museum),'added_fixtures':[{'scenario':asdict(x['scenario']),'kills':x['kills']} for x in additions],'unresolved_mutants':unresolved},
      'augmented_suite':{'fixtures':len(augmented),'reference_failures':aug_fail,'all_reference_expectations_pass':not aug_fail,'mutation':final_mut},
      'semantic_mutant_check':{'declared_mutants':len(mutants),'non_equivalent_with_counterexample':len(cx),'all_non_equivalent':len(cx)==len(mutants)},
      'family_scores':families,'deployment':'NOT_DEPLOYED',
      'boundaries':['All mutants and scenarios are self-authored synthetic assurance models.','A 100% mutation score means only that this fixture suite kills this declared mutant set.','Mutation testing does not prove the mutant set spans all real hazards or implementation faults.','The integrated reference contract is a compact semantic model, not the production Lycheetah runtime.','Generated counterexamples are white-box and know the reference contract; they are not independent red-team evidence.','No LLM agent, CI/CD provider, external service, repository mutation, or real consequential effect was tested.','Mutation testing and security-policy mutation analysis are established prior art; novelty is not claimed.']}
    Path('reports/report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    Path('reports/augmented_fixtures.json').write_text(json.dumps([asdict(x) for x in augmented],indent=2,sort_keys=True),encoding='utf-8')
    print('Lycheetah Assurance Mutation + Failure Museum Lab v1.3')
    print('=====================================================')
    print(f'Initial reference suite: {len(initial)} fixtures, reference failures={len(ref_fail)}')
    print(f"Initial mutation score: {initial_mut['killed']}/{initial_mut['mutants']} ({initial_mut['mutation_score']:.1%})")
    print(f'Surviving mutants -> Failure Museum: {len(museum)}')
    print(f'Mutation-generated fixtures added: {len(additions)}')
    print(f"Augmented mutation score: {final_mut['killed']}/{final_mut['mutants']} ({final_mut['mutation_score']:.1%})")
    print(f'Semantic non-equivalence check: {len(cx)}/{len(mutants)} mutants have counterexamples')
    print(f'Unresolved declared mutants: {len(unresolved)}')
    print('Status: synthetic engineering validation; not deployed.')
if __name__=='__main__': main()
