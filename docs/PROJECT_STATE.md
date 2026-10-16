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

## Active work item: stage 1 (closure qualification)

Issue #2 and PR #3 remain the sole active delivery. Main is still
`b4087a472015d6898687c0aeff444efb4f1a9524` before integration.
Stage 0 was integrated through PR #1.

Implemented: strict CLI/configuration/BP validation; independent accepted-state
OBJ/CSV/log and per-incidence verification; exact repeatability; deterministic
logical-edge smoothing order; coherent patch-incidence orientation through
control-net construction, coarse mesh and adaptive reconstruction; physical arc
mapping and corner-curve repair; corrected CSV header semantics.

Closure candidate results: native Windows GCC 16.1.0 serial C++17 Release build
PASS; CTest **9/9 PASS, zero skipped**; 65 Python controls, 23 invalid-input
controls, 14 real orientation cases covering 44 attempted states, analytic
constructor/arc tests and actual analyzer scope controls PASS. Selected exporter
clang-tidy and changed C++ range formatting PASS. Vendor files are unchanged;
first-party diagnostics remain errors and full legacy warning debt is open.

Eistute and Book repeat exactly with fixed executable/configuration/command,
including all acceptance/CSV fields, OBJ and incidence snapshots. Every attempted
article state has positive shared-incidence coverage and zero measured position
gap. Both models accept steps 0 and 1. Last accepted triangles: Eistute 1,168;
Book 4,256. The Book change from 4,418 is an explicit corner-curve defect repair.
Raw previous-candidate comparisons remain failed and retained, including CSV
label corrections. Strict comparison to a reference with only the two minimal
CSV/corner fixes passes for both models. No oracle or tolerance was relaxed.

The previously required reversed-generation and CSV-schema failures are repaired.
Historical failures remain evidence. Current detailed results and source/input/
executable hashes: `docs/evidence/STAGE1_ORIENTATION_REPAIR.md` and
`docs/evidence/stage1/orientation/`. Earlier incidence and smoothing reports are
historical observations, not current gate status.

Next: verify the exact published PR head, recheck remote concurrency/checks,
integrate only with green required gates, and repeat regression on main. Record
post-merge closure before starting stage 2's mesh/architecture inventory. Every
stage requires the user's requested explicit audit and regression.

## Open blockers and limitations

- Integration and post-merge qualification remain pending until recorded on
  the actual delivery revision. Prepublication passing checks alone do not close
  the stage. Stages 2-11 have not begun.
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
