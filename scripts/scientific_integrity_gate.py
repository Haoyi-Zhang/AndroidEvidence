from pathlib import Path
import ast,csv,json,re,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifact'; PAPER=ROOT/'paper'; DATA=ART/'data'; MAN=ART/'manifests'

def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
pyfiles=[p for p in ART.rglob('*.py') if '__pycache__' not in p.parts]
syntax=[]; functions=0; tests=0; loc=0; risky_paths=[]; network_in_repro=[]; ml_imports=[]
for p in pyfiles:
    t=p.read_text(encoding='utf-8',errors='ignore'); loc+=sum(1 for x in t.splitlines() if x.strip() and not x.lstrip().startswith('#'))
    try: tree=ast.parse(t,filename=str(p))
    except SyntaxError as e: syntax.append({'file':str(p.relative_to(ROOT)),'error':str(e)});continue
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            functions+=1
            if n.name.startswith('test_'):tests+=1
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            names=[]
            if isinstance(n,ast.Import):names=[a.name.split('.')[0] for a in n.names]
            else:names=[(n.module or '').split('.')[0]]
            if any(x in ('sklearn','torch','tensorflow','xgboost','lightgbm') for x in names):ml_imports.append({'file':str(p.relative_to(ROOT)),'imports':names})
    if '/mnt/data' in t or '/home/oai' in t:risky_paths.append(str(p.relative_to(ROOT)))
    if p.name in ('reproduce.py','final_reviewer_gate.py','scientific_integrity_gate.py'):
        if re.search(r'\b(?:urllib|requests|httpx|aiohttp|socket)\b',t):network_in_repro.append(str(p.relative_to(ROOT)))
assert not syntax, syntax
assert not risky_paths, risky_paths
assert not network_in_repro, network_in_repro
# Required evidence products
required=[DATA/'external_bibliography_verification.csv',DATA/'citation_context_ledger.csv',DATA/'review_robustness_analysis.csv',DATA/'claim_robustness_analysis.csv',MAN/'BLIND-REVIEW-AUDIT.json',MAN/'CLAIM-ROBUSTNESS.json',ART/'reports/FINAL-BLIND-REVIEW.md']
missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
assert not missing, missing
b=json.loads((MAN/'BLIND-REVIEW-AUDIT.json').read_text())
c=json.loads((MAN/'CLAIM-ROBUSTNESS.json').read_text())
oa=json.loads((MAN/'OPENALEX-STATUS-AUDIT.json').read_text())
assert oa['retracted']==0, oa
assert oa['title_mismatch']==0, oa
assert b['reference_count']>=55
assert b['reference_count']==b['cited_key_count']
assert b['failed_external_identity_checks']==0
assert c['unsupported']==0
# Source-frame stress tests must cover temporal, role, and depth partitions.
r=csvrows(DATA/'review_robustness_analysis.csv')
labels=' '.join(x.get('challenge','').lower() for x in r)
assert 'temporal' in labels or 'period' in labels
assert 'primary' in labels
assert 'depth' in labels or 'full' in labels
# Paper must state correct experimental boundary.
tex='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in PAPER.rglob('*.tex'))
for phrase in ['trains no classifier','source-frame overfitting','not estimates of detector accuracy','single-workflow self-audit']:
    assert phrase.lower() in tex.lower(), phrase
# Reject known inflated novelty formulations in the front matter.
front=tex[:40000].lower()
for phrase in ['the first comprehensive survey','the first survey of','no prior work has']:
    assert phrase not in front, phrase
# No predictive stack means conventional model overfitting is not silently being claimed.
assert not ml_imports, ml_imports
out={
 'status':'PASS','python_files':len(pyfiles),'nonblank_python_loc':loc,'functions':functions,'test_functions_detected':tests,
 'hard_coded_runtime_paths':risky_paths,'network_dependency_in_reproduction_entrypoints':network_in_repro,
 'predictive_ml_framework_imports':ml_imports,'references':b['reference_count'],'citation_occurrences':b['citation_occurrences'],
 'material_claims':c['claims'],'unsupported_material_claims':c['unsupported'],
 'scope_assessment':'Adequate for the claimed structured-synthesis and audit artifact. It does not constitute, and is not evaluated as, a production Android lineage detector.'
}
(MAN/'SCIENTIFIC-INTEGRITY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('SCIENTIFIC INTEGRITY GATE: PASS')
print(json.dumps(out,sort_keys=True))
