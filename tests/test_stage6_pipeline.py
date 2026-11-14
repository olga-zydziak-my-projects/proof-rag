"""Failure-boundary tests; mocked process failures are never proof evidence."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'scripts'))
import stage6
from test_stage6_answer import fixture
from repo_proof.generator import generate_certificate
from repo_proof.stage6_export import render_query
from repo_proof.stage6_answer import expected_answer
from repo_proof.stage5_v2 import canonical
from stage4_support import file_info


class Stage6PipelineTests(unittest.TestCase):
    def test_axiom_audit_failure_cannot_release_answer(self):
        # The process is mocked to isolate the post-kernel output boundary.
        from test_stage6_axioms import valid_output
        complete = valid_output()
        bad_outputs = [
            '\n'.join(complete.splitlines()[1:]),
            complete + '\n' + complete.splitlines()[0],
            complete + "\n'QueryProof.accepted' does not depend on any axioms",
            complete.replace('[propext, Classical.choice, Quot.sound]', '[sorryAx]', 1),
        ]
        for output in bad_outputs:
            with self.subTest(output=output), tempfile.TemporaryDirectory() as d:
                c = fixture(); c.timings = {}
                cache = {'identity': 'cache', 'source_proof': {'reused': True}}
                project = Path(d); lean = project/'lean.exe'; lean.write_bytes(b'fixture')
                def process(name, command, env, folder, timeout):
                    if name == 'lean_version':
                        return dict(passed=True, stdout='Lean (version 4.35.0, fixture)', stderr='')
                    Path(command[2]).write_bytes(b'fixture output, not a real proof')
                    return dict(passed=True, stdout=output, stderr='')
                with patch.object(stage6, 'anchored_capture', return_value=c), \
                     patch.object(stage6, 'validate_cache', return_value=cache), \
                     patch.object(stage6, 'run_process', side_effect=process):
                    report = stage6.execute_query(project, project/'cache', 'a.mojom',
                                                 project/'run', lean)
                self.assertEqual(report['status'], 'QUERY_REJECTED')
                self.assertFalse(report['answer_released'])
                self.assertIn('axiom', report['error'])
                self.assertFalse((project/'run/answer.json').exists())
                self.assertFalse((project/'run/answer.txt').exists())

    def test_final_report_write_failure_revokes_promoted_answers(self):
        # This is failure-path injection, not evidence of a kernel proof.
        c = fixture(); c.timings = {}
        cache = {'identity': 'cache', 'source_proof': {'reused': True}}
        with tempfile.TemporaryDirectory() as d:
            project = Path(d); lean = project/'lean.exe'; lean.write_bytes(b'fixture')
            original_write = Path.write_bytes
            def fail_pass_report(path, raw):
                if path.name == 'query-report.json' and json.loads(raw)['status'] == 'STAGE6_QUERY_PASS':
                    raise OSError('injected final report write failure')
                return original_write(path, raw)
            def process(name, command, env, folder, timeout):
                if name == 'lean_version':
                    return dict(passed=True, stdout='Lean (version 4.35.0, fixture)', stderr='')
                Path(command[2]).write_bytes(b'fixture output, not a real proof')
                names = ('accepted', 'erased_accepted', 'paths_unique', 'source_to_answer')
                return dict(passed=True, stdout='\n'.join(
                    f"'QueryProof.{n}' does not depend on any axioms" for n in names), stderr='')
            with patch.object(stage6, 'anchored_capture', return_value=c), \
                 patch.object(stage6, 'validate_cache', return_value=cache), \
                 patch.object(stage6, 'run_process', side_effect=process), \
                 patch.object(Path, 'write_bytes', fail_pass_report):
                report = stage6.execute_query(project, project/'cache', 'a.mojom',
                                             project/'run', lean)
            self.assertEqual(report['status'], 'QUERY_REJECTED')
            self.assertIn('injected final report', report['error'])
            self.assertFalse((project/'run/answer.json').exists())
            self.assertFalse((project/'run/answer.txt').exists())
            self.assertTrue((project/'run/answer.json.failed').exists())
            self.assertEqual(json.loads((project/'run/query-report.json').read_bytes())['status'],
                             'QUERY_REJECTED')

    def test_unknown_root_cannot_release_answer(self):
        c = fixture(); c.timings = {}
        with tempfile.TemporaryDirectory() as d:
            project = Path(d); lean = project / 'lean.exe'; lean.write_bytes(b'fixture')
            with patch.object(stage6, 'anchored_capture', return_value=c):
                report = stage6.execute_query(project, project/'cache', '../a.mojom',
                                             project/'run', lean)
            self.assertEqual(report['status'], 'QUERY_REJECTED')
            self.assertFalse(report['answer_released'])
            self.assertFalse((project/'run/answer.json').exists())

    def test_compiler_failure_cannot_release_answer(self):
        c = fixture(); c.timings = {}
        cache = {'identity': 'cache', 'source_proof': {'reused': True}}
        with tempfile.TemporaryDirectory() as d:
            project = Path(d); lean = project / 'lean.exe'; lean.write_bytes(b'fixture')
            responses = [dict(passed=True, stdout='Lean (version 4.35.0, test)', stderr=''),
                         dict(passed=False, stdout='', stderr='kernel rejected', exit_code=1)]
            with patch.object(stage6, 'anchored_capture', return_value=c), \
                 patch.object(stage6, 'validate_cache', return_value=cache), \
                 patch.object(stage6, 'run_process', side_effect=responses):
                report = stage6.execute_query(project, project/'cache', 'a.mojom',
                                             project/'run', lean)
            self.assertEqual(report['status'], 'QUERY_REJECTED')
            self.assertIn('QueryProof failed', report['error'])
            self.assertFalse((project/'run/answer.json').exists())
            self.assertFalse((project/'run/answer.txt').exists())

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d); run = project/'run'; run.mkdir()
            sentinel = run/'answer.json'; sentinel.write_bytes(b'preserved')
            with self.assertRaises(FileExistsError):
                stage6.execute_query(project, project/'cache', 'a.mojom', run, project/'lean.exe')
            self.assertEqual(sentinel.read_bytes(), b'preserved')

    def test_substituted_certificate_and_proof_inputs_rejected(self):
        c = fixture(); root = 'a.mojom'; cert = generate_certificate(c.graph, root)
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); (folder/'lean').mkdir()
            content = {'certificate.json': canonical(cert),
                       'expected-answer.json': canonical(expected_answer(c, root, cert, 'cache')),
                       'lean/QueryProof.lean': render_query(c.graph, root, cert).encode()}
            for rel, raw in content.items(): (folder/rel).write_bytes(raw)
            frozen = {rel: file_info(folder/rel) for rel in content}
            stage6.validate_artifacts(folder, c, root, cert, {'identity':'cache'}, frozen)
            for rel, changed in [('certificate.json', canonical(generate_certificate(c.graph, 'c.mojom'))),
                                 ('lean/QueryProof.lean', content['lean/QueryProof.lean']+b'-- change\n')]:
                with self.subTest(rel=rel):
                    (folder/rel).write_bytes(changed)
                    with self.assertRaises(ValueError):
                        stage6.validate_artifacts(folder, c, root, cert, {'identity':'cache'}, frozen)
                    (folder/rel).write_bytes(content[rel])


if __name__ == '__main__':
    unittest.main()
