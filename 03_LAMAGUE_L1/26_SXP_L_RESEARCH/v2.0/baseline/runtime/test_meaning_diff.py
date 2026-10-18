import unittest
from meaning_diff import compare

class DifferenceTests(unittest.TestCase):
    def test_identical_expressions_no_changes(self):
        e='mi noka kapera bakumo mi pamisa bakumo fura mi satoma tesavo tesavo devora'
        self.assertTrue(compare(e,e)['equivalent_typed_representation'])
    def test_capacity_vs_denied_promise(self):
        a='mi noka pamisa bakumo fura mi satoma tesavo devora'
        b='mi noka kapera bakumo mi pamisa bakumo fura mi satoma tesavo tesavo devora'
        d=compare(a,b)
        self.assertFalse(d['equivalent_typed_representation'])
        self.assertTrue(any(x['path']=='/node/kind' and x['priority']=='high' for x in d['differences']))
    def test_desire_vs_intention_not_equal(self):
        a='mi vanira bakumo fura mi satoma tesavo devora'
        b='mi nivara bakumo fura mi satoma tesavo devora'
        d=compare(a,b)
        self.assertFalse(d['equivalent_typed_representation'])
        self.assertEqual(d['differences'][0]['path'],'/node/stance')
    def test_polarity_matters(self):
        a='fura mi satoma devora'
        b='fura mi noka satoma devora'
        d=compare(a,b)
        self.assertTrue(any('/polarity' in x['path'] for x in d['differences']))
    def test_conditional_is_not_two_facts(self):
        a='sivane bakumo mi satoma tesavo tanaro bakumo ti satoma tesavo devora'
        b='mi satoma devora'
        self.assertFalse(compare(a,b)['equivalent_typed_representation'])

if __name__=='__main__':unittest.main()
