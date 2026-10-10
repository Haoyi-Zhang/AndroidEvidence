# Manuscript source

This directory contains the single-column ACM review manuscript source,
97-entry bibliography, generated count fragments, and native TikZ figures.
The template mode is `manuscript,screen,review`; fonts, margins and page
dimensions come from the unmodified ACM class.

From the artifact repository root, regenerate the evidence fragments and build:

```sh
python -B scripts/reproduce.py
python -B manuscript_snapshot/build.py
```

The build uses `pdflatex`, BibTeX and `pdfinfo`, with shell escape disabled.
It checks citation closure and agreement with `data/references.bib`, imports
the generated fragments from `results/tex/`, and rejects layout errors or a
manuscript exceeding the project's local 35-page budget. That budget is not
a statement of the journal's official submission limit. The current review
manuscript has 34 pages including references.

`paper.pdf` and `build/main.pdf` are equivalent output entry points for this
manuscript. A build checks document structure; it does not replace review of
the source interpretations or mathematical arguments.
