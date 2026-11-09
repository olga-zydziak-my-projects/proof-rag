"""Adversarial full-content binding checks, independent of the exporter."""
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "stage4_binding_auditor", Path(__file__).resolve().parents[1] / "scripts/review_stage4_binding.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


@unittest.skipUnless(Path("formal/ChromiumFast.lean").exists() and
                     Path("local/stage2/extraction.json").exists(), "requires exported Chromium data")
class Stage4BindingTests(unittest.TestCase):
    def test_full_actual_data(self):
        result = review.audit("formal/ChromiumFast.lean")
        self.assertEqual((result["nodes_compared"], result["edges_compared"],
                          result["witnesses_compared"], result["actual_edge_hints_checked"]),
                         (1864, 4419, 477, 476))

    def test_mutations_reject_incomplete_or_substituted_data(self):
        source = Path("formal/ChromiumFast.lean").read_text(encoding="utf-8")
        hint = re.search(r"some\s*\((\d+),\s*(\d+)\)", source)
        self.assertIsNotNone(hint)
        block, position = map(int, hint.groups())
        old_hint = hint.group(0)
        other_position = (position + 1) % 64
        record = re.search(r"some ⟨⟨(\d+), by decide \+kernel⟩, (\d+), some \(\d+, \d+\)⟩", source)
        self.assertIsNotNone(record)
        parent, rank = map(int, record.groups())
        old_record = record.group(0)
        graph = review.section(source, "graph")
        first_block = re.search(r"edgeBlock\d+", graph).group(0)
        conditions = re.search(r"if v\.val < (\d+) then", review.section(source, "witnessBlock0"))
        self.assertIsNotNone(conditions)
        tree_body = review.section(source, "witnessBlock0")
        missing_tree = source.replace(tree_body, "none", 1)
        omitted_definition = re.sub(r"^def witnessBlock0\b.*?(?=^def )", "", source,
                                    count=1, flags=re.MULTILINE | re.DOTALL)
        mutations = {
            "bad block": source.replace(old_hint, f"some (999999, {position})", 1),
            "bad position": source.replace(old_hint, f"some ({block}, 999999)", 1),
            "wrong actual edge": source.replace(old_hint, f"some ({block}, {other_position})", 1),
            "omitted edge block": source.replace(graph, graph.replace(first_block + ",", "", 1), 1),
            "duplicated edge block": source.replace(graph, graph.replace(first_block, first_block + "," + first_block, 1), 1),
            "missing witness definition": omitted_definition,
            "incomplete dense tree": missing_tree,
            "parent": source.replace(old_record, old_record.replace(f"⟨⟨{parent},", f"⟨⟨{(parent + 1) % 1864},", 1), 1),
            "rank": source.replace(old_record, old_record.replace(f"⟩, {rank},", f"⟩, {rank + 13},", 1), 1),
            "root": source.replace("def root : Fin 1864 := ⟨995,", "def root : Fin 1864 := ⟨994,", 1),
            "false result": re.sub(r"(?m)^(\s+)none$", lambda m: m.group(1) + old_record,
                                    source, count=1),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Substituted.lean"
            for label, changed in mutations.items():
                with self.subTest(label=label):
                    self.assertNotEqual(changed, source, label)
                    path.write_text(changed, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        review.audit(path)


if __name__ == "__main__":
    unittest.main()
