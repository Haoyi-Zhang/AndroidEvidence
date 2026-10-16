# Review protocol

## Review question

Which observable evidence supports which Android software-lineage or assurance claim, under what transformation and trust assumptions, when applications include third-party components and AI-mediated changes?

## Review form

This is a bounded claim-centered structured evidence synthesis with a closest-review adversary matrix. It is not described as PRISMA-complete because the retained-record provenance was reconstructed retrospectively and no complete database-search result denominator is available.

## Search and discovery

Discovery combined the historical RePack review, backward and forward scholarly snowballing, targeted searches across Android repackaging, third-party libraries, supply-chain provenance and assurance, SBOMs, reproducible builds and transparency, and AI-mediated development/security. `search_slices.csv` records the major search slices. `search_provenance.csv` records a discovery route for every retained item and explicitly labels that trace retrospective.

`screening_ledger.csv` contains 105 retained and excluded decisions. Inclusion requires a software-artifact lineage, component, process, authorization, behavioral, review-method, or directly relevant AI-mediated evidence object. General LLM or GUI-agent work without a software-artifact lineage object is excluded. Withdrawn or retracted records cannot enter the active corpus.

## Corpus obligations

The frozen active corpus has 97 works: 76 primary/empirical/system and 21 review/method. Seventy-four primary/system records and 93 records overall have venue publication evidence. The active set includes three explicitly typed preprints and one technical method report.

## Publication and bibliographic integrity

Each active work has a one-to-one row in `bibliography_verification.csv`. The audit requires:

- exact corpus/BibTeX title and year agreement after conservative normalization;
- publication type agreement between corpus and BibTeX;
- a unique canonical identifier and HTTPS scholarly or official locator;
- canonical `doi:` identifiers and `https://doi.org/` URLs for all 82 DOI records;
- no withdrawn or retracted language in the active ledger;
- exact exclusion of keys in `excluded_publications.csv`.

This is a record-level locator/version check, not a comprehensive retraction-registry search. Consumed reading representations remain separate in `source_locations.csv`; for example, a venue record can be canonical while an author manuscript or preprint was the inspected representation.

## Extraction and coding

Every retained work has a row in `study_extractions.csv`: evidence object, observation, transformation model, oracle or policy, claim ceiling, counter-history and inference limit. Source reports and survey classifications are distinguished. Claim levels are L0 identity, L1 composition, L2 resemblance, L3 derivation, L4 process provenance, L5 authorization and L6 behavioral assurance.

The acquired set contains 85 exact retrieved PDFs, each with a complete retrieved-representation/seven-field assessment in `semantic_readings.csv`. Twelve records lack an acquired PDF through attempted routes; some retain selected primary-HTML readings. Legacy reading-depth labels (61 full-or-selected-source and 36 abstract-or-selected-source) remain historical labels, separate from semantic assessments. The locator ledger contains 88 checks: 85 complete-scoped PDF locator rows and three selected HTML readings; nine records lack a current locator check.

## Closest-review adversary matrix

The 21 review/method records are compared across Android repackaging, component/version evidence, production provenance, authorization, behavior, AI-mediated workflows and explicit claim-ceiling/cross-layer binding. Codes are 1 for direct treatment, P for partial treatment, 0 for absence grounded in complete scoped reading, and ? for unresolved coverage.

The matrix contains 75 direct/partial cells, 41 scoped absences and 31 unresolved cells. Eighteen records have content checks. Brereton's seven cells await representation-aware admission; 24 other cells remain unresolved: seven each for Sufatrio, Ohm-Stuke and Reichert, and three for Wu. The three unchecked review records can still supply an all-dimension witness, so direct coverage remains undetermined.

