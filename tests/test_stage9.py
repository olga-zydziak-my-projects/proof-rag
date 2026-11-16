"""Stage 9 attacks on source shards, contextual identity, reuse and publication."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import stage9
from stage9_export import export_sources,audit_sources,export_query,audit_query
from repo_proof.stage8_graph import reverse_index,search
from repo_proof.stage8_sources import capture
from repo_proof.stage8_fixture import create
from repo_proof.stage5_v2 import canonical


class Stage9Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.names=[('a@upstream','1'*40,'a.mojom'),('b@default','2'*40,'b.mojom'),('c@default','3'*40,'c.mojom')]
        self.sources=[b'module a;',b'module b; import "a/a.mojom";',b'module c; import "a/a.mojom";']
        self.rules=[{'id':str(i),'from':list(self.names[i][:2]),'prefix':'a/',
                    'to':list(self.names[0][:2]),'target_prefix':'','evidence':'config'} for i in (1,2)]
        self.edges=np.array([[1,0],[2,0]],dtype=np.int64)

    def exported(self):
        export_sources(self.folder,self.names,self.sources,self.rules,self.edges)

    def rejects_source(self,path,change,names=None,sources=None,rules=None,edges=None):
        self.exported()
        p=self.folder/path
        p.write_text(change(p.read_text(encoding='utf-8')),encoding='utf-8',newline='\n')
        with self.assertRaises(ValueError):
            audit_sources(self.folder,names or self.names,sources or self.sources,rules or self.rules,self.edges if edges is None else edges)

    def test_complete_shards_and_query_audits(self):
        self.exported()
        self.assertTrue(audit_sources(self.folder,self.names,self.sources,self.rules,self.edges))
        ids,p,r=search(3,reverse_index(3,self.edges),0)
        export_query(self.folder,3,self.edges,0,ids,p[ids],r[ids])
        self.assertTrue(audit_query(self.folder,3,self.edges,0,ids,p[ids],r[ids]))

    def test_changed_source_bytes(self):
        changed=list(self.sources); changed[0]+=b'\n'
        self.rejects_source('SourceNames.lean',lambda s:s,sources=changed)

    def test_omitted_source(self):
        self.rejects_source('SourceGroup0000.lean',lambda s:s.replace('def file1 :','def omitted :',1))

    def test_omitted_import_edge(self):
        self.rejects_source('SourceGroup0000.lean',lambda s:s,edges=self.edges[:1])

    def test_wrong_project_commit_and_context(self):
        self.exported()
        for field,value in ((0,'a@other-context'),(1,'4'*40)):
            names=list(self.names); row=list(names[0]); row[field]=value; names[0]=tuple(row)
            with self.assertRaises(ValueError):
                audit_sources(self.folder,names,self.sources,self.rules,self.edges)
        with self.assertRaises(ValueError):
            stage9.identities([{'repo_id':'chromium','commit':'1'*40,'path':'x.mojom'}],{**stage9.CONTEXTS,'chromium':'electron-default'})

    def test_rule_mapping_changed(self):
        rules=deepcopy(self.rules); rules[0]['target_prefix']='wrong/'
        self.rejects_source('SourceNames.lean',lambda s:s,rules=rules)

    def test_inverse_export_substitution(self):
        self.rejects_source('SourceNames.lean',lambda s:s.replace('then some ⟨0,','then some ⟨1,',1))

    def test_extra_lean_command(self):
        self.rejects_source('SourceGroup0000.lean',lambda s:s+'axiom extra : False\n')

    def test_missing_or_extra_answer(self):
        ids,p,r=search(3,reverse_index(3,self.edges),0)
        for wrong in (ids[:2],np.append(ids,2)):
            export_query(self.folder,3,self.edges,0,ids,p[ids],r[ids])
            path=self.folder/'QueryAnswer.lean'
            path.write_text(path.read_text(encoding='utf-8').replace(':= [⟨0,',':= [⟨2,',1),encoding='utf-8')
            with self.assertRaises(ValueError):
                audit_query(self.folder,3,self.edges,0,wrong,p[wrong],r[wrong])

    def test_corrupted_certificate(self):
        ids,p,r=search(3,reverse_index(3,self.edges),0)
        with self.assertRaises(ValueError):
            export_query(self.folder,3,self.edges,0,ids,p[ids],np.zeros(3,dtype=np.int64))

    def test_axiom_report_missing_invalid_and_extra(self):
        module='Demo'
        (self.folder/'lean').mkdir(); (self.folder/'logs'/module).mkdir(parents=True)
        source=self.folder/'lean/Demo.lean'; source.write_text('#print axioms Demo.ok\n')
        source.with_suffix('.olean').write_bytes(b'unit fixture only')
        output=self.folder/'logs/Demo/stdout.log'; (self.folder/'logs/Demo/stderr.log').write_bytes(b'')
        good="'Demo.ok' does not depend on any axioms\n"
        output.write_text(good)
        record={'source_sha256':stage9.digest(source),'olean_sha256':stage9.digest(source.with_suffix('.olean')),
                'theorems':['Demo.ok'],'axioms':{'Demo.ok':[]}}
        stage9.verify_modules(self.folder,{'Demo':record})
        for bad in ('',"'Demo.ok' depends on axioms: [sorryAx]\n",good+good,good+'garbage\n'):
            output.write_text(bad)
            with self.assertRaises(ValueError):stage9.verify_modules(self.folder,{'Demo':record})
        output.write_text(good); source.with_suffix('.olean').write_bytes(b'substituted')
        with self.assertRaises(ValueError):stage9.verify_modules(self.folder,{'Demo':record})

    def test_independent_receipt_anchor_rejects_changed_manifest(self):
        p=self.folder/'receipt.json'; p.write_bytes(b'{"status":"PASS"}')
        anchor=stage9.digest(p); p.write_bytes(b'{"status":"PASS","changed":true}')
        with self.assertRaises(ValueError):stage9.anchored(p,anchor)

    def test_failed_query_cannot_publish_or_reuse_old_directory(self):
        a=SimpleNamespace(run_dir=str(self.folder/'query'))
        with patch.object(stage9,'validate_prepared',side_effect=ValueError('stale cache')):
            result=stage9.query(a)
        self.assertFalse(result['formally_verified'])
        self.assertFalse((Path(a.run_dir)/'answer.json').exists())
        with self.assertRaises(FileExistsError):stage9.query(a)

    def test_file_rule_mode_is_explicit_and_ambiguity_is_rejected(self):
        root=self.folder/'git-fixture'; manifest,_,locations=create(root)
        # Replace directory rules with file prefixes. The old CLI continues to
        # reject these unless the new explicit option is supplied.
        rule=manifest['rules'][0]
        rule['prefix']='a/a.mojom'; rule['target_prefix']='local/a.mojom'
        raw=canonical(manifest); path=root/'changed.json'; path.write_bytes(raw)
        with self.assertRaises(ValueError):capture(path,sha256(raw).hexdigest(),locations)
        capture(path,sha256(raw).hexdigest(),locations,file_prefixes=True)
        manifest['rules'].append(deepcopy(manifest['rules'][-1]))
        manifest['rules'][-1]['id']='ambiguous'
        raw=canonical(manifest); path.write_bytes(raw)
        with self.assertRaises(ValueError):capture(path,sha256(raw).hexdigest(),locations,file_prefixes=True)

    def test_stale_bytecode_prefix_is_rejected(self):
        cache=self.folder/'bytecode'; cache.mkdir()
        with patch.object(sys,'pycache_prefix',str(cache)),patch.object(sys,'dont_write_bytecode',True),patch.object(sys,'flags',SimpleNamespace(no_site=1)):
            stage9.bytecode_policy()
            (cache/'stale.pyc').write_bytes(b'stale')
            with self.assertRaises(ValueError):stage9.bytecode_policy()

    def test_timeout_and_resource_limit_cannot_publish(self):
        for status in ('TIMEOUT','RESOURCE_LIMIT','FAILED','PROCESS_PASS'):
            folder=self.folder/status; folder.mkdir()
            answer={'formally_verified':False,'results':[{'path':'x.mojom'}]}
            stage9.write(folder/'candidate-answer.json',answer)
            stage9.write(folder/'query.json',{'status':'KERNEL_QUERY_PASS','answer':answer})
            stage9.write(folder/'oracle.json',answer['results'])
            resource=folder/'resources.json'
            stage9.write(resource,{'status':status,'remaining_job_processes':1 if status=='PROCESS_PASS' else 0,'exit_code':0})
            result=stage9.finalize_run('query',folder,resource,stage9.PROJECT/'verification/stage9-config.json')
            self.assertFalse(result['formally_verified']); self.assertFalse((folder/'answer.json').exists())
            self.assertFalse((folder/'candidate-answer.json').exists())

    def test_supervisor_pass_publishes_complete_answer(self):
        answer={'formally_verified':False,'results':[{'path':'x.mojom'},{'path':'y.mojom'}]}
        stage9.write(self.folder/'candidate-answer.json',answer)
        stage9.write(self.folder/'query.json',{'status':'KERNEL_QUERY_PASS','answer':answer})
        stage9.write(self.folder/'oracle.json',answer['results'])
        resource=self.folder/'resources.json'
        stage9.write(resource,{'status':'PROCESS_PASS','remaining_job_processes':0,'exit_code':0})
        result=stage9.finalize_run('query',self.folder,resource,stage9.PROJECT/'verification/stage9-config.json')
        self.assertTrue(result['formally_verified']); self.assertEqual(stage9.read(self.folder/'answer.json')['results'],answer['results'])

    def reuse_fixture(self):
        prepared=self.folder/'prepared'; prepared.mkdir()
        resource=self.folder/'resource.json'
        stage9.write(resource,{'status':'PROCESS_PASS','remaining_job_processes':0,'exit_code':0})
        config=stage9.PROJECT/'verification/stage9-config.json'
        env={'code':'code','dependencies':'deps','lean_toolchain':'lean','python_runtime':'python','git_runtime':'git','specifications':'spec'}
        receipt={'status':'SOURCE_LAYER_PASS','source_to_graph':True,'manifest_sha256':'a'*64,
            'environment':env,'artifact_inventory':{},'modules':{},'config_sha256':stage9.digest(config),
            'supervision':{'path':str(resource),'sha256':stage9.digest(resource)}}
        stage9.write(prepared/'prepare.json',receipt)
        a=SimpleNamespace(prepared_dir=prepared,prepared_sha256=stage9.digest(prepared/'prepare.json'),
                          manifest_sha256='a'*64,lean='unused-unit-fixture',config=config)
        return a,receipt

    def test_real_reuse_validator_rejects_each_stale_environment_component(self):
        a,receipt=self.reuse_fixture()
        for component in receipt['environment']:
            changed={**receipt['environment'],component:'changed'}
            with self.subTest(component=component),patch.object(stage9,'environment',return_value=changed):
                with self.assertRaisesRegex(ValueError,'full code/dependency/tool/spec'):
                    stage9.validate_prepared(a,self.folder)

    def test_real_reuse_validator_rejects_substituted_artifact(self):
        a,receipt=self.reuse_fixture(); (Path(a.prepared_dir)/'substituted.olean').write_bytes(b'changed')
        with patch.object(stage9,'environment',return_value=receipt['environment']):
            with self.assertRaisesRegex(ValueError,'artifact inventory'):
                stage9.validate_prepared(a,self.folder)

    def test_reuse_requires_successful_supervised_preparation(self):
        a,receipt=self.reuse_fixture()
        receipt['supervision']['sha256']='0'*64; stage9.write(Path(a.prepared_dir)/'prepare.json',receipt)
        a.prepared_sha256=stage9.digest(Path(a.prepared_dir)/'prepare.json')
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):stage9.validate_prepared(a,self.folder)

    def test_actual_inventory_changes_after_code_or_artifact_mutation(self):
        code=self.folder/'source.py'; code.write_text('original')
        before=stage9.file_inventory(self.folder); code.write_text('changed')
        self.assertNotEqual(before,stage9.file_inventory(self.folder))

    def test_aggregate_cannot_accept_forged_pass_labels(self):
        import stage9_run
        root=self.folder/'aggregate'; (root/'verification').mkdir(parents=True)
        manifest=root/'verification/stage9-manifest.json'; stage9.write(manifest,{})
        anchor=stage9.digest(manifest)
        reports={'stage9-manifest-anchor.json':{'sha256':anchor},
            'stage9-corpus.json':{'manifest_sha256':anchor,'real_distinct_files':1251,'projects':3},
            'stage9-corpus-review.json':{'status':'CORPUS_REVIEW_PASS','blocking_findings':[],'manifest_sha256':anchor},
            'stage9-regression.json':{'status':'REGRESSION_PASS','tests':0,'code_and_tests':{}},
            'stage9-measurements.json':{'status':'QUERIES_PASS','samples':[]},
            'stage9-formal-review.json':{'status':'FORMAL_REVIEW_PASS','blocking_findings':[]}}
        for name,value in reports.items():stage9.write(root/'verification'/name,value)
        with patch.object(stage9_run,'PROJECT',root):
            result=stage9_run.status(root/'missing-prepare',Path('unused'),Path('unused'),candidate=True)
        self.assertEqual(result['status'],'STAGE9_INCOMPLETE')
        self.assertFalse(result['gates']['G3_all_sources_formal'])
        self.assertFalse(result['gates']['G9_full_regression'])

    def test_aggregate_rejects_resource_label_without_profile(self):
        import stage9_run
        path=self.folder/'resources.json'
        stage9.write(path,{'status':'PROCESS_PASS','exit_code':0,'remaining_job_processes':0,'limits':{}})
        with self.assertRaises(ValueError):
            stage9_run.checked_resource({'path':str(path),'sha256':stage9.digest(path)},600,self.folder)

    def test_public_cli_waits_and_propagates_failed_query(self):
        root=Path(stage9.__file__).resolve().parents[1]
        run=self.folder/'public-cli'/'work'
        # Missing accepted receipt fails before any expensive source check.
        command=[sys.executable,'-B',str(root/'scripts/stage9.py'),'query',
            '--manifest',str(root/'verification/stage9-manifest.json'),'--manifest-sha256','0'*64,
            '--locations','unused','--lean',sys.executable,'--run-dir',str(run),
            '--prepared-dir',str(self.folder/'absent'),'--prepared-sha256','0'*64,
            '--repo-id','chromium','--commit','1'*40,'--context','upstream','--path','x.mojom']
        result=subprocess.run(command,capture_output=True,timeout=45,cwd=root)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(stage9.read(run/'query.json')['status'],'QUERY_FAILED')
        self.assertFalse((run/'answer.json').exists())
        resources=stage9.read(run.with_name('work-control')/'process/resource-report.json')
        self.assertEqual(resources['remaining_job_processes'],0)

    def test_measurement_driver_requires_independent_preparation_anchor(self):
        import stage9_run
        prepared=self.folder/'untrusted-cache'; prepared.mkdir()
        stage9.write(prepared/'prepare.json',{'status':'SOURCE_LAYER_PASS'})
        with self.assertRaisesRegex(ValueError,'independent preparation anchor'):
            stage9_run.queries(self.folder/'measurement',prepared,Path('unused'),Path('unused'),'0'*64)


if __name__=='__main__':unittest.main()
