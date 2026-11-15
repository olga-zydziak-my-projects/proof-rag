"""Offline tests: SDK responses and process results here are explicit fakes."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace as NS
import tempfile
import unittest
from unittest.mock import patch, Mock

from repo_proof.stage7 import (Stage7Error, validate_interpretation, parse_response,
    resolve, accept_stage6, render, run, ClaudeInterpreter, validate_question)
from repo_proof.generator import generate_certificate
from repo_proof.stage6_answer import expected_answer, render_answer
from repo_proof.stage5_v2 import canonical


class Stage7Tests(unittest.TestCase):
    nodes = ['a/time.mojom', 'b/frame.mojom', 'c/frame.mojom']

    def interpretation(self, ref='time.mojom', op='reverse_importers'):
        return {'operation': op, 'file_reference': ref}

    def response(self, text=None, stop='end_turn', blocks=None):
        return NS(stop_reason=stop, content=blocks if blocks is not None else
                  [NS(type='text', text=text or json.dumps(self.interpretation()))])

    def test_exact_and_unique(self):
        for ref in ('time.mojom', 'a/time.mojom'):
            with self.subTest(ref=ref):
                plan = resolve(self.interpretation(ref), 'All importers of '+ref, self.nodes)
                self.assertEqual(plan['root'], 'a/time.mojom')
                self.assertEqual(plan['status'], 'ready')

    def test_ambiguous(self):
        plan = resolve(self.interpretation('frame.mojom'), 'import frame.mojom', self.nodes)
        self.assertEqual(plan, {'status': 'needs_clarification', 'root': None,
                               'candidates': ['b/frame.mojom', 'c/frame.mojom']})

    def test_no_guessing(self):
        for ref in ('Time.mojom', 'missing.mojom', 'x/time.mojom', 'a/../a/time.mojom',
                    './a/time.mojom', 'a//time.mojom', 'a\\time.mojom'):
            with self.subTest(ref=ref):
                self.assertEqual(resolve(self.interpretation(ref), 'import '+ref,
                                         self.nodes)['status'], 'not_found')

    def test_unsupported_direction_scope_and_clarification(self):
        for question in ('What does time.mojom import?', 'Only direct importers of time.mojom'):
            plan = resolve(self.interpretation(op='unsupported'), question, self.nodes)
            self.assertEqual(plan['status'], 'unsupported')
            self.assertIsNone(plan['root'])
        self.assertEqual(resolve(self.interpretation(None, 'needs_clarification'),
                                 'All importers?', self.nodes)['status'], 'needs_clarification')

    def test_invalid_schema_and_unquoted_file(self):
        invalid = [self.interpretation('invented.mojom'), {}, [],
                   {**self.interpretation(), 'command': 'run'},
                   self.interpretation(None), self.interpretation(12),
                   self.interpretation(op=True), self.interpretation(op='forward'),
                   {'operation': 'unsupported'}, self.interpretation('')]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(Stage7Error):
                validate_interpretation(value, 'All importers of time.mojom')

    def test_substring_is_not_a_literal_file(self):
        for question in ('a/time.mojom', 'other_time.mojom', 'time.mojomx', 'time.mojom.bak'):
            with self.subTest(question=question), self.assertRaises(Stage7Error):
                validate_interpretation(self.interpretation(), question)

    def test_sentence_punctuation(self):
        self.assertEqual(validate_interpretation(self.interpretation(),
                         'All importers of time.mojom.'), self.interpretation())

    def test_local_scope_veto_for_misclassified_model_output(self):
        questions = ('Co importuje time.mojom?', 'Które pliki importuje time.mojom?',
                     'What does time.mojom import?', 'Only direct importers of time.mojom',
                     'Tylko bezpośrednich importerów time.mojom',
                     'Importerzy time.mojom bez pośrednich')
        for question in questions:
            with self.subTest(question=question):
                self.assertEqual(resolve(self.interpretation(), question, self.nodes)['status'], 'unsupported')

    def test_invalid_response_keeps_safe_evidence(self):
        client = ClaudeInterpreter.__new__(ClaudeInterpreter)
        client.requests, client.limit, client.sdk_version = 0, 1, 'fake'
        client.model, client.effort = 'fake', 'medium'
        client.client = Mock()
        response = self.response(stop='max_tokens')
        response.model_dump = Mock(return_value={'usage': {'output_tokens': 1024}})
        client.client.messages.create.return_value = response
        with self.assertRaises(Stage7Error) as error:
            client.interpret('time.mojom')
        self.assertEqual(error.exception.evidence['response']['usage']['output_tokens'], 1024)

    def test_blocks_by_type(self):
        blocks = [NS(type='thinking', thinking='ignored'),
                  NS(type='text', text=json.dumps(self.interpretation()))]
        self.assertEqual(parse_response(self.response(blocks=blocks), 'time.mojom'), self.interpretation())

    def test_refusal_truncation_missing_and_multiple_text(self):
        for response in [self.response(stop='refusal'), self.response(stop='max_tokens'),
                         self.response(stop='pause_turn'), self.response(blocks=[]),
                         self.response(blocks=[NS(type='refusal')]),
                         self.response(blocks=[NS(type='text', text='{}'), NS(type='text', text='{}')])]:
            with self.subTest(response=response), self.assertRaises(Stage7Error):
                parse_response(response, 'time.mojom')

    def test_invalid_json_and_duplicate_fields(self):
        for text in ('{', 'null', '[]', '{"operation":"unsupported","operation":"unsupported","file_reference":null}'):
            with self.subTest(text=text), self.assertRaises(Stage7Error):
                parse_response(self.response(text), 'time.mojom')

    def test_input_limits(self):
        for question in ('', '  ', 'ą'*4001, None):
            with self.subTest(question=str(question)[:20]), self.assertRaises(Stage7Error):
                validate_question(question)

    def test_missing_key(self):
        with patch.dict('os.environ', {}, clear=True), self.assertRaises(Stage7Error):
            ClaudeInterpreter()

    def test_api_limits_and_errors_without_sdk(self):
        # Explicit client fake; exercises redaction and physical call accounting.
        client = ClaudeInterpreter.__new__(ClaudeInterpreter)
        client.requests, client.limit = 0, 1
        client.model, client.effort = 'fake', 'medium'
        client.client = Mock()
        client.client.messages.create.side_effect = RuntimeError('sensitive payload')
        with self.assertRaisesRegex(Stage7Error, 'RuntimeError') as error:
            client.interpret('time.mojom')
        self.assertNotIn('sensitive', str(error.exception))
        with self.assertRaisesRegex(Stage7Error, 'limit'):
            client.interpret('time.mojom')
        self.assertEqual(client.client.messages.create.call_count, 1)

    def fixture(self, folder):
        c = NS(graph={'nodes': ['a/time.mojom', 'b/frame.mojom'],
                      'edges': [['b/frame.mojom', 'a/time.mojom']]},
               pin={'manifest_sha256': 'fake-source-identity'})
        cert = generate_certificate(c.graph, 'a/time.mojom')
        answer = expected_answer(c, 'a/time.mojom', cert, 'fake-cache')
        for name, value in [('certificate.json', cert), ('answer.json', answer)]:
            (folder/name).write_bytes(canonical(value))
        (folder/'answer.txt').write_bytes(render_answer(answer).encode())
        report = {'status': 'STAGE6_QUERY_PASS', 'passed': True, 'answer_released': True,
                  'root': 'a/time.mojom', 'cache_identity': 'fake-cache',
                  'answer': {'paths': 2}}
        for name, key in [('answer.json', 'json'), ('answer.txt', 'text')]:
            raw = (folder/name).read_bytes()
            report['answer'][key] = {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}
        (folder/'query-report.json').write_bytes(canonical(report))
        return c, answer, report

    def test_full_answers_and_render(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            c, answer, _ = self.fixture(folder)
            accepted = accept_stage6(folder, 'a/time.mojom', c, 'fake-cache', 0)
            self.assertEqual(accepted, answer)
            text = render(accepted, folder/'query-report.json')
            self.assertEqual(text.split('Pełna lista:\n')[1].splitlines(), answer['paths'])
            self.assertIn('nie dowodzi poprawności interpretacji', text)

    def test_process_and_report_failures(self):
        for mutation in ({'status': 'FAILED'}, {'passed': False}, {'answer_released': False},
                         {'root': 'b/frame.mojom'}, {'cache_identity': 'other'},
                         {'answer': {'paths': 0}}):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                c, _, report = self.fixture(folder)
                report.update(mutation)
                (folder/'query-report.json').write_bytes(canonical(report))
                with self.assertRaises(ValueError):
                    accept_stage6(folder, 'a/time.mojom', c, 'fake-cache', 0)
        with tempfile.TemporaryDirectory() as temp:
            c, _, _ = self.fixture(Path(temp))
            with self.assertRaises(Stage7Error):
                accept_stage6(Path(temp), 'a/time.mojom', c, 'fake-cache', 1)

    def test_complete_list_tampering(self):
        for name in ('answer.json', 'answer.txt'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                c, answer, _ = self.fixture(folder)
                if name.endswith('.json'):
                    answer['paths'] = ['a/time.mojom']
                    (folder/name).write_bytes(canonical(answer))
                else:
                    (folder/name).write_text(render_answer(answer).replace('b/frame.mojom\n', ''), encoding='utf-8')
                with self.assertRaises(ValueError):
                    accept_stage6(folder, 'a/time.mojom', c, 'fake-cache', 0)

    def test_report_digest_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            c, _, report = self.fixture(folder)
            report['answer']['json']['sha256'] = '0'*64
            (folder/'query-report.json').write_bytes(canonical(report))
            with self.assertRaises(Stage7Error):
                accept_stage6(folder, 'a/time.mojom', c, 'fake-cache', 0)

    def test_orchestration_stops_before_proof(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
        for operation in ('unsupported', 'needs_clarification'):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as temp:
                interpreter = Mock()
                interpreter.interpret.return_value = (self.interpretation(None, operation), {'fake': True})
                with patch('repo_proof.stage7.anchored_capture', return_value=NS(graph={'nodes': self.nodes})), \
                     patch('repo_proof.stage7.validate_cache', return_value={'identity': 'fake'}), \
                     patch('repo_proof.stage7.subprocess.run') as process:
                    result = run('question', interpreter, Path(temp), Path(temp)/'cache',
                                 Path(temp)/'run', Path(temp)/'lean')
                    self.assertFalse(result['verified'])
                    self.assertEqual(result['status'], operation)
                    process.assert_not_called()
                    interpreter.interpret.assert_called_once_with('question')
                    self.assertFalse((Path(temp)/'run/answer.txt').exists())

    def test_orchestration_failure_releases_nothing(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
        for failure in ('process', 'timeout', 'acceptance'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temp:
                interpreter = Mock()
                interpreter.interpret.return_value = (self.interpretation(), {'fake': True})
                with patch('repo_proof.stage7.anchored_capture', return_value=NS(graph={'nodes': self.nodes})), \
                     patch('repo_proof.stage7.validate_cache', return_value={'identity': 'fake'}), \
                     patch('repo_proof.stage7.subprocess.run') as process, \
                     patch('repo_proof.stage7.accept_stage6', side_effect=Stage7Error('reject')):
                    if failure == 'timeout':
                        from subprocess import TimeoutExpired
                        process.side_effect = TimeoutExpired('fake', 1)
                    else:
                        process.return_value = NS(returncode=1 if failure == 'process' else 0,
                                                  stdout=b'fake', stderr=b'')
                    result = run('All importers of time.mojom', interpreter, Path(temp),
                                 Path(temp)/'cache', Path(temp)/'run', Path(temp)/'lean')
                    self.assertFalse(result['verified'])
                    self.assertFalse((Path(temp)/'run/answer.txt').exists())
                    args, kwargs = process.call_args
                    self.assertIsInstance(args[0], list)
                    self.assertFalse(kwargs['shell'])
                    self.assertNotIn('ANTHROPIC_API_KEY', kwargs['env'])


if __name__ == '__main__':
    unittest.main()
