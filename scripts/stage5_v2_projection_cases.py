"""Kernel checks for specified lexical positives and explicit rejections."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.source_bytes_v2 import bytes_literal

CASES=[
 ('empty',b'',True,[]),
 ('simple',b'import "a.mojom";',True,['a.mojom']),
 ('comments',b'// import "bad";\n/* import "bad"; */ import "a.mojom";',True,['a.mojom']),
 ('string',b'const string x = "import \\"bad\\";";',True,[]),
 ('attributes',b'[EnableIf=flag] import "a.mojom";',True,['a.mojom']),
 ('spacing',b'import\t/*x*/\r\n"a.mojom" /*x*/ ;',True,['a.mojom']),
 ('duplicates',b'import "a.mojom"; import "a.mojom";',True,['a.mojom','a.mojom']),
 ('late',b'struct X {}; import "a.mojom";',False,[]),
 ('unterminated_comment',b'/* import "x";',False,[]),
 ('unterminated_string',b'import "a.mojom',False,[]),
 ('missing_semicolon',b'import "a.mojom"',False,[]),
 ('dotdot',b'import "../a.mojom";',False,[]),
 ('escape_path',b'import "a\\x.mojom";',False,[]),
 ('bom',b'\xef\xbb\xbfimport "a.mojom";',False,[]),
 ('utf8_comment',b'// \xc4\x85\nimport "a.mojom";',True,['a.mojom']),
 ('invalid_utf8',b'// \xc0\x80\n',False,[]),
 ('mismatched_delimiter',b'struct X { ];',False,[]),
]

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    lines=['import SourceByteScanner','import ProofTiming','open RepoProof',
           'set_option maxHeartbeats 0','set_option maxRecDepth 100000']
    for name,data,accepted,events in CASES:
        block=f'(⟨{len(data)}, 0x{int.from_bytes(data,"little"):x}⟩ : SourceBytes.Block)'
        run=f'(SourceBytes.run SourceBytes.initial {block}.bytes)'
        lines += [f'theorem {name}_accepted : SourceBytes.finish {run}.1 = '+str(accepted).lower()+' := by',
                  '  timed_kernel_decide']
        if accepted:
            event_list='['+', '.join(bytes_literal(x.encode('utf-8')) for x in events)+']'
            lines += [f'theorem {name}_events : {run}.2 = {event_list} := by','  timed_kernel_decide']
        lines += [f'#print axioms {name}_accepted']
    with Path(args.output).open('xb') as target:
        target.write(('\n'.join(lines)+'\n').encode('utf-8'))
