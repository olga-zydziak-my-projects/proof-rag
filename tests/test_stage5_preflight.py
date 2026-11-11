"""Public fail-closed tests; these do NOT discharge Stage 5 gates A-L."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from repo_proof.stage5_preflight import (BASELINE,CONTRACT_SHA256,INVENTORY_CLAIM,
    Pin,accepted_anchor,digest,pin_differences,preservation)

PROJECT=Path(__file__).resolve().parents[1]


class Stage5PreflightTests(unittest.TestCase):
    def test_frozen_contract_and_preservation(self):
        self.assertEqual(digest((PROJECT/'docs/stage5-contract.md').read_bytes()),CONTRACT_SHA256)
        self.assertTrue(preservation(PROJECT)['preserved'])

    def test_pin_conflict_is_not_reconciled_by_matching_counts(self):
        anchor,_=accepted_anchor(PROJECT)
        differences=pin_differences(INVENTORY_CLAIM,anchor)
        self.assertEqual(set(differences),{'commit','tree'})
        self.assertEqual(pin_differences(anchor,anchor),{})  # Pin agreement alone is not PASS.
        self.assertEqual(BASELINE,'e4984110743131d04ad984eaaa48d33d72867336')

    def call_cli(self,*args):
        return subprocess.run([sys.executable,'scripts/stage5_preflight.py',*map(str,args)],
                              cwd=PROJECT,capture_output=True,text=True,encoding='utf-8',timeout=120)

    def test_public_boundary_rejects_self_consistent_producer_claim(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/'local') as folder:
            base=Path(folder); fake=base/'producer'; fake.mkdir()
            data=b'// attacker-controlled fixture\n'; (fake/'input.mojom').write_bytes(data)
            attacker={'commit':INVENTORY_CLAIM.commit,'tree':INVENTORY_CLAIM.tree,
                      'count':1,'entries':[{'path':'input.mojom','sha256':digest(data)}]}
            (fake/'manifest.json').write_text(json.dumps(attacker),encoding='utf-8')
            self.assertEqual(attacker['count'],len(list(fake.glob('*.mojom'))))
            self.assertEqual(attacker['entries'][0]['sha256'],hashlib.sha256(data).hexdigest())
            config=base/'config.json'
            config.write_text(json.dumps({'repository':INVENTORY_CLAIM.repository,
                'commit':INVENTORY_CLAIM.commit,'data_dir':str(fake)}),encoding='utf-8')
            run_dir=base/'run'
            run=self.call_cli('--config',config,'--run-dir',run_dir)
            self.assertEqual(run.returncode,3,run.stdout+run.stderr)
            report=json.loads((run_dir/'diagnostic.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'BLOCKED_PIN_CONFLICT')
            self.assertFalse(report['success']); self.assertFalse(report['answer_released'])
            self.assertIn('config_error',report)
            self.assertEqual(report['accepted_anchor']['commit'],'27cec857a08a0ee0e1b41f5eb18c07467a0ce093')
            self.assertFalse((run_dir/'answer.json').exists())

    def test_existing_run_is_not_overwritten(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/'local') as folder:
            run_dir=Path(folder)/'run'; run_dir.mkdir()
            sentinel=run_dir/'diagnostic.json'; sentinel.write_bytes(b'previous diagnostic')
            run=self.call_cli('--run-dir',run_dir)
            self.assertEqual(run.returncode,2)
            self.assertEqual(sentinel.read_bytes(),b'previous diagnostic')

    def test_malformed_config_is_diagnostic_failure_not_empty_success(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/'local') as folder:
            base=Path(folder); config=base/'bad.json'; config.write_text('null',encoding='utf-8')
            run=self.call_cli('--config',config,'--run-dir',base/'run')
            self.assertEqual(run.returncode,2)
            result=json.loads((base/'run/diagnostic.json').read_text(encoding='utf-8'))
            self.assertFalse(result['success']); self.assertFalse(result['answer_released'])
            self.assertEqual(result['status'],'STAGE5_FAIL__PREFLIGHT')
