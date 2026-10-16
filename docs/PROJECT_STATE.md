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

## Next work item: stage 1

Audit remote main/branches/open PRs/checks, then implement explicit invalid-input
failure and trustworthy accepted-state regression. Inspect the input failure path
before changing behavior; reproduce the existing false success with a negative
test. Keep publication artifacts, attempted candidates and accepted output separate.
Check each boundary incidence independently; reject zero-coverage confirmation.
Use the prior patch as evidence only, not an automatically accepted repair.

## Open blockers and limitations

- Invalid input can still return success; historical generation verifier may
  approve a rejected Eistute stage. These application defects are not fixed here.
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