Sixteen matrix decisions reuse existing complete-PDF assessments: two scoped zeros for TPL process provenance and AI-mediated workflows, and six scoped zeros plus partial ceiling treatment each for Wohlin and Kitchenham. TPL's August 2021 author version covers component privileges and stage limits, not authenticated build histories or generative-assistant changes. Wohlin's ten-page EASE 2014 representation bounds citation-cluster discovery and replication inferences (PDF pp. 3, 5, 7-10). Kitchenham's July 2004 report distinguishes unknown conduct, duplicate reports and incomparable outcomes, and leaves cross-study-type aggregation unsolved (PDF pp. 21-25, 30). Their method-level ceilings are partial antecedents, not integrated artifact/principal/policy bindings. The matrix supplies per-dimension page locators and reasons; `source_readings.csv` and `semantic_readings.csv` retain the exact versions and complete-reading declarations. This matrix coding adds no acquired source, seven-field assessment or independent coder.

AStRA v2 discusses AI-generated software prospectively, while Williams et al. directly discuss generation workflows. Xu et al.'s update-actor flow is partial lifecycle context, not an authenticated build chain. Codes apply to inspected representations, with selected HTML readings kept separate from complete-PDF absence evidence.

## Source-grounded rule rechecks

Ninety of 97 assignments (92.8%) have cumulative dated recheck entries. The current content ledger checks 88 works; the other two recheck entries retain historical or non-paper readings. The cumulative total is not a new 90-source reading pass or independent verification. The dated historical ledger is unchanged; `recoding_transitions.csv` binds eighty-two historical ceilings to their new located recodings and source bytes. Other historical ceiling drift still fails. Rechecks belong to the same authoring process; they are not independent dual coding, and no agreement statistic is reported.

## Synthesis rule

No observation is promoted above the proposition directly observed under its assumptions. Counter-histories remain explicit. Cross-study performance is not pooled across incompatible labels, candidate populations, transformation models, time cuts, and counting units.

## Reproduction and negative controls

The artifact checks ledger bindings, publication-status constraints, screening and recheck coverage, synthesis sources, located coding fields, and manuscript-facing counts. Mutation tests require reproduction to fail when a withdrawn status enters the active ledger, a canonical identifier duplicates, an excluded key leaks, title/year/DOI data drift, publication status mismatches, or a checked extraction/field binding changes without updating its evidence.

The historical 16-record gap pilot and exhaustive 3x3 completion oracle remain regression fixtures. They validate unknown-handling and implementation bookkeeping; they do not establish the manuscript's novelty or substantive conclusions.

## Field-level source bindings

`source_readings.csv` identifies 85 acquired representations with exact source bytes, physical page counts, dates and version boundaries. Its `retrieved_pdf_locator_binding` scope does not itself assert understanding. `semantic_readings.csv` separately records the 85 complete retrieved-PDF/seven-field assessments. `field_evidence.csv` supplies 595/679 located fields; twelve records remain outside that supplement. Physical page numbers refer to PDF pages, not extracted figure control characters.

Complete reading applies to the retrieved body, references and included appendices, not linked material or an uncompared final publication. Author/preprint and canonical publication identities stay separate, including the MaMaDroid 2019 extension, Contour extended v2, AppForge v1 and Gokkaya's differently titled 2023 v1. No copyrighted primary PDFs are bundled.

OpenAI Codex assisted source reading, coding, matrix review, tests and exposition. Same-process assessments and selected-passage cross-checks are not independent second-human coding; no human agreement statistic is reported. Software checks declared source/field identities and arithmetic, not semantic understanding. Cumulative historical rechecks, acquisition, current semantic assessments and independent coding are distinct denominators.

Kitchenham's Sections 5.1.3 and 5.4 recommend retrieval logs, piloted extraction and independent or sampled checks; its Section 7 leaves cross-study-type aggregation unresolved. Wohlin's Sections 3 and 4.9 distinguish seed inclusion, citation context and missed independent clusters. These are inherited method obligations, not a novel survey procedure or certification that this retrospective map satisfies independent coding or exhaustive discovery. Unreported conduct remains unknown, rather than being automatically coded absent.
