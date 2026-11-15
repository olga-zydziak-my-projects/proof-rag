"""Resource supervisor: sum process-tree RSS/private memory, timeout and disk cap."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil


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


def terminate_tree(process):
    try:
        children = process.children(recursive=True)
    except psutil.NoSuchProcess:
        children = []
    for proc in [*reversed(children), process]:
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--artifact-root', help='explicit common root for outputs outside the log directory')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    folder = Path(a.run_dir)
    folder.mkdir(parents=True, exist_ok=False)
    artifact_root = Path(a.artifact_root).resolve() if a.artifact_root else folder.resolve()
    if not folder.resolve().is_relative_to(artifact_root):
        raise ValueError('log directory must be within artifact root')
    config = json.loads(Path(a.config).read_bytes())
    limits = config['limits']
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    result = {'status': 'IN_PROGRESS', 'command': command, 'limits': limits,
              'artifact_root': str(artifact_root),
              'memory_method': 'sampled simultaneous sum supervisor + child tree RSS/private; shared RSS may be counted twice',
              'initial_ram_available': psutil.virtual_memory().available,
              'initial_disk_free': psutil.disk_usage(str(folder.resolve())).free,
              'peak_tree_rss': 0, 'peak_tree_private': 0, 'peak_artifact_bytes': 0,
              'sample_interval_requested_seconds': limits['sample_seconds']}
    started = time.perf_counter()
    with (folder/'stdout.log').open('wb') as out, (folder/'stderr.log').open('wb') as err:
        child = subprocess.Popen(command, stdout=out, stderr=err, shell=False)
        process = psutil.Process(child.pid)
        status = None
        maximum_gap, previous = 0, time.perf_counter()
        try:
            while child.poll() is None:
                now = time.perf_counter()
                maximum_gap = max(maximum_gap, now-previous)
                previous = now
                own = psutil.Process().memory_info()
                rss, private = own.rss, getattr(own, 'private', own.rss)
                try:
                    processes = [process, *process.children(recursive=True)]
                except psutil.NoSuchProcess:
                    processes = []
                for proc in processes:
                    try:
                        mem = proc.memory_info()
                        rss += mem.rss
                        private += getattr(mem, 'private', mem.rss)
                    except psutil.NoSuchProcess:
                        continue
                size = directory_bytes(artifact_root)
                result['peak_tree_rss'] = max(result['peak_tree_rss'], rss)
                result['peak_tree_private'] = max(result['peak_tree_private'], private)
                result['peak_artifact_bytes'] = max(result['peak_artifact_bytes'], size)
                if now-started > limits['timeout_seconds']:
                    status = 'TIMEOUT'
                elif max(rss, private) > limits['tree_memory_bytes'] or size > limits['artifact_bytes']:
                    status = 'RESOURCE_LIMIT'
                if status:
                    break
                time.sleep(limits['sample_seconds'])
        except Exception as exc:
            status = 'MONITOR_FAILED'
            result['monitor_error'] = type(exc).__name__+': '+str(exc)
        finally:
            if child.poll() is None:
                terminate_tree(process)
        result.update(exit_code=child.wait(), elapsed_seconds=time.perf_counter()-started,
                      max_sample_gap_seconds=maximum_gap)
    result['status'] = status or ('PROCESS_PASS' if result['exit_code'] == 0 else 'FAILED')
    result['final_artifact_bytes'] = directory_bytes(artifact_root)
    (folder/'resource-report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'PROCESS_PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
