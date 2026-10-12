# AI-era mobile software evidence artifact

This directory contains the standard-library-only evidence companion to **From Resemblance to Authority: Claim-Bounded Evidence for Android Software Lineage in AI-Mediated Supply Chains**. Its offline scripts check the evidence tables and finite coverage calculations.

## Reproduce

From this directory:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -B scripts/reproduce.py --out /path/to/check-output
```

Use an output path outside the artifact to keep a new local run separate from retained historical evidence. On Windows, set the two environment variables in the invoking shell. The runner executes five serial commands, each with a 45-second limit and a 240-second whole-run limit:

1. active-corpus, bibliography, publication-status, calibration, screening, extraction, and traceability audit;
2. retained historical gap-ledger audit;
3. independent finite completion oracle;
4. all discovered unit and mutation tests (69 methods, including six display-row regressions);
5. deterministic manuscript-table and count-fragment generation.

A passing run ends with a JSON object whose `status` is `passed`, `commands` is `5`, `corpus_records` is `97`, and `unit_tests` equals the completed discovered suite (69 methods in this source). Test counts come from the completed test summary, not possibly interleaved progress lines. Child CPU and peak RSS are reported as `null` when the platform lacks `getrusage`; missing measurements are not zero-filled.

## Current evidence inventory

- `data/corpus.csv` - 97 included scholarly records.
- `data/references.bib` - 97-entry standalone bibliography snapshot.
- `data/study_extractions.csv` - one populated claim-level row per record; current source-specific checks are identified separately.
- `data/source_locations.csv` - canonical record bindings, actual checked primary-fulltext URLs and PDF-page/numbered-HTML-section locators, reading boundaries and explicit content-check statuses.
- `data/search_provenance.csv` - one retrospective retained-record discovery trace per record.
- `data/bibliography_verification.csv` - one canonical identifier and publication-status row per record.
- `data/excluded_publications.csv` - excluded/superseded publication-status quarantine, including one withdrawn work.
- `data/review_gap_matrix.csv` - 21 closest review/method records coded across seven dimensions.
- `data/calibration_papers.csv` - 22 writing-calibration papers: 12 closest, five influential/method, five adjacent.
- `data/source_rechecks.csv` - 90 cumulative disclosed same-process recheck records (92.8%), with dates and reading boundaries. The content ledger checks 87 works; three recheck entries retain historical/non-paper readings. The cumulative count is not a count of newly read papers.
- `data/screening_ledger.csv` - 105 retained and excluded screening decisions.
- `data/synthesis_claims.csv` - seven synthesis rules with supporting sources, counter-histories, and boundaries.
- `claim_evidence_ledger.csv` - 28 material paper/artifact claims and their evidence paths.

The retained corpus has 76 primary/empirical/system works and 21 review/method works. Seventy-four primary/system works and 93 works overall have venue publication evidence. Legacy reading-depth labels are 61 full-or-selected-source and 36 publisher-abstract-or-selected-source records. Current content checks cover 87 works: 84 selected readings and three complete scoped readings. Ten legacy records remain not reverified. The 21-row review matrix has 49 located direct/partial cells, two scoped absences and 96 unresolved cells and its direct all-dimension coverage is undetermined.

## What the checks establish

The selected ten-row manuscript matrix consumes `paper/generated/review_matrix_rows.tex`.
Its generator requires exactly one row for each displayed key in a declared
order and preserves all seven `0/P/1/?` cells. Six portable regressions in
`tests/test_render_tables.py` compare a named literal fixture and an independent
scan reference, exercise every selected cell/code, container permutations,
missing/duplicate keys, and failed-corpus admission. They run in the existing
discovered suite and scientific workflow; they validate display traceability,
not the coded interpretation of a publication. The literal display fixture follows the coded cells; formatting tests do not validate source interpretation.

The scripts enforce exact active key binding across corpus, bibliography, extractions, source locations, provenance, and status ledgers; title/year agreement; canonical DOI form for 82 DOI records; active/excluded quarantine; minimum corpus and review obligations; calibration group counts; explicit reading and independence boundaries; source-recheck coverage; synthesis-source bindings; and deterministic finite bookkeeping.

Additional controls reject checked-content promotion using generic page locators or missing primary-fulltext URLs, positive review coverage from unverified fulltexts, and absence coding based only on selected sections. Mutation tests ensure that withdrawn-status leakage, duplicate canonical identifiers, corpus/BibTeX title or year drift, DOI URL drift, publication-type mismatch, calibration-count drift, excluded-key leakage, review-key/record drift, stale recheck ceilings, and contradictory independence declarations make reproduction fail. Each corpus mutation first passes an unmutated positive control. A failed corpus audit retains its error JSON but cannot generate a new count fragment.

## What the checks do not establish

A passing run does not prove exhaustive search, a PRISMA denominator, a comprehensive retraction-registry search, independent source interpretation, detector accuracy, prevalence, causal direction, behavioral safety, worldwide novelty, or submission readiness. The same authoring process performed the extraction and recheck passes; `independent=false` is retained and no agreement statistic is reported.

## Main outputs

- `results/corpus_summary.json`
- `results/coverage_result.json`
- `results/oracle_result.json`
- `results/reproduction/run.json`
- `results/visual-inspection.json`
- `results/clean-reproduction.json`
- `results/tex/*.tex`

The retained corpus, coverage, oracle and execution/resource results under `results/` describe earlier research runs, not a new run. The manuscript-only `paper_build_evidence.json` and `manuscript_bibliography_audit.json` bind the actual PDF, final engine log and active source. Compiler commands and resource measurements describe the one sibling paper build; the snapshot is a byte-identical delivery mirror. `visual-inspection.json` records supplied layout inspection of all 36 full-size pages at 108 dpi and six contact grids, with all listed fonts embedded according to actual `pdffonts` checking. No clipped text, overlapping table/figure or citation-layout issue was observed. This layout inspection is not independent peer review or fulltext certification. `results/tex/*.tex` match the private reproduction fragments used for this build, without changing their coded values. A new `--out` run produces its own summaries, raw command logs and `tex/` fragments; historical CPU/RSS must not be attributed to that new run. The visual-evidence test requires a completed all-page receipt and is unchanged. No source-reading status is upgraded.

`manuscript_snapshot/` contains the synchronized active source for the current
36-page manuscript, with the same 36-page internal budget and a single
`build/main.pdf` output per build. In the complete packet the canonical delivery
is `paper/build/main.pdf`; current page/source bindings are in
`manifests/PAGE-COUNT.json`, `manuscript_snapshot/build-evidence.json` and
`manuscript_snapshot/visual-inspection.json`. The delivered snapshot PDF and actual final engine log
are byte-identical current mirrors for artifact-only use. Its current metadata
is in `manuscript_snapshot/` and `results/`; the older manuscript-only PDF/logs
are privately archived. See `manuscript_snapshot/README.md`. This packaging
alignment neither upgrades source-reading coverage nor certifies CSUR policy.

When this directory is the repository root, `.github/workflows/scientific-checks.yml` runs these owned offline checks on Ubuntu 24.04 and uploads raw output even on failure. The retained local Windows run in `results/current/` records the earlier 61-test suite; its timing and platform details remain historical. The current source suite has 69 tests; retained raw runs do not describe current execution. All 97 corpus records pass their consistency checks, and 19,683 ternary matrices plus 262,144 binary completions have no oracle disagreement. Generated count fragments describe this same retained corpus, not a new literature-search or source-reading pass.
