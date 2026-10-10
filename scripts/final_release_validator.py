"""Check the delivered manuscript against a fresh owned-artifact reproduction."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ART = Path(__file__).resolve().parents[1]
PAPER = ART.parent / 'paper'
FULL = PAPER.is_dir()
if not FULL:
    PAPER = ART / 'manuscript_snapshot'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ART / 'results' / 'validation')
    args = parser.parse_args()
    output = args.out.resolve()
    subprocess.run([sys.executable, '-B', str(ART / 'scripts/reproduce.py'),
                    '--out', str(output)], cwd=ART, check=True, timeout=260)
    run = json.loads((output / 'reproduction/run.json').read_text(encoding='utf-8'))
    corpus = json.loads((output / 'corpus_summary.json').read_text(encoding='utf-8'))
    if run['status'] != 'passed':
        raise SystemExit('Artifact reproduction did not complete successfully.')
    subprocess.run([sys.executable, '-B', str(PAPER / 'check_citations.py')],
                   cwd=PAPER, check=True, timeout=45)
    if (PAPER / 'references.bib').read_bytes() != (ART / 'data/references.bib').read_bytes():
        raise SystemExit('Paper and artifact bibliography differ.')
    pdf = PAPER / 'build/main.pdf'
    if not pdf.is_file():
        pdf = PAPER / 'paper.pdf'
    if not pdf.is_file():
        raise SystemExit('Build the manuscript before checking the delivery.')
    try:
        import fitz
        with fitz.open(pdf) as document:
            pages = document.page_count
    except ImportError:
        import re
        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    if not 0 < pages <= 35:
        raise SystemExit(f'Manuscript has {pages} pages; local budget is at most 35.')
    if FULL:
        subprocess.run([sys.executable, '-B', str(ART / 'scripts/manuscript_quality_gate.py')],
                       cwd=ART, check=True, timeout=45)
    report = {'status': 'passed', 'pages': pages, 'local_page_budget': 35,
              'corpus_records': corpus['records'], 'reproduction_commands': len(run['commands']),
              'pdf': str(pdf.relative_to(ART.parent if FULL else ART)),
              'scope': 'Fresh offline consistency checks and current manuscript structure; not external peer review or full-source interpretation.'}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
