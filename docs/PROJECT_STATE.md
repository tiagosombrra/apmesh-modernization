# Project state

Updated: 2026-10-17 UTC.
Scope: implementation modernization preserving the published technique.

## Completed in stage 0

- Private separate repository; canonical name is `tiagosombrra/apmesh-modernization`.
- Exact 513-blob publication import at `cbfb863fb014e798289d824e158f67922036a5e3`.
- Source commit and tree pinned; licenses, citation and historical README kept.
- Initial audit, validation status and unapplied candidate patch retained.
- English working agreement and complete stages 0-11 plan.
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
is closed. The documentation-only closure record preserves production/test/tool
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

## Completed in stage 2

Issue #5 and PR #6 deliver the inventory. Qualified head
`3544c99501ceb5883795c4211215df8a5d01b23f` integrated as main
`071cba93a0074918d392bdfb28eba02c4acbb7bd`, preserving its exact 653-blob tree.
All required gates passed again after merge. The documentation-only closure
record preserves production/development/test/build/input identities; see
`docs/evidence/STAGE2_CLOSURE.md`. Stage 1 issue #2 remains closed.

Delivered: a reproducible inventory of all 122 production C++ files (57 units,
65 headers), three build inputs, 22 reviewed contracts and 78 source anchors;
physical/UV domain and identity/conversion maps, ownership/invalidation and
computation-duplication ledgers, one six-header include cycle, an engineering
ADR and a dependency-ordered repair sequence. Production/build/model/config/
vendor and existing verifier identities are unchanged.

Entry CTest 9/9 and its 65 Python controls passed. The candidate CTest is also
9/9 with zero skips, now including 73 Python controls after eight independent
inventory controls; the same suite passed on the published head and main. Fresh-build Eistute/Book repetitions and strict entry/
previous-stage comparisons pass for all nine attempted states, with positive
incidence coverage and named CSV audits. Selected exporter lint passes.

Source review records the node copy/adoption contradiction, copied adjacency,
manual endpoint detachment, rollback observer invalidation, patch-copy and cache
mutation limits, and the build macro/routing gap. These are differentiated from
newly reproduced runtime defects. No new memory or parallel qualification is
claimed. Architecture: `docs/architecture/MESH_ARCHITECTURE.md`; decisions and
next-slice priorities: `docs/architecture/REFACTOR_SEQUENCE.md` and
`docs/decisions/ADR-0001-mesh-domains-and-lifetimes.md`.

Current audit and exact-head/post-merge evidence:
`docs/evidence/STAGE2_ARCHITECTURE_AUDIT.md`, `docs/evidence/STAGE2_CLOSURE.md`
and `docs/evidence/stage2/`.

## Stage 3 in progress: slice 1 qualified (#8, PR #9)

Qualified head `6c6c2f2d50f5870fd92e4edbc91fc5d901a1cd22` integrated as main
`e30fa99a8ea6da709f3943e8975efb31d9610b1d`, preserving the exact 674-blob tree.
All required gates passed again after merge. This documentation-only follow-up
preserves qualified production/tool/test/build/input identities. See
`docs/evidence/STAGE3_SLICE1_CLOSURE.md` and `docs/WORKLOG.md`.

The first bounded slice repairs a reproduced ASan heap-use-after-free: SetNoh
copied foreign element observers into a new mesh node. It now preserves scalar
state while clearing those observers; local triangles rebuild adjacency. The
header explicitly distinguishes copying from unique/raw ownership adoption.
General node copies and triangle removal/replacement remain outside this slice.

Candidate, exact-head and main gates: CTest 10/10, zero skips; 74 Python controls; selected SubMesh
lint/formatting; seven qualified ASan/Debug CRT cases including deliberate UAF,
double-free and leak controls. Repeated Eistute/Book and strict entry/stage-2
comparisons are exact across all nine attempted states, preserving 1,168/4,256
last-accepted triangles and measured shared-incidence coverage. See
`docs/evidence/STAGE3_NODE_LIFETIME.md` and `docs/evidence/stage3/`.

Slice 1 is complete for its measured boundary; the full stage 3 remains open.
## Stage 3 slice 2 qualified (#11, PR #12)

Head `a5fb2cd0d7ebbe6dc10f98689f4d6caa60419c0c` integrated as main
`5bfcadaaa2172c297448c9870c0f468feeae8f4a`, preserving the exact 706-blob tree
`306907d63f893767736bddfd995cf313f1bfcf8f`. Exact-head and post-merge CTest
11/11, 74 Python controls, 26 UV ASan/CRT cases, seven previous node cases,
selected lint/formatting and strict repeated Eistute/Book regression pass.
Registered UV templates have a single owner through failure and ordered
transfer; endpoint teardown allocates nothing and handles midpoint aliases.
Both models retain 1,168/4,256 last-accepted triangles, exact OBJ/acceptance/
incidence results and 189 matching named CSV fields. No scientific policy,
independent verifier, input or vendor changed. The documentation closure
preserves all qualified production/tool/test/build/input identities; see
`docs/evidence/STAGE3_UV_CLOSURE.md`, the failed original and ADR-0003.
Only this measured slice is closed; the wider stage 3 remains open.

