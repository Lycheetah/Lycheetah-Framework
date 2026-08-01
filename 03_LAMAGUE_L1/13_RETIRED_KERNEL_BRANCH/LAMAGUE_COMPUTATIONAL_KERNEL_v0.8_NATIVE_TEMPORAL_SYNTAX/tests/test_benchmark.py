from __future__ import annotations
import json, unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lamague_benchmark.engine import compare
from lamague_benchmark.runner import run_manifest

class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = ROOT / 'benchmark_corpus' / 'manifest.json'
        cls.manifest = json.loads(cls.manifest_path.read_text())
        cls.report = run_manifest(cls.manifest_path)

    def test_reference_count(self):
        self.assertEqual(len(self.manifest['references']), 20)

    def test_candidate_count(self):
        self.assertEqual(len(self.manifest['candidates']), 200)

    def test_harness_matches_all_seed_labels(self):
        self.assertEqual(self.report['expected_matches'], 200)
        self.assertEqual(self.report['accuracy'], 1.0)

    def test_all_classes_present(self):
        expected = {'EXACT_EQUIVALENT','INVARIANT_EQUIVALENT','PARTIAL_EQUIVALENT','UNSAFE_COLLAPSE','DIVERGENT','UNDECODABLE'}
        self.assertEqual(set(self.report['classification_distribution']), expected)

    def test_unknown_loss_detected(self):
        item = next(x for x in self.manifest['candidates'] if 'unknown_erased' in x['candidate'])
        ref = json.loads((self.manifest_path.parent/item['reference']).read_text())
        cand = json.loads((self.manifest_path.parent/item['candidate']).read_text())
        self.assertEqual(compare(ref,cand).classification.value, 'UNSAFE_COLLAPSE')

    def test_invariant_change_diverges(self):
        item = next(x for x in self.manifest['candidates'] if 'invariant_changed' in x['candidate'])
        ref = json.loads((self.manifest_path.parent/item['reference']).read_text())
        cand = json.loads((self.manifest_path.parent/item['candidate']).read_text())
        self.assertEqual(compare(ref,cand).classification.value, 'DIVERGENT')

    def test_malformed_packet_undecodable(self):
        item = next(x for x in self.manifest['candidates'] if 'invalid_structure' in x['candidate'])
        ref = json.loads((self.manifest_path.parent/item['reference']).read_text())
        cand = json.loads((self.manifest_path.parent/item['candidate']).read_text())
        self.assertEqual(compare(ref,cand).classification.value, 'UNDECODABLE')

if __name__ == '__main__': unittest.main()
