"""Fault tests for checked hints; corrupted hints need not pass the old checker."""
import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from repo_proof.fast_export import render_fast
from repo_proof.generator import generate_certificate
from repo_proof.checker import verify_certificate


class FastExportTests(unittest.TestCase):
    def setUp(self):
        self.g={'nodes':['a','b','r','isolated'],
                'edges':[['a','b'],['b','r'],['b','a']]}
        self.c=generate_certificate(self.g,'r')

    def test_hint_schema_rejects_malformed_without_coercion(self):
        for hints in [{'a':(-1,0)},{'a':(False,0)},{'a':(0,)},
                      {'unknown':(0,0)},{'a':'0,0'}]:
            with self.assertRaises(ValueError): render_fast(self.g,'r',self.c,hints=hints)

    @unittest.skipUnless(os.environ.get('REPO_PROOF_LEAN'),'set REPO_PROOF_LEAN')
    def test_checked_hints_and_witness_faults_in_lean(self):
        cases=[]
        def add(c=None,hints=None,expected=False):
            c=self.c if c is None else c
            cases.append((render_fast(self.g,'r',c,f'F{len(cases)}',hints).split('theorem accepted')[0],expected))
        add(expected=True)
        # These first three are well-formed Nat indices, including a real
        # position naming the wrong edge. Old erased witnesses still pass.
        for hints in [{'a':(99,0)},{'a':(0,999)},{'b':(0,0)},
                      {'a':None},{'r':(0,0)}]:
            self.assertTrue(verify_certificate(self.g,'r',self.c))
            add(hints=hints)
        for mutation in ['parent','rank','omitted','false','missing_parent']:
            c=copy.deepcopy(self.c)
            a=next(w for w in c['candidates'] if w['node']=='a')
            if mutation=='parent': a['parent']='r'
            if mutation=='rank': a['rank']=0
            if mutation=='omitted': c['candidates']=[w for w in c['candidates'] if w['node']!='a']
            if mutation=='false': c['candidates'].append({'node':'isolated','parent':'r','rank':1})
            if mutation=='missing_parent': c['candidates']=[w for w in c['candidates'] if w['node']!='b']
            add(c)
        gap=copy.deepcopy(self.c)
        for w in gap['candidates']: w['rank']*=7
        add(gap,expected=True)
        source='import FastChecker\nimport ProofTiming\n'
        for i,(data,_) in enumerate(cases):
            source+=data.replace('import FastChecker\n','').replace('import ProofTiming\n','')+f'end F{i}\n'
        source+='def main : IO Unit := do\n'
        for i in range(len(cases)):
            source+=f'  IO.println (RepoProof.fastCheck F{i}.graph F{i}.root F{i}.certificate)\n'
        source+='  IO.println (RepoProof.fastCheck F0.graph ⟨0, by decide⟩ F0.certificate)\n'
        with tempfile.TemporaryDirectory(dir='local') as folder:
            path=Path(folder)/'FastFaults.lean'; path.write_text(source,encoding='utf-8')
            env=dict(os.environ,LEAN_PATH=str(Path('formal').resolve()))
            run=subprocess.run([os.environ['REPO_PROOF_LEAN'],'--run',str(path)],env=env,
                               capture_output=True,text=True,encoding='utf-8',timeout=120)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertEqual(run.stdout.splitlines(),[str(x[1]).lower() for x in cases]+['false'])
