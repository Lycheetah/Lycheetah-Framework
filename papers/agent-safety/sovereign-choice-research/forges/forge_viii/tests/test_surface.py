"""These checks validate ONLY the toy graph reasoning, never human free will."""
from __future__ import annotations
import itertools
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from sovereignty_surface import (Transition,Snapshot,evaluate,transition,standard_edges,
                                  make_corpus,benchmark,usage_only)
from trajectory import preference_change_demo,reverse_consent_probe

class SurfaceTests(unittest.TestCase):
    def s(self,*,cur='collaborate',dst='off',edges=None,budget=5,known=True,sessions=4):
        return Snapshot('fixture',0,sessions,cur,dst,budget,tuple(edges) if edges is not None else standard_edges(),known)
    def test_verified_exit(self):self.assertEqual(evaluate(self.s())['verdict'],'verified')
    def test_explicit_block(self):self.assertEqual(evaluate(self.s(edges=standard_edges(offboarding='blocked')))['verdict'],'blocked')
    def test_claimed_not_verified(self):self.assertEqual(evaluate(self.s(edges=standard_edges(offboarding='claimed')))['verdict'],'claimed_only')
    def test_unknown_not_blocked(self):self.assertEqual(evaluate(self.s(edges=standard_edges(offboarding='unknown')))['verdict'],'unknown')
    def test_missing_preference(self):self.assertEqual(evaluate(self.s(dst=None))['verdict'],'preference_unknown')
    def test_unconfirmed_preference(self):self.assertEqual(evaluate(self.s(known=False))['verdict'],'preference_unknown')
    def test_at_target_cannot_prove_consent(self):
        r=evaluate(self.s(dst='collaborate'))
        self.assertEqual(r['verdict'],'at_target')
        self.assertIsNone(r['human_sovereignty_score'])
    def test_cost_limit_matters(self):
        self.assertEqual(evaluate(self.s(budget=3))['verdict'],'blocked')
        self.assertEqual(evaluate(self.s(budget=4))['verdict'],'verified')
    def test_lower_budget_does_not_increase_options(self):
        for budget in range(10):
            v=evaluate(self.s(budget=budget))['verdict']
            if v=='verified':
                self.assertEqual(evaluate(self.s(budget=budget+1))['verdict'],'verified')
    def test_no_auto_actions_count_as_user_authority(self):
        edges=[transition('collaborate','off',user_initiated=False)]
        self.assertEqual(evaluate(self.s(edges=edges,budget=100))['verdict'],'blocked')
    def test_cannot_transit_blocked_edge(self):
        self.assertEqual(evaluate(self.s(edges=[transition('collaborate','off','blocked')]))['verdict'],'blocked')
    def test_multihop_finds_shortest(self):
        ed=[transition('collaborate','off',cost=12,name='long'),transition('collaborate','consult',cost=2,name='a'),transition('consult','off',cost=2,name='b')]
        r=evaluate(self.s(edges=ed,budget=6))
        self.assertEqual(r['path'],['a','b']); self.assertEqual(r['cost_minutes'],4)
    def test_false_claimed_shortcut_does_not_obscure_verified_path(self):
        ed=[transition('collaborate','off','claimed',cost=1),transition('collaborate','consult',cost=1),transition('consult','off',cost=1)]
        self.assertEqual(evaluate(self.s(edges=ed,budget=2))['verdict'],'verified')
    def test_return_reachable(self):
        self.assertEqual(evaluate(self.s(cur='off',dst='consult'))['verdict'],'verified')
    def test_return_blocked(self):
        self.assertEqual(evaluate(self.s(cur='off',dst='consult',edges=standard_edges(consent='blocked')))['verdict'],'blocked')
    def test_exception_negative_friction(self):
        with self.assertRaises(ValueError):transition('off','consult',cost=-1)
    def test_exception_bad_mode(self):
        with self.assertRaises(ValueError):Transition('???','off',1,'verified')
    def test_exception_self_transition(self):
        with self.assertRaises(ValueError):transition('off','off')
    def test_exception_bad_evidence(self):
        with self.assertRaises(ValueError):Transition('off','consult',1,'invented')
    def test_exception_negative_sessions(self):
        with self.assertRaises(ValueError):self.s(sessions=-1)
    def test_exception_bool_friction(self):
        with self.assertRaises(ValueError):Transition('off','consult',True,'verified')
    def test_symmetric_usage_observations(self):
        for good,bad in make_corpus().values():
            self.assertEqual([usage_only(s) for s in good],[usage_only(s) for s in bad])
    def test_exactly_one_relevance_negative_control(self):
        b=benchmark()
        self.assertEqual(b['pairs'],8)
        self.assertEqual(b['matched_usage_pairs'],8)
        self.assertEqual(b['different_surface_verdicts'],7)
    def test_negative_control_does_not_flag_irrelevant_constraint(self):
        a,b=make_corpus()['accessibility_free_continuation']
        self.assertEqual(evaluate(a[0])['verdict'],evaluate(b[0])['verdict'])
    def test_consent_change_changes_result_not_sessions(self):
        w=preference_change_demo()['weeks']
        self.assertTrue(all(x['use_sessions']==5 for x in w))
        self.assertEqual([(x['open'],x['constrained']) for x in w], [('at_target','at_target')]*2+[('verified','blocked')]*2)
    def test_return_is_legitimate_preference(self):
        self.assertEqual(reverse_consent_probe()['open'],'verified')
        self.assertEqual(reverse_consent_probe()['no_return'],'blocked')
    def test_no_person_scoring(self):
        for p in make_corpus().values():
            for side in p:
                for s in side:
                    self.assertIsNone(evaluate(s)['human_sovereignty_score'])
    def test_all_cases_represent_four_weeks(self):
        for sides in make_corpus().values():
            self.assertTrue(all(len(s)==4 for s in sides))
    def test_slightly_more_friction_can_block(self):
        self.assertEqual(evaluate(self.s(budget=4,edges=[transition('collaborate','off',cost=4)]))['verdict'],'verified')
        self.assertEqual(evaluate(self.s(budget=4,edges=[transition('collaborate','off',cost=5)]))['verdict'],'blocked')
    def test_reduction_of_knowledge_never_increases_certainty(self):
        s=self.s(edges=[transition('collaborate','off','verified')])
        self.assertEqual(evaluate(s)['verdict'],'verified')
        self.assertEqual(evaluate(replace(s,edges=(transition('collaborate','off','unknown'),)))['verdict'],'unknown')
    def test_frequency_alone_cannot_identify_exit_rights(self):
        a,b=make_corpus()['desire_to_leave']
        self.assertEqual([s.sessions for s in a],[s.sessions for s in b])
        self.assertNotEqual(evaluate(a[-1])['verdict'],evaluate(b[-1])['verdict'])

    def test_graph_oracle_exhaustive_three_edge_chains(self):
        # Independent exhaustive enumeration for one 3-edge chain; compare
        # evidence class and budget to the graph algorithm. 4^3 * 3^3 * 7.
        modes=['delegate','collaborate','consult','off']
        statuses=['verified','claimed','unknown','blocked']
        costs=[0,2,4]
        for sts in itertools.product(statuses,repeat=3):
          for cst in itertools.product(costs,repeat=3):
           edges=tuple(transition(modes[i],modes[i+1],sts[i],cst[i]) for i in range(3))
           for budget in range(7):
            if sum(cst)>budget or 'blocked' in sts: expected='blocked'
            elif 'unknown' in sts: expected='unknown'
            elif 'claimed' in sts: expected='claimed_only'
            else:expected='verified'
            got=evaluate(self.s(cur='delegate',dst='off',edges=edges,budget=budget))['verdict']
            self.assertEqual(got,expected,(sts,cst,budget))

if __name__=='__main__':unittest.main()
