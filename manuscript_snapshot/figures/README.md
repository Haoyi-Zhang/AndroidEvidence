# Figure sources

The three conceptual diagrams are drawn by Python/Matplotlib in
`../../figures/build_figures.py`, then embedded as vector PDFs with STIX fonts.
Labels and geometry are maintained in Python; captions and figure references
remain in the adjacent TeX sections:

- `../sections/03-evidence-model.tex`, Figure `fig:ladder` — seven-level claim ladder.
- `../sections/06-provenance.tex`, Figure `fig:lifecycle` — lifecycle evidence chain.
- `../sections/08-synthesis.tex`, Figure `fig:assurance-case` — cross-layer assurance case.

No raster figure is required. Quantitative values are carried by booktabs tables and the audited corpus macros rather than plots.

The manuscript build calls this generator before TeX compilation. These diagrams
express the evidence model and lifecycle; they are not experimental measurements.
