"""All examples synthetic. MiniCascade is explicitly a test double, not canonical."""
import tempfile
import unittest
from pathlib import Path
from dataclasses import dataclass

from hybrid_gateway.core import HybridGateway, SourceDocument, ClaimProposal
from hybrid_gateway.cascade_bridge import (EvidenceWeights, diagnose_with_cascade,
                                           gateway_snapshot_digest)
from hybrid_gateway.temporal_audit import TemporalCase, audit_temporal_cases, public_report
from hybrid_gateway.canonical_loader import (git_blob_sha, load_canonical_classes,
                                              PINNED_GIT_BLOB_SHA1)


@dataclass
class MiniBlock:
    id: str
    content: str
    domain: str
    paradigm: str
    evidence_strength: float
    explanatory_power: float
    uncertainty: float
    regime: str = 'universal'

    @property
    def truth_pressure(self):
        return self.evidence_strength * self.explanatory_power / max(self.uncertainty, .01)


class MiniCascade:
    """A *substitute* for exercising adapter mechanics only, not CASCADE validation."""
    def __init__(self):
        self.blocks = []
        self.cascade_events = []

    def add_block(self, block):
        for old in self.blocks:
            if (block.domain == old.domain and block.paradigm != old.paradigm
                    and old.regime == 'universal'
                    and block.truth_pressure > old.truth_pressure + .3):
                old.regime = 'qualified'
                self.cascade_events.append({'affected': old.id})
        self.blocks.append(block)

    def coherence(self):
        active = [x for x in self.blocks if x.regime == 'universal']
        return 1 if len({x.paradigm for x in active}) < 2 else .5


def build_fixture():
    g = HybridGateway()
    for n, text in [('s14', 'Refunds allowed within 14 days.'),
                    ('s30', 'Refunds allowed within 30 days.'),
                    ('s60', 'Refunds allowed within 60 days.')]:
        g.register_source(SourceDocument(n, 'demo', 'urn:' + n, text))
    for name, source, val, valid, recorded, supersedes in [
            ('c14', 's14', '14', '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z', ()),
            ('c30', 's30', '30', '2026-02-01T00:00:00Z', '2026-02-03T00:00:00Z', ('c14',)),
            ('c60', 's60', '60', '2026-02-01T00:00:00Z', '2026-02-05T00:00:00Z', ())]:
        p = ClaimProposal(name, 'demo', 'refunds', 'window_days', 'online', val,
                          valid, source, g.sources[source].body, supersedes=supersedes)
        assert g.ingest(p, recorded_at=recorded, reviewer_approved=True).disposition == 'ALLOW'
    return g


def tc(ident, effective, known, scope='online'):
    return TemporalCase(ident, 'demo', 'refunds', 'window_days', scope,
                        effective + 'T00:00:00Z', known + 'T00:00:00Z')


