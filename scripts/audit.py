"""Reproduce the selected-record audit. No network, models, apps, or malware."""
from __future__ import annotations
import argparse,csv,json,time
from pathlib import Path
from coverage import summarize,minimal_known_cover
from resource_usage import usage
ROOT=Path(__file__).resolve().parents[1]
MAX_CSV_BYTES=2*1024*1024
CONFIRMED={'publisher_record','author_archive_publication_statement'}


def read_csv(path):
    if path.stat().st_size > MAX_CSV_BYTES: raise ValueError('oversized CSV')
    with path.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)>5000: raise ValueError('too many CSV rows')
    return rows


def eligible(record, mode='base'):
    if record['role'] not in {'core','adjacent'}: return False
    if record['publication_evidence']=='withdrawn': return False
    if mode=='core_only': return record['role']=='core'
    if mode=='publication_documented': return record['publication_evidence'] in CONFIRMED
    return True


def load_data():
    records=read_csv(ROOT/'data/records.csv')
    ids=[r['record_id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate record id')
    index={r['record_id']:r for r in records}
    obligations=read_csv(ROOT/'data/obligations.csv')
    oids=[r['obligation_id'] for r in obligations]
    if len(oids)!=len(set(oids)):raise ValueError('duplicate obligation id')
    cells=read_csv(ROOT/'data/coverage.csv'); lookup={}
    for c in cells:
        key=(c['record_id'],c['obligation_id'])
        if key in lookup: raise ValueError('duplicate cell')
        if key[0] not in index or key[1] not in oids:raise ValueError('unbound cell')
        if not key[0].startswith('R'):raise ValueError('primary study in review matrix')
        value=c['value']
        if value not in {'0','1','?'}:raise ValueError('invalid coverage value')
        if value=='1' and (c['basis']!='body_positive' or not c['source_location'] or index[key[0]]['reading_depth'] not in {'selected_sections','complete_substantive_text'}):
            raise ValueError('positive cell lacks substantive source locator')
        if value=='0' and (c['basis']!='complete_scope_absence' or index[key[0]]['reading_depth']!='complete_substantive_text'):
            raise ValueError('absence not grounded in a complete scoped reading')
        if not c['reason']:raise ValueError('cell lacks decision rationale')
        lookup[key]=None if value=='?' else int(value)
    expected={(rid,o) for rid in ids if rid.startswith('R') for o in oids}
    if set(lookup)!=expected:raise ValueError('coverage matrix incomplete')
    for r in records:
        if r['main_corpus_included']=='true':
            if not (r['record_id'].startswith('P') and r['publication_evidence'] in CONFIRMED and r['reading_depth']=='complete_substantive_text'):
                raise ValueError('unjustified promotion to main primary corpus')
    ex=read_csv(ROOT/'data/extractions.csv'); eids={x['extraction_id'] for x in ex}
    if len(eids)!=len(ex) or any(x['record_id'] not in index for x in ex):raise ValueError('unbound or duplicate extraction')
    for k in read_csv(ROOT/'data/contradictions.csv'):
        if k['left'] not in eids or k['right'] not in eids: raise ValueError('unbound contradiction')
    return records,obligations,lookup,ex


def compute():
    records,obligations,cells,extract=load_data()
    out={}
    def subset(name, chosen, obs):
        rids=[r['record_id'] for r in chosen];oids=[o['obligation_id'] for o in obs]
        mat=[[cells[r,o] for o in oids] for r in rids]
        result=summarize(mat)
        cover=minimal_known_cover(mat)
        result.update(record_ids=rids,obligation_ids=oids,
                      known_cover=None if cover is None else [rids[i] for i in cover])
        out[name]=result
    coarse=[o for o in obligations if o['granularity']=='coarse']
    for mode in ('base','core_only','publication_documented'):
        chosen=[r for r in records if eligible(r,mode)]
        subset(mode+'_all',chosen,obligations)
        subset(mode+'_coarse',chosen,coarse)
    base=[r for r in records if eligible(r)]
    for r in base:subset('leave_out_'+r['record_id'],[s for s in base if s!=r],coarse)
    selection=json.loads((ROOT/'data/recheck_selection.json').read_text())
    rechecks=read_csv(ROOT/'data/rechecks.csv') if (ROOT/'data/rechecks.csv').exists() else []
    selected={(r,o['obligation_id']) for r in selection['selected_records'] for o in obligations}
    actual={(r['record_id'],r['obligation_id']) for r in rechecks}
    if len(actual)!=len(rechecks):raise ValueError('duplicate recheck')
    if (selection.get('completed') and actual!=selected) or (rechecks and (actual!=selected or any(r['independent']!='false' for r in rechecks))):
        raise ValueError('recheck selection or independence disclosure mismatch')
    for r in rechecks:
        val=None if r['value_after']=='?' else int(r['value_after'])
        if val != cells[r['record_id'],r['obligation_id']]:raise ValueError('stale recheck')
    # A success label here is deliberately NOT a survey completion flag.
    return {'status':'ledger_audit_only','scientific_lock':False,
        'record_counts':{'selected_scholarly':len(records),'review_records':sum(r['record_id'].startswith('R') for r in records),
        'base_eligible_reviews':len(base),'withdrawn':sum(r['publication_evidence']=='withdrawn' for r in records),
        'boundary_reviews':sum(r['role']=='boundary' for r in records),'horizon_primary':sum(r['role']=='horizon_primary' for r in records),
        'main_primary_corpus':sum(r['main_corpus_included']=='true' for r in records),'extractions':len(extract),
        'coverage_cells':len(cells),'positive_cells':sum(v==1 for v in cells.values()),
        'unknown_cells':sum(v is None for v in cells.values())},
        'recheck':{'completed_cells':len(rechecks),'total_cells':len(cells),'fraction':len(rechecks)/len(cells),'independent':False},
        'analyses':out,'scope':'Pointwise coverage of encoded obligations only; not a worldwide absence or joint-synthesis proof.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results')
    args=parser.parse_args();start=time.perf_counter();cpu=time.process_time()
    result=compute();args.out.mkdir(parents=True,exist_ok=True)
    # Semantic result is deterministic; measured run metadata is intentionally separate.
    (args.out/'coverage_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    r=usage()
    measured={'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
              'peak_rss_kib':r['peak_rss_kib'],'rss_measurement_basis':r['basis'],
              'workers':1,'input_selection':'all supplied selected-record tables',
              'output':'coverage_result.json','scientific_experiment':False}
    (args.out/'audit_resources.json').write_text(json.dumps(measured,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':result['record_counts'],
        'coarse_mosaic':result['analyses']['base_coarse']['mosaic'],
        'joint_mosaic':result['analyses']['base_all']['mosaic']},sort_keys=True))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,csv.Error,json.JSONDecodeError) as e:
        raise SystemExit(f'audit failed: {e}')
