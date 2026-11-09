# APMesh QUAD - canonical state and resume point

**Branch:** `quad-templates`

**Entry baseline / unchanged modernization main:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`

**Last session:** 2026-11-08-08

**Current milestone:** **Working real-quadtree UV QUAD bridge in `quad/uv-leaf-bridge`; application/physical integration remains pending. M0 stays qualified; M1/M2/M3 remain partial.**

**Protocol:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md)

**Plan:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

**Evidence:** [M1 historical review](M1_HISTORICAL_ORACLE_REVIEW.md), [M0_EVIDENCE.md](M0_EVIDENCE.md), [memory applicability](evidence/M0_MEMORY_APPLICABILITY_20261108.json), [serial contract register](M0_SERIAL_TRI_CONSUMERS.md), [GNU qualification](evidence/M0_GNU_QUALIFICATION_20261108.json), [MSVC review](evidence/M0_MSVC_REVIEW_20261108.json)

**History:** [SESSION_LOG.md](SESSION_LOG.md)

## Measured baseline and engineering delivery

[PR #184](https://github.com/tiagosombrra/apmesh-modernization/pull/184) integrates engineering-only M0 validation portability at `a29711bea1e38f6a1ea49dde443f0ae58ebadfa7`; qualified head `d11b83c33c6fc68892ea72d42c0cd5a1ba5aa205` has the identical tree. Production sources, inputs, presets, formulas, ordering and policies remain identical to the entry baseline. Session 05 changes only research documentation and evidence, based on `bb56d0741acdef9d775186c83bac7832a2e5c43f`.

- Linux GCC 13.3 C++17 serial full build and **75 CTest / 527 Python controls** passed on the exact delivery head and research merge. All original 526 Python IDs remain, plus one inventory regression. Checkpoint `5b928375d3033a0ab67150987123b8956562a362` also passes the full 75/527 with no failures/skips; see the [closure receipt](evidence/M0_CLOSURE_20261108.json). Final documentation seal publication must pass the same exact-head gate before push; absent or failing results block delivery.
- Linux Eistute/Book strictly preserve **9 states, 45 exact scientific artifacts and 123 positive boundaries**, including physical/UV precision and accepted/rejected decisions. Preserved checked-MSVC C++17 build/article captures have independently verified identities and the same bounded article counts. Do not regenerate these captures for documentation changes.
- Windows GCC has six affected native entries and 527 Python controls in the previously recorded scopes. Full Windows CTest was not repeated; no new complete-process Windows ASan/CRT claim is made.
- M0-G6: **22 source-bound MSVC Node outcomes reused**, including 46 verified denial sites; stale UV evidence rejected and **21 current ASan/CRT outcomes refreshed** against 293 repository dependencies per profile. Controls detect actual UAF/shared-delete/leak; positive retention and rollback/denial oracles pass.
- Old complete-process Linux evidence had 11 changed production dependencies and was rejected as current. Current Clang 18.1.3 C++17 **separate UBSan/LSan** builds pass the unchanged fixed inventory: **32 normal/invalid production processes plus five controlled terminal contexts per profile**. Instrument controls and runtime hashes are verified. Eight article comparisons pass; each instrument compares 18 states, 90 exact artifact pairs and 246 positive boundaries. The 959 copied raw records are byte-verified.
- M0-G7: reviewed all named serial producer/consumer contracts and three-node loops. The 38 explicit cast sites have dispositions: **16 selected serial, 17 preprocessor-excluded, five compiled entries with no selected serial caller identified**. Compiler-selected lines and manual call/contract review support this bounded register; it is not formal whole-program or external-client proof.
- Navigation-only maintenance corrects 18 inherited relative hrefs; prior failed link checks remain in dated history. All eight research documents pass local target-existence checks; URLs/fragments are unmeasured.

A working isolated UV QUAD generator, typed element and native test suite now exist in candidate branch `quad/m01-uv-prototype`. They are not integrated into the production application. Modernization Stage 3 remains separate and open.

## Worktrees and retained evidence

- Windows research: `C:\Users\tiago\Documents\dev\research\apmesh-quad`.
- Native Linux: `/home/apmesh/quad-m0-20261108-04` in WSL Ubuntu 24.04. Native Git cannot use the Windows worktree's drive-letter gitdir pointer. Transfer verified objects using authenticated Windows Git and fast-forward the clean native clone; never use the old native-Git recipe in `/mnt/c/.../apmesh-quad`.
- GNU regression profile: GCC 13.3 / CMake 3.28.3 / Ninja / LLVM format-tidy 22.1.8. Memory profiles explicitly use qualified Clang 18.1.3 and its recorded runtimes. MSVC probes use Visual Studio 2022 / 14.44, C++17 ASan RelWithDebInfo and checked CRT Debug.
- Raw session 05 reports, commands, compiler read dependencies, inputs, binaries and negative prefixes: `build/quad-m0/session-20261108-05/`; Linux originals under `build/quad-m0/session05-memory/` in the native clone. Session 04 and original MSVC records remain unchanged.
- Exact checkpoint regression: `python3 tools/validation_session.py plan --scope delivery`, then `python3 tools/validation_session.py run --scope delivery` in the native clone. Retain its generated `build/validation-session/<id>/report.json`, JUnit and complete LastTest.log; bind the source hash and test inventories before remote publication. This adapter alone does not authorize or qualify scientific work.

## Milestones and explicit remaining limits

| Milestone | State | Remaining admission / exit |
| --- | --- | --- |
| M0 - baseline | QUALIFIED: scoped G0-G7 baseline; 75/527 checkpoint regression recorded | Scoped exceptions retained below; no main/Stage 3 closure |
| M1 - historical T1-T6 oracle | PARTIAL | Graphs now execute with supplied positive points; historical numerical expectations and stated adviser decisions remain |
| M2 - UV QUAD topology | WORKING ISOLATED PROTOTYPE / PARTIAL | Value-owned UV mesh, canonical midpoints, quad emitter and disk validator; review, denials and broader numeric qualification remain |
| M3 - quadtree emitter | READ-ONLY LEAF BRIDGE IMPLEMENTED / PARTIAL | Real leaf capture/16 signatures and QUAD output tested; application opt-in call and full milestone qualification pending |
| M4 - physical QUAD | PENDING | Defined UV-to-XYZ geometry and four-node lifecycle/ownership |
| M5 - boundary transition | PENDING | Adviser decision: quad-dominant or all-quad; complete valid patch mesh |
| M6 - shared-curve multipatch | PENDING | Reversed two-patch and at least three-patch conformity |
| M7 - repeated adaptation | PENDING | QUAD history and accept/reject/retry/rollback |
| M8 - model study | PENDING | Reproducible independent metrics |
| M9 - anisotropy | OPTIONAL / PENDING | Approved formulation and isolated ablation |

Bounded fixture memory observations do not prove complete-process Windows safety. The fixed Linux inventory does not close all Stage 3 recovery, external-observer/caller, parallel or ownership obligations. The static serial register must reopen for new dispatch, element types and exports. Original timeouts, unavailable-tool observations, failed prefixes, rejected old identities and the offline diagnostic-parser error remain recorded. Zero remote statuses/check-runs is not passing CI.

## Next exact action

Review the actual-tree bridge in draft PR #185 and bind the numerical point rule the user reports is already aligned. Then connect the tested bridge through an explicit application opt-in entry, preserving the default TRI path. Physical QUAD/XYZ geometry, full patch boundary completion, shared-curve conformity and repeated adaptation retain separate milestones. The read-only leaf-to-QUAD bridge itself is now implemented and tested.

## Current M1 reconstruction

- Original seven-page local scan identified by SHA-256 `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`; Figure 7, printed p. 288 / PDF page 4, inspected visually. Drive candidate metadata is available, but its remote byte identity is unverified.
- The printed columns map to current classes **T1,T2,T4,T3,T5,T6**. Column 5 has no central junction; the intermediate polygon graph includes triangles in columns 2 and 5. Ordered CCW cycles and a review SVG are recorded, with explicit schematic-coordinate conventions.
- Local documentary checks pass 48 D4 graph observations, covering 16 geometric split signatures. Six deliberately altered records are detected. These are not production tests, independent human review or runtime QUAD validation.
- The paper's later midpoint/centroid subdivision implies counts **4,11,12,8,11,16** in printed order, conditional on the stated graphs/valid geometry. No such emitter is implemented. The numeric embedding and centroid formula remain review choices; boundary triangle retention prevents a general historical all-quad guarantee.
- Session 06 changes only research documentation/evidence. Raw source renders, local checker, audit and preview are under `build/quad-m1/session-20261108-06/`. Exact committed checkpoint publication requires full delivery regression, pre-commit/links and fresh remote audit/readback. Preserve that local report and the final SHA in the session response.
- M1 remains open; M2 is not admitted. No new article, memory or scientific campaign runs for this documentary checkpoint. Main stays `f6050ec1`; all broader Stage 3 limits remain.

## Current implementation candidate - session 07

- User explicitly requested implementation, clarified that the graph table is only a reference, and reported existing adviser alignment with decisions to follow. Continue the isolated implementation; do not treat a generic continuation as a supplied numerical formula.
- Candidate `quad/m01-uv-prototype`, implementation revision `e88081d2e2a80ea1baa8b988dc8f3888f19a62c1`: `research/quad/uv_mesh.h/.cpp`, `demo.cpp`, README and standalone `tests/quad`. Typed four-index elements, canonical endpoint-ID midpoints, per-corner QUAD emission, strong input preservation and independent topology/area validation are implemented. Caller-supplied interior points avoid freezing an unspecified centroid policy.
- Native suite passes **117 outcomes per profile** under Linux GCC 13.3, Windows GCC 16.1 and checked-MSVC 19.44 Debug, including 48 pattern transforms, 32 bounded grids, a 19-quad 2:1 seam and actual invalid-input/output controls. Separate suite: the production inventory remains 75 CTest /527 Python.
- Native demo generates **8 quads /15 vertices /area 2**. All three platform OBJ files are byte-identical; Windows also passes eight CLI positive/negative observations. Linux format and configured static analysis pass for all new compilation units. Compact source/binary/log evidence is in candidate `docs/research/quad/evidence/UV_QUAD_PROTOTYPE_20261108.json`.
- Final publication requires the complete regression on the exact final committed candidate and the research checkpoint, pre-commit/links and fresh remote checks/readback. Earlier successful 117-outcome captures may be reused only with matching code/build hashes. Final hashes/results and review link are recorded in the session response.
- Scope limits: isolated UV disk API and OBJ only; no production QUAD option/leaf connection, physical element, XYZ/curvature, whole-boundary, multipatch or adaptation support. No whole M1/M2/Stage 3 closure or performance/memory-safety claim.

## Published review candidate

[Draft PR #185](https://github.com/tiagosombrra/apmesh-modernization/pull/185),
head `1178720474c4b6efae37d01534648a1a8788ed2d`, contains the executable prototype.
Its exact full baseline passes 75 CTest /527 Python with no failures/skips;
117 native QUAD outcomes per profile are source/binary-bound. See the
[draft delivery receipt](evidence/UV_QUAD_DRAFT_DELIVERY_20261108.json).
The initial required-gate failure is a missing new CMake inventory entry;
the corrected candidate records that one generated input without changing
production sources/build targets. Remote statuses/check-runs are absent, not green.
This research checkpoint publishes status/evidence only; the code remains in
the draft branch and has not been merged into `quad-templates` or main.

## Current implementation - session 08

- The primary checkout `C:\Users\tiago\Documents\dev\research\apmesh-modernization` now uses `quad/uv-leaf-bridge`, so implementation files are visible directly under `research/quad`. Branch `main` is preserved at `f6050ec1`; it is no longer the active primary checkout. Committed files are visible in Explorer/history, not as pending Source Control changes. Compare with `git diff main -- research/quad tests/quad`.
- `quadtree_quad.h/.cpp` captures actual legacy Quadtree leaves in original publication order, validates reciprocal 2:1 neighbors/hierarchy and emits T1-T6 polygons for all 16 split masks. Shared UV IDs use dyadic hierarchy keys, not coordinate welding. Boundary exclusion, source owners/IDs/geometry/stats remain unchanged; no sorting/refinement/publication is performed on the source.
- GCC16/Windows, checked-MSVC19.44 Debug and GCC13/Linux pass **117 UV +30 bridge outcomes per profile**. Real uniform/adaptive trees, actual existing TRI preservation, 16 masks, neighbor-order independence and invalid/throwing cases are measured. The adaptive demo emits **42 quads /53 vertices /area 1/4** from **19 actual leaves**; OBJ raw bytes match all three platforms.
- C++17 standalone legacy support reuses the same 14-source component as the existing UV probe plus unchanged runtime defaults. No `src/include/libs` change. Configured analysis plus explicit new-header coverage pass. Historical legacy warnings and both failed prefixes remain retained in the [bridge receipt](evidence/QUAD_LEAF_BRIDGE_20261108.json).
- Candidate source `c1e09a18a107530d250e05ebb55eb6ba28f1800c`; final publication requires exact committed-head 75 CTest /527 Python, pre-commit/links and fresh remote audit/readback. Prototype/bridge native evidence may be reused only with matching compiled inputs and actual images. Final code/checkpoint revisions and PR state are recorded in the session response.
- Once qualified, the final candidate revision and baseline log hashes are recorded separately in `evidence/QUAD_LEAF_BRIDGE_DELIVERY_20261108.json` on the research checkpoint; the draft PR remains the code continuity source.
- Still pending: application selection/call, agreed point rule, physical element/UV-to-XYZ, complete patch boundary, multipatch and adaptation. The synthetic demo's vertex-mean selector is test input, not an adopted scientific centroid formula. This does not close M1/M2/M3 or modernization Stage 3.
