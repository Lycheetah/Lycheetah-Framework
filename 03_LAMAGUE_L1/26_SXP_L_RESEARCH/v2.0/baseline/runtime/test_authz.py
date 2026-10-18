"""Deterministic reference-gate checks; no production security claim."""
import copy
import unittest
from authz import (decision,sign_fixture,grant_claims,revoke_claims,receipt)
from consent import parse_expression,interpret

KEY=b'secret-test-key-at-least-sixteen'
OTHER=b'other-test-key-at-least-sixteen'

class GateTests(unittest.TestCase):
    def setUp(self):
        self.grant=grant_claims('gfirst','owner','agena','send_email','darafa',100,200)
        self.signed=sign_fixture(self.grant,KEY)
        self.req={'grantee':'agena','operation':'send_email','resource':'darafa'}
        self.keys={'owner':KEY}
        self.ownership={'owner':{'darafa'}}
    def check(self,events=None,req=None,now=150,keys=None,ownership=None):
        return decision(self.req if req is None else req,
                        [self.signed] if events is None else events,
                        self.keys if keys is None else keys,
                        self.ownership if ownership is None else ownership,now=now)
    def test_allow_exact_authenticated_scope(self):
        self.assertTrue(self.check()['allowed'])
    def test_no_grant_denied(self):
        self.assertFalse(self.check(events=[])['allowed'])
    def test_expired_denied(self):
        self.assertEqual('DENY_NO_LIVE_GRANT',self.check(now=200)['code'])
    def test_not_active_yet_denied(self):
        self.assertFalse(self.check(now=99)['allowed'])
    def test_wrong_actor_denied(self):
        self.assertFalse(self.check(req={**self.req,'grantee':'nara'})['allowed'])
    def test_wrong_action_denied(self):
        self.assertFalse(self.check(req={**self.req,'operation':'delete_file'})['allowed'])
    def test_wrong_resource_denied(self):
        self.assertFalse(self.check(req={**self.req,'resource':'rapora'})['allowed'])
    def test_revoked_denied(self):
        rev=sign_fixture(revoke_claims(self.grant,149),KEY)
        self.assertEqual('DENY_REVOKED',self.check(events=[self.signed,rev])['code'])
    def test_future_revocation_is_not_yet_active(self):
        rev=sign_fixture(revoke_claims(self.grant,160),KEY)
        self.assertTrue(self.check(events=[self.signed,rev])['allowed'])
    def test_tampering_denied(self):
        fake=copy.deepcopy(self.signed);fake['claims']['resource']='rapora'
        self.assertFalse(self.check(events=[fake])['allowed'])
    def test_wrong_mac_denied(self):
        fake=copy.deepcopy(self.signed);fake['mac']='a'*64
        self.assertFalse(self.check(events=[fake])['allowed'])
    def test_untrusted_issuer_denied(self):
        self.assertFalse(self.check(keys={})['allowed'])
    def test_signer_without_resource_ownership_denied(self):
        self.assertFalse(self.check(ownership={'owner':{'rapora'}})['allowed'])
    def test_invalid_time_denied(self):
        self.assertFalse(self.check(now='150')['allowed'])
    def test_malformed_event_denied(self):
        for bad in ({'claims':[], 'mac':[]}, {'claims':{},'mac':None},
                    {'claims':{**self.grant,'operation':['send_email']},'mac':'a'*64}):
            with self.subTest(bad=bad):self.assertFalse(self.check(events=[bad])['allowed'])
    def test_invalid_request_denied(self):
        for bad in ({**self.req,'operation':['send_email']}, {'operation':'send_email'},
                    {**self.req,'resource':'*'}):
            with self.subTest(bad=bad):self.assertFalse(self.check(req=bad)['allowed'])
    def test_duplicate_grant_id_denied(self):
        self.assertEqual('DENY_DUPLICATE_GRANT_ID',self.check(events=[self.signed,self.signed])['code'])
    def test_duplicate_revocation_denied(self):
        r=sign_fixture(revoke_claims(self.grant,140),KEY)
        self.assertFalse(self.check(events=[self.signed,r,r])['allowed'])
    def test_wrong_scope_revoke_denied(self):
        r=revoke_claims(self.grant,140);r['grantee']='nara'
        bad=sign_fixture(r,KEY)
        self.assertEqual('DENY_REVOCATION_SCOPE_MISMATCH',self.check(events=[self.signed,bad])['code'])
    def test_unverified_text_never_upgrades_rights(self):
        text='mi periva gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora'
        self.assertFalse(interpret(parse_expression(text))['authorizes'])
        self.assertFalse(self.check(events=[])['allowed'])
    def test_thousand_untrusted_utterances_still_not_authorized(self):
        text='mi periva gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora'
        parsed=parse_expression(text)
        for _ in range(1000):
            self.assertFalse(interpret(parsed)['authorizes'])
        self.assertFalse(self.check(events=[])['allowed'])
    def test_high_impact_requires_human_approval_flag_from_signer(self):
        grant=grant_claims('gsecond','owner','agena','send_email','darafa',100,200,'ordinary')
        with self.assertRaises(ValueError):sign_fixture(grant,KEY)
    def test_readonly_ordinary_approval_allowed(self):
        grant=grant_claims('gread','owner','agena','read_file','darafa',100,200,'ordinary')
        self.assertTrue(self.check(events=[sign_fixture(grant,KEY)],req={**self.req,'operation':'read_file'})['allowed'])
    def test_bounded_ttl_required(self):
        grant=grant_claims('gsecond','owner','agena','send_email','darafa',100,100+86401)
        with self.assertRaises(ValueError):sign_fixture(grant,KEY)
    def test_false_true_boolean_numeric_is_invalid(self):
        bad={**self.grant,'not_before':True}
        with self.assertRaises(ValueError):sign_fixture(bad,KEY)
    def test_receipt_is_deterministic_not_external_proof(self):
        d=self.check();r=receipt(self.req,[self.signed],d,150)
        self.assertEqual(r,receipt(self.req,[self.signed],d,150))
        self.assertIn('fingerprint',r['integrity_claim'])
    def test_revocation_has_priority_over_matching_grant(self):
        rev=sign_fixture(revoke_claims(self.grant,110),KEY)
        self.assertFalse(self.check(events=[self.signed,rev])['allowed'])
    def test_invalid_event_in_list_causes_fail_closed(self):
        self.assertEqual('DENY_UNVERIFIED_EVIDENCE',self.check(events=[self.signed,{'bad':'event'}])['code'])

if __name__=='__main__':unittest.main()
