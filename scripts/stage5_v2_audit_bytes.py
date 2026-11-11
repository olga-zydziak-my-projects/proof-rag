"""Compare every packed Lean source block with a fresh anchored capture.

This is an IO boundary check, not a replacement for the Lean transition proofs.
"""
import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from repo_proof.stage5_v2 import capture, canonical, validate_snapshot
from repo_proof.extraction import read_json


def route_body(body, leaf_pattern, n):
    """Parse the entire decision expression, then evaluate every domain point."""
    token = re.compile(r'\s*(?:if v\.val < (\d+) then|(else)|('+leaf_pattern+r'))')
    tokens=[]
    pos=0
    while body[pos:].strip():
        match=token.match(body,pos)
        if not match: raise ValueError('unexpected routing expression')
        tokens.append(match.groups()); pos=match.end()
    cursor=0
    def parse():
        nonlocal cursor
        if cursor>=len(tokens): raise ValueError('incomplete routing expression')
        bound,otherwise,leaf=tokens[cursor]; cursor+=1
        if leaf is not None: return ('leaf',leaf)
        if bound is None or otherwise is not None: raise ValueError('unexpected routing else')
        yes=parse()
        if cursor>=len(tokens) or tokens[cursor][1] is None: raise ValueError('routing else missing')
        cursor+=1
        return ('if',int(bound),yes,parse())
    expression=parse()
    if cursor!=len(tokens): raise ValueError('extra routing tokens')
    def at(i,node):
        if node[0]=='leaf': return node[1]
        return at(i,node[2] if i<node[1] else node[3])
    return [at(i,expression) for i in range(n)]


def unpack(size, packed):
    size, packed = int(size), int(packed, 16)
    if size < 0 or packed >= 256 ** size:
        raise ValueError('noncanonical packed bytes')
    return packed.to_bytes(size, 'little')


def audit(folder, captured):
    folder = Path(folder)
    validate_snapshot(read_json(folder / 'snapshot.json'), captured)
    if canonical(read_json(folder / 'graph.json')) != canonical(captured.graph):
        raise ValueError('graph differs from captured extraction')
    if canonical(read_json(folder / 'certificate.json')) != canonical(captured.certificate):
        raise ValueError('certificate differs from captured extraction')
    names = (folder / 'lean/SourceNames.lean').read_text(encoding='utf-8')
    paths = re.findall(r'^def path(\d+) : Path := \(⟨(\d+), 0x([0-9a-f]+)⟩ : SourceBytes.Block\).bytes$', names, re.M)
    if len(paths) != len(captured.blobs):
        raise ValueError('path coverage')
    for expected, (index, size, packed) in enumerate(paths):
        if int(index) != expected or unpack(size, packed) != captured.blobs[expected].path.encode('utf-8'):
            raise ValueError('path bytes or ID changed')
    body=names.split('def names ',1)[1].split(':=',1)[1].split('def inverse ',1)[0]
    if route_body(body,r'path\d+',len(paths))!=[f'path{i}' for i in range(len(paths))]:
        raise ValueError('filename routing changed')
    seen = []
    count = 0
    for module in sorted((folder / 'lean').glob('SourceGroup*.lean')):
        text = module.read_text(encoding='utf-8')
        pieces = {}
        for index, chunk, size, packed in re.findall(r'^def f(\d+)p(\d+) : SourceBytes.Piece := ⟨⟨(\d+), 0x([0-9a-f]+)⟩,', text, re.M):
            key = (int(index), int(chunk))
            if key in pieces:
                raise ValueError('duplicate source block')
            pieces[key] = unpack(size, packed)
        used = set()
        module_ids = []
        for index, refs in re.findall(r'^def f(\d+) : File \d+ := ⟨\[([^\]]*)\],', text, re.M):
            index = int(index)
            module_ids.append(index)
            expected_refs = [(index, j) for j in range(len([k for k in pieces if k[0] == index]))]
            actual_refs = [(int(a), int(b)) for a, b in re.findall(r'f(\d+)p(\d+)', refs)]
            if actual_refs != expected_refs:
                raise ValueError('source block omission, duplication or order')
            if refs != ', '.join(f'f{a}p{b}' for a, b in actual_refs):
                raise ValueError('unexpected source list syntax')
            raw = b''.join(pieces[key] for key in actual_refs)
            if raw != captured.blobs[index].data:
                raise ValueError('actual Lean source bytes differ from anchored Git object')
            seen.append(index)
            used.update(actual_refs)
        if used != set(pieces):
            raise ValueError('unreferenced source blocks')
        proofs = [int(i) for i in re.findall(r'^theorem f(\d+)_ok :', text, re.M)]
        if proofs != module_ids:
            raise ValueError('file proof omission, duplication or order')
        count += len(pieces)
    if seen != list(range(len(captured.blobs))):
        raise ValueError('file omission, duplication or order')
    master_path=folder/'lean/ChromiumSource.lean'
    if master_path.exists():
        master=master_path.read_text(encoding='utf-8')
        body=master.split('def files ',1)[1].split(':=',1)[1].split('theorem files_checked',1)[0]
        expected=[f'SourceGroup{i//64:03}.f{i}' for i in seen]
        if route_body(body,r'SourceGroup\d+\.f\d+',len(seen))!=expected:
            raise ValueError('file routing changed')
        ids_text=master.split('def resultIDs ',1)[1].split(':= [',1)[1].split(']',1)[0]
        actual_ids=[int(i) for i in re.findall(r'⟨(\d+), by decide \+kernel⟩',ids_text)]
        expected_paths=[x['node'] for x in captured.certificate['candidates']]
        if [captured.blobs[i].path for i in actual_ids]!=expected_paths:
            raise ValueError('certified output ID sequence changed')
        payload=master.split('def payloadPaths : List Path := ',1)[1].split('\ntheorem answer_checked',1)[0]
        if json.loads(payload)!=[list(p.encode('utf-8')) for p in expected_paths]:
            raise ValueError('certified complete payload path sequence changed')
    return {'passed': True, 'files': len(seen), 'source_bytes': sum(len(b.data) for b in captured.blobs),
            'packed_blocks': count, 'comparison': 'full decoded bytes, not hashes or counts alone'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--report')
    args = parser.parse_args()
    result = audit(args.run_dir, capture(Path.cwd()))
    print(json.dumps(result))
    report=Path(args.report) if args.report else Path(args.run_dir)/'byte-audit.json'
    with report.open('xb') as target:
        target.write(canonical(result))
