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
4/4. New C++ validator/consumer formatting and consumer clang-tidy passed.
Book preserved every OBJ and all decision/metric fields. Eistute preserved every
OBJ and accepted/rejected steps, but strict numerical-report comparison failed.
The unchanged reference executable also varies numerically between repetitions,
including runs with identical configuration bytes, command and output paths.
See `docs/evidence/STAGE1_VALIDATION.md` and its JSON evidence.

Next action: localize the pre-existing numerical instability without changing
formulas, iteration ordering, stopping thresholds or comparison tolerances.
Keep the strict failing gate and draft PR until the discrepancy is explained
and the required comparison passes. No root cause is asserted yet.

Per-incidence boundary validation also remains open: legacy OBJ lacks patch
incidence labels, and synchronized legacy reports compare zero curve groups.
The new verifier explicitly reports absent incidence coverage and fails the
strict boundary-coverage request, even if a legacy group summary is measured.
Do not mark stage 1 complete or begin stage 2 while this work item is open.

## Open blockers and limitations

- Main still has the historical input/verifier defects. The stage 1 draft repairs
  those defects, but integration is blocked by reference numerical repeatability.
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
