"""SXP-L 1.2 tests: directional roles, indirect speech, tamper, old forms."""
from __future__ import annotations
import copy
import random
import unittest
from sxpl_v03 import SXPError
from discourse12 import (parse_expression, render_expression, interpret,
                         BECAUSE, THEREFORE, INDIRECT)
from oracle12 import parse as second_reader, OracleReject, OracleUnsupported
from oracle11 import act as standalone_action_signature
from test_discourse11 import speech, named, quote, relation
from sovereignty import ACTS
from consent import SPEECH_ROOTS, ACTION_ROOTS


def directed(construction: str, cause: str, effect: str) -> str:
    first, second = (effect, cause) if construction == BECAUSE else (cause, effect)
    return f'mi {construction} bakumo {first} tesavo bakumo {second} tesavo devora'


def indirect(source: str, content: str) -> str:
    return f'mi {INDIRECT} {source} bakumo {content} tesavo devora'


class Discourse12Tests(unittest.TestCase):
    def checked(self, line):
        doc = parse_expression(line)
        self.assertEqual(render_expression(doc), line)
        self.assertEqual(parse_expression(render_expression(doc)), doc)
        self.assertFalse(interpret(doc)['authorizes'])
        return doc

    def test_original_love_unchanged(self):
        obj = self.checked('mi liva ti devora')
        self.assertEqual(obj['node']['kind'], 'legacy_v11')
        with self.assertRaises(SXPError):
            parse_expression('mi jiva ti devora')

    def test_directed_causal_roles(self):
        cause = 'mi liva ti devora'
        effect = speech('ranova', 'ti', 'tavona', 'darafa')
        b = self.checked(directed(BECAUSE, cause, effect))
        t = self.checked(directed(THEREFORE, cause, effect))
        self.assertEqual(b['node']['cause_ast'], t['node']['cause_ast'])
        self.assertEqual(b['node']['effect_ast'], t['node']['effect_ast'])
        self.assertNotEqual(b['node']['construction'], t['node']['construction'])
        self.assertEqual(b['node']['cause_words'], cause)
        self.assertEqual(b['node']['effect_words'], effect)
        self.assertFalse(interpret(b)['causal_connection_verified'])
        self.assertFalse(interpret(t)['causal_connection_verified'])
        self.assertEqual(second_reader(render_expression(b))[3], second_reader(render_expression(t))[3])
        self.assertEqual(second_reader(render_expression(b))[4], second_reader(render_expression(t))[4])

    def test_reverse_clause_order_changes_which_is_cause(self):
        a = speech('tinora', 'ti', 'mesara', 'darafa')
        b = speech('resama', 'ti', 'mesara', 'darafa')
        forward = self.checked(directed(BECAUSE, a, b))
        reverse = self.checked(directed(BECAUSE, b, a))
        self.assertEqual(forward['node']['cause_words'], reverse['node']['effect_words'])
        self.assertNotEqual(forward['node']['cause_ast'], reverse['node']['cause_ast'])

    def test_borema_remains_underspecified_not_reinterpreted(self):
        a = speech('tinora','ti','tavona','darafa')
        b = speech('resama','ti','tavona','darafa')
        prev = self.checked(relation(a,b,'borema'))
        self.assertEqual(prev['node']['kind'], 'legacy_v11')
        self.assertEqual(prev['node']['content']['node']['relation'], 'causal_claim_report')
        self.assertNotIn('cause_ast', prev['node']['content']['node'])

    def test_quote_and_paraphrase_are_not_same(self):
        sentence = speech('periva', 'ti', 'tavona', 'darafa')
        quote_node = self.checked(quote(sentence, named('nara')))
        indirect_node = self.checked(indirect(named('nara'), sentence))
        self.assertEqual(quote_node['node']['kind'], 'legacy_v11')
        self.assertEqual(indirect_node['node']['kind'], 'indirect_report')
        self.assertEqual(indirect_node['node']['wording_status'], 'paraphrase_not_verbatim')
        self.assertNotIn('quoted_words', indirect_node['node'])
        self.assertFalse(interpret(indirect_node)['literal_words_authenticated'])

    def test_indirect_binding_and_spelling(self):
        sentence = speech('resama', 'ti', 'lenova', 'draft_17')
        for src in ('mi', 'ti', named('nara'), named('agent_7')):
            with self.subTest(source=src):
                obj = self.checked(indirect(src, sentence))
                self.assertEqual(obj['node']['embedded_mi_binding'], 'reported_source_not_reporter')
                self.assertFalse(interpret(obj)['source_authenticated'])
                self.assertEqual(second_reader(indirect(src, sentence))[0], 'indirect')

    def test_new_form_malformed_rejected(self):
        a = speech('tinora', 'ti', 'tavona', 'darafa')
        b = speech('periva', 'ti', 'tavona', 'darafa')
        good = directed(BECAUSE, a, b)
        examples = [
            good.replace(' bakumo ', ' ', 1),
            good.replace(' tesavo bakumo ', ' bakumo ', 1),
            good.replace(' devora', ' kevonu', 1),
            good + ' mi',
            good.replace('mi larumeko', 'ti larumeko'),
            good.replace('mi larumeko', 'mi jiva'),
            indirect('ti', a).replace(' tesavo devora', ' devora'),
            indirect('ti', a) + ' tesavo',
            indirect('ti', a).replace('nimareko ti', 'nimareko devora ti'),
        ]
        for x in examples:
            with self.subTest(text=x):
                with self.assertRaises(SXPError):
                    parse_expression(x)

    def test_tampered_ast_is_rejected(self):
        a = speech('tinora', 'ti', 'tavona', 'darafa')
        b = speech('periva', 'ti', 'tavona', 'darafa')
        d = parse_expression(directed(THEREFORE, a, b))
        changes = [
            ('authorizes', True),
            ('connection_status','verified'),
            ('cause_words',b),
            ('construction','because'),  # alone changes surface, but remains a valid AST!
        ]
        for field, value in changes[:-1]:
            altered = copy.deepcopy(d)
            altered['node'][field] = value
            with self.subTest(field=field), self.assertRaises(SXPError):
                render_expression(altered)
        other = copy.deepcopy(d)
        other['node']['construction'] = 'because'
        # Changing presentation choice is allowed, and changes the emitted utterance.
        self.assertNotEqual(render_expression(other), render_expression(d))
        self.assertEqual(interpret(other)['cause'], interpret(d)['cause'])
        q = parse_expression(indirect('ti', a))
        for field, value in [('authorizes', True),('wording_status','verbatim'),
                             ('attribution_status', 'verified'),('embedded_mi_binding','outer_reporter')]:
            altered = copy.deepcopy(q)
            altered['node'][field] = value
            with self.subTest(field=field), self.assertRaises(SXPError):
                render_expression(altered)

    def test_long_input_bound(self):
        huge = 'mi larumeko ' + 'bakumo ' * 4200 + 'devora'
        with self.assertRaises(SXPError):
            parse_expression(huge)

    def test_old_v11_and_v10_forms_survive(self):
        inner = speech('periva','ti','mesara','darafa')
        for line in ('mi liva ti devora', inner, quote(inner), relation(inner,inner,'kasora')):
            with self.subTest(line=line):
                obj = self.checked(line)
                self.assertEqual(obj['node']['kind'], 'legacy_v11')

    def test_generated_cross_reader_1800(self):
        rng = random.Random(121212)
        actors = ['mi', 'ti', named('nara'), named('agent_7')]
        roots = list(ACTS) + list(SPEECH_ROOTS)
        actions = list(ACTION_ROOTS)
        resources = ['darafa','draft_17','agent_7','nara']
        for index in range(1800):
            def sample():
                root = rng.choice(roots)
                actor = 'mi' if root == 'domera' else rng.choice(actors)
                return speech(root, actor, rng.choice(actions), rng.choice(resources))
            left = sample()
            right = sample()
            if index % 3 == 0:
                source = rng.choice(actors)
                statement = indirect(source,left)
                node = self.checked(statement)['node']
                oracle = second_reader(statement)
                self.assertEqual(oracle[0], 'indirect')
                self.assertEqual(oracle[2], node['source'])
                self.assertFalse(oracle[-1])
            else:
                mode = BECAUSE if index % 3 == 1 else THEREFORE
                statement = directed(mode,left,right)
                node = self.checked(statement)['node']
                oracle = second_reader(statement)
                self.assertEqual(oracle[0], 'directed')
                self.assertEqual(oracle[2], node['construction'])
                self.assertEqual(oracle[3], standalone_action_signature(left.split()))
                self.assertEqual(oracle[4], standalone_action_signature(right.split()))
                self.assertFalse(oracle[-1])

    def test_oracle_rejects_bad(self):
        for bad in ('mi larumeko bakumo mi liva ti devora tesavo devora',
                    'mi voraneku bakumo mi liva ti devora tesavo bakumo mi liva ti devora devora',
                    'mi nimareko ti bakumo mi periva ti devora tesavo devora'):
            with self.subTest(bad=bad), self.assertRaises(OracleReject):
                second_reader(bad)

if __name__ == '__main__':
    unittest.main()
