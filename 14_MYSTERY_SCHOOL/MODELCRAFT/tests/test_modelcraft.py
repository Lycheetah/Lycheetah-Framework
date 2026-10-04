"""Contract/ranking failure cases; synthetic runs are not empirical evidence."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

HOME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOME))
from reference import errors, rank


def read(name):
    return json.loads((HOME / name).read_text())


def stamp(value):
    return value.isoformat().replace('+00:00', 'Z')


class ModelcraftContracts(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.cards = read('data/recommendations.json')['recommendations']
        self.request = read('examples/ranking-request.json')
        self.hypothesis = read('examples/hypothesis.json')

    def make_tested(self):
        result = deepcopy(self.hypothesis)
        when = stamp(self.now - timedelta(days=1))
        result.update(maturity='REPRODUCED_ONCE', freshness='CURRENT',
                      last_tested_at=when, stale_after=stamp(self.now + timedelta(days=29)),
                      observed_effect='SYNTHETIC FIXTURE ONLY: one supporting record.', reproduction_count=1)
        result['reproductions'] = [{
            'run_id': 'SYNTHETIC-1', 'runner_id': 'TEST-RUNNER-A', 'model_family': 'SYNTHETIC-A',
            'model_version': 'FIXTURE', 'tested_at': when, 'result': 'SUPPORT',
            'fixture_ref': 'SYNTHETIC-TASK', 'baseline_output_ref': 'SYNTHETIC-BASELINE',
            'technique_output_ref': 'SYNTHETIC-TREATMENT', 'evidence_refs': ['SYNTHETIC-RECORD'],
            'budget_control': 'Synthetic example; no model call occurred.', 'baseline_cost': None,
            'technique_cost': None, 'currency': None, 'baseline_latency_ms': None, 'technique_latency_ms': None,
        }]
        return result

    def test_all_twenty_four_families_and_ten_halls_remain_unmeasured(self):
        rows = read('data/techniques.json')['techniques']
        self.assertEqual({r['id'] for r in rows}, {f'T{i:02}' for i in range(1, 25)})
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(r['empirical_status'] == 'UNTESTED_IN_THIS_PACKET' for r in rows))
        halls = read('data/halls.json')['halls']
        self.assertEqual(len(halls), 10)
        mapped = [ident for h in halls for ident in h['technique_ids']]
        self.assertEqual(sorted(mapped), sorted(r['id'] for r in rows))
        self.assertTrue(all(r['hall'] == h['id'] for h in halls for r in rows if r['id'] in h['technique_ids']))

    def test_catalogue_and_private_examples_validate(self):
        for card in self.cards:
            self.assertEqual(errors('recommendation', card, self.now), [])
        self.assertEqual(errors('ranking-request', self.request, self.now), [])
        self.assertEqual(errors('trick', self.hypothesis, self.now), [])
        self.assertEqual(errors('recommendation-event', read('examples/recommendation-event.json'), self.now), [])

    def test_unknown_cost_is_not_zero_or_a_free_budget_match(self):
        card = deepcopy(self.cards[2])
        card['cost'].update(kind='UNKNOWN', amount=None, currency=None, verified_at=None, verification_source=None)
        self.assertEqual(rank([card], self.request, self.now), [])
        self.request['budget'] = {'kind': 'UNSPECIFIED', 'max_amount': None, 'currency': None}
        shown = rank([card], self.request, self.now)
        self.assertIn('COST_UNKNOWN', shown[0]['ranking_reason_codes'])
        card['cost']['amount'] = 0
        self.assertTrue(errors('recommendation', card, self.now))

    def test_paid_budget_requires_fresh_cost_same_currency_and_amount(self):
        card = deepcopy(self.cards[2])
        card['cost'].update(kind='PAID', amount=2, currency='NZD', verified_at=stamp(self.now - timedelta(days=1)))
        self.assertEqual(rank([card], self.request, self.now), [])
        self.request['budget'] = {'kind': 'LIMITED', 'max_amount': 3, 'currency': 'NZD'}
        self.assertEqual(len(rank([card], self.request, self.now)), 1)
        for currency, amount in [('USD', 3), ('NZD', 1)]:
            with self.subTest(currency=currency, amount=amount):
                self.request['budget'].update(currency=currency, max_amount=amount)
                self.assertEqual(rank([card], self.request, self.now), [])

    def test_stale_free_and_paid_routes_are_excluded_even_without_budget(self):
        self.request['budget'] = {'kind': 'UNSPECIFIED', 'max_amount': None, 'currency': None}
        for kind, amount in [('PAID', 2), ('FREE_TIER', 0)]:
            with self.subTest(kind=kind):
                card = deepcopy(self.cards[2])
                card['cost'].update(kind=kind, amount=amount, currency='NZD', verified_at=stamp(self.now - timedelta(days=30)))
                self.assertEqual(rank([card], self.request, self.now), [])

    def test_no_goal_and_engagement_fields_fail_visibly(self):
        empty = deepcopy(self.request)
        empty['goal_ids'] = []
        with self.assertRaises(ValueError):
            rank(self.cards, empty, self.now)
        for field in read('data/policy.json')['forbidden_inputs']:
            with self.subTest(field=field):
                request = deepcopy(self.request)
                request[field] = 100
                with self.assertRaises(ValueError):
                    rank(self.cards, request, self.now)

    def test_prerequisites_and_tool_authority_are_not_inferred(self):
        card = deepcopy(self.cards[2])
        card.update(prerequisites=['LESSON-A'], requires_tools=['PERMITTED-TOOL'])
        self.assertEqual(rank([card], self.request, self.now), [])
        self.request['completed_prerequisites'] = ['LESSON-A']
        self.assertEqual(rank([card], self.request, self.now), [])
        self.request['tool_ids'] = ['PERMITTED-TOOL']
        self.assertEqual(len(rank([card], self.request, self.now)), 1)

    def test_continue_requires_explicit_unfinished_project(self):
        card = deepcopy(self.cards[2])
        card.update(type='CONTINUE', project_ref='PROJECT-A', section='CONTINUE_MY_WORK', goal_ids=['CONTINUE'])
        self.request['goal_ids'] = ['CONTINUE']
        self.assertEqual(rank([card], self.request, self.now), [])
        self.request['unfinished_project_ids'] = ['PROJECT-A']
        shown = rank([card], self.request, self.now)
        self.assertIn('EXPLICIT_UNFINISHED_WORK', shown[0]['ranking_reason_codes'])
        card['project_ref'] = None
        self.assertTrue(errors('recommendation', card, self.now))

    def test_top_five_stable_ties_and_duplicate_id_rejection(self):
        cards = [deepcopy(self.cards[2]) for _ in range(7)]
        for i, card in enumerate(cards):
            card['id'] = f'TIE-{i}'
        first = rank(cards, self.request, self.now)
        second = rank(list(reversed(cards)), self.request, self.now)
        self.assertEqual([r['id'] for r in first], [f'TIE-{i}' for i in range(5)])
        self.assertEqual(first, second)
        self.assertEqual(first[0]['score'], sum(first[0]['score_components'].values()))
        self.assertEqual(first[0]['matched_goal_ids'], ['LEARN_AI'])
        cards[1]['id'] = cards[0]['id']
        with self.assertRaises(ValueError):
            rank(cards, self.request, self.now)

    def test_rank_does_not_mutate_inputs_or_consume_skip_history(self):
        cards, request = deepcopy(self.cards), deepcopy(self.request)
        first = rank(cards, request, self.now)
        event = read('examples/recommendation-event.json')
        self.assertEqual(event['action'], 'SKIPPED')
        self.assertEqual(errors('recommendation-event', event, self.now), [])
        self.assertEqual(rank(cards, request, self.now), first)
        self.assertEqual(cards, self.cards)
        self.assertEqual(request, self.request)
        request['skip_history'] = ['R03']
        with self.assertRaises(ValueError):
            rank(cards, request, self.now)

    def test_untested_item_cannot_claim_support_or_current_evidence(self):
        for key, value in [('maturity', 'REPRODUCED_ONCE'), ('freshness', 'CURRENT'), ('reproduction_count', 5), ('observed_effect', 'It worked 10x better.')]:
            with self.subTest(key=key):
                item = deepcopy(self.hypothesis)
                item[key] = value
                self.assertTrue(errors('trick', item, self.now))

    def test_duplicate_and_missing_evidence_cannot_count(self):
        item = self.make_tested()
        self.assertEqual(errors('trick', item, self.now), [])
        item['reproductions'].append(deepcopy(item['reproductions'][0]))
        item.update(maturity='REPRODUCED_MULTI_RUN', reproduction_count=2)
        self.assertTrue(errors('trick', item, self.now))
        item = self.make_tested()
        item['reproductions'][0]['evidence_refs'] = []
        self.assertTrue(errors('trick', item, self.now))

    def test_multi_user_and_cross_model_need_distinct_records(self):
        item = self.make_tested()
        second = deepcopy(item['reproductions'][0])
        second['run_id'] = 'SYNTHETIC-2'
        item['reproductions'].append(second)
        item.update(maturity='REPRODUCED_MULTI_USER', reproduction_count=2, applicability='CROSS_MODEL')
        self.assertTrue(errors('trick', item, self.now))
        second.update(runner_id='TEST-RUNNER-B', model_family='SYNTHETIC-B')
        self.assertEqual(errors('trick', item, self.now), [])

    def test_new_failure_updates_last_tested_without_erasing_support(self):
        item = self.make_tested()
        failure = deepcopy(item['reproductions'][0])
        failure.update(run_id='SYNTHETIC-FAILURE', result='FAIL', tested_at=stamp(self.now - timedelta(hours=1)))
        item['reproductions'].append(failure)
        item['lifecycle'] = 'FAILED_REPLICATION'
        self.assertTrue(errors('trick', item, self.now))
        item['last_tested_at'] = failure['tested_at']
        self.assertEqual(errors('trick', item, self.now), [])

    def test_expired_evidence_and_fake_failure_badges_fail(self):
        item = self.make_tested()
        item['stale_after'] = stamp(self.now - timedelta(hours=1))
        self.assertTrue(errors('trick', item, self.now))
        item['freshness'] = 'STALE'
        self.assertEqual(errors('trick', item, self.now), [])
        item = self.make_tested()
        item['lifecycle'] = 'FAILED_REPLICATION'
        self.assertTrue(errors('trick', item, self.now))

    def test_private_receipts_cannot_silently_publish_or_add_pressure(self):
        for key, value in [('privacy', 'PUBLIC'), ('publication_consent', True)]:
            with self.subTest(key=key):
                item = deepcopy(self.hypothesis)
                item[key] = value
                self.assertTrue(errors('trick', item, self.now))
        for key, value in [('storage_consent', False), ('privacy', 'PUBLIC'), ('resistance_score', 5)]:
            with self.subTest(key=key):
                item = read('examples/recommendation-event.json')
                item[key] = value
                self.assertTrue(errors('recommendation-event', item, self.now))
        for key, value in [('skip_effect', 'Lose progress'), ('source_of_urgency', 'Return now')]:
            with self.subTest(key=key):
                card = deepcopy(self.cards[2])
                card[key] = value
                self.assertTrue(errors('recommendation', card, self.now))

    def test_timestamps_and_budget_types_are_checked(self):
        for value in ['yesterday', '2026-02-30T00:00:00Z', '2026-10-04T01:00:00']:
            with self.subTest(timestamp=value):
                item = self.make_tested()
                item['last_tested_at'] = value
                self.assertTrue(errors('trick', item, self.now))
        card = deepcopy(self.cards[2])
        card['cost']['verified_at'] = stamp(self.now + timedelta(days=1))
        self.assertTrue(errors('recommendation', card, self.now))
        for budget in [{'kind': 'ZERO', 'max_amount': None, 'currency': None},
                       {'kind': 'LIMITED', 'max_amount': 3, 'currency': None},
                       {'kind': 'UNSPECIFIED', 'max_amount': 100, 'currency': 'USD'}]:
            with self.subTest(budget=budget):
                request = deepcopy(self.request)
                request['budget'] = budget
                self.assertTrue(errors('ranking-request', request, self.now))
        with self.assertRaises(ValueError):
            rank(self.cards, self.request, self.now, limit=10)


if __name__ == '__main__':
    unittest.main()
