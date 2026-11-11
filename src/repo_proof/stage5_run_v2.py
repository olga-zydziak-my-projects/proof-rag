"""Operational run binding. Hashes protect IO identity, not source semantics."""
import hashlib
from pathlib import Path
from .extraction import read_json
from .stage5_v2 import canonical


def input_files(folder):
    folder=Path(folder)
    return sorted([p for p in folder.glob('*.json') if p.name not in
                   ('run-seal.json','operational-receipt.json','result.json','answer.json','answer.pending.json')]
                  +list((folder/'lean').glob('*.lean')))


def seal(folder,nonce):
    folder=Path(folder)
    expected={'schema':'stage5-run-seal-v2','nonce':nonce,
              'files':{p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in input_files(folder)}}
    with (folder/'run-seal.json').open('xb') as target:
        target.write(canonical(expected))
    return expected


def check_seal(folder,expected,nonce):
    folder=Path(folder)
    if nonce!=expected['nonce'] or read_json(folder/'run-seal.json')!=expected:
        raise ValueError('cross-run seal or nonce mismatch')
    paths={p.relative_to(folder).as_posix() for p in input_files(folder)}
    if paths!=set(expected['files']):
        raise ValueError('run input inventory changed')
    for rel,digest in expected['files'].items():
        if hashlib.sha256((folder/rel).read_bytes()).hexdigest()!=digest:
            raise ValueError('persisted input changed before use: '+rel)
    return True
