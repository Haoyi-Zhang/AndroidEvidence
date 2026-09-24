"""Check that the manuscript cites a large, internally consistent bibliography."""
from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parent
bib=(ROOT/'references.bib').read_text(encoding='utf-8')
keys=re.findall(r'^@\w+\{([^,]+),',bib,re.M)
duplicates=sorted({k for k in keys if keys.count(k)>1})
tex_parts=[]
for p in [ROOT/'main.tex',*sorted((ROOT/'sections').glob('*.tex'))]:
    tex_parts.append(p.read_text(encoding='utf-8'))
tex='\n'.join(tex_parts)
cited=[]
for m in re.finditer(r'\\cite[a-zA-Z*]*\s*\{([^}]+)\}',tex):
    cited.extend(k.strip() for k in m.group(1).split(',') if k.strip())
cited_unique=sorted(set(cited))
missing=sorted(set(cited_unique)-set(keys))
uncited=sorted(set(keys)-set(cited_unique))
report={'bibliography_entries':len(keys),'unique_bibliography_entries':len(set(keys)),
        'unique_cited_entries':len(cited_unique),'citation_occurrences':len(cited),
        'duplicates':duplicates,'missing_bib_entries':missing,'uncited_bib_entries':uncited,
        'minimum_unique_citations':55}
report['status']='passed' if len(cited_unique)>=55 and not duplicates and not missing and not uncited else 'failed'
(ROOT/'bibliography-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,sort_keys=True))
raise SystemExit(0 if report['status']=='passed' else 1)
