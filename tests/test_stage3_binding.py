import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('binding_review',Path(__file__).resolve().parents[1]/'scripts/review_stage3_binding.py')
review=importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

@unittest.skipUnless(Path('local/stage2/extraction.json').exists(), 'requires local Chromium artifacts')
class BindingReviewTests(unittest.TestCase):
    def test_actual_full_content_and_mutations(self):
        source=Path('formal/Chromium.lean').read_text(encoding='utf-8')
        self.assertTrue(review.audit('formal/Chromium.lean','local/stage2')['passed'])
        changes=[('def root : Fin 1864 := ⟨995,','def root : Fin 1864 := ⟨994,'),
                 ('FiniteGraph 1864','FiniteGraph 1863'),
                 ('android_webview/common/mojom/','changed/common/mojom/'),
                 ('some ⟨⟨995, by decide +kernel⟩, 1⟩','some ⟨⟨994, by decide +kernel⟩, 1⟩'),
                 ('some ⟨⟨995, by decide +kernel⟩, 1⟩','some ⟨⟨995, by decide +kernel⟩, -1⟩')]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'Mutated.lean'
            for old,new in changes:
                self.assertTrue(old in source, old)
                p.write_text(source.replace(old,new,1),encoding='utf-8')
                with self.assertRaises(ValueError): review.audit(p,'local/stage2')
