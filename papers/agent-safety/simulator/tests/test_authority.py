from dataclasses import replace
import unittest

from safety_sim.authority import CapabilityAuthority, ConventionalACL
from safety_sim.fixtures import fresh, full_scope
from safety_sim.model import State


ARMS = (CapabilityAuthority, ConventionalACL)


class AuthorityTests(unittest.TestCase):
    def test_nested_attenuation_cannot_add_any_dimension(self):
        for arm in ARMS:
            f = fresh(arm)
            base = full_scope()
            expansions = (
                replace(base, operations=base.operations | {"delete"}),
                replace(base, objects=base.objects | {"other"}),
                replace(base, recipients=base.recipients | {"attacker"}),
                replace(base, purpose="unrelated purpose"),
            )
            for scope in expansions:
                with self.subTest(arm=arm.label, scope=scope):
                    with self.assertRaises(PermissionError):
                        f.worker("child", scope=scope)

    def test_child_cannot_outlive_parent(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                with self.assertRaises(PermissionError):
                    fresh(arm).worker("child", expires=101)

    def test_non_delegable_grant_cannot_be_forwarded(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm, delegable=False)
                with self.assertRaises(PermissionError):
                    f.worker("child")

    def test_child_cannot_redelegate_without_permission(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm)
                _, child = f.worker("child")
                with self.assertRaises(PermissionError):
                    f.worker("grandchild", parent=child)

    def test_root_revocation_blocks_grandchildren(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm)
                _, child = f.worker("child", delegable=True)
                session, grandchild = f.worker("grandchild", parent=child)
                f.authority.revoke(f.root)
                result = f.broker.submit(session, grandchild, f.send())
                self.assertEqual(result.state, State.REJECTED)
                self.assertEqual(f.service.effects(), ())

    def test_child_revocation_preserves_unrelated_sibling(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm)
                session_a, child_a = f.worker("a")
                session_b, child_b = f.worker("b")
                f.authority.revoke(child_a)
                denied = f.broker.submit(session_a, child_a, f.send("a"))
                allowed = f.broker.submit(session_b, child_b, f.send("b"))
                self.assertEqual(denied.state, State.REJECTED)
                self.assertEqual(allowed.state, State.CONFIRMED)
                self.assertEqual(len(f.service.effects()), 1)

    def test_expiry_boundary_is_exclusive(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm, expires=1)
                f.clock.advance(1)
                result = f.broker.submit(f.session, f.root, f.send())
                self.assertEqual(result.state, State.REJECTED)
                with self.assertRaises(PermissionError):
                    f.worker("child", expires=1)

    def test_delegates_share_budget_instead_of_copying_it(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm, budget=1)
                session_a, grant_a = f.worker("a")
                session_b, grant_b = f.worker("b")
                first = f.broker.submit(session_a, grant_a, f.send("a"))
                second = f.broker.submit(session_b, grant_b, f.send("b"))
                self.assertEqual(first.state, State.CONFIRMED)
                self.assertEqual(second.state, State.REJECTED)
                self.assertEqual(len(f.service.effects()), 1)

    def test_narrow_child_rejects_operation_object_and_sink(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm)
                scope = replace(full_scope(), operations=frozenset({"send_document"}),
                    objects=frozenset({"public"}), recipients=frozenset({"owner"}))
                session, child = f.worker("child", scope=scope)
                for action in (f.draft(), f.send("object", object_id="secret"),
                               f.send("sink", recipient="guest")):
                    self.assertEqual(f.broker.submit(session, child, action,
                        witness=f.witness).state, State.REJECTED)
                self.assertEqual(f.service.effects(), ())

    def test_invalid_issuer_limits_are_rejected(self):
        for arm in ARMS:
            for value in (-1, True, 1.5, float("nan")):
                with self.subTest(arm=arm.label, value=value):
                    with self.assertRaises(ValueError):
                        fresh(arm, budget=value)

    def test_mutable_scope_is_not_accepted(self):
        with self.assertRaises(ValueError):
            replace(full_scope(), objects={"public"})


if __name__ == "__main__":
    unittest.main()
