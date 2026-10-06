# Review protocol

## Review question

Which observable evidence supports which Android software-lineage or assurance claim, under what transformation and trust assumptions, when applications include third-party components and AI-mediated changes?

## Review form

This is a bounded claim-centered structured evidence synthesis with a closest-review adversary matrix. It is not described as PRISMA-complete because the retained-record provenance was reconstructed retrospectively and no complete database-search result denominator is available.

## Search and discovery

Discovery combined the historical RePack review, backward and forward scholarly snowballing, targeted searches across Android repackaging, third-party libraries, supply-chain provenance and assurance, SBOMs, reproducible builds and transparency, and AI-mediated development/security. `search_slices.csv` records the major search slices. `search_provenance.csv` records a discovery route for every retained item and explicitly labels that trace retrospective.

`screening_ledger.csv` contains 105 retained and excluded decisions. Inclusion requires a software-artifact lineage, component, process, authorization, behavioral, review-method, or directly relevant AI-mediated evidence object. General LLM or GUI-agent work without a software-artifact lineage object is excluded. Withdrawn or retracted records cannot enter the active corpus.

## Corpus obligations

The frozen active corpus has 97 works: 76 primary/empirical/system and 21 review/method. Seventy-four primary/system records and 93 records overall have venue publication evidence. The active set includes three explicitly typed preprints and one technical method report. It satisfies the planned 60-140 primary/system range and at least 12 closest review/method works.

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

Every retained work is coded once in `study_extractions.csv` using:

`(object, observation, transformation model, oracle or policy, claim ceiling, counter-history, inference limit)`.

Claim levels are L0 identity, L1 composition, L2 resemblance, L3 derivation, L4 process provenance, L5 authorization, and L6 behavioral assurance. Reading depth is recorded as either full-or-selected-source (61 records) or publisher-abstract-or-selected-source (36 records). The lighter category is not represented as cover-to-cover full-text coding.

## Closest-review adversary matrix

Twenty-one review or method records are coded across seven dimensions: Android repackaging, component/version evidence, process provenance, authorization, behavioral assurance, AI-mediated development, and an explicit claim-ceiling/cross-layer binding rule. These are the seven columns of `review_gap_matrix.csv`; transformation models are separately retained in the claim-level extractions. A direct-coverage value is assigned only when the source itself substantively covers the dimension. No retained row directly covers all seven dimensions under one uniform observation-to-claim and binding rule. This supports bounded positioning only.

## Source-grounded rule rechecks

Twenty-six of 97 high-load assignments (26.8%) have a recorded source-grounded recheck. This is the cumulative dated ledger, not a claim that all 26 were reread during the current repair. The ledger records the prior assignment, inspected location, rule applied, decision, and boundary. Rechecks belong to the same authoring process; they are not independent dual coding, and no agreement statistic is reported.

## Writing calibration

`calibration_papers.csv` contains 22 papers at full-or-selected-source depth: 12 closest papers, five influential/method papers, and five adjacent evidence papers. It records explanatory and evidence-organization patterns only; wording, claims, and paper-specific structure are not reused.

## Synthesis rule

No observation is promoted above the proposition directly observed under its assumptions. Counter-histories remain explicit. Cross-study performance is not pooled across incompatible labels, candidate populations, transformation models, time cuts, and counting units.

## Reproduction and negative controls

The artifact checks all one-to-one ledger bindings, publication-status constraints, calibration obligations, screening and recheck coverage, synthesis sources, and manuscript-facing counts. Mutation tests require reproduction to fail when a withdrawn status enters the active ledger, a canonical identifier duplicates, an excluded key leaks, title/year/DOI data drift, publication status mismatches, or calibration group counts change.

The historical 16-record gap pilot and exhaustive 3x3 completion oracle remain regression fixtures. They validate unknown-handling and implementation bookkeeping; they do not establish the manuscript's novelty or substantive conclusions.
