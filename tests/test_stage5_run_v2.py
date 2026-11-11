import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from repo_proof.stage5_v2 import Blob,snapshot_payload,validate_snapshot,canonical
from repo_proof.stage5_run_v2 import seal


class RunBoundaryTests(unittest.TestCase):
    def test_boolean_id_is_not_integer_id(self):
        c=SimpleNamespace(pin={'commit':'fixed'},blobs=(Blob('x.mojom',b'', 'oid','100644'),))
        value=snapshot_payload(c); value['files'][0]['id']=False
        with self.assertRaises(ValueError): validate_snapshot(value,c)

    def test_public_preflight_rejects_mixing_and_changes_without_releasing_answer(self):
        with tempfile.TemporaryDirectory(dir='local') as temp:
            root=Path(temp); run=root/'run'; (run/'lean').mkdir(parents=True)
            (run/'snapshot.json').write_bytes(b'{}\n')
            expected=seal(run,'first')
            trusted=root/'trusted.json'; trusted.write_bytes(canonical(expected))
            command=[sys.executable,'scripts/stage5_v2_verify_inputs.py','--run-dir',str(run),
                     '--trusted-seal',str(trusted),'--nonce']
            for attack in ('cross-run','changed-bytes','updated-local-manifest'):
                if attack!='cross-run': (run/'snapshot.json').write_bytes(b'{"changed":true}\n')
                if attack=='updated-local-manifest':
                    local=json.loads((run/'run-seal.json').read_bytes())
                    local['files']['snapshot.json']='attacker-hash'
                    (run/'run-seal.json').write_bytes(canonical(local))
                result=subprocess.run(command+(['second'] if attack=='cross-run' else ['first']),
                                      capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,2,result.stdout+result.stderr)
                self.assertIn('INPUT_REJECTED',result.stderr)
                self.assertFalse((run/'answer.json').exists())
