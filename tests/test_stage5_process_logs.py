import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from stage5_support import run_process


@unittest.skipUnless(os.name=='nt','Windows counters')
class Stage5ProcessLogsTests(unittest.TestCase):
    def test_logs_are_exclusive_and_existing_bytes_preserved(self):
        with tempfile.TemporaryDirectory(dir='local') as directory:
            first=run_process('probe',[sys.executable,'-c','print("ok")'],dict(os.environ),directory)
            self.assertTrue(first['passed'])
            out=Path(first['log_paths'][0]); saved=out.read_bytes()
            with self.assertRaises(FileExistsError):
                run_process('probe',[sys.executable,'-c','print("changed")'],dict(os.environ),directory)
            self.assertEqual(out.read_bytes(),saved)

    def test_two_runs_keep_separate_log_paths(self):
        with tempfile.TemporaryDirectory(dir='local') as directory:
            a=run_process('probe',[sys.executable,'-c','print("a")'],dict(os.environ),Path(directory)/'a')
            b=run_process('probe',[sys.executable,'-c','print("b")'],dict(os.environ),Path(directory)/'b')
            self.assertNotEqual(a['log_paths'],b['log_paths'])
            self.assertEqual(a['stdout'].strip(),'a'); self.assertEqual(b['stdout'].strip(),'b')
