# APMesh QUAD - canonical state and resume point

**Branch:** `quad-templates`

**Entry baseline / unchanged modernization main:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`

**Last session:** 2026-11-09-16 (PR #185 merged into research; native/scientific CI passed; post-merge CI pending)

**Current milestone:** **Isolated read-only real-quadtree UV QUAD bridge integrated in research `quad-templates` via PR #185. Application/physical integration remains pending. M0 remains qualified; M1/M2/M3 remain PARTIAL.**

**Protocol:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md) — includes remote-first continuity across ChatGPT/Codex sessions (2026-11-09).

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

## 2026-11-09 operational handoff checkpoint

- Read/write access to the linked GitHub repository was confirmed; this is not access to any local uncommitted VS Code changes.
- Remote PR [#185](https://github.com/tiagosombrra/apmesh-modernization/pull/185) remains **open and draft**, targeting `quad-templates`, feature head `bb50b161cad0121402cc61475442b32aef33d2bd`. `quad/uv-leaf-bridge` was compared to the PR feature and found identical in Git history in this review. At this checkpoint the PR head and research base are divergent (one base-only commit); review ancestry again at actual integration.
- Previously recorded 117 UV + 30 leaf checks per native profile and 75 CTest /527 Python baseline are **retained historical evidence**, not re-executed in this ChatGPT session. No compilation, native benchmark, local clean-worktree inspection, merge, or source changes were performed; no milestone was closed.
- Every future substantive conversation or Codex session must read live GitHub status first, write a bounded checkpoint on the research branch, preserve feature-PR code separately, and verify readback. An agent that cannot access GitHub must explicitly report that no remote checkpoint occurred. The documentation-only commit of this session is not an exact-head scientific test certification.

## 2026-11-09-10 PR #185 pre-merge inspection

- [Pre-merge review](PR185_PREMERGE_REVIEW_20261109.md) inspected live PR #185 (draft/open), candidate `bb50b161cad0121402cc61475442b32aef33d2bd`, and the divergent base. GitHub reports `mergeable=false`; canonical `STATE.md` and append-only `SESSION_LOG.md` are overlapping changes. Preserve both branches' recorded history before any attempt to merge.
- **No native tests rerun and no code or PR branch changed in this ChatGPT session.** Existing native/regression reports are historical. Shell Git access to GitHub was unavailable here; all verified reads/writes used the connected GitHub integration.
- Next gate: non-destructive reconciliation of the research-branch and PR history, followed by full exact-candidate QUAD + TRI baseline qualification before integrating code into `quad-templates`. Scientific interior-point choice and production opt-in remain open; `main` stays untouched.

## 2026-11-09-11 reconciled PR #185 candidate (validation pending)

- [Exact-head candidate/runbook](PR185_RECONCILED_CANDIDATE_20261109.md) identifies merge commit `c57749e8691907bc25575114191f20782ba16248` on `quad/integration-pr185-20261109`, with parents `37a5771a396ff14dfda1647875df144773d1f9ad` (canonical research) and `bb50b161cad0121402cc61475442b32aef33d2bd` (draft PR #185). The candidate preserves full ancestry, canonical checkpoint files and exact candidate C++/test blobs.
- Remote compare confirms exactly 12 feature files over the prior research base; `main` and the original PR branch have not been changed. This is structural reconciliation, **not** scientific approval.
- **Blocked validation:** no native C++ build, no new 117+30 QUAD outcome run, no 75 CTest/527 Python run and no MSVC/WSL/production oracle requalification here. Shell Git cannot resolve GitHub; hosted workflows are prohibited by repository policy. Existing historical results remain historical.
- Next action is to run the recorded gates on the exact candidate SHA in a clean native worktree, publish complete bounded evidence, and only then consider integrating into `quad-templates`.

## 2026-11-09-12 scoped remote CI available

- Owner-authorized, bounded public GitHub Actions CI is now enabled on the candidate via [workflow](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-pr185-20261109/.github/workflows/quad-research-validation.yml). The prohibition in `AGENTS.md` was revised for free standard runners only (canonical policy commit `2709dd1135b2e751d17b402afcbb6ef4314c9891`).
- [Live remote CI receipt](REMOTE_CI_SETUP_20261109.md) preserves run #42629394523: native Linux QUAD and Windows QUAD jobs **success**; TRI baseline **in progress** when read. A second run #42629587785 for latest feature SHA `73184eb3eb25b2f73452737753cb707c092f18f0` was **pending**. Do not infer a completed exact-final-head gate.
- The workflow is implementation infrastructure, not an alteration of the scientific algorithm. Full delivery regression/scientific oracle qualification, reviewers and branch integration remain open.

## 2026-11-09-13 first CI failure and environment-only repair

- First CI [run #42629394523](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42629394523) on `098b8aeb...`: Linux and Windows QUAD CTest each passed both tests (2/2 per platform), with example 19 leaves /42 quads /53 UV vertices /area 0.25. The TRI baseline CTest completed **67/75 passing, eight failing**. Seven affected entries required historical Git objects unavailable in shallow `checkout`; the `tooling.tidy_header_scope` entry required newer Clang tooling. The run is a **failed CI attempt**, retained without concealing any original gate.
- Fixed only the GitHub Actions runner setup: `fetch-depth: 0` and pinned `clang-tidy==22.1.8`, `clang-format==22.1.8`; candidate workflow commit `1f87f8c270df5da0bd662fa147db32cb76fb44de`, canonical workflow update `aed5e517d897d0d8acd27208dab61cdfe13693e9`. No scientific test, C++ source or acceptance oracle modified.
- [Corrected CI run #42630886815](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42630886815), SHA `1f87f8c270df5da0bd662fa147db32cb76fb44de`: **in_progress** when inspected; no passing final-head delivery conclusion yet. The previous policy-head run was superseded/cancelled in its TRI baseline. Future conversations must read the latest remote run status instead of these snapshots.

## 2026-11-09-14 final native CI pass and scientific equivalence launch

- [Run #42630886815](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42630886815) **completed success** on `1f87f8c270df5da0bd662fa147db32cb76fb44de`. Checked complete job logs: Linux native QUAD CTest 2/2; Windows MSVC native QUAD CTest 2/2; reference TRI application compiled; 75/75 CTest and 527/527 Python unittest controls passed, with no reported failures. Both QUAD demos emitted 19 source leaves, 42 quads, 53 UV vertices and area 0.25.
- [Experimental scientific comparison run #42633924826](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42633924826) launched on candidate workflow commit `602f04a26c28a163c179969763eef2813351634e`; added a separate Linux job that builds frozen `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` and candidate with the same compiler/flags, executes Eistute and Book with original 300s model budgets, independently validates full accepted/rejected states and boundary incidences, then requires byte-identical OBJ and exact comparison fields. **In progress**, no completed scientific pass claimed.
- This historical-baseline comparison is an additional required gate; it does not replace original memory-sanitizer qualification, scientific adviser decisions, numerical centroid rule, boundary integration or independent M1–M3 review. The original PR #185 and `main` remain unchanged.

## 2026-11-09-15 independently compared TRI science, archive repair underway

- [Scientific run #42633924826](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42633924826) (candidate `602f04a26c28a163c179969763eef2813351634e`) compiled frozen TRI reference and candidate with matching GCC/flags; executable SHA-256 was **identical** `4d5861edfc3bd69cfc03f841550a0e55aa3f74f5b1403459836ffda9de707ab5`.
- Both Eistute and Book reference/candidate model processes exited zero. The independent `verify_generation.py --baseline ... --require-boundary-coverage` step succeeded: Eistute five attempted states, 1168 triangles on last accepted step; Book four attempted states, 4256 triangles on last accepted step; OBJ SHA, acceptance fields, metrics and shared-boundary incidence matched exactly. The step's explicit five/four states and boundary coverage assertions passed.
- **Whole workflow run is not green.** The following artifact-upload step rejected `../apmesh-tri-reference/...` relative paths outside the GitHub workspace. This is a publication/retention failure, not a numerical mismatch. Preserve the original failure report.
- Corrected only the workflow artifact paths: baseline process receipts are copied into the candidate workspace before bounded upload. New [candidate commit `0aa9b2edcfb1ee0a5abb428bf2d032182b9dcf4b`](https://github.com/tiagosombrra/apmesh-modernization/commit/0aa9b2edcfb1ee0a5abb428bf2d032182b9dcf4b); [run #42634304685](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42634304685) was in progress at this checkpoint.
- Full latest-head green CI, independent scientific evidence capture and original M1/M2/M3 research approvals are distinct; `main` and draft PR #185 remain unchanged.

## 2026-11-09-16: research PR #185 integrated with exact-tree CI evidence

- [PR #185](https://github.com/tiagosombrra/apmesh-modernization/pull/185) is **MERGED** into `quad-templates` at `514f92ea4fac97ec09445996ca659aa544f91461`. The tested synthetic GitHub PR merge `af3e34749a42b924ec03dd24b681389cd59052d4`, PR head `2e10fe199365f181c1e17d3525279cccef470dd6`, and final research merge all share exact tree `d5270ba261c9c1ad99dea9b3557376e978360fdc`. No production `main` change.
- [Full PR workflow #42635829240](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42635829240) **success** on the exact tree: Linux QUAD CTest 2/2, Windows MSVC QUAD CTest 2/2, Linux TRI CTest 75/75, Python tooling 527/527; both Eistute/Book TRI comparisons accepted five/four attempted states with exact OBJ, decisions, metrics and positive boundary incidence. Bounded scientific artifact `13682488092` exists. The earlier failed/aborted CI prefixes remain in history.
- [Integration evidence](evidence/PR185_RESEARCH_INTEGRATION_20261109.json) distinguishes tested implementation, independent numerical oracle, integration SHA and still-open contracts. An on-push `quad-templates` workflow was added in this documentation/policy checkpoint for separate post-merge regression. No result is inferred for that new run until recorded.
- **Research-only integration:** `research/quad` and `tests/quad` are now present on `quad-templates`. No application opt-in code, adopted interior-point/centroid rule, physical QUAD, full boundary, multipatch or repeated adaptation implementation. Do not close M1/M2/M3 or modernization Stage 3.

## Next exact action

Inspect the post-merge GitHub Actions result on the new research checkpoint SHA; retain failure evidence if any. Then implement a separately scoped M3 **opt-in application entry/dispatch** using the integrated read-only UV QUAD bridge, preserving default TRI behavior and refusing to invent an unapproved scientific interior-point rule. Prepare the numerical policy/oracle decision for the advisers and keep M4/M5/M6/M7 separate.

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
