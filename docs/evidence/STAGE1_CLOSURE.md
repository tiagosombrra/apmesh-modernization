# Stage 1 closure audit and post-merge regression

Date: 2026-10-16 UTC. Work item: issue #2. Implementation PR: #3.

Stage 1 is complete for the measured serial scope. The required reversed-curve
and CSV failures found by the preceding audit were repaired, and all required
local gates passed on the published head and again after integration.

## Revision identity

- Qualified PR head: `fd59206497b12e3352fc8bea634702d7fe9eb8a9`.
- Integrated main: `b7bdda0a5ac035938bdaa3ea59ae8a5c587aa2b6`.
- Identical source tree: `b2ce576483247a804a5a2335951739f007dc54c0`.
- All 632 remote blobs matched the expected tree, including both immutable
  publication binaries; all 630 locally available text blobs matched.
- Post-merge executable SHA-256:
  `782fa6d0c235bca7f3fcb1e02e623cb105855f918a74c0616f262948c60a632e`.

Remote main, branches, open PRs, mergeability and check/status endpoints were
audited before integration. The leased PR head and expected main were unchanged.
No hosted checks or workflows are configured; zero hosted checks was not used
as evidence of qualification. No paid Actions were created. Merge preserved the
qualified tree exactly. The post-merge local build reported no work to do.

The earlier prepublication executable and the later rebuild have different PE
hashes; both identities are retained. The complete source manifest is unchanged,
and the rebuilt executable received its own exact repetitions, strict reference
comparisons, semantic audits and application tests. Binary identity was checked
within each experiment, rather than assuming rebuild bytes were identical.

## Required results on main

| Gate | Result |
| --- | --- |
| Full CTest | 9 passed, 0 failed, 0 skipped |
| Python tooling/checker controls | 65 passed |
| Actual invalid-input controls | 23 passed |
| Actual mixed-orientation generation | 14 cases, 44 attempted states, all passed |
| Analytic constructor/arclength probe | 16 direction combinations, 8 edge orientations and corner control passed |
| Actual analyzer scope controls | Vendor positive and both first-party negative controls passed |
| Selected exporter clang-tidy | Passed; first-party warnings remain errors |
| Incremental C++ formatting | 17 files' changed ranges / complete new files passed |
| Eistute and Book exact repetition | Both passed; every OBJ, CSV/decision and incidence field exact |
| Strict minimally corrected reference comparison | Both passed across all 9 attempted article states |
| Independent shared-incidence coverage | Every article state passed with positive comparisons and zero measured gap |
| Independent named CSV audit | Both repetitions of both models passed |
| Strict post-merge vs qualified-head comparison | Both models passed |

Eistute accepts steps 0 and 1, rejects 2-4 and ends with 1,168 accepted triangles.
Book accepts steps 0 and 1, rejects 2-3 and ends with 4,256 accepted triangles.
The Book reduction from 4,418 follows the separately proved corner-curve repair.
The unchanged acceptance policy still rejects Eistute's historical stage-4
target; a matching rejected artifact cannot qualify as the accepted result.

The raw preceding-candidate comparisons remain failed and stored. No assertion,
strict numerical tolerance, scientific criterion or independent checker was
relaxed. See STAGE1_ORIENTATION_REPAIR.md for the defect/change ledger and
controlled_reference.patch for the two minimal reference repairs.

## Audit disposition and remaining scope

Code review covered canonical curve identity, input control preservation, local
UV traversal, increasing integration limits and the completed edge's preceding
side. Tests challenge actual generation as well as the independent checkers.
Contracts and current documentation distinguish attempted, accepted, rejected,
retried, unmeasured and failed outcomes. Historical failures are preserved.

Source/observer ownership, sanitizer qualification, all transient inner-retry
meshes, parallel modes, full warning cleanup, Eigen removal, C++23, Doxygen,
Decor Shelf generation and performance remain outside this stage's closure.
The legacy zero-comparison summary remains unmeasured; actual incidence
observations provide the positive coverage. The archived test remains an
artifact check. These limits carry forward explicitly rather than disappearing
when stage 1 closes.

This closure record changes only documentation and evidence. Production, tests,
tools, build configuration, model/config inputs and vendor sources retain their
qualified blob identities. The record itself is reviewed and checked before
integration, followed by another main check. Stage 2 is next: inventory mesh
concepts, ownership, identities, conversions, duplication and dependencies
before consolidation. The same end-stage audit/regression rule continues.

Executed commands and toolchain are in STAGE1_ORIENTATION_REPAIR.md. Exact-head
and post-merge reports/logs are in stage1/orientation/exact_head_qualification.json,
postmerge_qualification.json, exact_head_ctest.log, postmerge_ctest.log and
postmerge_tidy.log. Large raw campaign files remain local with report hashes.
