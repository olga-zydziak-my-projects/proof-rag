"""Fresh measured compilation of independent concrete source proof modules."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
from stage5_support import run_process

p = argparse.ArgumentParser()
p.add_argument('--run-dir', required=True)
p.add_argument('--lean', required=True)
p.add_argument('--workers', type=int, default=2)
p.add_argument('--first-group', type=int, default=0)
a = p.parse_args()
folder = Path(a.run_dir).resolve()
env = dict(os.environ, LEAN_PATH=str(folder/'lean')+';'+str(Path('formal').resolve()))
receipt_dir = folder/'group-receipts'
receipt_dir.mkdir(exist_ok=False)
modules = [x for x in sorted((folder/'lean').glob('SourceGroup*.lean'))
           if int(x.stem.removeprefix('SourceGroup')) >= a.first_group]

def compile_module(path):
    result = run_process(path.stem, [a.lean, '-o', str(path.with_suffix('.olean')), str(path)],
                         env, folder, timeout=7200)
    with (receipt_dir/(path.stem+'.json')).open('x', encoding='utf-8') as target:
        json.dump(result, target, ensure_ascii=False, indent=2)
    return result

with ThreadPoolExecutor(max_workers=a.workers) as executor:
    futures = [executor.submit(compile_module, path) for path in modules]
    for future in as_completed(futures):
        result = future.result()
        print(json.dumps({k:result[k] for k in ('name','passed','seconds','exit_code')}), flush=True)
        if not result['passed']:
            print(result['stdout'][-4000:], result['stderr'][-2000:], flush=True)
            for pending in futures:
                pending.cancel()
            raise SystemExit(1)
