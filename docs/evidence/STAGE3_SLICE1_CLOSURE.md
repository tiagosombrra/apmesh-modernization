# Stage 3 slice 1 closure audit

Issue #8; implementation PR #9. Qualified head:
`6c6c2f2d50f5870fd92e4edbc91fc5d901a1cd22`.
Integrated main: `e30fa99a8ea6da709f3943e8975efb31d9610b1d`.
Identical head/main tree: `41874ce10a950d713ffcf245880d651d8a874c21`,
674 blobs, including two unchanged remote-only publication artifacts.

The original SubMesh::SetNoh copied foreign triangle observers into a new owned
node. A qualified AddressSanitizer experiment reproduced heap-use-after-free
after original-triangle destruction. The repaired boundary clears only copied
adjacency, preserving scalar fields, caller ownership and unique adoption
identity. All six current call sites construct fresh scalar nodes. No observed
article generation behavior changes; no scientific policy, formula, ordering,
threshold, input or numerical verifier was modified.

## Exact-head and post-merge gates

The complete remote tree was matched to the expected blob map. Local source
bytes match all 672 available text blobs; the two immutable binaries are
preserved through the base tree. An outgoing console-encoding mismatch in two
documents was detected and corrected before commit publication; no corrupted
document tree was attached to a branch. The source/content gate was never
relaxed. Historical stage 1/2 evidence remains unchanged.

Both the published head and integrated main passed:

- GCC 16.1.0 serial C++17 Release, MPI/OpenMP/LTO off; CMake/CTest 4.4.3.
- CTest **10/10**, zero skipped, including **74 Python controls**, 23 invalid
  inputs, existing orientation/analytic/verifier-negative/analyzer-scope controls
  and 200 node-copy/rebuild/move/replacement/teardown iterations.
- Seven separate MSVC 19.44.35229 ASan/Debug CRT cases. Valid ownership cases
  pass; CRT reports zero retained blocks/bytes. Deliberate use-after-free,
  double-free and a three-block/136-byte leak are detected. The historical
  original implementation remains a failing negative reproduction.
- Reviewed inventory freshness: 122 production C++ files, four CMake inputs,
  22 contracts, 79 anchors. SubMesh selected clang-tidy and changed-file
  formatting/whitespace checks pass. Legacy warning debt is not suppressed.
- Eistute and Book each repeated twice with the same executable/configuration/
  command within each experiment, then compared strictly with entry. All nine
  attempted states retain exact OBJ, acceptance/CSV and incidence results.
  Positive shared-incidence coverage and zero measured gap remain; accepted
  steps are 0/1. Final accepted triangles: **1,168 / 4,256**. Named CSV audits:
  **189 fields**, zero differences. Entry also matches stage 2 main exactly.

Application executable SHA-256:
`b1244378f7638d4508df04d76e091615a62158d76a5a1f7068b1079321d46adf`.
Commands, source/executable/input hashes, original failures and measured limits:
[initial checkpoint](STAGE3_NODE_LIFETIME.md),
[head qualification](stage3/head_qualification.json),
[main qualification](stage3/postmerge_qualification.json),
[current source identities](stage3/source_identities.json).

Remote audits before integration and after merge found only the authorized
work item/PR. No hosted workflows, checks or commit statuses are configured;
the empty aggregate status is not interpreted as a passing check. The required
local gates passed on the exact reviewed implementation revision.

## Scope and next step

The code, tests, ownership contracts, current architecture map, decision record,
state, plan and failure inventory have been reviewed. This follow-up changes
only documentation/evidence, preserving every qualified production, test,
development-tool, build, model, configuration and vendor blob. Its head is
audited and CTest/inventory checked before merge, then main checked again.

**Only slice 1 is complete; stage 3 remains in progress.** Next: coherent UV
front/edge/face teardown with normal, partial and failed generation, plus
deliberate ownership controls. Sample/initialization ownership (including
source-proved center/estimator gaps), rollback observers, retained meshes,
UV exceptions, general node snapshots, triangle removal/replacement/cache
mutation and full-process leaks remain open. Windows ASan/CRT isolation is not
Linux LSan, UBSan, full-application memory or parallel qualification. Decor Shelf
generation and every internal retry state remain unmeasured. Stages 4-11 remain
pending; numerical budgets and existing boundary criteria stay unchanged.
