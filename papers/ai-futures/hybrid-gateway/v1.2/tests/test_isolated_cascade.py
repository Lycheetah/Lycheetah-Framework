"""Test subprocess boundary with a declared toy engine, NOT canonical Lycheetah CASCADE."""
import os
import tempfile
import unittest
from pathlib import Path
from hybrid_gateway.core import HybridGateway,SourceDocument,ClaimProposal
from hybrid_gateway.canonical_loader import git_blob_sha
from hybrid_gateway.cascade_bridge import EvidenceWeights, gateway_snapshot_digest
from hybrid_gateway.isolated_cascade import diagnose_isolated

TOY='''import os
class KnowledgeBlock:
    def __init__(self,**kwargs): self.__dict__.update(kwargs)
class CascadeEngine:
    def __init__(self): self.blocks=[];self.cascade_events=[]
    def add_block(self,block):
        os.environ['LYCHEETAH_SUBPROCESS_PROBE']='only_child'
        self.blocks.append(block)
    def coherence(self): return 1.0
'''


def build():
    g=HybridGateway()
    s=SourceDocument('source','tenant','urn:example','Refunds allowed within 14 days.')
    g.register_source(s)
    p=ClaimProposal('claim','tenant','refunds','window_days','online','14',
          '2026-01-01T00:00:00Z','source',s.body)
    assert g.ingest(p,recorded_at='2026-01-02T00:00:00Z',reviewer_approved=True).disposition=='ALLOW'
    return g


def toy_dir(t, text=TOY):
    p=Path(t)/'12_IMPLEMENTATIONS/core/cascade_engine.py';p.parent.mkdir(parents=True)
    data=text.encode();p.write_bytes(data)
    return git_blob_sha(data)


def call(g,t,sha,**kwargs):
    return diagnose_isolated(g,tenant='tenant',subject='refunds',predicate='window_days',
            scope='online',effective_at='2026-01-03T00:00:00Z',known_at='2026-01-04T00:00:00Z',
            calibrated_weights={'claim':EvidenceWeights(.6,1.5,.4)},framework_root=t,
            expected_blob_sha=sha,**kwargs)


class IsolatedTests(unittest.TestCase):
    def test_toy_isolated_success_and_object_unchanged(self):
        g=build();before=gateway_snapshot_digest(g)
        with tempfile.TemporaryDirectory() as t:
            sha=toy_dir(t)
            d=call(g,t,sha)
        self.assertEqual(d.claim_ids,('claim',))
        self.assertEqual(d.event_count,0)
        self.assertEqual(d.diagnostic_coherence,1.0)
        self.assertEqual(d.canonical_blob_sha,sha)
        self.assertEqual(before,gateway_snapshot_digest(g))
        self.assertNotEqual(os.environ.get('LYCHEETAH_SUBPROCESS_PROBE'),'only_child')

    def test_wrong_pin_rejected_in_child(self):
        with tempfile.TemporaryDirectory() as t:
            toy_dir(t)
            with self.assertRaisesRegex(RuntimeError,'isolated CASCADE diagnostic failed'):
                call(build(),t,'0'*40)

    def test_missing_calibrated_weights_refused_before_child(self):
        g=build()
        with self.assertRaises(ValueError):
            diagnose_isolated(g,tenant='tenant',subject='refunds',predicate='window_days',
                 scope='online',effective_at='2026-01-03T00:00:00Z',
                 known_at='2026-01-04T00:00:00Z',calibrated_weights={},framework_root='/missing')

    def test_malformed_weights_refused(self):
        g=build()
        with self.assertRaises(TypeError):
            diagnose_isolated(g,tenant='tenant',subject='refunds',predicate='window_days',
                 scope='online',effective_at='2026-01-03T00:00:00Z',
                 known_at='2026-01-04T00:00:00Z',calibrated_weights={'claim':123},framework_root='/missing')

    def test_arbitrary_pin_not_allowed(self):
        with self.assertRaises(ValueError):call(build(),'/missing','notasha')

    def test_timeout_reaps_child(self):
        slow=TOY.replace('import os','import os\nimport time\ntime.sleep(2)')
        with tempfile.TemporaryDirectory() as t:
            sha=toy_dir(t,slow)
            with self.assertRaisesRegex(TimeoutError,'timeout'):
                call(build(),t,sha,timeout_seconds=.2)

    def test_crash_does_not_reveal_claim_in_exception(self):
        bad='raise RuntimeError("sensitive value 14")\n'+TOY
        g=build();before=gateway_snapshot_digest(g)
        with tempfile.TemporaryDirectory() as t:
            sha=toy_dir(t,bad)
            with self.assertRaises(RuntimeError) as cm:call(g,t,sha)
        self.assertNotIn('sensitive value',str(cm.exception))
        self.assertEqual(before,gateway_snapshot_digest(g))

    def test_empty_citation_is_coherence_none(self):
        g=build()
        with tempfile.TemporaryDirectory() as t:
            sha=toy_dir(t)
            d=diagnose_isolated(g,tenant='tenant',subject='refunds',predicate='window_days',scope='shop',
                effective_at='2026-01-03T00:00:00Z',known_at='2026-01-04T00:00:00Z',
                calibrated_weights={},framework_root=t,expected_blob_sha=sha)
            self.assertEqual(d.query_disposition,'ABSTAIN_NO_EVIDENCE')
            self.assertIsNone(d.diagnostic_coherence)

if __name__=='__main__':unittest.main()
