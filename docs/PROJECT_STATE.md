# Project state

Updated: 2026-10-16 UTC (2026-10-15 in Fortaleza).
Scope: implementation modernization preserving the published technique.

## Completed in stage 0

- Private separate repository; canonical name is `tiagosombrra/apmesh-modernization`.
- Exact 513-blob publication import at `cbfb863fb014e798289d824e158f67922036a5e3`.
- Source commit and tree pinned; licenses, citation and historical README kept.
- Initial audit, validation status and unapplied candidate patch retained.
- English working agreement and complete stages 0–11 plan.
- EditorConfig, clang-format/tidy configurations, explicit local quality commands,
  optional staged-byte hook, CMake presets and meaningful CTest registration.
- Compatibility-report checker rejects empty or zero-comparison coverage.

## Delivery status

Stage 0 implementation is complete and locally validated. Publication and
integration are tracked in GitHub PR #1. See
`docs/evidence/BOOTSTRAP_VALIDATION.md` for executed checks and limitations.
No automatic hosted workflows or paid Actions have been created.

## Active work item: stage 1 (draft; integration blocked)

Issue #2 tracks the candidate delivery. Main remains at
`b4087a472015d6898687c0aeff444efb4f1a9524`; these stage 1 changes are not integrated.

Implemented: strict configuration syntax/numeric checks, pre-allocation BP
grammar validation, English CLI error diagnostics, independent OBJ/CSV/log
verification, rejection of historical targets without accepted-state evidence,
strict before/after comparisons and exact-configuration repeatability tooling.

Executed: GCC serial build, 38 Python controls, 23 real invalid-input controls,
three valid shipped model grammars, six valid configuration controls and CTest
5/5. New C++ header/probe formatting and consumer clang-tidy passed.

Numerical root cause proved: EdgeSet orders Edge* addresses, so identical
Laplacian inputs were summed in different orders. A full-precision trace found
5,685 different sums with otherwise identical inputs in 424,144 aligned vertex
visits. The draft now sorts adjacency by unique edge ID and rejects ambiguous
IDs. This is a behavior-changing defect repair, not a numerical-neutral refactor.
Formulas, weights, thresholds, vertex iteration, quality checks and acceptance
policy remain unchanged. No tolerance was relaxed.

Strict Eistute/Book candidate repetitions pass: 5/4 identical OBJ files and all
CSV/decision fields equal. The controlled reference (main plus only the same
smoothing-order repair) also repeats exactly for Eistute and compares exactly
with the input-validation candidate for both cases. Last accepted stage remains
1: Eistute 1,168 triangles, Book 4,418. Original-reference Eistute comparison
still fails in 43 fields and remains recorded; Book remains exact. See
`docs/evidence/STAGE1_SMOOTHING_ORDER.md` and its source/executable manifests.

Next action: export and independently check every shared-boundary incidence,
including reversed orientations and non-manifold sheets. Keep draft PR #3 and
main unchanged until that gate and the declared regression checks pass.

Per-incidence boundary validation also remains open: legacy OBJ lacks patch
incidence labels, and synchronized legacy reports compare zero curve groups.
The new verifier explicitly reports absent incidence coverage and fails the
strict boundary-coverage request, even if a legacy group summary is measured.
Do not mark stage 1 complete or begin stage 2 while this work item is open.

## Open blockers and limitations

- Main still has the historical input/verifier and pointer-order defects. The
  draft repairs them; integration is blocked by missing boundary incidence proof.
- Compatibility instrumentation may record zero compared groups; the new checker
  rejects such a report but does not repair the instrumentation itself.
- Ownership findings, timers, duplicate mesh representations, VLAs and warning
  debt remain. No full-application leak-free claim is justified.
- Eigen remains; CRABMesh consolidation, complete English renaming, generated
  Doxygen review, C++23 qualification and performance work remain open.
- The archived-artifact test is not a new accepted-mesh generation experiment.
- Local Git network access cannot resolve github.com; remote operations use the
  GitHub connector. Local source validation excludes the two binary publication
  artifacts; their remote import hashes are independently compared with source.

## Continuation rule

One work item at a time. Every delivery records scope, reviewed changes,
executed checks, toolchain, failures and next step. Recheck remote authority
before writing and after integration. Scientific algorithm changes wait for
explicit advisor alignment.
