# AI-era mobile software evidence artifact

This directory contains the standard-library-only evidence companion to **From Resemblance to Authority: Claim-Bounded Evidence for Android Software Lineage in AI-Mediated Supply Chains**. Its offline scripts check the evidence tables and finite coverage calculations.

## Reproduce

From this directory:

```bash
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -B scripts/reproduce.py --out /path/to/check-output
```

Use an output path outside the artifact to keep a new local run separate from retained historical evidence. On Windows, set the two environment variables in the invoking shell. The runner executes five serial commands, each with a 45-second limit and a 240-second whole-run limit:

1. active-corpus, bibliography, publication-status, screening, extraction, and traceability audit;
2. retained historical gap-ledger audit;
3. independent finite completion oracle;
4. all discovered unit and mutation tests, including display-row, reader-assessment and matrix-admission regressions;
5. deterministic manuscript-table and count-fragment generation.

A passing run ends with a JSON object whose `status` is `passed`, `commands` is `5`, `corpus_records` is `97`, and `unit_tests` equals the completed discovered suite. This count is distinct from the 88 source-location checks and 85 complete seven-field assessments. Test counts come from the completed test summary, not interleaved progress lines. Child CPU and peak RSS are reported as `null` when the platform lacks `getrusage`; missing measurements are not zero-filled.

## Current evidence inventory

- `data/corpus.csv` - 97 included scholarly records.
- `data/references.bib` - 97-entry standalone bibliography snapshot.
- `data/study_extractions.csv` - one populated claim-level row per record; current source-specific checks are identified separately.
- `data/source_locations.csv` - canonical record bindings, actual checked primary-fulltext URLs and PDF-page/numbered-HTML-section locators, reading boundaries and explicit content-check statuses.
- `data/search_provenance.csv` - one retrospective retained-record discovery trace per record.
- `data/bibliography_verification.csv` - one canonical identifier and publication-status row per record.
- `data/excluded_publications.csv` - excluded/superseded publication-status quarantine, including one withdrawn work.
- `data/review_gap_matrix.csv` - 21 closest review/method records coded across seven dimensions.
- `data/source_rechecks.csv` - 90 cumulative disclosed same-process recheck records (92.8%), with dates and reading boundaries. The content ledger checks 88 works; two recheck entries retain historical/non-paper readings. The cumulative count is not a count of newly read papers.
- `data/source_readings.csv` - eighty-five retrieved-PDF locator/version rows, source-byte digests, physical page counts, version distinctions and the same-process extractor declaration. Acquisition and locator rows are separate from completed semantic assessments.
- `data/semantic_readings.csv` - eighty-five explicit complete-retrieved-PDF/seven-field reader assessments, bound to the exact source and coded values; software checks their identity and counts, not understanding.
- `data/recoding_transitions.csv` - eighty-two dated bindings from unchanged historical ceiling rechecks to located current recodings; historical recheck rows are not rewritten to match current conclusions.
- `data/screening_ledger.csv` - 105 retained and excluded screening decisions.
- `data/synthesis_claims.csv` - seven synthesis rules with supporting sources, counter-histories, and boundaries.
- `claim_evidence_ledger.csv` - 27 material paper/artifact claims and their evidence paths.

The retained corpus has 76 primary/empirical/system works and 21 review/method works. Seventy-four primary/system works and 93 works overall have venue publication evidence. Legacy reading-depth labels remain 61 full-or-selected-source and 36 publisher-abstract-or-selected-source records. Locator entries cover 88 works: three selected HTML readings and 85 complete-scoped PDF rows. The separate reader ledger records complete retrieved-PDF/seven-field coding for all 85 acquired PDFs. Twelve records have no acquired PDF through attempted routes, although some have selected HTML readings; nine lack the locator check. The 21-row review matrix has 75 direct/partial cells, 41 scoped absences and 31 unresolved cells, leaving direct all-dimension coverage undetermined. Brereton's seven cells await representation-aware admission; the other 24 unresolved cells require further original-source support. The TPL review's component-policy coverage, AStRA v2's prospective AI discussion and Williams et al.'s direct AI-workflow treatment retain their distinct scopes. Complete retrieved-source reading does not certify an uncompared final publication or independent human coding.

## What the checks establish

The selected ten-row manuscript matrix consumes `paper/generated/review_matrix_rows.tex`.
Its generator requires exactly one row for each displayed key in a declared
order and preserves all seven `0/P/1/?` cells. Six portable regressions in
`tests/test_render_tables.py` compare a named literal fixture and an independent
scan reference, exercise every selected cell/code, container permutations,
missing/duplicate keys, and failed-corpus admission. They run in the existing
discovered suite and scientific workflow; they validate display traceability,
not the coded interpretation of a publication. The literal display fixture follows the coded cells; formatting tests do not validate source interpretation.

