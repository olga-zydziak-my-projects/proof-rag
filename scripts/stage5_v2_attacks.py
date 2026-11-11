"""Stage 5 A-L actual input substitutions, with honest rejecting layers."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from repo_proof.stage5_v2 import capture, snapshot_payload, validate_snapshot, canonical, ROOT
from repo_proof.stage5_answer_v2 import expected_answer, check_answer, render_answer, check_human
from repo_proof.generator import generate_certificate
from repo_proof.checker import verify_certificate
from repo_proof.mojom_parser import parse_source
from repo_proof.source_bytes_v2 import certificate as byte_certificate
from stage5_v2_audit_bytes import audit as audit_bytes


def run_attacks(captured, run_dir):
    """Any accepted attack raises before a PASS report can be returned."""
    c = captured
    run_dir = Path(run_dir)
    snapshot, answer, results = snapshot_payload(c), expected_answer(c), []

    def reject(name, layer, action):
        try:
            action()
        except (ValueError, OSError) as error:
            results.append({'name': name, 'class': name[0], 'layer': layer,
                            'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError('attack accepted: ' + name)

    def source_attack(name, mutate):
        value = copy.deepcopy(snapshot)
        mutate(value)
        reject(name, 'anchored full source inventory and byte comparison', lambda: validate_snapshot(value, c))

    source_attack('A-remove-selected-source', lambda v: v['files'].pop())
    empty_path = next(row['path'] for row in c.extraction['files'] if not row['imports'])
    empty = next(i for i, blob in enumerate(c.blobs) if blob.path == empty_path)
    source_attack('A-remove-no-import-source', lambda v: v['files'].pop(empty))

    def alter(value):
        row = value['files'][0]
        data = base64.b64decode(row['data_base64']) + b'\n'
        row['data_base64'] = base64.b64encode(data).decode('ascii')
        row['sha256'] = hashlib.sha256(data).hexdigest()
        row['oid'] = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

    source_attack('B-change-bytes-update-local-identities', alter)
    source_attack('C-wrong-commit', lambda v: v['pin'].update(commit='1ab171af2976555a2b12b9bca8b984c204962ba8'))
    source_attack('C-wrong-tree', lambda v: v['pin'].update(tree='9e5b002b0ce384a82f6cb836fd3abaebab8a7da6'))

    def swap_labels(value):
        a, b = value['files'][:2]
        a['path'], b['path'] = b['path'], a['path']

    source_attack('F-swap-labels-same-count', swap_labels)
    source_attack('I-duplicate-source', lambda v: v['files'].append(copy.deepcopy(v['files'][0])))

    def graph_check(value):
        if canonical(value) != canonical(c.graph):
            raise ValueError('graph differs from captured source graph')

    for name, mutate in [
        ('D-remove-edge', lambda v: v['edges'].pop()),
        ('D-add-edge', lambda v: v['edges'].append([ROOT, ROOT])),
        ('D-same-count-replace', lambda v: v['edges'].__setitem__(0, [ROOT, ROOT])),
        ('E-delete-file-info-time', lambda v: v['edges'].remove(['mojo/public/mojom/base/file_info.mojom', ROOT])),
        ('I-duplicate-edge', lambda v: v['edges'].append(copy.deepcopy(v['edges'][0]))),
    ]:
        graph = copy.deepcopy(c.graph)
        mutate(graph)
        if name == 'I-duplicate-edge':
            reject(name, 'graph schema duplicate-edge check', lambda: generate_certificate(graph, ROOT))
            continue
        regenerated = generate_certificate(graph, ROOT)
        verify_certificate(graph, ROOT, regenerated)
        reject(name, 'full source-derived graph comparison before proof release', lambda: graph_check(graph))
        results[-1].update(regenerated_candidates=len(regenerated['candidates']), graph_relative_certificate_accepted=True)
        if name.startswith('E-') and len(regenerated['candidates']) != 473:
            raise AssertionError('real deletion did not produce the required 473-result attack')

    for name, mutate in [
        ('G-omit-path', lambda v: v['paths'].pop()),
        ('G-add-path', lambda v: v['paths'].append('extra.mojom')),
        ('G-duplicate-path', lambda v: v['paths'].__setitem__(0, v['paths'][1])),
        ('G-replace-same-count', lambda v: v['paths'].__setitem__(0, 'replacement.mojom')),
        ('H-change-root', lambda v: v['query'].update(root='different.mojom')),
        ('H-change-root-id', lambda v: v['query'].update(root_id=0)),
        ('H-change-root-policy', lambda v: v['query'].update(include_root=False)),
    ]:
        value = copy.deepcopy(answer)
        mutate(value)
        reject(name, 'full canonical answer comparison', lambda: check_answer(value, c))
        reject(name + '-human', 'independent complete human answer parse', lambda: check_human(render_answer(value), c))

    # One isolated copy is restored after each mutation. The real run is untouched.
    with tempfile.TemporaryDirectory(prefix='stage5-attacks-') as temp:
        isolated = Path(temp) / 'isolated'
        (isolated / 'lean').mkdir(parents=True)
        for name in ('snapshot.json', 'graph.json', 'certificate.json'):
            shutil.copyfile(run_dir / name, isolated / name)
        for source in (run_dir / 'lean').glob('*.lean'):
            shutil.copyfile(source, isolated / 'lean' / source.name)
        audit_bytes(isolated, c)
        names_file = isolated / 'lean/SourceNames.lean'
        original_names = names_file.read_text(encoding='utf-8')
        path0 = next(line for line in original_names.splitlines(True) if line.startswith('def path0 :'))
        path1 = next(line for line in original_names.splitlines(True) if line.startswith('def path1 :'))
        left, right = path0.split(':=', 1), path1.split(':=', 1)
        changed_names = original_names.replace(path0, left[0] + ':=' + right[1], 1)
        changed_names = changed_names.replace(path1, right[0] + ':=' + left[1], 1)
        try:
            names_file.write_text(changed_names, encoding='utf-8', newline='')
            reject('F-swap-Lean-path-bytes-same-count', 'independent filename byte/ID comparison',
                   lambda: audit_bytes(isolated, c))
        finally:
            names_file.write_text(original_names, encoding='utf-8', newline='')
        source = isolated / 'lean/SourceGroup000.lean'
        original = source.read_text(encoding='utf-8')
        first_piece = next(line for line in original.splitlines(True) if line.startswith('def f0p0 :'))
        first_file = next(line for line in original.splitlines(True) if line.startswith('def f0 :'))
        substitutions = [
            ('I-omit-source-block', original.replace(first_piece, '', 1)),
            ('I-duplicate-source-block', original + first_piece),
            ('I-omit-file-block', original.replace(first_file, '', 1)),
            ('I-duplicate-file-block', original + first_file),
            ('I-omit-proof-block', original.replace('theorem f0_ok :', 'theorem f0_hidden :', 1)),
            ('I-duplicate-proof-block', original + '\ntheorem f0_ok : True := by trivial\n'),
        ]
        for name, changed in substitutions:
            try:
                source.write_text(changed, encoding='utf-8', newline='')
                reject(name, 'persisted Lean source/byte/file/proof coverage audit', lambda: audit_bytes(isolated, c))
            finally:
                source.write_text(original, encoding='utf-8', newline='')
        audit_bytes(isolated, c)

    # Parser/model agreement supports operational J/K checks, not a parser proof.
    positive = [
        ('J-comments-strings', b'// import "fake.mojom";\n/* import "fake2.mojom"; */\nimport "r.mojom";\nconst string Text = "import \\"fake3.mojom\\";";\n', ['r.mojom']),
        ('J-attributes-and-duplicates', b'[EnableIf=flag] import "r.mojom";\nimport "r.mojom";\n', ['r.mojom', 'r.mojom']),
        ('J-legal-formatting', b'import\t/* gap */\r\n"r.mojom" /*gap*/ ;\r\n', ['r.mojom']),
    ]
    for name, data, expected in positive:
        parsed = parse_source(data, 'fixture.mojom')
        if parsed['status'] != 'parsed':
            raise AssertionError(name + ': positive fixture rejected ' + str(parsed['diagnostics']))
        actual = [row['decoded_path'] for row in parsed['imports']]
        _, projected = byte_certificate(data)
        if actual != expected or projected != expected:
            raise AssertionError(name + ': false or missing import')
        results.append({'name': name, 'class': 'J', 'layer': 'pinned full parser and byte projection model',
                        'passed': True, 'imports': actual, 'no_false_imports': True})

    negative = [
        ('K-malformed-body', b'import "r.mojom"; struct Broken { this is not a field; };'),
        ('K-unterminated-comment', b'/* import "r.mojom";'),
        ('K-unterminated-string', b'import "r.mojom'),
        ('K-invalid-utf8', b'//\xc0\x80\n'),
        ('K-unsupported-bom', b'\xef\xbb\xbfmodule target;'),
    ]
    for name, data in negative:
        parsed = parse_source(data, 'fixture.mojom')
        if parsed['status'] != 'unresolved' or not parsed['diagnostics']:
            raise AssertionError(name + ': malformed input became complete extraction')
        results.append({'name': name, 'class': 'K', 'layer': 'pinned full parser/strict encoding input gate',
                        'rejected': True, 'status': parsed['status'], 'diagnostics': parsed['diagnostics']})
    reject('K-unsupported-import-escape', 'byte projection unsupported-input rejection',
           lambda: byte_certificate(b'import "r\\x.mojom";'))

    from repo_proof.stage5_run_v2 import seal, check_seal
    with tempfile.TemporaryDirectory(prefix='stage5-run-binding-') as temp:
        run = Path(temp) / 'run'
        (run / 'lean').mkdir(parents=True)
        for name, value in [('snapshot.json', snapshot), ('graph.json', c.graph), ('certificate.json', c.certificate)]:
            (run / name).write_bytes(canonical(value))
        (run / 'lean/Fixture.lean').write_text('def fixture : Nat := 0\n', encoding='utf-8')
        expected = seal(run, 'run-A')
        check_seal(run, expected, 'run-A')
        reject('L-cross-run-receipt', 'run nonce and immutable expected seal', lambda: check_seal(run, expected, 'run-B'))
        other = Path(temp) / 'other-run'
        shutil.copytree(run, other)
        (other / 'run-seal.json').unlink()
        seal(other, 'run-B')
        original_seal = (run / 'run-seal.json').read_bytes()
        shutil.copyfile(other / 'run-seal.json', run / 'run-seal.json')
        reject('L-mix-persisted-run-seal', 'persisted receipt and immutable expected run identity',
               lambda: check_seal(run, expected, 'run-A'))
        (run / 'run-seal.json').write_bytes(original_seal)
        old = (run / 'snapshot.json').read_bytes()
        (run / 'snapshot.json').write_bytes(old + b' ')
        reject('L-change-source-after-validation', 'persisted input consumption-boundary seal', lambda: check_seal(run, expected, 'run-A'))
        (run / 'snapshot.json').write_bytes(old)
        old_proof = (run / 'lean/Fixture.lean').read_bytes()
        (run / 'lean/Fixture.lean').write_bytes(old_proof.replace(b'0', b'1'))
        reject('L-change-proof-after-validation', 'persisted proof consumption-boundary seal', lambda: check_seal(run, expected, 'run-A'))

    classes = sorted(set(row['class'] for row in results))
    if classes != list('ABCDEFGHIJKL'):
        raise AssertionError('incomplete attack classes: ' + repr(classes))
    return {'status': 'ATTACKS_A_L_PASS', 'classes': classes, 'checks': results,
            'note': 'Rejections are attributed to their actual operational layer; projection kernel fixtures are audited separately.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', default='local/stage5-v2/full-01')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = run_attacks(capture(Path.cwd()), args.run_dir)
    with Path(args.output).open('xb') as target:
        target.write(canonical(result))
    print(json.dumps({'status': result['status'], 'checks': len(result['checks']), 'classes': result['classes']}))


if __name__ == '__main__':
    main()
