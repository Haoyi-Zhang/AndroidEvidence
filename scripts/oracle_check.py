from pathlib import Path
import argparse,json,sys,time,resource
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_coverage import exhaustive_3x3
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args()
t=time.perf_counter();c=time.process_time();r=exhaustive_3x3()
a.out.mkdir(parents=True,exist_ok=True)
(a.out/'oracle_result.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
(a.out/'oracle_resources.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-t,'cpu_seconds':time.process_time()-c,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'workers':1,'seed':None,'enumeration':'all 3^9 ternary inputs and all consistent binary completions'},indent=2)+'\n')
print(json.dumps(r,sort_keys=True))
