"""Independent-eval-ready scorer tests. Fixtures are self-authored, not external."""
import json
from pathlib import Path
import tempfile
import unittest
from hybrid_gateway import canonical_digest, evaluate

from tests.test_contracts import AT


def fact(value='14', subject='refunds', scope='store'):
    return dict(subject=subject,predicate='window_days',scope=scope,value=value,
                valid_from=AT,valid_until=None)


def gold(i, items):
    return dict(case_id=str(i),source_digest=canonical_digest(f'fake source {i}'),
                gold=items, answerable=bool(items))


def pred(i, items):
    return dict(case_id=str(i),claims=items,review_minutes=.5)


class ExternalReadyEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.gold=Path(self.tmp.name)/'gold.jsonl'
        self.pred=Path(self.tmp.name)/'pred.jsonl'

    def write(self, g,p):
        self.gold.write_text(''.join(json.dumps(x)+'\n' for x in g))
        self.pred.write_text(''.join(json.dumps(x)+'\n' for x in p))

    def test_precision_recall_abstention_document_and_wrong_field(self):
        self.write([gold('a',[fact('14')]),gold('b',[]),gold('c',[fact('21')]),
                    gold('d',[fact('8')])],
                   [pred('a',[fact('14')]),pred('b',[]),
                    pred('c',[fact('21',scope='online')]),pred('d',[])])
        r=evaluate(self.gold,self.pred)
        self.assertEqual((r.true_positive,r.false_positive,r.false_negative),(1,1,2))
        self.assertEqual(r.wrong_field_or_scope_candidates,1)
        self.assertAlmostEqual(r.precision,.5)
        self.assertAlmostEqual(r.recall,1/3)
        self.assertEqual(r.correct_negative_abstentions,1)
        self.assertEqual(r.missed_positive_documents,1)
        self.assertEqual(r.exact_document_matches,2)
        self.assertEqual(r.total_review_minutes,2.0)
        self.assertNotIn('case_id',r.public_dict())

    def test_all_abstention_has_zero_recall_on_positive_cases(self):
        self.write([gold('a',[fact()]),gold('b',[])],[pred('a',[]),pred('b',[])])
        r=evaluate(self.gold,self.pred)
        self.assertEqual(r.recall,0.0)
        self.assertEqual(r.precision,0.0)
        self.assertEqual(r.negative_abstention_rate,1.0)
        self.assertEqual(r.positive_document_coverage,0.0)

    def test_duplicates_count_as_false_positives(self):
        self.write([gold(1,[fact()])],[pred(1,[fact(),fact()])])
        r=evaluate(self.gold,self.pred)
        self.assertEqual((r.true_positive,r.false_positive,r.false_negative),(1,1,0))
        self.assertEqual(r.exact_document_matches,0)

    def test_input_files_must_match_ids(self):
        self.write([gold(1,[fact()]),gold(2,[])],[pred(1,[fact()])])
        with self.assertRaises(ValueError):
            evaluate(self.gold,self.pred)

    def test_frozen_gold_digest_detects_data_change(self):
        self.write([gold(1,[fact()])],[pred(1,[fact()])])
        good=evaluate(self.gold,self.pred)
        self.assertEqual(evaluate(self.gold,self.pred,
                         expected_corpus_digest=good.corpus_digest).recall,1)
        with self.assertRaises(ValueError):
            evaluate(self.gold,self.pred,expected_corpus_digest='sha256:wrong')

    def test_invalid_non_finite_or_duplicate_json_field_rejected(self):
        self.write([gold(1,[fact()])],[pred(1,[fact()])])
        text=self.pred.read_text().strip()
        for bad in [text.replace('"review_minutes": 0.5','"review_minutes": NaN'),
                    text.replace('"case_id": "1"','"case_id": "1", "case_id": "1"'),
                    text.replace('"review_minutes": 0.5','"review_minutes": -2')]:
            self.pred.write_text(bad+'\n')
            with self.assertRaises(ValueError):
                evaluate(self.gold,self.pred)

    def test_wrong_field_not_mistaken_for_true_positive(self):
        self.write([gold(1,[fact('14')])],[pred(1,[fact('14',subject='loyalty')])])
        r=evaluate(self.gold,self.pred)
        self.assertEqual((r.true_positive,r.false_positive,r.false_negative),(0,1,1))
        self.assertEqual(r.wrong_field_or_scope_candidates,1)


if __name__=='__main__': unittest.main()
