"""Temporary disk-backed ordered facts with bounded row-batch iteration."""
from collections.abc import Sequence
import json
import tempfile


class FactRows(Sequence):
    def __init__(self, folder=None):
        self.stream = tempfile.TemporaryFile(mode='w+b', dir=folder)
        self.offsets = []

    def append(self, row):
        self.stream.seek(0, 2)
        self.offsets.append(self.stream.tell())
        self.stream.write(json.dumps(row, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')+b'\n')

    def __len__(self):
        return len(self.offsets)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]
        self.stream.seek(self.offsets[index])
        return json.loads(self.stream.readline())

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False
        return len(self) == len(other) and all(a == b for a, b in zip(self, other))

    def close(self):
        self.stream.close()

    def __del__(self):
        self.close()
