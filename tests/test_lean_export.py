"""Differential tests: agreement is evidence, not a refinement proof."""
import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from repo_proof.generator import generate_certificate
from repo_proof.checker import verify_certificate
from repo_proof.graph import ValidationError
from repo_proof.lean_export import render, load_json

class LeanExportTests(unittest.TestCase):
    def setUp(self):
        self.g = {'nodes':['a','b','r','isolated'], 'edges':[['a','b'],['b','r'],['b','a']]}
        self.c = generate_certificate(self.g,'r')

    def test_serialization_rejects_malformed(self):
        mutations = [lambda c:c['candidates'].append(c['candidates'][0]),
                     lambda c:c['candidates'][0].update(rank=-1),
                     lambda c:c['candidates'][0].update(rank=True),
                     lambda c:c['candidates'][0].update(node='unknown'),
                     lambda c:c['candidates'][0].update(parent='unknown'),
                     lambda c:c['candidates'][0].update(extra=1)]
        for mutate in mutations:
            c=copy.deepcopy(self.c); mutate(c)
            with self.assertRaises(ValueError): render(self.g,'r',c)
        g=copy.deepcopy(self.g); g['edges'].append(g['edges'][0])
        with self.assertRaises(ValueError): render(g,'r',self.c)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'; p.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError): load_json(p)

    @unittest.skipUnless(os.environ.get('REPO_PROOF_LEAN'), 'set REPO_PROOF_LEAN for Lean differential execution')
    def test_differential(self):
        cases=[]
        def add(g,c,root='r'):
            try: verify_certificate(g,root,c); accepted=True
            except ValidationError: accepted=False
            cases.append((g,root,c,accepted))
        add(self.g,self.c)
        for label in ['omitted','false','root','outside','edge','cycle','rank','gaps']:
            c=copy.deepcopy(self.c)
            if label=='omitted': c['candidates']=[w for w in c['candidates'] if w['node']!='a']
            if label=='false': c['candidates'].append({'node':'isolated','parent':'r','rank':1})
            if label=='root': c['candidates']=[w for w in c['candidates'] if w['node']!='r']
            a=next((w for w in c['candidates'] if w['node']=='a'),None)
            b=next((w for w in c['candidates'] if w['node']=='b'),None)
            if label=='outside': a['parent']='isolated'
            if label=='edge': a['parent']='r'
            if label=='cycle': b['parent']='a'; b['rank']=3
            if label=='rank': a['rank']=0
            if label=='gaps':
                for w in c['candidates']: w['rank']*=7
            add(self.g,c)
        # Every directed graph on three nodes, for all three independent roots.
        names=['a','b','r']; edges=[(a,b) for a in names for b in names]
        for mask in range(512):
            g={'nodes':names, 'edges':[list(e) for i,e in enumerate(edges) if mask & (1<<i)]}
            for root in names: add(g,generate_certificate(g,root),root)
        sources=[]
        for i,(g,r,c,_) in enumerate(cases):
            s=render(g,r,c,f'T{i}').split('theorem accepted')[0]
            sources.append(s.replace('import ProofTiming\n', '')+'end T'+str(i)+'\n')
        source='import ProofTiming\n'+'\n'.join(sources)+ '\ndef main : IO Unit := do\n'
        for i in range(len(cases)):
            source+=f'  IO.println (RepoProof.check T{i}.graph T{i}.root T{i}.certificate)\n'
        source+='  IO.println (RepoProof.check T0.graph ⟨0, by decide⟩ T0.certificate)\n'
        source+='  IO.println (RepoProof.check (⟨[]⟩ : RepoProof.FiniteGraph 4) T0.root T0.certificate)\n'
        extra_expected=[]
        for graph,root in [(self.g,'a'),({'nodes':self.g['nodes'],'edges':[]},'r')]:
            try:
                verify_certificate(graph,root,self.c)
                extra_expected.append('true')
            except ValidationError:
                extra_expected.append('false')
        with tempfile.TemporaryDirectory(dir='local') as d:
            p=Path(d)/'Differential.lean'; p.write_text(source,encoding='utf-8')
            env=dict(os.environ,LEAN_PATH=str(Path('formal').resolve()))
            run=subprocess.run([os.environ['REPO_PROOF_LEAN'],'--run',str(p)],env=env,capture_output=True,text=True,timeout=600)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertEqual(run.stdout.splitlines(),[str(c[3]).lower() for c in cases]+extra_expected)
