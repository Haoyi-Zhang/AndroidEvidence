"""Serial, bounded, offline reproduction with command-level evidence."""
from pathlib import Path
import json,os,resource,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/reproduction';out.mkdir(parents=True,exist_ok=True)
    commands=[('corpus',[sys.executable,'scripts/corpus_audit.py']),
              ('ledger',[sys.executable,'scripts/audit.py']),
              ('oracle',[sys.executable,'scripts/oracle_check.py']),
              ('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v']),
              ('tables',[sys.executable,'scripts/render_tables.py'])]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1')
    records=[];overall=time.perf_counter()
    for name,cmd in commands:
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.perf_counter()
        timeout=False
        with (out/(name+'.stdout.txt')).open('w') as so,(out/(name+'.stderr.txt')).open('w') as se:
            try:
                result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=so,stderr=se,timeout=45,check=False)
                code=result.returncode
            except subprocess.TimeoutExpired:
                code=None;timeout=True
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        records.append({'name':name,'command':['python']+cmd[1:],'cwd':'repository root','timeout_seconds':45,
            'timed_out':timeout,'exit_code':code,'wall_seconds':time.perf_counter()-start,
            'child_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'cumulative_max_child_rss_kib':after.ru_maxrss})
        report={'status':'passed' if all(r['exit_code']==0 for r in records) and len(records)==len(commands) else 'incomplete_or_failed',
            'commands':records,'wall_seconds':time.perf_counter()-overall,
            'measured_child_cpu_seconds':sum(r['child_cpu_seconds'] for r in records),'workers':1,
            'rss_note':'Linux RUSAGE_CHILDREN running maximum, not a sum of simultaneous RSS.',
            'scope':'Only these commands; discovery/intake and earlier construction were not fully CPU instrumented.'}
        (out/'run.json').write_text(json.dumps(report,indent=2)+'\n')
        if code!=0:
            print(f'{name} failed; inspect results/reproduction/',file=sys.stderr);return 1
    summary=json.loads((ROOT/'results/corpus_summary.json').read_text(encoding='utf-8'))
    print(json.dumps({'status':'passed','commands':len(commands),'corpus_records':summary['records'],'unit_tests':sum(1 for line in (out/'tests.stderr.txt').read_text(encoding='utf-8').splitlines() if line.startswith('test_') and ' ... ok' in line),'independent_review':False}));return 0
if __name__=='__main__':raise SystemExit(main())


# Scientific-scope and reviewer-readiness gate.
if __name__ == '__main__':
    import subprocess as _sp, sys as _sys
    _sp.run([_sys.executable, str(Path(__file__).with_name('scientific_integrity_gate.py'))], check=True)


# Manuscript structural and rhetoric gate.
if __name__ == '__main__':
    import subprocess as _sp, sys as _sys
    _sp.run([_sys.executable, str(Path(__file__).with_name('manuscript_quality_gate.py'))], check=True)


# Final release validator.
if __name__ == '__main__':
    import subprocess as _sp, sys as _sys
    _sp.run([_sys.executable, str(Path(__file__).with_name('final_release_validator.py'))], check=True)
