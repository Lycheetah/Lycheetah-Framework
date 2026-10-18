"""v0.5 coverage protocol; fictional source, no LLM inference."""
import unittest
from dataclasses import replace

from hybrid_gateway import (
    SourceDocument, HybridGateway, TrustedClause, TrustedContractRegistry,
    ClaimProposal, ScriptedNeuralAdapter, ExtractionPlan, CoverageAuditor,
)
from tests.test_contracts import SRC, REFUND, LOYAL, AT, KNOW, clause, candidate


def loyalty_clause():
    return clause(quote=LOYAL, grammar='loyalty_points_v1', subject='loyalty',
                  predicate='points_per_order', scope='members')


def loyalty_candidate(cid='points-a'):
    return candidate(quote=LOYAL, val='21', subject='loyalty',
                     predicate='points_per_order', scope='members', claim_id=cid)


def rig(candidates, *, both=False, selected=None, source=SRC):
    clauses = [clause()] + ([loyalty_clause()] if both else [])
    registry = TrustedContractRegistry([source], clauses)
    gateway = HybridGateway(semantic_validator=registry.validate_claim)
    gateway.register_source(source)
    plan = ExtractionPlan.create(registry, source.source_id, selected=selected)
    adapter = ScriptedNeuralAdapter('fixture', {source.source_id: candidates})
    auditor = CoverageAuditor(gateway, adapter, registry, plan)
    return gateway, registry, plan, auditor


