"""Preserve the identity of complete artifacts after their content checks."""
from pathlib import Path
from .stage8_store import digest


def inventory(folder):
    folder = Path(folder).resolve()
    result = {}
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            if not path.resolve().is_relative_to(folder):
                raise ValueError('artifact escapes its declared directory')
            result[path.relative_to(folder).as_posix()] = digest(path)
    if not result:
        raise ValueError('missing artifact directory contents')
    return result


def verify(folder, expected):
    if not expected or inventory(folder) != expected:
        raise ValueError('missing, added or modified checked artifact')
    return True
