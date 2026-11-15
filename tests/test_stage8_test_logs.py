from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_stage8 import passed_test


class TestLogTests(unittest.TestCase):
    def test_exact_test_identity_accepts_lf_and_crlf(self):
        name = 'test_example.ExampleTests.test_negative_case'
        line = 'test_negative_case ('+name+') ... ok'
        for ending in ('\n', '\r\n', '\r'):
            self.assertTrue(passed_test('earlier'+ending+line+ending+'later'+ending, name))
        for other in (line.replace('ok', 'FAIL'), line.replace('test_example.', 'other_module.'),
                      line.replace('ok', 'skipped'), line+' trailing text'):
            self.assertFalse(passed_test(other+'\r\n', name))
