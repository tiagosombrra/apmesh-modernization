# Stage 2 architecture inventory: closure candidate audit

Date: 2026-10-16. Work item: issue #5.
Base main: `d4561c9421226503cb4a478faad71ed5ad012381`.
Base tree: `b6ab987ae795ac1713adcde7b262c6303a412915`.

## Entry audit and regression

Remote main and all branches were inspected before work. No open PR, issue or
other active delivery existed; no hosted workflow/check was configured. The new
stage 2 issue is the sole active work item. All 636 locally available text blobs
matched remote content; the two immutable publication binaries retain their
remote identities. An independent writable working copy was created; synced
project reference files and the previous working copy were not edited.

Native Windows UCRT64 GCC 16.1.0, C++17 serial Release, MPI/OpenMP/LTO OFF,
CMake/CTest 4.4.3 and LLVM 22.1.8 reproduce the stage 1 entry suite: 9/9 CTest,
zero failures/skips, including its 65 Python controls and actual invalid-input,
orientation, analytic and analyzer-scope controls. All 57 production translation
units appear in the fresh compilation database.

The copied stage 1 executable SHA-256 is
`782fa6d0c235bca7f3fcb1e02e623cb105855f918a74c0616f262948c60a632e`.
The fresh build SHA-256 is
`aa02aa970dfa277d1e4590bb31d46a3ec35f8f36734accd7d2bfbf08027d1301`.
Their identities differ; each received its own fixed-executable/command/config
repetition. Strict comparisons of all nine attempted Eistute/Book states pass
between them and against stage 1's retained post-merge results. Neither path
relocation nor the fresh rebuild changed OBJ, CSV/decisions or incidence results.
Named CSV semantic audits pass on both repetitions of both models for each
executable. The exact configuration/model hashes are retained in the reports.

## Delivered inventory and findings

- Reproducible inventory of 122 production C++ files: 57 translation units,
  65 headers and three build-input hashes. All production/build blobs remain
  identical to the base. Model/config/vendor and existing verifier inputs are
  unchanged. No formula, tolerance, accumulation order or policy is modified.
- 453 potential literal include directives and 268 distinct first-party edges;
  one six-header strongly connected include set in crab_mesh/aft. Directory
  grouping and lexical cycles are explicitly separated from semantic layers
  and runtime ownership.
- 22 reviewed domain/lifecycle contracts with 78 checked source anchors, plus
  coordinate/identity/conversion, ownership, invalidation, duplication and
  dependency ledgers in docs/architecture/.
- A decision record preserves physical/UV separation, canonical/incidence
  orientation, explicit owners/observers and staged equivalence checks before
  consolidation. A prioritized sequence defines the next stage 3 slice and
  dependencies through stage 11.

Source-proved facts include SetNoh copying versus its adoption comment, copied
node adjacency, Face/Edge endpoint deletion with manual detachment, conditional
quadtree/boundary ownership, ID-preserving curve sample recreation on rollback,
incomplete pointer-taking patch-copy semantics and mutation setters without a
coherent coefficient/cache refresh contract. They are recorded as contracts or
risks, not newly reproduced whole-application memory failures.

The build inventory also exposes AP_MESH_HAS_OPENMP/MPI definitions versus
USE_OPENMP/MPI branches with false defaults and no indexed production bridge.
External definitions can affect execution. Later portability qualification must
measure effective macros and execution routing; successful linkage or a thread
argument alone does not certify that route. No new parallel run is claimed.

## Controls and closure candidate results

Eight new independent tooling controls pass. They challenge added/empty source
coverage, changed content hashes, comment exclusion and exact include lines,
cycle reporting, missing/outside source anchors, duplicate/empty contracts and
the retained production/build inventory. They are part of normal tooling CTest;
the Python total is now 73. The full suite still has nine CTests and passes
9/9 with zero failures or skips. None is marked WILL_FAIL to conceal a defect.

Selected exporter clang-tidy passes with the unchanged checks and vendor scope.
No C++ formatting change is in this delivery; production source hashes are the
preservation gate. New Python/doc/JSON whitespace and source-anchor/inventory
freshness checks pass. This is not a full legacy lint-clean or formatting claim.

| Required article result | Eistute | Book |
| --- | --- | --- |
| Attempted states per execution | 5 | 4 |
| Accepted steps | 0, 1 | 0, 1 |
| Rejected steps | 2, 3, 4 | 2, 3 |
| Last accepted triangles | 1,168 | 4,256 |
| Entry and fresh-build exact repetitions | PASS | PASS |
| Strict candidate/entry and entry/stage-1 comparison | PASS | PASS |
| Every-state shared-incidence coverage | PASS | PASS |
| Named CSV semantics in both repetitions | PASS | PASS |

All 16 Eistute and 112 Book patch sides are observed in every attempted state.
Shared non-manifold groups have 4/28 sheets, 3/27 comparisons per state and zero
measured position gap. Historical raw failures from stage 1 remain untouched;
the independent evaluator/export budgets and strict comparison oracle are
unchanged. Rejected candidates remain distinct from the accepted result.

The closure audit reviewed the development-code delta, source coverage,
semantic contracts against actual constructors/destructors/call paths, domain
and identity assumptions, test failure controls, dependency order, current
documentation and known qualification inventory. It is focused architectural
review, not an exhaustive proof of every source line or reachable lifetime.

## Limits, next work and reproduction

The scanner does not preprocess conditions, expand macros/raw-string grammar,
resolve system include search paths or infer ownership/reachability. Source
anchors establish traceability; semantic interpretation remains reviewed prose.
The production hashes and scientific regression are independent checks of the
claim that this inventory delivery does not alter the generator.

Sanitizers, mutation API correctness, full exception/inner-retry teardown,
ownership repair, parallel routing, full warning cleanup, Eigen replacement,
C++23, Doxygen, Decor Shelf generation and performance remain later-stage work.
The next implementation slice characterizes node copy/adoption and adjacency
lifetime with qualified positive and deliberately invalid diagnostic controls.
Portability work may unblock it through one explicit stage 4 item if needed.

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
python tools/quality.py tidy src/input_output/incidence_snapshot.cpp --build build/local-serial
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh --model eistute --output build/new-stage2-eistute --report stage2-eistute.json
python tools/audit_metric_schema.py build/new-stage2-eistute/repetition-1 --report schema.json
python tools/verify_generation.py build/new-stage2-eistute/repetition-1 --require-boundary-coverage --report generation.json
```

Use .exe on Windows, repeat for Book and both repetitions, and compare with the
entry run using --baseline. Fresh output directories are required. Small reports
and hashes live under docs/evidence/stage2/; large raw outputs remain local.
Exact published-head and post-merge qualification are still required before
stage 2 closure. No paid Actions or hosted workflow is introduced.
