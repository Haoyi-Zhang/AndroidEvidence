from pathlib import Path
import argparse,re,json,subprocess,sys,runpy
ART=Path(__file__).resolve().parents[1]; MAN=ART/'manifests'
parser=argparse.ArgumentParser(description='Check the current manuscript PDF/source/log without compiling or rerunning scientific experiments.')
parser.add_argument('--snapshot',action='store_true',help='Select the artifact-only manuscript even when a sibling paper exists.')
parser.add_argument('--out',type=Path,default=MAN/'MANUSCRIPT-QUALITY.json',help='Quality JSON output path.')
args=parser.parse_args()
FULL=(ART.parent/'paper').is_dir() and not args.snapshot
ROOT=ART.parent if FULL else ART
PAPER=ART.parent/'paper' if FULL else ART/'manuscript_snapshot'
if not PAPER.is_dir():
 raise SystemExit('Current manuscript source and compiled PDF/log are required in paper/ or manuscript_snapshot/.')
main=PAPER/'main.tex'
build_config=runpy.run_path(str(PAPER/'build.py'))
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
 for braced,bare in re.findall(r'\\input\s*(?:\{([^{}]+)\}|([^\s{}%]+))',content):
  name=braced or bare
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
logpath=PAPER/'build/main.log'
assert logpath.is_file(),'no final LaTeX log'
log=logpath.read_text(encoding='utf-8',errors='ignore')
for bad in ['Undefined control sequence','There were undefined references','Citation `','multiply defined','Overfull \\hbox','Overfull \\vbox']:
 assert bad not in log,bad
# PDF page count.
pdf=PAPER/'build'/'main.pdf'
assert pdf.is_file(), 'Compiled main PDF is missing'
evidence=build_config['check_current_binding'](PAPER,pdf)
try:
 import fitz
 with fitz.open(pdf) as document:n=document.page_count
except Exception:
 o=subprocess.check_output(['pdfinfo',str(pdf)],text=True,encoding='utf-8',errors='replace');n=int(re.search(r'^Pages:\s+(\d+)',o,re.M).group(1))
budget=build_config['MAX_PAGES']
assert 0<n<=budget,f'Local manuscript budget is at most {budget} pages; the PDF has {n}.'
assert evidence['pages']==n,'Build-evidence page count differs from the PDF'
out={'status':'PASS','main_tex':main.relative_to(ROOT).as_posix(),'abstract_words':len(abstract_words),'sections':len(sections),'subsections':len(subsections),'labels':len(labels),'references_to_labels':len(refs),'pages':n,'local_page_budget':budget,'scope':'Structural and rhetorical gate; not a substitute for independent copyediting or peer judgment.'}
out.update(pdf=pdf.relative_to(ROOT).as_posix(),pdf_sha256=evidence['pdf_sha256'],source_sha256=evidence['source_sha256'],log_sha256=evidence['log_sha256'],manuscript_mode='sibling-paper' if FULL else 'artifact-only-snapshot')
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(out,indent=2),encoding='utf-8')
print('MANUSCRIPT QUALITY GATE: PASS');print(json.dumps(out,sort_keys=True))
