"""Source identity diagnostics; never releases a source-bound answer."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.stage5_preflight import diagnose


def main():
    project=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',required=True)
    p.add_argument('--config',default=str(project/'local/corpus.json'))
    a=p.parse_args()
    try:
        result,code=diagnose(project,Path(a.config),Path(a.run_dir))
    except (ValueError,OSError) as exc:
        print(json.dumps({'success':False,'status':'STAGE5_FAIL__RUN_INPUT','error':str(exc)}))
        return 2
    print(json.dumps({'status':result['status'],'success':False,'answer_released':False,
                      'diagnostic':str(Path(a.run_dir)/'diagnostic.json')}))
    return code


if __name__=='__main__': raise SystemExit(main())
