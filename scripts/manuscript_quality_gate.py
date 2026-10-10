from pathlib import Path
import re,json,subprocess,sys
ART=Path(__file__).resolve().parents[1]; ROOT=ART.parent; PAPER=ROOT/'paper'; MAN=ART/'manifests'
if not PAPER.is_dir():
 raise SystemExit('Full-project input required: the manuscript gate needs the sibling paper tree and compiled PDF/log. Run scripts/reproduce.py for standalone evidence checks.')
main=PAPER/'main.tex'
assert main.is_file(), 'paper/main.tex is missing'
tex=main.read_text(encoding='utf-8',errors='ignore')
sources=[]; pending=[main]; visited=set()
while pending:
 p=pending.pop().resolve()
 assert p.is_relative_to(PAPER.resolve()), 'TeX input leaves the manuscript directory'
 if p in visited:continue
 visited.add(p)
 content=p.read_text(encoding='utf-8')
 sources.append(content)
 for name in re.findall(r'\\input\{([^{}]+)\}',content):
  path=PAPER/name
  if not path.suffix:path=path.with_suffix('.tex')
  assert path.is_file(), f'Missing TeX input: {name}'
  pending.append(path)
alltex='\n'.join(sources)
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
assert r'\documentclass[manuscript,screen,review]{acmart}' in tex
# Unassigned publication furniture is omitted; scientific layout is unchanged.
for pat in [r'nonacm',r'printccs\s*=\s*false',r'\\geometry\{',r'\\vspace\s*\{\s*-',r'\\vskip\s*-']:
    assert not re.search(pat,alltex,re.I),pat
# Diagram labels use an explicit readable local font; body typography remains
# controlled by the publisher class, including outside figure environments.
bodytex=re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', alltex, flags=re.S)
for pat in [r'\\fontsize\{',r'\\tiny\b']:
 assert not re.search(pat,bodytex,re.I),pat
for size in re.findall(r'\\fontsize\{([0-9.]+)\}',alltex):
 assert float(size)>=8, 'Diagram label font is smaller than 8 pt'
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
pdf=PAPER/'build'/'main.pdf'
if not pdf.is_file():pdf=PAPER/'paper.pdf'
assert pdf.is_file(), 'Compiled main PDF is missing'
try:
 import fitz
 with fitz.open(pdf) as document:n=document.page_count
except Exception:
 o=subprocess.check_output(['pdfinfo',str(pdf)],text=True);n=int(re.search(r'^Pages:\s+(\d+)',o,re.M).group(1))
budget=35
assert 0<n<=budget,f'Local manuscript budget is at most {budget} pages; the PDF has {n}.'
out={'status':'PASS','main_tex':str(main.relative_to(ROOT)),'abstract_words':len(abstract_words),'sections':len(sections),'subsections':len(subsections),'labels':len(labels),'references_to_labels':len(refs),'pages':n,'local_page_budget':budget,'scope':'Structural and rhetorical gate; not a substitute for independent copyediting or peer judgment.'}
(MAN/'MANUSCRIPT-QUALITY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('MANUSCRIPT QUALITY GATE: PASS');print(json.dumps(out,sort_keys=True))
