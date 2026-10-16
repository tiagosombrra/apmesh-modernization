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

Executed in the current incidence follow-up: native Windows GCC 16.1.0 serial
C++17 build PASS; 65 Python controls and 23 executable invalid-input controls
PASS. New exporter/header format PASS. Full CTest is **5 passed, 2 failed,
0 skipped**; the two new required application gates expose pre-existing defects.
Selected exporter clang-tidy also fails on 18 existing included legacy/Eigen
header diagnostics; no suppressions or vendor edits were applied.

The prior pointer-ordered Laplacian defect is repaired and remains documented
as a behavior-changing defect repair. Current article repetitions preserve every
OBJ, CSV/acceptance field and incidence snapshot exactly. Before/after comparison
against the previous candidate preserves every old artifact/decision field.
The original-reference numerical failures remain recorded.

Per-incidence observation is now implemented: all 16 Eistute / 112 Book patch
sides are checked in each of their 5 / 4 attempted states, including rejected
candidates. Shared non-manifold curves have 4 / 28 sheets, with 3 / 27 independent
comparisons per state and zero observed shared-position gap. Last accepted stage
remains 1: Eistute 1,168 triangles; Book 4,418. The independent checker has positive
mixed-orientation controls, but those do not qualify actual reversed generation.

The closure audit found two required failures:

- `application.boundary_orientation`: aligned manifold/non-manifold controls
  pass, but reversed controls return success with accepted degenerate geometry.
  The previous executable produces identical failing OBJ bytes. A reused curve's
  stored direction is consumed without a coherent patch-incidence mapping;
  source control points and shared endpoints are altered in the analytic control.
- `application.metric_schema`: CSV control-column labels do not align with their
  emitted values. A real aligned control has nine mismatches against named log
  fields. Previous Eistute output also fails the independent semantic audit.
  Exact before/after equality alone preserves this existing reporting defect.

Next action: repair direction handling in control-net construction and local
boundary-to-UV mapping, then qualify real reversed adaptive/retry/rollback cases.
Repair CSV header/value alignment with independent controls and an explicit
output-change record. Re-run closure audit and all required gates on the same
revision. Keep PR #3 draft and main unchanged; do not begin stage 2.

Evidence: `docs/evidence/STAGE1_INCIDENCE_AUDIT.md` and
`docs/evidence/stage1/incidences/`. The historical numerical investigation is in
`docs/evidence/STAGE1_SMOOTHING_ORDER.md`. Every stage now requires an explicit
closing audit, regression, failure inventory and post-merge validation.

## Open blockers and limitations

- Main still has the historical input/verifier and pointer-order defects. The
  draft repairs them but cannot integrate while reversed geometry and CSV
  semantics fail required gates.
- Legacy compatibility summaries still compare zero groups when synchronized.
  Independent incidence evidence now measures actual sheets and does not treat
  that legacy zero as proof of compatibility.
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
