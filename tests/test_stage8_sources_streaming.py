"""Regression checks for batched, content-anchored source capture."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from hashlib import sha256
from copy import deepcopy

from repo_proof.source_bytes_v2 import certificate
from repo_proof.stage8_fixture import create
from repo_proof.stage8_sources import capture, import_events
from repo_proof.stage5_v2 import canonical


class StreamingSourceTests(unittest.TestCase):
    def test_event_projection_matches_existing_byte_specification(self):
        samples = [b'module x;', b'import "a/a.mojom"; import "a/a.mojom";',
                   b'// import "ignored";\n import "valid.mojom";',
                   'module x; /*ąć*/ import "ż.mojom";'.encode()]
        for data in samples:
            self.assertEqual(list(import_events(data)), certificate(data)[1])
        for data in (b'import "unfinished', b'/* unfinished', b'\xff'):
            with self.assertRaises(ValueError):
                list(import_events(data))

    def test_one_batch_reader_per_repository_and_linear_metadata(self):
        import repo_proof.stage8_sources as sources
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            _, anchor, locations = create(folder)
            with patch.object(sources, 'blob_reader', wraps=sources.blob_reader) as readers:
                files, edges, facts = capture(folder/'manifest.json', anchor, locations)
            self.assertEqual(readers.call_count, 3)
            self.assertEqual((len(files), len(edges)), (4, 3))
            self.assertGreater(facts['metadata'][0]['source_bytes'], 0)

    def test_reanchored_source_hash_substitution_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            manifest, _, locations = create(folder)
            bad = deepcopy(manifest)
            bad['repositories'][0]['files'][0]['sha256'] = '0'*64
            raw = canonical(bad)
            (folder/'bad.json').write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'source bytes changed'):
                capture(folder/'bad.json', sha256(raw).hexdigest(), locations)

    def test_existing_partial_scope_prefixes_keep_their_meaning(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            manifest, _, locations = create(folder)
            for prefix, expected in [('local', 4), ('local/a', 3)]:
                selected = deepcopy(manifest)
                repo = selected['repositories'][0]
                repo['prefixes'] = [prefix]
                repo['files'] = [f for f in repo['files'] if f['path'].startswith(prefix)]
                raw = canonical(selected)
                (folder/'selected.json').write_bytes(raw)
                files, _, _ = capture(folder/'selected.json', sha256(raw).hexdigest(), locations)
                self.assertEqual(len(files), expected)


if __name__ == '__main__':
    unittest.main()
