"""Five serial offline checks with per-command and whole-run limits."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import time
from resource_usage import usage

ROOT = Path(__file__).resolve().parents[1]


def completed_test_count(stderr):
    """Use the completed unittest footer; test output may interleave with progress."""
    counts = re.findall(r'^Ran (\d+) tests? in ', stderr, re.M)
    if len(counts) != 1 or not re.search(r'^OK$', stderr, re.M):
        raise ValueError('Expected one completed unittest summary with no skipped tests.')
    return int(counts[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    results = args.out.resolve()
    out = results / 'reproduction'
    out.mkdir(parents=True, exist_ok=True)
    python = [sys.executable, '-B']
    commands = [
        ('corpus', python + ['scripts/corpus_audit.py', '--out', str(results)]),
        ('ledger', python + ['scripts/audit.py', '--out', str(results)]),
        ('oracle', python + ['scripts/oracle_check.py', '--out', str(results)]),
        ('tests', python + ['-m', 'unittest', 'discover', '-s', 'tests', '-v']),
        ('tables', python + ['scripts/render_tables.py', '--results', str(results)]),
    ]
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1')
    records = []
    overall = time.perf_counter()
    for name, cmd in commands:
        before = usage(children=True)
        start = time.perf_counter()
        limit = min(45, max(0, 240 - (start - overall)))
        code, timed_out, launch_error = None, False, None
        with (out / (name + '.stdout.txt')).open('w', encoding='utf-8') as so, \
             (out / (name + '.stderr.txt')).open('w', encoding='utf-8') as se:
            try:
                if limit <= 0:
                    raise subprocess.TimeoutExpired(cmd, limit)
                code = subprocess.run(cmd, cwd=ROOT, env=env, stdout=so, stderr=se,
                                      timeout=limit, check=False).returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                se.write(f'Command exceeded {limit:.3f} seconds.\n')
            except OSError as exc:
                launch_error = str(exc)
                se.write(launch_error + '\n')
        after = usage(children=True)
        cpu = (after['cpu_seconds'] - before['cpu_seconds']
               if after['cpu_seconds'] is not None and before['cpu_seconds'] is not None else None)
        records.append(dict(name=name, command=['python'] + cmd[1:], cwd='repository root',
                            timeout_seconds=limit, timed_out=timed_out, exit_code=code,
                            launch_error=launch_error, wall_seconds=time.perf_counter()-start,
                            child_cpu_seconds=cpu, cumulative_max_child_rss_kib=after['peak_rss_kib']))
        all_cpu = [r['child_cpu_seconds'] for r in records]
        report = dict(
            status='passed' if len(records) == len(commands) and all(r['exit_code'] == 0 for r in records)
            else 'incomplete_or_failed', commands=records, wall_seconds=time.perf_counter()-overall,
            whole_run_limit_seconds=240, measured_child_cpu_seconds=sum(all_cpu) if all(v is not None for v in all_cpu) else None,
            workers=1, platform=sys.platform, resource_measurement_basis=after['basis'],
            rss_note='Running maximum, not simultaneous RSS; unavailable measurements are null.',
            scope='Only the five offline checks; no source interpretation, TeX/PDF build, or release-readiness certification.')
        (out / 'run.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if code != 0:
            print(f'{name} failed; inspect {out}', file=sys.stderr)
            return 1
    summary = json.loads((results / 'corpus_summary.json').read_text(encoding='utf-8'))
    tests = (out / 'tests.stderr.txt').read_text(encoding='utf-8')
    try:
        test_count = completed_test_count(tests)
    except ValueError as exc:
        report['status'] = 'incomplete_or_failed'
        report['test_summary_error'] = str(exc)
        (out / 'run.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(dict(status='passed', commands=len(commands), corpus_records=summary['records'],
                         unit_tests=test_count,
                         independent_review=False)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
