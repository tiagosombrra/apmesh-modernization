# Stage 2 closure audit and post-merge regression

Date: 2026-10-16. Work item: issue #5. Implementation PR: #6.

Stage 2 is complete for its architectural inventory scope. It preserves all
production, build, model/config/vendor and existing scientific verifier blobs.
The new development tool, independent controls and reviewed contracts received
exact-head qualification and the required regression again after integration.

## Revision identity and remote audit

- Entry main: `d4561c9421226503cb4a478faad71ed5ad012381`.
- Qualified PR head: `3544c99501ceb5883795c4211215df8a5d01b23f`.
- Integrated main: `071cba93a0074918d392bdfb28eba02c4acbb7bd`.
- Identical qualified/merged tree: `d7803664cfeac6771c376898d7bfc9db8c759b19`.
- All 653 remote blobs matched expectations; all 651 local text blobs matched.
  Both remote-only immutable publication artifacts retained their identities.
- Executable SHA-256:
  `aa02aa970dfa277d1e4590bb31d46a3ec35f8f36734accd7d2bfbf08027d1301`.

Main, branches, open issues/PRs and checks/workflows were audited at entry and
before integration. Only issue #5/PR #6 were active. The expected main/head
remained unchanged and mergeability was clean. No hosted checks or workflow are
configured; zero checks was not used as proof of qualification. No paid Actions
were created. Integration preserved the exact qualified tree. Post-merge build
reported no work to do.

The earlier copied stage 1 executable has its separate retained hash. Entry
repetitions, the independently rebuilt executable, exact-head and post-merge
results all compare strictly. Rebuild bytes were not assumed identical.

## Closure results

| Required gate | Published head and integrated main |
| --- | --- |
| Production inventory | 122 files: 57 translation units, 65 headers |
| Build-source identity and compile coverage | Three CMake inputs unchanged; all 57 production units in the fresh compilation database |
| Reviewed traceability | 22 contracts and 78 exact source anchors; retained inventory fresh |
| Include evidence | 453 potential literal directives, 268 distinct first-party edges, one six-header strongly connected set |
| Full CTest | 9 passed, 0 failed, 0 skipped |
| Python tooling/checker controls | 73 passed, including eight new independent inventory controls |
| Existing application controls | 23 invalid inputs, 14 orientation cases/44 attempted states, analytic constructor/arclength and actual analyzer-scope controls passed |
| Selected exporter clang-tidy | Passed with unchanged checks/vendor policy |
| Eistute and Book exact repetitions | Both passed, all nine attempted article states |
| Strict comparison to entry and qualified head | Both models passed, including OBJ/CSV/decisions/incidence snapshots |
| Shared-incidence and named CSV semantics | Positive every-state coverage and both repetitions' named-field audits passed |
| New Python/doc/JSON whitespace and document links | Passed |

Eistute still accepts steps 0 and 1 and rejects 2-4; its last accepted mesh has
1,168 triangles. Book still accepts 0 and 1 and rejects 2-3; its last accepted
mesh has 4,256 triangles. Shared boundaries retain every measured sheet, with
16/112 sides, 4/28 shared sheets and 3/27 comparisons per attempted state;
measured shared-position gaps remain zero. No formula, numerical tolerance,
accumulation order, adaptation budget or acceptance policy was changed.

Historical stage 1 raw failures and rejected target artifacts remain preserved.
The same independent evaluator/export budgets and exact regression oracle apply.
An archived artifact, a rejected candidate and a zero-comparison legacy summary
are still not substitutes for qualified accepted-state/boundary observations.

## Architectural audit disposition

The audit reviewed the development-code delta, all-file inventory coverage,
independent invalid controls, and semantic statements against actual field types,
constructors/destructors and the serial orchestration/conversion/rollback paths.
Coordinate domains, logical IDs, ownership/adoption/copy, observer rebinding,
cache invalidation, duplication and scientific execution order are documented.
The ADR and staged repair sequence preserve domain separation and require
equivalence before consolidation. Current project state and plan are updated.

The following source facts carry forward as priorities, not a new claim of
whole-application dynamic qualification: SetNoh copies despite its ownership
comment; node copies carry observer adjacency; Face/Edge deletion needs manual
endpoint detachment; curve restoration recreates sampled pointers by ID;
quadtree/boundary ownership is conditional; pointer-taking patch copies are not
full graph clones; public control mutation lacks a uniform cache refresh
contract. CMake's AP_MESH_HAS flags and production USE flags also require later
effective-preprocessor/routing qualification.

The lexical scanner does not prove active preprocessing, macro/raw-string
grammar, system-header resolution, runtime reachability or ownership semantics.
Anchors prove source traceability; human review supplies the stated interpretation.
No broad source rewrite, alternate generator, Eigen deletion or scientific
proposal was introduced. The inventory is not an exhaustive line-by-line proof.

## Remaining work and closure-record scope

Stage 3 starts with a bounded physical-node copy/adoption and adjacency lifetime
characterization, using qualified positive and deliberately invalid diagnostic
controls. Stage 4 may unblock actual instrumentation/portability barriers. Dynamic
memory safety, every transient inner retry/exception path, mutation APIs,
parallel modes, full warning cleanup, Eigen replacement, C++23, generated
Doxygen, Decor Shelf generation and performance remain later-stage scope.

This follow-up closure record changes documentation/evidence only. Production,
development tools/tests, build/model/config/vendor and the reviewed inventory
retain their qualified blob identities. The record is reviewed and checked
before integration, with main checked again afterward. The user's mandatory
end-stage audit, regression, failure inventory and post-merge rule continues.

Evidence and commands: [stage 2 audit](STAGE2_ARCHITECTURE_AUDIT.md),
[architecture map](../architecture/MESH_ARCHITECTURE.md),
[follow-up sequence](../architecture/REFACTOR_SEQUENCE.md),
[exact-head qualification](stage2/exact_head_qualification.json) and
[post-merge qualification](stage2/postmerge_qualification.json). CTest, inventory
and selected lint logs are retained beside those reports. Large raw campaigns
remain local with identities/results retained in the reports.
