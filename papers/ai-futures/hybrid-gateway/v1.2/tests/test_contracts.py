"""v0.4 independent contract-boundary cases; all policies are fictional."""
import unittest
from dataclasses import replace

from hybrid_gateway import (
    HybridGateway, SourceDocument, ClaimProposal, ScriptedNeuralAdapter,
    TrustedClause, TrustedContractRegistry, ContractedHybridPipeline,
    EvidenceBindingError, BoundStage,
)

AT = '2026-10-01T00:00:00Z'
KNOW = '2026-10-04T00:00:00Z'
SRC = SourceDocument('policy-42', 'shop-A', 'urn:fictional:shop-A',
    'Refunds allowed within 14 days. Loyalty members earn 21 points per order. '
    'EXAMPLE ONLY: Refunds allowed within 60 days. '
    'Refunds not allowed within 90 days. Online orders: refunds within 10 days.')
REFUND = 'Refunds allowed within 14 days.'
LOYAL = 'Loyalty members earn 21 points per order.'
ONLINE = 'Online orders: refunds within 10 days.'


def clause(quote=REFUND, **kwargs):
    args = dict(source_id=SRC.source_id, source_digest=SRC.digest, tenant=SRC.tenant,
        subject='refunds', predicate='window_days', scope='store', exact_quote=quote,
        grammar='refund_days_v1', effective_from=AT)
    args.update(kwargs)
    return TrustedClause(**args)


def candidate(quote=REFUND, val='14', **kwargs):
    args = dict(claim_id='model-a', tenant=SRC.tenant, subject='refunds',
        predicate='window_days', scope='store', value=val, valid_from=AT,
        source_id=SRC.source_id, evidence_quote=quote)
    args.update(kwargs)
    return ClaimProposal(**args)


def rig(cases, contracts=None):
    r = TrustedContractRegistry([SRC], contracts or [clause()])
    g = HybridGateway(semantic_validator=r.validate_claim)
    g.register_source(SRC)
    p = ContractedHybridPipeline(g, ScriptedNeuralAdapter('fixture', {SRC.source_id: cases}), r)
    return r, g, p


