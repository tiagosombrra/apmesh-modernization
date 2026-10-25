# Attempt metric export and domain input repair

Classification: engineering-only output correction. Base main is
`a936323569875cce070879d367d6e7ec123eb868`. The first candidate was blocked by full
generator static analysis; the measured resolution is recorded below. This is
not another qualified memory slice or stage closure. Prior slice-37 qualification
remains bounded by its own evidence.

## Defect and implementation

`WriteQualityMesh` indexed accepted-history vectors by attempted step. Rejected
steps do not append to those vectors, so exports substituted growth 1, score 0,
zero curvature counts/retry, configured base rates and, after consecutive
rejections, the candidate element count as its own previous count. Both CSV and
quality log shared this defect, so their existing schema cross-check passed.

`MeshAttemptMetrics` carries explicit current/reference/initial errors, reference
element count, error drop per element, growth, score, curvature counts, retry and
applied rates through `SaveMesh` to the actual exporter. Curvature counts reset
for reporting at each retry and are captured only after error evaluation, so an
unevaluated rejected retry cannot inherit prior counts. Existing algorithm state,
history appends, formulas and decisions retain their original timing and values.
Other control columns keep their existing current-attempt/history handling.

This changes the public helper signatures of `SaveMesh` and `WriteQualityMesh`.
All repository callers are updated; external clients are not qualified. No
parallel, whole-process memory, LSan, UBSan, performance or mesh-quality
improvement claim follows. Numerical error itself is not independently recomputed
by the new report auditor.

## Functional evidence before publication

Retained generation source is main `e81eb804eb67599e47c1068069f602c7dd231da9`,
full campaign report SHA-256
`3899238fe3b66bc930780a17b158562b67403b7f05ce993cbd995278927eda74`.
Its executable SHA-256 is
`4abd3d98869d65653e6360bec8e63912976006468ce099290c2e88540942545f`.
The stronger attempt oracle fails on all five original rejected states: 52
differing observations across CSV and quality log, representing the 26 CSV values
previously confirmed against mesh counts/accepted reference/native score.

Actual production exporter controls pass eight cases with 132 candidate-field
checks: initial, acceptance, two consecutive rejections, later acceptance, a
rejected retry without curvature evaluation and zero-initial-error exports.
Seven independent checker controls include mutually wrong CSV/log growth,
rejected-as-previous state, wrong score, nonfinite values, missing/duplicate rows
and duplicate named analysis fields. The full Python tooling inventory passes
81 controls after refreshing the changed source/build hashes in the architecture
inventory. Both focused CTest metric entries pass.

The preliminary Eistute/Book executions preserve 43 mesh/incidence/decision/
adaptation artifact files exactly, covering all nine attempted states. Four
accepted CSV rows are unchanged. The only changed CSV values are 36 Eistute and
20 Book values in rejected rows, within these fourteen named fields:
`elements_prev`, `elements_delta`, `element_growth_factor`,
`actual_element_growth`, `actual_growth_step`, `acceptance_score`,
`error_improvement_per_element`, `gauss_nodes`, `mean_nodes`, `gauss_ratio`,
`mean_ratio`, `retry_attempt`, `adaptation_relaxation`, `adaptation_max_delta`.
Quality logs change only the corresponding named values. Independent mesh-count/
last-accepted-reference/native-score checks pass all 144 observations.

Local evidence is under `build/s38-attempt-metrics/`. Complete exact-head checks
and hashes belong to the PR validation record and `head/report.json`; the
prepublication observations above do not claim an exact-head full gate pass.

## Historical failing gate and retained preparation failures

Full generator clang-tidy exits 1 on both original and candidate: one possible
null geometry dereference, five dead stores and two `nullptr` modernization
diagnostics. The diagnostic messages, checks, source lines and multiplicities
match. Both raw logs and `lint-comparison.json` remain preserved. Equal baseline
debt did not make this gate pass; the first candidate remained blocked under the
repository working agreement. The resolution does not suppress diagnostics.

The first 56-entry CTest run failed the retained-inventory comparison because
source/build hashes had changed. The inventory was refreshed without changing
contracts or weakening the assertion; the 81 tooling controls then passed.
Two test-parser preparation failures are also retained: repeated histogram
labels were initially treated as duplicate metric keys, and the quality log's
combined step/rank line was initially parsed as one number. They were corrected
by selecting the intended named fields. None counts as production validation.

## Resolution of the eight diagnostics

`AdaptDomain` now throws `std::invalid_argument` for null geometry or mesh before
changing state. Four final assignments to unused factor/size locals are removed;
their values were not subsequently consumed. Two pointer initializers use
`nullptr`. The one-argument legacy `SaveErrorMesh` writes
`submesh_curvature_error[index]` after its existing normalization, making the
previously discarded result observable. No arithmetic expression or evaluation
order is removed or changed. Classification: behavior-changing invalid-input
repair plus engineering-only output/cleanup. All other generator source is
preserved by an exact, enumerated delta comparison against `a7786ab`.

Actual production controls reject null geometry, null mesh and both null without
changing a populated mesh. Curved and planar Hermite controls generate five nodes
and four triangles each, then call the initialized legacy writer. Independent
closed-form Gaussian curvature and angle-deficit/area calculations verify the
new normalized summary: approximately 0.200671 and exactly zero respectively.
Three deliberately corrupted reports (wrong zero, nonfinite and missing summary)
are rejected. Original generator objects linked with the same fixture reproduce
two null-geometry access violations, the missing null-mesh exception, and both
missing-summary failures. Legacy node logs and fixture values match exactly after
removing only the newly added summary line.

An initial exact-physical-point analytic assertion failed and remains retained.
The unchanged Hermite inverse recovers approximate corner parameters under the
default tolerance: the curved control's maximum spatial residual is about
0.00200319, and corner Gaussian curvature is about -395.536 rather than the exact
corner value -400. The final oracle evaluates the independent closed form at the
actual recovered parameters, explicitly limiting its claim to the writer's
existing input semantics. No inverse/tolerance repair or exact-point curvature
qualification is claimed. The flat control remains analytic zero.

Full generator and fixture clang-tidy now pass with the existing checks and
warnings-as-errors. Local evidence is under `build/s38-lint-resolution/`;
`source-review.json`, `original-link.json`, `original-controls/report.json` and
the positive diagnostic reports retain identities and limits. Complete exact
review-head and post-merge commands, results and report hashes are recorded in
the PR #102 validation record and `head/report.json` / `main/report.json`.

## Required delivery checks

Run on the exact review revision: C++17 build; 57-entry CTest with zero failures/
skips; whitespace, explicit changed-line formatting, inventory and full generator
lint of the generator and its fixture; actual diagnostic controls and their
negative controls; twice-repeated unmodified article configurations for Eistute and Book;
independent attempt/schema audits, strict artifact comparison and an explicit
fourteen-field rejected-row change list. Require all CSV metrics to match the
previous functional candidate `a7786ab`. Audit remote main/branches/open PRs and
checks before publication. Do not merge while a required gate fails. A further
complete memory campaign is not justified by this reporting-only delta.

Once integrated, investigate Book's boundary/interior transition under its fixed
`research_debug` configuration. The observed concentration of poor elements at
patch boundaries does not yet establish a generator defect or justify changing
fallback, acceptance, budgets, tolerances or stopping policies.
