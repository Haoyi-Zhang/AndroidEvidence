from pathlib import Path
import argparse,re,json,subprocess,sys,runpy
ART=Path(__file__).resolve().parents[1]; MAN=ART/'manifests'

def require(condition, message):
 if not condition:
  raise ValueError(message)

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
require(main.is_file(), 'paper/main.tex is missing')
tex=main.read_text(encoding='utf-8')
sources=[]; pending=[main]; visited=set()
while pending:
 p=pending.pop().resolve()
 require(p.is_relative_to(PAPER.resolve()), 'TeX input leaves the manuscript directory')
 if p in visited:continue
 require(p.is_file(), f'Missing TeX input: {p}')
 visited.add(p)
 content=p.read_text(encoding='utf-8')
 sources.append(content)
 for braced,bare in re.findall(r'\\input\s*(?:\{([^{}]+)\}|([^\s{}%]+))',content):
  name=braced or bare
  path=PAPER/name
  if not path.suffix:path=path.with_suffix('.tex')
  require(path.is_file(), f'Missing TeX input: {name}')
  pending.append(path)
alltex='\n'.join(sources)
# Front matter and argument structure.
am=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',alltex,re.S)
require(am is not None,'abstract missing')
absplain=re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}',r'\1',am.group(1))
absplain=re.sub(r'\\[A-Za-z]+|[{}]',' ',absplain)
abstract_words=re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*",absplain)
require(120<=len(abstract_words)<=350,f'Abstract has {len(abstract_words)} words; expected 120-350.')
sections=re.findall(r'\\section\{([^}]+)\}',alltex)
subsections=re.findall(r'\\subsection\{([^}]+)\}',alltex)
require(7<=len(sections)<=9,f'Expected 7-9 H1 sections; found {len(sections)}: {sections}')
require(re.search(r'\bRQ\s*1\b|research question',alltex,re.I) is not None,'research questions absent')
# Reviewer-facing prose must not contain workflow chatter or unfinished-state language.
for phrase in ['current checkpoint','work in progress','unfinished manuscript','we were asked to']:
    require(phrase not in alltex.lower(),f'Unfinished-state phrase: {phrase}')
# Reject common absolute novelty inflation and unsupported performance rhetoric.
for phrase in ['the first comprehensive survey','the first survey of','no prior work has','state-of-the-art accuracy','outperforms all']:
    require(phrase not in alltex.lower(),f'Unsupported claim phrase: {phrase}')
# Template integrity and anti-page-hacking.
require(r'\documentclass[manuscript,screen,review]{acmart}' in tex,'ACM manuscript class contract missing')
# Unassigned publication furniture is omitted; scientific layout is unchanged.
for pat in [r'nonacm',r'printccs\s*=\s*false',r'\\geometry\{',r'\\vspace\s*\{\s*-',r'\\vskip\s*-']:
    require(re.search(pat,alltex,re.I) is None,f'Forbidden layout pattern: {pat}')
# Diagram labels use an explicit readable local font; body typography remains
# controlled by the publisher class, including outside figure environments.
bodytex=re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', alltex, flags=re.S)
for pat in [r'\\fontsize\{',r'\\tiny\b']:
 require(re.search(pat,bodytex,re.I) is None,f'Forbidden body font pattern: {pat}')
for size in re.findall(r'\\fontsize\{([0-9.]+)\}',alltex):
 require(float(size)>=8, 'Diagram label font is smaller than 8 pt')
require('\\nocite{*}' not in alltex,'Unbounded nocite is forbidden')
# Cross-reference integrity at source level.
labels=re.findall(r'\\label\{([^}]+)\}',alltex); refs=re.findall(r'\\(?:ref|autoref|cref|Cref)\{([^}]+)\}',alltex)
require(len(labels)==len(set(labels)),'duplicate labels')
missing=sorted(set(refs)-set(labels));require(not missing,f'Missing labels: {missing}')
# All figures and tables need captions and labels.
float_issues=[]
for env in ('figure','figure*','table','table*'):
 for m in re.finditer(r'\\begin\{'+re.escape(env)+r'\}(.*?)\\end\{'+re.escape(env)+r'\}',alltex,re.S):
  b=m.group(1)
  if '\\caption' not in b or '\\label' not in b:float_issues.append(env)
require(not float_issues,f'Uncaptioned or unlabeled floats: {float_issues}')
# Build log checks.
logpath=PAPER/'build/main.log'
require(logpath.is_file(),'no final LaTeX log')
log=logpath.read_text(encoding='utf-8',errors='ignore')
for bad in ['Undefined control sequence','There were undefined references','Citation `','multiply defined','Overfull \\hbox','Overfull \\vbox']:
 require(bad not in log,f'Final LaTeX log contains: {bad}')
# PDF page count.
pdf=PAPER/'build'/'main.pdf'
require(pdf.is_file(), 'Compiled main PDF is missing')
evidence=build_config['check_current_binding'](PAPER,pdf)
try:
 import fitz
 with fitz.open(pdf) as document:n=document.page_count
except Exception:
 o=subprocess.check_output(['pdfinfo',str(pdf)],text=True,encoding='utf-8',errors='replace')
 page_match=re.search(r'^Pages:\s+(\d+)',o,re.M)
 require(page_match is not None,'pdfinfo did not report a page count')
 n=int(page_match.group(1))
budget=build_config['MAX_PAGES']
require(0<n<=budget,f'Local manuscript budget is at most {budget} pages; the PDF has {n}.')
require(evidence['pages']==n,'Build-evidence page count differs from the PDF')
out={'status':'PASS','main_tex':main.relative_to(ROOT).as_posix(),'abstract_words':len(abstract_words),'sections':len(sections),'subsections':len(subsections),'labels':len(labels),'references_to_labels':len(refs),'pages':n,'local_page_budget':budget,'scope':'Structural and rhetorical gate; not a substitute for independent copyediting or peer judgment.'}
out.update(pdf=pdf.relative_to(ROOT).as_posix(),pdf_sha256=evidence['pdf_sha256'],source_sha256=evidence['source_sha256'],log_sha256=evidence['log_sha256'],manuscript_mode='sibling-paper' if FULL else 'artifact-only-snapshot')
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(out,indent=2),encoding='utf-8')
print('MANUSCRIPT QUALITY GATE: PASS');print(json.dumps(out,sort_keys=True))