class EvidenceContractsTests(unittest.TestCase):
    def test_positive_end_to_end_and_time_travel(self):
        r, g, p = rig([candidate()])
        staged = p.stage(SRC)
        self.assertEqual(len(staged), 1)
        self.assertFalse(g.events)
        self.assertEqual(p.commit_one(staged[0], recorded_at=KNOW).disposition, 'REVIEW')
        self.assertEqual(p.commit_one(staged[0], recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')
        k = dict(tenant='shop-A', subject='refunds', predicate='window_days', scope='store', effective_at=KNOW)
        self.assertEqual(g.query(**k, known_at=KNOW).value, '14')
        self.assertEqual(g.query(**k, known_at='2026-10-03T00:00:00Z').disposition, 'ABSTAIN_NO_EVIDENCE')
        self.assertTrue(g.verify_chain(anchored_head=g.head_digest))

    def test_contract_is_not_a_model_proposal(self):
        contract = clause()
        self.assertEqual(contract.parsed_value, '14')
        self.assertEqual(contract.effective_from, AT)
        self.assertTrue(contract.fingerprint.startswith('sha256:'))
        with self.assertRaises(ValueError):
            clause(grammar='anything_goes')
        with self.assertRaises(ValueError):
            clause(subject='loyalty')
        with self.assertRaises(ValueError):
            clause(quote='Refunds not allowed within 14 days.')
        with self.assertRaises(ValueError):
            clause(quote='Refunds allowed within 14 days. Except sale items.')

    def test_quote_and_number_are_not_automatic_authority(self):
        wrong = [
            candidate(quote='Refunds allowed within 60 days.', val='60'),
            candidate(quote='Refunds not allowed within 90 days.', val='90'),
            candidate(quote=LOYAL, val='21'),
            candidate(val='1'), candidate(val='140'),
            candidate(scope='online'), candidate(subject='loyalty'),
            candidate(tenant='shop-B'), candidate(source_id='fake'),
            candidate(valid_from='2026-09-01T00:00:00Z'),
            candidate(valid_until='2026-11-01T00:00:00Z'),
            candidate(supersedes=('old-unapproved',)),
        ]
        for c in wrong:
            with self.subTest(claim=c), self.assertRaises((EvidenceBindingError, ValueError)):
                r, g, p = rig([c])
                p.stage(SRC)
            self.assertFalse(g.claims)

    def test_batch_with_one_adversarial_candidate_never_stages(self):
        _, g, p = rig([candidate(), candidate(quote=LOYAL, val='21', claim_id='bad')])
        with self.assertRaises(EvidenceBindingError):
            p.stage(SRC)
        self.assertIsNone(g.head_digest)

    def test_operator_must_choose_correct_policy_scope(self):
        online_contract = clause(quote=ONLINE, grammar='online_refund_days_v1', scope='online')
        online_claim = candidate(quote=ONLINE, val='10', scope='online')
        _, g, p = rig([online_claim], [online_contract])
        self.assertEqual(p.commit_one(p.stage(SRC)[0], recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')
        self.assertEqual(g.query(tenant='shop-A', subject='refunds', predicate='window_days',
                                scope='store', effective_at=KNOW, known_at=KNOW).disposition, 'ABSTAIN_NO_EVIDENCE')
        _, _, bad_pipeline = rig([candidate(quote=ONLINE, val='10', scope='store')], [online_contract])
        with self.assertRaises(EvidenceBindingError):
            bad_pipeline.stage(SRC)

    def test_second_domain_does_not_mix_predicates(self):
        c = clause(quote=LOYAL, grammar='loyalty_points_v1', subject='loyalty',
                   predicate='points_per_order', scope='members')
        p = candidate(quote=LOYAL, val='21', subject='loyalty', predicate='points_per_order', scope='members')
        _, g, pipe = rig([p], [c])
        self.assertEqual(pipe.commit_one(pipe.stage(SRC)[0], recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')
        self.assertEqual(g.query(tenant='shop-A', subject='loyalty', predicate='points_per_order',
                                scope='members', effective_at=KNOW, known_at=KNOW).value, '21')

    def test_duplicate_quote_in_source_is_ambiguous(self):
        source = SourceDocument('policy-42', 'shop-A', 'urn:fictional:shop-A',
                                'Refunds allowed within 14 days. Refunds allowed within 14 days.')
        with self.assertRaises(ValueError):
            TrustedContractRegistry([source], [replace(clause(), source_digest=source.digest)])

    def test_source_digest_is_required(self):
        with self.assertRaises(ValueError):
            TrustedContractRegistry([SRC], [clause(source_digest='sha256:bogus')])
        with self.assertRaises(ValueError):
            TrustedContractRegistry([SRC], [clause(), clause()])

    def test_wrong_validator_or_unregistered_source_refused(self):
        r = TrustedContractRegistry([SRC], [clause()])
        with self.assertRaises(ValueError):
            ContractedHybridPipeline(HybridGateway(semantic_validator=lambda p: True),
                ScriptedNeuralAdapter('fixture', {}), r)
        with self.assertRaises(ValueError):
            ContractedHybridPipeline(HybridGateway(semantic_validator=r.validate_claim),
                ScriptedNeuralAdapter('fixture', {}), r)

    def test_post_stage_swap_or_new_registry_blocked(self):
        r, g, p = rig([candidate()])
        item = p.stage(SRC)[0]
        replaced = replace(item, registry_fingerprint='sha256:tamper')
        self.assertEqual(p.commit_one(replaced, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        forged = replace(item, staged=replace(item.staged, candidate=candidate(val='21')))
        self.assertEqual(p.commit_one(forged, recorded_at=KNOW, reviewer_approved=True).disposition, 'REVIEW')
        self.assertFalse(g.claims)

    def test_post_stage_source_rebinding_even_at_same_digest_blocks(self):
        r, g, p = rig([candidate()])
        item = p.stage(SRC)[0]
        g.sources[SRC.source_id] = SourceDocument(SRC.source_id, SRC.tenant, 'urn:wrong-uri', SRC.body)
        self.assertEqual(p.commit_one(item, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(g.claims)

    def test_validator_swap_blocks_even_if_bypass_would_allow(self):
        r, g, p = rig([candidate()])
        item = p.stage(SRC)[0]
        g.semantic_validator = lambda proposal: True
        self.assertEqual(p.commit_one(item, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(g.events)

    def test_fixture_neural_adapter_enters_only_contract_bound_stage(self):
        import json
        from hybrid_gateway import OpenAICompatibleAdapter, ProviderConfig, ExtractionTarget
        raw = {"subject": "refunds", "predicate": "window_days", "scope": "store",
               "value": "14", "valid_from": AT, "valid_until": None,
               "evidence_quote": REFUND, "supersedes": []}
        response = {"choices": [{"message": {"content": json.dumps({"claims": [raw]})}}]}
        adapter = OpenAICompatibleAdapter(ProviderConfig('fixture-model'),
            ExtractionTarget('refunds', 'window_days', 'store', AT),
            transport=lambda url, request, config: response)
        registry = TrustedContractRegistry([SRC], [clause()])
        gateway = HybridGateway(semantic_validator=registry.validate_claim)
        gateway.register_source(SRC)
        pipe = ContractedHybridPipeline(gateway, adapter, registry)
        stages = pipe.stage(SRC)
        self.assertEqual(len(stages), 1)
        self.assertFalse(gateway.events)
        self.assertEqual(pipe.commit_one(stages[0], recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')

    def test_supersession_edges_require_trusted_contract_and_existing_prior_claim(self):
        # No prior admitted claim: despite an operator-approved edge, ledger must BLOCK.
        r, g, p = rig([candidate(supersedes=('prior',))], [clause(permitted_supersedes=('prior',))])
        self.assertEqual(p.commit_one(p.stage(SRC)[0], recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(g.claims)

    def test_unconfigured_policy_language_abstains(self):
        # Known limitation: grammars are not universal. This is a deliberate false-abstain.
        with self.assertRaises(ValueError):
            clause(quote='For returns, customers get a fortnight to ask for their money back.')


if __name__ == '__main__':
    unittest.main()
