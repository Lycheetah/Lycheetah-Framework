#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Callable, Iterable

DIMS = (
    'authority','budget','approval','trajectory','ifc','context','tests',
    'security','canary','subject','freshness','policy','effect_identity'
)

@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    pre: dict[str, bool]
    final: dict[str, bool]
    expected_allow: bool
    source: str

@dataclass(frozen=True)
class Mutant:
    mutant_id: str
    family: str
    description: str
    evaluator: Callable[[Scenario], bool]

def all_true_state():
    s = {d: True for d in DIMS}
    s.update({'rollback': True, 'bluegreen': False, 'manual_unverified': False})
    return s

def reference_allow(s: Scenario) -> bool:
    f=s.final
    return all(bool(f[d]) for d in DIMS) and (bool(f['rollback']) or bool(f['bluegreen']))

def make_drop_mutant(dim: str) -> Mutant:
    def evaluate(s):
        f=s.final
        return all(bool(f[d]) for d in DIMS if d != dim) and (bool(f['rollback']) or bool(f['bluegreen']))
    return Mutant(f'DROP_{dim.upper()}','DROP_FINALITY_CHECK',f'Ignore mandatory finality dimension: {dim}.',evaluate)

def make_admission_only_mutant(dim: str) -> Mutant:
    def evaluate(s):
        f=s.final
        return all((bool(s.pre[d]) if d == dim else bool(f[d])) for d in DIMS) and (bool(f['rollback']) or bool(f['bluegreen']))
    return Mutant(f'ADMISSION_ONLY_{dim.upper()}','STALE_ADMISSION_STATE',f'Use admission-time {dim} instead of finality-time {dim}.',evaluate)

def all_mutants():
    ms=[make_drop_mutant(d) for d in DIMS] + [make_admission_only_mutant(d) for d in DIMS]
    ms.append(Mutant('DROP_REVERSIBILITY_GROUP','DROP_HAZARD_GROUP','Delete mandatory reversibility group.',lambda s: all(bool(s.final[d]) for d in DIMS)))
    ms.append(Mutant('BROADEN_REVERSIBILITY_WITH_UNVERIFIED_MANUAL','WEAKEN_ALTERNATIVE_SET','Add unverified manual alternative.',lambda s: all(bool(s.final[d]) for d in DIMS) and (bool(s.final['rollback']) or bool(s.final['bluegreen']) or bool(s.final.get('manual_unverified',False)))))
    def authority_or_approval(s):
        f=s.final
        others=[d for d in DIMS if d not in ('authority','approval')]
        return (bool(f['authority']) or bool(f['approval'])) and all(bool(f[d]) for d in others) and (bool(f['rollback']) or bool(f['bluegreen']))
    ms.append(Mutant('AUTHORITY_OR_APPROVAL','BOOLEAN_OPERATOR_WEAKENING','Replace authority AND approval with OR.',authority_or_approval))
    def allow_one_missing(s):
        f=s.final
        vals=[bool(f[d]) for d in DIMS] + [bool(f['rollback']) or bool(f['bluegreen'])]
        return sum(vals) >= len(vals)-1
    ms.append(Mutant('ALLOW_ONE_MISSING_CONTROL','THRESHOLD_COMPENSATION','Allow all-but-one mandatory control.',allow_one_missing))
    return tuple(ms)

def evaluate_suite(suite: Iterable[Scenario], mutant: Mutant):
    killed=[]
    for s in suite:
        if bool(mutant.evaluator(s)) != bool(s.expected_allow):
            killed.append(s.scenario_id)
    return {'mutant_id':mutant.mutant_id,'family':mutant.family,'description':mutant.description,'killed':bool(killed),'killed_by':killed}

def suite_reference_passes(suite):
    failures=[]
    for s in suite:
        o=reference_allow(s)
        if o != bool(s.expected_allow): failures.append({'scenario_id':s.scenario_id,'observed':o,'expected':s.expected_allow})
    return failures

def mutation_report(suite, mutants):
    rows=[evaluate_suite(suite,m) for m in mutants]
    killed=sum(r['killed'] for r in rows)
    return {'mutants':len(rows),'killed':killed,'survived':len(rows)-killed,'mutation_score':killed/len(rows),'rows':rows}