Next bounded scope: allocation failure before UV registration and
constructor/setter replacement. Curve sample/rollback ownership, other UV
exceptions, generic adjacency and cache mutation, full process leaks and
parallel paths still need qualification.
Stage 4 may unblock actual instrumentation barriers. Keep one active item.

## Stage 3 slice 3 qualified (#14, PR #15)

Head `fce74915755d1535b89dbd280cbc1ba3813f9b91` integrated as main
`68ef4db735d3c478215815128309c6bdd7a8e90c`, preserving tree
`2bb4359687579a9069e162b228228dea2b1197be` (737 blobs). Exact-head and
implementation-main gates pass: CTest 12/12, zero skips, 74 Python controls,
UV 35/35, node 7/7, five-unit selected lint, changed-range formatting, inventory
and strict repeated Eistute/Book regression. Last accepted meshes remain
1,168/4,256 triangles with 189 matching CSV fields and positive incidence
coverage. All scientific policies and independent numerical verifiers remain.

The original runner stays failed with Edge/front construction retention,
partially changed failed cache replacement and a Face endpoint-alias UAF.
Both Face constructors are passing controls. Local owners now prepare caches
and Boundary adoption before commit. All 53 measured primitive allocation
failures unwind without retention and preserve the required live/caller state.
This documentation-only closure preserves every qualified production/tool/test/
build/input/vendor identity. See `docs/evidence/STAGE3_UV_ALLOCATION_CLOSURE.md`
and ADR-0004; the wider stage 3 remains open with three qualified slices.

Next bounded scope: template arrays/object creation before registration and
Boundary registration, followed by other setters/helper temporaries, then curve
sample/initialization ownership and rollback. Full-process and parallel memory
qualification, other template patterns and same-front reuse remain open.

## Stage 3 slice 4 qualified (#17, PR #18)

Head `ef89fd9d3305a9ed4c88548df086540d00bbadd3` integrated through PR #18 as main
`da3eed2dc351cfe1a82b117d686164686c738d95`, preserving tree `465fea56b1267644c352b1200250dc033b062188`
(784 blobs). Exact-head and implementation-main gates pass: CTest 14/14, zero
skips, 74 Python controls, UV 49/49, node 7/7, six-unit selected lint,
changed-range formatting, inventory and strict Eistute/Book regression.
Eight new sweeps inject 1,361 allocation failures; both missing-quadtree
subdivision overloads are independently qualified. Successful UV geometry,
IDs, registration order and allocation counts match the pinned original.
All nine scientific mesh states and acceptance/incidence results remain exact;
last accepted meshes retain 1,168/4,256 triangles and 189 matching CSV fields.
The original fails 12 of the 49 cases while its previous 35 remain passing.

Boundary guards pending registration and commits contour/IDs after success.
TemplateStorage owns unregistered suffixes while Quadtree owns adopted prefixes.
Face::quality protects borrowed endpoints during allocation failure. Missing
quadtree context throws std::logic_error without changing valid subdivision
criteria. Template failure is qualified for destruction, not retry or observer
consumption. Original failures, fixture/build/lint failures and an encoding
repair remain recorded. No scientific formula, threshold, input or vendor
changed. This documentation-only follow-up preserves every qualified
production/tool/test/build/input/vendor identity.

The wider stage 3 remains open with four qualified slices. Next qualify
earlier tree generation/subdivision, remaining mutation/helper and curve
internal scopes, then sample/initialization/rollback ownership. Other template
patterns, full-process and parallel/LSan/UBSan scope remain open.

See `evidence/STAGE3_UV_REGISTRATION_CLOSURE.md` and ADR-0005.

## Open blockers and limitations

- Stages 0-2 are closed for their measured scope. Stage 3 is in progress and
  stages 4-11 remain pending;
  architecture inventory is not dynamic memory, parallel or portability
  qualification. Broad numerical and generated-documentation work remains open.
- Legacy compatibility summaries still compare zero groups when synchronized.
  Independent incidence evidence now measures actual sheets and does not treat
  that legacy zero as proof of compatibility.
- Ownership findings, timers, duplicate mesh representations, VLAs and warning
  debt remain. No full-application leak-free claim is justified.
- Eigen remains; CRABMesh consolidation, complete English renaming, generated
  Doxygen review, C++23 qualification and performance work remain open.
- The archived-artifact test is not a new accepted-mesh generation experiment.
- Earlier local Git networking failed DNS; this delivery uses the GitHub
  connector for remote operations. Local source validation excludes the two
  binary publication artifacts; their remote import hashes are independently compared with source.

## Continuation rule

One work item at a time. Every delivery records scope, reviewed changes,
executed checks, toolchain, failures and next step. Recheck remote authority
before writing and after integration. Scientific algorithm changes wait for
explicit advisor alignment.
