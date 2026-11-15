from pathlib import Path
import tempfile
import unittest
from repo_proof.stage8_artifacts import inventory, verify


class ArtifactIdentityTests(unittest.TestCase):
    def test_checked_artifacts_must_remain_complete_and_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            proof = folder/'proof.olean'
            proof.write_bytes(b'checked')
            expected = inventory(folder)
            self.assertTrue(verify(folder, expected))
            proof.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                verify(folder, expected)
            proof.unlink()
            with self.assertRaises(ValueError):
                verify(folder, expected)
            proof.write_bytes(b'checked')
            (folder/'extra.lean').write_bytes(b'unchecked')
            with self.assertRaises(ValueError):
                verify(folder, expected)
