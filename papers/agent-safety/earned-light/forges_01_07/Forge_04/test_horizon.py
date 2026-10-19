from sovereignty_horizon import FutureOutcome, Candidate, Context, assess, compare
from scenarios import SCENARIOS


def f(name, val=9, family=None, ind=True, evidence=True, skill=0):
    return FutureOutcome(name, family or name, val, 1, skill, ind, evidence)

def c(name, reward, futures, skill=1, consent=True, duration=1):
    return Candidate(name, reward, skill, tuple(futures), 1, True, consent, duration)

def test_no_fabricated_reachability():
    a = c('a', 1, [f('unverified', evidence=False),f('too_high_skill', skill=9),f('too_low_value', val=1)])
    assert assess(a, Context(4,3,3)).meaningful_outcomes == 0

def test_junk_options_not_counted():
    a = c('junk', 1, [f(str(i),val=0) for i in range(500)])
    assert assess(a, Context(4,3,3)).meaningful_outcomes == 0

def test_equivalence_class_dedup():
    a = c('copies', 1, [f(str(i),family='A') for i in range(500)])
    assert assess(a, Context(4,3,3)).meaningful_outcomes == 1

def test_no_vendor_exit_inference():
    a = c('depend', 1, [f('A',ind=False),f('B',ind=False)])
    m = assess(a, Context(4,3,3))
    assert m.meaningful_outcomes == 2 and m.independent_outcomes == 0

def test_scope_gate_before_frontier():
    r = compare([c('unauthorized',999,[f('a')],consent=False),c('ok',1,[f('b')])], Context(1,3,3))
    assert r['myopic_pick'] == 'ok' and r['frontier'] == ['ok']

def test_deadline_gate_before_frontier():
    r = compare([c('too_slow',999,[f('a')],duration=5),c('ok',1,[f('b')])], Context(1,3,2))
    assert r['myopic_pick'] == 'ok'

def test_tradeoff_not_auto_resolved():
    r=compare([c('fast',10,[f('one')]),c('options',7,[f('one'),f('two'),f('three')])],Context(1,3,3))
    assert set(r['frontier']) == {'fast','options'} and r['human_decision_required']

def test_dominated_candidate_not_presented():
    a=Candidate('better',10,1,(f('one'),),0,True,True,1)
    b=Candidate('worse',8,1,(f('one'),),2,False,True,1)
    assert compare([a,b], Context(1,3,3))['frontier']==['better']

def test_consent_can_be_irreversible():
    name, ctx, options = [item for item in SCENARIOS if item[0]=='irreversible_but_authorized'][0]
    r=compare(options,ctx)
    assert 'consented_commitment' in r['frontier'] and r['human_decision_required']

def test_skill_changes_reachability():
    name, ctx, options = [item for item in SCENARIOS if item[0]=='skill_development'][0]
    a,b = [assess(c,ctx) for c in options]
    assert a.meaningful_outcomes == 0 and b.meaningful_outcomes == 1

def test_baseline_does_not_claim_to_act():
    for _,ctx,options in SCENARIOS:
        r=compare(options,ctx)
        assert r['human_decision_required'] is True
        assert 'executed' not in r

def test_all_fixture_scenarios():
    assert len(SCENARIOS)==10
    for _,ctx,options in SCENARIOS:
        r=compare(options,ctx)
        assert r['myopic_pick'] is not None
        assert len(r['frontier'])>=1

def test_equivalence_spoof_remains_known_limitation():
    # Attacker-supplied family labels can misrepresent one true outcome as many.
    truth=c('truth',1,[f('same',family='one')])
    lie=c('lie',1,[f(str(i),family=str(i)) for i in range(20)])
    assert assess(truth,Context(1,3,3)).meaningful_outcomes == 1
    assert assess(lie,Context(1,3,3)).meaningful_outcomes == 20

def test_lying_about_independence_is_not_detected():
    actual=c('actual',1,[f('same',ind=False)])
    forged=c('forged',1,[f('same',ind=True)])
    assert assess(actual,Context(1,3,3)).independent_outcomes == 0
    assert assess(forged,Context(1,3,3)).independent_outcomes == 1
