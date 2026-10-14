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
4. all discovered unit and mutation tests (101 methods, including six display-row and six reader-assessment regressions);
5. deterministic manuscript-table and count-fragment generation.

A passing run ends with a JSON object whose `status` is `passed`, `commands` is `5`, `corpus_records` is `97`, and `unit_tests` equals the completed discovered suite (101 methods in this source). This count is distinct from the 88 source-location content-check records. Test counts come from the completed test summary, not possibly interleaved progress lines. Child CPU and peak RSS are reported as `null` when the platform lacks `getrusage`; missing measurements are not zero-filled.

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
- `data/semantic_readings.csv` - thirteen explicit complete-PDF/seven-field reader assessments, bound to the exact source and coded values; software checks their identity and counts, not understanding.
- `data/recoding_transitions.csv` - eighty-two dated bindings from unchanged historical ceiling rechecks to located current recodings; historical recheck rows are not rewritten to match current conclusions.
- `data/screening_ledger.csv` - 105 retained and excluded screening decisions.
- `data/synthesis_claims.csv` - seven synthesis rules with supporting sources, counter-histories, and boundaries.
- `claim_evidence_ledger.csv` - 27 material paper/artifact claims and their evidence paths.

The retained corpus has 76 primary/empirical/system works and 21 review/method works. Seventy-four primary/system works and 93 works overall have venue publication evidence. Legacy reading-depth labels are 61 full-or-selected-source and 36 publisher-abstract-or-selected-source records. Content-status entries cover 88 works: 3 selected and 85 complete-scoped locator records. The separate reader ledger records 13/97 complete seven-field codings, including DroidMOSS, LibID and the retrieved RepDetector author manuscript. A further 72 acquired PDFs remain pending semantic coding; 12 records have no acquired PDF through attempted legal routes, although some have selected HTML readings. Nine records lack the locator check. The 85 source-byte-bound field tables distinguish the thirteen assessed records from provisional interpretations. The 21-row review matrix has 63 located direct/partial cells, eleven scoped absences and 73 unresolved cells; its direct all-dimension coverage is undetermined. The TPL review's partial component-authorization and stage-limit coverage is not release-history coverage. AStRA's v2 future-work AI discussion is partial treatment; its expanded 2026 final text is not silently certified. Williams et al. provide direct AI supply-chain treatment but no Android repackaging treatment within their complete published scope.

## What the checks establish

The selected ten-row manuscript matrix consumes `paper/generated/review_matrix_rows.tex`.
Its generator requires exactly one row for each displayed key in a declared
order and preserves all seven `0/P/1/?` cells. Six portable regressions in
`tests/test_render_tables.py` compare a named literal fixture and an independent
scan reference, exercise every selected cell/code, container permutations,
missing/duplicate keys, and failed-corpus admission. They run in the existing
discovered suite and scientific workflow; they validate display traceability,
not the coded interpretation of a publication. The literal display fixture follows the coded cells; formatting tests do not validate source interpretation.

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

Most retained results under `results/` describe earlier offline runs. The exceptions are `paper_build_evidence.json`, `visual-inspection.json`, and the six default `tex/` fragments, which mirror the current owned 38-page manuscript build and its source-bound inputs. A new `--out` run produces separate summaries, raw command logs and `tex/` fragments; historical CPU/RSS must not be attributed to that new run. The visual-evidence regression compares the current snapshot receipt, result mirrors, active source/PDF/log and dynamic content-check counts; it does not certify source interpretation.

`manuscript_snapshot/` mirrors the current sibling `paper/` source, 38-page PDF,
final engine log, compiled bibliography, build evidence and directly inspected
180-dpi visual receipt. The local budget is 39 pages, not a certified CSUR cap.
The sibling `paper/` remains the primary source; the snapshot is an artifact-only
delivery mirror, not a second compilation. Earlier evidence is retained privately.

When this directory is the repository root, `.github/workflows/scientific-checks.yml` is configured to run these owned offline checks on Ubuntu 24.04 and upload raw output even on failure; that configuration does not establish a current CI execution. The retained local Windows run in `results/current/` records the earlier 61-test suite; its timing and platform details remain historical. The current source suite has 101 tests; its fresh run is separate from retained raw results. The retained runs show all 97 corpus records passing their consistency checks, and 19,683 ternary matrices plus 262,144 binary completions have no oracle disagreement. Regenerated fragments describe current coded inputs, not search completeness or independent source interpretation.

## Located coding and reading boundaries

The `reading_scope` field in `data/source_readings.csv` uses
`retrieved_pdf_locator_binding`: it identifies an acquired PDF and bounded
locators, rather than asserting a completed semantic reading. The field-binding
tests reject the former completed-reading label. Source-specific interpretation
requires the separately documented literature reading and coding.

`data/field_evidence.csv` contains 595 located field bindings for 85 retrieved PDFs. Each coded value is bound to its extraction, primary URL, source bytes and physical pages, with source reports separated from analytical classifications. The completed-reading subset is declared separately in `data/semantic_readings.csv`; the remaining interpretations are provisional. Twelve records lack supplementary seven-field bindings. The RepDetector record uses the 17-page PSU author manuscript rather than treating an earlier selected HTML reading as the same representation. AppForge v1 has 21 physical pages; extracted figure control characters do not change that count. Retrieved copies and final publications retain their stated version distinctions. No copyrighted primary PDFs are bundled.

The audit rejects extraction/locator disagreement, conflicting source URLs, missing or duplicate fields, stale coded values, and out-of-range physical pages. Reader assessments must match the exact source and the seven coded values; changing either requires reassessment. Historical-to-current transitions bind the unchanged older recheck to its later source and ceiling. The generated summaries retain the 595/679 field denominator and `semantic_interpretation_verified_by_code=false`. Software checks declarations and calculations; the reading judgments remain same-process assessments. Fresh fragments are generated before rebuilding the primary manuscript, then its exact PDF, source and visual evidence are mirrored.
