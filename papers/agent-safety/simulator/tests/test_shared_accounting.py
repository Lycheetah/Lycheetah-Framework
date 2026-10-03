"""Self-authored multi-broker regressions, with both permission stores."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event
import unittest

from safety_sim.authority import CapabilityAuthority, ConventionalACL
from safety_sim.broker import Broker
from safety_sim.fixtures import fresh, full_scope
from safety_sim.model import State
from safety_sim.world import FakeService


ARMS = (CapabilityAuthority, ConventionalACL)


class SharedAccountingTests(unittest.TestCase):
    def each_arm(self, exercise):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                exercise(arm)

    def other(self, f, service=None):
        return Broker(f.authority, f.gate, service or f.service)

    def test_second_broker_cannot_reset_one_unit_allowance(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            other = self.other(f)
            self.assertIs(f.broker.ledger, other.ledger)
            first = f.broker.submit(f.session, f.root, f.send('first'))
            second = other.submit(f.session, f.root, f.send('second'))
            self.assertEqual(first.state, State.CONFIRMED)
            self.assertEqual(second.state, State.REJECTED)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertEqual(sum(a.spent for a in f.authority.ledger.accounts().values()), 1)
        self.each_arm(exercise)

    def test_children_on_different_brokers_share_the_root(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            left_session, left = f.worker('left')
            right_session, right = f.worker('right')
            self.assertEqual(f.broker.submit(left_session, left, f.send('left')).state, State.CONFIRMED)
            self.assertEqual(self.other(f).submit(right_session, right, f.send('right')).state, State.REJECTED)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_concurrent_distinct_effects_respect_shared_ceiling(self):
        def exercise(arm):
            f = fresh(arm, budget=5)
            brokers = [self.other(f) for _ in range(8)]
            def submit(index):
                return brokers[index % 8].submit(f.session, f.root, f.send(f'effect-{index}'))
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(submit, range(24)))
            self.assertEqual(sum(r.state == State.CONFIRMED for r in results), 5)
            self.assertEqual(len(f.service.effects()), 5)
            self.assertEqual(sum(a.spent for a in f.authority.ledger.accounts().values()), 5)
            self.assertTrue(all(a.reserved == 0 for a in f.authority.ledger.accounts().values()))
        self.each_arm(exercise)

    def test_cross_broker_replay_is_observation_without_double_charge(self):
        def exercise(arm):
            f = fresh(arm)
            action = f.send()
            original = f.broker.submit(f.session, f.root, action)
            replay = self.other(f).submit(f.session, f.root, action)
            self.assertEqual(replay, original)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertEqual(sum(a.spent for a in f.authority.ledger.accounts().values()), 1)
            self.assertEqual(sum(e.kind == 'ADMIT' for e in f.authority.events()), 1)
        self.each_arm(exercise)

    def test_concurrent_replays_across_brokers_have_one_admission(self):
        def exercise(arm):
            f = fresh(arm)
            brokers = [self.other(f) for _ in range(8)]
            action = f.send()
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda i: brokers[i % 8].submit(f.session, f.root, action), range(24)))
            self.assertTrue(all(r.state in {State.ADMITTED, State.DISPATCHED, State.CONFIRMED} for r in results))
            self.assertEqual(len(f.service.effects()), 1)
            self.assertEqual(sum(a.spent for a in f.authority.ledger.accounts().values()), 1)
            self.assertEqual(sum(e.kind == 'ADMIT' for e in f.authority.events()), 1)
        self.each_arm(exercise)

    def test_cross_broker_unknown_reservation_blocks_then_reconciles_once(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            action = f.send()
            f.service.inject_fault(action.effect_id, 'TIMEOUT_AFTER_ACCEPT')
            self.assertEqual(f.broker.submit(f.session, f.root, action).state, State.UNKNOWN)
            other = self.other(f)
            self.assertEqual(other.submit(f.session, f.root, f.send('next')).state, State.REJECTED)
            self.assertEqual(other.submit(f.session, f.root, action).state, State.UNKNOWN)
            self.assertEqual(other.reconcile(f.session, action.effect_id).state, State.CONFIRMED)
            self.assertEqual(f.broker.reconcile(f.session, action.effect_id).state, State.CONFIRMED)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertTrue(all(a.spent == 1 and a.reserved == 0 for a in f.authority.ledger.accounts().values()))
        self.each_arm(exercise)

    def test_pending_dispatch_holds_capacity_across_brokers(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            admitted, release = Event(), Event()
            def pause(_):
                admitted.set()
                if not release.wait(5):
                    raise RuntimeError('test controller did not release dispatch')
            f.broker.before_dispatch = pause
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending = pool.submit(f.broker.submit, f.session, f.root, f.send('pending'))
                try:
                    self.assertTrue(admitted.wait(5))
                    self.assertEqual(self.other(f).submit(f.session, f.root, f.send('other')).state, State.REJECTED)
                finally:
                    release.set()
                self.assertEqual(pending.result(timeout=5).state, State.CONFIRMED)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_certified_no_effect_releases_capacity_for_other_broker(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            action = f.send('failure')
            f.service.inject_fault(action.effect_id, 'FAIL_BEFORE_ACCEPT')
            self.assertEqual(f.broker.submit(f.session, f.root, action).state, State.FAILED)
            self.assertEqual(self.other(f).submit(f.session, f.root, f.send('replacement')).state, State.CONFIRMED)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_replay_cannot_substitute_actor_request_or_adapter(self):
        def exercise(arm):
            f = fresh(arm)
            action = f.send()
            f.broker.submit(f.session, f.root, action)
            other = self.other(f)
            stranger = f.authority.open_session('stranger')
            self.assertEqual(other.submit(stranger, f.root, action).state, State.REJECTED)
            self.assertEqual(other.submit(f.session, f.root, replace(action, recipient='guest')).state, State.REJECTED)
            service = FakeService()
            different_adapter = self.other(f, service)
            self.assertEqual(different_adapter.submit(f.session, f.root, action).state, State.REJECTED)
            self.assertEqual(different_adapter.reconcile(f.session, action.effect_id).state, State.REJECTED)
            self.assertEqual(service.effects(), ())
            self.assertEqual(sum(a.spent for a in f.authority.ledger.accounts().values()), 1)
        self.each_arm(exercise)

    def test_independent_root_allowances_remain_separate(self):
        def exercise(arm):
            f = fresh(arm, budget=1)
            grant = f.authority.issue_root('owner', full_scope(), budget=1)
            self.assertEqual(f.broker.submit(f.session, f.root, f.send('root-1')).state, State.CONFIRMED)
            self.assertEqual(self.other(f).submit(f.session, grant, f.send('root-2')).state, State.CONFIRMED)
            self.assertEqual(len(f.authority.ledger.accounts()), 2)
        self.each_arm(exercise)


if __name__ == '__main__':
    unittest.main()
