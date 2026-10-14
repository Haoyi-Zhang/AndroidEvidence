# Manuscript source

This directory contains the single-column ACM review manuscript source,
97-entry bibliography, generated count fragments, and native TikZ figures.
The template mode is `manuscript,screen,review`; fonts, margins and page
dimensions come from the unmodified ACM class.

From the artifact repository root, regenerate the evidence fragments and build:

```sh
python -B scripts/reproduce.py --out /path/to/check-output
python -B manuscript_snapshot/build.py --results /path/to/check-output
```

Use an output directory outside the artifact to preserve retained raw results.
On Windows, set `PYTHONUTF8=1` and `PYTHONDONTWRITEBYTECODE=1` in the invoking
shell. Without `--results`, the driver imports retained `results/tex/` fragments;
the default does not certify their freshness against the ledgers.

The build uses `pdflatex`, BibTeX and `pdfinfo`, with shell escape disabled.
It checks citation closure and agreement with `data/references.bib`, imports
the generated fragments from `results/tex/`, and rejects layout errors or a
manuscript exceeding the project's local 39-page budget. That budget accommodates
the current methodology content; it is not a statement of the journal's official
submission limit or CSUR certification. The genuinely rebuilt current manuscript
has 38 pages including references. Citation, overfull-box and typography guards
remain in force.

The active LaTeX inputs, bibliography, publisher template, current generated
fragments and build/citation drivers match the sibling `paper/` tree. The one
current PDF delivery in the complete packet is `paper/build/main.pdf`.
An artifact-only build writes only `manuscript_snapshot/build/main.pdf`; it does
not create a second `paper.pdf` entry point.

The delivered `build/main.pdf` is the current 38-page output of the sibling
paper's owned build driver, byte-identical to the complete-packet paper.
Its `build/main.log` and `build/main.bbl` are the actual final engine log and
compiled bibliography. Active TeX inputs, bibliography and publisher template
match the current build's source binding. The compiler commands and resource
measurements describe that one paper build, not a separate snapshot compilation.
Older compiler/visual evidence is preserved privately.

From the artifact root, check the delivered PDF/source/log without compiling:

```sh
python -B scripts/manuscript_quality_gate.py --snapshot --out /path/to/current-quality.json
```

The gate also selects this snapshot automatically in an artifact-only checkout.
It retains the page, overfull, citation/reference, font and template checks and
rejects stale byte bindings. A future source change needs its own actual build
and page-image inspection.

Current build metadata binds the genuine new PDF/log and records the actual
paper compiler run; unavailable Windows child CPU/RSS measurements remain null.
The supplied layout inspection directly covers all 38 full-size pages rendered
at 180 dpi; actual `pdffonts` checking confirmed all listed fonts embedded and no Type 3 font.
No clipped text, overlapping table/figure or citation-layout issue was observed.
This layout inspection is not independent peer review or fulltext certification.
A build checks document structure; it does not replace review of source
interpretations or mathematical arguments. Primary corpus/coverage/oracle
measurements and historical execution resources under `results/` remain unchanged.
The manuscript-only build, citation and visual metadata there identify
this current byte-bound delivery. The existing visual-evidence test still
requires a completed all-page receipt and has not been weakened.
