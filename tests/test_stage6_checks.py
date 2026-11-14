"""Reporting must recognize successful differential tests without invented stdout."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from check_stage6 import regression_summary


class Stage6CheckReportingTests(unittest.TestCase):
    def test_real_unittest_success_without_printed_case_count(self):
        result = {'passed': True, 'exit_code': 0, 'stdout': '',
                  'stderr': 'test_differential (test_lean_export.LeanExportTests.test_differential) ... ok\n'
                            '\nRan 113 tests in 165.959s\n\nOK (skipped=1)\n'}
        summary = regression_summary(result)
        self.assertEqual(summary['test_count'], 113)
        self.assertEqual(summary['test_skipped'], 1)
        self.assertEqual(summary['differential_cases'], 1547)

    def test_skipped_or_failed_differential_is_not_accepted(self):
        for state in ('skipped missing Lean', 'FAIL', 'ERROR'):
            with self.subTest(state=state):
                result = {'passed': True, 'exit_code': 0, 'stdout': '1547',
                          'stderr': 'test_differential (test_lean_export.LeanExportTests.test_differential) ... '+state+
                                    '\nRan 113 tests in 1s\nOK (skipped=1)\n'}
                with self.assertRaises(ValueError):
                    regression_summary(result)


if __name__ == '__main__':
    unittest.main()
