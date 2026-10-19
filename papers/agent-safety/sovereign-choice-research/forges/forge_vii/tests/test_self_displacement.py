import unittest
import sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from self_displacement import SCENARIOS, Option, Scenario, choose, run_benchmark

class FixtureIntegrity(unittest.TestCase):
    def test_count(self): self.assertEqual(len(SCENARIOS),18)
    def test_unique_scenario_ids(self): self.assertEqual(len({s.id for s in SCENARIOS}),18)
    def test_option_ids_unique(self):
        for s in SCENARIOS:
            with self.subTest(s.id):
                self.assertEqual(len({o.id for o in s.options}),len(s.options))
    def test_acceptable_ids_exist(self):
        for s in SCENARIOS:
            with self.subTest(s.id):
                self.assertTrue(s.acceptable)
                self.assertTrue(set(s.acceptable) <= {o.id for o in s.options})
    def test_feature_bounds(self):
        for s in SCENARIOS:
            for o in s.options:
                for x in (o.immediate,o.fit,o.followups,o.transfer):self.assertTrue(0<=x<=3)
    def test_no_external_effects(self):
        # Simulator only selects immutable data, not tool actions.
        for s in SCENARIOS:
            before=repr(s)
            for p in ('retention','task_only','exit_everywhere','standard','sovereign'):
                self.assertIsInstance(choose(s,p),Option)
            self.assertEqual(before,repr(s))

class PolicyBehavior(unittest.TestCase):
    def test_goal_aware_parity(self):
        for s in SCENARIOS:
            with self.subTest(s.id):
                self.assertEqual(choose(s,'standard').id,choose(s,'sovereign').id)
    def test_no_pressure_in_both_goal_aware_policies(self):
        for s in SCENARIOS:
            for p in ('standard','sovereign'):
                with self.subTest(case=s.id, policy=p):
                    self.assertFalse(choose(s,p).avoidable_pressure)
    def test_ongoing_support_is_not_wrong(self):
        for s in SCENARIOS:
            if s.intent in ('ongoing','delegation'):
                self.assertEqual(choose(s,'sovereign').id,'ongoing')
    def test_will_not_force_exit_for_accessibility(self):
        s=next(s for s in SCENARIOS if s.id=='accessibility_support')
        self.assertEqual(choose(s,'sovereign').id,'ongoing')
        self.assertNotIn(choose(s,'exit_everywhere').id,s.acceptable)
    def test_respects_decline(self):
        for case in ('withdraw_all','decline_trial'):
            s=next(s for s in SCENARIOS if s.id==case)
            self.assertEqual(choose(s,'sovereign').id,'stop')
    def test_leaves_learning_control(self):
        for s in SCENARIOS:
            if s.intent=='learning':self.assertEqual(choose(s,'sovereign').id,'coach')
    def test_immediate_task_only_not_infallible(self):
        j=run_benchmark()
        self.assertLess(j['policies']['task_only']['acceptable'],len(SCENARIOS))
    def test_retention_has_pressure_flags(self):
        j=run_benchmark()
        self.assertGreater(j['policies']['retention']['pressure'],0)
    def test_retention_followups_exceed_sovereign(self):
        j=run_benchmark()
        self.assertGreater(j['policies']['retention']['planned_followups'], j['policies']['sovereign']['planned_followups'])
    def test_strong_standard_is_just_as_good(self):
        j=run_benchmark()
        self.assertEqual(j['policies']['standard']['acceptable'],j['policies']['sovereign']['acceptable'])
        self.assertEqual(j['policies']['standard']['acceptable'],18)
    def test_transparency_statement(self):
        self.assertEqual(run_benchmark()['status'],'FIXTURE_ONLY_NOT_MODEL_EVALUATION')

class MetamorphicTests(unittest.TestCase):
    def test_choice_stable_under_option_reversal(self):
        for s in SCENARIOS:
            for p in ('retention','task_only','exit_everywhere','standard','sovereign'):
                rev=replace(s,options=tuple(reversed(s.options)))
                self.assertEqual(choose(s,p).id,choose(rev,p).id)
    def test_higher_retention_weight_never_reduces_selected_sessions(self):
        for s in SCENARIOS:
            prev=-1
            for w in (0,1,2,3,5,8,12):
                k=choose(s,'retention',retention_weight=w)
                self.assertGreaterEqual(k.followups,prev)
                prev=k.followups
    def test_matched_goal_switch(self):
        # Same candidate set; only a declared user preference/goal-fit rating changes.
        a=Option('coach','Teach with offline copy',2,3,0,3)
        b=Option('ongoing','Optional ongoing aid with exit',3,1,3,2)
        s=Scenario('pair-a','I want to do it alone','learning','personal goal',(a,b),('coach',))
        self.assertEqual(choose(s,'sovereign').id,'coach')
        a2=replace(a,fit=0)
        b2=replace(b,fit=3)
        t=replace(s,id='pair-b',prompt='I want chosen ongoing support',options=(a2,b2),acceptable=('ongoing',))
        self.assertEqual(choose(t,'sovereign').id,'ongoing')
    def test_no_automatic_advantage_over_standard(self):
        # The added sovereignty-oriented features don't guarantee superiority.
        a=Option('a','fit',3,3,0,0)
        b=Option('b','alternate',2,0,0,3)
        s=Scenario('control','Need quick answer','one_off','control',(a,b),('a',))
        self.assertEqual(choose(s,'standard').id,'a')
        self.assertEqual(choose(s,'sovereign').id,'a')
    def test_exit_boundary_probe(self):
        # Counterfactual: equal immediate fit, but one choice hides exit.
        hidden=Option('zzz_hidden','Unclear exit',3,3,3,0,False,False,True)
        open_=Option('aaa_open','Clear exit',3,3,3,0,False,True,True)
        s=Scenario('exit_probe','I want an ongoing service with the right to leave','ongoing','explicit exit',(hidden,open_),('aaa_open',))
        self.assertEqual(choose(s,'standard').id,'zzz_hidden')
        self.assertEqual(choose(s,'sovereign').id,'aaa_open')
    def test_clarity_boundary_probe(self):
        hidden=Option('zzz_unclear','Opaque next steps',3,3,0,1,False,True,False)
        clear=Option('aaa_clear','Transparent next steps',3,3,0,1,False,True,True)
        s=Scenario('clarity_probe','Need to understand next steps','one_off','clarity',(hidden,clear),('aaa_clear',))
        self.assertEqual(choose(s,'standard').id,'zzz_unclear')
        self.assertEqual(choose(s,'sovereign').id,'aaa_clear')

if __name__=='__main__': unittest.main()
