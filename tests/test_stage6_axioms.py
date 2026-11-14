"""Strict Stage 6 axiom record parsing, independent of historical audits."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from stage6_support import audit, QUERY_THEOREMS


def valid_output():
    return '\n'.join(
        f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
        for name in QUERY_THEOREMS)


class Stage6AxiomTests(unittest.TestCase):
    def test_complete_valid_reports_and_timing(self):
        output = 'proof_construction_ms=0; kernel_check_and_insert_ms=12\n' + valid_output()
        result = audit(output)
        self.assertEqual(tuple(result), QUERY_THEOREMS)
        self.assertTrue(all(used == ['propext', 'Classical.choice', 'Quot.sound']
                            for used in result.values()))
        empty = '\n'.join(f"'{name}' does not depend on any axioms" for name in QUERY_THEOREMS)
        self.assertEqual(audit(empty), dict.fromkeys(QUERY_THEOREMS, []))

    def test_missing_duplicate_and_contradictory_reports(self):
        lines = valid_output().splitlines()
        mutations = [
            '\n'.join(lines[1:]),
            valid_output() + '\n' + lines[0],
            valid_output() + f"\n'{QUERY_THEOREMS[0]}' does not depend on any axioms",
            valid_output() + f"\n'{QUERY_THEOREMS[0]}' depends on axioms: [sorryAx]",
        ]
        for output in mutations:
            with self.subTest(output=output), self.assertRaises(ValueError):
                audit(output)

    def test_malformed_and_disallowed_reports(self):
        output = valid_output()
        mutations = [
            output.replace('[propext, Classical.choice, Quot.sound]', '[sorryAx]', 1),
            output.replace('[propext, Classical.choice, Quot.sound]', '[propext, propext]', 1),
            output.replace('[propext, Classical.choice, Quot.sound]', '[propext,]', 1),
            output.replace('[propext, Classical.choice, Quot.sound]', '[,propext]', 1),
            output.replace('[propext, Classical.choice, Quot.sound]', '[propext', 1),
            output.replace("'QueryProof.accepted'", "prefix 'QueryProof.accepted'", 1),
            output.replace('[propext, Classical.choice, Quot.sound]', '[propext] suffix', 1),
            output + "\n'QueryProof.extra' does not depend on any axioms",
            output + "\n'QueryProof.accepted' depends on axioms: broken",
        ]
        for changed in mutations:
            with self.subTest(output=changed), self.assertRaises(ValueError):
                audit(changed)


if __name__ == '__main__':
    unittest.main()
