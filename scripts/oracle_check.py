from pathlib import Path
import argparse,json,sys,time
from resource_usage import usage
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_coverage import exhaustive_3x3
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results');a=p.parse_args()
t=time.perf_counter();c=time.process_time();r=exhaustive_3x3()
a.out.mkdir(parents=True,exist_ok=True)
(a.out/'oracle_result.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
r=usage()
(a.out/'oracle_resources.json').write_text(json.dumps({'wall_seconds':time.perf_counter()-t,'cpu_seconds':time.process_time()-c,'peak_rss_kib':r['peak_rss_kib'],'rss_measurement_basis':r['basis'],'workers':1,'seed':None,'enumeration':'all 3^9 ternary inputs and all consistent binary completions'},indent=2)+'\n')
print(json.dumps(r,sort_keys=True))
