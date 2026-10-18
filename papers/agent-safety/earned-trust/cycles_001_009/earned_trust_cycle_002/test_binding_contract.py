import unittest
from transactional_provider import Intent
from binding_contract import verify_action_binding

class BindingTest(unittest.TestCase):
    def setUp(self):
        self.intent = Intent("e1","a1","agent","order",1200)
        self.action = self.intent.payload()

    def test_exact_match(self):
        self.assertTrue(verify_action_binding(self.action,dict(self.action),self.intent).valid)

    def test_guard_substitution(self):
        swapped={**self.action,"amount_cents":1300}
        self.assertEqual(verify_action_binding(self.action,swapped,self.intent).reason,
                         "event-vs-guard-action-mismatch")

    def test_provider_substitution(self):
        changed = Intent("e1","a1","agent","other-order",1200)
        self.assertEqual(verify_action_binding(self.action,self.action,changed).reason,
                         "guard-vs-provider-action-mismatch")

    def test_extra_fields_rejected(self):
        action={**self.action,"approval_claim":"self-attested"}
        self.assertEqual(verify_action_binding(action,action,self.intent).reason,"invalid-schema")

    def test_missing_fields_rejected(self):
        action={"amount_cents":1200,"subject":"order"}
        self.assertFalse(verify_action_binding(action,action,self.intent).valid)

    def test_bool_amount_rejected(self):
        action={**self.action,"amount_cents":True}
        self.assertFalse(verify_action_binding(action,action,self.intent).valid)

if __name__ == "__main__":unittest.main()
