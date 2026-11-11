"""Generate the final source-to-answer instance; compilation remains mandatory."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.stage5_v2 import capture, tree, range_proof
from repo_proof.source_bytes_v2 import bytes_literal

def export_master(captured, folder):
    """Export from the caller-owned capture; do not reread any corpus input."""
    folder=Path(folder)
    c=captured
    n=len(c.blobs)
    ids={b.path:i for i,b in enumerate(c.blobs)}
    selected=[ids[row['node']] for row in c.certificate['candidates']]
    if n!=1864 or len(selected)!=477 or len(set(selected))!=477:
        raise ValueError('master exporter requires the unchanged Chromium regression instance')
    fin=lambda i:f'⟨{i}, by decide +kernel⟩'
    lines=['import ChromiumFast','import AnswerBinding','import ProofTiming']
    lines += [f'import SourceGroup{i:03}' for i in range((n+63)//64)]
    lines += ['open RepoProof RepoProof.SourceBinding RepoProof.AnswerBinding',
              'set_option maxHeartbeats 0','set_option maxRecDepth 100000',
              'namespace ChromiumSource',f'def files (v : Fin {n}) : File {n} :=']
    lines += tree(0,n,lambda i:f'SourceGroup{i//64:03}.f{i}','  ',lambda m:f'v.val < {m}')
    lines += ['theorem files_checked : allVertices (fun v => fileOK SourceNames.names (files v)) = true := by',
              '  apply allVertices_of_range']
    lines += range_proof(0,n,lambda i:
        f'exact index_from (fun v => fileOK SourceNames.names (files v)) {fin(i)} SourceGroup{i//64:03}.f{i}_ok')
    lines += ['theorem graph_equal : (graphOfFiles files).edges = (eraseGraph ChromiumFast.graph).edges := by',
              '  timed_kernel_decide',
              'theorem source_bound : sourceBinding SourceNames.names SourceNames.inverse files ChromiumFast.graph = true :=',
              '  sourceBinding_of_parts _ _ _ _ SourceNames.mapping_checked files_checked graph_equal',
              f'def resultIDs : List (Fin {n}) := ['+', '.join(fin(i) for i in selected)+']',
              'def payloadPaths : List Path := ['+', '.join(bytes_literal(c.blobs[i].path.encode('utf-8')) for i in selected)+']',
              'theorem answer_checked : answerOK SourceNames.names ChromiumFast.certificate resultIDs payloadPaths = true := by',
              '  apply answerOK_of_parts', '  · apply allVertices_of_range']
    # Short ranges avoid one large kernel reduction over the certificate and mapping.
    def coverage(start,count,indent):
        if count<=16: return [indent+'timed_kernel_decide']
        k=count//2
        return [indent+f"apply all_range'_split {start} {k} {count-k}",indent+'·']+coverage(start,k,indent+'  ')+[indent+'·']+coverage(start+k,count-k,indent+'  ')
    lines += coverage(0,n,'    ')
    lines += ['  · timed_kernel_decide','  · timed_kernel_decide',
              'theorem paths_unique : payloadPaths.Nodup :=',
              '  answer_nodup _ _ SourceNames.mapping_checked _ _ _ answer_checked',
              'theorem source_to_answer (p : Path) :',
              '    p ∈ payloadPaths ↔ ∃ v, SourceNames.names v = p ∧',
              '      Reach (ReverseEdge (Import SourceNames.names files)) ChromiumFast.root v :=',
              '  RepoProof.AnswerBinding.source_to_answer _ _ _ _ _ _ _ _ source_bound ChromiumFast.accepted answer_checked p',
              'end ChromiumSource',
              '#print axioms ChromiumSource.source_bound',
              '#print axioms ChromiumSource.paths_unique',
              '#print axioms ChromiumSource.source_to_answer']
    with (folder/'lean/ChromiumSource.lean').open('xb') as target:
        target.write(('\n'.join(lines)+'\n').encode('utf-8'))
    return folder/'lean/ChromiumSource.lean'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-dir', required=True)
    a=p.parse_args()
    export_master(capture(Path.cwd()), Path(a.run_dir))
    print('Generated final instance; no acceptance claimed before successful kernel compilation.')


if __name__=='__main__':
    main()
