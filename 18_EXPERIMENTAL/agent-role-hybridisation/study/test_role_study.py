"""Focused artifact-integrity checks; synthetic text is not a model response study."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('role_study.py')


class StudyIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.run = self.home / 'run'
        self.cli('prepare', '--case', 'threshold-counterexample', '--out', str(self.run))

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def fill_responses(self, mixed=False):
        for index in range(1, 5):
            text = self.home / f'response-{index}.txt'
            text.write_text('SYNTHETIC CLI TEST FIXTURE, not a model experiment.\n')
            model = 'test-fixture-2' if mixed and index == 4 else 'test-fixture-1'
            self.cli('record', '--run', str(self.run), '--item', f'item-{index}',
                     '--response', str(text), '--model-snapshot', model)

    def ratings(self):
        review = self.home / 'review'
        self.cli('blind', '--run', str(self.run), '--out', str(review))
        path = review / 'RATINGS.json'
        data = json.loads(path.read_text())
        data['reviewer_id'] = 'synthetic-integrity-fixture'
        data['reviewer_relationship'] = 'Test author; not independent'
        for rating in data['ratings']:
            rating['score'] = 1
            rating['rationale'] = 'Synthetic fixture checks report plumbing only.'
        return path, data

    def test_names_and_review_keys_are_separated(self):
        key = json.loads((self.run / 'OWNER_KEY.json').read_text())['items']
        criteria = json.loads((self.run / 'RUN.json').read_text())['case']['criteria']
        for item, condition in key.items():
            prompt = (self.run / f'{item}.txt').read_text()
            self.assertEqual('Eidos Reed' in prompt, condition == 'D')
            self.assertNotIn('criterion_id', prompt)
            for criterion in criteria:
                self.assertNotIn(criterion['acceptance'], prompt)
        self.assertEqual(set(key.values()), {'A', 'B', 'C', 'D'})

    def test_prepare_refuses_overwrite(self):
        before = (self.run / 'RUN.json').read_bytes()
        self.cli('prepare', '--case', 'tower-choice', '--out', str(self.run), ok=False)
        self.assertEqual((self.run / 'RUN.json').read_bytes(), before)

    def test_changed_prompt_blocks_recording(self):
        (self.run / 'item-1.txt').write_text('Changed prompt')
        response = self.home / 'response.txt'
        response.write_text('Synthetic')
        self.cli('record', '--run', str(self.run), '--item', 'item-1', '--response', str(response),
                 '--model-snapshot', 'test-fixture', ok=False)
        self.assertFalse((self.run / 'item-1.response.json').exists())

    def test_over_budget_blocks_recording(self):
        response = self.home / 'response.txt'
        response.write_text('Synthetic')
        self.cli('record', '--run', str(self.run), '--item', 'item-1', '--response', str(response),
                 '--model-snapshot', 'test-fixture', '--output-tokens', '601', ok=False)
        self.assertFalse((self.run / 'item-1.response.json').exists())

    def test_mixed_models_block_review(self):
        self.fill_responses(mixed=True)
        review = self.home / 'review'
        self.cli('blind', '--run', str(self.run), '--out', str(review), ok=False)
        self.assertFalse(review.exists())

    def test_nonfinite_resource_measurement_blocks_recording(self):
        response = self.home / 'response.txt'
        response.write_text('Synthetic')
        self.cli('record', '--run', str(self.run), '--item', 'item-1', '--response', str(response),
                 '--model-snapshot', 'test-fixture', '--elapsed-seconds', 'nan', ok=False)
        self.assertFalse((self.run / 'item-1.response.json').exists())

    def test_null_rating_blocks_report(self):
        self.fill_responses()
        path, ratings = self.ratings()
        ratings['ratings'][0]['score'] = None
        path.write_text(json.dumps(ratings))
        report = self.home / 'report.json'
        self.cli('summarize', '--run', str(self.run), '--ratings', str(path), '--out', str(report), ok=False)
        self.assertFalse(report.exists())

    def test_duplicate_rating_blocks_report(self):
        self.fill_responses()
        path, ratings = self.ratings()
        ratings['ratings'].append(dict(ratings['ratings'][0]))
        path.write_text(json.dumps(ratings))
        report = self.home / 'report.json'
        self.cli('summarize', '--run', str(self.run), '--ratings', str(path), '--out', str(report), ok=False)
        self.assertFalse(report.exists())

    def test_boolean_is_not_a_valid_score(self):
        self.fill_responses()
        path, ratings = self.ratings()
        ratings['ratings'][0]['score'] = True
        path.write_text(json.dumps(ratings))
        self.cli('summarize', '--run', str(self.run), '--ratings', str(path),
                 '--out', str(self.home / 'report.json'), ok=False)

    def test_complete_review_preserves_unknown_resources(self):
        self.fill_responses()
        path, ratings = self.ratings()
        path.write_text(json.dumps(ratings))
        report = self.home / 'report.json'
        self.cli('summarize', '--run', str(self.run), '--ratings', str(path), '--out', str(report))
        result = json.loads(report.read_text())
        self.assertEqual(result['status'], 'OPERATOR_RECORDED_DESCRIPTIVE_REVIEW')
        self.assertEqual(result['provider_calls_by_kit'], 0)
        self.assertEqual(len(result['observations']), 8)
        self.assertTrue(all(r['output_tokens'] is None for r in result['resources'].values()))
        self.assertNotIn('aggregate_score', result)


if __name__ == '__main__':
    unittest.main()
