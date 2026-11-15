"""Real Windows process lifecycle regressions for the stage 8 supervisor."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import psutil

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / 'scripts' / 'stage8_supervise.py'
WORKER = '''import json, os, pathlib, subprocess, sys, time
import psutil
folder = pathlib.Path(sys.argv[1])
role, mode = sys.argv[2:4]
record = folder / (role + '.pending')
record.write_text(json.dumps([os.getpid(), psutil.Process().create_time()]))
record.replace(folder / (role + '.json'))
if role != 'grandchild':
    next_role = 'child' if role == 'root' else 'grandchild'
    subprocess.Popen([sys.executable, __file__, str(folder), next_role, mode], close_fds=True)
    while not (folder / 'grandchild.json').exists(): time.sleep(.005)
if role == 'root':
    if mode == 'fast': sys.exit(0)
    if mode == 'failure': sys.exit(7)
time.sleep(60)
'''


@unittest.skipUnless(os.name == 'nt', 'Windows Job Object integration')
class Stage8SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.worker = self.folder / 'worker.py'
        self.worker.write_text(WORKER, encoding='utf-8')
        self.processes = []

    def tearDown(self):
        # Test cleanup is independent of the mechanism under test and verifies
        # process creation identity before touching any retained fixture PID.
        for child in self.processes:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=10)
        for path in self.folder.glob('*.json'):
            if path.stem not in ('root', 'child', 'grandchild'):
                continue
            pid, created = json.loads(path.read_text())
            try:
                process = psutil.Process(pid)
                if process.create_time() == created:
                    process.kill()
                    process.wait(timeout=10)
            except psutil.NoSuchProcess:
                pass
        self.temp.cleanup()

    def start(self, mode='fast', *, timeout=5, memory=2**31, disk=2**24,
              sample=.02, wrapper=None, command=None):
        config = self.folder / 'config.json'
        config.write_text(json.dumps({'limits': {
            'timeout_seconds': timeout, 'tree_memory_bytes': memory,
            'artifact_bytes': disk, 'sample_seconds': sample}}))
        runner = SUPERVISOR
        if wrapper:
            runner = self.folder / 'runner.py'
            runner.write_text('import sys\nsys.path.insert(0, ' + repr(str(SUPERVISOR.parent)) + ')\n'
                              'import stage8_supervise as s\n' + wrapper + '\nraise SystemExit(s.main())\n')
        args = [sys.executable, str(runner), '--config', str(config),
                '--run-dir', str(self.folder / 'run'), '--artifact-root', str(self.folder), '--']
        args += command or [sys.executable, str(self.worker), str(self.folder), 'root', mode]
        child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(child)
        return child

    def finish(self, child):
        stdout, stderr = child.communicate(timeout=20)
        report_path = self.folder / 'run' / 'resource-report.json'
        self.assertTrue(report_path.exists(), stderr.decode(errors='replace'))
        report = json.loads(report_path.read_bytes())
        self.assertEqual(child.returncode, 0 if report['status'] == 'PROCESS_PASS' else 2,
                         stdout.decode(errors='replace'))
        self.assertEqual(report['remaining_job_processes'], 0)
        self.assert_gone()
        return report

    def wait_ready(self):
        deadline = time.monotonic() + 10
        while not (self.folder / 'grandchild.json').exists():
            self.assertLess(time.monotonic(), deadline, 'fixture did not create grandchild')
            time.sleep(.01)

    def assert_gone(self):
        for role in ('root', 'child', 'grandchild'):
            path = self.folder / (role + '.json')
            if path.exists():
                pid, created = json.loads(path.read_text())
                try:
                    self.assertNotEqual(psutil.Process(pid).create_time(), created, role + ' survived')
                except psutil.NoSuchProcess:
                    pass

    def test_fast_root_exit_drains_child_and_grandchild(self):
        report = self.finish(self.start(sample=.5))
        self.assertEqual(report['status'], 'PROCESS_PASS')
        self.assertGreaterEqual(report['members_before_cleanup'], 2)
        self.assertTrue((self.folder / 'grandchild.json').exists())

    def test_failed_root_drains_descendants(self):
        report = self.finish(self.start('failure'))
        self.assertEqual((report['status'], report['exit_code']), ('FAILED', 7))

    def test_timeout_drains_three_generations(self):
        report = self.finish(self.start('wait', timeout=1))
        self.assertEqual(report['status'], 'TIMEOUT')
        self.assertTrue((self.folder / 'grandchild.json').exists())

    def test_memory_limit_drains_job(self):
        report = self.finish(self.start('wait', memory=1))
        self.assertEqual(report['status'], 'RESOURCE_LIMIT')

    def test_assignment_failure_blocks_execution_and_acceptance(self):
        wrapper = '''original = s.WindowsJob.__init__
def failed_assignment(self):
    original(self)
    def fail(*args):
        s.ctypes.set_last_error(5)
        return 0
    self.api.UpdateProcThreadAttribute = fail
s.WindowsJob.__init__ = failed_assignment'''
        report = self.finish(self.start(wrapper=wrapper))
        self.assertEqual(report['status'], 'CONTROL_FAILED')
        self.assertFalse((self.folder / 'root.json').exists())

    def test_successful_short_task(self):
        report = self.finish(self.start(command=[sys.executable, '-c', 'print("complete")']))
        self.assertEqual((report['status'], report['exit_code']), ('PROCESS_PASS', 0))

    def test_short_task_final_artifact_limit(self):
        code = 'from pathlib import Path; Path(' + repr(str(self.folder / 'large.bin')) + ').write_bytes(b"x"*100000)'
        report = self.finish(self.start(disk=50000, sample=.5, command=[sys.executable, '-c', code]))
        self.assertEqual(report['status'], 'RESOURCE_LIMIT')
        self.assertGreaterEqual(report['final_artifact_bytes'], 100000)

    def test_report_itself_can_exceed_artifact_limit(self):
        limit = self.worker.stat().st_size + 512
        report = self.finish(self.start(disk=limit, command=[sys.executable, '-c', 'pass']))
        report_path = self.folder / 'run' / 'resource-report.json'
        total = sum(path.stat().st_size for path in self.folder.rglob('*') if path.is_file())
        self.assertLess(total - report_path.stat().st_size, limit)
        self.assertEqual(report['status'], 'RESOURCE_LIMIT')
        self.assertTrue(report['final_artifact_limit_exceeded'])
        self.assertEqual(report['final_artifact_bytes'], total)
        self.assertGreaterEqual(report['peak_artifact_bytes'], total)

    def test_monitor_exception_drains_three_generations(self):
        wrapper = '''original = s.directory_bytes
def broken(folder):
    if (folder / 'grandchild.json').exists(): raise RuntimeError('injected monitor failure')
    return original(folder)
s.directory_bytes = broken'''
        report = self.finish(self.start('wait', wrapper=wrapper))
        self.assertEqual(report['status'], 'MONITOR_FAILED')
        self.assertTrue((self.folder / 'grandchild.json').exists())

    def test_interrupt_drains_three_generations(self):
        wrapper = '''original = s.directory_bytes
def interrupted(folder):
    if (folder / 'grandchild.json').exists(): raise KeyboardInterrupt()
    return original(folder)
s.directory_bytes = interrupted'''
        # Restore the artifact function after the single injected interrupt.
        wrapper = wrapper.replace("raise KeyboardInterrupt()", "s.directory_bytes = original; raise KeyboardInterrupt()")
        report = self.finish(self.start('wait', wrapper=wrapper))
        self.assertEqual(report['status'], 'INTERRUPTED')

    def test_abrupt_supervisor_death_closes_job_and_kills_descendants(self):
        child = self.start('wait')
        self.wait_ready()
        child.kill()
        child.communicate(timeout=10)
        deadline = time.monotonic() + 10
        while True:
            try:
                self.assert_gone()
                break
            except AssertionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.02)

    def test_supervisor_death_before_resume_kills_suspended_root(self):
        wrapper = '''original = s.WindowsJob.__init__
def stalled_resume(self):
    original(self)
    def stall(thread):
        record = s.Path('RECORD_PATH')
        record.write_text(s.json.dumps([self.pid, s.psutil.Process(self.pid).create_time()]))
        s.time.sleep(60)
    self.api.ResumeThread = stall
s.WindowsJob.__init__ = stalled_resume'''.replace('RECORD_PATH', (self.folder / 'root.json').as_posix())
        child = self.start('wait', wrapper=wrapper)
        deadline = time.monotonic() + 10
        while not (self.folder / 'root.json').exists():
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.01)
        # The entire record must be flushed before the monitor is interrupted.
        while True:
            try:
                json.loads((self.folder / 'root.json').read_text())
                break
            except json.JSONDecodeError:
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.01)
        child.kill()
        child.communicate(timeout=10)
        while True:
            try:
                self.assert_gone()
                break
            except AssertionError:
                self.assertLess(time.monotonic(), deadline)
                time.sleep(.02)
        self.assertFalse((self.folder / 'child.json').exists())


if __name__ == '__main__':
    unittest.main()
