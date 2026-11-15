"""Supervise controlled Windows tasks using a Job Object, timeout and disk cap.

Root creation atomically assigns the job and suspends execution. Descendants are terminated
and waited for on root exit. Kill-on-close also covers abrupt monitor death.
This controls pipeline process lifetimes, not arbitrary hostile programs.
"""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import time
import psutil


class BasicLimits(ctypes.Structure):
    _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64),
                ('flags', wintypes.DWORD), ('min_ws', ctypes.c_size_t),
                ('max_ws', ctypes.c_size_t), ('active_limit', wintypes.DWORD),
                ('affinity', ctypes.c_size_t), ('priority', wintypes.DWORD),
                ('scheduling', wintypes.DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [('basic', BasicLimits), ('io', ctypes.c_uint64 * 6),
                ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]


class Accounting(ctypes.Structure):
    _fields_ = [('times', ctypes.c_int64 * 4), ('faults', wintypes.DWORD),
                ('total', wintypes.DWORD), ('active', wintypes.DWORD),
                ('terminated', wintypes.DWORD)]


class StartupInfo(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('reserved', wintypes.LPWSTR),
                ('desktop', wintypes.LPWSTR), ('title', wintypes.LPWSTR),
                ('x', wintypes.DWORD), ('y', wintypes.DWORD),
                ('x_size', wintypes.DWORD), ('y_size', wintypes.DWORD),
                ('x_chars', wintypes.DWORD), ('y_chars', wintypes.DWORD),
                ('fill', wintypes.DWORD), ('flags', wintypes.DWORD),
                ('show', wintypes.WORD), ('reserved_size', wintypes.WORD),
                ('reserved_bytes', ctypes.c_void_p), ('stdin', wintypes.HANDLE),
                ('stdout', wintypes.HANDLE), ('stderr', wintypes.HANDLE)]


class StartupInfoEx(ctypes.Structure):
    _fields_ = [('startup', StartupInfo), ('attributes', ctypes.c_void_p)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [('process', wintypes.HANDLE), ('thread', wintypes.HANDLE),
                ('pid', wintypes.DWORD), ('tid', wintypes.DWORD)]


class WindowsJob:
    def __init__(self):
        if os.name != 'nt':
            raise RuntimeError('stage8 supervisor requires Windows Job Objects')
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            'SetInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
            'QueryInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
            'TerminateJobObject': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            'ResumeThread': ([wintypes.HANDLE], wintypes.DWORD),
            'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL),
            'InitializeProcThreadAttributeList': ([ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                                   ctypes.POINTER(ctypes.c_size_t)], wintypes.BOOL),
            'UpdateProcThreadAttribute': ([ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t,
                                          ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                          ctypes.c_void_p], wintypes.BOOL),
            'DeleteProcThreadAttributeList': ([ctypes.c_void_p], None),
            'CreateProcessW': ([wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
                                wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
                                ctypes.POINTER(StartupInfoEx), ctypes.POINTER(ProcessInfo)], wintypes.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, result
        self.handle = self.api.CreateJobObjectW(None, None)
        self.process = None
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            limits = ExtendedLimits()
            limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            self.check(self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        except BaseException:
            self.close()
            raise

    @staticmethod
    def check(ok):
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())

    def start(self, command, out, err):
        import _winapi
        import msvcrt
        with open(os.devnull, 'rb') as stdin:
            handles = [msvcrt.get_osfhandle(stream.fileno()) for stream in (stdin, out, err)]
            info = StartupInfoEx()
            info.startup.cb = ctypes.sizeof(info)
            info.startup.flags = subprocess.STARTF_USESTDHANDLES
            info.startup.stdin, info.startup.stdout, info.startup.stderr = handles
            size = ctypes.c_size_t()
            self.api.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(size))
            attributes = ctypes.create_string_buffer(size.value)
            self.check(self.api.InitializeProcThreadAttributeList(attributes, 2, 0, ctypes.byref(size)))
            info.attributes = ctypes.addressof(attributes)
            previous = [os.get_handle_inheritable(handle) for handle in handles]
            thread = None
            try:
                inherited = (wintypes.HANDLE * len(handles))(*handles)
                jobs = (wintypes.HANDLE * 1)(self.handle)
                self.check(self.api.UpdateProcThreadAttribute(attributes, 0, 0x20002,
                    inherited, ctypes.sizeof(inherited), None, None))  # HANDLE_LIST
                self.check(self.api.UpdateProcThreadAttribute(attributes, 0, 0x2000D,
                    jobs, ctypes.sizeof(jobs), None, None))  # JOB_LIST, Windows 10+
                for handle in handles:
                    os.set_handle_inheritable(handle, True)
                created = ProcessInfo()
                self.check(self.api.CreateProcessW(None,
                    ctypes.create_unicode_buffer(subprocess.list2cmdline(command)),
                    None, None, True, 0x80000 | 0x4 | subprocess.CREATE_NO_WINDOW,
                    None, None, ctypes.byref(info), ctypes.byref(created)))
                self.process, thread, self.pid = created.process, created.thread, created.pid
                if self.api.ResumeThread(thread) == 0xFFFFFFFF:
                    raise ctypes.WinError(ctypes.get_last_error())
            except BaseException:
                if self.process is not None:
                    # Retained creation handle identifies our suspended root
                    # if resuming it fails before the first user instruction.
                    _winapi.TerminateProcess(self.process, 2)
                    _winapi.WaitForSingleObject(self.process, _winapi.INFINITE)
                raise
            finally:
                if thread is not None:
                    _winapi.CloseHandle(thread)
                for handle, inheritable in zip(handles, previous):
                    os.set_handle_inheritable(handle, inheritable)
                self.api.DeleteProcThreadAttributeList(attributes)

    def poll(self):
        import _winapi
        if _winapi.WaitForSingleObject(self.process, 0) == _winapi.WAIT_OBJECT_0:
            return _winapi.GetExitCodeProcess(self.process)
        return None

    def accounting(self):
        data = Accounting()
        self.check(self.api.QueryInformationJobObject(self.handle, 1, ctypes.byref(data), ctypes.sizeof(data), None))
        return data

    def pids(self):
        capacity = 64
        while True:
            class PidList(ctypes.Structure):
                _fields_ = [('assigned', wintypes.DWORD), ('count', wintypes.DWORD),
                            ('ids', ctypes.c_size_t * capacity)]
            data = PidList()
            if self.api.QueryInformationJobObject(self.handle, 3, ctypes.byref(data), ctypes.sizeof(data), None):
                return list(data.ids[:data.count])
            if ctypes.get_last_error() != 234:  # ERROR_MORE_DATA
                raise ctypes.WinError(ctypes.get_last_error())
            capacity = max(capacity * 2, data.assigned)

    def drain(self):
        self.check(self.api.TerminateJobObject(self.handle, 2))
        deadline = time.monotonic() + 15
        while self.accounting().active:
            if time.monotonic() >= deadline:
                raise RuntimeError('job processes did not terminate within 15 seconds')
            time.sleep(0.01)
        if self.process is not None:
            import _winapi
            if _winapi.WaitForSingleObject(self.process, 15000) != _winapi.WAIT_OBJECT_0:
                raise RuntimeError('root process termination wait failed')

    def close(self):
        if self.process is not None:
            self.api.CloseHandle(self.process)
            self.process = None
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def directory_bytes(folder):
    """Temporary DuckDB files may disappear between enumeration and stat."""
    total = 0
    for path in Path(folder).rglob('*'):
        try:
            if path.is_file():
                total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total


def write_resource_report(path, artifact_root, result, artifact_limit):
    """Count the report itself, allowing its size fields and status to settle."""
    for _ in range(16):
        path.write_bytes(json.dumps(result, indent=2).encode('utf-8'))
        try:
            size = directory_bytes(artifact_root)
        except Exception as exc:
            if result['status'] == 'PROCESS_PASS':
                result['status'] = 'MONITOR_FAILED'
            result['final_artifact_error'] = type(exc).__name__ + ': ' + str(exc)
            path.write_bytes(json.dumps(result, indent=2).encode('utf-8'))
            return
        exceeded = size > artifact_limit
        status = 'RESOURCE_LIMIT' if exceeded and result['status'] == 'PROCESS_PASS' else result['status']
        peak = max(result['peak_artifact_bytes'], size)
        if (result.get('final_artifact_bytes') == size
                and result.get('final_artifact_limit_exceeded') == exceeded
                and result['peak_artifact_bytes'] == peak and result['status'] == status):
            return
        result.update(final_artifact_bytes=size, final_artifact_limit_exceeded=exceeded,
                      peak_artifact_bytes=peak, status=status)
    result['status'] = 'MONITOR_FAILED'
    result['final_artifact_error'] = 'artifact size did not stabilize after 16 report writes'
    path.write_bytes(json.dumps(result, indent=2).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--artifact-root', help='explicit common root for outputs outside the log directory')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    folder = Path(args.run_dir)
    folder.mkdir(parents=True, exist_ok=False)
    artifact_root = Path(args.artifact_root).resolve() if args.artifact_root else folder.resolve()
    if not folder.resolve().is_relative_to(artifact_root):
        raise ValueError('log directory must be within artifact root')
    limits = json.loads(Path(args.config).read_bytes())['limits']
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or any(limits[key] <= 0 for key in
                          ('sample_seconds', 'timeout_seconds', 'tree_memory_bytes', 'artifact_bytes')):
        raise ValueError('command and positive supervision limits are required')
    result = {'status': 'IN_PROGRESS', 'command': command, 'limits': limits,
              'artifact_root': str(artifact_root),
              'process_control': 'Windows Job Object; atomic creation JOB_LIST; suspended resume; kill-on-close; no breakaway',
              'descendant_exit_policy': 'terminate and wait for all remaining job members on root exit',
              'memory_method': 'sampled supervisor + Job Object members RSS/private; shared RSS may be counted twice',
              'initial_ram_available': psutil.virtual_memory().available,
              'initial_disk_free': psutil.disk_usage(str(folder.resolve())).free,
              'peak_tree_rss': 0, 'peak_tree_private': 0, 'peak_artifact_bytes': 0,
              'sample_interval_requested_seconds': limits['sample_seconds']}
    started = time.perf_counter()
    status, job, maximum_gap = None, None, 0
    task_started = False
    result['exit_code'] = None
    with (folder/'stdout.log').open('wb') as out, (folder/'stderr.log').open('wb') as err:
        try:
            job = WindowsJob()
            job.start(command, out, err)
            task_started = True
            previous = time.perf_counter()
            while True:
                now = time.perf_counter()
                maximum_gap = max(maximum_gap, now - previous)
                previous = now
                own = psutil.Process().memory_info()
                rss, private = own.rss, getattr(own, 'private', own.rss)
                for pid in job.pids():
                    try:
                        mem = psutil.Process(pid).memory_info()
                        rss += mem.rss
                        private += getattr(mem, 'private', mem.rss)
                    except psutil.NoSuchProcess:
                        continue
                size = directory_bytes(artifact_root)
                result['peak_tree_rss'] = max(result['peak_tree_rss'], rss)
                result['peak_tree_private'] = max(result['peak_tree_private'], private)
                result['peak_artifact_bytes'] = max(result['peak_artifact_bytes'], size)
                if now - started > limits['timeout_seconds']:
                    status = 'TIMEOUT'
                elif max(rss, private) > limits['tree_memory_bytes'] or size > limits['artifact_bytes']:
                    status = 'RESOURCE_LIMIT'
                result['exit_code'] = job.poll()
                if status or result['exit_code'] is not None:
                    break
                time.sleep(limits['sample_seconds'])
        except KeyboardInterrupt:
            status = 'INTERRUPTED'
        except Exception as exc:
            status = 'MONITOR_FAILED' if task_started else 'CONTROL_FAILED'
            result['monitor_error'] = type(exc).__name__ + ': ' + str(exc)
        finally:
            if job is not None:
                try:
                    result['members_before_cleanup'] = job.accounting().active
                    job.drain()
                    result['remaining_job_processes'] = job.accounting().active
                    if job.process is not None:
                        result['exit_code'] = job.poll()
                except Exception as exc:
                    status = 'CLEANUP_FAILED'
                    result['cleanup_error'] = type(exc).__name__ + ': ' + str(exc)
                finally:
                    job.close()
    result.update(status=status or ('PROCESS_PASS' if result['exit_code'] == 0 else 'FAILED'),
                  elapsed_seconds=time.perf_counter() - started,
                  max_sample_gap_seconds=maximum_gap)
    write_resource_report(folder/'resource-report.json', artifact_root, result, limits['artifact_bytes'])
    print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'PROCESS_PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
