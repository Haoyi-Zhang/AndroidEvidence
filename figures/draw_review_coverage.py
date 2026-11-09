"""Render located, partial, absent, and unresolved source codes without recoding."""
import csv
from collections import Counter
from pathlib import Path
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt

HERE=Path(__file__).resolve().parent
FIELDS=[
    ('android_repackaging','Repackaging'),('component_version','Component / version'),
    ('supply_chain_provenance','Process provenance'),('authorization_policy','Authorization'),
    ('behavioral_assurance','Behavior'),('ai_mediated_workflow','AI-mediated workflow'),
    ('claim_ceiling_binding','Claim ceiling / binding'),
]

def render(output=HERE/'review-coverage.pdf'):
    from android_panels import coverage
    with (HERE.parent/'data/review_gap_matrix.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==len({r['review_id'] for r in rows})==21
    counts=[Counter(r[k] for r in rows) for k,_ in FIELDS]
    assert all(set(c)<={'1','P','0','?'} and c.total()==21 for c in counts)
    totals=sum(counts,Counter())
    assert (totals['1']+totals['P'],totals['0'],totals['?'])==(75,41,31)
    return coverage(counts,FIELDS,output)

if __name__=='__main__':
    render()
