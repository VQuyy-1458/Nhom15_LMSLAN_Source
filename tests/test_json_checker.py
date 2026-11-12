import unittest
from app.code_runner import matches

class JsonCheckerTests(unittest.TestCase):
    def test_structural_comparison_preserves_value_types_and_array_order(self):
        self.assertTrue(matches('{"b": [1.0,true], "a":"x"}','{"a":"x","b":[1,true]}','json'))
        for actual,expected in [('true','1'),('[2,1]','[1,2]'),('"1"','1'),('null','0')]:self.assertFalse(matches(actual,expected,'json'))
    def test_reject_invalid_or_ambiguous_json(self):
        for bad in ['NaN','Infinity','{"x":1,"x":2}','1 trailing','[1,]']:
            self.assertFalse(matches(bad,bad,'json'))