class CoverageAuditTests(unittest.TestCase):
    def test_complete_batch_staged_and_requires_review(self):
        g, r, plan, audit = rig([candidate()])
        batch = audit.audit(SRC)
        self.assertEqual(batch.receipt.disposition, 'READY_FOR_REVIEW')
        self.assertEqual((batch.receipt.expected, batch.receipt.received, batch.receipt.supported_unique), (1, 1, 1))
        self.assertEqual(len(batch.stages), 1)
        self.assertEqual(audit.commit_one(batch, 0, recorded_at=KNOW).disposition, 'REVIEW')
        self.assertIsNone(g.head_digest)
        self.assertEqual(audit.commit_one(batch, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')
        self.assertTrue(g.verify_chain(anchored_head=g.head_digest))

    def test_empty_model_response_cannot_hide_required_clause(self):
        g, _, _, auditor = rig([])
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'REVIEW_MISSING')
        self.assertEqual(len(b.receipt.missing_fingerprints), 1)
        self.assertEqual(b.stages, ())
        self.assertEqual(auditor.commit_one(b, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'REVIEW')
        self.assertFalse(g.events)

    def test_partial_two_clause_response_detected(self):
        g, _, _, auditor = rig([candidate()], both=True)
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'REVIEW_MISSING')
        self.assertEqual((b.receipt.expected, b.receipt.supported_unique), (2, 1))
        self.assertFalse(b.stages)
        self.assertFalse(g.claims)

    def test_two_clauses_both_present(self):
        _, _, _, audit = rig([loyalty_candidate(), candidate()], both=True)
        b = audit.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'READY_FOR_REVIEW')
        self.assertEqual((b.receipt.expected, len(b.stages)), (2, 2))

    def test_duplicate_matching_claim_detected(self):
        g, _, _, auditor = rig([candidate(), candidate(claim_id='second')])
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'REVIEW_DUPLICATE')
        self.assertEqual(len(b.receipt.duplicate_fingerprints), 1)
        self.assertFalse(b.stages)
        self.assertFalse(g.events)

    def test_unexpected_extra_converts_to_review(self):
        _, _, _, auditor = rig([candidate(), candidate(val='60', quote='Refunds allowed within 60 days.', claim_id='bad')])
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'REVIEW_UNEXPECTED')
        self.assertEqual(len(b.receipt.unexpected_candidate_digests), 1)
        self.assertFalse(b.stages)

    def test_simultaneously_missing_and_unexpected_is_mixed(self):
        _, _, _, auditor = rig([candidate(val='60', quote='Refunds allowed within 60 days.')])
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'REVIEW_MIXED')
        self.assertEqual(len(b.receipt.missing_fingerprints), 1)

    def test_selected_subset_does_not_expand_to_other_clause(self):
        r = TrustedContractRegistry([SRC], [clause(), loyalty_clause()])
        selected = (r.contracts_for_source(SRC.source_id)[0].fingerprint,)
        g, reg, plan, auditor = rig([candidate()], both=True, selected=selected)
        self.assertEqual(auditor.audit(SRC).receipt.disposition, 'READY_FOR_REVIEW')
        _, _, _, other = rig([candidate(), loyalty_candidate()], both=True, selected=selected)
        self.assertEqual(other.audit(SRC).receipt.disposition, 'REVIEW_UNEXPECTED')

    def test_explicit_empty_plan_abstains_correctly(self):
        _, _, _, auditor = rig([], selected=())
        b = auditor.audit(SRC)
        self.assertEqual(b.receipt.disposition, 'READY_FOR_REVIEW')
        self.assertEqual((b.receipt.expected, b.receipt.received, b.stages), (0, 0, ()))
        self.assertEqual(auditor.commit_one(b, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')

    def test_empty_plan_rejects_any_candidate(self):
        _, _, _, auditor = rig([candidate()], selected=())
        self.assertEqual(auditor.audit(SRC).receipt.disposition, 'REVIEW_UNEXPECTED')

    def test_foreign_tenant_is_not_supported(self):
        _, _, _, auditor = rig([candidate(tenant='shop-B')])
        self.assertEqual(auditor.audit(SRC).receipt.disposition, 'REVIEW_MIXED')

    def test_ledger_advancing_between_audit_and_review_forces_reaudit(self):
        g, _, _, auditor = rig([candidate()])
        b = auditor.audit(SRC)
        g.withdraw('not-a-claim', effective_from=AT, recorded_at=KNOW, reviewer_approved=True)
        # Non-admitted withdrawal does not change head. Instead admit a legitimate
        # different, explicitly approved claim directly through the gateway.
        manual = replace(candidate(), claim_id='already-admitted')
        self.assertEqual(g.ingest(manual, recorded_at=KNOW, reviewer_approved=True).disposition, 'ALLOW')
        self.assertEqual(auditor.commit_one(b, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'REVIEW')

    def test_stage_payload_tampering_blocked(self):
        from hybrid_gateway import AuditedBatch
        g, _, _, auditor = rig([candidate()], both=True,
                               selected=(clause().fingerprint,))
        b = auditor.audit(SRC)
        forged = AuditedBatch(b.receipt, (replace(b.stages[0], staged=replace(
            b.stages[0].staged, candidate=replace(candidate(), claim_id='forged'))),))
        self.assertEqual(auditor.commit_one(forged, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(g.events)

    def test_approval_boolean_alone_cannot_override_bad_batch(self):
        g, _, _, auditor = rig([])
        b = auditor.audit(SRC)
        d = auditor.commit_one(b, 0, recorded_at=KNOW, reviewer_approved=True)
        self.assertEqual(d.disposition, 'REVIEW')
        self.assertFalse(g.events)

    def test_plan_fingerprint_change_forces_rejection(self):
        g, r, plan, auditor = rig([candidate()])
        b = auditor.audit(SRC)
        from hybrid_gateway import AuditedBatch
        forged = AuditedBatch(replace(b.receipt, plan_fingerprint='sha256:wrong'), b.stages)
        self.assertEqual(auditor.commit_one(forged, 0, recorded_at=KNOW, reviewer_approved=True).disposition, 'BLOCK')
        self.assertFalse(g.events)

    def test_cannot_make_plan_for_foreign_clause(self):
        g, r, plan, auditor = rig([candidate()])
        with self.assertRaises(ValueError):
            ExtractionPlan.create(r, SRC.source_id, selected=('sha256:unregistered',))
        with self.assertRaises(ValueError):
            ExtractionPlan.create(r, SRC.source_id, selected=(clause().fingerprint, clause().fingerprint))

    def test_source_mutation_before_audit_rejected(self):
        g, _, _, auditor = rig([candidate()])
        g.sources[SRC.source_id] = replace(SRC, uri='urn:changed')
        with self.assertRaises(ValueError):
            auditor.audit(SRC)

    def test_bad_adapter_object_rejected(self):
        g, r, p, a = rig([])
        a.adapter.extract = lambda source: ['not a claim']
        with self.assertRaises(ValueError):
            a.audit(SRC)
        self.assertFalse(g.events)

    def test_no_duplicate_plan_slot(self):
        g, r, p, a = rig([candidate()])
        with self.assertRaises(ValueError):
            CoverageAuditor(g, a.adapter, r, replace(p,
                required_contract_fingerprints=p.required_contract_fingerprints * 2))

if __name__ == '__main__':
    unittest.main()
