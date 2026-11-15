"""Ask one Polish or English question using Claude and the Stage 6 proof CLI."""
import argparse
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage7 import ClaudeInterpreter, Stage7Error, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--question', required=True)
    parser.add_argument('--model', default='claude-haiku-5-5')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--cache-dir', required=True)
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--lean', required=True)
    args = parser.parse_args()
    try:
        result = run(args.question, ClaudeInterpreter(args.model, args.effort), PROJECT,
                     args.cache_dir, args.run_dir, args.lean)
    except (Stage7Error, ImportError) as exc:
        print('STAGE7_QUERY_FAILED: ' + str(exc), file=sys.stderr)
        return 2
    if result['verified']:
        print((Path(args.run_dir)/'answer.txt').read_text(encoding='utf-8'))
    else:
        print(json.dumps(result, ensure_ascii=True))
    return 0 if result['verified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
