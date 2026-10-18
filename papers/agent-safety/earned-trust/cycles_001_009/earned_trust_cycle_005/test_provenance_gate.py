import copy
import unittest
from provenance_gate import (Source, TrustedRegistry, RegistryError, ProvenanceGate,
                             sign_statement, naive_signed_quorum)


def fixture():
    sources = [
        Source('original-crm','crm-operator'),
        Source('bank-ledger','bank-operator'),
        Source('network-trace','network-operator'),
        Source('copy-store','crm-operator',('original-crm',)),
        Source('witness-a','audit-provider-A',('original-crm',),True),
        Source('witness-b','audit-provider-B',('copy-store',),True),
        Source('witness-c','audit-provider-C',('bank-ledger',),True),
        Source('witness-d','audit-provider-D',('network-trace',),True),
        Source('witness-e','crm-operator',('network-trace',),True),
    ]
    keys={f'witness-{c}': (c*32).encode() for c in 'abcde'}
    registry=TrustedRegistry(sources,keys)
    return registry,ProvenanceGate(registry)


def signed(reg, sid, **kw):
    p=dict(effect_id='effect-1',action_sha256='a'*64,token_sha256='b'*64,
           status='COMMITTED',correctness='TRUE',observed_at=100,revision=1)
    p.update(kw)
    return sign_statement(reg,sid,**p)