class TemporalCascadeTests(unittest.TestCase):
    def setUp(self):
        self.g = build_fixture()
        self.profiles = {
            'flat': {'c14': EvidenceWeights(.5, 1.5, .5),
                     'c30': EvidenceWeights(.5, 1.5, .5),
                     'c60': EvidenceWeights(.5, 1.5, .5)},
            '60_high': {'c14': EvidenceWeights(.5, 1.5, .5),
                        'c30': EvidenceWeights(.2, 1.0, .8),
                        'c60': EvidenceWeights(.9, 2.0, .2)}
        }

    def run_audit(self, cases, profiles=None):
        return audit_temporal_cases(self.g, cases,
                                    weight_profiles=profiles or self.profiles,
                                    engine_factory=MiniCascade, block_factory=MiniBlock)

    def test_older_effective_at_remains_historical(self):
        row = self.run_audit([tc('old', '2026-01-15', '2026-03-01')])[0]
        self.assertEqual((row.ledger_disposition, row.ledger_value), ('ANSWER', '14'))
        self.assertEqual(row.latest_known_value, '60')
        self.assertFalse(row.baseline_matches_ledger)

    def test_late_knowledge_does_not_leak_into_past(self):
        row = self.run_audit([tc('before-publication', '2026-02-10', '2026-02-02')])[0]
        self.assertEqual(row.ledger_value, '14')
        self.assertEqual(row.latest_known_value, '14')

    def test_supersession_applies_only_at_known_at(self):
        row = self.run_audit([tc('revision', '2026-02-10', '2026-02-04')])[0]
        self.assertEqual(row.ledger_value, '30')
        self.assertEqual(row.latest_known_value, '30')
        self.assertEqual(row.citation_count, 1)

    def test_equal_authorized_conflict_yields_abstention(self):
        row = self.run_audit([tc('conflict', '2026-02-10', '2026-02-06')])[0]
        self.assertEqual(row.ledger_disposition, 'ABSTAIN_CONFLICT')
        self.assertIsNone(row.ledger_value)
        self.assertEqual(row.citation_count, 2)
        self.assertTrue(row.cascade_changed_across_profiles)
        self.assertEqual(row.cascade_event_counts[0], ('60_high', 1))
        self.assertEqual(row.cascade_event_counts[1], ('flat', 0))

    def test_missing_scope_abstains_even_when_model_has_other_scope(self):
        row = self.run_audit([tc('scope', '2026-02-10', '2026-02-10', 'shop')])[0]
        self.assertEqual(row.ledger_disposition, 'ABSTAIN_NO_EVIDENCE')
        self.assertIsNone(row.latest_known_value)
        self.assertFalse(row.cascade_changed_across_profiles)

    def test_before_first_admission_has_no_evidence(self):
        row = self.run_audit([tc('pre', '2026-01-03', '2026-01-01')])[0]
        self.assertEqual(row.ledger_disposition, 'ABSTAIN_NO_EVIDENCE')

    def test_ledger_snapshot_unchanged_for_multi_profile_audit(self):
        before = gateway_snapshot_digest(self.g)
        _ = self.run_audit([tc('revision', '2026-02-10', '2026-02-04'),
                            tc('conflict', '2026-02-10', '2026-02-06')])
        self.assertEqual(before, gateway_snapshot_digest(self.g))
        self.assertTrue(self.g.verify_chain(anchored_head=self.g.head_digest))

    def test_reject_missing_independent_weights(self):
        with self.assertRaisesRegex(ValueError, 'missing independently supplied'):
            self.run_audit([tc('conflict', '2026-02-10', '2026-02-06')],
                           {'incomplete': {'c30': EvidenceWeights(.5, 1.5, .5)}})

    def test_reject_boolean_numeric_calibration(self):
        with self.assertRaises(ValueError):
            EvidenceWeights(True, 2, .4)
        with self.assertRaises(ValueError):
            EvidenceWeights(.5, False, .2)

    def test_hardcoded_framework_cannot_self_calibrate(self):
        with self.assertRaises(ValueError):
            EvidenceWeights(2, 1, .1)
        with self.assertRaises(ValueError):
            EvidenceWeights(.5, 1, 0)

    def test_duplicate_and_empty_cases_refused(self):
        case = tc('dup', '2026-02-10', '2026-02-06')
        for rows in ([], [case, case]):
            with self.assertRaises(ValueError):
                self.run_audit(rows)

    def test_naive_latest_known_ignores_withdrawal(self):
        self.assertEqual(self.g.withdraw('c60', effective_from='2026-02-01T00:00:00Z',
                          recorded_at='2026-02-07T00:00:00Z', reviewer_approved=True).disposition, 'ALLOW')
        row = self.run_audit([tc('after-withdrawal', '2026-02-10', '2026-02-08')])[0]
        self.assertEqual((row.ledger_value, row.latest_known_value), ('30', '60'))

    def test_public_report_never_leaks_quoted_policy_text_or_tenant(self):
        import json
        report = public_report(self.run_audit([tc('one', '2026-02-10', '2026-02-06')]))
        dumped = json.dumps(report)
        self.assertNotIn('Refunds allowed', dumped)
        self.assertNotIn('urn:s', dumped)
        self.assertNotIn('"demo"', dumped)
        self.assertEqual(report['abstentions'], 1)

    def test_detect_private_mutation_even_if_head_not_changed(self):
        class MutatingMini(MiniCascade):
            def add_block(self, block):
                self.outer._by_key.clear()
                super().add_block(block)
        MutatingMini.outer = self.g
        before_head = self.g.head_digest
        with self.assertRaisesRegex(RuntimeError, 'gateway state mutated'):
            diagnose_with_cascade(self.g, tenant='demo', subject='refunds', predicate='window_days',
               scope='online', effective_at='2026-02-10T00:00:00Z', known_at='2026-02-04T00:00:00Z',
               calibrated_weights=self.profiles['flat'], engine_factory=MutatingMini, block_factory=MiniBlock)
        self.assertEqual(before_head, self.g.head_digest)


class CanonicalLoaderTests(unittest.TestCase):
    def test_blob_hash_matches_known_git_encoding(self):
        self.assertEqual(git_blob_sha(b'test content\n'),
                         'd670460b4b4aece5915caf5c68d12f560a9fe3e4')

    def test_different_files_cannot_pass_pinned_hash(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / '12_IMPLEMENTATIONS/core/cascade_engine.py'
            p.parent.mkdir(parents=True)
            p.write_text('class CascadeEngine: pass\nclass KnowledgeBlock: pass\n')
            with self.assertRaisesRegex(ValueError, 'does not match pinned'):
                load_canonical_classes(t)

    def test_loader_rejects_malformed_sha(self):
        with self.assertRaises(ValueError):
            load_canonical_classes('/nonexistent', expected_blob_sha='not-a-sha')

    def test_loader_uses_supplied_local_checkout_when_hash_matches(self):
        # This test validates the loader with a toy file only. NOT a canonical run.
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / '12_IMPLEMENTATIONS/core/cascade_engine.py'
            p.parent.mkdir(parents=True)
            data = b'class CascadeEngine: pass\nclass KnowledgeBlock: pass\n'
            p.write_bytes(data)
            loaded = load_canonical_classes(t, expected_blob_sha=git_blob_sha(data))
            self.assertEqual(loaded.engine_factory.__name__, 'CascadeEngine')
            self.assertEqual(loaded.block_factory.__name__, 'KnowledgeBlock')


if __name__ == '__main__':
    unittest.main()
