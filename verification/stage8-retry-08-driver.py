"""Apply a recorded CPU profile to an owned regression Job Object."""
import ctypes
from ctypes import wintypes
from hashlib import sha256
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT/'scripts'), str(PROJECT/'local/stage8-deps')]
import stage8_supervise

arguments = sys.argv[1:]
header = arguments[:arguments.index('--')]
config_path = Path(header[header.index('--config')+1])
folder = Path(header[header.index('--run-dir')+1])
limits = json.loads(config_path.read_bytes())['limits']
base_job = stage8_supervise.WindowsJob


class ProfiledJob(base_job):
    def __init__(self):
        super().__init__()
        try:
            configured = stage8_supervise.ExtendedLimits()
            configured.basic.flags = 0x2000 | 0x10 | 0x20
            configured.basic.affinity = limits['job_affinity_mask']
            configured.basic.priority = limits['job_priority_class']
            self.check(self.api.SetInformationJobObject(self.handle, 9,
                ctypes.byref(configured), ctypes.sizeof(configured)))
            observed = stage8_supervise.ExtendedLimits()
            self.check(self.api.QueryInformationJobObject(self.handle, 9,
                ctypes.byref(observed), ctypes.sizeof(observed), None))
            if (observed.basic.flags & configured.basic.flags != configured.basic.flags
                    or observed.basic.flags & (0x800 | 0x1000)
                    or observed.basic.affinity != configured.basic.affinity
                    or observed.basic.priority != configured.basic.priority):
                raise RuntimeError('Job Object CPU profile was not established')
            self.profile = {'job_flags': observed.basic.flags,
                'job_affinity_mask': observed.basic.affinity,
                'job_priority_class': observed.basic.priority,
                'configured_before_root_creation': True,
                'driver_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
            self.api.GetPriorityClass.argtypes = [wintypes.HANDLE]
            self.api.GetPriorityClass.restype = wintypes.DWORD
            self.api.GetProcessAffinityMask.argtypes = [wintypes.HANDLE,
                ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
            self.api.GetProcessAffinityMask.restype = wintypes.BOOL
        except BaseException:
            self.close()
            raise

    def start(self, command, out, err):
        super().start(command, out, err)
        affinity, system = ctypes.c_size_t(), ctypes.c_size_t()
        self.check(self.api.GetProcessAffinityMask(self.process,
            ctypes.byref(affinity), ctypes.byref(system)))
        priority = self.api.GetPriorityClass(self.process)
        if affinity.value != limits['job_affinity_mask'] or priority != limits['job_priority_class']:
            raise RuntimeError('effective root CPU profile differs from experiment')
        self.profile.update(effective_root_affinity_mask=affinity.value,
                            effective_root_priority_class=priority)
        (folder/'job-profile.json').write_bytes(json.dumps(self.profile,
            sort_keys=True, separators=(',', ':')).encode('utf-8'))


stage8_supervise.WindowsJob = ProfiledJob
raise SystemExit(stage8_supervise.main())
