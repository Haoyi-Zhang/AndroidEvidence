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

Every retained work is coded once in `study_extractions.csv` using:

`(object, observation, transformation model, oracle or policy, claim ceiling, counter-history, inference limit)`.

Claim levels are L0 identity, L1 composition, L2 resemblance, L3 derivation, L4 process provenance, L5 authorization, and L6 behavioral assurance. Legacy reading depth is recorded as full-or-selected-source (61 records) or publisher-abstract-or-selected-source (36 records). These labels are not substantive content certificates. The source-location ledger separately identifies 88 content checks: 4 selected readings and 84 complete scoped readings, each with actual PDF pages/sections or numbered primary-HTML sections. Nine legacy records remain not reverified. All 84 complete-scoped records now have source-byte-bound seven-field recodings. Selected reading is not cover-to-cover.

## Closest-review adversary matrix

Twenty-one review or method records are coded across seven dimensions: Android repackaging, component/version evidence, process provenance, authorization, behavioral assurance, AI-mediated development, and an explicit claim-ceiling/cross-layer binding rule. These are the seven columns of `review_gap_matrix.csv`; transformation models are separately retained in the claim-level extractions. A direct-coverage value is assigned only when the source substantively covers the dimension. Located readings justify 63 direct/partial cells and eleven scoped absences. Eighteen records have content checks, including four method records whose coverage remains unresolved; three records are not substantively reverified. The TPL review's component privilege policies and stage-specific limits warrant partial U/X coverage, not release-authority or complete cross-layer coverage. AStRA v2 supplies a partial AI future-work discussion, not final-version certification. Williams et al.'s published scope covers LLM supply chains but not Android repackaging. There are 73 unknown cells. Direct all-dimension coverage is undetermined, so the matrix establishes no retained-set gap.

## Source-grounded rule rechecks

Ninety of 97 assignments (92.8%) have cumulative dated recheck entries. The current content ledger checks 88 works; the other two recheck entries retain historical or non-paper readings. The cumulative total is not a new 90-source reading pass or independent verification. The dated historical ledger is unchanged; `recoding_transitions.csv` binds eighty-two historical ceilings to their new located recodings and source bytes. Other historical ceiling drift still fails. Rechecks belong to the same authoring process; they are not independent dual coding, and no agreement statistic is reported.

## Synthesis rule

No observation is promoted above the proposition directly observed under its assumptions. Counter-histories remain explicit. Cross-study performance is not pooled across incompatible labels, candidate populations, transformation models, time cuts, and counting units.

## Reproduction and negative controls

The artifact checks ledger bindings, publication-status constraints, screening and recheck coverage, synthesis sources, located coding fields, and manuscript-facing counts. Mutation tests require reproduction to fail when a withdrawn status enters the active ledger, a canonical identifier duplicates, an excluded key leaks, title/year/DOI data drift, publication status mismatches, or a checked extraction/field binding changes without updating its evidence.

The historical 16-record gap pilot and exhaustive 3x3 completion oracle remain regression fixtures. They validate unknown-handling and implementation bookkeeping; they do not establish the manuscript's novelty or substantive conclusions.

## Field-level source bindings

Eighty-four retrieved PDFs were read completely, including their references and included appendices: RePack (18 pages), LibScout (12), the TPL review (32), secure-design-properties SoK (10), TUF (12), in-toto (19), CHAINIAC (19), Text2App v2 (10), Wohlin (10), Kitchenham's 2004 report (33), AStRA v2 (18), FlowDroid (11), Diplomat (16 including the USENIX cover), Reproducible Containers (16), AppForge v1 (21), Williams et al. (38), Reproducible Builds v1 (10), DroidMOSS (10), AdRob (14), LibID (11), the vulnerability-origins v3 draft (34), Sandoval et al. (19), the static-analysis review (32), the Android-testing review (23), the ASE 2020 TPL comparison (12), Ladisa's v2 taxonomy (18), Xu et al.'s ecosystem survey (47), Tam et al.'s accepted manuscript (36), Blackburn et al. (7), DNADroid (18), AppInk (12), CodeMatch (11), DR-Droid (14), DAPASA (14), APPraiser (11), SimiDroid (8), CLANdroid (10), the resource-based evaluation (16), DroidEagle (12), MassVet (17 including the USENIX cover), WuKong (12), AnDarwin (13), the centroid study (12), FSquaDRA (16), ResDroid (10), ViewDroid (12), the longer Juxtapp manuscript (27), Huang et al.'s evaluation framework (18), the common-library investigation v1 (12), LibD (12), LibRadar (4), ORLIS (11), ATVHunter (13), OSSPolice (17), Keep me Updated (14 including questionnaire) and Salza et al.'s library-update study (12-page author draft), AppCommune (11), LibPecker (12), the potentially malicious-library study (11), AndroZoo (4), the plagiarism study (14-page author representation), the Android-market reuse study (10), the piggybacking study (16-page author representation), DroidChameleon (6), DREBIN (15), MaMaDroid extended v2 (33, not the final NDSS2017 text), the GitHub CI study (18 including cover) and the package-manager study (10), Duan et al.'s MalOSS study (17), Backstabber's Knife Collection v1 (21), Small World with High Risks (16), Weak Links v2 (10), le-git-imate (14), Contour extended v2 (14, not the final 17-page text), Pearce et al.'s v3 (15), Perry et al.'s v3 (16), Spracklen et al. (21 including cover), Khoury et al.'s April 2026 v2 (7), CodexLeaks (19 including cover), Zeng et al.'s v1 survey (21), Latsiou and Lambrinoudakis (11), Gokkaya et al.'s 2023 v1 (27), Bi et al.'s August 2023 v2 (23) and BOMs Away (13). Claim-critical rendered pages were also inspected. `source_readings.csv` records exact source bytes, physical page counts and versions; seven-field recodings in `field_evidence.csv` distinguish source reports and survey interpretations. This yields 588/679 located fields for 84/97 records, with 13 outside the supplement. The content-status total of 88 combines inherited readings and new recodings, not 88 newly read full texts. OpenAI Codex assisted reading, coding, tests and exposition; no independent human coding is inferred. Retrieval or text extraction alone never promotes reading status. Software validates declared traceability and arithmetic, not semantic understanding. Physical page numbers refer to the PDF, not form-feed segments in extracted figure glyphs.

Kitchenham's Sections 5.1.3 and 5.4 recommend retrieval logs, piloted extraction and independent or sampled checks; its Section 7 leaves cross-study-type aggregation unresolved. Wohlin's Sections 3 and 4.9 distinguish seed inclusion, citation context and missed independent clusters. These are inherited method obligations, not a novel survey procedure or certification that this retrospective map satisfies independent coding or exhaustive discovery. Unreported conduct remains unknown, rather than being automatically coded absent.
