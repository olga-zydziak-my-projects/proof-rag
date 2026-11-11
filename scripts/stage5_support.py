"""Stage 5 process measurements with exclusive log files in each new run."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import time

from stage4_support import MemoryCounters


def run_process(name,command,env,run_dir,timeout=1200):
    if os.name!='nt': raise RuntimeError('Windows process counters required')
    if not name or Path(name).name!=name or name in ('.','..'):
        raise ValueError('invalid process log name')
    folder=Path(run_dir)/'process-logs'; folder.mkdir(parents=True,exist_ok=True)
    out=folder/(name+'.stdout'); err=folder/(name+'.stderr')
    native=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
    native.argtypes=[wintypes.HANDLE,ctypes.POINTER(MemoryCounters),wintypes.DWORD]
    native.restype=wintypes.BOOL
    peaks={'peak_working_set_bytes':0,'peak_process_commit_bytes':0}; samples=0
    def sample(p):
        nonlocal samples
        c=MemoryCounters(); c.cb=ctypes.sizeof(c)
        if not native(wintypes.HANDLE(int(p._handle)),ctypes.byref(c),c.cb): return False
        samples+=1
        peaks['peak_working_set_bytes']=max(peaks['peak_working_set_bytes'],c.PeakWorkingSetSize)
        peaks['peak_process_commit_bytes']=max(peaks['peak_process_commit_bytes'],c.PeakPagefileUsage)
        return True
    start=time.perf_counter()
    with out.open('xb') as stdout,err.open('xb') as stderr:
        p=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr)
        expired=False
        while True:
            sample(p)
            try:
                code=p.wait(timeout=.02); break
            except subprocess.TimeoutExpired:
                if time.perf_counter()-start>timeout:
                    expired=True; p.kill(); code=p.wait(); break
        elapsed=time.perf_counter()-start
        final=sample(p)
    return {'name':name,'command':command,'passed':code==0 and not expired,
            'exit_code':code,'timed_out':expired,'seconds':elapsed,
            'stdout':out.read_text(encoding='utf-8',errors='replace'),
            'stderr':err.read_text(encoding='utf-8',errors='replace'),
            'log_paths':[str(out),str(err)],
            'memory':{**peaks,'successful_queries':samples,'post_exit_query_succeeded':final,
                'scope':'Windows native PeakWorkingSetSize (resident) and PeakPagefileUsage (process commit), this process only. Requested20ms waits; scheduling can lengthen them. Successful post-exit query covers lifetime. Wall clock includes opening exclusive logs, Popen, execution and wait; log decoding excluded.'}}
