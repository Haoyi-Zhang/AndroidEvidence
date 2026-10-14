# Evidence boundaries

## Claim levels

- **L0 identity:** the compared bytes or content-addressed object are identical under the stated digest/normalization premise.
- **L1 composition:** a component, family, package, resource, or feature is present under the detector's model.
- **L2 resemblance:** artifacts share measured structure or behavior above a declared criterion.
- **L3 derivation:** one artifact descends from another under a direction-bearing model and evidence.
- **L4 process provenance:** authenticated records bind declared steps, inputs, outputs, and environment.
- **L5 authorization:** a principal was entitled under a specific policy, scope, and time to perform or release the action.
- **L6 behavioral assurance:** a stated behavioral property holds under an explicit analysis or execution model.

These are claim ceilings, not a universal total order of detector quality. A mechanism may support several incomparable subclaims, and stronger evidence at one layer does not numerically substitute for another.

## Required non-substitutions

- Similarity does not establish derivation direction without chronology, source, ownership, authenticated process, or another direction-bearing premise.
- Component presence does not establish application ancestry, exact version, reachability, or exploitability.
- A valid signature establishes cryptographic verification under a key, not automatically release authorization under the relevant policy.
- Reproducible output establishes equality under declared inputs and environment, not approval of those inputs or benign behavior.
- Provenance can authenticate a process statement yet still record a compromised or under-specified process. Trusted in-toto inspections and rebuilders add only the properties they actually check; metadata authentication alone does not establish those properties.
- A generation log may omit retrieval state, hidden tool context, rejected outputs, manual edits, and model drift.
- Behavioral evidence must name the property, environment, oracle, and temporal scope; it does not retroactively prove lineage.

## Current evidence map

The active map contains 97 works: 76 primary/empirical/system and 21 review/method records. It includes 97 claim-level extractions, direct locators, source-location rows, retrospective provenance rows and publication-status rows; a 21-row review matrix; and 90 unchanged cumulative same-process rechecks. Eighty-two ceiling recodings have transitions from those historical rows. Legacy depth labels remain 61 full-or-selected-source and 36 publisher-abstract-or-selected-source. The locator ledger covers 88 works (three selected HTML readings and 85 complete-scoped PDF rows); nine lack a current locator check. The separate reader ledger contains 85 complete retrieved-PDF/seven-field assessments, with 595/679 located fields. Twelve records have no acquired PDF through attempted routes. The matrix contains 73 direct/partial cells, 27 scoped absences and 47 unknown cells; direct all-dimension coverage remains undetermined. Retrieved author/preprint and canonical final-publication versions retain their stated distinctions.

The checked passages support a bounded mechanism analysis; populated legacy rows do not independently verify the full 97-record synthesis. They do not support an exhaustive census, PRISMA denominator, prevalence estimate, pooled accuracy estimate, independent coding claim, or worldwide novelty proof.

## Publication-status boundary

One withdrawn SBOM review is excluded from the active corpus and bibliography. Its official withdrawal state is retained in `excluded_publications.csv`. The older 16-record pilot preserves the withdrawn record only as a historical regression fixture so that the audit can verify exclusion and conservative unknown-handling. It is not active evidence and does not govern the 97-work manuscript.

All active records have checked scholarly or official locators and status/type consistency, but the project did not perform a comprehensive search of every retraction registry. The publication-status ledger must therefore be read as record-level verification, not a global guarantee.

## Code and finite-check boundary

The code validates deterministic ledgers, key equality, counts, status constraints, mutation controls, and finite matrix semantics. It cannot decide whether a paper's argument was interpreted correctly, whether a search is exhaustive, or whether the synthesis is novel. The exhaustive 3x3 oracle covers exactly 19,683 ternary matrices and 262,144 consistent completion visits; it is not a proof for arbitrary dimensions unless the underlying formula is separately justified.

## Security boundary

The project uses defensive static/formal reasoning and bibliographic evidence only. It does not execute malware, probe third-party services, reproduce exploits, generate attack code, or autonomously test real systems.