def verdict(gate, claims, **kw):
    p=dict(effect_id='effect-1',action_sha256='a'*64,token_sha256='b'*64,
           now=105,current_revisions={w['body']['source_id']:1 for w in claims if isinstance(w,dict) and isinstance(w.get('body'),dict) and isinstance(w['body'].get('source_id'),str)})
    p.update(kw)
    return gate.evaluate(claims,**p)


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.reg,self.gate=fixture()

    def test_independent_bank_and_crm_confirm(self):
        v=verdict(self.gate,[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')])
        self.assertEqual((v.decision,v.disjoint_witnesses),('CONFIRMED',2))
    def test_network_and_bank_confirm(self):
        self.assertEqual(verdict(self.gate,[signed(self.reg,'witness-c'),signed(self.reg,'witness-d')]).decision,'CONFIRMED')
    def test_common_root_is_not_independent(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-b')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
        self.assertEqual(naive_signed_quorum(self.reg,c,effect_id='effect-1',action_sha256='a'*64,token_sha256='b'*64,now=105,current_revisions={'witness-a':1,'witness-b':1}),'CONFIRMED')
    def test_same_controller_with_different_roots_is_not_independent(self):
        self.assertEqual(verdict(self.gate,[signed(self.reg,'witness-a'),signed(self.reg,'witness-e')]).decision,'REVIEW')
    def test_shared_ancestor_detected_transitively(self):
        roots_a,_=self.reg.exposure('witness-a');roots_b,_=self.reg.exposure('witness-b')
        self.assertEqual(roots_a,roots_b)
    def test_three_with_common_pair_can_still_have_two_independent(self):
        c=[signed(self.reg,x) for x in ('witness-a','witness-b','witness-c')]
        self.assertEqual(verdict(self.gate,c).decision,'CONFIRMED')
    def test_transitive_controllers_include_original(self):
        _,ctrl=self.reg.exposure('witness-b')
        self.assertIn('crm-operator',ctrl)
    def test_registry_misclassification_can_fake_independence(self):
        # Deliberately mis-register two CRM-derived signers as distinct roots.
        roots=[Source('fake-root-1','fake-org-1'),Source('fake-root-2','fake-org-2')]
        leaves=[Source('wa','fake-a',('fake-root-1',),True),
                Source('wb','fake-b',('fake-root-2',),True)]
        registry=TrustedRegistry(roots+leaves,{'wa':b'A'*32,'wb':b'B'*32})
        gate=ProvenanceGate(registry)
        c=[signed(registry,sid) for sid in ('wa','wb')]
        # TRUE world lineage, unknown to this registry: both reused one CRM.
        self.assertEqual(verdict(gate,c).decision,'CONFIRMED')
    def test_legitimate_key_holder_can_attest_false_information(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        # Changing only external ground truth cannot change any signed bytes.
        self.assertEqual(verdict(self.gate,c).decision,'CONFIRMED')
    def test_one_false_witness_conflicts(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',correctness='FALSE')]
        self.assertEqual(verdict(self.gate,c).decision,'CONFLICT')
    def test_not_committed_conflicts(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',status='NOT_COMMITTED')]
        self.assertEqual(verdict(self.gate,c).decision,'CONFLICT')
    def test_uncertainty_requires_review(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',correctness='UNKNOWN')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_both_independent_but_false_still_confirm(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c).decision,'CONFIRMED') # latent ground truth false; cannot infer
    def test_mismatched_action_refused(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',action_sha256='x'*64)]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_mismatched_token_refused(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',token_sha256='x'*64)]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_mismatched_effect_refused(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c',effect_id='other')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_tampered_body_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        c[1]['body']['status']='NOT_COMMITTED'
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_tampered_hmac_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        c[1]['hmac_sha256']='0'*64
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_fake_signer_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        c[1]['body']['source_id']='witness-z'
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_missing_provider_proof_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c,provider_receipt_valid=False).decision,'REVIEW')
    def test_duplicate_signer_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-a')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_stale_evidence_fails(self):
        c=[signed(self.reg,'witness-a',observed_at=10),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_future_evidence_fails(self):
        c=[signed(self.reg,'witness-a',observed_at=106),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_current_revision_required(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c,current_revisions=None).reason,'current-witness-readback-unavailable')
    def test_stale_revision_fails(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c,current_revisions={'witness-a':2,'witness-c':1}).decision,'REVIEW')
    def test_current_revision_must_be_int_not_bool(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]
        self.assertEqual(verdict(self.gate,c,current_revisions={'witness-a':True,'witness-c':1}).decision,'REVIEW')
    def test_malformed_envelope_fails(self):
        self.assertEqual(verdict(self.gate,[{},signed(self.reg,'witness-c')]).decision,'REVIEW')
    def test_extra_fields_fail(self):
        c=[signed(self.reg,'witness-a'),signed(self.reg,'witness-c')]; c[0]['body']['extra']='x'
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_excess_witnesses_fail(self):
        c=[signed(self.reg,'witness-a')]*33
        self.assertEqual(verdict(self.gate,c).decision,'REVIEW')
    def test_missing_witnesses_fail(self):
        self.assertEqual(verdict(self.gate,[]).decision,'REVIEW')
    def test_source_cycle_rejected(self):
        with self.assertRaisesRegex(RegistryError,'cycle'):
            TrustedRegistry([Source('a','org',('b',)),Source('b','org',('a',))],{})
    def test_missing_source_rejected(self):
        with self.assertRaisesRegex(RegistryError,'unknown upstream'):
            TrustedRegistry([Source('a','org',('missing',))],{})
    def test_duplicate_source_rejected(self):
        with self.assertRaisesRegex(RegistryError,'unique'):
            TrustedRegistry([Source('a','org'),Source('a','org')],{})
    def test_weak_signer_key_rejected(self):
        with self.assertRaisesRegex(RegistryError,'adequate'):
            TrustedRegistry([Source('a','x'),Source('b','y',('a',),True)],{'b':b'x'})
    def test_signer_requires_upstream_lineage(self):
        with self.assertRaisesRegex(RegistryError,'root lineage'):
            TrustedRegistry([Source('a','x',(),True)],{'a':b'x'*32})
    def test_three_distinct_roots_with_min3(self):
        g=ProvenanceGate(self.reg,min_independent=3)
        c=[signed(self.reg,x) for x in ('witness-a','witness-c','witness-d')]
        self.assertEqual(verdict(g,c).decision,'CONFIRMED')
    def test_two_distinct_roots_with_min3(self):
        g=ProvenanceGate(self.reg,min_independent=3)
        c=[signed(self.reg,x) for x in ('witness-a','witness-c')]
        self.assertEqual(verdict(g,c).decision,'REVIEW')
    def test_no_automatic_relaxation_of_min(self):
        with self.assertRaises(ValueError): ProvenanceGate(self.reg,min_independent=1)


if __name__=='__main__':unittest.main()
