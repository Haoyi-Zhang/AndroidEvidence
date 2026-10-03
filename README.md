# AI-era mobile software evidence artifact

This directory is a standalone, standard-library-only audit repository for the internal survey **From Resemblance to Authority: Claim-Bounded Evidence for Android Software Lineage in AI-Mediated Supply Chains**. It checks the delivered evidence ledgers and finite bookkeeping obligations. It does not execute malware, models, devices, external services, or attacks.

## Reproduce

From this directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/reproduce.py
```

The runner executes five serial commands, each with a 45-second limit:

1. active-corpus, bibliography, publication-status, calibration, screening, extraction, and traceability audit;
2. retained historical gap-ledger audit;
3. independent finite completion oracle;
4. 41 unit and mutation tests;
5. deterministic manuscript-table and count-fragment generation.

A passing run ends with a JSON object whose `status` is `passed`, `commands` is `5`, `corpus_records` is `97`, and `unit_tests` is `41`.

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
- `data/source_rechecks.csv` - 26 disclosed same-process source-grounded rechecks (26.8%).
- `data/screening_ledger.csv` - 105 retained and excluded screening decisions.
- `data/synthesis_claims.csv` - seven synthesis rules with supporting sources, counter-histories, and boundaries.
- `claim_evidence_ledger.csv` - 28 material paper/artifact claims and their evidence paths.

The retained corpus has 76 primary/empirical/system works and 21 review/method works. Seventy-four primary/system works and 93 works overall have venue publication evidence. Reading depth is 61 full-or-selected-source records and 36 publisher-abstract-or-selected-source records.

## What the checks establish

The scripts enforce exact active key binding across corpus, bibliography, extractions, source locations, provenance, and status ledgers; title/year agreement; canonical DOI form for 82 DOI records; active/excluded quarantine; minimum corpus and review obligations; calibration group counts; explicit reading and independence boundaries; source-recheck coverage; synthesis-source bindings; and deterministic finite bookkeeping.

Mutation tests ensure that withdrawn-status leakage, duplicate canonical identifiers, corpus/BibTeX title or year drift, DOI URL drift, publication-type mismatch, calibration-count drift, and excluded-key leakage make reproduction fail.

## What the checks do not establish

A passing run does not prove exhaustive search, a PRISMA denominator, a comprehensive retraction-registry search, independent source interpretation, detector accuracy, prevalence, causal direction, behavioral safety, worldwide novelty, or submission readiness. The same AI-assisted authoring process performed the extraction and recheck passes; `independent=false` is retained and no agreement statistic is reported.

## Main outputs

- `results/corpus_summary.json`
- `results/coverage_result.json`
- `results/oracle_result.json`
- `results/reproduction/run.json`
- `results/visual-inspection.json`
- `results/clean-reproduction.json`
- `results/tex/*.tex`

The `results/` directory contains reproducible outputs, not an independent review verdict.

## Optional manuscript gate

`scripts/manuscript_quality_gate.py` requires the full project distribution,
including the sibling `paper/` directory, its PDF and build log. It is not part
of standalone evidence reproduction. Its 35-page check is the project manuscript
target, not a claim that the current journal rules have been verified. The
current confirmed-author manuscript has 36 pages; that editorial target remains
unmet. Required truthful usage statements are not classified as workflow chatter.
