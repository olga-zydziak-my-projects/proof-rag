"""Process measurement and strict Lean audit helpers (Windows, no dependencies)."""
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import re
import subprocess
import time

STANDARD_AXIOMS={'propext','Classical.choice','Quot.sound'}


class MemoryCounters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
        (name,ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize',
        'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
        'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]


def run_process(name,command,env,timeout=1200):
    """Wall clock from just before Popen to observed exit; native OS high waters.

    GetProcessMemoryInfo queried between requested 20ms waits and once after exit
    while the handle remains open. OS scheduling can lengthen wait intervals.
    Record whether that final OS query succeeded. No child process
    memory is included. PeakPagefileUsage denotes process commit, not disk IO.
    """
    if os.name!='nt':
        raise RuntimeError('this measurement implementation requires Windows')
    folder=Path('local/stage4'); folder.mkdir(parents=True,exist_ok=True)
    native=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
    native.argtypes=[wintypes.HANDLE,ctypes.POINTER(MemoryCounters),wintypes.DWORD]
    native.restype=wintypes.BOOL
    peaks={'peak_working_set_bytes':0,'peak_process_commit_bytes':0}
    samples=0
    def sample(process):
        nonlocal samples
        c=MemoryCounters(); c.cb=ctypes.sizeof(c)
        if not native(wintypes.HANDLE(int(process._handle)),ctypes.byref(c),c.cb):
            return False
        samples+=1
        peaks['peak_working_set_bytes']=max(peaks['peak_working_set_bytes'],c.PeakWorkingSetSize)
        peaks['peak_process_commit_bytes']=max(peaks['peak_process_commit_bytes'],c.PeakPagefileUsage)
        return True
    out=folder/(name+'.stdout'); err=folder/(name+'.stderr')
    start=time.perf_counter()
    with out.open('wb') as stdout,err.open('wb') as stderr:
        process=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr)
        expired=False
        while True:
            sample(process)
            try:
                code=process.wait(timeout=.02)
                break
            except subprocess.TimeoutExpired:
                if time.perf_counter()-start>timeout:
                    expired=True; process.kill(); code=process.wait(); break
        elapsed=time.perf_counter()-start
        final_query=sample(process)
    return dict(name=name,command=command,passed=code==0 and not expired,
                exit_code=code,timed_out=expired,seconds=elapsed,
                stdout=out.read_text(encoding='utf-8',errors='replace'),
                stderr=err.read_text(encoding='utf-8',errors='replace'),
                memory={**peaks,'successful_queries':samples,'post_exit_query_succeeded':final_query,
                        'scope':'Windows GetProcessMemoryInfo native high-water counters for this process only; requested 20ms wait intervals (OS scheduling may lengthen them) plus post-exit query. PeakWorkingSetSize resident bytes; PeakPagefileUsage process commit bytes. Successful post-exit query covers the complete process lifetime.'})


def audit(output,names,allowed=STANDARD_AXIOMS):
    result={}
    for name in names:
        if f"'{name}' does not depend on any axioms" in output:
            used=[]
        else:
            match=re.search(re.escape(f"'{name}' depends on axioms: [")+r'([^\]]*)\]',output)
            if not match: raise ValueError('missing audit: '+name)
            used=[s.strip() for s in match.group(1).split(',') if s.strip()]
        if not set(used)<=allowed: raise ValueError('unexpected axioms: '+name+str(used))
        result[name]=used
    return result


def file_info(path):
    p=Path(path)
    return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
