"""Public persisted-input preflight; acceptance here is not a proof or answer."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.stage5_run_v2 import check_seal
from repo_proof.stage5_v2 import capture
from repo_proof.extraction import read_json
from repo_proof.stage5_answer_v2 import check_answer
from stage5_v2_audit_bytes import audit


def validate_inputs(folder,captured,expected,nonce):
    folder=Path(folder)
    check_seal(folder,expected,nonce)
    if not (folder/'lean/ChromiumSource.lean').exists(): raise ValueError('master source missing')
    result=audit(folder,captured)
    check_answer(read_json(folder/'expected-answer.json'),captured)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',required=True)
    p.add_argument('--trusted-seal',required=True,help='independent caller-retained seal, not an attacker-selected expected identity')
    p.add_argument('--nonce',required=True)
    a=p.parse_args()
    try:
        expected=read_json(a.trusted_seal)
        check_seal(a.run_dir,expected,a.nonce)
        validate_inputs(a.run_dir,capture(Path.cwd()),expected,a.nonce)
    except (ValueError,OSError) as error:
        print('INPUT_REJECTED: '+str(error),file=sys.stderr)
        return 2
    print('INPUT_BOUNDARY_PASS (no proof acceptance or answer release)')
    return 0


if __name__=='__main__': raise SystemExit(main())
