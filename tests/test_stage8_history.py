"""Preserve checkout bytes while honoring existing Git text normalization."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import check_stage8


class HistoricalReportTests(unittest.TestCase):
    def test_crlf_checkout_is_anchored_without_rewriting_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            def git(*arguments):
                return subprocess.check_output(['git', '-c', 'core.hooksPath=',
                    '-c', 'user.name=Stage8 fixture', '-c', 'user.email=fixture@example.invalid',
                    '-C', str(folder), *arguments], stderr=subprocess.PIPE).decode().strip()
            git('init', '--quiet')
            (folder/'verification').mkdir()
            (folder/'.gitattributes').write_bytes(b'*.json text eol=lf\n')
            path = folder/'verification/history.json'
            path.write_bytes(b'{\n  "historical": true\n}\n')
            git('add', '.')
            git('commit', '-qm', 'Synthetic historical checkout fixture')
            base = git('rev-parse', 'HEAD')
            raw = b'{\r\n  "historical": true\r\n}\r\n'
            path.write_bytes(raw)
            with patch.object(check_stage8, 'PROJECT', folder), patch.object(check_stage8, 'BASE', base):
                before = check_stage8.historical_report_inventory()
                self.assertEqual(before['verification/history.json']['raw_sha256'], sha256(raw).hexdigest())
                self.assertEqual(path.read_bytes(), raw)
                # Older commits can contain CRLF blobs despite later LF attrs.
                (folder/'.gitattributes').write_bytes(b'*.json -text\n')
                git('add', '.')
                git('commit', '-qm', 'Historical raw CRLF blob')
                (folder/'.gitattributes').write_bytes(b'*.json text eol=lf\n')
                git('add', '.gitattributes')
                git('commit', '-qm', 'Later LF attributes without rewriting history')
                with patch.object(check_stage8, 'BASE', git('rev-parse', 'HEAD')):
                    legacy = check_stage8.historical_report_inventory()
                    self.assertEqual(legacy['verification/history.json']['raw_sha256'], sha256(raw).hexdigest())
                path.write_bytes(raw.replace(b'true', b'false'))
                with self.assertRaisesRegex(ValueError, 'historical report differs'):
                    check_stage8.historical_report_inventory()
