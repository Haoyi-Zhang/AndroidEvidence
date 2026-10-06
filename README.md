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
4. 55 unit and mutation tests;
5. deterministic manuscript-table and count-fragment generation.

A passing run ends with a JSON object whose `status` is `passed`, `commands` is `5`, `corpus_records` is `97`, and `unit_tests` is `55`. Test counts come from the completed test summary, not possibly interleaved progress lines. Child CPU and peak RSS are reported as `null` when the platform lacks `getrusage`; missing measurements are not zero-filled.

## Current evidence inventory

- `data/corpus.csv` - 97 included scholarly records.
- `data/references.bib` - 97-entry standalone bibliography snapshot.
- `data/study_extractions.csv` - one source-specific claim-level extraction per record.
- `data/source_locations.csv` - one consumed-source and reading-boundary row per record.
- `data/search_provenance.csv` - one retrospective retained-record discovery trace per record.
- `data/bibliography_verification.csv` - one canonical identifier and publication-status row per record.
- `data/excluded_publications.csv` - excluded/superseded publication-status quarantine, including one withdrawn work.
- `data/review_gap_matrix.csv` - 21 closest review/method records coded across seven dimensions.
- `data/calibration_papers.csv` - 22 writing-calibration papers: 12 closest, five influential/method, five adjacent.
- `data/source_rechecks.csv` - 26 cumulative disclosed same-process source-grounded rechecks (26.8%), with dates and reading boundaries. This is not a new all-source recheck batch.
- `data/screening_ledger.csv` - 105 retained and excluded screening decisions.
- `data/synthesis_claims.csv` - seven synthesis rules with supporting sources, counter-histories, and boundaries.
- `claim_evidence_ledger.csv` - 28 material paper/artifact claims and their evidence paths.

The retained corpus has 76 primary/empirical/system works and 21 review/method works. Seventy-four primary/system works and 93 works overall have venue publication evidence. Reading depth is 61 full-or-selected-source records and 36 publisher-abstract-or-selected-source records.

## What the checks establish

The scripts enforce exact active key binding across corpus, bibliography, extractions, source locations, provenance, and status ledgers; title/year agreement; canonical DOI form for 82 DOI records; active/excluded quarantine; minimum corpus and review obligations; calibration group counts; explicit reading and independence boundaries; source-recheck coverage; synthesis-source bindings; and deterministic finite bookkeeping.

Mutation tests ensure that withdrawn-status leakage, duplicate canonical identifiers, corpus/BibTeX title or year drift, DOI URL drift, publication-type mismatch, calibration-count drift, excluded-key leakage, review-key/record drift, stale recheck ceilings, and contradictory independence declarations make reproduction fail. Each corpus mutation first passes an unmutated positive control. A failed corpus audit retains its error JSON but cannot generate a new count fragment.

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

The retained `results/`, build evidence, PDFs, and visual-inspection files describe earlier recorded runs, not the repaired source state. A new `--out` run produces its own summaries, raw command logs, and `tex/` fragments. Regenerate and import those fragments before rebuilding the paper; historical CPU/RSS or PDF-layout measurements must not be attributed to a new local run.

When this directory is the repository root, `.github/workflows/scientific-checks.yml` runs only these owned offline checks on Ubuntu 24.04 with bounded time/memory and uploads raw output even on failure. The current Linux run in `results/current/` completes all five commands in 6.57 seconds, with 55 passing tests and no skips. All 97 corpus records pass their consistency checks, and 19,683 ternary matrices plus 262,144 binary completions have no oracle disagreement. Generated count fragments describe this same retained corpus, not a new literature-search or source-reading pass.
