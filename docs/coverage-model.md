# Conservative coverage accounting

## Object and interpretation
A row is one selected review and a column is one explicitly defined obligation. Each cell is 1 (a located substantive passage supports coverage), 0 (a complete scoped reading supports absence), or ? (unresolved). Current data contain no 0 cells. A 1 is a coding judgment, not a claim that a review exhausts a topic. Abstracts identify candidate scope only; they cannot establish a body-positive or an absence cell in this artifact.

Direct coverage is the existence of a row covering every encoded column. Pointwise mosaic coverage is the existence of at least one supporting row for each column. Neither predicate proves an integrated argument connecting the columns. In particular, a causal-provenance review and an Android-identification review can cover separate coarse topics without synthesizing evidence transfer between them. O7 therefore asks for that joint obligation explicitly. Its coverage is unknown, not absent.

The selected review set is not the universe of publications. A finite-matrix gap would not prove worldwide novelty even if every encoded decision were correct. A covered matrix is an adversarial check against novelty claimed merely from combining topic headings.

## Bound proposition and complete argument
Let C be any nonempty finite rectangular matrix over {0,1,?}. A completion B replaces each ? independently by 0 or 1 while retaining every known cell. Write C- for the all-zero replacement and C+ for the all-one replacement. Order Boolean matrices coordinatewise.

Define D(B) = OR_i AND_j B[i,j] and M(B) = AND_j OR_i B[i,j].

For either F in {D,M}, its value over all completions is fully characterized by F(C-) and F(C+):
- (1,1): every completion is covered;
- (0,0): every completion lacks encoded coverage;
- (0,1): coverage is undetermined by the current cells.

Proof. Every completion satisfies C- <= B <= C+. A conjunction and a disjunction of Boolean coordinates are monotone; compositions of these operations are monotone. Consequently F(C-) <= F(B) <= F(C+). Equal endpoint values force all completions to have that value. Unequal endpoints are themselves attained because C- and C+ are legal completions. Thus both outcomes occur and neither a coverage nor an absence claim is determined. The fourth pair (1,0) is impossible. This proves both the soundness and the completeness of the endpoint classification for this finite bookkeeping model.

Assumptions matter. Unknown cells are unconstrained Boolean variables; semantic dependencies among coverage judgments are not modeled. Additional justified constraints could exclude an endpoint, requiring a different procedure. Source correctness, search completeness, equivalence of obligations and scientific originality are outside this proposition. The argument is elementary monotonicity, not a new research theorem.

## Cost and exact finite check
Endpoint classification takes O(m*n) work and O(m*n) storage in the supplied implementation. A diagnostic smallest known-cover witness enumerates row subsets in increasing cardinality, at most 2^m, and is explicitly limited to 16 rows. It is not needed to classify coverage and does not solve literature selection generally. The current largest eligible matrix has 11 rows and 7 columns.

A separately implemented finite oracle enumerates all 3^9 ternary 3-by-3 matrices and every consistent binary completion. Its direct predicate counts complete rows; its mosaic predicate counts nonempty columns. It does not call the classifier's Boolean predicate or endpoint status function. There are 19,683 matrices and 4^9 = 262,144 completion visits: per coordinate, the three ternary symbols contribute 1+1+2 possible completions. These are visits across inputs, not distinct Boolean 3-by-3 matrices. There are only 2^9 distinct Boolean matrices. The observed comparison found zero mismatches.

The two implementations check the stated finite domain. Their agreement is not a mechanized proof for arbitrary dimensions or independent validation of the source coding. The mathematical argument above supplies the general finite-model justification.

## Benign negative controls
A completely covering row must block a direct-gap conclusion. Disjoint supporting rows may establish a mosaic without a direct cover. A single unknown must not behave like a known absence. Ledger checks preserve an active preprint as unknown at the historical pilot boundary, reject abstract-only promotion to body coverage, reject undocumented promotion into a peer-reviewed main corpus, reject duplicated identities, and reject disappearance of completed rechecks. These controls do not test detectors, malware, generated applications or security vulnerabilities.