`tests/test_review_matrix_admissions.py` binds the 16 TPL/Wohlin/Kitchenham
matrix decisions to their exact retrieved source versions, physical page
locators, existing complete reader assessments and seven-field bindings.
Negative controls remove or downgrade those prerequisites and alter cell/page
values. These are consistency controls for declared source-based judgments,
not a new source-reading pass or a second human interpretation. The matrix CSV
schema and the 85/595 reading/field denominators are unchanged.

The scripts enforce exact active key binding across corpus, bibliography, extractions, source locations, provenance, and status ledgers; title/year agreement; canonical DOI form for 82 DOI records; active/excluded quarantine; retained corpus and review bindings; explicit reading and independence boundaries; source-recheck coverage; synthesis-source bindings; and deterministic finite bookkeeping.

Additional controls reject checked-content promotion using generic page locators or missing primary-fulltext URLs, positive review coverage from unverified fulltexts, and absence coding based only on selected sections. Mutation tests ensure that withdrawn-status leakage, duplicate canonical identifiers, corpus/BibTeX title or year drift, DOI URL drift, publication-type mismatch, excluded-key leakage, review-key/record drift, stale recheck ceilings, and contradictory independence declarations make reproduction fail. Each corpus mutation first passes an unmutated positive control. A failed corpus audit retains its error JSON but cannot generate a new count fragment.

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

Most retained results under `results/` describe earlier offline runs. The exceptions are `corpus_summary.json`, `paper_build_evidence.json`, `visual-inspection.json`, and the six default `tex/` fragments, which describe current coded inputs or mirror the owned 38-page manuscript build. A new `--out` run produces separate summaries, raw command logs and `tex/` fragments; historical CPU/RSS must not be attributed to that new run. The visual-evidence regression compares the current snapshot receipt, result mirrors, active source/PDF/log and dynamic content-check counts; it does not certify source interpretation.

`manuscript_snapshot/` mirrors the current sibling `paper/` source, 38-page PDF,
final engine log, compiled bibliography, build evidence and directly inspected
180-dpi visual receipt. The local budget is 39 pages, not a certified CSUR cap.
The sibling `paper/` remains the primary source; the snapshot is an artifact-only
delivery mirror, not a second compilation. Earlier evidence is retained privately.

When this directory is the repository root, `.github/workflows/scientific-checks.yml` runs these owned offline checks on Ubuntu 24.04 and uploads raw output even on failure. Exact-commit workflow results provide CI execution evidence separately from this configuration. The current local reproduction in `results/current/` records the completed 112-test suite and its actual platform and timing fields. Earlier runs are retained outside the delivery tree. All 97 corpus records pass their consistency checks; 19,683 ternary matrices and 262,144 binary completions have no oracle disagreement. Regenerated fragments describe the coded inputs, not search completeness or independent source interpretation.

## Located coding and reading boundaries

The `reading_scope` field in `data/source_readings.csv` uses
`retrieved_pdf_locator_binding`: it identifies an acquired PDF and bounded
locators, rather than asserting a completed semantic reading. The field-binding
tests reject the former completed-reading label. Source-specific interpretation
requires the separately documented literature reading and coding.

`data/field_evidence.csv` contains 595 located field bindings for 85 retrieved PDFs. Each coded value is bound to its extraction, primary URL, source bytes and physical pages, with source reports separated from analytical classifications. Complete-reading assessments for those 85 representations are declared separately in `data/semantic_readings.csv`; twelve records lack supplementary seven-field bindings. RepDetector uses the 17-page PSU author manuscript rather than treating an earlier selected HTML reading as the same representation. AppForge v1 has 21 physical pages; extracted figure control characters do not change that count. Retrieved copies and final publications retain their stated version distinctions. No copyrighted primary PDFs are bundled.

The audit rejects extraction/locator disagreement, conflicting source URLs, missing or duplicate fields, stale coded values, and out-of-range physical pages. Reader assessments must match the exact source and the seven coded values; changing either requires reassessment. Historical-to-current transitions bind the unchanged older recheck to its later source and ceiling. The generated summaries retain the 595/679 field denominator and `semantic_interpretation_verified_by_code=false`. Software checks declarations and calculations; the reading judgments remain same-process assessments. Fresh fragments are generated before rebuilding the primary manuscript, then its exact PDF, source and visual evidence are mirrored.