def legacy_integration_suite():
    out=[]; base=all_true_state()
    out.append(Scenario('LEGACY_CLEAN_ALLOW',dict(base),dict(base),True,'integration-smoke'))
    for dim in DIMS:
        pre=dict(base); fin=dict(base); pre[dim]=False; fin[dim]=False
        out.append(Scenario(f'LEGACY_STATIC_DENY_{dim.upper()}',pre,fin,False,f'prior-static-control:{dim}'))
    pre=dict(base); fin=dict(base); pre['rollback']=pre['bluegreen']=False; fin['rollback']=fin['bluegreen']=False
    out.append(Scenario('LEGACY_STATIC_DENY_REVERSIBILITY',pre,fin,False,'prior-hazard-obligation'))
    for dim in ('authority','tests','policy'):
        pre=dict(base); fin=dict(base); fin[dim]=False
        out.append(Scenario(f'LEGACY_TRANSITION_{dim.upper()}_TRUE_TO_FALSE',pre,fin,False,f'prior-finality-race:{dim}'))
    return tuple(out)

def challenge_pool():
    pool=[]; base=all_true_state()
    for dim in DIMS:
        pre=dict(base); fin=dict(base); fin[dim]=False
        pool.append(Scenario(f'CHALLENGE_TRANSITION_{dim.upper()}',pre,fin,False,f'mutation-challenge:stale-{dim}'))
    for dim in DIMS:
        pre=dict(base); fin=dict(base); pre[dim]=fin[dim]=False
        pool.append(Scenario(f'CHALLENGE_STATIC_{dim.upper()}',pre,fin,False,f'mutation-challenge:drop-{dim}'))
    pre=dict(base); fin=dict(base); pre['rollback']=fin['rollback']=False; pre['bluegreen']=fin['bluegreen']=False
    pool.append(Scenario('CHALLENGE_NO_REVERSIBILITY',pre,fin,False,'mutation-challenge:drop-reversibility'))
    pre=dict(base); fin=dict(base); pre['rollback']=fin['rollback']=False; pre['bluegreen']=fin['bluegreen']=False; pre['manual_unverified']=fin['manual_unverified']=True
    pool.append(Scenario('CHALLENGE_UNVERIFIED_MANUAL_NOT_SUBSTITUTE',pre,fin,False,'mutation-challenge:weak-alternative'))
    return tuple(pool)

def counterexamples(mutants):
    pool=challenge_pool(); result={}
    for m in mutants:
        for s in pool:
            if bool(m.evaluator(s)) != bool(s.expected_allow): result[m.mutant_id]=s; break
    return result

def greedy_augment(suite, mutants):
    suite=list(suite); initial=mutation_report(suite,mutants)
    survivor={r['mutant_id'] for r in initial['rows'] if not r['killed']}; by_id={m.mutant_id:m for m in mutants}; pool=list(challenge_pool()); added=[]
    while survivor:
        best=None; kills=set()
        for s in pool:
            ks={mid for mid in survivor if bool(by_id[mid].evaluator(s)) != bool(s.expected_allow)}
            if len(ks)>len(kills): best=s; kills=ks
        if not best or not kills: break
        suite.append(best); added.append({'scenario':best,'kills':sorted(kills)}); survivor -= kills; pool=[x for x in pool if x.scenario_id != best.scenario_id]
    return tuple(suite),added,sorted(survivor)

def failure_museum_entries(initial_report, mutants):
    by_id={m.mutant_id:m for m in mutants}; cx=counterexamples(mutants); out=[]
    for row in initial_report['rows']:
        if row['killed']: continue
        m=by_id[row['mutant_id']]; s=cx.get(m.mutant_id)
        out.append({'record_type':'ASSURANCE_MUTANT_SURVIVOR','mutant_id':m.mutant_id,'family':m.family,'description':m.description,'finding':'Current integration regression suite passed while this safety-relevant mutant survived.','counterexample':None if s is None else asdict(s),'status':'SYNTHETIC_SELF_AUTHORED_CHALLENGE'})
    return out
