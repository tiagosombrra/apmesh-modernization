# Project state

Updated: 2026-10-16 UTC.
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

Stage 0 is integrated in PR #1 and locally validated. See
`docs/evidence/BOOTSTRAP_VALIDATION.md` for executed checks and limitations.
No automatic hosted workflows or paid Actions have been created.

## Completed in stage 1

PR #3 integrated the qualified head `fd59206497b12e3352fc8bea634702d7fe9eb8a9`
as main `b7bdda0a5ac035938bdaa3ea59ae8a5c587aa2b6`. Its tree is exactly the
qualified 632-blob tree. All required gates passed again after merge; issue #2
can close. The documentation-only closure record preserves production/test/tool
source identities. See `docs/evidence/STAGE1_CLOSURE.md`.

Implemented: strict CLI/configuration/BP validation; independent accepted-state
OBJ/CSV/log and per-incidence verification; exact repeatability; deterministic
logical-edge smoothing order; coherent patch-incidence orientation through
control-net construction, coarse mesh and adaptive reconstruction; physical arc
mapping and corner-curve repair; corrected CSV header semantics.

Pre-merge and post-merge results: native Windows GCC 16.1.0 serial C++17 Release build
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

## Active work item: stage 2 (closure qualification)

Issue #5 is the sole active work item. Base main is
`d4561c9421226503cb4a478faad71ed5ad012381`; stage 1 issue #2 is closed.
The entry remote audit found no open PR/issue or hosted workflow/check.

Delivered: a reproducible inventory of all 122 production C++ files (57 units,
65 headers), three build inputs, 22 reviewed contracts and 78 source anchors;
physical/UV domain and identity/conversion maps, ownership/invalidation and
computation-duplication ledgers, one six-header include cycle, an engineering
ADR and a dependency-ordered repair sequence. Production/build/model/config/
vendor and existing verifier identities are unchanged.

Entry CTest 9/9 and its 65 Python controls passed. The candidate CTest is also
9/9 with zero skips, now including 73 Python controls after eight independent
inventory controls. Fresh-build Eistute/Book repetitions and strict entry/
previous-stage comparisons pass for all nine attempted states, with positive
incidence coverage and named CSV audits. Selected exporter lint passes.

Source review records the node copy/adoption contradiction, copied adjacency,
manual endpoint detachment, rollback observer invalidation, patch-copy and cache
mutation limits, and the build macro/routing gap. These are differentiated from
newly reproduced runtime defects. No new memory or parallel qualification is
claimed. Architecture: `docs/architecture/MESH_ARCHITECTURE.md`; decisions and
next-slice priorities: `docs/architecture/REFACTOR_SEQUENCE.md` and
`docs/decisions/ADR-0001-mesh-domains-and-lifetimes.md`.

Next: qualify the exact delivery revision, integrate only after passing gates,
and repeat main validation. Stage 3 then starts with physical-node copy/adoption
and adjacency lifecycle characterization using qualified diagnostics; stage 4
may unblock tooling if a proved portability barrier requires it. Current audit:
`docs/evidence/STAGE2_ARCHITECTURE_AUDIT.md` and `docs/evidence/stage2/`.

## Open blockers and limitations

- Stage 1 is closed for its measured serial scope; stage 2 awaits final
  delivery qualification. Stages 3-11 remain pending. Broad numerical, memory,
  portability and generated-documentation qualification remain open.
- Legacy compatibility summaries still compare zero groups when synchronized.
  Independent incidence evidence now measures actual sheets and does not treat
  that legacy zero as proof of compatibility.
- Ownership findings, timers, duplicate mesh representations, VLAs and warning
  debt remain. No full-application leak-free claim is justified.
- Eigen remains; CRABMesh consolidation, complete English renaming, generated
  Doxygen review, C++23 qualification and performance work remain open.
- The archived-artifact test is not a new accepted-mesh generation experiment.
- Earlier local Git networking failed DNS; this delivery uses the GitHub
  connector for remote operations. Local source validation excludes the two binary publication
  artifacts; their remote import hashes are independently compared with source.

## Continuation rule

One work item at a time. Every delivery records scope, reviewed changes,
executed checks, toolchain, failures and next step. Recheck remote authority
before writing and after integration. Scientific algorithm changes wait for
explicit advisor alignment.
