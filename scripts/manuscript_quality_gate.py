from pathlib import Path
import re,json,subprocess,sys
ART=Path(__file__).resolve().parents[1]; ROOT=ART.parent; PAPER=ROOT/'paper'; MAN=ART/'manifests'
if not PAPER.is_dir():
 raise SystemExit('Full-project input required: the manuscript gate needs the sibling paper tree and compiled PDF/log. Run scripts/reproduce.py for standalone evidence checks.')
main=max([(p.stat().st_size,p) for p in PAPER.rglob('*.tex') if '\\documentclass' in p.read_text(encoding='utf-8',errors='ignore')])[1]
tex=main.read_text(encoding='utf-8',errors='ignore')
alltex='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in PAPER.rglob('*.tex'))
# Front matter and argument structure.
am=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',alltex,re.S)
assert am,'abstract missing'
absplain=re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}',r'\1',am.group(1))
absplain=re.sub(r'\\[A-Za-z]+|[{}]',' ',absplain)
abstract_words=re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*",absplain)
assert 120<=len(abstract_words)<=350,len(abstract_words)
sections=re.findall(r'\\section\{([^}]+)\}',alltex)
subsections=re.findall(r'\\subsection\{([^}]+)\}',alltex)
assert len(sections)>=7,sections
assert re.search(r'\bRQ\s*1\b|research question',alltex,re.I),'research questions absent'
# Reviewer-facing prose must not contain workflow chatter or unfinished-state language.
for phrase in ['current checkpoint','work in progress','unfinished manuscript','we were asked to']:
    assert phrase not in alltex.lower(),phrase
# Reject common absolute novelty inflation and unsupported performance rhetoric.
for phrase in ['the first comprehensive survey','the first survey of','no prior work has','state-of-the-art accuracy','outperforms all']:
    assert phrase not in alltex.lower(),phrase
# Template integrity and anti-page-hacking.
assert re.search(r'\\documentclass\[[^\]]*(?:acmsmall|acmlarge)[^\]]*\]\{acmart\}',alltex)
for pat in [r'nonacm',r'\\setcopyright\{none\}',r'printacmref\s*=\s*false',r'printccs\s*=\s*false',r'\\geometry\{',r'\\fontsize\{',r'\\tiny\b',r'\\vspace\s*\{\s*-',r'\\vskip\s*-']:
    assert not re.search(pat,alltex,re.I),pat
assert '\\nocite{*}' not in alltex
# Cross-reference integrity at source level.
labels=re.findall(r'\\label\{([^}]+)\}',alltex); refs=re.findall(r'\\(?:ref|autoref|cref|Cref)\{([^}]+)\}',alltex)
assert len(labels)==len(set(labels)),'duplicate labels'
missing=sorted(set(refs)-set(labels));assert not missing,missing
# All figures and tables need captions and labels.
float_issues=[]
for env in ('figure','figure*','table','table*'):
 for m in re.finditer(r'\\begin\{'+re.escape(env)+r'\}(.*?)\\end\{'+re.escape(env)+r'\}',alltex,re.S):
  b=m.group(1)
  if '\\caption' not in b or '\\label' not in b:float_issues.append(env)
assert not float_issues,float_issues
# Build log checks.
logs=sorted(PAPER.rglob('*.log'),key=lambda p:p.stat().st_mtime,reverse=True)
assert logs,'no LaTeX log'
log=logs[0].read_text(encoding='utf-8',errors='ignore')
for bad in ['Undefined control sequence','There were undefined references','Citation `','multiply defined','Overfull \\hbox','Overfull \\vbox']:
 assert bad not in log,bad
# PDF page count.
pdfs=sorted(PAPER.rglob('*.pdf'),key=lambda p:p.stat().st_mtime,reverse=True);assert pdfs
try:
 import fitz;n=fitz.open(pdfs[0]).page_count
except Exception:
 o=subprocess.check_output(['pdfinfo',str(pdfs[0])],text=True);n=int(re.search(r'^Pages:\s+(\d+)',o,re.M).group(1))
assert n==35,f'Project manuscript target is 35 pages; the actual PDF has {n}. This is not a source-code execution failure or a newly verified journal hard limit.'
out={'status':'PASS','main_tex':str(main.relative_to(ROOT)),'abstract_words':len(abstract_words),'sections':len(sections),'subsections':len(subsections),'labels':len(labels),'references_to_labels':len(refs),'pages':n,'scope':'Structural and rhetorical gate; not a substitute for independent copyediting or peer judgment.'}
(MAN/'MANUSCRIPT-QUALITY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('MANUSCRIPT QUALITY GATE: PASS');print(json.dumps(out,sort_keys=True))
