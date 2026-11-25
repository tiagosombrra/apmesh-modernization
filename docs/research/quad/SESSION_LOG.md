# APMesh QUAD — append-only session log

Newest sessions are appended at the bottom. This log is not a substitute for [STATE.md](STATE.md), which contains the single current handoff. Corrections must be explicit entries, not silent rewrites.

## 2026-11-08-00 — Research branch and planning (reconstructed from actual GitHub artifacts)

**Intent:** separate QUAD scientific work from engineering modernization.  
**Verified artifacts:** `quad-templates`, `docs/research/quad/BASELINE_AUDIT.md`, `docs/research/quad/IMPLEMENTATION_ROADMAP.md`.  
**Engineering baseline:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (modernization PR #183).  
**Outcome:** branch created and roadmap/audit committed. The temporary long-named branch was deleted by the user and `quad-templates` retained.  
**Limit:** source inspection only. No QUAD implementation or native verification recorded.  
**Decision:** preserve TRI as the default, isolate scientific QUAD mode and require explicit validation before integration.

## 2026-11-08-01 — Introduce durable continuity, start M0 (current session)

**User request:** every QUAD research conversation must leave a durable GitHub state record usable from any future chat or VS Code agent. Begin the plan now.

**Changes:**
- Add the mandatory [conversation handoff protocol](CONTINUATION_PROTOCOL.md).
- Add the canonical [current state](STATE.md), this session log, and the [M0 evidence ledger](M0_EVIDENCE.md).
- Extend root `AGENTS.md` for branch-scoped handoff; retain all original modernization safeguards.
- Cross-link the continuation rules in [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md).

**Verified starting facts:**
- GitHub branch search returned `quad-templates`, with no obsolete `research/quad-templates-bento1993` branch.
- `BASELINE_AUDIT.md` and `IMPLEMENTATION_ROADMAP.md` were fetched successfully from the research branch.
- GitHub returned zero PR workflow runs and zero status entries for baseline commit `f6050ec1`. No green CI conclusion can be inferred.
- README documents local serial configure/build/CTest commands; the root `AGENTS.md` requires local gates and disallows automatic hosted workflows.

**Testing:** no local compiler, CTest, Python scientific checks or QUAD algorithms were executed during the connector audit.  
**Milestone:** M0 *in progress*; native execution and oracle evidence are pending.  
**Next action:** check out branch in isolated worktree, run recorded local qualification and frozen scientific comparisons, update M0 evidence, then start M1 only if M0 exit criteria are satisfied.  
**Limitations:** GitHub source inspection and metadata are not a substitute for an executed build. The protocol does not auto-run after a conversation ends.

**Delivery checkpoint (verified remote writes):** `CONTINUATION_PROTOCOL.md` at `dec71454`; `STATE.md` at `2f05ca64`; `SESSION_LOG.md` initial creation at `693fdd87`; `M0_EVIDENCE.md` at `2fd7a14d`; root `AGENTS.md` at `3363a2d8`; `IMPLEMENTATION_ROADMAP.md` at `61a625e2`; root `README.md` at `c3bf3440`. All file paths were read back through GitHub after the initial writes (README is the final navigation addition). No production code, TRI pipeline, or `main` file was changed. The current session's final log entry and state checkpoint constitute additional documentation-only commits.

**Result:** continuity procedure installed and discoverable from both `README.md` and `AGENTS.md`; M0 evidence ledger remains open with no native run.

## 2026-11-08-02 — M0 executable baseline attempted; environment blocker retained

**Intent:** execute M0 from the latest research checkpoint, report actual results and proceed only after gates.

**Remote verification:** initial `main` head `f6050ec1`, initial `quad-templates` `f9e1f868`, zero open PRs. No changes to `main`.

**Actual operations and observations:**
- Inspected the prescribed CMake presets, `tools/quality.py`, `tools/run_generation_case.py`, Eistute/Book configs and current quality guidance.
- Read GitHub’s untruncated recursive source tree (2,589 entries) and counted 164 `src/include` C++ files (76 implementations, 88 headers). Recorded a **targeted, not exhaustive**, scan of 15 high-risk existing files in [M0_TRI_DEPENDENCY_SCAN.md](M0_TRI_DEPENDENCY_SCAN.md).
- Attempted an authenticated-free `git ls-remote` from the available Linux execution environment. Git exited 128: cannot resolve `github.com`. No source checkout was created.
- Installed [`tools/quad_m0_baseline.py`](../../../tools/quad_m0_baseline.py) in the research branch: strict branch/ancestry/clean preflight, GCC/MSVC presets, full GCC CTest, opt-in isolated Eistute/Book runs using unchanged 300-second scientific timeout, hashed logs and partial-failure JSON.
- A prepared local copy of the runner passed Python syntax/help checks; its negative preflight returned exit 2, `blocked_preflight`, with no subprocess tests. The exact GitHub upload has not been compiled/executed from a checkout.

**Testing and classification:** GCC/MSVC builds **NOT RUN**, CTest/Python suite **NOT RUN**, scientific oracle comparisons **NOT RUN**, ASan/MSVC/CRT **NOT RUN**. Script-preflight negative smoke is **not** an application test. Precise results and limitations are in [M0_EVIDENCE.md](M0_EVIDENCE.md).

**Decision:** M0 remains **BLOCKED**, not passed. Do not start M1 or silently relax an oracle. Continue on a genuine local `quad-templates` worktree and capture required logs/hashes; then update state and this journal before closing the next session.

**GitHub artifacts:** runner commit `0e51325b549d1d9efffc29f1769fa56de07ce405`; targeted scan `274e77ddb985f83219aaac64c45a8d4bab48c595`; M0 evidence update `27f3fa200ca672b1cc44c43c1a0b0125b8a9d3c0`. The final state checkpoint follows this entry.

## 2026-11-08-03 - review local continuation and recovered M0 evidence

**Intent:** analyze `quad-templates`, verify the current process and establish the next executable work item.

**Entry:** research head `e8c55184f112d9ffb4fa004a9c9d88f5cf17ff49`; main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; clean isolated worktrees; authenticated remote access works; no open PRs or returned commit statuses/PR-triggered workflow runs.

**Findings:** no QUAD implementation exists. Source review confirms six neighborhood classes, boundary-cell exclusion, triangular Face storage and triangular adjacency consumers. The runner omits full Python, independent oracle and memory qualification; CTest runs only in GCC mode. M0 remains the one active milestone.

**Recovered evidence:** pre-existing local `build/quad-m0/20261108T141009Z-msvc/` at exact entry source records MSVC C++17 Debug configure/build and both capped article executions, followed by a missing-PATH doctor failure. This session reran no native operation. All eight log hashes and current executable match the capture.

**Actual review:** exact-checkout runner syntax/help pass. Offline unchanged-verifier/exact-artifact comparison passes for MSVC: 9 states, 45 scientific artifacts, 123 positive boundaries and preserved accepted/rejected decisions. Full-precision physical/UV quality is available; reference and capture manifests stay unchanged. Local environment discovery fails; iteration planning fails on a missing worktree-local baseline. WSL availability only: Ubuntu 24.04 / GCC 13.3 / CMake 3.28.3 / Ninja.

**Changes:** state, evidence, this journal, compact MSVC receipt and roadmap evidence summary. No production/build/input/test or modernization-document changes.

**Handoff:** M0 PARTIAL / OPEN. Prepare local validation prerequisites, then execute clean WSL GCC and complete full CTest/Python, GCC science and applicable memory gates. Do not repeat MSVC generation for a profile fix. M1 awaits M0 and verified historical fixtures. Boundary topology and first-paper scope require adviser alignment. No QUAD scientific delivery or main merge is claimed. Checkpoint commit and remote readback are reported in the session response.

**Documentation checks:** five-file whitespace passes. Full changed-document link validation stops on an inherited four-parent runner link in the earlier M0 evidence; the historical journal has the same path. Earlier entries remain intact; the corrected current link is [the runner](../../../tools/quad_m0_baseline.py). This is a retained documentation finding, not a passing link gate.

## 2026-11-08-04 - native baseline and GNU validation portability

**Intent:** continue M0 qualification from the verified checkpoint and preserve completed/pending results.

**Entry:** `quad-templates=d400f37da8184b8cec6e1a40ff69d34f3e9c8ed1`, main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, clean worktrees and no open PRs. Authenticated Windows Git remains the continuity channel.

**Preparation:** native Linux Git cannot read the Windows worktree's drive-letter pointer. Create an isolated WSL clone at the published source SHA, prepare local validation profiles/baseline and required development tools. GCC stays 13.3/C++17; LLVM 18's unsupported-key failure is preserved, then LLVM 22.1.8 is installed without changing the configuration or disabling diagnostics.

**Bounded repair:** Windows-specific allocation symbol mangling blocks the Linux full build; a dynamic C++ runtime later bypasses string-copy denial. The inventory also uses host-dependent Path order. A six-file engineering delivery detects size_t type, links only the GNU test probe's C++ runtime locally, makes inventory order explicit, adds one mixed-case regression and a standalone calibration, and refreshes the build fingerprint. No production source/input/preset/scientific-policy change.

**Actual evidence:** complete Linux head and research-merge regression pass 75 CTest / 527 Python without skips. Original 526 IDs are preserved. Windows has six affected native entries and 527 Python controls in their recorded scopes. The old-ordering negative control is detected; dynamic/static allocation calibration records zero/one actual denials respectively. Fresh Linux Eistute/Book preserve 9 states, 45 exact artifacts, 123 positive boundaries and accepted/rejected decisions. The MSVC captures remain untouched.

**Negative evidence:** retain original link failure; stale generated hash; cross-host inventory mismatch; failed snapshot copy-denial context; clang-tidy 18 configuration failure; and local summary-controller failure after successful CTest. The last is verified offline using complete LastTest.log, with no native repetition for the parser. Every source/tool prerequisite change has a distinct capture directory. All 168 copied native artifacts are byte-verified.

**Delivery:** [PR #184](https://github.com/tiagosombrra/apmesh-modernization/pull/184), qualified head `d11b83c33c6fc68892ea72d42c0cd5a1ba5aa205`, research merge `a29711bea1e38f6a1ea49dde443f0ae58ebadfa7`; identical trees, guarded checkout preserves 2,368 tracked timestamps per checkout. Exact post-merge 75/527 passes, and matching executable/tree permits science reuse. Zero returned remote statuses/check-runs is not passing CI. Main and its canonical state/plan remain untouched; the research source inventory updates its technical CMake fingerprint.

**Checkpoint:** [GNU receipt](evidence/M0_GNU_QUALIFICATION_20261108.json), state, evidence, expanded source scan and roadmap summary. M0 is PARTIAL / OPEN. G6 memory applicability/identity and G7 semantic TRI consumer/loop disposition remain pending; inherited historical link errors remain explicit. No M1/QUAD implementation or scientific decision is admitted. Next session continues G6/G7 with these artifacts, without repeating the completed baseline or articles.

## 2026-11-08-05 - current memory applicability and frozen serial inventory

**Intent/entry:** complete M0-G6/G7 from published `bb56d0741acdef9d775186c83bac7832a2e5c43f`; main remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Initial remote branch/PR/status audit found no concurrent research advance or open PR. Windows environment/iteration planning pass; zero selected documentation iteration tests is not validation. Session changes only research documentation/evidence.

**G6 actual work:** offline compiler-read/binary/log audit reuses current Node 22 outcomes/46 denials. Earlier UV records have two changed repository headers and earlier complete-process Linux has 11 changed dependencies; both are rejected as current while retained historically. Refresh unchanged UV21 on current MSVC ASan/CRT: all pass, 293 current read dependencies per profile, real negative controls, 342 transfer, six root and 3,470 tree-denial sites. Refresh existing separate Clang 18 UBSan/LSan fixed Linux inventory: 32 SP01-SP08 production observations plus five controlled SP09/SP10 terminal contexts per profile pass; 76 production units/78 controlled groups checked. Same controllers, models, configuration, caps and oracles; no hidden retry. Instrument runtime/control binary/source/raw identities independently verified for calibration reuse. Eight instrumented article comparisons pass; per instrument 18 states/90 exact scientific artifact pairs/246 positive boundaries. Copy 959 raw Linux records with byte identity. Exact command/cap/log/source manifests stay in `build/quad-m0/session-20261108-05/` and its native Linux origin.

**Preserved negative evidence:** old captures remain historical. An offline diagnostic reader initially expects a symbolic label literally; retain its failure, use the unchanged existing CRT regex, and re-audit without repeating native work. Prior build, instrument and parser failures remain recorded.

**G7:** complete reviewed static serial contract register, source census 164 files, compiler-selected Generator/Adapter activity and all 38 explicit cast dispositions (16 selected serial, 17 excluded, five compiled nonselected). Include implicit TRI loops/metrics/producer/export and physical-versus-UV ownership semantics. This is not runtime QUAD/external-caller/parallel proof.

**Navigation correction:** change only 18 relative hrefs (16 audit, one evidence, one historical journal) from four parent traversals to three. Preserve historical result/assertion text and failed-link observations; original targets/byte hashes are retained locally in `navigation-repair.json` and earlier Git blobs. All eight research documents now pass local target existence; URL/fragment validation is not claimed.

**Closure/handoff:** evidence includes a six-area code/tests/contracts/docs/scientific/known-gap audit. M0 technical inventory is complete with explicit exceptions, subject to the final committed checkpoint full 75/527 delivery gate and fresh remote readback before publication. Run `python3 tools/validation_session.py plan --scope delivery` and `run --scope delivery` on the exact native checkpoint, preserve generated report/JUnit/full LastTest.log and compare source inventories; do not repeat article/memory captures when every dependency remains identical. A failed gate blocks publication/admission. No main merge, Stage 3 closure, QUAD implementation or scientific topology choice. Next work after the successful checkpoint gate is independently verifying Figure 7 ordered T1-T6 topology/orientations/incidences; unresolved scientific choices require adviser alignment before executable fixtures/emission. The final session response records the verified checkpoint hash and exact regression result.

**Measured closure supplement:** exact checkpoint `5b928375d3033a0ab67150987123b8956562a362` passes 75 CTest /527 Python, no failures/skips, with full JUnit/LastTest.log/inventory readback and clean source. The [closure receipt](evidence/M0_CLOSURE_20261108.json) freezes commands and hashes. Preserve an initial offline seal-reader key error; inspect the existing schema and read the same capture correctly without native repetition. This technical M0 qualification admits only the historical reconstruction next. Final documentation seal must itself pass the complete exact-head gate before push, and remote readback must match; session response records that final SHA/result. Main remains unchanged.

## 2026-11-08-06 - primary-source Figure 7 transcription

**Entry/scope:** remote and local `quad-templates=069e9fb8bb8674a84baaf3cdfd04dde6799a1911`, clean research/main trees, `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; no open PRs or returned statuses. Continue the admitted M1 source reconstruction only. No production/build/test/input/scientific-policy change.

**Source discovery:** public primary coauthor bibliography confirms title/authors/pages, but search does not obtain the full paper; publisher archive request times out. Find the original seven-page scan in Downloads (5,439,448 bytes; SHA-256 `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`). Connected Drive search locates a same-title/size candidate; metadata does not expose usable content hashes, so remote byte identity remains unverified. No files/messages/sharing settings are written in Drive. Text extraction returns only page separators; read actual page renders instead. Inspect authorship, balancing/interior discussion, Figure 7 on p. 288 and boundary discussion on pp. 289-290. Preserve the initially mispositioned detail crop separately; use the corrected 800-dpi pattern detail for the fifth graph.

**Actual reconstruction:** new [historical review](M1_HISTORICAL_ORACLE_REVIEW.md), ordered JSON graph and new review SVG. Printed columns are T1,T2,T4,T3,T5,T6 under current source class names, not sequential type numbers. T5 has no center junction; intermediate triangle polygons appear in T2/T5. Explicit normalized CCW schematic graph yields conditional later subdivision counts 4,11,12,8,11,16; no runtime generator is implemented. Numeric embedding/centroid interpretation are proposals for adviser review. Boundary text permits retained triangles and does not establish general all-quad output.

**Actual checks:** offline exact-rational schematic audit passes 48 D4 observations, area/incidence/orientation/strict-convexity/Euler checks and all 16 geometric boundary split signatures. Six deliberately altered records are detected (missing, reversed, repeated, duplicate, T3/T4 swap and invented T5 center). Chrome headless renders the new SVG for visual inspection. These are documentary checks, not new CTest/Python inventory or scientific runtime evidence. Existing environment/iteration plan pass with zero selected iteration tests; that is not regression qualification. Raw helper/commands/render/audit artifacts stay under `build/quad-m1/session-20261108-06/`; compact receipts retain hashes. Source scan is not redistributed.

**Closure and handoff:** six-area code/tests/contracts/docs/scientific/known-gap review is in the historical review. M0 remains qualified; M1 is PARTIAL / REVIEW PENDING. Independent reviewer confirmation, numerical embedding/centroid alignment and executable fixtures remain; M2 is not admitted. No production/scientific decision or modernization integration. Before publishing this documentation checkpoint, require pre-commit, research local links, complete exact committed-head 75 CTest /527 Python and fresh remote branch/PR/check audit, then push and compare readback. The session response records that final hash/result; absence or failure blocks publication. Next action is to review the concrete six-cycle table and numeric questions with the advisers before isolated M1 fixtures.

## 2026-11-08-07 - implement working isolated UV QUAD generation

**Steering/entry:** user explicitly prioritizes implementation and reports adviser alignment already exists, with specific decisions to follow. Entry `quad-templates=97536dd75305251218dbdfe0da354e33a76717e5`, main `f6050ec1`, clean worktrees and no open PRs/statuses. Create candidate `quad/m01-uv-prototype`; keep production sources/build/input/oracles unchanged.

**Implemented:** value-owned UvVertex/UvQuad/UvMesh, index-based polygon input, canonical edge-midpoint registry and one emitted four-node quad per original polygon corner. Interior points are supplied by the caller; no automatic centroid or adviser numerical decision is invented. Validate finite coordinates, strict convexity/orientation, incidence/order, identity, crossing/overlap/hanging nodes, boundary manifoldness, connected disk/Euler and expected area. Construction is local and input-preserving. Separate locale/format-independent four-index OBJ exporter and runnable eight-quad demo. Standalone CMake/tests remain outside production targets.

**Measured:** implementation `e88081d2e2a80ea1baa8b988dc8f3888f19a62c1` passes 117 native outcomes per Linux GCC13.3, Windows GCC16.1 and checked-MSVC19.44 C++17 Debug profile. Includes 48 graph transforms, 32 bounded grids, actual 19-quad 2:1 seam with shared midpoint IDs, analytic connectivity/count/area, invalid geometry/topology and I/O controls. Initial 84-outcome captures are retained before expansion; later source changes (writer format/locale isolation and demo path existence check) have separate source-bound captures. The first cross-platform OBJ audit fails on 23 Windows CRLF records versus Linux LF; preserve original bytes and the failed summary prefix, open the demo output in binary mode, and capture fresh native exports without comparison normalization. Windows eight CLI contexts pass; final Linux/Windows-GCC/MSVC raw OBJ SHA-256 is identical. Demo reports 15 vertices, eight quads, area two, 12 boundary/10 interior edges. Linux existing format and configured clang-tidy pass for all three new TUs; no diagnostics disabled. Raw reports/helpers/logs/builds and rendered native OBJ visualization are local under `build/quad-prototype/session-20261108-07/`, compact receipt in the candidate.

**Closure review:** code is an isolated working research capability, not a production algorithm change; tests are native positive/negative and separate from baseline; contracts include explicit ownership/IDs, disk/tolerance and supplied-point semantics; documentation includes build/run instructions; scientific point policy remains external pending supplied decisions; known gaps include allocation-denial/extreme-coordinate campaigns, holes/exact predicates, real leaf emission, XYZ/curvature, boundary, multipatch and adaptation. M1/M2 remain partial and Stage 3 remains open. Complete exact-final-candidate production 75/527, pre-commit/local links and fresh remote gates before publishing a reviewable draft PR to `quad-templates`; update the research checkpoint and verify readback. Exact final hashes/review/results are in the session response. No production/memory/article campaign is added for unchanged production identities.

**Required-gate prefix:** exact candidate `5debb110f7066dc58050afccb67b295aa2e6630d` stops at architecture inventory, before production build/CTest. The new standalone `tests/quad/CMakeLists.txt` is a required build-fingerprint input; regenerate only that added inventory entry, retain the failed report, and qualify the corrected exact revision. No test, diagnostic or scientific oracle is removed.

**Published review supplement:** draft [PR #185](https://github.com/tiagosombrra/apmesh-modernization/pull/185), head `1178720474c4b6efae37d01534648a1a8788ed2d`, targets `quad-templates`. Exact candidate full baseline passes 75 CTest /527 Python without failure/skip; code/build hash binding retains all 117 native outcomes per profile and final binary OBJ comparisons. No remote statuses/check-runs exist. Candidate code remains unmerged. A separate clean worktree `apmesh-quad-checkpoint` records this canonical research status/evidence without modifying the main worktree or removing the locally reviewable prototype. The checkpoint itself must pass exact-head full baseline before push/readback; final source hashes and results are reported in the session response.

## 2026-11-08-08 - visible primary checkout and actual quadtree bridge

**Intent/entry:** user cannot see implementation in the current source workspace and requests continuation. Primary `apmesh-modernization` is clean on main `f6050ec1`; implementation is committed in separate worktree `apmesh-quad`, draft PR #185 head `fac4cfbf8157ac70e568ed24b3d284c44f1a841a`; research checkpoint `cf2795746b278cdcca91fde86d87614782624c85`. Verify remote/PR. Switch the clean primary checkout to new `quad/uv-leaf-bridge` at the verified prototype head; preserve the historical main branch. No copying research code into main and no overwrite of concurrent edits. Source Control pending changes differ from committed Explorer/history content.

**Implemented:** actual `Quadtree`/`QuadtreeCell` leaf capture with unchanged publication order, reciprocal neighbor/2:1 and dyadic hierarchy checks, depth cap 30, T1-T6 rotation/class mapping for all 16 masks, canonical grid-key UV identities, source boundary exclusion and caller-supplied points. Emit through existing isolated QUAD subdivision/validation; no source-tree refinement/sort/owner publication. Optional standalone `AP_MESH_QUAD_WITH_TREE=ON` reuses the existing 14-source UV component plus actual runtime defaults. New native fixture/demo use the public legacy APIs and a closed square contour. No production source/input/formula/policy changes.

**Measured:** source `c1e09a18a107530d250e05ebb55eb6ba28f1800c`, 117 core +30 bridge outcomes per GCC16 Windows, checked-MSVC19.44 Debug and GCC13 Linux. Actual uniform/adaptive trees and all 16 signatures pass, including existing TRI object/position/ID/list/stat preservation, source-neighbor-order independence, invalid/unbalanced/foreign graphs and selector failures. Native demo: 19 leaves, 42 quads, 53 vertices, area 1/4; identical raw OBJ across three platforms and eight Windows CLI observations. Linux format/static analysis pass on all three new TUs, with explicit new research/test header coverage. Existing legacy warnings remain visible. Thirteen copied Linux report/log/metadata/OBJ artifacts are byte-verified; local raw root `build/quad-leaf/session-20261108-08/`, compact bridge receipt retained.

**Negative evidence:** first GCC batch reaches the TRI-preservation entry and crashes on null Boundary. GDB identifies `Boundary::getLastVertexId(this=nullptr)` called by historical `makeTemplateBasedMesh`; fix fixture preconditions/ownership to a real closed contour, retain output/debugger/binary prefix and change no production code. Later MSVC rejects duplicate-neighbor data with reciprocity before duplicate because pointer-map iteration differs. Preserve that failure; validate all local neighbor-list shapes before cross-cell relations so the existing exact rejection oracle is retained. Distinct source-bound captures follow both identified corrections; no native retry to disguise a failure. No model, timeout, reference or diagnostic is weakened.

**Closure review:** code is a read-only bridge outside production targets; tests are real native positive/negative and separate from baseline; contracts cover dyadic identity/order, temporary source observers and value-owned results/callback exceptions; docs explain visible checkout/API/build commands; scientific point rule remains external and default TRI/boundary policy is unchanged; known inventory retains legacy diagnostics, failed prefixes, disk/depth limits, missing extreme/denial qualification and absent application/XYZ/boundary/multipatch/adaptation integration. M1/M2/M3 and broader Stage 3 remain open. Before publication, run full 75 CTest /527 Python on the final committed head, review staged bytes, fresh remote heads/PR/checks and readback. Extend the existing draft review and checkpoint quad-templates; exact final revisions/results are reported in the session response.

## 2026-11-09-09 - remote-first cross-conversation handoff

**Intent:** User elected to continue the QUAD implementation through this ChatGPT conversation and future independent conversations, in addition to local Codex/VS Code work. Verify the connected GitHub permissions and establish a durable handoff without modifying the research algorithm.

**Remote preflight:** GitHub repository `tiagosombrra/apmesh-modernization` is public with authenticated push permission; research `quad-templates` and draft PR [#185](https://github.com/tiagosombrra/apmesh-modernization/pull/185) are accessible. PR base `quad-templates`, head `quad/m01-uv-prototype` at `bb50b161cad0121402cc61475442b32aef33d2bd`, unmerged. Research base and PR were divergent by one base-only commit and seven candidate commits at this inspection. Do not assume the local Windows checkout or its uncommitted changes can be read by the GitHub connector.

**Change:** Update the existing continuity protocol with remote-first branch/PR SHA checks, local versus remote boundaries, non-destructive concurrent-edit handling, canonical versus experimental ownership, exact-test reporting and session-end verified checkpoint rules. Update canonical STATE.md with an operational handoff, without changing implementation or scientific decisions.

**Executed:** GitHub metadata, PR, compare and document read; authenticated repository write and remote readback are required to close this documentation checkpoint. **Not executed:** C++ build, CTest, Python control suite, MSVC/WSL source runs, code merge, GitHub Actions or inspection of uncommitted local work. Previous test results are historical only; this documentation-only checkpoint is not scientific qualification.

**Next:** Review PR #185 and the outstanding point-selection/centroid scientific rule, reconcile the branch ancestry with upstream before integration, then implement a separately gated opt-in application path preserving TRI. Read the latest state and PR SHA anew in any resumed conversation.

## 2026-11-09-10 - PR #185 integration-readiness audit

**Scope:** inspected draft PR #185 and current research base for the next executable gate. Candidate `bb50b161cad0121402cc61475442b32aef33d2bd`, base observed `d85b5edc5cc4ef32673f9eb5967a7cd8d3fb570d`, `7` candidate-only versus `4` base-only commits, GitHub `mergeable=false`. Canonical `STATE.md` and `SESSION_LOG.md` require non-destructive reconciliation. [Full audit](PR185_PREMERGE_REVIEW_20261109.md).

**Changes:** new technical pre-merge review and canonical next-action update only; no research C++ sources, test logic, existing historical evidence, PR branch, default TRI algorithm or `main` modified.

**Executed:** live GitHub reads and targeted source inspection; new report and state committed/read back. **Not executed:** new native compilation, 117+30 QUAD test controls, 75 CTest/527 Python, scientific comparisons, merge, MSVC/WSL/local worktree inspection. Native Git network to github.com unavailable in this session. Absence of remote checks is not a passing check.

**Next:** integrate base into feature safely while preserving both documentation histories, run exact merged-candidate gates, then review the PR for research-branch integration. Scientifically adopted centroid and production opt-in remain separate tasks.

## 2026-11-09-11 — non-destructive PR #185 merge candidate

**Entry:** researched current remote canonical base `37a5771a396ff14dfda1647875df144773d1f9ad` and PR #185 `bb50b161cad0121402cc61475442b32aef33d2bd`, with `main` separate. Native shell `git ls-remote` failed DNS for github.com; the authenticated GitHub connector remained usable. Repository policy rejects automatic/paid Actions.

**Implemented:** Published the two-parent merge commit `c57749e8691907bc25575114191f20782ba16248` on isolated branch `quad/integration-pr185-20261109`. Started from the exact canonical research tree; inserted only the 12 exact feature blobs (seven `research/quad`, four `tests/quad`, one build inventory). The canonical `STATE.md`, `SESSION_LOG.md`, handoff protocol, roadmap and evidence were retained. GitHub compare verifies both parents are ancestors and only the intended feature paths differ from the initial canonical base. No force update, history discard, `main` change, original PR branch mutation, production `src/` modification or algorithmic formula change.

**Gate result:** Structural reconciliation passed remote readback. **NOT RUN:** native compile, standalone QUAD checks, 75/527 application baseline, scientific Eistute/Book captures, MSVC/WSL, memory and remote CI (none configured/permitted). No gate was silently declared green. See [candidate and exact qualification commands](PR185_RECONCILED_CANDIDATE_20261109.md).

**Next action:** run the specified clean-worktree exact-head native qualification and retain raw reports/hashes. Only after passed gates/review integrate code into `quad-templates`. Scientific M1/M2/M3 remain partial.

## 2026-11-09-12 — owner-authorized public remote CI

**Intent/constraint:** User requires end-to-end development and verification from ChatGPT, independent of their VS Code machine. GitHub connector writes work, while container shell DNS cannot resolve github.com. Research root `AGENTS.md` previously barred hosted workflows; user explicitly authorized necessary adjustments.

**Implemented:** created scoped [QUAD research workflow](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-pr185-20261109/.github/workflows/quad-research-validation.yml) on isolated candidate in commit `098b8aeb12858567a9602a8d523bf844996a0461`. It uses free standard public repository Ubuntu/Windows runners, readonly contents access, short artifact retention, no secrets/paid runners/deployments/automerge. Candidate policy update `73184eb3eb25b2f73452737753cb707c092f18f0`; canonical `quad-templates` root `AGENTS.md`/`README.md` policy updated at `2709dd1135b2e751d17b402afcbb6ef4314c9891`. QUAD C++ sources and production `main` untouched.

**Measured:** GitHub pushed workflow run #42629394523 on commit `098b8aeb...`: standalone Linux QUAD and Windows MSVC QUAD job steps completed successfully; full TRI baseline job still in progress. The final policy candidate run #42629587785 for `73184eb3...` is pending; exact-final-head validation is not claimed.

**Open gates:** Actual TRI baseline completion, final feature-head CI logs, exact original 75 CTest/527 Python admission, Eistute/Book scientific comparisons and memory/ownership gates. No M1/M2/M3 closure, PR merge or main changes. See [bounded remote CI receipt](REMOTE_CI_SETUP_20261109.md).

**Next:** inspect latest run jobs/logs, fix real failures without relaxing oracles, then publish exact candidate evidence for review.
## 2026-11-09-13 — hosted TRI CTest first failure and environment repair

**Observed:** Run #42629394523 executes both QUAD native jobs successfully (2/2 CTest per Linux GCC and Windows MSVC, demo 19/42/53/0.25). TRI baseline produces **67 passed / 8 failed of 75** CTest entries. Seven fail when tests call `git show` for historical frozen SHA/path records absent from shallow `actions/checkout`, including tooling.controls with six affected Python lookups. One scope check fails due runner's older clang-tidy rejecting `ExcludeHeaderFilterRegex`. Failure logs and bounded uploaded artifact are retained, with no changed scientific reference.

**Correction:** Updated only workflow on candidate and scientific base with `fetch-depth: 0` and environment-local PyPI LLVM `clang-tidy==22.1.8`/`clang-format==22.1.8` wheels. Candidate `1f87f8c270df5da0bd662fa147db32cb76fb44de`; canonical `aed5e517d897d0d8acd27208dab61cdfe13693e9`. Superseded runs may be cancelled; do not recast them as passes. Corrected run #42630886815 launched.

**Not yet qualified:** complete exact-candidate 75/527, independent Eistute/Book scientific comparisons and broader memory claims. No source, unit test or acceptance policy modified, no PR merge, no main update. Next read corrected CI and, if it passes, expand independent scientific qualification without relaxing gates.
## 2026-11-09-14 — remote native qualification passed; physical TRI oracle campaign started

**Measured complete CI:** [run #42630886815](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42630886815) on `1f87f8c270df5da0bd662fa147db32cb76fb44de` finished success. Inspected decoded GitHub job logs: Linux GCC QUAD 2/2 CTest, Windows MSVC QUAD 2/2 CTest; both demos 19 leaves, 42 QUADs, 53 UV vertices and 0.25 area. Linux production TRI build succeeded, 75/75 CTest succeeded, 527/527 Python `unittest` controls succeeded. Initial eight CI failures and environment fix remain documented separately; no failed evidence discarded.

**New scientific check:** candidate `602f04a26c28a163c179969763eef2813351634e` adds only workflow job `scientific-tri-compare`: build original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` in a separate Git worktree and the candidate using the same Ubuntu compiler/flags, assert unchanged `src/`, `include/`, `configs/`; execute Eistute/Book with 300s caps per model; verify original and candidate using the existing independent geometry/quality/boundary checks and require equal accepted/rejected state trace, metrics, output OBJ bytes and positive boundary incidence. [Run #42633924826](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42633924826) launched; its outcome was **in progress** at checkpoint. Do not claim final equivalence prematurely.

**Unexecuted/unqualified:** end-to-end scientific output comparison pending; full original owner/ASan/LSan/CRT campaigns on current CI are not included; neither historical point rule approval nor production QUAD opt-in exists. No PR merge or production `main` update; M1/M2/M3 remain partial. Next: inspect science job reports and fix real failures without lowering scientific oracles, then reconcile exact delivery candidate and continue review.
## 2026-11-09-15 — independent Eistute/Book oracle pass; artifact upload defect

**Executed science:** [workflow #42633924826](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42633924826), candidate `602f04a26c28a163c179969763eef2813351634e`, built baseline `f6050ec1...` and feature on one Ubuntu GCC runner with identical flags and binary SHA `4d5861edfc3bd69cfc03f841550a0e55aa3f74f5b1403459836ffda9de707ab5`. The four original model runs (reference/candidate Eistute, reference/candidate Book) exited zero. Independent `verify_generation.py` comparison step passed with exact accepted/rejected decisions, metrics, OBJ SHA-256 and boundary coverage; Eistute 5 attempted states and Book 4. Last accepted Eistute 1168 triangles, Book 4256; native generated sources remain identical.

**Actual failure:** the subsequent artifact upload attempted an out-of-workspace `../` path, rejected by `actions/upload-artifact@v4`. Preserve whole job status as **failure** despite passing numerical comparison. This is not an excuse to ignore the failure or to relabel the whole run green. Earlier failure/cancellation and scientific pass step remain in GitHub job logs.

**Repair:** only workflow packaging changed: copy bounded baseline process.json receipts into permitted candidate build directory and upload there. Feature commit `0aa9b2edcfb1ee0a5abb428bf2d032182b9dcf4b`; corrected [run #42634304685](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42634304685) launched and remains to be inspected. No scientific tolerance, input, source, CLI budget or comparator altered.

**Still open:** exact final commit run result, final integrated-base gate, independent memory/ownership scope and M1 historical numeric policy. PR #185 still draft; no code merged to `quad-templates` or modernized `main`. Next check corrected run and exact report, then reconcile source/history.

## 2026-11-09-16 — merged verified UV QUAD prototype into the scientific branch

**Pre-merge verification:** Preserved original PR #185 ancestry by fast-forwarding draft review from `bb50b161...` to `2e10fe199365f181c1e17d3525279cccef470dd6`, with second parent the canonical research checkpoint `3ef6e7c488e08c1e0fc7887926f035d5d2976206`. The PR diff was confined to standalone QUAD source/tests, inventory and scoped CI workflow; source and production TRI path unchanged. The comment review retained scientific scope limitations and was not an adviser approval.

**Measured exact PR gate:** [run #42635829240](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42635829240) completed SUCCESS with four green jobs: Linux QUAD 2/2 CTest, Windows MSVC QUAD 2/2 CTest, TRI Linux 75/75 CTest and 527/527 Python controls, and separate strict frozen-reference Eistute/Book equivalence (five/four attempted states, byte-identical OBJ, acceptance and metrics, verified shared boundary). CI tested synthetic merge `af3e34749a42b924ec03dd24b681389cd59052d4`, whose tree was compared to head `2e10fe199365f181c1e17d3525279cccef470dd6` and proved identical `d5270ba261c9c1ad99dea9b3557376e978360fdc`. Scientific artifact `13682488092` was uploaded. Earlier failure and cancellation attempts are preserved, not relabeled.

**Integrated:** PR #185 was marked ready after this gate and merged with GitHub merge method into research `quad-templates`: `514f92ea4fac97ec09445996ca659aa544f91461`. Post-merge remote fetch proved this commit has the same exact tree `d5270ba261c9c1ad99dea9b3557376e978360fdc`. Default modernization `main` remains at `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; original TRI source/binary inputs unchanged.

**Now:** Added a bounded `quad-templates` push trigger to the already reviewed free-runner workflow, with a `docs/research/quad/**` documentation-only path exclusion, so that post-merge source checkouts have independent CI and future documentation checkpoint writes do not continually rebuild. Store [bounded integration evidence](evidence/PR185_RESEARCH_INTEGRATION_20261109.json), then inspect the post-merge run separately.

**Limits:** The integrated source remains an isolated UV QUAD bridge for interior leaves, with caller-injected point and strictly convex disk validator. Historical numeric T1–T6 oracle/adviser decision, M3 production opt-in, M4 physical XYZ, M5 boundary, M6 multipatch and M7 adaptation remain open. Full ASan/LSan/CRT/denial campaigns are not replaced by the CI CTest. No M1/M2/M3 milestone closure claimed. Next: post-merge CI readback, then gated M3 opt-in work.

## 2026-11-09-17 — exact post-merge CI closure and M3 next slice

**Rechecked:** `quad-templates=3650a50e4101fa9348147cdfb6979c1bad77a7a7`, PR #185 merged, `main` remains `f6050ec1...`. [Post-merge CI #42637555612](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42637555612) completed SUCCESS with Linux QUAD 2/2, MSVC QUAD 2/2, TRI Linux 75/75 CTest and Python 527/527. Exact frozen Eistute/Book comparison retains nine states, byte-equal OBJ output and verified boundaries; logged artifact `13682654557`. Runtime observed 6m19s, not a future guarantee.

**Actions:** publish [post-merge evidence](POSTMERGE_CI_20261109.md), identify real app call graph from verified `src/main.cpp`, `RunApplication`, `RuntimeConfig`, `GeneratorAdaptive` and `AdvancingFront`, and publish [M3 opt-in implementation gate](M3_OPTIN_APPLICATION_DESIGN_20261109.md). This session does not modify production C++ or approve an unspecified numerical centroid.

**Milestones:** baseline M0 qualified in scope; M1/M2/M3 partial, M4-M7 pending. Post-merge CI pending status from session 16 now closed. Separate memory/3D/multipatch/adaptation claims remain open. Next use a feature branch for fail-closed opt-in dispatch and its full exact-head regression.

## 2026-11-09-18 — M3-1 application selector implemented, audited and merged

**Entry:** Canonical research `3f1b81ae...`; no open QUAD feature PR. Existing UV bridge integrated; `main` at `f6050ec1...`. User requested continued autonomous GitHub-based implementation.

**Changes:** isolated feature `quad/integration-m3-dispatch-20261109`, PR [#186](https://github.com/tiagosombrra/apmesh-modernization/pull/186): separate `MESH_ELEMENT_KIND=tri|quad_uv` runtime configuration, default `tri` and independent `USE_TEMPLATE` semantics. QUAD is fail-closed before `ApplyRuntimeConfig`; no false production QUAD output or unapproved point rule. New Linux/MSVC native grammar CTest plus seven direct application CLI refusals. Historical serial input validator fully preserved, architecture SHA-256 inventory regenerated and verified with standard known-answer vector. CI accepts only reviewed production mode/parser file changes; source baseline and science comparisons remain mandatory.

**Failure preserved:** initial head `3313ccd3...`, CI #42678447975, 74/75 CTest: `tooling.serial_reader_preservation` correctly rejected a changed protected `include/input_output/input_validation.h`. Parser was moved into application runtime configuration instead of disabling the oracle. A separate temporary offline inventory SHA computation used wrong round constant ordering and was corrected with independently checked SHA-256 test vector; source hashes in the final candidate reflect actual bytes. Previous failures/cancellations remain in GitHub history.

**Qualified:** exact reviewed head `cb0ec354d725e8db70dc06fca8f62751fc594b2f` run [#42680076066](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42680076066) completed SUCCESS: Linux QUAD 3/3, Windows QUAD 3/3, Linux TRI 75/75 CTest, Python 527/527, seven real CLI deny controls, and strict Eistute/Book scientific parity for five/four states, OBJ/acceptance/boundary equality. Scoped code review and merge-tree check before integration.

**Integrated:** PR #186 merged into `quad-templates` as `e8c465e0ac5e1a127bc89bd4d2971dc4ec0583ca`, same source tree as the reviewed head; modernization `main` unchanged. Post-merge Actions #42681339818 launched, running at checkpoint. [Receipt](evidence/M3_DISPATCH_GATE_20261109.json).

**Limits/next:** M1/M2/M3 remain partial. No actual production UV QUAD, approved numerical centroid, physical XYZ, closed boundary, shared curve multipatch or repeated adaptation. Inspect exact merge-head CI; next M3-2 design targets a read-only leaf capture seam after `AdvancingFront::refineAccordingToNeighbors` before TRI template generation, without changing default behavior. Native sanitizer/denial campaigns and full lifecycle remain outside this first gate.
## 2026-11-09-19 — M3-2 observer merged after genuine native/SCI regression

**Entry:** Canonical `538af191...`, prior post-merge M3-1 CI #42681339818 successful. Started isolated `quad/integration-m3-refined-observer-20261109` and draft PR #187, preserving default TRI behavior and `main`.

**Implemented:** new optional `AdvancingFront::SetRefinedQuadtreeObserver` called after successful neighbor refinement and before TRI templates. No `EmitLeafQuads` call and no numerical centroid. Native contract builds a real square-boundary `AdvancingFront`, invokes the existing read-only `CaptureLeafPolygons` bridge at the live stage, verifies no TRI template publication and exception abort, then validates the empty-observer original TRI path. CMake/native test and source inventory updated; science source whitelist restricts changes to reviewed AFT paths.

**Failed prefix retained:** initial unbounded null-curve synthetic fixture caused Linux 30s CTest timeout and Windows test crash in Actions #42688580750. A separate original science guard correctly failed before the whitelist extension. Added `setMaxLevelCap(3)` **in the test fixture only**, with no production numeric policy changes. The temporary runs and logs remain as negative evidence.

**Passing proof:** exact final PR head `cd5825c19d976be0b9197428d8e77cc79b51c897`, [Actions #42689321763](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42689321763) SUCCESS all four jobs: GCC and MSVC QUAD each 4/4 CTest, TRI 75/75 CTest and 527/527 Python, seven CLI denial controls, Eistute/Book 5/4 state identical OBJ/acceptance/boundary evidence. Source-path and branch-head review verified no unexpected changes.

**Integration:** PR #187 review comment recorded, marked ready and merged to `quad-templates` as `43809cd03578eb03cdfb76b9b150a040ebf13288`. Verified its merge tree equals the tested candidate tree `64c8d440039aac16ee1e0302ce46bac76787d955`; modernization `main` remains `f6050ec1...`. Post-merge [Actions #42690813905](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42690813905) started but remains pending at checkpoint.

**Limits:** The observed object is a mutable legacy `Quadtree&`; read-only is a caller contract, not type-enforced. No full QUAD generated, no approved interior-point formula, no XYZ, complete boundary, multipatch, repeated adaptation or full sanitizer campaign. M1/M2/M3 stay partial. Next: inspect exact post-merge run and design M3-3 value-only patch-level observer registration before any experimental positive generation mode.

## 2026-11-09-20 — post-merge M3-2 exact-head green and adapter insertion review

**Run verified:** GitHub Actions [#42690813905](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42690813905) on merged code head `43809cd03578eb03cdfb76b9b150a040ebf13288` completed SUCCESS with four green jobs; Linux/Windows QUAD each 4/4 CTest, TRI 75/75 CTest, Python 527/527, M3-1 real CLI negatives 7/7, Eistute/Book nine state exact OBJ/acceptance/boundary equivalence. Earlier pending checkpoint superseded without erasing prior negative CI attempt.

**Research:** audited `src/adapter/adapter.cpp` and located both actual `AdvancingFront` entry points: `AdaptDomainOmp` line ~903/execute ~1038, and retry-aware `AdaptDomain` line ~1291/execute ~1393, sharing `ConfigureAdvancingFront` line ~1719. Published [M3-3 adapter capture review](M3_ADAPTER_CAPTURE_REVIEW_20261109.md), no new production code.

**Closure:** M3-2 observer seam and first experimental call path qualified in tested scope; `main=f6050ec1...` unchanged. M1/M2/M3 remain partial. The legacy callback still exposes mutable `Quadtree&`, so true compile-time read-only proof is absent; value-owned attempt captures with provenance are the next M3-3 deliverable. No approved interior point/UV->XYZ/boundary/multipatch/adaptation or full sanitizer claim.

## 2026-11-10-01 — M3-3 experimental value-only patch captures qualified and merged

**Entry:** research `5e96d898...` with M3-2 qualified; user authorized next activity. Built isolated branch `quad/integration-m3-attempt-capture-20261109` and PR #188.

**Implementation:** `research/quad/adapter_capture.h` adds value-owned `AttemptUvCapture` and explicit callback pair. `Adapter::SetResearchUvCapture` installs hooks only per instance; both OMP and retry-aware `AdaptDomain` bind the same configuration seam with patch, step, retry, local attempt. Native tests exercise copied geometry, source lifetime, no adopted centroid, provenance, partial-hook rejection, exception/nonpublication, independent attempts; scientific source whitelist and SHA architecture inventory updated. CLI `quad_uv` remains fail-closed.

**Failure prefix retained:** original head `def82c3b8...` failed TRI build at `attempt_metrics_probe` after removed one-argument signature; repaired with backward-compatible default `PatchAttemptIdentity{}`. Explicit OMP source syntax gate then revealed historical `AppendDomainDebugLog` call missing its `RegionalPatchStats` argument; repaired using existing regional metric function and temporary `SubMesh` RAII in OMP without altering TRI output. Old CI failures are preserved in PR review discussion.

**Evidence:** [#42729761791](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42729761791) SUCCESS four jobs on `b2ec2104...` (Linux/MSVC QUAD 4/4 each, serial TRI 75/75 CTest, tooling 527/527 Python, seven CLI refusals, `USE_OPENMP=1` syntax, exact Eistute/Book 5/4-state scientific parity). Merged PR #188 to `quad-templates` at `078301a27feaffda0a7ecd8d69de1f3ba0d4c71e`; exact merge tree matches tested feature. [Post-merge #42731206966](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42731206966) SUCCESS all four jobs on merge SHA. `main` remains `f6050ec1...`.

**Unresolved:** M1/M2/M3 partial. Capture events provisional, no locally selected/global accepted decision classification; OMP concurrent execution and sanitizers not qualified. No physical QUAD, approved interior point, UV->XYZ, full boundary, multipatch or repeated adaptation. Next: M3-4 explicit per-attempt local disposition with retry distinction, without falsifying global acceptance.
## 2026-11-10-02 — M3-4 local attempt classification implemented, qualified and merged

**Entry:** Canonical `5d6b45d5...` with M3-3 exact post-merge CI qualified. Created isolated `quad/integration-m3-local-decisions-20261110`, PR [#189](https://github.com/tiagosombrra/apmesh-modernization/pull/189).

**Source:** Extended research capture contract with `CaptureHooks::local_selection_sink`, value-only `LocalSelectionEvent` and `LocalSelectionKind` identifying **locally selected for Adapter return**, superseded local candidates and generation failures. `PublishLocalSelections` fully validates duplicate IDs, invalid chosen IDs, selected failures and success-without-selection before any event is emitted. Retained `AttemptUvCapture::PendingTriDecision`. Added bookkeeping to both actual Adapter paths; retry-aware serial path records statuses and publishes only after best/fallback selection; OMP path identifies its sole candidate upon successful SubMesh completion. Production CLI never installs hooks.

**Native/science results:** exact reviewed head `8798ca7a61eddd53862f78db15e4a6225ddf4a3f`, [CI #42785252030](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42785252030) SUCCESS all four jobs: GCC QUAD 4/4 CTest, MSVC QUAD 4/4 CTest, TRI baseline 75/75 CTest, Python 527/527, seven CLI denial cases and conditional `USE_OPENMP=1` syntax check. Strict scientific Eistute 5 and Book 4 states retained byte-identical OBJ, unchanged acceptance fields and exact verified boundary coverage. Reviewer compared exactly five changed paths and validated the SHA-256 source inventory.

**Integration:** PR #189 approved within reviewed scope, merged into `quad-templates` as `1ce8bdc967367714ee780ee52077115252fd465c`, tree SHA `a8891ee1f0419f7af2c7e0e22e66d2d84760ac2e` same as reviewed candidate; `main=f6050ec1...` unaffected. Post-merge [Actions #42786259118](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42786259118) queued/running at checkpoint; must inspect final result.

**Limits/next:** Local selection is *not* global GeneratorAdaptive acceptance. Existing native tests cover pure decision contracts and AFT observation, not a separate hook-enabled real-Adapter patch execution with retry selection; qualify that as M3-5. OMP execution concurrency, multi-subscriber atomicity, sanitizers and numerical/physical QUAD remain unqualified. M1/M2/M3 partial, production quad_uv still blocked.
## 2026-11-10-03 — M3-5 real Adapter capture, real fallback and controlled abort qualified

**Entry/branch:** Prior M3-4 `1ce8bdc9...` post-merge [Actions #42786259118](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42786259118) completed SUCCESS all 4 jobs. Existing draft PR #190 on `quad/integration-m3-real-adapter-fixture-20261110` was audited and continued, not replaced.

**Actual source execution:** New test-only root `quad.adapter.real_patch_capture` links real `ap_mesh_engine`, creates a genuine `Models3d::ModelBaseQuadrada` patch and `BuildInitialSubMesh` TRI seed, then calls `Adapter::AdaptDomain` with research capture and decision hooks enabled. Test-local AFT ratio 0.15 produces interior quadtree polygons under depth cap 3. Positive case completed three actual attempts, three source-independent UV snapshots, one selected local result, two superseded/failed and 30 TRI elements. Negative case deliberately throws during first capture; one snapshot, no decisions or output mesh, original patch observer retained. Neither case produces QUAD elements or chooses an interior-point formula.

**Preserved failures/repaired fixture:** first CI caused a real curve-sort scratch/parameters fault; added scoped legacy sort vector + endpoint parameters. Next returned `Quadtree has no included interior leaves`; test-only AFT ratio set to 0.15, no production AFT change. Follow-on compile failed from incomplete AftConfig; included its actual definition in test. Next run confirmed nonempty UV capture but exposed real fallback and a false test assumption of a single `local_attempt=0`; strengthened assertions for unique multi-attempt selection and supersession. All failed logs retained in Actions, never disabled a CTest.

**Qualification:** Reviewed exact candidate `67a4ceb58af09d48ba86fa964b51efaae0c660cc` passed [CI #42808140065](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42808140065): four jobs green; QUAD Linux/Windows 4/4, TRI **76/76** CTest including real fixture, Python 527/527, seven CLI denials, Eistute/Book 5+4 exact OBJ/acceptance/boundary. First successful fixture output: `real_adapter_capture_cases=2 normal_triangles=30 snapshots=4 local_attempts=3 selected=1 superseded_or_failed=2 aborted_decisions=0`.

**Integration:** PR [#190](https://github.com/tiagosombrra/apmesh-modernization/pull/190) reviewed and merged to `quad-templates` as `536c94009ea8b6a3a613886dfdf93314f94c91f6`, identical tree to tested head. No production algorithm sources changed, `main=f6050ec1...` preserved. Post-merge [Actions #42809300817](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42809300817) in progress at this checkpoint.

**Unresolved:** Local selection is not generator-level acceptance. OMP parallel execution and ASan/LSan not covered. QUAD physical XYZ, boundary completion, numerical point selection, shared curves/multipatch and iterative adaptation remain scientific gates. M3 partial. Next M3-6 outer accepted/rejected event correlation, source-preserving and opt-in.

## 2026-11-10-04 — M3-6 outer-generator decision and provenance source audit

**Entry:** M3-5 PR #190 already merged into `quad-templates` at `536c9400...`, followed by canonical research checkpoint `3c9fcda4...`. Exact-head premerge [#42808140065](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42808140065) SUCCESS 4 jobs, actual Adapter retry 3 local attempts/1 selected/2 nonselected, root 76/76 CTest + 527 Python, frozen Eistute/Book exact parity. [Postmerge CI #42809300817](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42809300817) three of four jobs SUCCESS at this inspection; root Linux TRI build remained in progress. Do not infer full green postmerge status.

**Actual source-backed work:** Published [M3-6 global acceptance and identity design](M3_GLOBAL_ACCEPTANCE_DESIGN_20261110.md) on scientific branch. Source audit `GeneratorAdaptive::execute` shows outer `retry` iteration (~3066), budget/growth short-circuit retries (~3263 and ~3302), serial `AcceptedMeshScope::Commit` (~3570), and rejected-step restore of accepted domain/curve state (~3669–70). `GeneratorAdaptive::AdaptDomain` calls `Adapter::AdaptDomain` with its own patch `local_retry` and Adapter internal `local_attempt` — these are **not the outer retry counter**. The four-field `PatchAttemptIdentity` can recur across global retries. A direct numerical join from M3-3/M3-4 to global acceptance would be scientifically incorrect.

**Result and next gate:** No global audit production C++ added in this session; the concrete next implementation M3-6a must introduce explicit outer retry/epoch tokens, preserving existing zero-default legacy interfaces and complete source/test gates. M3-6b should emit separate post-commit accepted and post-rollback rejected events and record budget/growth retry evaluations, not conflate them. Keep default CLI `quad_uv` rejected, no approved centroid or physical QUAD. `main=f6050ec1...` remains unchanged.

## 2026-11-10-05 — M3-6a global retry namespace added, audited and merged

**Entry:** Research `36fa9fb3...`; M3-5 PR #190 merged, post-merge Actions #42809300817 independently checked SUCCESS. Earlier M3-6 design identified retry-ID collisions across outer generator loops.

**Implemented:** isolated `quad/integration-m3-global-epoch-20261110`, [PR #191](https://github.com/tiagosombrra/apmesh-modernization/pull/191). Added trailing `OuterAttemptIdentity{session,epoch,global_retry}` to the legacy patch/step/adapter-retry/local-attempt identity, with four-field aggregate compatibility and explicit unscoped sentinel. Public research-only `GeneratorAdaptive::SetResearchUvCapture` requires caller nonzero session and counts actual outer loop retries with monotonic per-instance epoch, injected via Adapter into provisional UV captures and local TRI selection events. Source scoped to Generator+Adapter changes, updated exact SHA-256 inventory and CI scientific diff guard. Pure negative tests reject malformed outer contexts and mixed-epoch local decision streams; revised mixed-epoch negative ensures local IDs differ, preventing duplicate-ID logic from masking the intended oracle. Real Adapter fixture runs two successful captures under identical local IDs but different outer epoch and a controlled abort under a third.

**Validation:** Latest tested head `65a566c3a895de28cd8c4b1c8e9cba12522bc4c5`, [Actions #42813339493](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42813339493) **SUCCESS** all four jobs; Linux GCC and Windows MSVC QUAD each 4/4, root TRI 76/76 CTest, tooling Python 527/527, seven M3 CLI refusals; frozen Eistute five states, Book four, exact OBJ/acceptance/boundary equivalence. The real Adapter fixture printed three cases, 30 normal TRI elements, four UV captures, three local attempts, one selected and two superseded/failed. Superseded pre-final runs were cancelled by CI concurrency, not counted as passes.

**Integration:** PR #191 marked ready, reviewed and merged only to `quad-templates` at `1f34cc31d7fef9f6a4427a9c7c0bfffaaf34d2eb`, matching source tree `3ce68b06bf6b6e8ed22b0657d72a2909dda0b8a3`; `main=f6050ec1...` unchanged. [Post-merge CI #42814238290](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42814238290) running at checkpoint.

**Limits:** Session namespace uniqueness is a caller obligation, not process-global guaranteed. The outer GeneratorAdaptive hook-enabled end-to-end global acceptance/rejection path is not yet tested; no actual global accepted/rejected event emitted. M3-6b is the next deliverable. Positive `quad_uv` CLI is still blocked; M1/M2/M3 partial, physical XYZ/boundary/multipatch/adaptation and full OpenMP sanitizer qualification open.
## 2026-11-10-06 — M3-6b bounded global TRI outcome log integrated

**Entry:** Found independently advanced research `b48c953b...` with M3-5 and M3-6a already complete, PR #192 open. Post-M3-6a [CI #42814238290](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42814238290) independently read as SUCCESS all four jobs.

**Implementation and audit:** PR [#192](https://github.com/tiagosombrra/apmesh-modernization/pull/192) introduces `research/quad/global_outcome.h`, a 128-entry value-only chronological prefix with `noexcept` Record, overflow/truncated and Reset, allocated per Generator only when the research provider/sink is explicitly installed. Actual serial GeneratorAdaptive transitions record budget/growth rejections as evaluations before retry, and accepted/rollback status strictly after `AcceptedMeshScope::Commit()` or both geometry/curve restoration, correlated to M3-6a session/outer epoch. No production CLI registration, no physical QUAD or centroid adoption.

**Native/scientific proof:** final exact candidate `ddbc678fccdbe7ea3c3e899514e4f51dd29a17e1`, [Actions #42816180344](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42816180344) SUCCESS all four jobs: Linux QUAD 4/4, MSVC QUAD 4/4, root TRI 76/76, Python 527/527, 7/7 negative CLI, Eistute 5 / Book 4 exact OBJ/acceptance/boundary agreement. Reviewed only six scoped changed files; unit tests validate four kinds, ordering and overflow, not a real GeneratorAdaptive run.

**Merge:** PR #192 source-reviewed, marked ready and merged to research `quad-templates` at `584fe2a2959b268908bc2d9feff8888658a47d62`, source tree identical to approved candidate, main remains `f6050ec1...`. Postmerge [#42821767939](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42821767939) in_progress at checkpoint. Next M3-6c is an actual hook-enabled GeneratorAdaptive fixture to prove chronology and outer epoch; M1/M2/M3 partial; OMP execution/sanitizer/positive QUAD remain out of scope.
## 2026-11-10-07 — M3-6c actual global TRI outcome test qualified and merged

**Entry:** Found PR #193 already open from a separate session, based on `quad-templates=1c44405a...`. This avoided duplicate implementation. PR #192 post-merge Actions #42821767939 independently checked SUCCESS, four jobs.

**Reviewed:** PR #193 changes exactly five expected files (CMake, SHA architecture inventory, research report, C++ `generator_outcome_probe.cpp`, Python relocated-model wrapper). It registers hooks only in a research executable linked to `ap_mesh_engine`. A real Eistute `GeneratorAdaptive::Execute` produces bounded global TRI commit/restore events; probe validates nontruncated chronological outer epochs and correlation of provisional captures/local selections. The provider intentionally retains only a **leaf count**: not UV quad topology nor a numerical centroid.

**Exact scientific tests:** [Actions #42823072772](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42823072772) SUCCESS four jobs; [#42823003811](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42823003811) independently SUCCESS. TRI 77/77 CTest, 527/527 Python, native QUAD Linux 4/4 and MSVC 4/4, seven CLI rejects; Eistute five and Book four state byte-identical OBJ, identical accepted/rejected decisions, verified boundary incidence. `quad.generator.real_global_outcomes` passed in 5.21 seconds within complete 77 CTest.

**Integration:** PR #193 review comment recorded, marked ready and merged to research as `131623d1fb39350d90779d61a0255b35fecb3dea`. Verified merge tree `781ad6558594bb8ab9ef5074a05caea67163b53b` equals tested head `ab91727c555c222f4a3e95143522615fa16522ca`, and `main` remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Post-merge Actions [#42825582252](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42825582252) was queued at checkpoint.

**Next:** close exact-head postmerge; test cross-model chronology and no-hook TRI behavior in separate M3-6d. M1/M2/M3 partial. No approved scientific interior rule, positive physical QUAD, completed boundary/XYZ or concurrency/sanitizer proof.
## 2026-11-10-08 — M3-6d actual Eistute/Book global event chronology merged

**Starting point:** Independent M3-6c PR #193 was found already open. Its CI [#42823072772](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42823072772) had completed with 77/77 TRI CTest, 527 Python, 4/4 QUAD Linux/MSVC and strict Eistute/Book science; PR #193 merged to research `131623d1...`. Its [post-merge #42825582252](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42825582252) later independently finished SUCCESS four jobs.

**M3-6d implementation:** Created isolated `quad/integration-m3-cross-model-outcomes-20261110`, PR [#194](https://github.com/tiagosombrra/apmesh-modernization/pull/194). Registered an additional root CTest invoking the unchanged real `GeneratorAdaptive` fixture on pinned Book article config. Strengthened actual event correlation: at least one selected local Adapter outer (session, epoch, retry) belongs to a real global outcome epoch. Updated the exact CMake SHA-256 in architecture inventory (verified with SHA-256 known-answer vector). No production source or article numeric settings changed.

**Qualified:** exact candidate `648b7c1b46864b7b0ca8c1cfaeadc4cce820da2d`, [Actions #42826247691](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42826247691) SUCCESS four jobs. Root TRI **78/78**; Eistute real probe 5.78s and Book real probe 3.38s; 527/527 Python, 7/7 CLI negatives, QUAD GCC/MSVC 4/4 each, strict 5/4 Eistute/Book OBJ and acceptance/boundary parity.

**Merge:** PR #194 reviewed and merged into `quad-templates` as `abab2155896671c70cf370fd032edab865b942c8`; verified merge tree `7e8b19291a9b9b01a33654f7f24ebf91303f1b37` equals tested candidate; unchanged `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Exact merged-head [post-merge #42827666971](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42827666971) in_progress at checkpoint. Changes affect only CMake/tests/inventory/research docs.

**Research limits:** These are TRI event chronology/correlation tests, not completed physical QUAD. M1 numerical point policy/centroid, M2/M3 scientific topology/coverage, boundary/XYZ/multipatch, OMP/MPI runtime concurrency and sanitizer/allocator fault proof remain open. Next work should advance the actual historical template/positive-UV evidence, not falsely mark M3 complete.
## 2026-11-10-09 — M1 historical Figure 7 executable exact rational audit

**Entry:** Canonical research `585d90722e29e80ec3f64d29fd7cca3c9177c49c`, earlier M3-6d post-merge [#42827666971](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42827666971) independently checked SUCCESS all four jobs. M1 source transcription remained an unapproved proposal; the existing C++ `uv_contracts.cpp` already covered 48 D4 witnesses, so duplication was avoided.

**Implementation:** new `tests/quad/test_m1_figure7_oracle.py`, a standard-library only **independent exact-rational** checker reading the pinned JSON transcription. Verifies six classes T1,T2,T4,T3,T5,T6, 48 D4 oriented source graphs, 96 test-only witness subdivisions using *both* arithmetic vertex mean and polygon area centroid, all 16 split signatures, area/convexity/edge sharing/Euler/connected disk and nine negative mutations. Analytic disparities T2 `ABOW` mean (3/8,1/4) vs area (7/18,2/9), T5 `WSND` mean (1/4,5/8) vs area (5/18,11/18). Registered standalone `quad.m1.figure7.oracle` CTest via Python3; `tests/quad/CMakeLists` SHA-256 inventory updated and independently read back.

**Failure retained:** initial [CI #42832471771](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42832471771) failed the new Python T5 negative fixture due to incorrectly joining tuple cycles; existing C++ native tests passed. Corrected the fixture in `2bb2ecb1...` without altering scientific graph data or test validity, retaining failure evidence in PR #195 discussion.

**Qualification:** exact reviewed `2bb2ecb1a7daacb153116c6c8486d49bdd6d1c50`; [Actions #42832685760](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42832685760) SUCCESS four jobs. GCC QUAD 5/5, Windows MSVC QUAD 5/5, root TRI 78/78 CTest and Python 527/527, seven CLI denials, Eistute five/Book four strict OBJ byte equality, acceptance and boundary incidence. Review confirmed only four permitted test/build-inventory/research-doc paths changed.

**Integration:** PR [#195](https://github.com/tiagosombrra/apmesh-modernization/pull/195) merged to research `quad-templates` as `cb5aca8bae44fc33f3e927188389edf0281ac04e`, merged tree `b2ded2a2a8340800fb40514f654e8159536934ac` identical to exact tested feature; modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` preserved. Post-merge [#42834073835](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42834073835) in_progress at checkpoint.

**Scientific limitations:** An independent algorithmic checker applied to a *manually transcribed* schematic is not an independent human reading of scanned Figure 7. Metadata scan hash was not revalidated against the Drive bytes. The area centroid and arithmetic vertex mean are competing **test witness** formulas and neither was authorized. M1/M2/M3 remain partial, physical QUAD/complete boundary/XYZ/multipatch/sanitizer/parallel paths remain open. Next: adviser review and approved numerical policy before isolated algorithm PR.
## 2026-11-10-10 — M1 explicit numeric witnesses implemented in isolated research library

**Starting point:** research `1ae3487fd401f8cb3f26735e69ee2107eae7c173`, with PR #195 [post-merge CI #42834073835](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42834073835) independently confirmed SUCCESS four jobs; `main=f6050ec1...` unchanged. Figure 7 source transcription and historical numerical centroid still await adviser review.

**Source:** created `research/quad/experimental_point_rule.{h,cpp}` and research-only static `apmesh_quad_experimental_point` target. The API requires an explicit `ExperimentalPointRule::VertexArithmeticMean` or `PolygonAreaCentroid`. Both use translated local coordinates and reject invalid tolerance, unknown enum, nonfinite, CW, concave/collinear or near-degenerate polygons and a point failing strict interior tests. No implicit production rule, no Adapter integration or positive QUAD CLI. Separate C++ native contracts exercise independent rational T2/T5 expected points, 96 D4 test-only witness UV subdivisions, scale/translation invariance, source immutability and negative cases. Native QUAD standalone test count increased 5 to 6. Architecture CMake SHA-256 updated and verified by readback.

**Qualified candidate:** `10065b24a7a4ae5a93dafc743a8324f5bf058975`. [Actions #42851499408](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42851499408) completed SUCCESS four jobs: Linux GCC QUAD 6/6 CTest, Windows MSVC QUAD 6/6 CTest, root TRI 78/78 CTest, tooling Python 527/527, CLI denials 7/7, Eistute 5 / Book 4 exact OBJ-byte, acceptance and boundary incidence parity. Earlier superseded feature build #42851113468 passed native QUAD but was not used as final merge gate after adding negative tests.

**Integration:** scoped PR [#196](https://github.com/tiagosombrra/apmesh-modernization/pull/196) reviewed and merged as `720309b4b153b5695a5afcb81aa9a967a17aaa0e`; merge tree `af7629b04fb5149960ebb34360309c99a587ddb4` equals exact qualified candidate, while modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` was not touched. [Post-merge Actions #42853155958](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42853155958) was in_progress at checkpoint; final conclusion not yet claimed.

**Limits and next:** These are two competing research proposals, NOT Bento/Creto-approved historical point rules. The 1993 scan bytes were not independently retrieved/rehashed, nor was the Figure 7 graph reverified by advisers. Production TRI remains stable, QUAD physical XYZ/boundary/patch synchronization/concurrency/sanitizers not qualified. Next: post-merge CI exact SHA, then scientific adviser decision before closing M1 or production-adjacent work.
## 2026-11-10-11 — M1 authenticated 1993 source and comparative centroid quality

**Entry:** Canonical research `f5c249d67d6e875bd0db91970d21e124a07aaf61`; M1 PR #196 [post-merge Actions #42853155958](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42853155958) subsequently concluded SUCCESS all four jobs. No open other PRs. `main` still `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

**Independent original source:** Used authenticated original Google Drive file `1993_Bento_SIBGRAPI_Combinacao_das_Tecnicas_Templates_Quadrilaterais.pdf` (seven pages, **5,439,448 bytes**); actual SHA-256 computation `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5` matches previously recorded source exactly. The lower six Figure 7 graphs in scanned printed p. 288 visually agree with proposed topology. The source does **not** print T1–T6 labels; mapping `T1,T2,T4,T3,T5,T6` is current code vocabulary. Paper specifies edge midpoints, polygon centroid and connections; does not give numeric centroid equation. Its 1987 Baehmann reference was identified (DOI 10.1002/nme.1620240603), but the full text was not examined. Paper distinguishes interior templates from exterior triangulation/Delaunay contour contraction.

**New research experiment:** Created isolated `quad/integration-m1-primary-source-audit-20261110`, PR [#197](https://github.com/tiagosombrra/apmesh-modernization/pull/197), with standard-library Python `quad.m1.point_rule_quality` CTest: six proposed pattern graphs × eight D4 transforms × two explicit unapproved point rules, **96 comparisons**. Independent golden normalized minimum corner sines: T1/T3/T6=1, T2/T5=0.6, T4≈0.70710678 for both rules. Mean-of-element minima differ slightly on T2/T4/T5 (arithmetic mean higher), but this local angle proxy neither defines the original algorithm nor physical curved-element quality. No production source or CLI changed.

**Qualified and merged:** exact feature head `881fc9236b9541bdf256c6da790d68b9ffba533d`; [Actions #42867018870](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42867018870) SUCCESS four jobs: Linux GCC and Windows MSVC QUAD **7/7** each, root TRI **78/78 CTest**, Python **527/527**, CLI rejects **7/7**, Eistute five and Book four exact OBJ/accepted/rejected/boundary parity. PR #197 reviewed and merged only to `quad-templates` as `7b0ae3aebb2c27d1504e5842e496742ca4d011a3`; exact merge tree `f37656927a834183128658e7196d9ee5271827ab` equals feature. Post-merge [#42868211131](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42868211131) was in_progress at checkpoint. Original modernization `main` remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

**Open scientific decision:** Geometric polygon centroid is normally signed-area centroid, but the 1993 wording does not certify the historical implementation or degenerate handling. Neither implemented experimental policy is formally approved by Bento/Creto; 1987 full paper and adviser decision remain next. M1/M2/M3 partial, no physical QUAD, completed boundary/XYZ/multipatch, OMP runtime or sanitizer evidence.
## 2026-11-10-12 — visual outputs, actual C++ OBJ emitter and user mode decision

User approved implementation sequence: first recreate hybrid 1993 (QUAD interior templates + Delaunay/contour contraction exterior); then separately add a selectable all-QUAD extension. No false claim that either is currently working CLI. User requested actual viewable meshes, not only abstract tests.

Published local offline HTML/PNG and ZIP visual review package from existing Figure 7 source cycles; six patterns (4/11/12/8/11/16 quads), both explicitly experimental center rules, 12 independent source-derived OBJ, 2-cell example, and an extra 2:1 neighbor-conformity fixture with 19 UV quads. Independent geometry audit: total area, Euler, shared-edge incidences; HTML inspected in Chromium (6 cards, 18 SVG compare, label/checkbox selection, no script errors) and supports exporting per-pattern human review JSON. **Do not present these independent renders as the actual application's physical mesh output.** Historical Figure 8 crop included only as 1993 source reference.

New research [PR #198](https://github.com/tiagosombrra/apmesh-modernization/pull/198): standalone C++ test `quad_visual_export`, linked to actual `apmesh_quad_uv` and experimental selector, writes 12 C++ UV OBJ files and verifies local topology. Research [SVG gallery](figures/M1_UV_6_PATTERNS_20261110.svg), [mode and visual workflow](MODE_CHOICES_AND_VISUAL_REVIEW_20261110.md), and architecture input hash stored for cross-chat continuation. Exact tested head `c0b1f86661133dc019d5699383f80d173f289056` [CI #42881742866](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42881742866) SUCCESS four jobs: Linux/Windows QUAD 8/8 each, TRI 78 CTest, 527 Python, seven CLI denials and Eistute/Book exact OBJ/acceptance/boundary parity. Merged into `quad-templates` `8559d4d12651b4ca37f0d3f9e0fe95c4bb2685bb`, exact tested tree; original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` preserved. Postmerge [#42883282973](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42883282973) in_progress at checkpoint.

**Next:** check exact post-merge CI; use real Quadtree fixtures to visualize candidate patch vs outer TRI/contour and then the actual hybrid application stage. Do not confuse standalone UV with physical QUAD or all-quad. Original historical centroid/hybrid completeness remains unapproved.
## 2026-11-10-13 — Real 19-leaf Quadtree visual evidence committed

Source remains research `quad-templates`. The next objective after six isolated Figure 7 templates was to visualize **actual source Quadtree leaves and emitted UV QUAD**, without inventing exterior TRI. Created [PR #199](https://github.com/tiagosombrra/apmesh-modernization/pull/199), 6 research/CI/test/inventory files, C++ `quad_tree_visual_export` linked to actual legacy tree bridge plus two explicit experimental center rule selectors. The actual tree fixture contains 19 leaves, 7 included candidates, 12 excluded boundary leaves. Native emitter generates 42 four-node QUAD, 53 UV vertices and area 0.25 for both rules. Actual SVG/CVS/OBJ/JSON files undergo independent Python Euler/area/incidence/source provenance assertions. GitHub Linux uploads actual binary-generated view as [artifact ID 13798922455](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42892551246/artifacts/13798922455), with 14-day retention. Chat preview PNG is independently derived, NOT mislabeled as native execution capture.

Initial [run #42892288498](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42892288498) failed because new C++ incorrectly indexed list-returning `getLeaves()`. Fixed by ordered range-for at exact tested source `5f72d163660aa3f29ef3f1f7184f26868650733a`, preserving the failure receipt.

[CI #42892551246](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42892551246) SUCCESS four jobs: QUAD Linux GCC and Windows MSVC 10/10 each, root TRI 78/78 CTest, Python 527/527, CLI rejects 7/7, strict frozen Eistute five/Book four OBJ and acceptance/boundary comparison. Reviewed six permitted paths and merged PR #199 to `799dd62f7e3dd9145fcc120c5c6daae09c8e01bb` with same tested tree `90dedc2310bc3c20f12f5fd3f87abecd5b650aa6`. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unmodified. Prior post-merge #42883282973 SUCCESS; new exact-merge [#42894221887](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887) in_progress at checkpoint.

**Next:** historical hybrid exterior Delaunay/contour contraction over 12 still-unmeshed boundary leaves, with shared QUAD/TRI interface and real area/topology/visual evidence; no invented triangles or prematurely enabled all-QUAD. M1/M2/M3 partial.
## 2026-11-10-14 — PR #199 post-merge native and TRI gate independently certified

[Actions #42894221887](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887) completed SUCCESS all four jobs on exact merge SHA `799dd62f7e3dd9145fcc120c5c6daae09c8e01bb`: Linux GCC 10/10 native, Windows MSVC 10/10 native, TRI 78/78 root CTest, 527 Python, 7 CLI negative, Eistute five and Book four strict OBJ/acceptance/boundary equality. GitHub uploaded **actual C++ runtime-produced** [visual artifact #13798814198](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887/artifacts/13798814198) and [scientific artifact #13798804430](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887/artifacts/13798804430) with 14-day retention. Full historical hybrid and all-quad generation still pending. No production main changes.
## 2026-11-10-15 — M5 actual C++ QUAD plus experimental exterior TRI closure

**Entry:** Canonical `quad-templates=5a6f6bcd33bb89025989bfd6b6da66c6f8c1d7bf`, prior PR #199 exact merged CI [#42894221887](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887) SUCCESS four jobs. Original modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. User requested continuing the next real physical hybrid milestone and visual proof.

**Real source, independent analysis:** Downloaded authentic C++ Quadtree artifact ID `13798814198` on prior merged SHA. Built independent research-only Python exterior cell-center fan from *unchanged* 42-QUAD OBJ and actual 19-leaf CSV, producing 60 TRI with 20 matching QUAD/TRI seam edges, a closed length-2 polyline and UV total area 1.0. Independent local checker read back the two combined 81-vertex meshes, verified positive winding, Euler disk, 16 outside edges, original QUAD IDs, missing/inverted/duplicate TRI and duplicate vertex denials. Generated standalone PNG and downloadable CI-source ZIP for visual review. Explicitly **not** a historical Delaunay/contour-contraction implementation.

**Code integration:** Isolated `quad/integration-m5-experimental-boundary-interface-20261110` with [PR #200](https://github.com/tiagosombrra/apmesh-modernization/pull/200) adds `test_m5_exterior_interface.py`, research CMake gate, Linux artifact publication, scoped documentation and SHA-256 inventory correction. No production `src/`, `include/`, defaults, acceptance or frozen model changes. The test consumes real C++ output, adds actual 60 experimental TRI faces and reproducible two-rule OBJ, SVG, seam CSV and manifest; four negative mutations checked.

**Qualification:** exact feature `d30bc0e7457aecfafe6264dfc0961e8bd57d009e` [Actions #42898041678](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42898041678) **SUCCESS four jobs**: Linux GCC and Windows MSVC native QUAD **11/11**, TRI **78/78 CTest**, Python **527/527**, CLI negative **7/7**; Eistute 5/Book 4 byte-identical OBJ, identical accept/reject and boundary incidence. CI Linux artifact [#13801072358](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42898041678/artifacts/13801072358) independently re-downloaded and passed a second local topology/area/manifest check.

**Merge/checkpoint:** reviewed scoped five paths; PR #200 merged to research at `8a088cb58e89794c1cc22e8f62221fef2dd3dae4`, tree `d71e28d2c2f3c131cb660cec9c918538e4ad7752` matches tested feature exactly, modernization main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unaffected. [Post-merge #42899687132](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42899687132) in_progress at checkpoint.

**Next scientific gate:** actual 1993 Delaunay/contour contraction rather than synthetic fan; historical point rule/adviser alignment; physical UV→XYZ ownership and contour. M1/M2/M3/M5 remain partial. All-QUAD selectable mode only after historical reproduction qualified.
## 2026-11-10-16 — PR #200 exact merge regression closure and next scientific gate

[Post-merge Actions #42899687132](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42899687132) on source merge `8a088cb58e89794c1cc22e8f62221fef2dd3dae4` completed **SUCCESS four jobs**. GCC QUAD 11/11, MSVC QUAD 11/11, TRI root 78/78 CTest, Python tooling 527/527, CLI denials 7/7, strict Eistute five/Book four OBJ-byte/acceptance/boundary parity. The previously recorded in-progress status is superseded by this exact evidence. Modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` remains unchanged.

Source review for the next step inspected `include/crab_mesh/aft/advancing_front.h`, `src/crab_mesh/aft/advancing_front.cpp` and `src/crab_mesh/aft/boundary.cpp`: the code contains `AdvancingFront` and explicit contour objects; this cannot be treated as the historical Delaunay/contour-contraction algorithm by name or assumption. The existing 60 exterior TRI are still only experimental center fans, notwithstanding successful full UV topology tests. Next isolated PR should reproduce actual 1993 exterior Delaunay and contraction using an explicitly audited source and scientific rules, then reuse the 20-edge shared QUAD/TRI seam and full native/science gates. Fully all-QUAD comes afterward.
## 2026-11-10-17 — M5 local constrained Delaunay research and verified C++ source artifact

**Starting branch:** `196807f754cb74ff1c9a36baec61de3493162f13`, PR #200 postmerge exact CI #42899687132 SUCCESS four jobs, `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` preserved. No other active PR at start.

**Experiment:** Native C++ 19-leaf Quadtree generates 53 original QUAD vertices/42 quads occupying 0.25 UV area, plus the preexisting experimental 60 exterior fan TRI. New research-only `tests/quad/test_m5_constrained_delaunay.py` builds 12 split-perimeter exterior leaf polygons, initial 36 ear-clipped triangles, then eight exact-rational Lawson flips while protecting the 20-edge QUAD/TRI seam and outer 16 edges. Final: 69 vertices / 42 native QUAD / 36 research TRI, full area 1.0, 24 eligible interior TRI edges satisfy local Delaunay condition, Euler single disk, positive orientation, five malformed mutations rejected. For both unapproved centroid experiments, triangulation is identical. Initial ear min angle 8.130102°, after flips 12.528808°. This is **NOT** historically faithful 1993 Delaunay point insertion/contraction, a physical XYZ mesh, or production mode.

**CI and evidence:** [Exact candidate Actions #42927019836](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42927019836) SUCCESS all four: native GCC/MSVC 12/12 CTest, root TRI 78/78, Python 527/527, seven CLI denials, Eistute 5/Book 4 byte OBJ/acceptance/boundary parity. Downloaded [CI artifact #13813973287](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42927019836/artifacts/13813973287) with actual C++ QUAD and optimized TRI. Independently verified native QUAD OBJ bytes unchanged and final 69/42/36 geometry/connectivity identical to local prototype (header text only differs). Interactive offline HTML/ZIP user deliverables include C++ artifact models, visual layer controls and exportable JSON visual review.

**Integration:** PR [#201](https://github.com/tiagosombrra/apmesh-modernization/pull/201) reviewed, merged only into `quad-templates` as `cd4aca73747edd95af2b4b370da6d6c4cfa4057b`; merge tree equals exact tested candidate. Modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. Postmerge Actions [#42928126047](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42928126047) in_progress at checkpoint; final result must be read separately.

**Next scientific gate:** Establish an independently grounded 1993 Delaunay + contour contraction specification from primary references and Bento/Creto, then implement real physical boundary insertion/mapping and visual before-and-after validation in a new isolated research PR. The legacy APMesh advances fronts and cannot be assumed to implement Delaunay merely by its name. M5 remains PARTIAL. All-QUAD extension remains later.

## 2026-11-10-18 — M6 analytic UV→XYZ research bridge

**Source:** research `720bafc6e24ae2ad58596d75a28a0ac00d6805c2`; PR #201 historical Delaunay research and 19-leaf 42-QUAD C++ artifacts already in place. Previous exact post-merge #42928126047 verified SUCCESS all four jobs. Modernization main remained `f6050ec1...`.

**Implemented:** [PR #202](https://github.com/tiagosombrra/apmesh-modernization/pull/202) adds `test_m6_analytic_surface_lift.py`, a standalone M6 native CTest consuming actual C++-origin 42 QUAD plus M5 research 36 TRI. Deterministic analytic graph `(u,v,k*u*(1-u)*v*(1-v))` for k=0,+/-1.6 and both explicitly unapproved centroid alternatives. Uses 69 IDs, 20 preserved QUAD/TRI seam edges, 16 z=0 outer edges, 120 oriented subtriangles, analytic tangent-normal projection and faceting-error diagnostics, and eight negative mutations. This is an analytically curved **synthetic test**, not `PatchBezier`, actual Eistute/Book XYZ, historical Delaunay insertion/contraction, full physical hybrid nor all-QUAD.

**Qualification:** exact feature head `e0e0d86ca4bad419425337ea7676b1c2a9ec3490`; [CI #42941827778](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42941827778) SUCCESS all four: Linux GCC/Windows MSVC QUAD 13/13 each, TRI 78/78, Python tooling 527/527, seven CLI rejects, and frozen Eistute 5 / Book 4 exact OBJ, acceptance and boundary equivalence. Downloaded native Actions artifact #13821515576 and independently compared all 69 XYZ coordinates (within 1e-13) and 78 face records to an external visualization from the prior native C++ M5 OBJ. Both explicit centroid variants retained identical external triangulation and seam. Minimum normal alignment 0.9897848826346841, maximum linear facet height error 0.01914063 for curved graph k=+/-1.6.

**Integration:** PR #202 reviewed and merged into `quad-templates` as `b48526ab22f7190679cd37c61a12005687666c5f`; merge tree identical to the exact CI-qualified candidate, main unchanged. Post-merge Actions #42942777929 `in_progress` at checkpoint; final result remains to be checked. All scientific production gates remain open.

**Next research:** actual APMesh geometry evaluation via `PatchBezier::Parameterize(u,v)` with `Qu/Qv` normal checks and explicit patch boundaries, independent geometry oracles, then separately the adviser-approved 1993 Delaunay+contour contraction algorithm. Preserve historical hybrid first, selectable all-QUAD later.

## 2026-11-10-19 — M4 production PatchBezier API experiment (feature proposed; CI pending)

**Entry:** canonical research `65f73647bb0594457ab44d113cc8fedf5fb921de`; modernization main remained `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. M6 analytic UV→XYZ research was merged; its source 42 native C++ QUAD, 36 experimental local-Delaunay TRI, 69 UV vertices and conforming 20-edge seam are preserved.

**New work:** feature branch `quad/integration-m4-patch-bezier-physical-probe-20261110` and [PR #203](https://github.com/tiagosombrra/apmesh-modernization/pull/203), exact feature `35397a5f9980ef889794162984f5e6dbe4e0d7c3`. Introduced `tests/quad/patch_bezier_physical_probe.cpp` using the actual production `PatchBezier`/owned curves with explicitly scoped test control points, independent bicubic polynomial XYZ/Qu/Qv oracles at 243 UV samples, twelve invalid UV guard cases, collapsed and mirrored geometry negative cases; root `CMakeLists.txt` registers the new serial research test. New scientific scope and limitations in `M4_PATCH_BEZIER_PHYSICAL_API_20261110.md`. No production source/CLI/default change.

**Actual qualification status at checkpoint:** shell GitHub network access here was unavailable; no native local build or root CTest was executed in this chat. [Actions #42944985482](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42944985482) was `in_progress`: Linux native QUAD job passed, Linux TRI baseline, Windows QUAD, and strict scientific equivalence not yet complete; the new physical-api CTest has **not** been certified. Required root count is 79, with 527 Python, seven CLI negatives, and Eistute/Book nine states; no merge permitted before actual pass. Synthetic point rule and 1993 Delaunay/contraction still unapproved.

**Next exact action:** inspect feature CI job logs, repair any failures in a reviewable follow-up commit and requalify exact new head, then merge PR #203 to `quad-templates` only after green gates, verify postmerge and update this checkpoint. After that, consume real native M5 topology with a live `PatchBezier` and validate CAD/physical seams; separately load real curved APMesh model geometry. All-QUAD remains later.

## 2026-11-11-20 — Close feature PR #203; M4 physical API qualified, post-merge pending

**Baseline and fault classification:** research `65f73647bb0594457ab44d113cc8fedf5fb921de` plus prior canonical documentation. PR #203 initially failed [Actions #42944985482](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42944985482) at `tooling.controls`: the frozen architecture inventory root CMake SHA-256 did not match the intentional new CMake research test registration. Root CTest then reported 78/79 passed, with the new `quad.patch_bezier.physical_api` itself passing; 526 remaining Python cases passed, one architecture inventory case failed. Corrected **only** the root CMake inventory hash to `4d3f6a6b221a0e7c7157277c96f70cdf87d7a5104846ef57e5c331816ad27396` in `docs/architecture/source_inventory.json`. Validated the previous retained hash against the unmodified base file before replacing it. No `src/`, `include/`, CLI, tolerance or original TRI data changed.

**New qualification:** exact feature `956127fdaef8535cb8ae995cae14f50099b306b5`; four-job [push Actions #42990400680](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42990400680) and [PR Actions #42990407284](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42990407284) **SUCCESS**. Push root logs record CTest **79/79**, Python **527/527**, M3 CLI guard and named `quad.patch_bezier.physical_api`; Linux/Windows native QUAD passed. Scientific equivalence job verified the unchanged frozen Eistute/Book baseline. No native executable was run inside this chat's local container; evidence is explicit remote hosted CI.

**Integration:** [PR #203](https://github.com/tiagosombrra/apmesh-modernization/pull/203) merged to research as `6dcffdc0a96a69bd3bd0a1ebc9b434ea607eba20`, confirmed live in branch head. Original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. [Postmerge Actions #42991513759](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42991513759) was **in_progress** on exactly `6dcffdc0...` when checked; GCC/MSVC native passed, root/scientific jobs pending. Do not claim post-merge completion until rechecked.

**Scope and next gate:** the actual `PatchBezier` production API was exercised on a deterministic controlled 16-point grid, not a loaded curved model, not native 69-vertex QUAD/TRI physical mapping, not a four-node physical element or historical Delaunay/contraction. Created [M4 real model hybrid design](M4_REAL_MODEL_HYBRID_DESIGN_20261111.md), an explicit **unimplemented** next gate using `Models3d::ModelCurvaBezier`, real C++ Quadtree UV and M5 36 TRI while retaining 20 seam edges, independent Bernstein goldens, physical normals and negative cases. Preserve numerical decision uncertainty, default TRI and no production QUAD. Before next development gate, verify merged CI completion and re-audit current research head.

## 2026-11-11-21 — M4 built-in curved model physical hybrid research implementation

**Starting status:** [PR #203](https://github.com/tiagosombrra/apmesh-modernization/pull/203) integrated with [postmerge #42991513759](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42991513759) later verified **SUCCESS** at `6dcffdc0a96a69bd3bd0a1ebc9b434ea607eba20`. Research branch began at `3bac7ef10ac42078cbc041fbb72d5e68c2d86878` after checkpoint-only documentation; modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Actual source and new implementation:** isolated `quad/integration-m4-real-model-hybrid-lift-20261111` integrates existing `tests/quad/tree_visual_export.cpp` with the actual C++ quadtree and kernel `ap_mesh_engine`, reuses *unmodified* pre-existing `test_m5_exterior_interface.py` and `test_m5_constrained_delaunay.py`, then invokes new `tests/quad/physical_model_hybrid_lift.cpp` to borrow `Geometry`-owned `Models3d::ModelCurvaBezier` / `PatchBezier`. The C++ lift maps 69 research UV vertices to physical XYZ/Qu/Qv without changing 42 original QUAD and 36 research TRI face IDs. `tests/quad/test_m4_real_model_hybrid.py` evaluates an independent pinned 16-control-point bicubic Bernstein golden, tests 120 oriented subtriangles, 20 seam and 16 outer edges, finite/positive Jacobian and normal projection, mapped boundary curves and edge midpoint faceting errors. Both unapproved point rules execute 11 negative mutations each (22 total). No `src/`, `include/`, CLI, production `SubMesh`, `QuadrilateralAdaptive`, acceptance/rollback, presets or scientific TRI changes.

**CI and merge:** root CMake registered research-only `quad.m4.real_builtin_model_hybrid`; architecture inventory CMake SHA updated exactly, and scoped `quad-research-validation.yml` publishes bounded physical witness OBJs/CSVs/manifest. [Feature Actions #42993951256](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42993951256) **SUCCESS** four jobs on exact feature `ac4eb3b464297962d7bc68376b97112c4523a8b5`, 80/80 CTest, 527/527 tooling Python, seven CLI invalid inputs and strict reference Eistute/Book, native research QUAD GCC/MSVC pass. Original earlier push [#42993814942](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42993814942) also passed; uploaded feature physical [artifact #13842634340](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42993951256/artifacts/13842634340). Reviewed six touched paths. [PR #204](https://github.com/tiagosombrra/apmesh-modernization/pull/204) merged to `quad-templates` at `da61e09d157698210faa674bfa911332f574c7ad`; exact [postmerge #42994999161](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42994999161) was **in progress** (native GCC/MSVC success, TRI root/science still active) when this log was written. No local native execution inside this chat; all execution evidence is linked remote CI.

**Explicit non-claims:** Built-in authored model is *not external imported curved CAD*; M5 Lawson is *not original 1993 Delaunay point insertion and contraction*; research UV→XYZ OBJ is *not owned physical four-node adaptive element*; historical centroid, multipatch edge synchronization, adaptation retry and optional all-QUAD remain pending. Next activity after postmerge qualification: isolated ownership/lifetime and boundary-consistent physical QUAD element prototype, plus advisor-supported historical decisions.

## 2026-11-11-22 — M4 built-in model hybrid exact merge closeout

**Verified result:** [Post-merge Actions #42994999161](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42994999161) completed **SUCCESS**, exact source merge `da61e09d157698210faa674bfa911332f574c7ad`, all four jobs. Root logs explicitly show **80/80 CTest** including `quad.m4.real_builtin_model_hybrid`, **527/527 Python tooling**, seven M3 CLI rejected modes; native Linux GCC and Windows MSVC QUAD jobs passed and frozen TRI Eistute/Book equivalence passed. A second bounded on-merge physical model [artifact #13844285703](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42994999161/artifacts/13844285703) was published from the merge tree. This supersedes the session-21 in-progress postmerge status; it is not an independently imported CAD witness.

**Preservation and scientific limits:** no `main` code edit; default TRI remains; the verified research physical lift is still not an owned physical four-node `QuadrilateralAdaptive`, historical 1993 Delaunay/contour contraction, imported CAD, approved centroid, multipatch or all-QUAD. Evidence receipt `evidence/M4_BUILTIN_MODEL_PHYSICAL_HYBRID_20261111.json` records exact source hashes and outcomes. Documentation-only checkpoint commits follow the qualified merged source; they do not change any compiled source or numerical controls.

**Next:** after the completed M4 geometry gate, design and implement a separately reviewable four-node physical element ownership/lifecycle prototype and independent curved boundary admission, keeping this historical research scope and default TRI untouched. Scientific historical algorithm/centroid policy still awaits adviser alignment.

## 2026-11-11-23 — Research physical four-node element ownership and lifecycle gate

**Input:** canonical research `9e775a1762523e6e88d7fa82ed98a38504f73404`; [PR #204](https://github.com/tiagosombrra/apmesh-modernization/pull/204) and its M4 real built-in `ModelCurvaBezier` UV→XYZ physical OBJ already passed exact postmerge `da61e09d157698210faa674bfa911332f574c7ad`. Modernization main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Implementation:** isolated `quad/integration-m4-four-node-ownership-20261111` built `research/quad/physical_quadrilateral_adaptive.h/.cpp`, a separate namespace-derived `ElementAdaptive` with four borrowed distinct `NodeAdaptive*` and UV corners, reference chart normal, two positive-orientation physical subtriangles, positive calculated area, normal and corner angles, erased copy/move and exception-safe observer registration. New `tests/quad/physical_quad_ownership_probe.cpp` consumes actual M4 built-in curved model output, builds one owning `SubMesh` with 69 nodes and 42 research QUAD plus 36 existing physical `TriangleAdaptive`, tests 276 reverse observer links, 20 shared seam/16 outer edges, ordinary `SubMesh` move construction and move assignment, self move, no stale external observers, four injected failures and seven malformed constructor inputs. `tests/quad/test_m4_quad_ownership.py` reruns the independent M4 Bernstein/differential/curved-boundary and native C++ source oracle and adds six corrupted OBJ negative runs for two unapproved centroid modes. No production `src/`, `include/`, default CLI, scientific formulas, acceptance/rollback or selectable mesh mode changed.

**Exact qualification and merge:** [feature Actions #42999207821](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42999207821) **SUCCESS** on exact feature `1366ce697a5d04156ba58bb890c989f711d39f93` with all four remote jobs: root 81/81 CTest including `quad.m4.four_node_ownership`, 527/527 Python tooling, seven CLI denials, native Linux GCC/Windows MSVC QUAD and strict frozen Eistute/Book equivalence. Research [ownership artifact #13846190675](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42999207821/artifacts/13846190675) uploaded. [PR #205](https://github.com/tiagosombrra/apmesh-modernization/pull/205) merged into `quad-templates` at `4ffd9cdac09d99352e0500df8a0b5467054949c3` after checking no unexpected code paths. [Postmerge #43000273810](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43000273810) was **in_progress** when this entry was prepared. No clone/native tests in this chat container; native evidence is GitHub-hosted. [Evidence receipt](evidence/M4_FOUR_NODE_PHYSICAL_OWNERSHIP_20261111.json) lists exact paths, numbers and explicit limitations.

**Non-claims and next scientific/engineering blocker:** physical curved QUAD research polyline faceting is *not* exact curved integration or robust imported CAD, historical 1993 contour contraction/insertion is *not* implemented, centroid mode *not* approved, multipatch shared control and repeated adaptation rollback *not* qualified; production element and all-QUAD remain disabled. Verify on-merge CI #43000273810 before declaring stage closed; next bounded gate is real shared-boundary physical synchronization with negative controls, then adaptation lifecycle under failure without any default TRI change.

## 2026-11-11-24 — All tracked models inventory, high-valence seam risk audit (PR #206)

**User question:** verify whether Eistute, Book, Pneu, Bolha and other APMesh models can use the completed research QUAD/TRI physical prototype. This session did **not** claim model-wide hybrid meshes or an adapted generator.

**Grounded source inventory:** three versioned `.bp` files: `eistute2.fixed.bp` 64 control records / 4 Bezier patches; `book_v7a.bp` 340 / 28; `ribbed_bracket_nm_decor.bp` 125 / 13. Static C++ `Models3d` scan: 14 built-in geometry factories, 45 Bezier and 23 Hermite patch construction sites. Notable built-ins: `ModelPneu` 2 Hermite; `ModelNariz` 14 Hermite; `ModelUtahteapot` 32 Bezier; `ModelCurvaBezier` 1 Bezier (current physical M4 witness). No tracked `ModelBolha` name or `input_models/bolha` path; don't invent a matching surface.

**Scientific discovery:** control-curve coordinate matching at 1e-7 finds one 4-way shared edge for Eistute (12 single-owner curves), one **28-way spine** for Book (84 single-owner curves), four 3-way curves for Ribbed Bracket (17 ordinary paired and six single-owner). Deliberate nonmanifold sheet junctions are not invalid input by default; naïve pairwise welding is unsafe. Independently sampled 9x9 Bernstein normals per external Bezier patch reveal 60 Eistute samples with normals opposite the corresponding center normal; this is a directional diagnostic, NOT a proof of invalid chart orientation. No sampled normal length was zero, but global regularity is NOT established.

**Implemented and qualified:** `tests/quad/audit_model_catalog.py` validates the exact source inventory, independent 9x9 parametric derivatives, shared control-curve valence, file SHA-256 and **seven malformed `.bp` rejections**. The existing four-job `.github/workflows/quad-research-validation.yml` now runs this source audit and uploads a 14-day JSON artifact. [Exact feature Actions #43009461867](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43009461867) SUCCESS (all 4 jobs), **81/81 root CTest**, **527/527 Python tooling**, **7/7 CLI negatives**, seven malformed model input controls, native Linux/Windows QUAD and frozen scientific Eistute/Book TRI comparison. [Artifact #13849658571](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43009461867/artifacts/13849658571). [PR #206](https://github.com/tiagosombrra/apmesh-modernization/pull/206) integrated to research as `eb28df95c150e6ed4825271d86c67b9c7f498732`; exact [postmerge #43010542893](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43010542893) pending at the time of this entry. Only audit source, research documentation and CI workflow changed. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` preserved.

**Closure limitations and next:** No production or research full-model conforming Eistute/Book/Bracket/Pneu mesh generated; no automatic historical 1993 exterior; no approved centroid; no global Jacobian proof. `PatchReader::ReaderFilePatches` is existing real Bezier file entrypoint; Hermite factories need separate `PatchHermite` adapter. **Next PR:** read `.bp` with production `PatchReader`, inspect actual `PatchBezier` per patch and safely prove boundary provenance on a two-patch Bezier fixture, then Eistute's 4-way and Book's 28-way physical junctions. Do not retrofit a simple manifold union to page/spine models.

## 2026-11-11-25 — Exact merged model-catalog qualification closeout

[Postmerge Actions #43010542893](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43010542893) **SUCCESS** on exact source merge `eb28df95c150e6ed4825271d86c67b9c7f498732`, four of four jobs. Root Linux logs explicitly verify **81/81 CTest**, **527/527 Python tooling**, **7/7 CLI negatives**, **7 malformed .bp audit rejections** and the `quad_model_catalog=ok` output. Native GCC/Windows MSVC QUAD suites and frozen TRI Eistute/Book scientific comparison are also successful. Exact merged-source [catalog artifact #13850132945](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43010542893/artifacts/13850132945) uploaded. This supersedes the pending postmerge status in session 24. Documentation-only source checkpoint follows the qualified code; original scientific input files and `main` unchanged.

Scientific blockers remain as previously recorded: high-valence model edges cannot be modeled as pairwise manifold welding, strong Eistute sampled normal rotations need full patch-aware orientation policy, Hermite-specific physical adapter and original 1993 algorithm approval remain open. **No full Eistute/Book/Pneu QUAD/TRI mesh was generated by this model inventory audit.**

## 2026-11-11-26 — Pairwise physical boundary preflight submitted (CI pending)

**Verified baseline:** live `quad-templates=5a65be92c64d40e6394236d50ebe1363731c427e`, `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; PR #206 and exact postmerge Actions #43010542893 previously SUCCESS, 81 CTest / 527 Python / 7 CLI / native Linux+Windows and frozen Eistute/Book equivalence. No other open PR at new branch creation.

**Changed candidate:** [draft PR #207](https://github.com/tiagosombrra/apmesh-modernization/pull/207), head `8fa12096ea2d3aea7e3c74f880cf7b3d7f6a8c86`, adds `tests/quad/patch_reader_pairwise_probe.cpp`, root `CMakeLists.txt` CTest, refreshed `docs/architecture/source_inventory.json` CMake SHA-256 and [M4 boundary scope](M4_PAIRWISE_BEZIER_BOUNDARY_20261111.md). Five generated `.bp` fixtures invoke the actual `PatchReader::ReaderFilePatches`; two admit only a seven-curve/two-patch seam with curve-pointer identity, per-incidence UV orientation, 9x9 analytic XYZ/Qu/Qv and 17 mapped seam/tangent samples. Three negative fixtures must reject seam displacement, reversed chart normal and triple-valence sharing. No real model-wide QUAD/TRI mesh, original 1993 algorithm or production behavior is changed.

**Tests actually executed:** [CI #43023937780](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43023937780) started on exact PR head. Native standalone Linux QUAD job **SUCCESS** at observation; root 82 CTest gate, 527 Python, 7 CLI, Windows native, frozen scientific TRI comparison and postmerge checks **PENDING**. No native code or scientific articles were executed inside this chat container; its Git clone cannot resolve GitHub. Do not equate source review with passed CTest.

**Handoff:** inspect the exact CI run and fix any build/test failures; only merge a qualified PR to `quad-templates`, verify postmerge, and then begin per-patch physical source-Quadtree candidate export with high-valence seam safety preserved. `main` untouched.

## 2026-11-11-27 — Pairwise PatchReader boundary gate merged; source postmerge pending

**Feature qualification:** [PR #207](https://github.com/tiagosombrra/apmesh-modernization/pull/207) candidate `8fa12096ea2d3aea7e3c74f880cf7b3d7f6a8c86` passed all four exact-head [CI #43023937780](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43023937780) jobs. Full root Linux log proves `quad.m4.pairwise_bezier_boundary` compiled and passed as CTest #71, **82/82 CTest** and **527/527 Python**; native research Linux and Windows each passed **13/13**; frozen Eistute/Book TRI scientific comparison passed. Review confirmed four changed paths only: isolated C++ probe, root CTest, matching source inventory CMake digest and research scope document. No `src/`, `include/`, production CLI or model assets modified.

**Research merge:** PR marked ready after checks, then successfully merged to `quad-templates` as `e2435dc796a5b455c3eae88d1b5ab926a0cb87dd`; live branch head and unchanged modernization main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` were checked. Exact [postmerge Actions #43025314995](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43025314995) began on that merge SHA and was still **in progress**, not a completed gate at checkpoint writing.

**Scope/next:** This is only real `.bp` loader/seam admission on controlled patches, *not* full external-model conforming QUAD/TRI, a production element, historical 1993 method or an approved high-valence sheet policy. No native local Windows/WSL tests, memory sanitizer or unmeasured model-wide gates are claimed. Verify postmerge CI before the next isolated per-patch physical candidate export and sheet-aware Eistute/Book edge tests; preserve original TRI `main`.

## 2026-11-11-28 — PR #207 postmerge qualified; PR #208 native-origin physical two-sheet candidate opened

**Prior gate closure:** Exact research merge `e2435dc796a5b455c3eae88d1b5ab926a0cb87dd` passed all four [postmerge CI #43025314995](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43025314995) jobs. Root 82 CTest, 527 tooling Python, seven mode rejections, Linux GCC/Windows MSVC research QUAD and frozen strict TRI Eistute/Book equivalence all passed. The previous session 27 pending status is superseded; this is CI evidence, not local native qualification.

**Actual new candidate:** [draft PR #208](https://github.com/tiagosombrra/apmesh-modernization/pull/208), feature head `6fd2d76253877e51e2b2f7d75937f941cea90e79`. Only `tests/quad/pairwise_physical_sampler.cpp`, `tests/quad/test_m4_pairwise_physical_candidates.py`, `CMakeLists.txt`, `docs/architecture/source_inventory.json`, `.github/workflows/quad-research-validation.yml` and [bounded scope](M4_NATIVE_PAIRWISE_PHYSICAL_CANDIDATES_20261111.md) change. Actual source is native C++ Quadtree 42 UV QUAD + M5 36 experimental Lawson TRI; output is two per-patch physical OBJ candidates for each of two temporary real-loaded Bezier models and two experimental centroid rules. The real production `PatchReader`/`PatchBezier` evaluates 69 physical samples per patch; the independently specified oracle checks derivative geometry, 120 oriented face subtriangles/patch, four opposite-direction seam edges, five equivalent physical seam site coordinates without global node welding. Seven input and twelve output mutations must fail closed.

**Qualification status:** [CI #43027138751](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43027138751) was in progress at the moment of this checkpoint; do **not** claim 83/83 CTest, 527 Python, native Windows/Ubuntu, CLI or strict Eistute/Book baseline on the new SHA until completed. No direct native compiler/Windows memory sanitizer execution in this ChatGPT environment. The separate modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` is preserved.

**Next:** inspect this exact-head feature CI, repair only bounded research code if a test fails, then (after all required gates) merge to `quad-templates` and qualify the merge SHA. The subsequent research problem is model-specific high-valence Bezier chart/boundary incidence for Eistute, Book and Ribbed Bracket; no arbitrary manifold welding or historical 1993 claim.

## 2026-11-11-29 — Distinguish PR test merge from exact candidate and strengthen seam invariance

**Initial candidate run:** [CI #43027138751](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43027138751) completed all four jobs successfully on GitHub's synthesized `pull_request` merge ref; root 83/83 CTest including `quad.m4.pairwise_native_physical_candidates`, 527/527 Python, native GCC/MSVC research QUAD, Eistute/Book TRI strict parity and artifact [#13858266044](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43027138751/artifacts/13858266044) published. This is **not** a standalone exact-feature-head push qualification; distinguish both refs.

**New stronger oracle:** On the same PR #208 feature, exact source `8c03fe0a0bcd72588c83c3eab045a3332ff57534` adds independent physical seam-site equality **between both unapproved interior-point rules**, per model. Per-patch XYZ/derivatives, directed seam edge, candidate OBJ topology and 7 input/12 output negative controls remain unweakened. There are now two required remote runs: exact `push`-head [Actions #43028264221](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43028264221) and separate `pull_request` test-merge [#43028272532](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43028272532). At this observation, GCC/MSVC research QUAD and frozen TRI comparison passed, **both full Linux root CTest jobs were still building**, so exact-head qualification and merge are blocked. No files in production `src/` or `include/` changed, modernization `main` untouched.

**Next:** inspect both Linux CI results, confirm the new seam-centroid invariant plus 83/527 and artifact SHA, then review and merge to research only when actual direct-head checks pass; postmerge source SHA requires its own run. No model-wide Bezier or Hermite claims.

## 2026-11-11-30 — PR #208 exact-head qualified and merged; postmerge pending

**Corrected run provenance:** [feature branch `push` CI #43028264221](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43028264221) **SUCCESS** on exact `8c03fe0a0bcd72588c83c3eab045a3332ff57534`; Linux CTest output confirms new test #72 of 83 and **83/83 PASS**, **527 Python PASS**, native GCC/MSVC 13 each, seven CLI mode negatives and strict frozen Eistute/Book TRI equivalence. Actual feature-SHA `quad-m4-pairwise-physical` [artifact #13860971504](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43028264221/artifacts/13860971504) retains per-patch physical OBJ/CSV and JSON. [Separate PR test-merge CI #43028272532](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43028272532) also **SUCCESS**. The strengthened test rejects a change in shared seam physical sites across experimental centroid alternatives.

**Actual research merge:** [PR #208](https://github.com/tiagosombrra/apmesh-modernization/pull/208) reviewed as six changed paths limited to research, root CTest, CI and CMake digest, with no `src/`/`include/` modifications. Marked ready and merged as `0cbb77f9ab8ac70445244f1543cb33728c99f88d`, verified live `quad-templates`; original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. [Postmerge Actions #43029796292](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43029796292) started on the **exact merge SHA** and was **in progress** when this checkpoint was written; it must be rechecked before final closure.

**Limited scientific deliverable:** eight physical patch-local OBJs (two indexed Bezier `.bp` fixtures, two centroid witnesses, two patches each), real C++ Quadtree 42 QUAD plus M5 36 experimental TRI per patch, 69 patch-local nodes/120 oriented physical subtriangles and four conforming 3D seam edges/five sites. A virtual 133-node global count does **not** instantiate a joined `SubMesh` nor qualify nonmanifold welding. No full Eistute/Book/Bracket/Pneu physical mesh, original 1993 procedure, normal-field proof, historical centroid decision, rollback or production mode. No local WSL/MSVC sanitizer gate executed.

**Next:** finish exact-merge CI; then research explicit per-sheet incidence and physical per-patch export of the 4/28/13 real external Bezier model patches. Avoid naïve union of Eistute 4-way, Book 28-way or Bracket 3-way edges, and keep Hermite `ModelPneu` separate.

## 2026-11-11-31 — PR #208 postmerge qualified; PR #209 real external BP candidates submitted

**Prior gate qualified:** Postmerge Actions #43029796292 at https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43029796292 completed SUCCESS on PR #208 merge `0cbb77f9ab8ac70445244f1543cb33728c99f88d`, all four jobs, 83 root CTest, 527 Python and frozen scientific TRI parity.

**Actual new candidate:** Draft PR #209 https://github.com/tiagosombrra/apmesh-modernization/pull/209 at feature SHA `705136518220138b57dc205b03aed94633e94b33`. Adds only two tests (production-backed C++ patch sampler and independent Python Bernstein/physical/curve incidence audit), one root CTest plus CMake source-inventory hash, CI archive, and research scope document. Reads 45 real source BP patches across Eistute 4, Book 28 and Ribbed Bracket 13, observes native Quadtree/M5 UV and evaluates each patch independently. Eighty? No: **90 patch-local OBJs** (45 patches × 2 unapproved centroid variants); 42 native QUAD plus 36 experimental TRI each, 69 patch-local vertices; model-shared curve groups diagnosed, never globally welded.

**Scientific nonclaims:** This repeated source UV topology is not actual model curvature-adapted tessellation or a full-model conforming surface. The 4/28/3-way incidences require a separately approved per-sheet graph policy. No Hermite Pneu evaluation, C1/global normal proof, original 1993 insertion/contour contraction or production QUAD enabling. `main` preserved at `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

**Gate:** CI #43033602254 https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43033602254 was IN PROGRESS; new 84th root CTest, 527 Python, seven CLI negative and separate native Linux/Windows/strict Eistute/Book TRI jobs not yet all qualified. Next verify exact head and fix failures; merge only after green and qualify exact source postmerge.

## 2026-11-11-32 — PR #209 root gate pending on existing M3-5 diagnostic

**Recorded observation:** Exact [CI #43033602254](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43033602254) feature candidate `705136518220138b57dc205b03aed94633e94b33` still has three successful completed jobs (standalone research QUAD Linux/Windows and strict frozen Eistute/Book TRI comparison). The full root Linux job completed its compilation but remains executing the *existing* M3-5 GDB diagnostic capture before CTest. It has not yet executed the new external 84th CTest according to GitHub's last visible step summary. No actual failures observed in reported jobs, but the remaining gates and physical artifact publication are unmeasured, not passed.

**No workaround:** Do not silently time-limit/suppress the diagnostic or bypass root CTest. PR #209 remains draft/unmerged; canonical research state and `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` are preserved. Last explicit action for the next connected agent: inspect Actions #43033602254; if root job eventually fails or stalls through its configured job limit, inspect full log and repair root-cause in a separately classified engineering review; do not weaken the frozen TRI oracle. Otherwise certify new 84/527 and 90 per-patch OBJ witnesses and review the physical quality JSON before research merge.

## 2026-11-11-33 — Diagnose external runner DNS failure; restore required CI path

**Observed failure:** PR #209 initial candidate `705136518220138b57dc205b03aed94633e94b33` ran [CI #43033602254](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43033602254). The Linux baseline job successfully built 923 compilation/link steps, including `quad_m4_external_bezier_sampler`, but stopped at a *preexisting optional GDB backtrace capture* before root CTest because its `apt-get update`/`install gdb` could not resolve `azure.archive.ubuntu.com` (exit 100). Three unrelated jobs (native QUAD Linux/Windows; strict TRI scientific equivalence) succeeded. No 84 CTest, 527 Python or physical diagnostic OBJ archive was executed in that initial failed job. This is an actual GitHub-hosted network/DNS infrastructure failure, not evidence of physics correctness or incorrectness.

**Actual repair:** Updated only the optional GDB portion of `.github/workflows/quad-research-validation.yml` on the same feature to exact `a5f46fb5da336fee2c27cf6f9e1e102832a12b30`: when GDB exists run its best-effort diagnostic; when absent explicitly warn `BACKTRACE NOT COLLECTED`, without an apt/network install. This preserves mandatory full root `ctest --preset local-serial --output-on-failure --no-tests=error`, Python 527, CLI negatives, native Linux/Windows QUAD and frozen TRI parity unmodified. The unavailable backtrace is not marked passed; no production code or scientific oracle changed.

**Current gate:** [exact feature push CI #43044996136](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43044996136) and [PR test-merge CI #43045007952](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43045007952) were initiated on the feature HEAD, and native QUAD plus strict TRI jobs passed. Root Linux CTest #84 and physical model artifacts remained pending at this observation. No merge performed. Next inspect both root jobs, inspect 90 patch-local OBJ/archive metrics if produced, and only then qualify/merge/revalidate source.

## 2026-11-11-34 — PR #209 exact-head qualified; real models measured; research merge

**Candidate CI:** exact source head `a5f46fb5da336fee2c27cf6f9e1e102832a12b30` passed 4/4 jobs in [push Actions #43044996136](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43044996136), and separately [PR merge-ref #43045007952](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43045007952). GitHub Linux logs explicitly confirm root **84/84 CTest** (new test #73), **527/527 tooling Python**; native research GCC/MSVC QUAD and strict frozen Eistute/Book TRI equivalence succeeded. Source still unchanged under production `src/`, `include/`; optional GDB missing is reported, not claimed collected.

**Artifact independently inspected:** [artifact #13867960046](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43044996136/artifacts/13867960046) downloaded from GitHub and opened. Inner ZIP contains exactly 90 patch-local OBJ, 14 CSV and one JSON. Source model counts 4 Eistute/28 Book/13 Ribbed Bracket; geometry lifted from real C++ Quadtree 42 QUAD + experimental M5 Lawson 36 TRI, 69 patch-local nodes, for two unapproved point rules. 3,780 QUAD / 3,240 TRI across all output files, NOT shared globally. Production owned curves: Eistute 13 (one valence 4), Book 85 (one valence 28), Bracket 27 (four valence 3). Maximum seam site gap respectively 0, 0, 2.6645352591003757e-15; minimum sampled cross norm respectively 12.003695754670666, 1.9994063772945894, 1.499999399999998. Zero sampled near-zero Jacobians, degenerate local facets and nonpositive local facet alignment; Eistute has 36 patch-center-opposite differential normals per rule, which does not imply inverted geometry. **No global proof of conforming mesh, node welding or regularity.** Four explicit mutations rejected. Measurements appended to [physical diagnostic evidence](M4_EXTERNAL_BEZIER_PHYSICAL_DIAGNOSTICS_20261111.md).

**Integration:** PR #209 marked ready then merged into research-only `quad-templates`, exact code-merge SHA `ff97e9c15d2b652433ecb494a90822fce88bea1b`; direct live research and unchanged modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` verified. [Exact merged-source postmerge #43046674566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43046674566) had 3/4 jobs success (native GCC/MSVC QUAD, frozen TRI), root Linux build in progress. Must validate that last gate before final closure, and keep nonmanifold sheet policy scientifically open.

## 2026-11-11-35 — Exact merged-source PR #209 fully qualified; permanent evidence and next sheet graph

**Postmerge closure:** GitHub Actions [#43046674566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43046674566) **SUCCESS** on exact merged source `ff97e9c15d2b652433ecb494a90822fce88bea1b`; all four jobs passed. Linux logs confirm `quad.m4.external_bezier_physical_diagnostics` CTest #73 PASSED, **84/84 root CTest** and **527/527 Python**; native Linux/Windows research QUAD and strict frozen TRI Eistute/Book comparisons passed. Research source artifact [#13868441332](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43046674566/artifacts/13868441332) contains the physical model manifest and ZIP. GitHub absent-GDB backtrace remains explicitly NOT COLLECTED; the required root gates passed.

**Persistent scientific evidence:** [M4_EXTERNAL_BEZIER_PHYSICAL_20261111.json](evidence/M4_EXTERNAL_BEZIER_PHYSICAL_20261111.json) captures 45 actual source patches, 90 per-patch OBJ output inventories, model source SHA-256 and exact feature/merge CI identities. [Physical diagnostics report](M4_EXTERNAL_BEZIER_PHYSICAL_DIAGNOSTICS_20261111.md) records measured seam gaps, sampled Jacobian magnitudes, 36 patch-center-opposed Eistute normals per centroid rule and required scope disclaimers. [Implementation roadmap](IMPLEMENTATION_ROADMAP.md) updated the completed bounded subgate and the distinct unresolved high-valence incidence/sheet reconciliation. No changed production TRI code.

**Next:** new isolated feature to inspect interpatch sheet-aware normal/tangent compatibility for Eistute 4-way, Book 28-way and Bracket 3-way control curves, with source-local node IDs and no automatic welding or scientific approval. Separate Hermite Pneu and 1993 Delaunay/contour contraction remain open. Modernization main verified unchanged `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; no local native Windows, WSL, sanitizer or historic scientific validation claimed.

## 2026-11-11-36 — M4 sheet-aware incidence graph candidate; required CI pending

**Baseline verified:** Research `quad-templates` at `a54d762db5799cc7a3f04f8c1fbed475bbde2a99`, modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; PR #209 source `ff97e9c15d2b652433ecb494a90822fce88bea1b` had exact-source Actions #43046674566 success (84 CTest, 527 Python, native GCC/MSVC and frozen TRI parity). There were no other open PRs before starting.

**Implemented feature:** [PR #210](https://github.com/tiagosombrra/apmesh-modernization/pull/210), draft head `c4dcf447fa6c918d69b000c75b189e58278f69ed`. Added `tests/quad/test_m4_sheet_incidence_graph.py`, `docs/research/quad/M4_SHEET_INCIDENCE_GRAPH_20261111.md`, one root CTest with explicit dependency on real-model physical evidence, CMake SHA inventory update and bounded 14-day JSON+DOT graph artifact. Uses existing production C++ PatchReader/Bezier and independently audited `.bp` source controls; performs no new physical node ownership or generator changes. Curve incidences are modeled as hyperedges. Valence3/4/28 pairing is quarantined, valence2 is a measured review candidate only. Samples five canonical UV/physical seam points; audits C0 gaps, tangents, patch winding, projected inward sectors; 9 synthetic/control mutations per model must pass for admission API. Real source pairwise graph counts independently observed: Eistute one 4-owner curve (6 hypothetical pairs), Book one 28-owner curve (378 hypothetical pairs), Ribbed Bracket four 3-owner curves (12 hypothetical pairs) plus 17 2-owner curves. None of these pair counts imply welding.

**CI and scientific limits:** [Exact feature push #43056284526](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43056284526) and [PR test-merge #43056373612](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43056373612) initiated; standalone native QUAD Linux/Windows and scientific Eistute/Book TRI equivalence passed, root Linux build still in progress. Do NOT claim the 85th graph CTest, tool suite, CLI negative suite or artifact yet. All-QUAD, original 1993 contour contraction / Delaunay insertion, model-wide welded QUAD/TRI and Hermite Pneu remain unavailable.

**Next:** verify exact-head 85/85 CTest and 527 tooling; repair only actual failing research test if needed; classify graph results and conduct source review, then merge research PR and certify exact merged source. Do not silently accept any high-valence welding. Local Windows/WSL/sanitizers unexecuted.

## 2026-11-11-37 — PR #210 exact head qualified, sheet graph integrated, postmerge still pending

**Execution:** Research-only [PR #210](https://github.com/tiagosombrra/apmesh-modernization/pull/210) implements immutable real-model Bezier curve incidence hypergraphs in a new Python test; no new C++ production code. Feature `c4dcf447fa6c918d69b000c75b189e58278f69ed` was independently qualified on direct push [Actions #43056284526](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43056284526) and test-merge [Actions #43056373612](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43056373612), each **4/4 jobs success**. Logs show CTest #74 new sheet graph PASS, 85/85 CTest total and 527/527 Python; native QUAD GCC/MSVC, CLI negatives and exact frozen TRI parity passed. Captured six JSON graph plus six DOT artifacts. Scientific evidence manually inspected from the GitHub artifact and persisted in `evidence/M4_SHEET_INCIDENCE_GRAPH_20261111.json` (first evidence commit `e69382b445391cc4f0cd207b97d8c198e18ba930`).

**Measured patch-sheet graph:** Eistute one degree-4 curve with six pair combinations quarantined, four candidate-only isolated patches. Book one degree-28 shared spine with 378 pair combinations quarantined, 28 candidate-only isolated patches. Ribbed Bracket four degree-3 curves with 12 combinations quarantined, 17 degree-2 curves compatible as *geometry candidates requiring advisor approval*; those form only the candidate components `[0..9]`, `[10]`, `[11]`, `[12]`. Across both centroid rules 27 fail-closed synthetic/admission cases; **396 high-valence combinations never welded**. No actual `NodeAdaptive` reidentification or model-wide `SubMesh` ownership, nonmanifold topology approval, historical 1993 algorithm, or production all-QUAD.

**Integration and pending gate:** PR reviewed as five paths only under CMake/digest, research Python test, CI and docs, no `src/` or `include/` source change. Marked ready and merged research `quad-templates` at `afa15277aef35aa5beae9a980b11e66a74c8dba3`. [Merged-source postmerge #43057855090](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090) started but was IN PROGRESS at checkpoint. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` untouched. Do not label the source merge final until exact postmerge passes.

**Next:** confirm postmerge four jobs 85/527 and artifact, update evidence + roadmap with exact result, then prepare scientific sheet-continuation decision table with per-model high-valence physical sector ordering. Physical welding and Hermite support remain separate future gates.

## 2026-11-11-38 — PR #210 exact source M4 sheet-incidence qualification

**Verified:** Source merge `afa15277aef35aa5beae9a980b11e66a74c8dba3` passed [postmerge Actions #43057855090](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090) all 4/4 jobs. Linux root **85/85 CTest** including `quad.m4.sheet_incidence_graph` #74, **527/527 Python**, native QUAD Linux/Windows, seven CLI negatives and strict frozen Eistute/Book TRI baseline all passed. Premerge feature SHA `c4dcf447fa6c918d69b000c75b189e58278f69ed` and PR test-merge also 4/4 success. Actual merged-source [graph artifact #13873615406](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090/artifacts/13873615406) published 6 JSON + 6 DOT graphs and manifest.

**Observed incidence graph:** Eistute 4 patches, 1 degree-4 curve (6 pairs quarantined); Book 28 patches, 1 degree-28 spine (378 quarantined); Ribbed Bracket 13 patches, 4 degree-3 curves (12 quarantined) plus 17 degree-2 geometric review candidates. Candidate-only Bracket components: `[0..9]`, `[10]`, `[11]`, `[12]`. Total 396 high-valence potential pairs quarantined and **zero welded physical nodes**. 27 admission/negative controls passed and both experimental center rules yield the same classification. No global conforming mesh, original 1993 method, fixed world-normal assumption or production QUAD.

**Continuity:** [Permanent evidence](evidence/M4_SHEET_INCIDENCE_GRAPH_20261111.json) updated from pending to postmerge SUCCESS, [roadmap](IMPLEMENTATION_ROADMAP.md) records the bounded M4 research subgate, and [advisor decision matrix](M4_SHEET_POLICY_DECISION_MATRIX_20261111.md) sets out unresolved manifold/nonmanifold/split-sheet interpretations. Source modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` remains unchanged. No local Windows/WSL/sanitizer qualification claimed.

**Next:** explicit high-valence sheet-topology decision from advisors, beginning Eistute axial curve; approve source-SHA-bound patch-side incidences before any welding code. Node ownership, conforming multi-patch generation, rollback, Hermite Pneu/Nariz and historical 1993 Delaunay/contour contraction remain separate gates.

## 2026-11-11-39 — Audit and corrected opt-in QUAD interior template delivery sequence

**User clarified the actual feature:** when activated, the QUAD T1–T6 template elements must replace the TRI template elements **only in the existing Quadtree-interior template stage**. Existing curve discretization, shared curve behavior, UV boundary construction, remaining AFT triangle completion, adaptation policies and untouched default TRI mode must be retained. This is first a **quad-dominant** opt-in implementation, not all-QUAD or unconditional replacement of the entire triangular pipeline. This clarification supersedes the *priority* of the prior high-valence graph work, without falsifying its measured research results or erasing historical records.

**Source audit, not runtime qualification:** Read research `quad-templates=103bc0282d9d3ca566dcbdf830065459f558a4bf`, modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; no open PRs. Inspected real `RunApplication`, runtime config, `Quadtree/QuadtreeCell::makeTemplateBasedMesh`, `AdvancingFront::execute`, `Face` 3-vertex contract, `Adapter::AdaptDomain`, `GeneratorInitialMesh`, curve adaptation and shared-curve synchronization configuration, isolated QUAD UV emitter and physical four-node research element, dispatch rejection, physical 42 QUAD + 36 M5 experimental TRI artifacts, and existing milestone/1993 numerical gates.

**Findings:** The CLI currently **rejects** `MESH_ELEMENT_KIND=quad_uv` intentionally and `test_m3_dispatch.py` expects this; the 1993-proposed QUAD templates/UV emitter **observe and export** native C++ Quadtree data but **do not replace the TRI faces** in live `AdvancingFront`. Published `Face` and `TriangleAdaptive` paths have 3-node casts, so mixing 4-node elements needs a typed owned intermediate and conversion. The fixed 69-node, 42 C++ QUAD + 36 Lawson TRI fixture and 45 real-Bezier sampled patches are not the curvature-driven complete adaptive AFT pipeline. An explicit scientific interior-point formula remains unapproved. Shared Bezier curves, orientation and curve-point adaptation are already in the program; note that the separately disabled shared-curve-sync option exists. High-valence PR #210 diagnostics remain useful but must not block interior-only QUAD implementation.

**Actual changes:** Created [OPTIN_QUAD_IMPLEMENTATION_AUDIT_20261111.md](OPTIN_QUAD_IMPLEMENTATION_AUDIT_20261111.md), a source-grounded P0/P1/P2 defect/priority inventory with R0–R6 acceptance tests, verified API sites and full risk limits. Added a course-correction priority to [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md), preserving original M0–M9 history. Updated [STATE.md](STATE.md) checkpoint 39 with the precise next task. No C++ source, CMake, scientific model, production TRI code, oracle, user-facing CLI behavior or test was modified.

**Evidence:** Last source CI from research [PR #210 postmerge Actions #43057855090](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090) was previously measured 4/4, 85/85 CTest, 527/527 Python and strict frozen Eistute/Book TRI. **No native test, Python test, manual model run, WSL, MSVC or sanitizer was newly executed in this audit session.** Docs-only SHA movement is not equivalent to a fresh scientific runtime qualification.

**Next engineering PR:** isolated, opt-in QUAD T1–T6 selection from the SAME real refined tree, zero duplicate interior TRI publication, explicit QUAD-TRI AFT front/edge identity, then 4-node typed `SubMesh` publication; no `quad_uv` acceptance until a real curved full-patch result with exterior AFT TRI and negative controls. Afterward qualify repeated adaptation and Eistute/Book/Ribbed Bracket in the original pipeline. Preserve the historical 1993 point rule as unapproved and high-valence sheet policy as a separate later scientific decision.

## 2026-11-11-40 — R1 live Quadtree interior selector candidate and exact-head CI pending

**User-approved goal preserved:** opt-in substitution of QUAD templates for TRI templates *on eligible interior leaves of the same real quadtree*, retaining original curve and patch boundary discretization and TRI Advancing Front exterior completion. Keep default `MESH_ELEMENT_KIND=tri` and existing scientific output frozen. Read live research base `4cdebb62ec532c45d9834a72e3177a14a0dd3a87` and modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, no concurrent PR.

**Implementation on isolated feature:** [draft PR #211](https://github.com/tiagosombrra/apmesh-modernization/pull/211), feature `quad/integration-r1-interior-template-dispatch-20261111`, exact latest source `e2e106238d7482656a098f8e26bb3f31ae2a7b4d`. Added `research/quad/interior_template_dispatch.h/.cpp`: per-attempt one-of-two research dispatcher, actual legacy `Quadtree::makeTemplateBasedMesh` on TRI selection or owned `EmitLeafQuads` value-only UV output on experimental QUAD selection, pre-published TRI-owner rejection, no double selection, explicit polygon point policy, exact one-owner directed region frontier edges, no tree mutation on successful QUAD. Added `tests/quad/interior_template_dispatch_contracts.cpp` (12 authored cases, expected real uniform/refined QUAD 16/42, directed UV interface 16/20, TRI direct reference parity, input and callback negatives/retry); updated `tests/quad/CMakeLists.txt` for native Linux GCC and Windows MSVC, and `research/quad/README.md` for scope/remaining limitations. No `src/`, `include/`, root CMake or CLI mode modified; production TRI unaffected by this candidate.

**Scientific and execution boundaries:** Test cases are *authored*, not yet proven to pass. Feature [direct push CI #43098029135](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43098029135) and [PR test-merge CI #43098033267](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43098033267) were QUEUED at this checkpoint. Local clone `git ls-remote` failed with DNS resolution of github.com, so no local build or sanitizer validation claimed. Last *earlier* source gate [Actions #43057855090](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090) qualified 85/85 CTest, 527/527 Python; it is not evidence of new R1 code. Permanent [unqualified feature evidence](evidence/R1_INTERIOR_TEMPLATE_DISPATCH_20261111.json) records exact source scope and CI URLs.

**Next:** inspect exact feature run jobs (both Linux and Windows native including new R1 CTest; frozen full root CTest/Python/TRI) and repair any demonstrated failures. Merge only after full required green checks; verify exact research postmerge. Research QUAD selection still does NOT publish the live AFT interface, true mixed QUAD/TRI `SubMesh`, a real full-patch OBJ or production `quad_uv` CLI. R2 owns those milestones; advisor-approved 1993 centroid and high-valence welding remain separate scientific gates.

## 2026-11-11-41 — R1 native CI repair, qualified premerge and research PR #211 integration

**Scope:** Continue [PR #211](https://github.com/tiagosombrra/apmesh-modernization/pull/211) from session 40. Confirm the user-approved target is opt-in replacement of only existing TRI Quadtree **interior template faces** with actual T1–T6 QUAD; retain source curve adaptation, oriented patch boundary, normal AFT exterior TRI and original default TRI generator. Read live SHA and PR. No changes to production `src/` or `include/`, original TRI code, frozen science/point rules, CLI mesh admission, or modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

**Implementation quality improvement:** On feature `quad/integration-r1-interior-template-dispatch-20261111`, added `InteriorTemplateSelection::quad_face_origins` and ordered one-to-one `LeafPolygonOrigin` mapping for each actual QUAD, preserving source real cell ID, leaf ordinal, relative depth, pattern T1–T6 and polygon ordinal. Extended the native contract to check this mapping against independent source capture in all positive and repaired retry cases. The legacy TRI selection still calls the unchanged original method, QUAD still cannot publish overlapping TRI templates, and the nonfunctional QUAD CLI remains rejected.

**Actual CI defect repaired without gate relaxation:** The prior direct [Actions #43103466011](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43103466011) failed mandatory root `tooling.controls` because changing `tests/quad/CMakeLists.txt` left the source inventory's build-input SHA stale. Independent SHA-256 computation reproduced original `2e0508291719230c73cb92b522cf6d5eb8ed93d85f2a416c7ba9810daeae3799` and new file `0554f07f5f6c5803b6b91c49e10fde23c74c664e82c6471eeb153a2ebd0b3712`. Updated only the tracked `docs/architecture/source_inventory.json` entry. No test skipped, tolerance changed or expected outcome weakened.

**Qualified source validation before merge:** Feature SHA `72aebb902632971a358e006c5d3b51ed3370462b`. Direct push [Actions #43104622677](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104622677) **SUCCESS 4/4**; PR test-merge [Actions #43104631590](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104631590) **SUCCESS 4/4**, each with 14/14 CTest native Linux GCC and 14/14 native Windows MSVC, 85/85 root CTest and all 527 Python tooling tests, frozen Eistute/Book TRI scientific equivalence. Verified `quad.r1.interior_template_dispatch` was executed and passed on both native platforms. The new R1 test has 12 authored positive/negative controls exercised by successful native CTest.

**Actual integration:** Marked PR ready only after two complete success workflows; merged via protected expected feature SHA into `quad-templates` at **`254d5f9aadf8cbac5e0f31780b69fb564291d2a5`**. Confirmed `main` unchanged. Exact merged-code [Actions #43106047878](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43106047878) was **IN PROGRESS** at session checkpoint with 3/4 jobs passed (Linux/Windows native, frozen scientific TRI), required Linux root CTest/Python still in build. **Do not treat 3/4 as scientific postmerge closure.**

**Documentation/continuity:** Created [R2_LIVE_AFT_QUAD_INTERFACE_DESIGN_20261111.md](R2_LIVE_AFT_QUAD_INTERFACE_DESIGN_20261111.md), a source-grounded design showing why `Quadtree::makeTemplateBasedMesh` must not run in QUAD mode, how the QUAD midpoints differ from the legacy `GetFrontEdges()` segmentation, and how an owned orientation-reversed QUAD frontier must seed only the existing TRI exterior without duplicate area or unsafe `Face` casts. Updated [R1 evidence](evidence/R1_INTERIOR_TEMPLATE_DISPATCH_20261111.json) with exact feature SHA, merge SHA, old failure/fix and honest postmerge 3/4 status, and updated [STATE.md](STATE.md). No local git clone/build/sanitizer proof: local clone failed github.com DNS; all native executable evidence came from actual GitHub-hosted Linux GCC and Windows MSVC CI.

**Next action:** Verify exact postmerge 4/4 including 85 CTest/527 Python and update evidence; then start one R2a research-only PR for independent geometry comparison of the emitted QUAD boundary and existing legacy AFT Quadtree outer front. No global high-valence welding, 1993 centroid approval or production quad_uv admission is assumed.

## 2026-11-11-42 — Exact integrated R1 source fully certified; R2a is next

**Update to session 41 pending gate (no rewriting of previous checkpoint):** The exact merged research-source SHA of [PR #211](https://github.com/tiagosombrra/apmesh-modernization/pull/211) is `254d5f9aadf8cbac5e0f31780b69fb564291d2a5`. Its mandatory [postmerge Actions #43106047878](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43106047878) finished **SUCCESS 4/4**. The actual root job log independently confirms `85/85` CTest, `tooling.controls` passed and `527/527` Python passed (UNIX runner); Linux GCC and Windows MSVC QUAD native separately each passed `14/14` CTest; frozen Eistute/Book TRI scientific equivalence succeeded. The exact feature [Actions #43104622677](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104622677) and independent PR test merge [Actions #43104631590](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104631590) had already passed **4/4**; no gate was weakened to achieve this result.

**Actual persistence:** Updated permanent [R1 evidence](evidence/R1_INTERIOR_TEMPLATE_DISPATCH_20261111.json) to status `R1_RESEARCH_SOURCE_GATE_QUALIFIED_NOT_LIVE_AFT_OR_CLI`, appended the qualified result to [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md), and moved canonical [STATE.md](STATE.md) to active R2a. The R1 deliverable is a bounded experimental *same Quadtree interior template selection and one-owner UV boundary representation*, **not** successful live AFT QUAD publication or a physical mixed-element production CLI run. The default TRI algorithm and frozen modernization main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` remain unchanged.

**First pending work item R2a (not executed in this source-gate closure):** build a read-only geometry comparator between QUAD-derived, per-face source-traced one-owner UV interface edges and `Quadtree::GetFrontEdges()` of the legacy template path from an independently matching refined tree. Validate exact midpoint subdivision, edge coverage, orientations, and deliberate missing/duplicate/invalid negative cases without unsafe pointer publication. Then R2b should explicitly seed the *existing* AFT with a reversed, owned QUAD interface, and R2c should publish a real mixed `SubMesh`. The CLI `quad_uv` remains rejected until its own full-patch validation. Do not imply 1993 centroid approval or global sheet welding.

## 2026-11-11-43 — R2a original AFT front vs QUAD split-front geometry

**Exact source and continuity:** Read canonical `quad-templates=8190e5f000e63e93c2ae8d444229ce93251b84f1` and unchanged modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; no open PR at start. Kept user-goal scope: experimental opt-in **replace TRI interior templates by T1–T6 QUAD in the same real C++ Quadtree**, but leave source Bézier curves, UV patch boundary, default production TRI and original exterior TRI AFT unmodified. All code/comments/docs are research-only English.

**Implemented:** [PR #212](https://github.com/tiagosombrra/apmesh-modernization/pull/212) source SHA `1e26f68c3e82d26382ceef9fbaf97ee0fdeb8fa8`. Added `research/quad/front_interface_audit.{h,cpp}` to copy a **separately built, matching native original Quadtree TRI `GetFrontEdges()`** as value-only directed `UvFrontSegment`, require valid legacy source edge cell/boundary ownership, and audit exact axis-aligned supporting source lines against the R1 QUAD one-owner CCW region boundary with opposite winding for the exterior AFT. Every legacy segment is exactly tiled by one or more QUAD subsegments (including new midpoints), no gap, overlap, longer cross-source QUAD edge, duplicate/foreign/invalid orientation, zero/nonfinite/diagonal edges, invalid face-edge ownership or stale physical pointer usage admitted. Report is a **read-only geometry comparison**, not physical AFT injection.

**Tests:** Added `tests/quad/front_interface_audit_contracts.cpp` with **20 positive/adversarial cases** on two matching actual C++ fixture trees: uniform 16 and refined 42 QUAD from R1 with respectively 16 and 20 directed QUAD boundary pieces. One original legacy tree publishes original TRI template edges; the other stays TRI-unpublished and emits QUAD research values. Includes both explicit experimental interior-point formulas, value snapshot surviving source destruction, ordering invariance and adversarial duplication, omission, wrong winding, nonfinite, nonexistent endpoint, skewed segment and gap cases. `tests/quad/CMakeLists.txt` registers `quad.r2a.front_interface_audit` in Linux GCC and Windows MSVC native suites, with test count now **15**. Recomputed and updated mandatory `docs/architecture/source_inventory.json` build-input SHA from `0554f07f5f6c5803b6b91c49e10fde23c74c664e82c6471eeb153a2ebd0b3712` to `538d5a5329982e871ca54140d815e5eba9bf37f44f6e273c3810388a27cdf2e5`, no oracle relaxation.

**Evidence / merge:** [Exact head push Actions #43130141429](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43130141429) **SUCCESS 4/4** and [PR test-merge #43130207154](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43130207154) **SUCCESS 4/4**, each 15/15 standalone QUAD native CTest on Linux/GCC and Windows/MSVC, full 85/85 CTest, 527/527 Python tooling, unchanged frozen Eistute/Book TRI scientific state. Marked draft ready and merged after both successful gates; verified research `quad-templates` moved to `eabc5201eadfe016c2b9698d43648c9ea7062109`, production `main` unchanged. **Postmerge source [Actions #43131307374](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43131307374) is IN PROGRESS**, not a confirmed 4/4 yet. Updated [evidence/R2A_FRONT_INTERFACE_AUDIT_20261111.json](evidence/R2A_FRONT_INTERFACE_AUDIT_20261111.json) and [STATE.md](STATE.md) to capture the pending gate. No local clone/native sanitizer proof is claimed.

**Remaining limitations / next:** R2a is a bounded comparison over exact dyadic axis-aligned research fixture UV fronts, not yet externally adapted curved-patch boundary ownership, a full AFT-generated QUAD/TRI mesh or application `quad_uv` availability. Confirm exact merged-source 4/4 CI; upon qualification proceed to R2b owned **reversed QUAD front** seeding in the existing triangle AFT without re-running TRI interior templates or duplicating region. Then R2c typed physical `SubMesh`. Historical 1993 numerical rule and high-valence global welding are independent scientific gates.

## 2026-11-11-44 — R2a exact source certificate and R2b1 owned front implementation

**Research branch starting state:** `quad-templates=ccb94e2169ea0dc78d8c06f69db02231961ff380`, protected modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, no open pull requests. Read mandatory continuation, roadmap, state, original AFT, `QuadtreeCell::makeOuterEdges`, `Edge` ownership and `Adapter`/R2 design. **PR #212 R2a exact merged-source CI #43131307374 was independently verified SUCCESS 4/4**, root 85/85 CTest, Python 527/527, native QUAD 15/15 per Linux GCC and Windows MSVC and frozen TRI Eistute/Book parity. Reclassified permanent R2a evidence as fully qualified; earlier pending checkpoint was not rewritten.

**Actual new code:** [Draft PR #213](https://github.com/tiagosombrra/apmesh-modernization/pull/213), research feature `quad/integration-r2b-owned-aft-front-20261111`, exact candidate `eafaeb5bd15abea8effd5fc06994346eb657da0c`, based on research `8097be460c973e0e8db4b08a40b585ba176c7840`. Added `research/quad/owned_aft_front.h` and `.cpp`: source-provenance/leaf and independent R2a geometry comparison; one-owner QUAD UV frontier reversed to feed the **original native `AdvancingFront` protected front**, with actual `Edge/Vertex` objects, exact shared endpoint pointers, same unchanged patch-boundary initial front, mandatory live exterior `QuadtreeCell` observer, `Edge::isInBoundary/isFree`, adjacency and ownership-lifetime correct order. All new objects/list nodes are prepared under RAII before `std::list::splice` into existing AFT owner/observer lists; failure in *validated preflight* leaves AFT state unchanged. The original production AFT, Quadtree, Adapter, source-model curves, CLI and TRI templates were **not modified**. This is engineering-only, not an approved historical scientific formula.

**Native tests and build bookkeeping:** Added `tests/quad/owned_aft_front_contracts.cpp`: 13 positive/adversarial checks on native C++ tree: 16/20 QUAD source split edges, real AFT-owned edge and source cell, per-midpoint canonical pointer identity, manual area/face double publication prohibition, independent experimental midpoint policies, synthetic nonuniform eight-point UV boundary (not an external Bézier patch), wrong orientation, missing halfedge, stale foreign source/depth/count, old-triangle overlap and double selection, retry after invalid preflight. `tests/quad/CMakeLists.txt` registers the new test in both native Linux GCC/Windows MSVC lanes. Recomputed `docs/architecture/source_inventory.json` CMake SHA-256 `2865550a7cc8af00294f793c8dd3c335a81e2225d4ab7e92d0f9db2397c44b8a`, without relaxing the architectural gate.

**Measured to this checkpoint:** [Feature Actions #43137020105](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137020105) and [PR Actions #43137083615](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137083615) each native GCC **16/16** and native MSVC **16/16** CTest PASS (new R2b test executed); frozen source TRI Eistute/Book parity PASS. Each root Linux build/CTest/Python job remained **IN PROGRESS (3/4 jobs completed successfully)** at checkpoint; do not claim 85/85 or 527/527 on this new code until measured. PR #213 remains draft/unmerged. [Permanent measured/pending evidence](evidence/R2B_OWNED_AFT_FRONT_20261111.json). No local compiler, sanitizer or Windows native heap verification was performed in this session; CI evidence is actual hosted native GCC/MSVC.

**NEXT:** Recheck exact-head feature and PR Actions runs for 4/4 and full root 85/85 + 527/527. Correct any failure, then protected merge into `quad-templates` and certify exact merged-source SHA. Begin **R2b2** by calling the existing original AFT geometry/topology algorithm from the research-only seeded front, measuring actual complement TRI faces, zero QUAD/TRI overlay and matching halfedges, then R2c typed physical mixed `SubMesh`. Do not admit user-facing `MESH_ELEMENT_KIND=quad_uv` or claim full Eistute/Book hybrid output yet.

## 2026-11-11-45 — Protected R2b1 PR merge and exact integrated-source gate pending

**Continuation of recorded session 44:** Rechecked same R2b1 feature source `eafaeb5bd15abea8effd5fc06994346eb657da0c`. Independent [push Actions #43137020105](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137020105) and [PR test-merge #43137083615](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137083615) **both completed SUCCESS 4/4**. Native QUAD on GCC/Linux and MSVC/Windows **16/16** tests per platform (new `quad.r2b.owned_aft_front` passed), original Eistute/Book TRI scientific equivalence passed, root **85/85** CTest and **527/527** Python controls each passed, including mandatory architecture inventory.

**Protected integration:** [PR #213](https://github.com/tiagosombrra/apmesh-modernization/pull/213) marked reviewable only after full expected-head gates, checked production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged, merged with `expected_head_sha=eafaeb5bd15abea8effd5fc06994346eb657da0c` into research-only `quad-templates`, merged SHA **`8da5e523531b3579d9bacd69bbfe16ec96efe76d`**. Verified PR merged and actual branch head. No production source files, original TRI faces, point rules, adaptive policy or model inputs were modified.

**Scientific/engineering scope:** This delivery is an **owned and active native AFT front seed**, NOT successful completion of exterior triangles. The research-only derived `OwnedQuadAftFront` binds reversed QUAD face-boundary segments to actual `Edge` and `Vertex` owners in AFT's `innerEdges/innerVertices` with canonical midpoint pointers, exact exterior neighbor `QuadtreeCell` references and failure preflight validation. It preserves the original patch boundary by calling the original AFT initializer only. No `AdvancingFront::makeGeometryBasedMesh` result, physical mixed QUAD/TRI, typed repeated `SubMesh`, CLI acceptance, 1993 formula approval or global manifold welding is claimed. Original AFT smoothing would move seam vertices unless guarded at future R2b2/R2c: protect or skip smoothing for the QUAD seam until validated.

**Postmerge gate:** The exact merged-source [Actions #43138162247](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43138162247) was **IN PROGRESS with 3/4 jobs approved** at this checkpoint: native Linux/Windows QUAD and TRI science accepted; root Linux CTest/Python still building. Updated permanent [R2b1 evidence](evidence/R2B_OWNED_AFT_FRONT_20261111.json) to `R2B1_MERGED_EXACT_POSTMERGE_CI_IN_PROGRESS_NOT_QUALIFIED`, retained source and run URLs; refreshed canonical [STATE.md](STATE.md) with exact SHA and remaining science boundaries. This historical pending observation is not 4/4 qualification.

**Next:** Require 4/4 exact postmerge CI success, then mark R2b1 fully qualified and proceed with a separate isolated R2b2 feature PR running actual original AFT geometry/topology on the owned interface; verify nonzero exterior triangles, correct UV complement area, no overlap, exact shared midpoint identity, all QUAD seam edges matched to opposite TRI winding, rejection/rollback and no smoothing of locked seam vertices. Physical model trials, full mixed `SubMesh` and `quad_uv` CLI remain later work.

## 2026-11-12-46 — R2b1 postmerge certified; R2b2 real exterior AFT and UV overlap draft

**Entry:** Read the live `quad-templates=ed8f02b51b239738b809228a78bdd3f3d6d45f1a`, research continuation instructions, previous session 45 and original AFT source. No open PR at start. Confirmed unchanged production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Rechecked [R2b1 exact postmerge CI #43138162247](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43138162247): SUCCESS all four jobs, GCC+MSVC 16/16 QUAD CTest each, root 85/85 CTest, 527/527 Python and source-frozen Eistute/Book TRI results. Corrected canonical evidence instead of silently overwriting historical pending measurements.

**R2b2 implementation:** Created `quad/integration-r2b2-exterior-aft-20261112` and [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) based on the research branch only. Added one-use research `AttemptExteriorTriangulation`, requiring pre-seeded owned AFT and live original patch-boundary cell observers, invoking actual legacy AFT geometric/topological passes, and reporting triangle count, incident QUAD seam halfedges, closed/rejected front, signed UV area and unchanged seam coordinates. Skip `improveMesh` to prevent smoothing the QUAD seam. Original production AFT/Quadtree/Adapter remain unchanged, no physical mixed result or CLI publication.

**Native failures and fixes:** First feature commit `2d9e3a4` failed Linux GCC compilation on unsupported `const Vertex::getX/getY` usage; corrected in `03a636f`. Native Linux and Windows each passed 16/16 CTests for strict feature predecessor `28ee9b3`, including actual AFT exterior completion assertions. This proves that native original AFT can triangulate the bounded source fixture but not a real Bézier patch or mixed physical model. No evidence was erased or counted as postmerge qualification.

**Independent overlap audit:** Current feature head `319cfc90e34530b220ff55c7e9febc951572e78a` additionally clips convex CCW UV triangles against all QUAD polygons and each other, reports positive-area overlaps separately and includes three adversarial controls: edge-only contact permitted, TRI/TRI positive overlap detected, QUAD/TRI positive overlap detected. Positive overlap threshold is 1e-11 UV square units for the fixed dyadic research fixture (not a validated general physical-model tolerance). Exact feature [Actions #43186301495](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43186301495) and [PR #43186308348](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43186308348) newly requested; no completion assertion at checkpoint. Original 85 root CTest / 527 Python and frozen Eistute/Book checks are pending for this updated SHA. No local native binaries, ASan or external physical Bézier model tested.

**Closure audit:** Code confined to three research/test files; 19 authored tests expected in one existing CTest; original source/production semantics and model inputs unchanged; source-inventory CMake hash unchanged; original triangle regression preserved. Known open gaps: independent full patch containment and actual Bézier UV/XYZ mapping; acceptance/rollback after partial AFT; owner lifetimes under failures, numerical tolerance under non-dyadic meshes, iterative mixed output. PR #214 stays draft/unmerged; `quad_uv` remains rejected. Check exact feature CI, measure overlap and update evidence before any reviewable merge.
## 2026-11-12-47 — Refined AFT test exposed misleading seam metric; corrected fail-closed

**Reproduction:** Added actual R2b2 exterior AFT on (a) refined Quadtree with 20 split QUAD seam halfedges and (b) synthetic nonuniform eight-point UV patch boundary, retaining 16 regular QUAD seam halfedges. Source `6e6bf67c086a5689f8b54cd5a87b93936d6e3eac` failed native Linux [Actions #43186741954](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43186741954) as intended by the strengthened oracle: native refined exterior TRI emitted 24 triangles, UV TRI area 0.75, zero overlap but reported 44 seam face incidences despite only 20 original QUAD seam edges. The already accepted regular fixture had reported 36 seam face incidences, although it also had 16 source seam edges. This was a measurement bug, not proof that all original QUAD seam edges were matched.

**Root cause and code fix:** Existing `OwnedSeamEdges()` exposed the AFT `innerEdges` list. When original `makeGeometryBasedMesh` / `makeTopologyBasedMesh` runs, it appends new *TRI* edges to that owner list. Both the seam counter and its denominator accidentally included those new edges, so earlier strict regular runs could report a misleading success. Feature `2e88fc164d87e5ad10d3205dad845bbac9fd30bd` independently stages and retains owner-borrowed `std::vector<Edge*>` and `std::vector<Vertex*>` references to the 16 or 20 original QUAD seam objects during `Seed`, before AFT mutable owner lists can grow. The research getter now returns these stable seam-only views, and native R2b2 counts only original seam edges with exactly one correct reversed TRI oriented incidence. Original source AFT and TRI defaults not changed; no assertion weakened.

**Tests and status:** 21 authored native controls across original source ownership, invalid/retry, strict exterior AFT area/closure/seam, synthetic overlap and refined/nonuniform UV contour. Native Ubuntu GCC [Actions #43187098299](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43187098299) **passed all 16/16 standalone QUAD CTests**, including the extended R2b test. PR-native Ubuntu [Actions #43187106039](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43187106039) also passed 16/16. Exact Windows MSVC, root 85 CTest, 527 Python and frozen Eistute/Book tests still running at time of this recorded checkpoint, **not certified as 4/4**. Draft PR #214 remains blocked until complete checks. No local execution, physical Bézier patch or typed mixed SubMesh tested.

**Next:** Review exact feature/PR all-four-job status and fix any real failure, without modifying original TRI science. Then extend scientific R2b2 to the real curve-boundary and failed partial-AFT paths, after which R2c physical mixed elements can be attempted.

## 2026-11-12-48 — R2b2 exact 4/4 UV certification and real Bézier source/partial-failure trial

**Qualified predecessor:** Confirmed source `2e88fc164d87e5ad10d3205dad845bbac9fd30bd` feature CI #43187098299 and PR #43187106039 both SUCCESS 4/4, actual 85/85 root CTest / 527/527 Python, native Linux GCC 16/16 and Windows MSVC 16/16 research CTest, frozen Eistute/Book original TRI parity. This qualifies the bounded source-native QUAD-front/exterior-AFT UV seam/area/overlap checks; it does not qualify physical XYZ or application mode.

**New implementation:** Feature commit `7146aa44834d0820789303c4a2f840201209aa2b` added `tests/quad/r2b2_bezier_aft_probe.cpp` and root CMake `quad.r2b2.real_bezier_aft` registration, with source-inventory SHA-256 updated correctly. Actual `Models3d::ModelCurvaBezier` and `PatchReader` Eistute/Book `PatchBezier` supply source curves, XYZ and differentials for native `OwnedQuadAftFront` UV QUAD/TRI output. Physical candidate checks signed Jacobian, facet orientation, original control curves and unchanged accepted source mesh pointer. The fixed experimental UV contour has 16 sites and is not original Adapter curve adaptation; whole-model/physical SubMesh publication remain blocked. A per-patch rejection is explicitly diagnostic and not whole-model acceptance.

**Actual failure:** Both feature CI #43189110700 and independent PR CI #43189121270 failed root Linux source build due invalid C++17 `FaceUv` temporary list initialization at source line 234, even while native isolated 16/16 and frozen TRI lanes completed. Preserved original error; not misclassified as model failure. New exact feature `c103c77d5c390873760744912533ecaf7dd5a2a9` repairs this using an explicitly typed `FaceUv` value.

**Fault path:** The same new revision adds `OwnedQuadAftFront::SetResearchAbortAfterTriangles` and a test-only virtual `findBestVertex` injection after at least one generated exterior TRI face. Negative control requires partial TRI creation, catchable failure, rejected same-owner retry and safe retirement of whole AFT owner while the value-owned QUAD source remains unchanged. No production `AdvancingFront` or published `SubMesh` code changes. Original TRI regression cannot be inferred from new source before exact CI.

**Checkpoint:** [Draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) source `c103c77d...`, [exact feature CI #43189723674](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43189723674) in progress; independent PR run pending discovery. No physical model or source-native CTest acceptance is asserted for this head. Main remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

**Next:** Verify complete current Linux/MSVC/source-Bezier/fault CI, repair demonstrated scientific/compiler faults; then bridge actual Adapter curve sampling and typed mixed publication R2c separately, without unqualified `quad_uv` CLI.
## 2026-11-12-49 — Source-aligned real Bézier R2b2 and controlled partial-AFT failure, exact premerge passes

**Entry and exact source:** R2b2 feature `c103c77d5c390873760744912533ecaf7dd5a2a9` in [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), `quad-templates=0fe832a008df5ee06c4793e4510da14ba495a1f0` at entry, unchanged modernization main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Previous R2b2 UV-only `2e88fc1` already passed both exact 4/4 CIs.

**Certified current gates:** [Feature CI #43189723674](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43189723674) and [independent PR CI #43189733267](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43189733267) both completed **SUCCESS 4/4**. Linux GCC/Windows MSVC isolated native QUAD **16/16** per runner; root Linux **86/86 CTest** (including newly added `quad.r2b2.real_bezier_aft` at #68), tooling **527/527 Python**, frozen Eistute/Book original TRI equivalence **PASS**. Actual root logs were inspected, not inferred from job status alone. The initial invalid C++17 temporary test source `7146aa4` failed two root builds; corrected and requalified without gate relaxation.

**Physical-source witness:** Native `tests/quad/r2b2_bezier_aft_probe.cpp` executes original research-selected real C++ Quadtree T1–T6 QUAD and original exterior AFT native TRI. Directly maps its UV vertices/faces through production `Models3d::ModelCurvaBezier` and `PatchReader` source `PatchBezier` for Eistute four and Book twenty-eight patch candidates. Checks original four `CurveAdaptiveParametric` curve geometries at oriented parameter samples, `Parameterize`, `Qu/Qv`, nonzero differential magnitude, local positive XYZ triangle orientation, full exact UV complement, shared seams and independent positive-area overlap exclusion. Calls reject invalid UV and preserve the previously accepted source `SubMesh` pointer. **Actual source mapping gate is existential per external model**: at least one admitted patch in Eistute and Book, not total model acceptance. Accepted/rejected counts are printed by the passing executable but not captured in the ordinary CTest summary/artifact; report detailed counts as **unknown** rather than claiming all 32. Physical source evaluation is not publication of physical mixed elements.

**Fault evidence:** A research-only `findBestVertex` override injects a deterministic exception after at least one original AFT exterior TRI, with 22 authored native test cases including that partial-owner destruction/rejected retry path. No production `src/` or original AFT code changed; source-value QUAD selection survives rejection. No complete-process sanitizer or full memory leak qualification claimed.

**Open admission gate:** The native patch boundary source is a fixed experimental 16-segment UV chart, not an exact snapshot of the original `Adapter::AdaptCurve` sample/curve synchronization per attempt. Before research PR merge and R2c, capture actual Adapter boundary ordering/samples and revalidate exact matching native AFT front and physical curve owners, quantify per-patch rejected cases and original accepted mesh safety under late failure. Production CLI `quad_uv` remains deliberately blocked; historic 1993 numerical point formula is not approved.
## 2026-11-12-50 — Real serial Adapter curved-source boundary capture: initial failures and strict repair

**Work item:** Continue R2b2 original `Adapter::AdaptDomain` and `CurveAdaptiveParametric` sample continuity as mandated by session 49; never enable QUAD in the production CLI or replace accepted TRI behavior.

**Implementation:** On feature `quad/integration-r2b2-exterior-aft-20261112`, initial `7797b8b2aa8d1236400f3b8e7ace1dc4b982a4c0` extends the existing opt-in research `CaptureHooks` with `boundary_sink` and immutable `AdapterBoundaryCapture` containing actual original source sample indices, live model curve IDs/parameters/orientations, physical `NodeAdaptive` IDs and XYZ and the AFT boundary vertex IDs and oriented UV edges. A single opt-in synchronous callback is made after source boundary closure and before the original Quadtree generates/refines. Real `GeneratorAdaptive` Eistute/Book test compares this contour against the untouched actual refined Quadtree boundary. Original `src/adapter` defaults are byte-semantically gated when research hooks absent. Root original single-patch Adapter test adds a pre-tree negative observer fault.

**Observed strict failures:** On `7797b8b2`, actual [PR CI #43195490660](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43195490660) native Linux/Windows QUAD and frozen scientific TRI passed, but root **FAILED 3/86**. Strict architecture tooling correctly rejected stale `src/adapter/adapter.cpp` SHA. The original `quad.adapter.real_patch_capture` ran three old scenarios and segfaulted while starting a fourth `BuildInitialSubMesh` scenario; the current origin of that memory fault is **not proved**. The real Eistute `GeneratorAdaptive` had legitimate repeated logical attempt identity and the new map's uniqueness check threw `Original Adapter repeated the same boundary attempt identity`; Book did not fail that check. This demonstrated that patch/retry tuple alone is not an unambiguous per-callback identity. Preserve both negative findings.

**Fix and limits:** `5daf959b2ce4386b500b6f5f801c97e8cdfcde42` updates source inventory to the actual new Adapter SHA and tries adding verbose R2b2 source model admission output, but accidentally malformed the YAML using JavaScript replacement `$'` expansion; [CI #43196178948](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43196178948) failed before jobs. `7dcb67d8fd125ac38bdb1a5066ca2c339b6bc860` restored valid bounded workflow and a 14-day artifact. Latest `3330e0ed9dfa771ad2c38813697ba7b0fa7b83c7` replaces uniqueness with **strict synchronous callback ordering**, retains occurrence counts for reused keys, and isolates the pre-tree fault into the separate `quad.adapter.real_boundary_abort` CTest process (keeps old three-case process intact). Root CMake test registration and build SHA-256 inventory updated. This test separation is NOT evidence that the prior fourth-run segfault memory cause was eliminated.

**Exact new candidate:** feature `3330e0ed`; root 87/87, native Linux/Windows QUAD 16/16, tooling Python 527/527, Eistute/Book TRI frozen scientific equivalence, per-model `R2B2_SOURCE_MODEL mapped/rejected` are required before qualification. **CI not confirmed at entry of this checkpoint; no merges authorized.**

**Next:** Verify current push and PR exact-head gates and inspect actual model counts. Investigate any new failures without scientific gate relaxation. Then run independent real original Adapter contours through owned AFT with matching source leaf/refinement before research-only PR merge review. No `SubMesh` QUAD publication, repeated mixed adaptation or CLI `quad_uv` today.
## 2026-11-12-51 — Pre-tree negative fixture empty snapshot crash identified and repaired, strict CI pending

**Current source:** Draft R2b2 [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) feature `8b0a774f463ce450aedeee216d978965428ef481`. Original production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Exact regression evidence:** Predecessor `3330e0ed9dfa771ad2c38813697ba7b0fa7b83c7`, [feature CI #43197069224](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43197069224) and [PR CI #43197078482](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43197078482): native Linux GCC 16/16 and Windows MSVC 16/16, frozen original Eistute/Book TRI source parity, source architecture inventory/tooling, single-patch original Adapter capture, Eistute/Book live real Generator outcomes, real R2b2 Bézier source all **PASS**. Root **86 of 87 CTest passed**; exact negative root test `quad.adapter.real_boundary_abort` failed SIGSEGV. Root stdout confirmed the intentional callback was caught and no refined tree was built; C++ fixture unconditionally accessed `snapshots.front()` immediately after despite `snapshots.empty()` being its required negative case. No failed production meshing or algorithmic R2b2 seam is implied by this empty test oracle.

**Repair:** Source `8b0a774f463ce450aedeee216d978965428ef481` guards the first-refined-UV snapshot access and requires the observed zero-snapshot condition **only** for pre-tree exception; no modified production source, scientific formula, QUAD seam, acceptance or CMake inventory. This is a real negative-oracle fix and is not a waiver of its failure criteria. A distinct fourth-consecutive-fixture SIGSEGV from the first `7797b8b2` candidate happened earlier than this negative oracle dereference and remains unresolved as repeated-run lifetime risk; only dedicated ASan/UBSan or equivalent investigation can qualify it.

**Exact current CI:** [feature push #43198429209](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198429209) and [PR #43198438695](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198438695) native Linux QUAD 16/16 and Windows QUAD 16/16 PASS, frozen original TRI equivalence PASS; root 87/87, Python 527/527 and physical external source mapped/rejected counts still pending at checkpoint. No 4/4 or research merge claimed.

**Next:** Verify exact current source checks and actual source model results, update permanent evidence. Then implement source-compatible actual native refined Quadtree reconstruction and owned AFT using original per-attempt Adapter curved boundary IDs/parameters; qualify physical seams and late rollback separately before R2c.
## 2026-11-12-52 — Original Adapter contour instrumentation exact 4/4; 32/32 source Bézier patches mapped with fixed research perimeter

**Exact candidate:** `8b0a774f463ce450aedeee216d978965428ef481` on draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), `quad-templates=ce186672a3e0de29de947e9a78c23c23d44bbe26` at entry, independent modernization `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Actual exact tests:** [Feature push #43198429209](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198429209) and independent [PR test-merge #43198438695](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198438695) **SUCCESS 4/4 each**, not an inferred success: native Linux QUAD GCC **16/16** and Windows MSVC **16/16**; root Linux **87/87** CTest (prior original single patch capture, new isolated pre-tree abort, bounded Bézier native original AFT, actual Eistute & Book GeneratorAdaptive tests all PASSED), tooling **527/527** Python; frozen original TRI science parity Eistute/Book passed. Source-inventory SHA gate passed, no skipped science failures.

**Physical bounded source logs, both CIs:** `R2B2_SOURCE_MODEL patches=4 mapped=4 rejected=0` Eistute, `R2B2_SOURCE_MODEL patches=28 mapped=28 rejected=0` Book; native built-in curved Bézier `builtin_mapped=1`. New read-only workflow step retained `quad_r2b2_source_admission.log` as a 14-day artifact; source calls original `PatchReader/PatchBezier` for **every** source model chart, original exterior AFT and native QUAD T1–T6 fixed research 16-segment contour, checks per-chart UV seam/nonoverlap, signed area and 3D differential orientation. It is **not** the actual `Adapter::AdaptCurve` discretization nor full model-wide physical mixed connectivity/ownership, so do NOT claim global Eistute or Book hybrid mesh is generated.

**Real source Adapter boundary result:** Before original TRI refinement, the opt-in read-only observer captures actual serial four-curve source sample `CurveAdaptiveParametric` parameters, source point IDs, node XYZ, side reversal, exact directed Boundary UV segments and AFT vertex IDs. Original `GeneratorAdaptive` tests on Eistute/Book compared original refined Quadtree boundary IDs/UV count and ordered callbacks. Repeated logical patch/retry keys were observed and tracked by callback ordinal; failure after source boundary closure but before refinement passed separate native negative CTest and left prior accepted `SubMesh` bound. No physical QUAD publication occurred in the Adapter.

**Failure/corrective evidence:** First candidate `7797b8b2` root failed 3/86 (architecture inventory, false repeat-key uniqueness, and a fourth-consecutive native fixture segfault during coarse initialization). Architecture SHA and chronology fixed; fourth-in-process lifetime risk still **open**, not dismissed by isolating the new abort in a separate process. Source `3330e0ed` root 86/87 failed solely because the new pre-tree abort fixture dereferenced empty `snapshots.front()`, independent of the original earlier fourth-in-process crash. `8b0a774f` guards this and makes zero observations an explicit valid required negative, **both exact CIs now 87/87**; no rejection threshold loosened or scientific code changed in that repair.

**Remaining before R2c:** Still must connect the actual `Adapter::AdaptCurve` sample contour to source-matching owned Quadtree T1–T6 original AFT **within the same attempt**, preserve candidate rollback and late failure semantics, independently qualify repeated-in-process memory under sanitizer, publish typed mixed physical `SubMesh` only after full source physical ownership/continuity. PR #214 remains draft/unmerged, main and `MESH_ELEMENT_KIND=quad_uv` unchanged.
## 2026-11-12-53 — R2b2 first owned native replay from actual original serial Adapter, strict CI pending

**Work item:** Connect R2b2 selected QUAD T1–T6 and original AFT exterior to original Adaptive Curve-generated source tree instead of fixed synthetic test-only boundaries, without mutating in-flight TRI or existing accepted `SubMesh`.

**Feature code committed:** `8f48280b288f7c74ff222b04d0fa86851324338d` adds `research/quad/source_tree_replay.{h,cpp}` (standalone owned native exact topology and chart contour reconstruction, point IDs, source cell-box/depth/neighbor geometry verification, source bad UV negative rejection), extends `quad.adapter.real_patch_capture` to create independent legacy TRI-template source clone and QUAD/AFT candidate clone from actual `Adapter::AdaptDomain` source after real refinement and to require positive area, orientation, no spatial overlap, original TRI tree unchanged. Adds new target sources only to existing root CTest research binary; strict CMake SHA architecture inventory updated. This first original Adapter witness still uses the existing single-patch 4-vertex square (not nonuniform Eistute/Book) and an experiment-only arithmetic midpoint for cloned curve-less edges. It does not capture live parametric edge midpoint and normalized edge length, and does not publish mixed `SubMesh`.

**Verified failure:** `8f48280b` root [independent PR CI #43202178454](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43202178454) failed **compilation** in `source_tree_replay.cpp` on `const Boundary*` call to original non-const legacy getters `getBoundary/getEdges`. No application CTest was executed in that failed root job. Linux/Windows QUAD natively passed; no default TRI source changed. Feature `458cbea21e8330e23cdd5b3ca9c89f38d0c1d20d` changed `const auto* boundary` to `auto* boundary` solely in research clone validation.

**Current required execution:** [feature CI #43202602922](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43202602922) and [PR CI #43202612264](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43202612264) passed Linux GCC native QUAD and Windows MSVC native QUAD and independent frozen Eistute/Book TRI parity. Root 87 CTest and Python 527 controls **not yet verified** at this entry; any source replication/AFT science failure blocks stage closure. The separate model-wide real dynamic-boundary probe has been prepared as a later test, **not pushed or certified**; do not count it.

**Open scientific/lifetime gap:** Clone reconstructs exact chart sites, topology and neighbors but lacks original source edge `makeParamMid` curved midpoint/arc-length metadata. For arbitrary Bézier-adapted parametric boundaries source-edge `getCell()` based on curved midpoint can diverge from geometric midpoint; must measure and engineer a pointer-free transfer before claiming exact curved AFT. Earlier repeated fourth-in-process fixture crash remains unresolved under sanitizer. R2c physical QUAD/TRI remains blocked.

**Next:** Inspect exact current CI root and fix any positive/negative test failures, then run strict Eistute/Book dynamic-source replicas on actual observed Quadtree. Retain PR #214 draft/unmerged and untouched `main`.

## 2026-11-12-54 — Real original Adapter parametric edge and Eistute/Book Quadtree replay qualified, AFT physical completion not yet tested

**Source:** `76250559951b5ac0e45982d0c86606d001feb53a` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), research only. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. Previous single-patch replay source `458cbea21e8330e23cdd5b3ca9c89f38d0c1d20d` separately qualified by feature #43202602922 and PR #43202612264 (both 4/4; root 87/87, Python 527/527).

**Exact new implementation:** Captures the native `Edge::makeParamMid()` cached source UV midpoint and normalized curve arc length into the research-only `AdapterBoundaryCapture::original_edge_metrics` before `Quadtree::generate` consumes/resets the edge length. The owned independent research `ReplayNativeSourceTree` validates the native source midpoint against its original owner, copies cached midpoint into the cloned edge by value, adjusts the clone's current post-generation length to match the source, assigns its cell and checks **exact dyadic leaf geometry, depth, all 2:1 neighbor boxes and per-source-edge cell box equality**. No original curve pointer or mesh owner borrowed across callback. `quad_generator_outcome_probe` now invokes one bounded native replay on an actual original `GeneratorAdaptive` multi-site adapted chart per **Eistute** and **Book**, demands a correct dynamic leaf/edge count, deliberate corrupted directed boundary rejection and unchanged uncommitted TRI template ownership. CMake research-only generator probe is linked to the new replay source and strict SHA256 `docs/architecture/source_inventory.json` updated.

**Exact gate evidence:** [Feature push #43204053789](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43204053789) and [PR test-merge #43204061864](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43204061864) both **COMPLETED SUCCESS 4/4** on source `76250559951b5ac0e45982d0c86606d001feb53a`. Native Linux GCC QUAD **16/16**; native Windows MSVC QUAD **16/16**; root Linux CTest **87/87** including `quad.adapter.real_patch_capture`, `quad.adapter.real_boundary_abort`, Eistute/Book real `quad.generator.real_global_outcomes` and `quad.r2b2.real_bezier_aft`; Python tooling **527/527**; frozen scientific Eistute/Book TRI equivalence **PASS**. Verified directly from both CI root job logs. Previous Bezier fixed-contour R2b2 source-patch trial remains Eistute **4/4**, Book **28/28**, plus built-in curved **1/1** with zero rejections, but that result is not full-model QUAD/TRI completion.

**Admissibility limits:** Real dynamic source replay **one chart per external model**, no actual newly adapted QUAD exterior AFT executed for those source charts yet. No claim all curve attempts were reconstructed or a complete mixed Bézier mesh was physically published. Original fourth-consecutive single-process test crash remains an open sanitizer/lifetime gate; no ASan/UBSan performed. No default TRI, historical 1993 centroid/point rule, original smoothing/acceptance policies or `quad_uv` CLI changed. PR #214 remains **draft/unmerged**.

**Next:** Add a strictly bounded real-model `GeneratorAdaptive` source-native owned AFT experiment using the now-replayed original curve midpoint and cell topology, report true TRI exterior closure/nonoverlap/positive physical source area and accepted/rejected chart counts without weakening failure gates. Independently run native sanitizers for the legacy repeated-in-process lifetime concern. Only then review research PR merge and physical typed R2c admission.

## 2026-11-12-55 — First original exterior AFT over dynamic external Adapter contours (explicit classified diagnostic, CI pending)

**Intent:** After source-exact owned Quadtree and original Bézier edge midpoint replay is qualified on Eistute and Book (predecessor `7625055`, both 4/4), execute the real native original exterior AFT on the **same actual dynamically adapted source geometry** to learn precisely whether model-driven template selection, seam/area and source AFT completion can be admitted.

**Changed feature source:** `1f2da57ff4dc4dd6dde358ede0efd772da3fb3ba` in [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) adds bounded original AFT diagnostic to `tests/quad/generator_outcome_probe.cpp`: independently reconstructs two source-owned trees from the first nontrivial adapted chart of each Eistute/Book model; obtains actual native TRI template front on one clone; selects research T1–T6 QUAD on the other clone; calls `OwnedQuadAftFront::Seed` and original `AttemptExteriorTriangulation`; records `dynamic_source_aft_attempted`, `dynamic_source_aft_admitted`, `dynamic_source_aft_quad_faces`, `dynamic_source_aft_exterior_triangles`, `dynamic_source_aft_rejection`. Accepted candidate requires full front drain, original seam incidence, signed area, positive triangles, no spatial overlap. Rejected candidate catches reason and destroys its owned partial state; no re-use or `SubMesh` publication. Root research-only generator probe now includes existing QUAD research implementation object files with updated CMake SHA architecture inventory. Workflow repeats verbose mandatory Eistute/Book real generator CTests and keeps bounded 14-day evidence log.

**Scientific interpretation:** This is a **diagnostic**, not an automatic success gate for the original AFT: CTest regression can pass even when the observed original source-AFT candidate is rejected (record `admitted=0`). Only `admitted=1` together with strict UV invariants establishes bounded source-clone AFT viability; even that does not establish physical mixed QUAD/TRI XYZ or a global Eistute/Book mesh. Historical 1993 point policy and production `quad_uv` still blocked.

**Exact running gates:** [feature CI #43206236696](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206236696), [PR CI #43206246419](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206246419) on `1f2da57ff4dc4dd6dde358ede0efd772da3fb3ba`: native Linux/Windows 16/16 QUAD **passed**, root CTest 87, Python 527, frozen TRI science, and explicit new per-model AFT admission/rejection still pending at this checkpoint. No source code merge and no CLI/production change.

**Next:** Inspect exact latest CI and actual source-AFT output for both models; record all negative findings, resolve real topology/numerics without changing gates; independently address original repeated in-process fixture lifetime with sanitizer. Only after source-owned physical integration and rollback review may research merge/R2c proceed.

## 2026-11-12-56 — First true dynamically adapted original AFT exterior admitted for Eistute and Book, exact 4/4 on two pipelines

**Feature/source:** `1f2da57ff4dc4dd6dde358ede0efd772da3fb3ba` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Exact CI receipt:** [Feature push #43206236696](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206236696) and [PR merge-test #43206246419](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206246419) both **COMPLETED SUCCESS 4/4** on exact feature head; Linux GCC native QUAD **16/16**, Windows MSVC native QUAD **16/16**, Linux root CTest **87/87** (native single-patch and original Eistute/Book model GeneratorAdaptive tests included), tooling **527/527 Python**, frozen scientific original Eistute/Book TRI equivalence **PASS**. Verbose re-execution of both real model CTests recorded in a 14-day `quad_dynamic_source_aft.log` workflow artifact, and exact positive markers were read from BOTH root job logs. Do not infer scientific admission solely from root exit status.

**Measured true dynamic source QUAD/AFT results:**
- Eistute source original curve contour `original_adapted_boundary_sites=40`, `original_source_leaves_replayed=130`, `dynamic_source_aft_attempted=1 dynamic_source_aft_admitted=1 dynamic_source_aft_quad_faces=472 dynamic_source_aft_exterior_triangles=152 dynamic_source_aft_rejection=none`.
- Book original curve contour **36 source boundary sites**, **64 replayed leaves**, `dynamic_source_aft_attempted=1 dynamic_source_aft_admitted=1 dynamic_source_aft_quad_faces=188 dynamic_source_aft_exterior_triangles=100 dynamic_source_aft_rejection=none`.
- On both, original native `AdvancingFront` was actually invoked on two independent per-attempt source-exact cloned trees (TRI template reference and QUAD T1–T6 selection), original curved edge midpoint and source-cell owners reconstructed as values. Admission requires original exterior front completely drained, positive nondegenerate UV TRI, exact original QUAD seam incidence/opposite winding, untouched seam vertices, complete signed area balance and no pairwise positive-area TRI/TRI or QUAD/TRI overlaps. No partial/invalid candidate was counted as accepted. Original live `Quadtree` remains TRI-owned and unchanged.

**Limits and next:** This is **one dynamically adapted per-patch UV chart per external model**, not accepted full Eistute/Book hybrid output. The 4/4 and 28/28 earlier `PatchBezier` source physical experiments use a different *fixed* 16-site chart; physical XYZ/Jacobian and shared-curve endpoints of the **new true dynamic AFT faces remain unverified**. The experimental numeric vertex-mean point is not 1993 formula approval. Typed physical QUAD/TRI `SubMesh`, model-wide shared sheet continuity, repeated adaptation and production CLI remain blocked. Historical fourth-in-process fixture SIGSEGV has not had independent ASan/UBSan. PR #214 stays draft/unmerged; no postmerge claims.

**Next implementation:** Build native 3D `PatchBezier` face mapping of the current true adapted source AFT TRI/QUAD output with original curve-node XYZ and UV seam correspondence; require face orientation/finite area and exact rollback/ownership and model boundary stitching. Run sanitizer for repeated fixture memory concern in separate gated research work, then review scientific merge.
## 2026-11-12-57 — True original adapted AFT faces physically re-evaluated in independent PatchBezier, first compiler defect and repaired exact head pending

**Implementation:** Following the exact UV-native AFT positive evidence for one real Eistute chart (40 actual source sites, 130 leaves, 472 selected QUAD and 152 original exterior TRI) and one Book chart (36 sites, 64 leaves, 188 QUAD and 100 TRI) on `1f2da57ff4dc4dd6dde358ede0efd772da3fb3ba`, new opt-in **research only** `research/quad/dynamic_physical_audit.h` and `tests/quad/generator_outcome_probe.cpp` capture every actual accepted QUAD/TRI UV face from the research-owned AFT before its owner goes out of scope, alongside the native original Adapter source node XYZ, original curve parameters, reversal and patch index. After the real original TRI generator finishes, a separately owned original BP model `PatchReader` and `PatchBezier` re-evaluate each actual curve node against both `Parameterize` and `CurveAdaptiveParametric::FindPointByParameter`; all QUAD facets (two triangles each) and native exterior TRI use real `Qu × Qv` differential Jacobian/normal and positive signed facet area. Required rejection controls: modified original node XYZ, inverted TRI winding, UV outside chart; no candidate physical mesh publication.

**Predecessor exact failed gates:** `3adfff01d970e03368ebba5d0215214f9897bd86` [feature #43245604544](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43245604544) + [PR #43245617085](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43245617085) both root CTest/tooling jobs **FAILED C++ compile** before running physical audit, from ambiguous `std::vector<std::array<UvVertex, 3>>::push_back({ ... })` braced construction and a guard referring to `dynamic_physical_attempted` before declaration. Native standalone Linux/Windows QUAD and frozen original Eistute/Book TRI equivalence passed; no underlying geometry scientific gate ran. These failure states are preserved, not erased.

**Repair:** `24349b74befb2308bb3d6202f747998def5eedd3` replaces ambiguous initializer with explicit `PhysicalTriangleUv{UvVertex{..}, ..}` and moves the guard after physical audit declaration. No science condition/tolerance or production source modified. New [feature CI #43246304785](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246304785) and independent [PR CI #43246317558](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246317558) have native GCC/MSVC QUAD completed success; root 87 CTest, Python 527, frozen source TRI and the actual per-model `dynamic_physical_admitted` plus rejection/negative markers **pending** as of checkpoint. Root job green does **NOT** by itself qualify positive physical geometry if diagnostic marker says rejected.

**Next:** Qualify exact feature/PR gate and physical Eistute/Book metrics; if physical mismatches are detected, keep explicit rejection, investigate node/curve/source mapping rather than weakening acceptance. Then global shared-curve continuity, physical typed mixed QUAD/TRI `SubMesh` transaction/rollback, repeated adaptation and independent historical 4th-in-process sanitizer. Keep PR #214 draft, main and CLI unchanged.
## 2026-11-12-58 — Native original AFT dynamically adapted Eistute/Book physical XYZ/Jacobian exact 4/4 double-qualified

**Exact source:** `24349b74befb2308bb3d6202f747998def5eedd3`, [research PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) DRAFT/UNMERGED; `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. Source paths added `research/quad/dynamic_physical_audit.h` and extended `tests/quad/generator_outcome_probe.cpp`; no production source files, numerical policy, CMake, baseline reference or architecture hashes modified.

**Implemented observable original source physical audit:** The actual accepted AFT TRI and T1–T6 interior QUAD from the original adapted source chart per model are frozen as UV-by-value lists while their native research owners are live; original source Adapter sampled node XYZ/curve IDs/oriented parameters and patch index remain as values. AFTER original `GeneratorAdaptive::Execute` and TRI accepted/restored traces, load the independent real BP model using original `PatchReader`. For the same patch index compare EVERY original `CurveAdaptiveParametric` node XYZ with independent `PatchBezier::Parameterize` and original `FindPointByParameter` using side reversal and the pre-existing physical curve relative tolerance `2e-7*max(1, ||XYZ||)`. Split each QUAD into two test-only physical triangular facets, verify all real exterior TRI through original `Qu/Qv` finite nondegenerate Jacobian and strictly positive physical normal alignment/area, and maintain source/independent `SubMesh` pointer unchanged. Three independent adversarial checks must reject corrupted source node XYZ, reversed TRI face winding and invalid UV without publication. Physical `dynamic_physical_admitted` is separate from UV `dynamic_source_aft_admitted` and CTest return code.

**Exact failure & correction:** `3adfff01d970e03368ebba5d0215214f9897bd86` [push CI #43245604544](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43245604544) + [PR CI #43245617085](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43245617085) both root job FAILED during C++ compile, before scientific physical execution: ambiguous implicit nested `std::array<UvVertex,3>` initializer and guard reading `dynamic_physical_attempted` before its declaration. Standalone native Linux+Windows QUAD and frozen TRI passed. `24349b74befb2308bb3d6202f747998def5eedd3` explicitly initializes `PhysicalTriangleUv` and places guard after actual audit, preserving every physical threshold and old controls.

**Actual positive double CI:** [Feature #43246304785](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246304785) and [PR #43246317558](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246317558) each **COMPLETED SUCCESS 4/4** at exact feature source, with Linux GCC native QUAD 16/16, Windows MSVC native QUAD 16/16, root Linux **87/87 CTest**, Python **527/527**, frozen original Eistute+Book TRI science equivalence PASS. Examined BOTH verbose root logs, each independently reported:
- Eistute first real dynamically adapted patch: original source 40 boundary nodes, 130 leaves; 472 QUAD + 152 original AFT exterior TRI; `dynamic_physical_attempted=1 admitted=1 source_nodes=40 facets=1096 min_alignment=0.760759 max_source_error=8.97016e-15 negative_controls=1 rejection=none`; all 3 negative controls tested and rejected.
- Book first real dynamically adapted patch: 36 nodes, 64 leaves; 188 QUAD + 100 original AFT TRI; `dynamic_physical_attempted=1 admitted=1 source_nodes=36 facets=476 min_alignment=0.999823 max_source_error=2.48253e-16 negative_controls=1 rejection=none`. Original AFT source UV also `admitted=1 rejection=none` in both.

**Closure boundaries:** This is one experimental physical patch per model with complete within-patch UV seam and differential XYZ checks, not an actual committed `SubMesh` four-node QUAD/TRI mesh and not an all-model Eistute/Book hybrid. Prior 4/4+28/28 fixed 16-site source physical mapping is a DISTINCT experiment. Shared real curve interfaces between different actual dynamically adapted patches and sheets, global manifold conformity, physical candidate commit/rollback, repeated adaptivity and the historical 1993 interior point rule remain unqualified. The original fourth-consecutive-in-process native fixture SIGSEGV remains without ASan/UBSan, not silently marked fixed. No merge authorized.

**Next:** measure true model-wide shared boundary curve sample topology and orientation/XYZ incidence across Eistute (all 4) and Book (all 28), with negative mismatch detection and accepted/rejected explicit counts, before physical typed R2c `SubMesh` transaction and global model closure. Maintain `main` and CLI `quad_uv` unchanged.
## 2026-11-12-59 — Cross-patch original shared curve topology and coherent Adapter epoch source audit, native CI ongoing

**Feature:** `017d3f6c9cf85e5f13482b62719a884a048140f6` in [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214). Last fully certified `24349b74befb2308bb3d6202f747998def5eedd3`: physical one original dynamically adapted Eistute chart and one Book chart source and original AFT accepted with 1096/476 positive facets, all three source-XYZ/UV/winding negatives, both exact CI 4/4.

**Change:** `research/quad/shared_curve_audit.h` builds the FULL original PatchReader Eistute/Book model patch/curve incidence graph by original CURVE POINTER within independently owned model, enumerates exterior/shared and high-valence sheet junction curves, and snapshots the actual original Adapter side records by value including the conventionally omitted final endpoint from the next native boundary vertex. Per comparison, original source parameter, sample index, node ID, curve ID consistency, XYZ and opposite directed boundary traversal must agree. Source captures are restricted to one truly coherent outer (session, epoch, global_retry) to prevent false mixing of original adaptive attempts; repeated local attempts and omitted patches are measured and cannot count as global success. Separate controls invalidate actual original copied source XYZ, node ID, sample count and orientation; existing optional observability does not change TRI. New `R2B2_SHARED_CURVE_MODEL` verbose outputs preserve matched/rejected/unobserved counts and reasons including high-valence topology; neither a green CTest nor a matched source graph is yet a physically published full mixed mesh.

**Strict exact active CI:** [feature #43254280934](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43254280934) + [independent PR #43254298335](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43254298335) on feature `017d3f6c9cf85e5f13482b62719a884a048140f6` in progress. At checkpoint Linux/Windows native QUAD and frozen original Eistute/Book TRI parity PASSED, root Linux CTest 87 / Python 527 and actual model-wide source incidence counts PENDING. No claim of physical all-patch compatibility, no ASan/UBSan memory qualification, no PR merge. Production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged.

**Next:** read exact logs, classify every shared real interface and nonmanifold curve group; if oracle fails or scientific mismatches occur, maintain failed gate and investigate instead of loosening it. Then all-patch AFT and typed physical `SubMesh` rollback only with complete prerequisites.
## 2026-11-12-60 — True model-wide junction has source-curve valence 4 Eistute and 28 Book; all-pair direction oracle corrected

**Measured original external input topology and same-epoch Adapter coverage:** `5952a0ea6acfa408e352dc82cb36c68a6d98d7d7` [feature #43256219375](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43256219375) and [PR #43256234958](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43256234958) **both SUCCESS 4/4**, native QUAD GCC/MSVC 16/16 each, Linux root 87/87, tooling 527/527 Python, frozen original TRI Eistute+Book parity PASS. A corrected Python wrapper now makes the previously hidden `R2B2_SHARED_CURVE_MODEL` source observation mandatory, validates nonzero real same-epoch comparisons and retains output in the existing 14-day verbose CI artifact; exact feature root logs were read.

**Eistute:** external source geometry has 4 patches and 13 curve owners, 12 exterior and **one central curve incident on all four patches** (valence 4); original serial Adapter first global epoch captured **all 4/4** patches in one coherent retry. Original naive all-pair orientation gate: 1 compared central group, 0 matched, 1 rejected, reason `nonmanifold_sheet_policy:1,orientation:6`, 0 source node pairs inspected, four source-derived negative controls PASS.

**Book:** 28 patches and 85 unique curve owners, 84 exterior and **one central curve incident on all 28 patches** (valence 28); same original first epoch captured **all 28/28**. Naive all-pair orientation: 1 compared, 0 matched, 1 rejected, reason `nonmanifold_sheet_policy:1,orientation:378`, zero node pairs inspected, four negative controls PASS. Counts 6 and 378 are `n*(n-1)/2` from testing *every* pair for opposite winding, NOT evidence of 6/378 missing geometric matches or inverted adjacent facets.

**Root cause of first source-oracle rejection:** A multi-sheet axial/junction curve cannot have all incident patch pairs winding oppositely at once. The all-pairs requirement is valid only for actual TWO-SIDED face/edge manifold interfaces. The original research audit erroneously checked direction before source-XYZ, so no curve geometry was compared (zero source-pair counter). This is an oracle design defect, not proof of original model malformed curves, and demands scientific policy for explicit sheet partitioning. No cut/reverse/weld attempt made in production.

**Current correction:** Feature `1535b51ee42d19a406effbea36570514c4641bfb` updates `research/quad/shared_curve_audit.h`, `tests/quad/generator_outcome_probe.cpp`, `tests/quad/test_generator_outcomes.py`. For ALL incidences, compare true parameter and sample-index sequence, source node and curve identity, and XYZ in the original curve frame **without** enforcing impossible multi-way opposite orientation; separately count same/opposite direction pairs, mark high-valence `sheet_policy_pending`, and retain strict opposite-winding gate for actual valence-2 edges. Adds a meaningful negative control asserting geometric identity remains valid when reversing a synthetic counterpart's traversal only in geometry-only audit, without converting it to an admitted sheet. CTest wrapper requires new measured geometry totals and nonzero real pairs. [Push #43257927657](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43257927657) and [PR #43257943351](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43257943351) on exact new source are **in progress** at checkpoint. Do not claim geometry matches, native memory safety or R2c.

**Next:** Verify both exact CI jobs including real `shared_geometry_matched/rejected` and source site-pair counts; record reason if any geometry disagreement. Then define independently reviewed per-leaf oriented sheet partitions around the central curve, actual all-patch original AFT + physical Bezier validation, model-wide typed QUAD/TRI publication with rollback and historical sanitizer qualification. Production main untouched, PR #214 draft.
## 2026-11-12-61 — Exact central-curve source samples coincide in XYZ; separate endpoint ID and physical radial sector diagnosis

**Verified old feature:** `09af072264d2c3c4328b43612fbc502f12197dea` [push #43259404484](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43259404484) + [PR #43259664560](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43259664560), **SUCCESS 4/4 each**, native GCC/MSVC 16/16, root 87/87, Python 527/527 and Eistute/Book original TRI frozen parity PASS. Exact verbose Eistute: `patches=4 curves=13 shared=1 valence=4 shared_geometry_matched=1 shared_geometry_rejected=0 shared_source_ids_rejected=1 shared_node_id_mismatch_pairs=6 mismatch_sites=6 shared_node_pairs=66 max_shared_xyz_error=0 same_orientation_pairs=6 opposite_orientation_pairs=0 sheet_policy_pending=1`. Book: `patches=28 curves=85 shared=1 valence=28 geometry_matched=1 geometry_rejected=0 source_ids_rejected=1 mismatch_pairs=378 mismatch_sites=378 shared_node_pairs=4914 XYZ=0 same_orientation_pairs=378 opposite=0 sheet_policy_pending=1`. All original patches observed in same first global outer epoch/retry; no hybrid global connection inferred.

**New bounded research code:** Feature `47176ed47d0cfd4f7d328221777f499c15077a21` adds `research/quad/shared_curve_sector_audit.h` to independently reconstruct the **actual physical radial ordering** of all high-valence source Bézier sheet incidences, using the original common curve gradient and an inward patch evaluation at a real source sample parameter (no automatic welding/pairing). It records cyclic radial order, minimal angular gap, coincident directions, original shared curve-XYZ consistency, and invalid-duplicate/zero-tangent negative controls. Existing shared-curve audit now separates endpoint and interior original node-ID discrepancies rather than assuming any site ID mismatch is global physical fracture. The generator test records `R2B2_SHARED_SHEET_SECTORS`; Python required evidence verifies presence/coverage, negative controls and `automatic_sheet_pairing_enabled=0`. Production TRI code and source scientific numerical rule unchanged.

**Current exact CI:** [push #43265327210](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43265327210) + [PR #43265339342](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43265339342) on `47176ed`, in progress. No claim of radial geometry success or 4/4 for latest source before checking actual jobs and root model output. Historical fourth-consecutive-in-process fixture memory failure ASan/UBSan remains unresolved. PR #214 DRAFT/UNMERGED, `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` intact.

**Next:** Inspect exact CI results and real Eistute/Book sectors. Distinguish observed radial angles, high-valence nonmanifold graph and actual source node renumbering; do not invent manifold adjacency or authoritatively join patches from this geometric order. Only after audited sheet policy and all-patch AFT/XYZ/rollback can R2c physical mixed publish be considered.
## 2026-11-12-62 — Actual high-valence radial physical sectors verified; source owner terminal ID captured separately (current candidate pending)

**Prior exact qualified source:** `47176ed47d0cfd4f7d328221777f499c15077a21`, [feature #43265327210](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43265327210) and [independent PR #43265339342](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43265339342) **BOTH SUCCESS 4/4** (GCC/MSVC native research QUAD 16/16, root CTest 87/87, Python 527/527, frozen TRI parity Eistute and Book PASS). Verbatim PR root logs:
- Eistute true original first coherent generator epoch: 4 original patch incidences on shared central curve, 4 physically distinct inward radial directions around common tangent, minimum cyclic angular gap `1.5708` radians, zero physical XYZ source-curve error, 4 high-valence samples inspected, negative duplicate-radial/zero-tangent controls passed. All 6 original source mismatched node-ID site pairs occur at endpoints; 0 original ID mismatches in interiors, and 66 original source site pairs XYZ match.
- Book: 28 original patch incidences, 28 distinct inward radial directions, minimum physical angular separation `0.0318123` radians, shared source XYZ difference 0, all 378 ID-mismatch site pairs at endpoints, 0 interiors and 4914 original source site pairs matching in XYZ. Both results use the original independent `PatchBezier::Parameterize` and original shared curve tangent at an ACTUAL sampled parameter. `automatic_sheet_pairing_enabled=0`, since cyclic radial order is NOT a qualified physical connectivity policy. Full-model hybrid `SubMesh` remains unpublished.

**Source/oracle-specific finding:** Original `Adapter::AdaptDomain` closes AFT four-sided chart by omitting the last vertex of each side and aliasing the FIRST vertex of the following side. That correct AFT topological corner can carry the following side curve's node ID, which is not in general the same source curve object's final node ID. The earlier geometry-only evidence was always exact; the prior research `SnapshotSharedCurveSide` treated this next-side alias ID as the previous curve owner's terminal source ID, thus potentially causing a false one-ID-per-pair mismatch. This was demonstrated by the all-endpoint mismatch measurement, but whether canonical source-owner IDs agree globally must be tested, not assumed.

**New isolated experimental repair:** Feature `1d46ba4abce35cc5a28ec214c0d5787414928889` updates only `research/quad/adapter_capture.h`, `research/quad/shared_curve_audit.h` and two QUAD research C++/Python tests. It captures each original curve-owned terminal parameter, original point index/ID and XYZ before the native boundary corner aliases, uses THAT value for canonical shared-curve source identity only after checking geometric agreement to the borrowed next-side AFT corner within existing 2e-7 scale, and adds negative invalid terminal owner ID and forged XYZ controls. It does NOT modify real Adapter source, physical node ownership, original TRI, numeric QUAD point policy, CMake or CLI. Exact [feature #43267126924](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267126924) and [PR #43267143566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267143566) are **in progress**; latest GCC/MSVC QUAD 16/16 and frozen TRI parity PASS, root 87/87, tooling Python 527, original source node-ID results still pending at checkpoint. Do not claim global source ID or sheet conformity until both checks complete.

**Next:** Inspect exact latest source CI and explicit per-model `shared_source_ids_matched/rejected`, endpoint/interior mismatches and radial order; preserve all science gates. If original source IDs coincide, the remaining separate scientific problem is high-valence sheet/edge incidence policy and all-patch physical QUAD/AFT, not fictitious node geometry mismatch. Keep PR #214 draft and production main/CLI unchanged; historical fourth-in-process fixture sanitizer pending.
## 2026-11-12-63 — True original source-curve terminal ID lineage resolves ALL high-valence Eistute/Book false node mismatch pairs, double 4/4

**Source and scope:** Feature `1d46ba4abce35cc5a28ec214c0d5787414928889` on draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` untouched. Research-only `adapter_capture.h` now snapshots each original `CurveAdaptiveParametric` terminal point's parameter, original point index, true owner ID and XYZ by value, before native AFT contour closes with the *following* side's first vertex. `shared_curve_audit.h` restores this original curve-owned source identity for canonical parameter-sequence comparison, requiring actual borrowed AFT closing corner XYZ to agree with owner source XYZ within the existing **2e-7 relative scale**; no node welding or production renumbering. Test probes reject forged terminal source ID or XYZ and recheck original node-ID mismatch endpoints vs interiors. Source numerical point placement, source curve adaptation, native original AFT, production CLI and original accepted TRI `SubMesh` unchanged.

**Exact native CI:** [Feature push #43267126924](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267126924) and [independent PR #43267143566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267143566) **BOTH COMPLETED SUCCESS 4/4** at head `1d46ba4abce35cc5a28ec214c0d5787414928889`; standalone Linux/GCC research QUAD **16/16**, Windows/MSVC **16/16**, Linux root CTest **87/87**, tooling Python **527/527**, scientific frozen original Eistute and Book TRI parity PASS. Actual verbose source logs from BOTH root jobs:
- `R2B2_SHARED_CURVE_MODEL patches=4 ... coherent_epoch_patches=4 shared_geometry_matched=1 shared_geometry_rejected=0 shared_source_ids_matched=1 shared_source_ids_rejected=0 shared_node_id_mismatch_pairs=0 shared_node_id_mismatch_sites=0 shared_node_id_mismatch_endpoints=0 shared_node_id_mismatch_interiors=0 shared_node_pairs=66 max_shared_xyz_error=0 nonmanifold_sheet_policy:1 negative_controls=1 owner_endpoint_negative_controls=1 physical_SubMesh_published=0 global_mixed_model_admitted=0`.
- Book `patches=28 ... coherent_epoch_patches=28 shared_geometry_matched=1 shared_source_ids_matched=1 source_node_id_mismatch_pairs=0 shared_node_id_mismatch_sites=0 shared_node_pairs=4914 max_shared_xyz_error=0 nonmanifold_sheet_policy:1 owner_endpoint_negative_controls=1`.
- `R2B2_SHARED_SHEET_SECTORS`: Eistute 4 distinct radial directions, gap 1.5708 radians, Book 28 distinct directions, gap 0.0318123 radians, no co-directional radial coincidence or original physical curve XYZ mismatch; two independent invalid-sector controls rejected in each. `automatic_sheet_pairing_enabled=0`.
- Existing original AFT source/physical original sampled research single-patch `dynamic_source_aft_admitted=1`, `dynamic_physical_admitted=1` retained both, exact physical facet counts 1096/476; frozen original TRI parity not modified.

**Scientific interpretation:** The prior 6 Eistute / 378 Book one-per-pair source-ID mismatches were solely an *incorrect research observer substitution* of the next-side AFT closure alias for the real source curve's omitted final node ID, not a true mismatch of original shared curve node identity. The correction changed only the source observation, not the original AFT closure or adapter. Original source geometry and IDs now match throughout all 4/28 model incidences in ONE coherent epoch. However central curve valence 4/28 cannot be certified as a conventional two-sided manifold seam; a global mixed shell could require a **nonmanifold fan** whose node/edge incidence is policy-driven. No globally published QUAD/TRI or accepted multi-step adaptation is claimed. Book minimum radial gap ~1.823° is a geometric conditioning warning but not an overlap proof; radial ordering at one parameter does not guarantee global sheet non-intersection.

**Remaining before physical R2c:** Original dynamic T1–T6 QUAD/native exterior AFT and physical XYZ must be attempted for **all 4 Eistute and 28 Book patches** in the same original epoch with per-patch admit/reject/rollback; verify radial sector order along original sampled source curve and high-valence physical edge/vertex incidence without blind welding. Then real typed 4-node QUAD/TRI `SubMesh` atomic publication and prior accepted mesh rollback, repeated adaptation, and independent native sanitizer on historical fourth-in-one-process fixture SIGSEGV. Experimental 1993 interior point formula unapproved; PR remains draft/unmerged.

**Next exact code action:** extend bounded generator research probe from first one true adapted chart to every distinct original patch in the one coherent outer epoch, run original AFT independently per research-owned source tree, evaluate PatchBezier faces and report explicit complete-model patch admission percentages and failures. Do not enable CLI or merge.

## 2026-11-12-64 — All original real adapted Eistute/Book patch research AFT + physical admission probe, running checks

**Exact feature:** `d5c501c2eaa8d7b077caf95261cd2cf4e43c22b1` [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), main TRI `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. Predecessor original shared source ID+geometry high-valence incidence `1d46ba4abce35cc5a28ec214c0d5787414928889` fully verified BOTH exact CI 4/4, Linux/Windows native 16/16, CTest 87/87, Python 527/527, frozen original scientific TRI equivalence.

**What changed (test-only, no CMake/production edits):** `tests/quad/generator_outcome_probe.cpp` collects native independent QUAD T1–T6 + original exterior AFT for each FIRST observed distinct patch of the initial original global epoch/retry, retaining outcomes as value-only per-patch witnesses before the original Generator returns. After the original TRI has finished, it maps every UV-qualified patch into an INDEPENDENT original BP `PatchBezier`, checking source node XYZ and every QUAD/TRI facet Jacobian/orientation, reporting `R2B2_ALL_PATCH_RESULT` individually and one `R2B2_ALL_PATCH_MODEL` with exact coverage/accept/reject counts. In test-only `test_generator_outcomes.py`, all 4 Eistute / 28 Book distinct original patch IDs are REQUIRED, the epoch must equal the already certified coherent curve-graph epoch, and numerical facet count/accept-reject tallies must match; physical rejections cannot be labeled success even when CTest itself passes. No new numerical formula, alternate backend, production QUAD output, arbitrary shared-curve welding or old TRI path changes. Research physical tests borrow independent geometry only after original generator and never publish `SubMesh`.

**Current exact running evidence:** Feature [#43273801537](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43273801537) and PR [#43273812916](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43273812916) on the same `d5c501c2eaa8d7b077caf95261cd2cf4e43c22b1`: GCC/MSVC native QUAD 16/16 each in BOTH jobs **PASS**, root 87 CTest/Python 527, complete model TRI scientific equality and real all-patch admissions pending at checkpoint. A green root test is ONLY complete coverage and classification, not all candidates' physical admission.

**Next:** read exact pipelines and per-patch accepted/rejected markers, repair any exposed gates without downgrading scientific/geometry policy, update evidence on canonical research branch. After source-wide research physical acceptance, analyze true high-valence sheet fan radial stability along curve t, then physical typed mixed `SubMesh` atomic transaction/rollback, repeat adaptation, sanitizer check. PR draft/unmerged and original `main` unchanged.

## 2026-11-12-65 — Complete real external-source 4 Eistute + 28 Book original adapted chart QUAD/AFT physical acceptance, exact 4/4 dual CI

**Committed source:** `d5c501c2eaa8d7b077caf95261cd2cf4e43c22b1` on unmerged, draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214). Production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged, no `quad_uv` CLI. Changes confined to `tests/quad/generator_outcome_probe.cpp` and `tests/quad/test_generator_outcomes.py` — research probes and strict reporting, no production source, CMake, scientific point rule, build baseline or reference metrics changed.

**Work executed:** In the native original Adapter `RefinedQuadtree` observer, the FIRST distinct actual source patch capture per original global epoch 1/retry 0 is cloned into independent original native Quadtree owners. For EVERY observed patch on the original source Eistute 4/Book 28 model, research T1–T6 QUAD is seeded against the original TRI template seam, original exterior AFT completes and audits UV signed area, front closure, exact opposite seam and zero positive-area overlap. A copy of all native TRI/QUAD UV faces and source sampled curve-node XYZ/parameter/IDs is retained BY VALUE before original TRI `GeneratorAdaptive` resumes. After original TRI generator completes, independently owned source `PatchReader/PatchBezier` tests every admitted chart's original curve-source XYZ, `Qu/Qv` Jacobian and oriented 3D physical facets, without modifying accepted `SubMesh`. Each scientific candidate is recorded UV admitted/rejected and physical admitted/rejected, with per-patch reasons and no false model-level promotion. Required Python wrapper insists EXACT 4/28 unique patch IDs, one independently audited coherent curve incidence epoch, full face arithmetic, admission/rejection balance and `global_mixed_model_admitted=0 physical_SubMesh_published=0` on every execution.

**Precise double exact-head CI:** [Feature #43273801537](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43273801537) and independent [PR #43273812916](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43273812916) both **COMPLETED SUCCESS 4/4** on `d5c501c2eaa8d7b077caf95261cd2cf4e43c22b1`. Linux GCC QUAD **16/16**, MSVC Windows QUAD **16/16**, root Linux **87/87 CTest**, Python tooling **527/527**, frozen Eistute/Book original TRI scientific equivalence PASS. Verbose model evidence read directly from BOTH CI root job logs and agreed exactly:
- Eistute `R2B2_ALL_PATCH_MODEL expected=4 observed=4 coherent_epoch=1 coherent_retry=0 repeated_patch_attempts=20 uv_accepted=4 uv_rejected=0 physical_accepted=4 physical_rejected=0 source_sites=160 quad_faces=1888 exterior_triangles=608 validated_physical_facets=4384 min_physical_alignment=0.760759 max_source_xyz_error=9.10112e-15 full_patch_coverage=1 global_mixed_model_admitted=0 physical_SubMesh_published=0`.
- Book `R2B2_ALL_PATCH_MODEL expected=28 observed=28 coherent_epoch=1 coherent_retry=0 repeated_patch_attempts=0 uv_accepted=28 uv_rejected=0 physical_accepted=28 physical_rejected=0 source_sites=1008 quad_faces=5264 exterior_triangles=2800 validated_physical_facets=13328 min_physical_alignment=0.998453 max_source_xyz_error=4.44089e-16 full_patch_coverage=1 global_mixed_model_admitted=0 physical_SubMesh_published=0`.
- Each root log contained exactly **32 per-patch lines** (4+28) with zero `uv_admitted=0` or `physical_admitted=0`. Original `R2B2_SHARED_CURVE_MODEL` still reports central source high-valence **nonmanifold_sheet_policy:1** (Eistute valence 4, Book valence 28) despite correct source original IDs/XYZ, preventing fictitious global manifold admission. Original native TRI parity unchanged.

**Scientific limitations:** These original-source per-patch results were produced as independent **research candidates from the FIRST observed local attempt for each patch** within one complete original outer epoch, NOT as published physical QUAD/TRI `SubMesh` after the generator's final global TRI acceptance/retry. No stitched global mesh or high-valence fan edge incidence/ownership is proven; shared original source curve identity is known, but **face-to-face nonmanifold adjacency policy is still open**. Radial order observed only at one original curve parameter, not at all; 1993 point placement unapproved; historical fourth-consecutive-in-process native fault not yet ASan/UBSan diagnosed. Physical typed mixed `SubMesh` transaction/rollback, repeated mixed global adaptation, production CLI and research PR merge remain BLOCKED.

**Next:** Add independent radial-sector sampling throughout each shared original nonmanifold curve (both 4/28 valence) with exact source interval parameters and detect sector crossings/near-degenerate fan gaps; design explicit nonmanifold ownership/edge fan policy only after that evidence. Then R2c physical typed mesh atomic publish/restore and repeated adaptation. Maintain draft PR, main and default TRI.
## 2026-11-12-66 — Sample entire original high-valence Eistute/Book curve fan at original parameters and interval probes (CI pending)

**Work item:** With actual research per-patch original native QUAD/AFT and physical PatchBezier Eistute 4/4 and Book 28/28 already independently certified at source `d5c501c2eaa8d7b077caf95261cd2cf4e43c22b1`, continue the next pending high-valence common curve research gate. The existing `AuditOriginalHighValenceSectors` observed ONE midpoint parameter only and cannot establish stable sheet radial order along the original curve.

**Implementation:** `686ef7d50d7deb981aff7a7919d8d9c6ca44ebb3` in [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), files `research/quad/shared_curve_sector_sweep.h`, `tests/quad/generator_outcome_probe.cpp`, `tests/quad/test_generator_outcomes.py`. Keep actual coherent original `GeneratorAdaptive` epoch and source owner graph. For every source interval evaluate original interior curve nodes plus quarter/midpoint/three-quarter parameters, excluding curve endpoints where frame degeneracy is possible but retaining source endpoint identity checks. At EVERY sample recompute native `CurveAdaptiveParametric` gradient, source `PatchBezier` boundary XYZ and inward radial directions in its tangent-normal plane, then canonicalize sector order up to cyclic rotation, compare consecutive frames, monitor minimum cyclic angle, coincidence and maximum local relative rotation. Frame comparisons are observational, do not automatically pair/manifold-weld sectors. Invalid tangents/samples/source mismatches fail closed or produce explicit rejections. Negative oracle swaps two real patch identities, duplicates an angle, injects an invalid canonical parameter and verifies a harmless cyclic rotation. Python wrapper requires exactly one source-derived `R2B2_SHARED_SHEET_SWEEP` trace per model with internally balanced counts, original source coverage, negative controls, and no global mixed publication. A passing CTest does NOT imply sampled-order admission if `sampled_order_admitted=0`, and even sampled admission is not a continuous no-intersection proof.

**Current exact gates:** [feature push #43299825976](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43299825976) and [independent PR #43299837378](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43299837378) on `686ef7d50d7deb981aff7a7919d8d9c6ca44ebb3` are in progress at this checkpoint. No source-level GCC/MSVC/root CTest/Python or real Eistute/Book sweep-result success is claimed until exact-head CI concludes. No production Adapter/Generator, CMake, scientific point formula or output `SubMesh` changes. Main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` preserved.

**Next:** inspect both exact CI runs and quantitative Eistute/Book sampled radial order markers; retain failures and correct only reproduced code defects with full gates. Then investigate between-sample sector swaps/near-coincident fan and explicit physical nonmanifold edge ownership, followed by transactional typed mixed R2c, repeated global adaptivity and separate native ASan/UBSan memory qualification. PR remains draft/unmerged.
## 2026-11-12-67 — Original adapted high-valence entire source sampled curve radial order exact double CI qualified

**Candidate:** `686ef7d50d7deb981aff7a7919d8d9c6ca44ebb3` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214). No `src/adapter`, `GeneratorAdaptive`, original TRI, production `main`, 1993 numerical rule, CLI or typed `SubMesh` code changed. Added `research/quad/shared_curve_sector_sweep.h`; modified the research-only `tests/quad/generator_outcome_probe.cpp` and `tests/quad/test_generator_outcomes.py`.

**Exact CI qualification:** [feature #43299825976](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43299825976) and [independent PR #43299837378](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43299837378) BOTH **COMPLETED SUCCESS 4/4** at the same source. Native GCC Linux QUAD **16/16**, MSVC Windows QUAD **16/16**, Linux root **87/87 CTest**, Python **527/527**, frozen Eistute/Book original TRI scientific parity **PASS** in both. Actual original high-valence `R2B2_SHARED_SHEET_SWEEP` measurements and unchanged entire 4 Eistute / 28 Book physical per-patch research source admissions were independently read from BOTH root job logs. Neither a green CI alone nor a previously certified midpoint radial witness was used to infer sampled fan stability.

**Measured full original source interval sample coverage:** Eistute central curve valence **4**, 10 actual original curve intervals, 39 probe parameters (interior original nodes and quarter/midpoint/three-quarter of every interval), 156 radial sector observations, zero order changes, zero nearly-coincident sectors, zero invalid original sampling, sampled-order admitted 1, minimum cyclic angular gap **1.5708 rad** at t=0.25, maximum patch-curve XYZ error **8.88178e-16**, maximum adjacent sample angular drift **9.76996e-15 rad**, all actual-source adversarial controls PASSED. Book central curve valence **28**, 12 original curve intervals, 47 probe parameters, 1316 radial sector observations, zero sampled swaps/coincident/invalid, sampled-order admitted 1, narrowest gap **0.0318123 rad** at t=0.5, max patch-curve XYZ difference **2.22045e-16**, max sampled sector drift **0.0151401 rad**; negative controls PASS. No automatic sheet pairing or global mixed physical publication (`global_mixed_model_admitted=0 physical_SubMesh_published=0`).

**Engineering/scientific contract:** All fan frames use original shared curve derivative as tangent, independently loaded source `PatchBezier` edge XYZ and inward physical radial displacement projected into normal plane. Compare cyclic incidence ordering invariant to the angular origin. Deliberately permuting two real patch identities, duplicating an angular sector, repeating a source parameter, and rotating cyclic indices are observed by the negative/reference oracles. The result is a **finite-parameter sampled witness only**. A sheet crossing twice inside a parameter interval, tangent/curvature degeneracy between probes or a global self-intersection has not been mathematically excluded. Book's ~1.823° minimum gap requires particular conditioning attention; sampling alone is NOT a proof of interval-wide nonintersection. The old one-midpoint witness and all 4/28 original source per-patch physical validity remain separately qualified.

**Next scientific step:** derive source-specific interval bounds using original Bézier algebra/validated root exclusion or conservative interval techniques for radial sector swaps and near-coincident directions across every source t-interval, with numeric error budget and negative examples; separately propose explicit radial edge ring/sheet ownership policy and obtain advisor review before any actual nonmanifold typed `SubMesh` R2c publication/rollback. Repeated global mixed adaptation and historical fourth-in-process ASan/UBSan lifetime remain open. PR #214 stays draft, default TRI and main preserved.

## 2026-11-12-68 — First real Bézier Bernstein interval radial-order candidate committed; source proof pending

**Intent:** continue from exact sampled Eistute/Book high-valence source fan gate #67, which does not exclude between-probe swaps. Implement an independent finite-degree, interval-wide sign exclusion strategy while keeping the research-only candidate and original TRI production separated.

**Remote feature:** [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), head `ad9c789f200f2324c5d26a45703c10a621787809` (unmerged). Added `research/quad/bernstein_interval.h`, `research/quad/shared_curve_bernstein_audit.h` and `docs/research/quad/R2B2_BERNSTEIN_INTERVAL_ORIENTATION_20261112.md`; extended `tests/quad/generator_outcome_probe.cpp` and `tests/quad/test_generator_outcomes.py`. The native probe reads the original source cubic `CurveAdaptiveParametricBezier` tangent and the original bicubic patch control net, computes a degree-eight adjacent-sector orientation polynomial, and restricts its outward interval Bernstein coefficient bounds to every original source interval. Positive, sign-inverted and inconclusive intervals are classified separately. Synthetic controls catch a sign inversion, collapsed radial, malformed interval and two hidden crossings between positive endpoints. **No new scientific validity is asserted until the exact original model reports and toolchains are verified.**

**Current remote CI observation:** exact feature [PR run #43307378736](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43307378736): Linux native QUAD success; Windows native QUAD success; frozen original scientific TRI equivalence success; Linux root baseline/tooling still in progress. Full root CTest/Python and original Eistute/Book interval sign results are pending/unobserved at this checkpoint. Local native tests and sanitizers were unavailable. Earlier 4/4 Eistute, 28/28 Book per-patch QUAD/AFT physical witnesses and finite source-sector stability remain valid only under their already-certified previous SHA, not this new continuous theorem.

**Gate/constraints:** exact-head proof, not a sampled inference; if any interval is negative or unresolved, do not set `interval_order_certified=1`. A strict-positive control-net result would certify only the local ordered radial fan under numeric assumptions; not full surface intersections, nonmanifold sheet ownership, global `SubMesh` transaction or the 1993 point formula. `automatic_sheet_pairing_enabled=0`, `global_mixed_model_admitted=0`, main/TRI/production remain unchanged.

**Next:** inspect completed feature CI and real `R2B2_SHARED_SHEET_BERNSTEIN` markers for Eistute (expected 40 pair-intervals) and Book (expected 336), triage failures or inconclusive closed endpoints and rerun. Only then prepare the independently reviewed valence-4/28 edge-fan ownership policy and R2c publication/rollback.

## 2026-11-12-69 — Real-source CTest failure reproduced, signed-wide Bernstein defect repairs pushed

**Diagnosis:** Source exact push [#43307082540](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43307082540) failed two required CTests (Eistute/Book). Real Eistute observation actually computed 40/40 strict-positive pair intervals, smallest rounded polynomial lower bound 0.0329135; failure was a malformed literal backslash-n report line. Book returned `R2b2 continuous Bezier fan interval accounting incomplete` before marker because any wide original radial sector (>180 degrees) returned early; source Book was not geometrically rejected by the previous finite fan sweep. The patch fixes those concrete errors without weakening the oracle: a wide reference sector is certified with strictly **negative** signed `D_ij` (strict positive `-D_ij`), invalid gaps near 0/pi/2pi are classified inconclusive; expected-negative synthetic sign control added; source log termination and strict Python accounting corrected. Scientific model validity still depends on exact-source CI.

**Candidate:** [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), head `a2a830858357776d77ad0020721efd0adf7fa1cc`, still UNMERGED. Corrected `research/quad/shared_curve_bernstein_audit.h`, `tests/quad/generator_outcome_probe.cpp`, `tests/quad/test_generator_outcomes.py`, and mathematical description. New exact [CI #43309180825](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43309180825) underway at checkpoint. No local native or sanitizer testing. Do not report Book continuous-order certification or 87/87 root CTest /527 Python on this SHA until observed. Original TRI/default production/main unchanged.

**Next:** review exact push/PR complete CI, classify original Eistute 40 and Book 336 pair intervals, retain any inconclusive/negative domains. Then independent nonmanifold radial ownership policy and R2c transactional mixed `SubMesh` gates.

## 2026-11-12-70 — R2b2 original Bernstein full-source local radial order, exact independent CI double qualified

**Feature head / PR:** `e9cdea99463f18075ba29535a9f5c37a749a1330` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), unmerged. This session modifies only research source wrapper `tests/quad/test_generator_outcomes.py` to print the already-generated, separately validated `R2B2_SHARED_SHEET_BERNSTEIN` model line and check internal reason/positive-bound consistency. It does **not** change the underlying source Bézier curve, interval orientation algorithm, original production TRI, AFT, or `SubMesh` implementation.

**Exact independent CI:** feature push [#43313839319](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43313839319) and PR [#43313852405](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43313852405) both **completed success 4/4** on identical source `e9cdea99463f18075ba29535a9f5c37a749a1330`. Each separately passed native Linux GCC **16/16 QUAD**, Windows MSVC **16/16 QUAD**, root Linux **87/87 CTest**, tooling Python **527/527** and frozen production scientific TRI equivalence for Eistute/Book. Independently inspected unmodified real-source model interval markers from BOTH root job logs:
- Eistute: original valence=4, intervals=10, 40/40 positive oriented Bernstein interval checks, 0 inverted, 0 unresolved, 0 wide reference pairs, source lower bound 0.0329135; interval certificate=1; source negative controls=1.
- Book: original valence=28, intervals=12, 336/336 signed/oriented Bernstein interval checks, 0 inverted, 0 unresolved, 1 valid >pi reference pair whose correct expected sign is negative, lower bound 1.80351e-05; interval certificate=1; source negative controls=1.

**Numerical and scientific boundary:** Signed strict Bernstein control-hull exclusion of zero on each original closed source interval is stronger than finite source-frame observations: under the explicit floating-point assumptions, adjacent original radial sheets cannot exchange cyclic order without passing through a zero signed triple product. The 376/376 source interval certificates are **not** whole-surface global collision proof, physical sheet ownership approval, `halfedge.twin` pairing, original 1993 point/contour acceptance, mixed model `SubMesh` publication or production QUAD enablement. `automatic_sheet_pairing_enabled=0` and `global_mixed_model_admitted=0`. No local MSVC/sanitizer or repeated mixed adaptive lifetime run in this conversation; native hosted jobs only as documented.

**Next:** review and explicitly version model-source-SHA-bound junction sheet classifications for Eistute 4-owner and Book 28-owner curves, using read-only radial incidence rings without inventing twins. See `R2C_NONMANIFOLD_RADIAL_OWNERSHIP_DESIGN_20261112.md` as a proposal (not approved). Implement R2c-0 immutable fan incidence and policy schema validation only after the review requirements are met; staged owner/observer transaction, model-wide physical QUAD/TRI publication and repeated adaptivity remain gated. Current research PR #214 stays draft/unmerged; `main` and default TRI unchanged.

## 2026-11-12/13-71 — Implement R2c-0 source-edge radial identity and pending-sheet policy (exact CI pending)

**Scope:** Research-only draft PR #214, head `2907e0e04ea7f819e52009713a2d870cab70bc62` with no physical mesh mutation. The real C++ original Generator `generator_outcome_probe.cpp` now emits the original high-valence curve registry index, legacy source curve label (allowed to be zero), source knot parameters at 17-digit round-trippable precision, source physical node IDs, and measured radial order for the coherent source epoch/retry. Original native wrapper requires exact curve interval/node/order identity and source-signed Bernstein evidence agreement. No original math, TRI path, default CLI, `SubMesh` owners or AFT acceptance policy is changed.

**Implementation:** New `tests/quad/test_r2c0_source_radial_incidence.py` consumes actual retained verbose original Generator CTest trace and validated real M4 PatchReader graphs from both unapproved centroid UV center rules. It links original model SHA, original Geometry curve index, actual source segment endpoints/physical node IDs, patch/side/reversal, per-interval radial_next geometric adjacency and exact C++ sign certification. The validator builds an immutable pending policy whose model/curve/epoch/source-evidence hashes and full ordered incidences are mandatory, while sheet ID and junction kind remain undecided. It rejects forged scientific approval, nonempty continuations, node sharing, malformed identities/duplicate incidences, wrong hashes and epoch/retry changes. It does not create a manifold twin or physically publish/weld nodes. Required GitHub Actions step is downstream of the root M4 graph CTest and independent native original source log, writes and retains 14-day source JSON evidence. [Source design note](https://github.com/tiagosombrra/apmesh-modernization/blob/7cd5014936a417565415d736bad40dc70deb35df/docs/research/quad/R2C0_REAL_SOURCE_RADIAL_EDGE_RECORDS_20261112.md) may not exist; authoritative current [R2c0 implementation note](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C0_REAL_SOURCE_RADIAL_EDGE_RECORDS_20261112.md).

**Qualification at checkpoint:** exact matching feature [push #43336171330](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43336171330) and [PR #43336183353](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43336183353) not finished; QUAD Linux/Windows and TRI frozen comparison already green in push. Full 87 CTest/527 Python and native R2c0 records **not yet reviewed**. Earlier R2b2 376/376 bound certificates remain qualified on earlier head only. No native local/sanitizer runs. `main` and production TRI unchanged, PR draft/unmerged.

**Next:** inspect exact latest Actions root logs; correct any new R2c0 test failure and recertify, then update these provisional claims to measured per-model counters. Book 28-owner and Eistute 4-owner scientific sheet continuation remain pending advisor approval, Ribbed Bracket valence-3 continuous intervals unqualified, no model-wide QUAD/TRI publication.

## 2026-11-13-72 — R2c-0 original radial edge intervals + pending policy: independent double exact-CI qualified

**Feature and code:** [Draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) exact `1c7db831ded2324c78b33d0faf39fb1c0ce08439`. Native `generator_outcome_probe.cpp` emits original source `R2C0_ORIGINAL_SOURCE_RING` (true original source parameters/physical source node IDs, coherent Generator epoch/retry, `Geometry` registry curve index and cyclic `patch:side` incidences). `test_generator_outcomes.py` validates native identity, Bernstein and radial order. New `test_r2c0_source_radial_incidence.py` links source to exact real `.bp` model SHA and independently qualified M4 PatchReader hypergraphs for both unapproved UV centroid rules; produces immutable per-original-interval directed incidence records and pending-only scientific sheet policy templates. Every `radial_next` denotes geometric order, **NOT** physical `halfedge.twin`, and `node_sharing=NOT_AUTHORIZED`, `manifold_twin=null`. Policy validator rejects forged approval, source or incidence hashes, orientation, duplicate/missing owners, scientific pair continuations and shared-node authorization; no physical `SubMesh` is created. The required Actions step preserves small JSON source artifacts. [Feature source note](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C0_REAL_SOURCE_RADIAL_EDGE_RECORDS_20261112.md).

**Initial failure, retained:** First exact [push #43336171330](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43336171330) failed root **85/87** (both real Eistute and Book wrapper tests) because new Python field regex `[^\\\\s]` was double-escaped; corrected to `[^\\s]` (three occurrences), with explicit missing-fields diagnostics, on feature `1c7db831ded2324c78b33d0faf39fb1c0ce08439`. This is not a scientific failure of the original Bernstein signs, and is not silently erased.

**Measured independent complete gates:** Both [feature push #43337244641](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43337244641) and [independent PR #43337254962](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43337254962) completed **SUCCESS 4/4**, native GCC QUAD **16/16**, native Windows MSVC **16/16**, root CTest **87/87**, Python tooling **527/527**, frozen original TRI scientific Eistute/Book equality PASS, and required exact real-source `R2C0_SOURCE_INCIDENCE models=2 source_intervals=22 adjacencies=376 negative_controls=38 radial_records=source_verified node_welding=0 scientific_sheet_approval=0 physical_SubMesh_published=0` in BOTH root job logs. Source Eistute high-valence `Geometry` curve index 3, legacy label 0, epoch 1/retry 0, 11 original knots (10 intervals), **40/40** signed certified source interval incidences, node IDs `21,81,82,83,84,85,86,87,88,89,58`, radial `0:3,3:3,2:3,1:3`. Book central curve index 3, legacy 0, epoch 1/retry 0, 13 original knots (12 intervals), **336/336**, 28 incident sheets, one valid wide reference sector, node IDs `141,170,171,172,173,174,175,176,177,178,179,180,160`, 0 unresolved/inverted. Negative policy controls **38/38 rejected** (19 per real model). Retained [push JSON](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43337244641/artifacts/13998900846) and [PR JSON](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43337254962/artifacts/13997918300); PR artifact name incorporates generated test-merge checkout SHA, but run head is feature `1c7db831ded2324c78b33d0faf39fb1c0ce08439`.

**Scientific and operational constraints:** Native hosted CI is not a local build or ASan/UBSan. R2c0 is only source-backed radial **read-only engineering qualification**, NOT advisor-approved sheet continuation, global physical surface nonintersection, multi-chart node welding or R2c per-patch `SubMesh` publication. Existing `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, TRI default, disabled `quad_uv` and draft PR unchanged. Next: R2c-1 reviewed model-SHA-bound high-valence Eistute and Book sheet semantics; only then consider permissive policy and staged cross-chart physical ownership/rollback; Ribbed Bracket valence 3 source intervals also remain unqualified.

## 2026-11-13-73 — R2c-1 bounded source-bound sheet review proposal validator (exact CI pending)

**Feature head:** `f5bf84552c5f73d4e57fd272ef48f85f496cef6d` on research draft PR #214. New Python `tests/quad/test_r2c1_sheet_review.py` reads actual original R2c0 model-source-hash records/pending policies from the same CI run. It verifies source physical node ownership provenance, original curve sample partition, directed `radial_next` for each original parameter interval, exact coherent native model and epoch identity. It generates one all-field, source-hash-locked `PENDING_ADVISOR_REVIEW` packet per Eistute and Book model. Five scientific questions have null findings; all physical rights false. The independent `DRAFT_NOT_APPROVED` structural proposal validator accepts test-only *syntax* for a complete MANIFOLD_PAIR or BRANCH_MULTI_SHEET group, preserving source incidences in radial order, and rejects partial interval coverage, false orientation/owner approvals, overlapping members, stale source hashes, tampered node ids, forged reviewers, fake model continuation and any mesh publication. Synthetic positive draft validation NEVER grants scientific or physical admission. 49 negative controls/model are encoded, expected 98 total, and wired to required CI step after R2c0. [Full method and limits](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C1_SOURCE_BOUND_SHEET_REVIEW_20261113.md).

**Not certified at checkpoint:** matching full root CTest + new required R2c1 step `R2C1_SHEET_REVIEW` and 98 adversaries were still running; GitHub-hosted exact push/PR complete gates have NOT been verified. Prior R2c0 double success stays historical only. No local native sanitizers, actual independent advisor decision or welded QUAD/TRI `SubMesh`. No production source touched. Next inspect [exact PR CI #43346066228](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43346066228) and exact feature push run; correct failures, preserve negative evidence and update this provisional checkpoint.

## 2026-11-13-74 — R2c-1 original-source science-review packets: two independent CI records, final head verified

**Source code:** [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), exact feature `f5bf84552c5f73d4e57fd272ef48f85f496cef6d`; actual review validator in `tests/quad/test_r2c1_sheet_review.py` and required source-native CI step. It consumes per-model real R2c0 source records and independently qualified source/model hashes and original radial interval partition. It emits one immutable versioned `PENDING_ADVISOR_REVIEW` packet for each actual high-valence Eistute and Book curve, with source curve nodes, original `Geometry` index, source epoch/retry, 22 source parameter intervals and all 376 geometric radial adjacency records. It has an unapproved **draft syntax only**, including explicitly labeled test-only pair and branch examples, with `REQUIRES_SCIENTIFIC_REVIEW` orientation, `UNASSIGNED` nodes and null reviewer findings; no model topology or synthetic decision is claimed as real.

**Independently verified CI:** [Source push #43345929005](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43345929005) on `244f23d6f3f057470ffd611b430ef0a7b9f59780` and [final PR #43346066228](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43346066228) on `f5bf84552c5f73d4e57fd272ef48f85f496cef6d` both **completed SUCCESS 4/4**, GCC QUAD native **16/16**, Windows MSVC native QUAD **16/16**, root Linux **87/87 CTest**, Python tooling **527/527**, frozen original scientific Eistute and Book TRI comparison PASS. A GitHub compare confirmed `244f23d6f3f057470ffd611b430ef0a7b9f59780..f5bf84552c5f73d4e57fd272ef48f85f496cef6d` changes **only the added R2c1 research documentation**, not any source, test, workflow or numerical gate. BOTH independently inspected root logs show `R2C1_SHEET_REVIEW source_models=2 original_intervals=22 radial_adjacencies=376 negative_controls=98 draft_structure_only=1 advisor_approved=0 node_welding=0 physical_SubMesh_published=0`, plus R2c0 original 38 pending-policy rejections. Review packet JSON retained as [push artifact #14001662390](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43345929005/artifacts/14001662390) and [final PR artifact #14001867145](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43346066228/artifacts/14001867145). **49 negative controls per actual source model, total 98**, all rejected. This qualifies only source-bound review data and fail-closed structural draft checker, **not a scientific sheet continuation or physical mesh**.

**Closure audit:** Original physical/node/element owners, `SubMesh`, AFT/Generator output, original TRI and scientific numerical Bernstein source not modified; no production CLI switch or `quad_uv` admission. No local native build or ASan/UBSan; hosted native/compiler evidence is bounded. All nonmanifold sheet topology and actual advisor/model-owner decision provenance remain pending; Ribbed Bracket valence-3 original intervals not certified, global repeated adaptive ownership/rollback not implemented, 1993 historical algorithm not approved. Production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged; PR #214 draft/unmerged.

**Next:** obtain real model-SHA-bound Eistute/Book scientific junction decisions and independent review; then design acceptance of genuinely reviewed topology/ownership data rather than promoting a `DRAFT_NOT_APPROVED` group or deriving `twin` from `radial_next`. Maintain research-only scope until then.

## 2026-11-13-75 — R2c-2 preflight disconnected chart owner staging; source and fault code, exact CI pending

Feature head `290e37a8b99a9c4096b6e7d32d636a0c2b513b1c` on draft PR #214 adds experimental `DisjointOwnerStage` (no production generator changes) and `quad.r2c2.disjoint_owner_stage` root CTest. It prepares a fully detached `MeshAdaptive` with individually owned `SubMesh` charts and chart-local QUAD and TRI node observers, rejects missing/null charts and cross-owner node provenance and checks 4-node/3-node element reverse memberships. Candidate construction failure does not touch active `MeshAdaptive`; after all source graph checks pass, a single `unique_ptr<MeshAdaptive>::swap` replaces the root with a fully populated disconnected stage. The old model remains intact after deliberately injected failures before every chart adoption and prepublication. Synthetic chart stress uses Eistute/Book cardinalities 4 and 28 (no claim of source geometry), and a **separately labeled** real physical-source example uses actual `PatchReader::ReaderFilePatches` on tracked Eistute/Book `.bp` files, `PatchBezier::Parameterize` and the original patch differential normal to construct only one interior QUAD and one TRI per patch. This is neither a full original native Quadtree/AFT patch tessellation nor any joined or accepted model-wide physical QUAD/TRI `SubMesh`. `Patch::SetSubMesh`/`SubMesh::SetPatch` are untouched on purpose; real forward/back observer commit and shared node ownership remain blocked. Original production TRI and `main` unmodified. [Methodological boundary](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C2_DETACHED_DISJOINT_STAGE_PREFLIGHT_20261113.md).

**Tests at checkpoint:** new root CTest installed but **not yet known successful**; expected 88 total CTests, 36 synthetic and 34 real original-patch failure-injection rejections, plus source graph and conservative existing R2c0 38 and R2c1 98 policy controls, frozen original TRI baseline. [PR CI #43348535255](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43348535255) queued. No exact-head/local sanitizer results claimed; any failure must be inspected, repaired and logged. Stage is engineering preflight only; high-valence scientific sheet semantics remain pending independently. Next: complete and audit exact CTest and CI then update canonical checkpoint.

## 2026-11-13-76 — R2c-2 source owner staging CTest positive; CI architecture/YAML remediation, exact full CI pending

**Measured limited proof:** New research `quad.r2c2.disjoint_owner_stage` passed as CTest #73/88 on first completed root [push #43348480434](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43348480434). This test exercises native C++17 detached chart ownership and failure-atomic `unique_ptr<MeshAdaptive>` root swap with 4/28 chart cardinality, seven owned nodes and two typed QUAD/TRI elements per chart, two successful repeated owner swaps, and original Eistute/Book tracked `.bp` source `PatchReader`/ `PatchBezier` interior physical samples; the prior accepted root and observers remain unchanged after injected faults. No model-wide AFT full mesh/physical junction is produced and no `Patch` observers are bound.

**Adverse CI and repair:** The overall root on #43348480434 failed **87/88** because the **existing** `tooling.controls` source architecture inventory CMake digest was stale after adding the bounded CTest, not because new R2c2 C++ crashed; exact CMake digest independently computed SHA-256 `564316245bfaf95c47930b74557fd962970e0c4b6fca29cf65a7b6b32c674d76` and updated the one `docs/architecture/source_inventory.json` build hash in `a0a611b2`. An attempted verbose-log workflow insertion using JS `String.replace` interpolated `$'` (the regex end anchor followed by a quote) as a suffix token, duplicating YAML and producing zero-job [push workflow failure #43349647165](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349647165). This was not dismissed: the entire original workflow was re-read from the last valid commit and restored, inserting the two expected bounded trace-and-retain steps using a literal-safe replacement callback; GitHub exact resulting workflow has 43 steps and original source gates preserved. Repair committed at current feature `54f0aafbfbbd27b8f3d6a923dbc34cc8579212a5`.

**Exact candidate CI:** [feature push #43349916549](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349916549) and [PR #43349923938](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349923938) for the same feature `54f0aafbfbbd27b8f3d6a923dbc34cc8579212a5` were both in progress when recorded, 3/4 jobs each with native GCC/MSVC QUAD and scientific frozen TRI parity passing, root Linux compiling. Full native root **88/88** and retained `R2C2` source/fault log are NOT YET CERTIFIED; no output counters fabricated. Previous R2c1 exact source evidence remains separately qualified. [Source implementation note](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C2_DETACHED_DISJOINT_STAGE_PREFLIGHT_20261113.md) and [bounded evidence](evidence/R2C2_DISJOINT_OWNER_STAGE_20261113.json). Main original TRI unchanged; scientific topological sheet semantics are still unapproved.

## 2026-11-13-77 — R2c-2 detached original-source per-patch owner and exception rollback: exact independent double-CI CERTIFIED

**Exact feature:** `54f0aafbfbbd27b8f3d6a923dbc34cc8579212a5` [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), base `quad-templates`; original production main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. `research/quad/disjoint_owner_stage.h` (research-only, no production app linkage) checks fully owned disconnected `SubMesh` charts, local QUAD/TRI reverse node observers and all unique chart node addresses. It constructs the complete candidate `MeshAdaptive` off-side and swaps the owner root exactly once only after nonthrowing publication condition. A new required root `quad.r2c2.disjoint_owner_stage` CTest executes 4 and 28 synthetic chart groups and actual tracked `.bp` Eistute/Book via production `PatchReader`/`PatchBezier` physical XYZ: only a small inner example QUAD + TRI per original patch, NOT full source Quadtree/AFT tessellation. No `Patch` forward/back observers are attached, and no cross-chart nodes are welded.

**Retained adverse CI:** [push #43348480434](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43348480434) passed new CTest #73/88 but failed existing `tooling.controls` source inventory CMake digest (root 87/88). Retained `docs/architecture/source_inventory.json` CMake SHA updated to `564316245bfaf95c47930b74557fd962970e0c4b6fca29cf65a7b6b32c674d76`. First verbose workflow insertion used a JS replacement string containing regex `$'`, causing unintended suffix interpolation and a malformed full workflow; no-job [run #43349647165](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349647165) failed. Fixed by literally reconstructing the original valid workflow with the two new bounded test-output/archive steps, using replacement callback (43 steps preserved) on final `54f0aafbfbbd27b8f3d6a923dbc34cc8579212a5`. Canceled intermediate runs do not count as green.

**Actual exact double-source qualification:** [push CI #43349916549](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349916549) and [PR CI #43349923938](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349923938) both **COMPLETED SUCCESS 4/4**, exact identical head `54f0aafbfbbd27b8f3d6a923dbc34cc8579212a5`. Each passes root **88/88 CTest**, Python tooling **527/527**, native QUAD Linux/GCC **16/16**, Windows/MSVC **16/16**, and unmodified original Eistute/Book TRI scientific comparisons. Both root logs include `R2C0_SOURCE_INCIDENCE` 376 source local radial adjacencies/38 negative controls, `R2C1_SHEET_REVIEW` 376/98, and new `R2C2_DISJOINT_STAGE` synthetic cardinality 4 (4 submeshes, 28 nodes, 8 typed QUAD/TRI elements, 6 injected source rollback failures and 2 successful root swaps) and cardinality 28 (28 submeshes, 196 nodes, 56 typed elements, 30 injected failures and 2 swaps). Real source `R2C2_REAL_SOURCE_DISJOINT` Eistute 4 patches 5 injected failures, Book 28 patches 29, 2 deliberately small interior physical source elements per patch. **70/70 injected/incomplete staging trials rejected**, 0 shared nodes, 0 `Patch` observer attachment, 0 global physical `SubMesh` publication or advisor sheet approval. Both real source records currently print on one line separated by literal `\\n` diagnostic formatting; explicitly inspect both marker substrings rather than treating the line count as a model count. Retained exact source C++ traces: [push artifact #14003742707](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349916549/artifacts/14003742707) and [PR artifact #14004455234](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43349923938/artifacts/14004455234).

**Closure boundary:** This is successful **detached, disconnected owner staging and rollback engineering preflight**, not full original physical QUAD/AFT per-patch tessellation in a joined model, not approval of nonmanifold physical seam continuations, and not actual atomic rebinding of `Patch` to published `SubMesh`. The two real models' sheet semantics remain **PENDING_ADVISOR_REVIEW**. Original main TRI/CLI unchanged, `quad_uv` disabled, research PR draft/unmerged; no local native sanitizer. Next bounded engineering research: carry over qualified R2b2 full per-patch candidate elements into detached staging and test source parameter seam integrity/rollback. Physical node sharing, patch-link atomics and global publication are independently gated behind model-SHA-bound scientific decisions and ASan/UBSan.


## 2026-11-13-78 — R2c-2 complete original QUAD/AFT patch inventories staged as disconnected owners; exact CI still pending

**Intent:** Replace the original R2c-2 pair of sample physical elements per original patch with the actual full research QUAD template + legacy exterior AFT TRI face inventory on each original Eistute and Book source Bézier chart, while retaining disconnected chart ownership and negative rollback gates. No scientific cross-patch continuation or production activation is authorized.

**Actual code:** Draft PR #214 feature head `e43979013cc402804675edbdf9d9ebba5df6d59b`. Added `tests/quad/full_source_patch_stage_probe.cpp` and root CTest `quad.r2c2.full_source_patch_stage` in `CMakeLists.txt`; updated `docs/architecture/source_inventory.json` CMake SHA256. Native original fixed 16-segment UV source sampling, original tree TRI reference and `SnapshotLegacyFront`, experimental QUAD templates, seeded owned AFT exterior TRI source cells, full native triangular/quad candidate physical XYZ lifting, source curve-side alignment and face orientation checks, locally unique nodes and reverse element observers, and detached full-model root swapping with three injected per-model rollback scenarios and prior pointer identity preservation are all present as candidate source. This does **not** call full original `Adapter::AdaptCurve`, adopt cross-patch physical seams, publish `Patch` observers or create a global conforming production output. Original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` was read and unchanged.

**Verification status:** Feature code committed; exact-head run [push #43397303113](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43397303113) queued when checked. Root Linux expected **89 tests if successfully configured**, native MSVC/GCC QUAD 16 each, Python tooling 527 and frozen TRI equivalence all **UNVERIFIED/PENDING** on this new SHA. The prior 88/88 CTest green belonged to earlier `54f0aafb`. Native local compiler/build/ASan/UBSan unexecuted because no local checkout/runtime access and remote Git DNS unavailable. Per-model full physical face counts have not been measured. Provisional exact-sha [evidence](evidence/R2C2_FULL_SOURCE_AFT_STAGE_20261113.json). No PR merge.

**Next handoff:** Inspect exact SHA root compiler/CTest logs and original source model trace; fix actual fails and rerun until verified independent feature/PR CI; record measured count/rollback outcomes and scientific coverage without weakening constraints. Obtain model-bound high-valence sheet review before designing physical shared-node ownership or atomic `Patch` observer transaction.


## 2026-11-13-79 — Full original per-patch QUAD/AFT source owner engineering gate exact independent double CI green; candidate inventories receipt queued

**Audit and source:** Read live `main`, `quad-templates`, research PR #214, source `e43979013cc402804675edbdf9d9ebba5df6d59b`, AGENTS and mandatory research continuation/state/roadmap/session protocol. Source code/test/build artifact files from session 78 were unchanged during qualification. Full native QUAD/AFT disconnected physical owners for original Eistute 4 and Book 28 Bézier source charts use reference fixed 16-sided UV chart boundaries, actual original Quadtree QUAD interior and owned AFT exterior TRI, `Parameterize` XYZ and source normals, typed physical elements, check chart-local reverse observer identity, original boundary samples, facet orientations and pre-publication failure rollback with previously accepted physical chart pointer preservation.

**Measured independently:** [push #43397303113](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43397303113) and [PR #43397311631](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43397311631) COMPLETED all 4/4 jobs SUCCESS on exact identical source SHA `e4397901`. Both Linux root logs state **89/89 CTest PASS** including the new `quad.r2c2.full_source_patch_stage` #74 (0.21s push / 0.25s PR), Python tooling **527/527 PASS**, native Linux GCC QUAD **16/16** and Windows MSVC QUAD **16/16**, unchanged frozen original Eistute/Book TRI parity PASS, R2c0 **376 adjacency/38 negative** controls PASS, R2c1 **376 adjacency/98 negative** controls PASS. Both verbose R2b2 source reports admit original Eistute **4/4** and Book **28/28** patch-local native AFT UV/XYZ mappings, **0 rejections**. No claim of physical interpatch continuity, all-model source adaptation or source sheet approval.

**Follow-up remote CI instrumentation:** To obtain **measured** physical source chart inventory counts rather than guessing from per-patch samples, added one `ctest --verbose` receipt and 14-day artifact upload for new full-source stage in `.github/workflows/quad-research-validation.yml` on feature. An intermediate `17d8a273` edit accidentally interpreted regex text `$'` via JavaScript string replacement and duplicated workflow YAML; [intermediate push #43398913350](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43398913350) FAILED with invalid workflow. Re-read complete last green workflow, corrected via literal replacement callback and verified exactly one baseline/test/receipt set, final feature workflow-only SHA `9360196fec8790e0cb7ddec42714b2717919530a`. [New workflow CI #43398974425](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43398974425) was queued; **DO NOT claim this newer SHA passed or that original physical node, QUAD or TRI totals were measured yet**. Exact earlier e439 double green remains valid for its own source SHA.

**Scope and unresolved scientific gates:** Source and original TRI production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. PR #214 DRAFT/UNMERGED. No global physical conformity, shared-node ownership, `Patch` forward/back rebind, source `Adapter::AdaptCurve` on fully synchronized interpatch curves, local ASan/UBSan, Ribbed Bracket valence-3 source proof or historical 1993 point/contour approvals. Real original Eistute valence-4 and Book valence-28 sheet junctions remain independent scientific advisor decisions. [Updated scoped evidence](evidence/R2C2_FULL_SOURCE_AFT_STAGE_20261113.json).

**Next:** Read exact `9360196f` push and PR CI plus retained verbose output, parse real `R2C2_FULL_SOURCE_AFT` markers by original model, update receipt and state. If errors occur, fix without altering original scientific gates or suppressing failed tests.


## 2026-11-13-80 — Exact physical model candidate totals certified; read-only original source-ordered QUAD/AFT boundary node audit implemented and pending CI

**Latest validated source head:** `9360196fec8790e0cb7ddec42714b2717919530a` independently passed all 4/4 jobs on [feature push #43398974425](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43398974425) and [PR #43399166024](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43399166024): Linux root **89/89 CTest**, Python **527/527**, native GCC and MSVC QUAD **16/16** each, historical original TRI equality PASS, R2c0 **38** rejected policy controls and R2c1 **98** rejected controls retained. The verbose full original native source owner CTest #74/89 printed **Eistute 4 patches/164 separate nodes/64 typed QUAD/128 typed TRI, 3 rejected injected stages** and **Book 28 patches/1932 nodes/1176 QUAD/1008 TRI, 3 rejected stages** in BOTH independent root logs. Aggregate 32 isolated patch-owned charts, 2096 nodes, 1240 QUAD + 1136 TRI. These are *per-patch* bounded source UV quarter-sampled native QUAD/AFT outputs; zero physical interpatch node ownership or joined model claims. Exact [push artifact](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43398974425/artifacts/14023779747) and [PR artifact](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43399166024/artifacts/14024912145); evidence [R2C2 full original physical source](evidence/R2C2_FULL_SOURCE_AFT_STAGE_20261113.json) updated.

**New one-work-item research probe:** Feature branch `quad/integration-r2b2-exterior-aft-20261112` now at `74a04b289a08a91ba0e7f26b234c7ba13ccab014`. Expanded the existing `tests/quad/full_source_patch_stage_probe.cpp`, not production code. For each actual typed `SubMesh` built from existing native QUAD/AFT interior/exterior research output, demand five original quarter-parameter physical nodes on every source patch side; copy `NodeAdaptive` xyz and pointer after staging, translate `PatchBezier::IsCurveReversed` to canonical original `CurveAdaptiveParametric` parameter order, assert source-coordinate agreement, group by original shared source `CurveAdaptiveParametric*` identity, compare every original source-order knot between distinct patch owners without node aliasing or topology assignment, and enforce valence 4 and 28 high-valence graph expected maxima. Four adversarial snapshot-only controls per source model: distorted physical site, absent node, null original curve, forged cross-patch pointer alias. No CMake or source inventory changes needed because the existing required root test was extended. Exact new [push #43427687327](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43427687327) and [PR #43427695306](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43427695306) were queued at update; new numerical and regression results are **NOT VERIFIED**. [Pending knot audit evidence](evidence/R2C2_SOURCE_CURVE_SITES_20261113.json).

**Scope and handoff:** This is a finite read-only comparison of original patch-local source quarter sites, *not* original dynamically adapted shared curve knot or full interval equivalence; no sheet/junction semantics, global welding, cross-patch `SubMesh`, original source historical 1993 point policy, or production `quad_uv`. Original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, default TRI and PR #214 draft/unmerged remain unchanged. No local C++ build or ASan/UBSan; GitHub Actions native runs furnish remote compiler evidence only.

**Next:** Inspect new exact-head native root logs and `R2C2_SOURCE_CURVE_SITES` measured counts; remedy actual failures while preserving strict negative controls and existing original source oracles; after qualifying source-bound sampling, separately design original `Adapter::AdaptCurve` interval synchronization and obtain external model-SHA-bound advisor scientific decisions before any global physical owner/observer publication.


## 2026-11-13-81 — Real source site oracle double CI qualified; native original two-pass high-valence AdaptCurve interval preflight implemented

**Remote baseline:** Rechecked live `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, canonical `quad-templates` research state, feature PR #214 head `74a04b28` and both completed exact native runs. The source-bound real physical QUAD/AFT site gate was **independently 4/4 SUCCESS on both [push #43427687327](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43427687327) and [PR #43427695306](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43427695306)**: Linux root **89/89 CTests**, Python **527/527**, native GCC and MSVC QUAD **16/16** each, unchanged source Eistute/Book TRI. Original source Eistute source incidence **16, physical source sites 80, shared pairwise checks 30, max valence 4, 4 snapshot faults rejected**; Book **112, 560, 1890, max valence 28, 4 rejected**. Complete previous disconnected original typed physical QUAD/AFT inventory unaffected: Eistute **164 nodes/64 QUAD/128 TRI** and Book **1932 nodes/1176 QUAD/1008 TRI**. [Source site evidence](evidence/R2C2_SOURCE_CURVE_SITES_20261113.json).

**Implementation:** On draft PR #214 added original high-valence source curve research fixture in the **existing test** `tests/quad/full_source_patch_stage_probe.cpp`, first source commit `7eaab1d494060973f5867b5960ed6f14036fcfb9`, then `85c4c7816eac32da21c18ab323a16740081cb219` with required original serial `ptr_aux` comparator scratch guard. The new step runs after qualified detached QUAD/AFT full-source checks and uses an independent `Geometry`, original `PatchReader`, existing coarse TRI `BuildInitialSubMesh` and its accepted patch observers, original two-pass `Adapter::AdaptCurveByCurve` + `Adapter::AdaptCurveBySurface` through existing `RefineCurveSamples` on precisely the original shared curve of valence 4/28. It snapshots the actual emitted source `CurveAdaptiveParametric` parameter/node graph, requires a genuinely refined partition (more than endpoints) with ordered finite parameters and nonduplicate physical IDs, matches EVERY resultant source-curve node to EVERY incident `PatchBezier` physical boundary using source orientation, preserves original coarse `Patch` observers and rejects 5 source-snapshot mutations (distorted XYZ, missing site, order swap, forged node ID, altered parameter) per original model. The fixture retires displaced coarse initial samples only after checking other original curve aliases; source graph lifetime is bounded. This is a **new attempted research native source-curve gate**, not the previously certified five-sample physical per-patch seam gate.

**Exact verification pending:** New [push #43431223035](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431223035) and [PR #43431234321](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431234321) run exact `85c4c781` source; GCC Linux and MSVC Windows native QUAD **reported successful** but full root Linux compiler/CTests and original new R2C3 marker remained pending when recorded. Intermediate prior code SHA `7eaab1d4` workflow runs were canceled after follow-up fix, not qualified. No local C++/ASan/UBSan run. [New pending evidence](evidence/R2C3_NATIVE_ADAPTER_SOURCE_INTERVALS_20261113.json).

**Boundary:** `GeneratorAdaptive::AdaptCurve` is the orchestrator; actual serial primitive names are `Adapter::AdaptCurveByCurve` and `Adapter::AdaptCurveBySurface`. One real source-curve graph is reused by all incident patches; matching this graph is *not* independent patch physical seam refinement, all source curves in one accepted epoch, high-valence advisor-approved sheet continuity, node welding, cross-patch physical adjacency, global publication or original 1993 point selection. No production generator/adapter/CLI/source CMake changes. PR remains draft, main unchanged.

**Next:** Inspect exact `85c4c781` source compiler and native test logs. On any failure diagnose and fix without relaxing source/adaptive geometry oracle; then repeat independent exact-head CI. Retain actual original adapted interval counts per model and explore source-driven *detached* QUAD/AFT boundary generation only after this new gate, while cross-patch physical publication remains scientifically gated.


## 2026-11-13-82 — Native original R2c3 high-valence source curve intervals: exact double CI qualified, physical seam mismatch identified

**Source and exact checks:** [Research draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) new C++ experimental source `85c4c7816eac32da21c18ab323a16740081cb219` was verified with two distinct fully completed GitHub-hosted workflows: [feature push #43431223035](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431223035) and [PR #43431234321](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431234321), exact same source SHA, **4/4 success jobs in both**, Linux root **89/89** CTests, Python **527/527**, Linux native GCC and Windows native MSVC QUAD **16/16** each, strict frozen original Eistute/Book TRI parity PASS. Actual verbose root logs on BOTH independent runs state precisely:
- `R2C3_NATIVE_ADAPTER_SOURCE_INTERVALS original_patches=4 original_shared_source_curves=1 source_sites=7 source_intervals=6 original_source_incidences=4 complete_incidence_sites=28 complete_incidence_intervals=24 pairwise_incidence_comparisons=6 pairwise_interval_matches=36 rejected_negative_controls=5 adaptation=AdapterByCurve+AdapterBySurface original_submesh_observers_preserved=1 topology_sheet_approval=0 physical_cross_patch_welding=0 global_mesh_publication=0`
- `R2C3_NATIVE_ADAPTER_SOURCE_INTERVALS original_patches=28 original_shared_source_curves=1 source_sites=7 source_intervals=6 original_source_incidences=28 complete_incidence_sites=196 complete_incidence_intervals=168 pairwise_incidence_comparisons=378 pairwise_interval_matches=2268 rejected_negative_controls=5 adaptation=AdapterByCurve+AdapterBySurface original_submesh_observers_preserved=1 topology_sheet_approval=0 physical_cross_patch_welding=0 global_mesh_publication=0`

**Engineering scope:** Used actual original `PatchReader` source geometry, original serial `BuildInitialSubMesh` TRI source initialization on the separate model, original actual `Adapter::AdaptCurveByCurve` and `Adapter::AdaptCurveBySurface` through existing `RefineCurveSamples` on the **single original shared maximal-valence curve per model** (not all original curves). Tested strictly ordered finite original source parameters, authentic source `NodeAdaptive` IDs/XYZ and all input original `PatchBezier` side parameter maps, distinct interval coverage across all incident original patches, and rejected five malformed source graph snapshots per model. Maintained accepted initial `Patch` observers; did not link QUAD into production. The native test source now lives in `tests/quad/full_source_patch_stage_probe.cpp`, appended under existing CTest `quad.r2c2.full_source_patch_stage`, and emitted a separately named `R2C3` source evidence marker. [Qualified evidence](evidence/R2C3_NATIVE_ADAPTER_SOURCE_INTERVALS_20261113.json).

**Scientific comparison uncovered:** The previously qualified detached per-patch mixed QUAD/AFT research physical meshes used **fixed 16 edges on a chart, four segments per side**; the original two-pass serial **shared source curve chose SIX intervals**, with endpoints as 7 shared source nodes. The prior four-quarter physical border cannot be admitted as actually synchronized with this dynamic source partition, regardless of five quarter-source geometric matches. Since every original patch incidence references one original source CurveAdaptive object, matching those source-curve samples does not establish independent **physical** QUAD/AFT boundary identities, sheet/weld decisions, or model-wide coherent accepted adaptivity. Our scientific gate remains **UNAPPROVED** for Eistute valence 4, Book valence 28 and original `GeneratorAdaptive::AdaptCurve` across every source curve in one accepted epoch. No original 1993 algorithm reconstruction, sanitizer or global physical output was claimed.

**Next finite engineering step:** Preserve research-only isolation and build actual detached native `AFT::Boundary` from the genuine generated source sample parameter lists on every incident high-valence original `PatchBezier`. Check source-oriented order, directed UV edges, full source interval correspondence, Bézier XYZ at every adapted knot, original source curve metadata, and negative mutation tests; no QUAD full interior, shared physical node owner, physical interpatch sheet topology or `Patch` forward observer publication. Then exact two independent source CI tests before further admission. Original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged, PR draft/unmerged; local ASan/UBSan still not run.


## 2026-11-13-83 — Original two-pass source-driven disjoint native AFT Boundary contour research stage implemented; exact native CI in flight

**Verified beginning:** Checked remote `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, research base `quad-templates=0772805f` before this checkpoint, feature `85c4c781`, open draft PR #214. Previous original Eistute 4 and Book 28 maximal-valence source curve interval gate had independently completed 4/4 SUCCESS on [push #43431223035](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431223035) and [PR #43431234321](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43431234321), Linux root 89/89 CTest, 527/527 Python, GCC/MSVC QUAD 16/16, frozen source TRI parity; original serial `Adapter::AdaptCurveByCurve` + `Adapter::AdaptCurveBySurface` produces seven real source curve nodes/six intervals for each model's single highest-valence curve. Prior detached full QUAD/AFT per-patch staging and fixed quarter-site comparisons remain separate proven engineering gates.

**New experimental implementation:** Committed test-only source `4258dbca7131427e22220fa190391af6810411ab` on existing research draft PR branch. In `tests/quad/full_source_patch_stage_probe.cpp`, after original source two-pass `Adapter` and original coarse TRI patch initialization, build for each original incidence independently owned genuine `AFT::Boundary` using the exact ordered `CurveAdaptiveParametric::parameters_` and original PatchBezier `IsCurveReversed`, original native source edge curve/reversal metadata, physical `NodeAdaptive` copies owned separately per detached contour, and `Boundary::close`. Validate `SnapshotOriginalAdapterBoundary` source-oriented full original node/parameter/XYZ/curve endpoint metadata, all real native directed edge/corner closures, normalized arc length/midpoint, positive chart UV area, `SnapshotSharedCurveSide` and pairwise `CompareSharedCurveSides` with original IDs/parameters/geometry for all 4/28 radial incidences, seven altered-capture negative controls per original model, and preservation of prior accepted original coarse TRI `Patch` observer pointers. Three other nonadapted sides remain coarse; expected **9 vertices/9 native directed edges per original patch**, expected Eistute **4 contours, 36 edges, 24 actual adaptive high-valence source edges** and Book **28 contours, 252 edges, 168 adaptive source edges**, if actually proven by new CI. No `Quadtree` templates or `AttemptExteriorTriangulation` are applied to the adapted source contour yet. No production code or CMake changed.

**Pending exact gates:** [Feature push run #43439921989](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439921989) and [PR #43439932294](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439932294) launched for exact same feature `4258dbca`. At first checkpoint both native Linux QUAD passed; root main Linux build/CTest and Windows MSVC/science checks were in progress. Do **not** count proposed source-contour metrics, rejected mutations or exact SHA compiled green before reading both native root logs. [Provisional evidence](evidence/R2C3_DETACHED_ADAPTED_AFT_BOUNDARIES_20261113.json).

**Separation:** Source adaptation covers only the one maximal-valence shared curve per original geometry, not all original curves or coherent original generation epochs. No scientific nonmanifold valence 4/28 sheet approval, shared physical nodes, cross-patch QUAD/TRI weld, forward/back `Patch` transaction, production `quad_uv`, historical 1993 algorithm, local ASan/UBSan or integration to `main`. Unrelated TRI production and modernization remain unchanged; feature PR remains draft.

**Next:** Inspect exact `4258dbca` compilation and `R2C3_NATIVE_ADAPTED_AFT_BOUNDARIES` source CTest output; fix compile/science failures without weakening source constraints; record native measured counts/CI on exact fully green push+PR before any interior QUAD/AFT source-driven mesh attempt.


## 2026-11-13-84 — Original native detached source-adapted AFT Boundary engineering gate exact independent double CI qualified

**Exact original code identity and two independent measurements:** Research-only `tests/quad/full_source_patch_stage_probe.cpp` feature commit **`4258dbca7131427e22220fa190391af6810411ab`**, draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), compared with `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` unchanged. Verified TWO fully complete GitHub Actions runs on exact same feature SHA: [push #43439921989](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439921989), [PR #43439932294](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439932294). Both **4/4 completed SUCCESS**, root Linux **89/89 CTests** with `quad.r2c2.full_source_patch_stage` #74 pass (0.20s push, 0.24s PR), Python **527/527**, QUAD GCC Linux **16/16**, QUAD MSVC Windows **16/16**, frozen original Eistute/Book TRI scientific equality PASS. All `R2C3_NATIVE_ADAPTED_AFT_BOUNDARIES` source markers are identical in both verbose native original model root logs, archived as [push native receipt](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439921989/artifacts/14046021014) and [independent PR native receipt](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439932294/artifacts/14044284605).

**Actual measured original models:** `R2C3_NATIVE_ADAPTED_AFT_BOUNDARIES` Eistute original_patches=4, detached_boundary_owners=4, native_owned_vertices=36, native_directed_edges=36, adapted_source_edges=24, canonical_source_site_checks=28, shared_incidence_pairs=6, cross_patch_source_site_pairs=42, cross_patch_source_interval_pairs=36, rejected_negative_snapshots=7; Book original_patches=28, detached_boundary_owners=28, native_owned_vertices=252, native_directed_edges=252, adapted_source_edges=168, canonical_source_site_checks=196, shared_incidence_pairs=378, cross_patch_source_site_pairs=2646, cross_patch_source_interval_pairs=2268, rejected_negative_snapshots=7. All original model source outcomes exactly matched between the two root runs; each group reports actual_source_Adapter_partition=1, untouched_source_sides_coarse=1, native_Boundary_closed=1, native_curved_edge_metrics=1, physical_node_copy_owners_disjoint=1, native_AFT_triangulation_executed=0, quadtree_quad_templates_executed=0, globally_welded=0, patch_observers_rebound=0, advisor_sheet_approved=0. **32 disjoint native contours**, 288 native directed edges/copy-owned 3D source site records, 192 genuinely adapted original common-curve incidence edges, **14/14 rejected negative snapshots**. No new full model-wide QUAD/TRI physical mesh is represented by these contour counters.

**Actual new test operations:** Separately owned original `PatchReader` geometries, untouched original `BuildInitialSubMesh` initial TRI acceptance and one fully qualified real serial `Adapter::AdaptCurveByCurve`+ `Adapter::AdaptCurveBySurface` source partition on the original maximal-valence shared curve of each model. Native `AFT::Boundary` construction with all actual source parameter indices and `PatchBezier::IsCurveReversed` / native CCW side traversal, real `Boundary::addVertex/close` and `Edge::makeParamMid`, original source curved edge length, private `NodeAdaptive` XYZ/ID values, `SnapshotOriginalAdapterBoundary` and `SnapshotSharedCurveSide` to inspect original node IDs, native UV directed edges, corner source endpoint and all shared radial source interval pairings. Each original contour's other **three sides remain coarse**: six adapted high-valence intervals plus three unchanged single intervals. No `Quadtree` or QUAD/AFT physical meshing on the dynamic contour yet. The previous fixed 16-edge detached full QUAD/AFT source chart proof remains a separate qualified benchmark, **not** this 9-edge contour result.

**Negative and unresolved gates:** 7 independently mutated boundary capture fault controls on EACH original external model: copied XYZ distortion, source parameter distortion, source physical node ID mutation, original curve ID spoof, reversal mutation, source sample omission, original endpoint identity corruption. All rejected with original TRI Patch observers unchanged. However there is **NO** original model-SHA-bound Eistute valence-4/Book valence-28 nonmanifold sheet/continuation/node-owner scientific approval, no global physical shared nodes or weld, no coherent original `GeneratorAdaptive::AdaptCurve` accepted epoch covering all curves, no source-driven experimental QUAD interior/AFT exterior for the 9-edge source contour, no global `Patch` observer transaction, production `quad_uv` or native local ASan/UBSan. No code merged into main. [Measured original source contour evidence](evidence/R2C3_DETACHED_ADAPTED_AFT_BOUNDARIES_20261113.json).

**Next single engineering work item:** Build detached independent original native Quadtree per source-aligned adapted 9-edge `Boundary`, attempt experimental QUAD template interior and original AFT exterior using exactly these source intervals, retain original native contour and 3D physical facet provenance, fail closed on unsuitable template or interface mismatches. After exact push+PR CI, assess repeat/adaptation and owner lifetime separately; no physical global mesh/sheet pairing until science reviewed.


## 2026-11-13-85 — First bounded full mixed original source-driven QUAD/AFT physical chart experiment, exact CI pending

**Beginning:** Verified remote original production `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, research canonical `quad-templates=9ec682a32ba7e2ed48465392ec3a1bbf6a82875a` and draft unmerged PR #214 feature `4258dbca7131427e22220fa190391af6810411ab`. Previous original adapted native detached boundary milestone [push #43439921989](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439921989) and [PR #43439932294](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43439932294) each 4/4 SUCCESS with Linux 89/89 CTest, Python 527/527, GCC/MSVC native QUAD 16/16 and frozen source TRI parity. Its original 4/28 Eistute/Book **nine-edge disconnected `AFT::Boundary`** results represent actual 6-segment native serial source `Adapter` output on one maximal-valence shared curve, other three curve sides coarse, not whole-model synchrony.

**Implementation:** Research branch source commit `80f839e1a7b01fa36e8f2f82c86c5766629d742c` extends **only** existing native source CTest `tests/quad/full_source_patch_stage_probe.cpp`: introduce `MakeDynamicSourceTree` to transfer each actual native nine-edge `Boundary` owner to a completely disconnected 4×4-leaf Quadtree research fixture; build separate second original TRI template reference front, select experimental QUAD interior templates and seed existing `OwnedQuadAftFront` on the distinct native candidate owner, resolve all original curve boundary edges to live native quadtree cells and run original geometry/topology exterior AFT. Fail closed unless original source front is drained; UV QUAD/TRI positive, nonoverlapping with independent clipping test and equal unit boundary area; one original seam incidence TRI per QUAD seam edge; original source seam vertices retained; physical Bézier `Parameterize`, `Qu`, `Qv` oriented facet positive; finite positive normalized UV triangle quality; actual existing AFT source boundary vertices (including all six dynamic source segment starts) map to real mixed physical element nodes, not inserted placeholders. Build truly typed local `SubMesh` with original UV and `NodeAdaptive`XYZ/ID and research `QuadrilateralAdaptive` / original `TriangleAdaptive`; stage all 4 Eistute/28 Book as disjoint candidate `MeshAdaptive` owner, no cross-chart node alias or production original TRI Patch observer mutation. No production source, CLI, original source Adapter, CMake or `main` edited.

**Exact native CI:** Two new independent [feature push #43443545741](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443545741) and [PR #43443556635](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443556635) runs on source `80f839e1` launched. Native GCC/MSVC QUAD and frozen source TRI parity were already successful in BOTH runs, but the new root Linux native C++/CTest and source marker `R2C3_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT` remained **PENDING** when recorded. The new experiment may be rejected by real AFT or geometric tests; do not call this a positive global mixed mesh or fabricate charts/counters. [Pending evidence](evidence/R2C4_DYNAMIC_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT_20261113.json). No local sanitizer or independent Windows memory-safety test.

**Scientific limitations and next:** This fixture uses an explicitly research-built independently refined 4×4 Quadtree, NOT original `GeneratorAdaptive::AdaptDomain` accepted leaf hierarchy, no accepted whole-model original `Adapter::AdaptCurve` all-curve epoch, no high-valence original source sheet/junction/owner scientific approval (Eistute valence 4/Book valence 28), no global shared-nodes physical conformity, physical owner/observer rebinding, historical 1993 policy or production `quad_uv`. Next diagnose exact source C++ root and native R2c4 reports, fix any rejected source-driven patch rather than skipping or substituting fixed quarter sampling; after double green record actual dynamic original physical nodes/QUAD/TRI counts, local quality and source frontier closure, advance scientific disjoint physical interface only.


## 2026-11-13-86 — Two independently certified 4+28 full original source-adapted disconnected physical mixed QUAD/AFT meshes

**Exact source and verified independent native results:** Research-only feature `80f839e1a7b01fa36e8f2f82c86c5766629d742c` on draft unmerged [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) was tested by two independent exactly matching source head GitHub runs: [push #43443545741](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443545741) and [PR #43443556635](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443556635), **both 4/4 completed SUCCESS**, Linux root **89/89 CTests**, Python **527/527**, Linux GCC and Windows MSVC native QUAD **16/16** each, original historical Eistute/Book TRI scientific parity PASS. New required original CTest #74 `quad.r2c2.full_source_patch_stage` passed (push 0.22s, PR 0.23s). Both original model-specific source logs show the *same* `R2C3_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT` receipts:
- Eistute original 4/4 source patches: `disconnected_physical_charts=4 physical_nodes=136 typed_QUAD=64 typed_TRI=100 source_boundary_knot_checks=36 dynamic_curve_knot_checks=24 research_source_tree_leaves=64 original_AFT_boundary_edges=36 quad_aft_seam_edges=64 minimum_uv_triangle_quality=0.203771 minimum_physical_normal_alignment=0.423 all_fronts_drained=1 quad_tri_area_balance=1 positive_nonoverlapping_uv_faces=1 real_original_six_interval_curve_used=1 original_other_three_sides_coarse=1 original_tri_patch_observers_preserved=1 all_chart_physical_nodes_disjoint=1 global_physical_mesh_welded=0 scientific_sheet_owner_approved=0 production_quad_enabled=0`.
- Book original 28/28 source patches: `disconnected_physical_charts=28 physical_nodes=952 typed_QUAD=448 typed_TRI=700 source_boundary_knot_checks=252 dynamic_curve_knot_checks=168 research_source_tree_leaves=448 original_AFT_boundary_edges=252 quad_aft_seam_edges=448 minimum_uv_triangle_quality=0.203771 minimum_physical_normal_alignment=0.741053` and the same all-pass local scope/boundary/published flags.
- Combined **32 physical local candidate `SubMesh`** from original models, **1088 nonaliased physical nodes, 512 `QuadrilateralAdaptive` + 800 `TriangleAdaptive` = 1312 real physical elements**, **288** actual source model frontier node checks and **192** dynamic original source curve knot confirmations, 512 test Quadtree leaves / QUAD/AFT seam edges. Original fully drained front and non-overlap and physical normals confirmed for all patches, no rejected positive original per-patch candidates.

**Implementation and exact changed code:** Only `tests/quad/full_source_patch_stage_probe.cpp` changed in research feature branch. `MakeDynamicSourceTree` adopts actual original native `AFT::Boundary` constructed from real source `Adapter` two-pass six-interval original maximal valence common source curve (three other patch sides originally coarse), uses a new **research-only** native 4×4-leaf Quadtree; independent original reference TRI templates and `SnapshotLegacyFront` are compared against experimental original native selected QUAD template interface through `OwnedQuadAftFront::Seed`. Original native exterior AFT attempts both geometry/topology phases and must drain its front with zero rejected AFT edges, positive UV TRI/QUAD and exact within-chart UV area, independent positive-overlap clipping, one TRI directed incidence per seam and unmoved source seam nodes. `BuildDynamicAdaptedAftChart` inserts actual Bézier-evaluated `NodeAdaptive`, research `QuadrilateralAdaptive` and original `TriangleAdaptive` into typed `SubMesh`; source native contour knots are **checked for pre-existence in the emitted physical element node map**, not post-inserted as guessed vertices. Each element's UV positive normalized quality and 3D differential Jacobian normal alignment is checked, and all 32 chart nodes staged through a separate `DisjointOwnerStage`/research `MeshAdaptive` with original accepted coarse TRI `Patch` observers unchanged and all cross-patch node pointers distinct. [Exact original native CTest receipt](evidence/R2C4_DYNAMIC_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT_20261113.json), [push native artifact #14046343101](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443545741/artifacts/14046343101) and [independent PR artifact #14047831316](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443556635/artifacts/14047831316).

**Honest stage-closure audit:** Original R2c3 prior dynamic native source Boundary mutation controls (7/7 per model) and previous serial original source Adapter controls (5/5 per model), plus prior fixed-boundary `DisjointOwnerStage` 3/3 injected rollback cases per original model, retained/passed. New R2c4 mixed physical stage currently has strong *positive* source, UV, quality, owner and observer constraints; **independent new full-dynamic post-stage failure injection/rollback, accepted adaptive second epoch and native local ASan/UBSan have NOT been run**, nor any independent Windows memory checker. Source-adaptation on exactly one original high-valence shared curve (seven nodes/six intervals) is not original complete accepted `GeneratorAdaptive::AdaptCurve` all-curve epoch; the 4×4 test Quadtree is NOT original `GeneratorAdaptive::AdaptDomain` accepted hierarchy. No original scientific high-valence 4/28 sheet continuation/owner decision was inferred or approved. No cross-chart welded shared node, full conforming physical QUAD/TRI global mesh, production CLI `quad_uv` or original 1993 historical generator semantics were added. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, default TRI and draft/unmerged PR remained unchanged.

**Next action:** Add explicit deterministic dynamic candidate stage abort/retry/rollback preserving accepted previous owner plus original `Patch` observers, audit memory/provenance repeat and identify real all-original-curve source interval synchronization requirements. Request source-model-bytes-hash-bound advisor decisions for Eistute valence 4 / Book valence 28 prior to any global physical junction connection. Preserve research double-CI policy; never count this engineering trial as original globally conforming hybrid mesh.


## 2026-11-13-87 — Actual source-adapted mixed QUAD/AFT MeshAdaptive fault-injection and same-source owner repeat implemented

**Verified at start:** `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, `quad-templates=2bbc7022a84fda05f9efda5ce6ecbf4ed2e547b6` before the new canonical evidence/checkpoint, draft PR #214 feature `80f839e1a7b01fa36e8f2f82c86c5766629d742c` with [push #43443545741](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443545741) and [PR #43443556635](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43443556635) **both 4/4 success** on exact source, root Linux 89/89 CTest, tooling 527/527 Python, native QUAD GCC/MSVC 16/16 and source Eistute/Book TRI parity PASS. Qualified original-adapted full detached physical QUAD/AFT model counts remain Eistute 4/4 **136 nodes/64 QUAD/100 TRI**, Book 28/28 **952/448/700**, total 1088 physical nodes and 1312 elements, 6 source curve intervals per original high-valence incidence, no global physical connectivity. [R2c4 exact evidence](evidence/R2C4_DYNAMIC_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT_20261113.json).

**This session's one engineering implementation:** Feature commit `232e29741d069dd8f408b029cb8dd69ab66d3cee` added only tests in `tests/quad/full_source_patch_stage_probe.cpp`. It preserves the originally accepted **FULL actual** source-adapted physically typed mixed QUAD/AFT disconnected model `MeshAdaptive` owner, 4 original Eistute or 28 original Book source patches and all original coarse TRI `Patch` observers. `DynamicPhysicalFingerprint` records each real chart's ordered full node ID/XYZ and QUAD-vs-TRI element types. `StageDynamicOriginalPhysicalCharts` now constructs fresh real source-aligned original `AFT::Boundary`, independent 4×4 test-native `Quadtree`, experimental QUAD template and original exterior TRI AFT for **every** original source patch in each candidate attempt; three `DisjointOwnerStage::Replace` failure injections at slots 0, N/2 and N must reject without altering the already accepted owner root, every original accepted chart and its first physical node/element pointer, all initial node/element-kind values, all adapted source `NodeAdaptive` pointer identities/IDs/XYZ/parameters, or any original TRI `Patch` forward observer. A separately rebuilt but one-chart-incomplete genuine physical model must reject. One successful same-source full dynamic replacement must swap owner atomically, match the accepted model's original per-chart node/element-type fingerprints and keep all original source node and TRI `Patch` observers stable; no retired old node/element is accessed after success. Expected candidate fingerprint comparisons: Eistute **19** (5×4−1) and Book **139** (5×28−1) from three full failures, one incomplete model and one accepted full replacement, all generated on the **SAME original source adaptation epoch**, NOT a second genuine `Adapter` pass. All C++ symbols/comments/diagnostics are in English; no production files, CMake, source Adapter/Quadtree/AFT, TRI or main changed.

**Exact CI started, no success asserted until observed:** [feature push #43449485572](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449485572) and [independent PR #43449501542](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449501542) on exact source `232e2974`, each requires Linux root native CTest #74, tooling and frozen TRI parity, GCC Linux and MSVC Windows native QUAD. At first checkpoint GCC/MSVC native QUAD already passed both, TRI parity and Linux root remained pending; source gate marker `R2C4_DYNAMIC_PHYSICAL_STAGE_ROLLBACK` not yet verified. [Pending source evidence](evidence/R2C5_DYNAMIC_PHYSICAL_OWNER_ROLLBACK_20261113.json). Failed real physical stage tests block this milestone; do not weaken source/old-owner invariants to produce green checks.

**Scope:** No true second `GeneratorAdaptive::AdaptCurve` original all-source-curve epoch (same accepted source graph is reused), no originally accepted production `AdaptDomain` hierarchy, no scientific model-byte-hash-bound Eistute valence-4/Book valence-28 sheet continuity/ownership decision, no node welding or interpatch observer transaction, no original 1993 scientific algorithm, no production `quad_uv`, no local ASan/UBSan. PR is still DRAFT/UNMERGED into `quad-templates`, historical production `main` unchanged.

**Next:** Read exact root native CTest and new R2c5 receipts from both independent runs. Only if all original Eistute/Book full QUAD/AFT failed and successful replacement controls pass, qualify measured rollback counts. The next *distinct* research gate is complete original same-epoch all-curve `Adapter::AdaptCurve` synchronization and model-hash-bound advisor decisions for valence-4/28 sheet/physical node ownership.


## 2026-11-13-88 — Exact independently double qualified original source-driven physical QUAD/AFT stage failure rollback and same-source model owner retirement

**Source and independent run receipts:** Feature research source `232e29741d069dd8f408b029cb8dd69ab66d3cee` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) independently passed exact [push workflow #43449485572](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449485572) and [PR #43449501542](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449501542), **both fully completed SUCCESS with 4/4 jobs**. Both Linux main root **89/89 CTest PASS** including mandatory native `quad.r2c2.full_source_patch_stage` #74, tooling Python **527/527 PASS**, native GCC QUAD Linux **16/16**, native MSVC QUAD Windows **16/16**, historical TRI Eistute/Book scientific parity PASS. The two original model verbose source receipts `R2C4_DYNAMIC_PHYSICAL_STAGE_ROLLBACK` and physical `R2C3_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT` outputs **match exactly** across push/PR runs; [push retained source artifact #14050271379](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449485572/artifacts/14050271379), [independent PR source artifact #14050496422](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449501542/artifacts/14050496422).

**Actually measured original R2c5 rollback samples:**
- **Eistute** original_patches=4, genuine_physical_charts_per_complete_stage=4, rejected_injected_owner_faults=3, rejected_incomplete_stages=1, repeated_atomic_publications=1, deterministic_real_chart_comparisons=19, preserved_adapted_source_node_observers=7; all flags original_TRI_Patch_observers_preserved=1, previous_accepted_QUAD_TRI_owner_preserved_on_fault=1, previous_accepted_QUAD_TRI_nodes_preserved_on_fault=1, previous_accepted_QUAD_TRI_elements_preserved_on_fault=1, original_Adapter_source_graph_unchanged=1, original_Adapter_reexecuted=0, global_welding=0, patch_observer_transaction=0, advisor_sheet_approved=0.
- **Book** original_patches=28, genuine_physical_charts_per_complete_stage=28, rejected_injected_owner_faults=3, rejected_incomplete_stages=1, repeated_atomic_publications=1, deterministic_real_chart_comparisons=139, preserved_adapted_source_node_observers=7; all identical invariant flags.
- **Aggregate** original full Eistute/Book all **32** disconnected physical QUAD/AFT charts, accepted per generation **1088** physical nodes and **512 QUAD + 800 native AFT TRI** generated by real source-aligned nine-edge (6 actually adapted intervals+3 coarse segments) AFT contours, 8 deterministic failed new physical model candidate publications rejected (**6 complete injected owner faults + 2 incomplete candidates**), 2 complete repeated same-source physical owner swaps accepted, 158 original chart deterministic physical node ID/XYZ and element type equivalence comparisons, 14 original source node pointer/parameter/XYZ identity checks. Original initial chart root and first node/element pointer observers are never lost on failed publication; the retired model is not dereferenced after a successful swap. No original TRI Patch observer changed.

**Code / test / regression / ownership closure:** Only the existing research test `tests/quad/full_source_patch_stage_probe.cpp` changed on source feature `232e2974`; R2c5 extends the already-qualified R2c4 full physical typed `MeshAdaptive` on original Eistute/Book models with `DisjointOwnerStage` full-injection and real same-source owner retirement. All previously certified original source curve snapshot 5 negative controls and native AFT boundary capture 7 negative controls per model remain in the same passing native CTest, as do the historical fixed contour stage fault controls. R2c5 test snapshots original original source `NodeAdaptive` point IDs, physical XYZ, curve parameter values, retained live pointer identities and accepted TRI `Patch` observers, and compares deterministic full model chart node/element kinds after each rejected candidate. No synthetic QUAD/AFT proxy element substitution, skipped original patches, changed numerical tolerance, new production code, original algorithm point-selection change, released source owner before use or source scientific sheet pairing was admitted. [Measured exact evidence](evidence/R2C5_DYNAMIC_PHYSICAL_OWNER_ROLLBACK_20261113.json).

**Remaining scientific / engineering limitations:** A repeated physical-stage publication using the same `Adapter` source graph does **NOT** constitute a second real original `Adapter::AdaptCurveByCurve`+`AdaptCurveBySurface` source model adaptive epoch, nor a complete whole-model all-curve `GeneratorAdaptive::AdaptCurve` accepted epoch; only the unique maximal valence-4 Eistute and valence-28 Book original shared curves were dynamically adapted in this research fixture. The 4×4-leaf Quadtree per original patch is a test-created native owner, not the production accepted original `GeneratorAdaptive::AdaptDomain` hierarchy. Eistute 4 / Book 28 source byte-sha-bound original sheet/junction/physical node ownership advisor approvals are absent. No interpatch conforming physical node welding, source-to-global `Patch` observer transaction, complete same-epoch all original shared source boundary subdivision, original 1993 historical Delaunay rule qualification, accepted production `quad_uv` CLI, local ASan/UBSan or memory allocation denial qualification. `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` and default production TRI unchanged, PR #214 DRAFT/UNMERGED.

**Next action:** Separately implement an auditable whole-original-model **all source curves**, same-epoch two-pass serial `Adapter` graph on original Eistute/Book input, retaining full parametric and original source node identity / curve orientation / physical boundary segment provenance, plus independent model file byte hashes and advisor decisions on physical sheet connectivity at nonmanifold valence 4 and 28. Only progress to physical cross-patch adjacency after explicit scientific review. Require exact double native CI and native sanitizers for future qualifying steps.


## 2026-11-13-89 — One actual original all-source-curve two-pass Adapter graph sweep, original model Git blob provenance, exact CI pending

**Remote starting state:** Verified original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, `quad-templates=4048fa480da69126984ba6bb8970a5ae1e5a3777` before these session docs, draft PR #214 source `232e29741d069dd8f408b029cb8dd69ab66d3cee` and both independent R2c5 [push #43449485572](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449485572) / [PR #43449501542](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43449501542), exact-double-success 4/4 jobs with 89/89 root CTest, 527/527 Python, native GCC and MSVC QUAD 16/16 and frozen original TRI scientific parity. Qualified 32 disjoint physical original mixed QUAD/AFT charts (Eistute 136/64/100 nodes/QUAD/TRI, Book 952/448/700), 6 complete stage faults and 2 incomplete models rejected across both inputs, two atomic re-publications of genuine fully typed QUAD/AFT model owners on the same original source curve graph. This did NOT re-run all source `Adapter` curves.

**R2c6 implementation:** Research feature `1c8f0c82fbc89d73118ea00e0f6c2157c94e8a01` adds a **separately owned entire-original-model source graph fixture** to existing native original CTest `tests/quad/full_source_patch_stage_probe.cpp`. Its full Eistute and Book models are original `PatchReader` sources, model content Git blob SHA-1 IDs `6fa2f40e4270cccb6da140111953bbbcb69b0086` (Eistute) and `7e3338a4ebc43f0b3119b1cb6eda47e2ac205d14` (Book), NOT raw-byte SHA-256 nor scientific advisor signatures. Every original coarse TRI `SubMesh` and source two-endpoint `CurveAdaptiveParametric` is initialized by original `BuildInitialSubMesh`, and the actual shared source topology is independently `BuildSharedCurveTopology`-audited. The production entire-graph `CurveSampleGraphTransaction` encloses **every** original curve in one research epoch and uses original `Adapter::AdaptCurveByCurve` and `AdaptCurveBySurface` with production `RefineCurveSamples` on each curve, one shared original map and research factor 1.0 (no budget target rebuild). All real emitted original curve ordered parameters, physical source `NodeAdaptive` IDs/XYZ and true `FindPointByParameter` are checked against **every** incident original `PatchBezier::Parameterize` and `PatchBezier::IsCurveReversed` side, all original shared source curve groups undergo canonical parameter/node-ID/XYZ pairwise checks with same/opposite actual source traversal counts but no approval of high-valence sheet pairing. An adversarial first shared-group source node-ID pair mismatch is rejected, plus 6 snapshot corruptions (XYZ, parameter, physical ID, curve ID, reversal, missing endpoint), and all original TRI Patch observers must be untouched. Audit logs distinguish newly refined curves and any legitimate two-endpoint survivors rather than synthesizing intervals. This runs **after** existing R2c5 physical-source-only fixture on its *own* original Geometry, without altering previous original source/physics or production main.

**Exact testing and limitations:** New independent [push #43461405847](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461405847) and [PR #43461420478](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461420478) test source `1c8f0c82`; Ubuntu native QUAD GCC and Windows native QUAD MSVC succeeded by this checkpoint, Linux root CTest and original TRI scientific checks were pending. Do NOT claim R2c6 entire-model pass, actual curve/incident cardinalities or original curve sample counts until matching native root receipts and exact two independent CI success. [Pending new evidence](evidence/R2C6_WHOLE_ORIGINAL_MODEL_SOURCE_CURVES_20261113.json). No local native ASan/UBSan. No original production `GeneratorAdaptive::AdaptCurve` whole control policy computation, no all-curve source-adapted physical QUAD/AFT `SubMesh` output (previous 6+3 physical chart belongs to separate fixture), no genuine accepted production `GeneratorAdaptive::AdaptDomain` hierarchy, no full accepted original generator step/retry, no global mesh welding, no `Patch` cross-chart owner transaction. Eistute valence-4 and Book valence-28 source model-SHA-bound adviser scientific sheet/node ownership decisions still unapproved, historical 1993 point selection unqualified.

**Next:** Diagnose new exact Linux root C++ and native CTest outcomes. Qualify actual original model curve counts, per-incidence real 3D sample and original shared interval pairing in two independent CI logs without relaxing geometric or source ID oracles. Next distinct bounded engineering gate: all four original per-patch source sides dynamically represented in detached native `AFT::Boundary` and physical QUAD/AFT candidate chart rather than earlier high-valence-only 6+3 edge contour. No global physical connection before advisor approval.


## 2026-11-13-90 — Exact independent double CI original Eistute/Book 98-curve source graph transaction and model SHA-256 certification

**Independent exact source runs, no pending claim:** Research feature `1c8f0c82fbc89d73118ea00e0f6c2157c94e8a01` draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) passed BOTH completed exact GitHub Actions workflows [push #43461405847](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461405847) and [PR #43461420478](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461420478), **4/4 success each**, root Linux **89/89** CTests including mandatory native full original `quad.r2c2.full_source_patch_stage` #74, Python **527/527**, GCC Linux native QUAD **16/16**, Windows MSVC native QUAD **16/16**, original Eistute/Book frozen TRI science parity PASS. Both independent native logs reproduce EXACT original model `R2C6_WHOLE_ORIGINAL_MODEL_SOURCE_CURVES` summaries; [feature retained source log #14055514255](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461405847/artifacts/14055514255), [independent PR source log #14056708088](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43461420478/artifacts/14056708088).

**Original Eistute provenance and measured source graph:** Original `input_models/eistute2.fixed.bp` **2213 ASCII bytes**, exact model content Git blob SHA-1 `6fa2f40e4270cccb6da140111953bbbcb69b0086` and SHA-256 `fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f`; **4** original patches, **13 original source curves** all adapted by both true original serial Adapter passes in one graph transaction, **13 refined**, **115 real source points / 102 genuine original source parameter intervals**, **16 original curve/patch side incidences**, **136** source original Bézier site and **120** interval incidence comparisons; only one shared nonmanifold source group **valence 4**, **6** source incidence pairs with **42** pairwise same-source real nodes/**36** intervals, **6 same computed original chart traversals/zero opposite**, 7/7 source corruption controls rejected, all 4 original `Patch` coarse TRI observers unchanged.

**Original Book provenance and measured source graph:** Original `input_models/book_v7a.bp` **11577 ASCII bytes**, source Git blob SHA-1 `7e3338a4ebc43f0b3119b1cb6eda47e2ac205d14`, content SHA-256 `3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d`; **28** original patches, **85 original source curves** all adapted via both actual native serial Adapter passes in one graph transaction, **85 refined**, **747 real `NodeAdaptive` curve samples / 662 real original source parameter intervals**, **112** original patch curve-side incidences, **936** original Bézier site / **824** interval incidence comparisons, sole shared nonmanifold source curve **valence 28**, **378** original shared incidence pairs with **2646** real pairwise source sites and **2268** real source intervals, **378 same computed original traversal/zero opposite**, 7/7 corrupted snapshots rejected and all 28 original TRI Patch observers unchanged. Together 98/98 original curves, 862 real source samples, 764 source intervals, 128 incidence sides, 1072 original physical source site comparisons, 2304 pairwise original shared source interval comparisons, 14/14 deliberate negative controls rejected.

**Exact code and hash method:** The **only** feature change is the existing `tests/quad/full_source_patch_stage_probe.cpp`: separate original model fixture using original `PatchReader`, `BuildInitialSubMesh`, `BuildSharedCurveTopology`, a single original production `CurveSampleGraphTransaction` per input model, the original `Adapter::AdaptCurveByCurve`+ `AdaptCurveBySurface` on **every** curve with one shared cache through `RefineCurveSamples` (research factor 1.0, disabled target-count rebuild), then final accepted source graph sample and original source-oriented patch Bézier check, shared real NodeAdaptive ID/XYZ/parameter cross-incidence verification, seven corrupted snapshot controls and no `Patch` observer rebinding. Model SHA-256 values were calculated on exact retrieved original ASCII source bytes with a pure-JS SHA-256 function **verified against the standard 'abc' test vector**, and model Git blob IDs recorded separately. These content IDs are not scientific advisor sign-off. No source parameter was synthesized to force an expected count. Frozen production source and numeric curve policy were unchanged.

**Critical science finding and blocked gates:** The one original high-valence shared `CurveAdaptiveParametric` in each model has all original chart-side canonical traversal signs the **same** for all 6/378 incidence pairs, despite perfect shared source point/parameter/ID/XYZ matching. Without original SHA-256 model-bound Creto/Bento-approved sheet/junction/physical node ownership, source trace direction alone cannot establish `halfedge.twin`, sheet crossing, globally welded physical graph or meaningful nonmanifold element adjacency. The original `GeneratorAdaptive::AdaptCurve` production complete adaptation targets/budget/retry/acceptance were NOT executed; this is real original two-pass **research** source graph sweep, not production accepted generation step. R2c5 previous 32 disconnected physical QUAD/AFT `SubMesh` trials still use **one** maximal-valence source curve adapted per model and three original coarse sides; they are not re-certified as all-four-sides-adapted physical meshes here. No independent local ASan/UBSan, original 1993 point rule, native accepted production `GeneratorAdaptive::AdaptDomain` Quadtree, cross-patch physical node welding, global `Patch` observer transaction, or production `quad_uv`. Original `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` and default TRI unaffected; PR #214 draft/unmerged. [R2c6 exact source evidence](evidence/R2C6_WHOLE_ORIGINAL_MODEL_SOURCE_CURVES_20261113.json).

**Next one engineering work item R2c-7:** Generate separate true native original `AFT::Boundary` contour for each of 4 Eistute/28 Book original `PatchBezier` patches using the **complete actual curve source parameter sets on ALL FOUR sides**. Audit original patch-side traversal/reversal, all generated dynamic source nodes, corner source provenance and native curved AFT lengths/midpoints; require physically disjoint owner copies and fault controls, avoid the prior 6+3 mixed contour shortcut. Then assess whether original native QUAD interior + AFT exterior can close when all source sides adapt, without claiming global physical continuity or advisor-approved valence 4/28 sheet ownership.

## 2026-11-13-91 — Deferred visual benchmark provenance mapped; R2c-7 native all-sides contour source candidate committed (CI pending)

**Intent:** Preserve the two previously displayed image-search illustrations as deferred scientific candidate concepts without falsely treating the pictures as parametric CAD models, then continue exactly R2c-7 on the existing original Eistute/Book geometry and native AFT.

**Input intake:** Opened [GitHub issue #215](https://github.com/tiagosombrra/apmesh-modernization/issues/215): IMG-01 Eistute-like and IMG-02 book-like illustrative searches have no authenticated image asset owner, downloadable original parametric controls, copyright/reuse rights or experimentally established non-manifold edge/vertex topology. Identified potentially useful independent public CAD repositories (ABC CAD dataset and Tangency Labs CC0 model collection) but no actual admitted model ID, conversion or validation. The original `.bp` Eistute/Book already in `input_models/` remain the only active scientific source corpus; no models, frozen TRI baselines or source SHA changed. This issue is **deferred, not blocking R2c-7**.

**R2c-7 feature source:** On draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), exact latest feature commit `2d3198d78743c2bd18ab3598f2b85b9e64d17830` (initial implementation `351f6f00`, followed by a source-only escaped-log-marker fix) changed only `tests/quad/full_source_patch_stage_probe.cpp`. The previous detached original AFT contour path was preserved through a wrapper, while the internal experimental builder accepts the original source-adapted dynamic intervals from **all four** sides, retaining native curved edge/CCW checks and physically disjoint samples. Original whole-model graph fixture now audits 4/28 complete patch-contour candidates, every original source curve incidence, source ID/parameter/Bézier XYZ pairwise comparisons and original TRI patch observers without any global physical node merge. New explicit adversarial checks: corrupt actual copied physical Node ID (native capture must reject) and two value-only shared curve mismatches (node ID, physical XYZ). The code emits an `R2C7_ALL_SIDES_AFT_BOUNDARIES` receipt only after all existing original R2c-6 source checks and the new contour assertions pass.

**Qualification state:** This is **implemented, uncompiled/unqualified within the current chat**; no new successful numerical/cardinality counts are claimed. At checkpoint, GitHub Actions [PR run #43484928465](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43484928465) was in progress on `2d3198d7`, with root CTest/527 Python, Linux GCC/Windows MSVC native QUAD and historical TRI parity unverified. Local sanitizer, full production `GeneratorAdaptive::AdaptDomain`, actual all-four-sides physical QUAD+AFT chart generation, high-valence sheet science approval and production `quad_uv` remain open. The R2c-6 exact feature `1c8f0c82` retains its independent successful source certification, which is **not** transferable to R2c-7.

**Durable evidence:** [R2c-7 pending receipt](evidence/R2C7_ALL_SIDES_AFT_BOUNDARIES_20261113.json) committed on canonical `quad-templates`, and this append-only log plus [STATE.md](STATE.md) updated. No `main` changes.

**Next:** Read exact source/native CI job logs on run #43484928465; repair any demonstrated compile, model boundary, lifetime or numeric problems without changing scientific oracles. Require independent complete CI plus actual R2c-7 original Eistute/Book native receipts before declaring boundary construction qualified. Next physical milestone is disconnected QUAD+real AFT completion with all four adapted sides; scientific model-SHA-scoped valence-4/28 owner rules are separately pending advisor review.

## 2026-11-13-92 — R2c-7 exact native source 4/4 pass; R2c-8 first original fully adapted physical patch trial implemented, pending exact run

**Verified prior source head:** PR #214 started at R2c-7 research feature `2d3198d78743c2bd18ab3598f2b85b9e64d17830`. The independently retrieved actual [GitHub Actions #43484928465](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43484928465) completed 4/4 SUCCESS: root Linux 89/89 CTest including mandatory #74 original source, Python 527/527, QUAD native GCC/Linux 16/16, QUAD native MSVC/Windows 16/16, frozen original TRI scientific parity. Native CTest #74 includes real `R2C7_ALL_SIDES_AFT_BOUNDARIES` receipts: Eistute 4 original patches, 16 adapted sides, 120 native directed AFT edges/copy-owner physical nodes, 6 shared source incidence pairs, 42 compared source sites, 1 corrupted physical copy rejection + 2 corrupted shared source snapshots; Book 28 patches, 112 adapted sides, 824 native edges/owners, 378 shared pairs and 2646 site comparisons with identical 1+2 rejected negative controls. All original patch observers remained bound to original TRI. The strong historical R2c-6 source audits remain passing in this run. Only **one** complete source-exact workflow was verified, so independently repeated same-SHA gate stays open; source-boundary output is **not** an admitted physical QUAD/AFT model. [Measured single-run R2c7 evidence](evidence/R2C7_ALL_SIDES_AFT_BOUNDARIES_20261113.json).

**New research-only physical diagnostic:** Feature code commit `4a90acfe430c233e4df1a66ef2300a11c0674e83` on PR #214 modifies the existing original native probe only: `MakeDynamicSourceTree` accepts native AFT contour edges with measured variable cardinality instead of only the nine-edge old source; `BuildDynamicAdaptedAftChart` preserves the historical one-adapted-side validation by default and has a named all-four-sides diagnostic option. A new `TrialAllSidesPhysicalOriginalPatch` tries actual native original QUAD interior + exterior AFT triangulation and typed detached `SubMesh` on **original patch 0** in Eistute and Book. It checks disjoint native geometry and stable accepted TRI Patch observer and emits an explicit success (with physical node/QUAD/TRI counts) or original rejection reason; failures are reported as diagnostic blockers and not counted as accepted physical output. No other original source patches are claimed physically tested by this new trial, though all 32 R2c7 AFT contour audits still execute.

**Qualification:** New candidate GitHub Actions [#43489732391](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43489732391) was **IN PROGRESS** at this checkpoint; no new original R2c8 native output inspected yet. Source branch remains draft/unmerged, production main and TRI untouched. Local C++/ASan/UBSan unavailable in this session; connected GitHub runner is the only native evidence source. No actual production accepted `GeneratorAdaptive::AdaptDomain` / repeated adaptive epoch, global non-manifold sheet pairing, cross-patch physical node welding or original 1993 point-rule approval. Deferred illustrative benchmark provenance remains recorded separately as [#215](https://github.com/tiagosombrra/apmesh-modernization/issues/215), not active.

**Next:** Inspect CI run #43489732391 and original native R2c8 diagnostic markers. If the first-patch physical trial succeeds for both models, expand to entire 4+28 original patches; if it fails, localize the failure through exact native original contour/AFT/Quadtree logs, retaining all acceptance oracles and no synthetic source simplifications. Require independent complete CI before qualifying new engineering milestones.

## 2026-11-13-93 — First native all-four-sides original physical patch success in both models; expand to complete detached 4+28 patch model candidate

**Verified source and exact execution:** Draft research [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), head at start `4a90acfe430c233e4df1a66ef2300a11c0674e83`. Actually downloaded completed Linux root job log from exact [workflow #43489732391](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43489732391), full 4/4 SUCCESS (native GCC and MSVC QUAD 16/16 each, root 89/89 CTest, 527 Python, original Eistute/Book frozen TRI parity). Native original model marker R2C8_ALL_SIDES_PHYSICAL_FIRST_PATCH_TRIAL: Eistute patch 0 source all-four-sides physically valid = 1, 55 NodeAdaptive, 16 physical QuadrilateralAdaptive, 46 actual native AFT TriangleAdaptive; Book patch 0 physically valid = 1, 47 nodes, 16 quads, 38 native AFT tris. Original TRI Patch observers intact, disjoint source research chart and 4x4 independent research native tree, not original accepted production domain. The original R2c7 source-boundary audit still passes for all 4+28 patches and 944 dynamic edges. Earlier source R2c5 32 disjoint chart trial adapted only the central high-valence original curve and did not satisfy this new all-four-side condition. [Exact first-patch R2c8 evidence](evidence/R2C8_ALL_SIDES_FIRST_PATCH_PHYSICAL_TRIAL_20261113.json).

**Source implementation to expand only proven capability:** New feature commit `9ab25427e3c99adad92a6ce77ce4738afdf26cf1` extends only the original mandatory research test `tests/quad/full_source_patch_stage_probe.cpp` with `TrialWholeOriginalAllSidesPhysicalModel`, using the same original whole-graph all-curve Adapter two-pass transaction from R2c6 and original R2c7 native AFT contours. For every source patch of real Eistute (4) and Book (28), build two separately owned all-four-side original AFT contours, native source Quadtree QUAD + actual exterior AFT physical TRI, genuine typed SubMesh with source boundary/UV and 3D normal/positive triangle quality. Stage only complete owners via existing DisjointOwnerStage; reject first failing patch with source-native error, do not publish partial candidate, never share physical node owner across patches and never touch original coarse TRI Patch observers. Output has explicit `R2C9_ALL_ORIGINAL_PHYSICAL_CHARTS complete_disconnected_model` with candidate geometry counts, typed nodes/quads/tris, min UV quality and 3D normal alignment. **A workflow success without complete_disconnected_model=1 for both models does not prove model generation.**

**Qualification:** New exact [CI #43491499508](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43491499508) launched and IN PROGRESS. No remote original modelwide new receipt inspected at this checkpoint. [Pending R2c9 evidence](evidence/R2C9_ALL_ORIGINAL_PHYSICAL_CHARTS_20261113.json). No local build, WSL native sanitizer, second independent exact-source CI, accepted original GeneratorAdaptive::AdaptDomain, full original accepted repeat adaptation or global non-manifold physical node welding. Production main/TRI, original source files and numerical tolerances unchanged; PR still draft/unmerged.

**Next single work item:** Read native R2c9 exact original source audit. If both Eistute and Book complete all 32 patches, then design safe standalone export and quality/conformity visualization before any full-model scientific claim. If any source patch fails, preserve diagnostic rejection, isolate and fix exact original geometry boundary/Quadtree/AFT incompatibility using native evidence, not a coarse boundary shortcut.

## 2026-11-13-94 — Entire original Eistute + Book 32 detached typed physical QUAD/AFT charts generated by real all-four-sides-adapted source contour research test

**Native measurement:** Original experimental feature source `9ab25427e3c99adad92a6ce77ce4738afdf26cf1`, draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), exactly completed [Actions #43491499508](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43491499508) **4/4 SUCCESS**: root Linux **89/89 CTest**, 527 Python, GCC Linux native QUAD **16/16**, MSVC Windows QUAD **16/16**, frozen original production TRI Eistute/Book parity PASS. Independent readback of actual native root job CTest #74 receipt `R2C9_ALL_ORIGINAL_PHYSICAL_CHARTS` confirms **Eistute** original 4/4 physically generated disconnected charts, 220 local physical nodes, 64 typed QUAD, 184 actual exterior AFT TRI, 120 original adapted boundary source intervals, min positive UV triangle quality 0.462158 and min positive Bézier normal alignment 0.986877; **Book** 28/28 charts, 1524 physical nodes, 448 QUAD, 1272 exterior AFT TRI, 824 adapted original boundary sites, min UV triangle quality 0.67345 and normal alignment 0.997508. Combined 32 original patch physical owners, 1744 physical nodes, 512 QUAD/1456 TRI typed actual generated elements and 944 all-four-source-side adapted boundary edges; every original TRI Patch observer preserved. Previous real original R2c6/7 and first patch R2c8 native source contracts also passed. Evidence [R2c9 measured original model receipt](evidence/R2C9_ALL_ORIGINAL_PHYSICAL_CHARTS_20261113.json) records exact counts and source SHA.

**Qualification boundary:** These candidates are valid **for the measured local native detached physical chart scope** on the 4×4 original research Quadtree fixture, not production accepted AdaptDomain, global manifold/nonmanifold sheet pairing or fully approved scientific mesh. `complete_disconnected_model=1` means only 4/4 or 28/28 **independent** `SubMesh` owners atomically staged into a disconnected in-memory `MeshAdaptive` candidate; no full original model OBJ/mesh file was produced, persisted or uploaded by this step. `first_rejected_patch=0` in successful output is an unqualified placeholder that means no rejection when `complete_disconnected_model=1`. At exact source checkpoint one complete CI exists, not a second independently triggered identical-source CI; local native ASan/UBSan, exact original 1993 point rule, repeated accepted production adaptation, global interpatch shared physical nodes and advisor-reviewed original model SHA-bound valence-4/28 sheet/junction semantics remain open. Production main / default TRI, original model inputs, physical geometry/quality checks and frozen scientific oracles untouched; PR #214 stays draft/unmerged.

**Next single work item R2c-10:** Export the actually staged and qualified original detached physical QUAD/AFT charts from native research harness into reproducible artifacts with patch source IDs, node/quad/tri counts, model input SHA-256 and orientation. Validate artifacts independently against original R2c9 native counts and physical curve source boundary sample correspondence before scientific visual/quality inspection. Do not call an un-welded chart collection a global connected nonmanifold mesh or release a production `quad_uv` mode.

## 2026-11-13-95 — Original detached 4+28 all-sides-adapted physical QUAD/AFT OBJ export source plus independent source-count/face integrity verifier (new CI pending)

**Qualified predecessor:** Exact real R2c9 source `9ab25427e3c99adad92a6ce77ce4738afdf26cf1`, 4/4 native [Actions #43491499508](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43491499508), 89/89 root CTest, 527 Python, native GCC and MSVC QUAD 16/16, frozen original TRI parity PASS. Eistute 4/4 original all-adapted physically staged *disconnected* charts = 220 nodes, 64 QUAD/184 AFT TRI; Book 28/28 = 1524 nodes, 448 QUAD/1272 AFT TRI. No global crosspatch welding/semantics or production accepted adapted original Quadtree.

**R2c10 implemented source:** Draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) feature head `068a3ea8849a07e6ff7b861791cfbed53d64089f`. Existing research native test `tests/quad/full_source_patch_stage_probe.cpp` optionally consumes explicit `APMESH_QUAD_R2C10_EXPORT_DIR` and serializes only full accepted all-four original source-adapted detached 4/28 physical `MeshAdaptive` candidates into per-model OBJ files with unique local vertex indices and original Patch groups, plus JSON manifest of original expected SHA-256 provenance, grouped node/typed-element counts and explicit disconnected/scientifically-unapproved flags. New standalone verifier `tools/verify_r2c10_mesh_export.py` parses actual OBJ vertices and face records, checks finite physical coordinates, no foreign/duplicate vertex references, distinct patch index ranges, nonzero 3D area for TRI/QUAD constituents, exact original R2c9 native expected physical totals and per-patch manifest identity. Modified only QUAD-scoped read-only `.github/workflows/quad-research-validation.yml` to execute original mandatory native CTest with the optional export flag, run independent Python verification and retain 2 OBJ + 2 source manifests + verification JSON + original native log as a bounded GitHub artifact if and only if all pass. Existing original runtime TRI remains unaffected.

**Edit correction preserved rather than hidden:** Initial workflow insertion accidentally expanded the original workflow text inside a JavaScript string replacement containing literal shell regex `$'` (replacement-string suffix interpolation); branch workflow temporarily had invalid duplicated YAML. Explicitly corrected using original workflow blob at the prior exact feature commit and a callback replacement that prevents JS replacement interpolation. Final remote readback showed the new commands, original following jobs and original workflow size restored to original plus bounded step. The intermediate invalid commits are unqualified, never counted as validation. Current head must pass actual native CI.

**Measured qualification at checkpoint:** New exact [GitHub Actions #43494028352](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43494028352) launched and was executing. No successful R2c10 native or independent OBJ verifier run or downloadable Eistute/Book artifact has yet been confirmed. [Pending proof file](evidence/R2C10_EXPORTED_ORIGINAL_DETACHED_PHYSICAL_MESHES_20261113.json). No new local C++ build, native ASan/UBSan, real accepted production GeneratorAdaptive::AdaptDomain, source model-approved Eistute valence-4 / Book valence-28 sheet/junction/physical node owner decision, original 1993 scientific rule, global connected physical nonmanifold output, independent second CI, production `quad_uv` or source model changes.

**Next action:** Inspect exact source native CTest and `R2C10_DETACHED_ORIGINAL_MESH_EXPORT` Eistute/Book receipts, independent `R2C10_INDEPENDENT_OBJ_VERIFICATION` and upload artifact ID from CI #43494028352. If failures, diagnose actual compile/geometry/OBJ provenance issue without relaxing source/quality or frozen TRI contracts; only after verified artifact delivery may exported disconnected model meshes be described as available.

## 2026-11-13-96 — Original complete Eistute/Book detached physical OBJ confirmed; new original source/physical seam atlas candidate; M0–M9 status board introduced

**Exact R2c-10 closure:** Research feature `068a3ea8849a07e6ff7b861791cfbed53d64089f` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), [exact GitHub Actions #43494028352](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43494028352) 4/4 completed SUCCESS: root CTest 89/89, Python tooling 527/527, GCC Linux native QUAD 16/16, Windows MSVC QUAD 16/16 and frozen original Eistute/Book TRI parity pass. Actually retrieved full native Linux job logs, verified R2C10_DETACHED_ORIGINAL_MESH_EXPORT original Eistute 4 patch groups, 220 nodes, 64 physical QUAD, 184 AFT TRI and original Book 28 groups, 1524 nodes, 448 QUAD, 1272 AFT TRI; R2C10_INDEPENDENT_OBJ_VERIFICATION separately parsed exported OBJ/manifests and accepted all actual patch groups, ownership-disjoint OBJ indices, nonzero 3D face areas and exact typed original native counts. Actual bounded [GitHub downloadable artifact #14070503827](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43494028352/artifacts/14070503827) contains OBJ x2 + JSON and original log, retention 14 days. Exact persistent [evidence R2c10](evidence/R2C10_EXPORTED_ORIGINAL_DETACHED_PHYSICAL_MESHES_20261113.json) updated from pending to verified. No source geometry SHA-256 re-hash during this export, only prior SHA-256 original byte evidence cited.

**Next R2c-11 bounded implementation:** On same research PR #214, feature head `1fd693eb38732b6c01a638cbd97208a6e87f9905` adds actual source curve atlas to `tests/quad/full_source_patch_stage_probe.cpp` (not production), independent `tools/verify_r2c11_source_seam_atlas.py` and existing QUAD GitHub workflow. Exporter now records all real source curve IDs/node IDs/parameters/original source physical XYZ and all omitted native AFT terminal-corner records for every of 4×4 and 28×4 original patch boundary incidences, with index witness into physically typed original model OBJ. This atlas is not a graph of approved node sharing; each physical OBJ group remains independently owned. Independent checker rejects foreign physical owner/invalid 3D XYZ, unordered side parameters, missing terminal, any source group/source point cardinality change, and disagreement of original shared-source curve parameter/node ID/XYZ across Eistute 6 valence-4 and Book 378 valence-28 radial incidence pairs. Tests must report 13/85 original curves, 115/747 unique original source points, 136/936 patch-side source sites (with end corners); no synthetic adapted source subdivision admitted. New CI [#43495975211](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43495975211) was **running** at this checkpoint, so R2c-11 NOT yet qualified; [pending R2c11 evidence](evidence/R2C11_ORIGINAL_SOURCE_SEAM_ATLAS_20261113.json).

**Global status reporting:** Added [MILESTONE_STATUS.md](MILESTONE_STATUS.md) as a permanent global M0–M9 scorecard separate from chronological small R2c gates and linked it from current [STATE.md](STATE.md). M4/M5 original **patch-local** hybrid physical QUAD/AFT plus OBJ positive in exact native CI; M6 **source** graph proven, physically shared non-manifold high-valence sheet/junction/physical node approval absent; M7 accepted generator multi-epoch adaptation pending; M8 comparative scientific trials and M9 optional anisotropy not qualified. Do not invent a total completion percentage, confuse source coincidence with global model connectivity or claim exact source-valid CI rerun that was not observed. No accepted production `GeneratorAdaptive::AdaptDomain`, native local ASan/UBSan, original 1993 point rule, source-model-bound Creto/Bento sheet pairing, production `quad_uv`, merge to `main` or mutations of original input corpus.

**Next:** Inspect R2c-11 exact native original + independent Python source atlas validation with CI jobs and source-identical run/artifact IDs; on failure identify first mismatch without loosening source/physical/Tri controls. Publish the result only after log-based proof and update the scorecard/STATE in the next checkpoint.

## 2026-11-13-97 — R2c11 native original source atlas exported; independent checker rejected ambiguous curve-ID grouping; canonical Geometry registry index correction in CI

**Previous qualified milestone retained:** R2c-10 original physical Eistute 4/4 patches, Book 28/28, source-adapted all four sides and actual typed 512 QUAD + 1456 AFT TRI; separately owned 1744 OBJ physical nodes. Exact [CI #43494028352](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43494028352) 4/4 SUCCESS and downloadable [artifact #14070503827](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43494028352/artifacts/14070503827).

**New exact R2c-11 negative diagnosis:** Initial feature head `1fd693eb38732b6c01a638cbd97208a6e87f9905`, exact [Actions #43495975211](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43495975211), 3/4 completed success, Linux integrated job failed. Native original 89/89 root CTest and #74 actually passed, Eistute `R2C11_ORIGINAL_SOURCE_SEAM_ATLAS` exported 136 source incidence sites with 136 mapped real physical OBJ witnesses, Book 936/936, R2c10 independent OBJ verifier remained green and all frozen original TRI baseline/gcc/msvc QUAD jobs succeeded. The new independent Python atlas check **correctly refused** to assert all source curves because it was grouping on legacy `CurveAdaptiveParametric::GetId()` alone, not on the unique original `Geometry::GetCurve(index)` registry identity. Failure: `ValueError: The actual source atlas does not cover all original curves`. No valid R2c11 artifact or scientific closure exists from this workflow. This does not invalidate actual native R2c9/10 proven detached model output.

**Targeted correction on PR #214:** Commit `c0560df53d46c68a5eafa6e55ef7a5b8dda06d42` exports an additional original `Geometry` curve registry index 0..N−1 for every real source-site CSV row, preserving original curve ID, original NodeAdaptive ID, parameter and XYZ. Commit `c6a9cb25985af82293c89ede6ede10a11a353df8` changes only `tools/verify_r2c11_source_seam_atlas.py` to group original incidences by registry index, additionally enforce each curve's original legacy ID consistency *within the curve*, and retain all 13/85 original curve, 115/747 unique source node and 136/936 patch source-site cardinality checks plus shared valence-4/28 identity/XYZ/parameter checks. No case was marked passed by weakening numerical criteria, creating artificial original source nodes, altering original model input or crossing physical chart owners. Revised [exact CI #43497162260](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43497162260) launched and was in progress at checkpoint.

**Current scientific status:** R2c11 is **not yet qualified**; previous R2c10 models remain downloadable as **disconnected** research OBJ, not globally approved nonmanifold meshes. No original production `GeneratorAdaptive::AdaptDomain` epoch, merged `quad_uv`, native local sanitizers, second independent full same-source CI, original 1993 rule approval or model-SHA-256-bound Creto/Bento high-valence sheet/physical node policy. Global [M0–M9 status board](MILESTONE_STATUS.md) and evidence [R2c11 failed/retry](evidence/R2C11_ORIGINAL_SOURCE_SEAM_ATLAS_20261113.json) persisted.

**Next:** Observe corrected exact CTest and independent R2c11 audit results. Only if both original models recover true 13+85 registry curves, 115+747 original source points, 136+936 patch-side source incidences and 6+378 shared radial pairs with full physically disjoint OBJ witness verification can the atlas be called qualified. Inspect actual uploaded artifact ID; no guessed output.

## 2026-11-13-98 — Native R2c11 source/physical OBJ seam qualified; R2c12 pending SHA-bound scientific advisor packet

**Qualified predecessor R2c11:** Draft PR #214 source c6a9cb25985af82293c89ede6ede10a11a353df8, completed [exact CI #43497162260](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43497162260) 4/4 SUCCESS: root Linux 89/89 CTest, 527 Python, GCC/Linux native QUAD 16/16, MSVC/Windows native QUAD 16/16 and frozen original Eistute/Book TRI parity. Actual native original Atlas export and independent Python audit verified Eistute 4 original patches, 13 real Geometry curve objects, 115 unique source curve points, 136 real patch-side OBJ physical witnesses, 6 high-valence-4 shared incidence pairs/42 source site comparisons; Book 28 original patches, 85 real curves, 747 source points, 936 OBJ physical witnesses, 378 high-valence-28 shared pairs/2646 site checks. Disjoint ownership remained intact, no global halfedge twin/weld/admission. [Physical mesh and source atlas artifact #14073665054](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43497162260/artifacts/14073665054), [R2c11 evidence](evidence/R2C11_ORIGINAL_SOURCE_SEAM_ATLAS_20261113.json).

**Original source identifier ambiguity:** First independent R2c11 audit failed after the real C++ native test had passed because legacy CurveAdaptiveParametric::GetId values were repeated over all 13/85 original curves; this was not evidence of fewer curves. It was corrected without dropping any expected source node/curve/physical quality or original TRI acceptance criterion by additionally exporting the canonical Geometry registry index. Actual successful second feature source is not scientifically equivalent to approving node-sharing.

**New R2c12 source:** Candidate PR #214 commit e4bfa162aff72a7ded3b3d424739349a700ea723 adds research-only tools/build_r2c12_advisor_handoff.py, which combines actual original R2c0 signed radial interval records, original R2c1 read-only source-bound advisor packets (49 negative controls per model), original .bp content SHA-256 and R2c11 separately owned physical OBJ/atlas source witnesses. The new verifier checks true source model hash, the original model source curve registry index, all high-valence (patch, side) incidence members and packet SHA; emits no-weld scientific reviewer handoffs with null findings/ownership/halfedge-twin approvals and independent OBJ/CSV hashes. Original accepted GeneratorAdaptive radial source sampling had Eistute 10 and Book 12 source intervals; the separately adapted R2c11 physical source graph has independently sampled knots, so no identical-node/source-interval claim between epochs is made. The new workflow step is after the R2c1 source review and before regular tooling controls; it uploads bounded original scientific handoff JSON only when complete checks pass.

**Qualification status:** Exact [CI #43499503532](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43499503532) was launched and in progress at checkpoint, and no R2c12 packet is yet qualified. [R2c12 provisional evidence](evidence/R2C12_MODEL_BOUND_ADVISOR_HANDOFF_20261113.json). [Overall M0–M9 scorecard](MILESTONE_STATUS.md) now shows R2c11 qualified and R2c12 in progress. Production original TRI, main, input_models and PR draft status unchanged.

**Next:** Inspect exact source CTest and R2c12 packet builder CI output. If one original source registry or cross-epoch membership assumption fails, preserve the rejection, inspect model-bound source records and correct the adapter/source identity without lowering counts or inventing advisor approval. If green, publish exact artifact ID and organize Creto/Bento reviewer questions; global welding is still blocked.

## 2026-11-13-99 — R2c12 model-hash-bound external science review packet generated and qualified; M6 physical connectivity still blocked

**Completed original source CI:** Feature e4bfa162aff72a7ded3b3d424739349a700ea723, [CI #43499503532](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43499503532), 4/4 jobs success. Original Linux root 89/89 CTest; tooling 527 Python; GCC and MSVC native QUAD 16/16; frozen original Eistute and Book TRI scientific parity. New R2c12 scientific read-only handoff builder passed all source SHA-256, radial record signature/packet digest, physical seam atlas ID/patch-side and original physical OBJ SHA checks, emitted two JSON packets and manifest [artifact #14072853917](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43499503532/artifacts/14072853917), subject to 14-day retention. Original model Eistute SHA fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f; Book SHA 3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d.

**Precise measured central source identities:** Both original models' high-valence source curve has actual canonical `Geometry::GetCurve` registry index **3**; Eistute central source valence **4**, Book **28**. Original production `GeneratorAdaptive` radial source certificate has **10** and **12** source intervals, while the separately adapted physical research `Adapter` curves have **6** and **6**. Engineering validation does not imply equal knots or node IDs between these two original sampling scopes. The generated packet therefore keeps `cross_epoch_physical_node_identity_approved=false`, all reviewer decision fields null and all welding/twin/automatic sheet flags false. No scientific reviewer actually provided approval. The packet allows source-backed discussion with Creto/Bento, NOT publication of a single connected globally conforming non-manifold model.

**Persistent documentation:** [R2c12 evidence](evidence/R2C12_MODEL_BOUND_ADVISOR_HANDOFF_20261113.json) updated to PASS, [M0–M9 dashboard](MILESTONE_STATUS.md) revised, [R2c12 advisor review guide](R2C12_ADVISOR_REVIEW_GUIDE_20261113.md) linked, [STATE.md](STATE.md) now records verified gate and next engineering M7. Original inputs, default TRI production, scientific model hashes and main unchanged. Draft PR #214 not merged.

**Next bounded engineering task:** independently audit actual production `GeneratorAdaptive::AdaptCurve` and `AdaptDomain` two-accepted-epoch/retry hooks; devise a research-only acceptance/rollback proof using original Eistute/Book with full original curve budgets and safe ownership. A separate high-valence source-model- and advisor-approved physical sheet topology remains a prerequisite to any welding, not to read-only source-epoch investigation.

## 2026-11-13-100 — M7 original production GeneratorAdaptive two-accepted-epoch experiment implemented, CI pending

**Original behavior established from actual previous CI:** Original `quad.generator.real_global_outcomes` (Eistute) and `quad.generator.real_global_outcomes.book` (Book) native source through exact fully passed [R2c-12 CI #43499503532](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43499503532) yielded original serial TRI commits/rollback: Eistute accepted TRI **1** with **3 restored rejected** steps across 4 source outer epochs; Book accepted TRI **1** with **2 restored rejected** steps across 3 source outer epochs. This is NOT two accepted epochs and does not imply any accepted production QUAD/AFT mesh. Rejected source graph state is restored using `restore_curve_snapshots` and accepted mesh root with existing `AcceptedMeshScope`, and hooks emit `AcceptedStepCommitted` only after `Commit`. Previous original baseline is still frozen.

**New M7 read-only code:** Source feature `082ecd0408d31808dae5d629e711be99fd01d1a7` on draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) extends only `tests/quad/generator_outcome_probe.cpp` with original commit trace `R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS`: distinct monotone accepted source outer epoch IDs and real step numbers, actual complete original Adapter boundary coverage for every original 4/28 patch on each accepted commit. Rejected/retried steps are separately counted, never inflated as accepted. A research-only runner `tests/quad/test_r2c13_m7_accepted_epochs.py` invokes the same genuine source `GeneratorAdaptive` with original unmodified article profile and two explicitly marked profile sensitivity variations in isolated output directories, validates pinned Eistute/Book original model SHA-256 and actual per-accepted-step logs: original curve adaptation CSV (all 13/85 original source curves), patch adaptation CSV, acceptance log, original physical mesh incidence JSON. Reports whether each scenario produced >=2 source-confirmed accepted epochs; no scientific claim from successful green CI without the qualified specific marker. Profiles use actual original TRI acceptance criteria; no source or numerical tolerance modification.

**CI and gating:** New QUAD research workflow original native source diagnostic and bounded report artifact step added. Exact [new candidate CI #43502743922](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922) launched. At checkpoint native QUAD GCC/Linux and MSVC/Windows passed; root integrated CTest and frozen TRI equivalence still executing. Two accepted M7 epochs **not yet verified**. [R2c13 pending evidence](evidence/R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS_20261113.json). No production TRI, source data, original high-valence sheet policy, original 1993 point rule or globally connected physical QUAD code changed. Previous research R2c-12 model SHA-bound advisor packet certified, still no advisor approval.

**Next:** Inspect exact 43502743922 native root job and independently validated per-model actual accepted step receipts. If baseline or research profile has fewer than two, retain exact reject/commit details and do not promote the full M7 milestone. If any model passes two, separately qualify consistency, atomic rollback and repeated accepted source partition, with M6 sheet decision still unresolved.

## 2026-11-13-101 — R2c13 real original M7 accepted generator epoch diagnosis completed with negative two-epoch result

**Source and measured run:** Draft PR #214 feature 082ecd0408d31808dae5d629e711be99fd01d1a7, full exact [CI #43502743922](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922) completed 4/4 SUCCESS: GCC/Linux QUAD 16/16, MSVC/Windows QUAD 16/16, original Linux CTest 89/89 and Python tooling 527/527, frozen Eistute/Book TRI baseline parity. New original accepted `GeneratorAdaptive` epoch probe and Python scenario runner passed as *diagnostic* only; actual native `AcceptedStepCommitted` and accepted source curve, patch, acceptance and incidence file digests were matched. Original input SHA-256 verified without modification.

**Actual six scenarios:** Pinned Eistute 1 accepted source step and 3 restored rejected steps, pinned Book 1 accepted and 2 restored; original accepted step always numbered 1 with outer epoch 1 and full original 4/28 patch Adapter boundary coverage. Eistute stable-small-increment 1/3, research-debug-low-intensity 1/2. Book debug-low-intensity 1/2; Book stable-small-increment **zero original accepted** and strict research native probe exits 1, not falsely qualified. The original stable-small-increment Eistute source result is byte-for-byte same per accepted step as pinned original for available logs, so cannot be presented as a genuine altered accepted epoch. **No model reached two accepted original production source steps.** The generated JSON explicitly records `all_models_two_accepted_epochs=false`, `global_quad_aft_model_approved=false`. Actual report and original six stdout/stderr cases in [artifact #14074978033](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922/artifacts/14074978033). [R2c13 evidence](evidence/R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS_20261113.json).

**Real rejection numeric evidence from original logs:** Eistute initial error 0.285481; accepted step1 error 0.0620623 with 1168 elements; step2 candidate error 0.0775284 and growth 1.71918 rejected, step3 0.0746173 and growth 1.88014 rejected, step4 error improves sharply to 0.0100167 but growth 6.17808 and score -2.52902, original hybrid criterion rejects it. Book initial error 51.5505; accepted step1 error 42.1875 with 4256 elements; rejected steps 2/3 error 168.932 and growth 4.64615. Book stable-small alternative candidate steps 2–4 improve the initial error to 34.1271 but growth 7 and negative hybrid score cause all rejected. Original rollback retains previous accepted mesh and source curves, so fabricated commit/sheet approval is prohibited.

**Roadmap status:** M7 real original two accepted GeneratorAdaptive epochs is NOT CLOSED. The experiment's green CI proves observability and correctly rejects premature claims. M6 source radial atlas and R2c12 scientific reviewer packets are engineering qualified but scientific high-valence physical owner/weld approval absent. M4/M5 original disconnected 32-patch QUAD+AFT research physical geometry and OBJ remain qualified in their bounded scope. `main`, default TRI, source model bytes, original numerical admission thresholds, 1993 rule and production `quad_uv` unchanged. Canonical [STATE.md](STATE.md) session 101 and [M0–M9 board](MILESTONE_STATUS.md) updated.

**Next:** R2c14 independent source candidate failure forensics. Archive actual original rejected step acceptance logs and curve/patch adaptation CSV, calculate per-patch error regression and source budget/quality/overshoot metrics against actual accepted ancestor, keeping separate model configurations. A zero-accepted profile remains failure; do not relax original acceptance criteria to force 2 commits.

## 2026-11-13-102 — R2c14 original M7 rejected-candidate source forensics in CI, not yet accepted

**Exact prior measurement:** Original genuine `GeneratorAdaptive` accepted epoch C++ instrumentation and independently digested per-accepted-step source outputs passed full original [CI #43502743922](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922) 4/4. Eistute 1 accepted step and 3 restored rejections; Book 1 accepted and 2 restored rejections. None of six original model/config profile combinations produced two accepted original source epochs; Book stable-small alternative had zero accepted mesh. All `AcceptedStepCommitted` events followed the original accepted scope commit and covered actual all-patch Adapter witnesses. Baseline Eistute candidate 4 reduced original error sharply but was rejected by hybrid original criterion, growth factor 6.17808 and score -2.52902; Book candidate 2/3 increased error from 42.1875 to 168.932, growth 4.64615. R2c13 research result is valid **negative diagnostic**, not an M7 production-adaptive success. [Previous exact artifacts](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922/artifacts/14074978033); [evidence](evidence/R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS_20261113.json).

**Next source diagnostic code actually committed:** Draft research PR #214 feature `2a668414694070b4e74f826996cc5811df6fd0a8` adds pure read-only `tools/diagnose_r2c14_generator_rejections.py`, parses the six actual original GeneratorAdaptive source profiles' rejected acceptance logs and original per-patch/per-curve adaptation CSV. Requires source `accepted=0` for rejected steps and disjoint real prior accepted step IDs, complete 4/28 original patches and 13/85 source curves, numeric finite score/quality/error/growth/overshoot/coherence, compares actual rejected patch local errors against the previous original accepted step (if any), computes strongest local regressions, original curve target shortfalls and SHA-256 of raw native logs. Explicitly labels its inability to reconstruct every Boolean acceptance gate from aggregate logging; does not permit force-admission or any physical QUAD welding. Adds QUAD-only CI run step and bounded artifact of report plus original rejected and accepted native logs/CSV.

**CI and state:** Exact [Actions #43504972443](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443) launched; at checkpoint GCC/Linux and MSVC/Windows QUAD native success, original TRI frozen equivalence success, Linux integrated job compiling; no actual R2c14 original source forensic receipt inspected yet. [Pending R2c14 evidence](evidence/R2C14_ORIGINAL_GENERATOR_REJECTION_FORENSICS_20261113.json). [M0–M9 board](MILESTONE_STATUS.md) and [STATE.md](STATE.md) updated with explicit M7 failure rather than artificial percent complete. Production TRI, original models, original acceptance thresholds, point-selection scientific method and main untouched; PR remains draft.

**Next:** Read full CI R2c14 original candidate rejection audit; pinpoint model/patch source error and actual gate metrics. Any fixed original M7 acceptance must be achieved under a scientifically legitimate production policy and be proven by two distinct commits, intact original curves, accepted geometry, rollback and TRI parity. M6 high-valence globally connected physical sheet decisions remain independently pending.

## 2026-11-13-103 — Exact R2c14 native rejected-model forensic pass, source-stable R2c15 and bounded original source R2c16 in one CI

**R2c14 engineering qualification:** Draft PR #214 source `2a668414694070b4e74f826996cc5811df6fd0a8` completed exact [Actions #43504972443](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443) **4/4 SUCCESS**: root Linux 89/89 CTest; Python 527/527; GCC and MSVC native QUAD 16/16 each; original frozen TRI scientific parity unchanged. Collected and independently checked six actual original Eistute/Book source GeneratorAdaptive scenarios with [original source candidate and per-patch/curve CSV artifact #14077445183](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443/artifacts/14077445183). [Exact R2c14 evidence](evidence/R2C14_ORIGINAL_GENERATOR_REJECTION_FORENSICS_20261113.json).

**Measured original candidate failure scopes:** Eistute pinned article accepted 1168 elements then step2/3 generated 2008/2196 elements and had positive source structural `ok` in all 4 patches but global error rose ~24.9%/~20.2%; step4 generated 7216 elements from prior 1168, error improvement ~83.9% but **4/4 `curve_transition_needs_retry`**, underresolved transitions 4/4, global growth 6.178x and original stable transition penalty 2.067. Book pinned article 28/28 `degenerate_needs_retry` on steps2/3, from prior 4256 to 19774 TRI elements, global error rose ~300.4% and growth 4.646x. Original source status means the Adapter fallback conditions were not met; it is not independent proof of a physically degenerate triangle. Book stable alt generated 784 elements for ~114 global target on source step2/3 with 28/28 status `ok`, 6.863x overshoot despite error reduction. These are findings from authentic `_patch_adaptation_rejected.csv`, not fabricated model geometry or scientific acceptance. [Structural source diagnosis](R2C14_STRUCTURAL_SOURCE_DIAGNOSIS_20261113.md).

**R2c15 new actual code:** Pure read-only `tools/verify_r2c15_original_acceptance_guards.py` parses the original rejected source logs, verifies actual C++ `GeneratorAdaptive` source literals, distinguishes `adaptive_stable` (Eistute) from `research_debug` (Book article), and only attributes violations of source-evaluable necessary conjuncts for step2/step3+ stable overshoot/transition-coherence/transition-ready. It cannot infer the entire historical acceptance decision tree and never forces a source step to be accepted. Original feature CI [#43508097551](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43508097551) was **cancelled before R2c15 integrated checker executed** when a subsequent source commit advanced the same PR branch; QUAD GCC/MSVC and TRI frozen parity success on that cancelled run do not qualify the missing R2c15 gate. [R2c15 evidence](evidence/R2C15_ORIGINAL_GENERATOR_STABLE_GUARDS_20261113.json).

**R2c16 bounded experiments:** Four additional true original `GeneratorAdaptive` runs on source-hashed original Eistute/Book with explicit isolated research overrides. Eistute: only `CURVE_POINT_GROWTH_STEPN=1.5` or only `PATCH_QUADTREE_DEPTH_STEPN=3`; Book: `CURVE_POINT_GROWTH_STEPN=1.5` in original debug, or `ADAPTIVE_MODE=adaptive_stable` plus `PATCH_QUADTREE_DEPTH_STEPN=2` (two-knob sensitivity, **not** a univariate causal ablation). No original scientific accepted-step rules, model input, default TRI source or original presets are changed. Every scenario still needs two original committed source epochs with full original AdaptCurve/AdaptDomain boundary/curve/patch receipts to count as M7. [Protocol and pending evidence](evidence/R2C16_CONTROLLED_ORIGINAL_GENERATOR_SOURCE_PROFILES_20261113.json).

**Combined CI:** Exact source `797c2b39be3d0508a71ddd8234ad17a213373c23`, [GitHub Actions #43509163882](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43509163882) launched with both R2c15 and R2c16 test steps and separate bounded artifact retention. At this checkpoint 3/4 independent jobs (GCC/Linux QUAD, MSVC/Windows QUAD, original TRI science parity) passed; Linux root original compilation still running. **Do not claim R2c15/16 evidence until complete runner receipts and artifacts are verified.** [M0–M9 scorecard](MILESTONE_STATUS.md) and canonical [STATE.md](STATE.md) were updated to distinguish confirmed R2c14 diagnostic from provisional R2c15/16.

**Code-level next gate:** Native `Adapter::PatchNeedsFallback` can set `degenerate_needs_retry` for lower element count, AFT minimum quality, poor ratio, source curve/patch spacing imbalance, transition missing or low-score Quadtree templates. The research `_domain_adaptation.csv` log has the discriminating per-patch per-retry source measurements but was not archived by R2c14. [R2c17 design](R2C17_ADAPTER_FALLBACK_ROOT_CAUSE_PLAN_20261113.md) specifies preserving and auditing the existing original domain CSV before modifying any production source. M6 physical high-valence sheet owners and true globally welded QUAD/AFT remain independent scientific advisor decisions, not authorized by these M7 diagnostics.

## 2026-11-13-104 — R2c15/16 exact source diagnostic CI qualified; R2c17 original native Adapter fallback source audit pending

**R2c15 and R2c16 exact CI evidence:** Draft PR #214 feature `797c2b39be3d0508a71ddd8234ad17a213373c23`, [Actions #43509163882](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43509163882) **4/4 success**, original native root CTest 89/89, Python 527/527, QUAD GCC and MSVC native 16/16 each, frozen original scientific TRI parity PASS. The R2c15 original source-backed script checked literal `GeneratorAdaptive` stable-mode necessary guard inequalities against actual rejected candidate source logs, not just the CI result; the R2c16 model-bound bounded source sensitivity runner completed four original Geometry cases. [R2c15 certified evidence](evidence/R2C15_ORIGINAL_GENERATOR_STABLE_GUARDS_20261113.json), [R2c16 certified negative evidence](evidence/R2C16_CONTROLLED_ORIGINAL_GENERATOR_SOURCE_PROFILES_20261113.json). Bounded original source artifact [#14076444324](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43509163882/artifacts/14076444324) and controlled profile artifact [#14076394263](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43509163882/artifacts/14076394263).

**Exact original source stable guards:** Eistute article step2 fails `stable_step2_overshoot_ok`; step3 fails `stable_progressive_overshoot_ok`; step4 fails progressive overshoot **and** transition coherence **and** transition readiness. Book **original** profile is `research_debug`: it must NOT inherit Eistute `adaptive_stable` predicates. Book stable-small research step2/3 fails transition coherence; step4 fails transition coherence and progressive overshoot. The code reports only source-provable necessary-conjunct failures; it cannot reconstruct all hidden quality/acceptance booleans from aggregate logs. No source acceptance criteria changed.

**Four original R2c16 research profiles:** Eistute source-curve point growth stepN 1.5 => **1 original accepted step/3 restored**; Eistute Quadtree source stepN max depth 3 => **1/3**; Book research_debug point-growth stepN 1.5 => **1/2**; Book changed from research_debug to stable mode and Quadtree stepN max depth 2 => **1/3**. These are legitimate isolated research runs, not production changes. The final Book case is explicitly a **two-knob sensitivity**, not a claim of a one-variable causal ablation. No two accepted original generator source epochs demonstrated in any case, so M7 remains OPEN.

**New R2c17 candidate:** Source feature `c37d6ef8a76a59223469c8123c1de263832879e9` on PR #214 adds `tools/verify_r2c17_original_adapter_domain_fallback.py` and QUAD CI original local-domain log collection. Uses the native existing `Adapter::AppendDomainDebugLog` original `*_domain_adaptation.csv` rows (step, retry, original patch, local regen attempt, generation status, degenerate pre/post-AFT/smoothing counts, template scores, curve-domain balance, transition floor/underresolution and physical quality) to certify every original rejected selected patch status against real local source attempt evidence. Source C++ `PatchNeedsFallback` anchors and original model/profile settings are checked without altering legacy TRI. A `degenerate_needs_retry` label by itself does not assert truly degenerate 3D triangles; that must come from metrics. [R2c17 exact pending evidence](evidence/R2C17_ORIGINAL_ADAPTER_DOMAIN_FALLBACK_20261113.json); [CI #43510748191](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43510748191) launched. [Research protocol](R2C17_ADAPTER_FALLBACK_ROOT_CAUSE_PLAN_20261113.md).

**Overall plan:** [M0–M9 global scorecard](MILESTONE_STATUS.md) updated to mark measured R2c15/16 as qualified **diagnostics**, not original M7 two-accepted-epoch success. M4/M5 original disconnected 32-patch physical QUAD+AFT and OBJ/CSV witness validation remain qualified. M6 globally conforming nonmanifold sheet/junction policy for Eistute valence-4 and Book valence-28 remains scientific advisor approval pending; M7 full accepted source multi-epoch original adaptation not proven; M8 quantitative comparison and M9 optional anisotropy are separate. Original `.bp`, production TRI, main, frozen science, original historical 1993 rule and production QUAD disabled/unchanged.

**Next:** Read exact R2c17 native original fallback metrics. If checker fails on authentic source provenance, repair the checker without weakening source/quality or fabricating selected local candidate; if it passes, select one opt-in minimal original Adapter source-configuration/transition-smoothing algorithm experiment only after diagnosing which fallback condition truly triggered. Keep original TRI parity and two accepted commits as independent gates.

## 2026-11-13-105 — Original native Adapter fallback proof qualified, next independent AFT postprocess sensitivity in CI

**Verified R2c17 native original source:** PR #214 research feature `c37d6ef8a76a59223469c8123c1de263832879e9`, exact [CI #43510748191](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43510748191) 4/4 SUCCESS, original Linux root CTest 89/89, Python 527/527, GCC and Windows MSVC QUAD native 16/16 and frozen Eistute/Book original TRI parity PASS. Source-linked `R2C17_NATIVE_ADAPTER_DOMAIN_FALLBACK` real native `Adapter::_domain_adaptation.csv` evidence joined every original selected rejected patch status to measured local source attempts. [Six source domain CSV and source-bound report artifact #14077649353](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43510748191/artifacts/14077649353), [qualified evidence](evidence/R2C17_ORIGINAL_ADAPTER_DOMAIN_FALLBACK_20261113.json).

**Root-cause measurements, not mere labels:** Book article `research_debug` steps2/3 have 28/28 original patches marked `degenerate_needs_retry` but **zero actually degenerate post-AFT and post-smoothing faces**; minimum AFT physical quality **0.181191** is below the original quality threshold **0.274** (quality priority 0.95). No low-score Quadtree templates, no underresolved transition, curve domain balance 1.0: weak minimum post-AFT face quality demonstrably triggers original `PatchNeedsFallback`. Eistute article `adaptive_stable` step4 has 4/4 original `curve_transition_needs_retry`, 64 individual local Adapter source attempts, all underresolved, min physical AFT quality **0.266221** below threshold **0.2692**, original curve/interior balance only 0.0866..0.1639; zero truly degenerate original post-smoothing faces. Book stable-small experimental step4 had 28/28 source transition retry status, 448 attempts, 280 underresolved, zero actual post-smoothing degeneracies. Eistute low-intensity `research_debug` steps2/3 *do* have post-AFT and post-smoothing degenerate counts: do not conflate model/epoch/quality sources. All findings are original model- and native log-bound, no production quality thresholds modified.

**R2c18 actual implemented next sensitivity:** Feature `cc18c1989017da231c9442190ab684cb1b50da44` changes only new `tests/quad/test_r2c18_original_aft_postprocess_profiles.py` and QUAD research CI. Four isolated genuine `GeneratorAdaptive` native profiles with original Eistute/Book SHA and original `article.conf` preserved: Eistute `AFT_LOCAL_POSTPROCESS_BLEND=0.78` or `AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD=0.80`; Book `AFT_LOCAL_POSTPROCESS_PASSES=4` or `=8`. Each case collects complete accepted original source step events and per-source patch/curve/mesh-incidence receipts from existing R2c13 runner and original detailed native `_domain_adaptation.csv` min quality, actual degeneracy and transition metrics. No original `GeneratorAdaptive`/AFT code edits or acceptance threshold override. Exact [workflow #43518589990](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43518589990) triggered; **CI in progress** at this checkpoint, R2c18 scientific conclusion pending. [Pending R2c18 evidence](evidence/R2C18_ORIGINAL_AFT_POSTPROCESS_SENSITIVITY_20261113.json).

**Milestone status:** [M0–M9 board](MILESTONE_STATUS.md) updated with R2c17 positive *forensic* validation and R2c18 source experiment pending. M4/M5 local original physical QUAD/AFT detached 32 original source patches and OBJ validated, M6 real source radial/physical atlas and advisor packet validated but no signed scientific nonmanifold sheet ownership/physical welding approval, M7 2+ genuinely accepted original `GeneratorAdaptive` source epochs **not demonstrated**, M8 full science paper metrics pending, M9 anisotropy optional. TRI production unchanged and qualified, PR #214 DRAFT/unmerged, main unchanged.

**Next:** Inspect actual exact R2c18 CI, source accepted-step matrix and actual AFT minimum quality/transition metrics versus original R2c17. Do not call repeated native local retry loops accepted epochs. Any subsequent original-source improvement should be opt-in with frozen TRI parity and independently measured scientific quality, not a silent default behavior change.

## 2026-11-13-106 — R2c18 Eistute three genuinely committed original source adaptive epochs; R2c19 repeat and Book source recovery pending

**Exact native R2c18 positive qualification:** Draft PR #214 research feature `cc18c1989017da231c9442190ab684cb1b50da44`, complete [Actions #43518589990](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43518589990) 4/4 SUCCESS: original Linux root 89/89 CTest, 527 Python tooling, GCC Linux / MSVC Windows native QUAD 16/16, frozen original Eistute/Book TRI parity PASS. Actual [R2c18 source OBJ/AFT profile and original domain log artifact #14081183906](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43518589990/artifacts/14081183906), [qualified measured evidence](evidence/R2C18_ORIGINAL_AFT_POSTPROCESS_SENSITIVITY_20261113.json). The profiles invoke original exact production `GeneratorAdaptive` with unchanged native admission, original source models and their prior SHA-256. No production QUAD mode, global nonmanifold sheet decision or silent relaxation.

**First real M7 original accepted-step breakthrough:** Eistute original `adaptive_stable` with only the existing experimental postprocess selection control `AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD=0.80` produced **3 actual distinct `AcceptedMeshScope::Commit` events**, original step IDs `[1,2,4]`, source outer epoch IDs `[1,2,5]`, with one source rejected/restored step3. Each accepted source epoch spans the **same original 4 patches**, complete original **13 curve logs**, accepted patch rows and mesh incidence checksum. Native original research hook prints `R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS ... accepted_committed_steps=3 ... two_accepted_original_generator_epochs=1`; independent R2c13 positive log/physical ownership verification passed. **Eistute now passes the bounded native M7 two-committed-source-epoch engineering gate.** Other Eistute postprocess blend 0.78 profile still had only one accepted source epoch and three rejections.

**Scientific efficiency caution:** Eistute accepted step1: 1,168 TRI elements, global `surface_curvature_3d_relative` error 0.0636432, quality min 0.184411; accepted step2: 2,008 TRI, error 0.0766612 (worse ~20.45%), quality min 0.167252; rejected/restored step3; accepted step4: 4,032 TRI, global error 0.0588399, quality min 0.208604, mean 0.6974. The physical TRI source model contains three **real accepted states** but quality/error progress is not monotone, and 3.45× last vs first accepted element count produces only ~7.5% net error improvement. Therefore do not claim the source acceptance policy optimized error/cost or that original 1993 rules were exactly implemented. Some local Adapter unselected/alternative attempt rows report degenerate post-smoothing face observations even though accepted final TRI CTest summary min quality is positive; a separate **accepted per-patch minimum 3D/UV quality check** is necessary before promoting scientific validity.

**Book remains blocked:** Original `research_debug` Book model, identical original SHA, experimental AFT postprocess passes 4 or 8, each returned only **1 accepted source epoch / 2 rejected restored**, original native second-step minimum quality 0.181191 versus historical fallback threshold 0.274, zero actual native post-AFT/smoothing degeneracy. No second accepted Book original source adaptive epoch; global M7 still OPEN for both models together.

**New R2c19 bounded code:** Feature `61abad7c1ebe21fbe38360fbc8bfd061426b2c4e` adds research-only `tests/quad/test_r2c19_original_accepted_quality_book_joint_recovery.py` and QUAD workflow step. It independently re-runs R2c18 source Eistute success in a *second complete original CI*, validates actual accepted `_acceptance_accepted.log` and full original 4-patch `_patch_adaptation_accepted.csv` minimum TRI quality **separately in 3D and UV**, and explicitly flags non-monotone global error; no per-face area scan or global QUAD welding is claimed. For Book it tests AFT postprocess passes 4 + quality selection 0.80 and passes 8 + threshold 0.80, recording **two-knob sensitivity (non-univariate)** to see whether Book min AFT quality and native source acceptance improve without changing any original admission threshold. [New exact CI #43520477471](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43520477471) launched, was in progress at checkpoint; [pending source evidence](evidence/R2C19_ACCEPTED_TRI_QUALITY_BOOK_JOINT_POSTPROCESS_20261113.json).

**Overall scientific boundary:** [M0–M9 dashboard](MILESTONE_STATUS.md) updated to mark Eistute original source multi-epoch engineering positive, Book M7 open; original physical 32 detached QUAD/AFT patch OBJ scope M4/M5 proven, but M6 globally connected high-valence 4/28 sheet/weld review by actual scientific advisors remains absent. M8 comparative scientific error/quality/cost trials and M9 optional anisotropy open. Main, production TRI, source inputs, original point selection scientific method and PR draft/unmerged unchanged.

**Next:** Inspect exact R2c19 positive/negative accepted TRI quality receipts and Book joint postprocess source metric before moving to a source-backed opt-in local quality repair or broader reproducibility experiments.

## 2026-11-13-107 — Correct original R2c19 TRI patch snapshot epoch, certify exact CI and start native accepted Wavefront OBJ face audit R2c20

**Exact prior first R2c19 run:** Research feature `61abad7c1ebe21fbe38360fbc8bfd061426b2c4e`, [Actions #43520477471](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43520477471) 4/4 completed SUCCESS; original Linux root 89/89 CTest, tooling 527 Python, GCC/Windows MSVC QUAD 16/16 each, frozen original Eistute+Book TRI science parity PASS. Actual Eistute source from independent R2c18 second native full run again accepted **steps [1,2,4]**, restored step3, with 4/4 original patches and 13/13 real curves per source epoch. Book original research `AFT_LOCAL_POSTPROCESS_PASSES=4` or `=8` plus joint `AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD=0.80` has **one** true source accepted step in each case, not two. Original artifact [#14083870355](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43520477471/artifacts/14083870355) includes actual source accepted TRI global and patch logs plus Book original domain attempts. No production original TRI acceptance change.

**Major source scientific scope correction:** Directly inspected all authentic Eistute `_acceptance_accepted.log` and `_patch_adaptation_accepted.csv`. Initial R2c19 script incorrectly named historical per-patch snapshot minima as `minimum_accepted_patch_quality_3d/uv`. Verified actual patch CSV records match **the preceding accepted mesh**: step1 patch minima 3D=0.0753097 UV=0.828427 equals initial accepted step0; step2 patches 3D=0.184411 UV=0.769725 equals globally accepted step1; step4 patches 3D=0.167252 UV=0.747618 equals globally accepted step2. Current accepted source GLOBAL `_acceptance_accepted.log` is valid: step1 3D=0.184411 UV=0.769725; step2 3D=0.167252 UV=0.747618; step4 3D=0.208604 UV=0.514657. The old script therefore overclaimed current patch-specific geometry even though it did legitimately prove positive current global native 3D and UV minima. Explicitly told user of prior overclaim; historical evidence not rewritten silently.

**Corrective actual source feature and closed CI:** Source `c659e37d3a958eb3f452a7261c7b1ab5b6b35797` changes only research `tests/quad/test_r2c19_original_accepted_quality_book_joint_recovery.py`. It validates true current global TRI minima separately, reads the previous true original accepted step0/step1/step2 logged source, requires exact Eistute original patch quality snapshot lag and labels patch values as `previous_source_epoch`, denying independent current patchwise quality certification. Fully [corrected exact CI #43522312435](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43522312435) **4/4 SUCCESS**, root 89/89 CTest, 527 Python tooling, GCC/MSVC native QUAD 16/16 and frozen original TRI parity. Native `R2C19_GLOBAL_ACCEPTED_TRI_QUALITY_AND_PATCH_SNAPSHOT_LAG` confirms original Eistute source accepted [1,2,4], current global min3D/UV strictly positive, current patchwise certification false and prior source snapshot lag true; Book joint source both one accepted. [Corrected R2c19 artifact #14084860307](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43522312435/artifacts/14084860307), [recorded scientific correction](evidence/R2C19_ACCEPTED_TRI_QUALITY_BOOK_JOINT_POSTPROCESS_20261113.json). This does NOT prove all current per-face areas or patch-specified native source geometry positive.

**New bounded independent original native OBJ source audit:** Since original `GeneratorAdaptive::SaveMesh` on unchanged `WRITE_MODE=h` already exports actual accepted 3D TRI meshes to `<OUTPUT_PREFIX>_passo_<step>_malha_<step>.obj`, added research-only `tools/verify_r2c20_original_accepted_tri_obj_faces.py`. Research feature `d96b30731048daecb7c04659f9219cb7c07a75f6` also adds QUAD CI step and 14-day bounded upload of **actual original accepted TRI OBJ**, including Eistute native accepted steps1/2/4 with source expected 1168/2008/4032 TRI faces and Book pinned first original accepted step1 4256 TRI faces. The verifier independently parses every 3D vertex and indexed face, requires all finite XYZ, three distinct valid face vertex IDs, positive nonzero physical area, independent positive dimensionless 3D TRI shape, no duplicate index triangle; ties original accepted source log SHA and .bp model SHA to the real R2c13/R2c18 accepted step receipts; includes five adversarial negative controls (reused/foreign index, collinear, NaN XYZ, repeated indexed triangle). Original OBJ lacks original patch groups; even if successful it proves **model-wide accepted 3D face integrity only**, not per-patch 3D/UV quality, normal orientation, global nonmanifold sheet owners/twins/welding, original 1993 rule, exact global scientific artifact. **Exact new [CI #43523848833](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43523848833) was IN PROGRESS at checkpoint**, no R2c20 positive claim yet. [R2c20 pending evidence](evidence/R2C20_INDEPENDENT_ORIGINAL_ACCEPTED_TRI_OBJ_FACE_INTEGRITY_20261113.json).

**Overall [M0–M9 scorecard](MILESTONE_STATUS.md):** R2c19 now corrected and qualified under global-only current 3D/UV scope; R2c20 new independent 3D face proof in progress. M4/M5 original all-four-sides detached 32-patch physical QUAD/AFT research meshes locally valid; M6 original radial high-valence seam atlas and source-model-bound reviewer packet engineered but Creto/Bento physical sheet/weld approval absent; M7 native Eistute 3 real accepted source steps but Book only 1, and error improvement is nonmonotonic and inefficient; M8 complete equal-error scientific comparisons and M9 optional anisotropy remain open. Main, production TRI, original .bp source SHA and scientific acceptance unchanged; PR #214 remains draft/unmerged. Native local sanitizer and full independent accepted patchwise quality/orientation gates are not complete.

**Next:** Inspect exact R2c20 CI and full original accepted OBJ face counts/areas and its 5 negative controls. If a real source Wavefront export defect occurs (ID alias/precision/zero area), preserve first failing 3D face/index/model source. Otherwise retain OBJ files and move to an independently reviewed Book second original source epoch and/or source patch-specific physical owner integrity proof without changing original TRI science.

## 2026-11-13 Fortaleza / 2026-11-14 UTC — R2c20 completed and R2c21 candidate 5ed7fdd

Read live PR #214, original main and canonical research branch. Confirmed exact source d96b307 Actions #43523848833 SUCCESS 4/4, including the real source R2c20 accepted TRI OBJ face-integrity step. Implemented independent research-only patch indexed-edge checker with seven adversarial controls, added it to GitHub Actions with bounded artifact and documented non-claims. Pushed 5ed7fdd572af195b0b2dce4c223ff6cd5f4c1183 with expected-head lease to draft PR #214; verified remote files and source SHA. Original full detached QUAD/AFT source still uses independent patch ownership with no welding. New CI #43532150635 was IN PROGRESS with no native acceptance at checkpoint. No local native compile, full sanitizer, source UV or Bezier normals validation performed. Original production TRI and main remain unchanged. Next: require exact R2c21 4/4 and actual per-patch outcomes; investigate failures without relaxing scientific guards, then original UV/differential normal evidence and advisor high-valence policy.

## 2026-11-13-109 — R2c21 exact scientific source gate qualified; R2c22 Bezier source facet trial

Confirmed actual PR #214 feature 5ed7fdd CI #43532150635 completed 4/4 SUCCESS, exact root 89/89 CTest and Python 527/527, native Linux/Windows QUAD 16/16 each and frozen TRI source parity. Full root log confirms all 32 original Eistute/Book source detached physical patch indexed topologies passed with seven negative trials. R2c21 qualified only for local indexed topology and does not authorize interpatch sheets.

Published candidate 7cd5014936a417565415d736bad40dc70deb35df to the existing draft feature PR: one original test exporter now records native UV/Bezier XYZ per original physical vertex plus Qu x Qv at each original TRI and split-QUAD facet centroid. Python independently audits UV signed orientation and real indexed physical XYZ against those native original differential samples with five negative controls. Added bounded read-only CI job steps/artifact and scope note. Exact candidate #43539022938 was in progress at checkpoint, not green proof. No local native test or sanitizers run; no production TRI, source models, original acceptance policies or main change.

Scientific limits: C++ generated Bezier differential samples are original-source witnesses, NOT an independent Bézier control-net reconstruction. Strict positive facets alone cannot prove continuous positive Jacobian or nonmanifold global sheet membership. Eistute valence 4 and Book valence 28 remain for source-SHA-bound advisor approval. Book multi-epoch and M8 remain open. Next: inspect exact CI failures and original model facet-level trace, rectify source evidence without weakening gates.


## 2026-11-13 Fortaleza — State, implementation and critical-path audit

Requested current-state/source/plan review. Pinned feature7cd5014 and retained
concurrent canonical advancement ff4d83e→7486e8e without overwriting its R2c21/
R2c22 handoff. Main f6050ec1 and the old primary bb50 checkout remain unchanged.
Read source, roadmap and actual GitHub runs; downloaded exact push5ed7fdd
topology/mesh/TRI-science artifacts and hashes. Local verifier replay reports all
32 detached charts and seven controls, semantically identical to published JSON.
Compiled current physical QUAD source in a bounded C++17 probe with unchanged
prior engine data objects: native exit1 exposes a concave element accepted with
area0.25 / reflex-corner angle2.2143. Failure logs and inputs are retained; no
repair/retry or tolerance change. This is a real admission-contract defect,
not evidence that the exported charts themselves are concave.

Audit distinguishes actual detached physical QUAD/AFT implementation from the
still-refused CLI path and genuine original TRI commits from absent mixed-element
M7 history. Registered the findings, corrected the M7 dashboard definition and
restated existing R2→R3 priority without changing scientific gates. Status/evidence
drift, stale README source-identity claims, large review scope and expiring hosted
artifacts remain explicit. Initial Windows environment/planning unavailable;
separate WSL environment/configure succeeded. Documentation checkpoint regression
has its own exact-revision report; no whole scientific closure is inferred.

Next: preserve/reject the concave input in a bounded physical-element repair,
then deliver one live curved manifold QUAD/AFT patch and two mixed-history epochs.
No source changes, hosted workflow dispatch, new scientific experiment, scientific
adviser approval, global welding or merge occurred during this review.

Final audit readback: exact push7cd5014 Actions43539017852 completed all four
jobs successfully; original pending snapshot is retained separately. This does
not exercise the newly exposed concavity negative input. Document review caught
Windows writer LF-to-CRLF conversion; restored the original LF convention
explicitly before checking again, retaining the failed observation.

Documentation gates also exposed inherited broken relative/missing feature links
and whitespace-only blank lines in the journal. Corrected root-relative depth,
used exact feature URLs for unmerged notes and linked the existing R2c0 radial
scope note; recorded original target names. Explicit journal whitespace cleanup
changes no historical observation. URLs/fragments are not validated by the local
link gate.


### Same-session explicit local/remote synchronization

User requested alignment and a simpler plan explanation. Confirmed primary
worktree clean; detached the clean old b93bad2 checkpoint worktree, safely
fast-forwarded local quad-templates to verified remote7486e8e, and switched the
primary workspace to that canonical branch. Old feature refs, all concurrent
changes, mainf6050ec1 and draft PR214 head7cd5014 are retained. Remote fetch and
branch checkout do not imply merging draft feature code.

Full native documentation-checkpoint build was externally interrupted at544/922
with no final report and zero CTest started. Its previous process is absent and
no build/validation remains; original logs/progress and stale lock were archived
before manual lock recovery. No test/campaign retry or local full-pass claim.
Publish only the mandatory audit/status handoff, with no scientific milestone
closure or feature integration. Source repair and its required exact-head gates
remain the next bounded item. Final remote checkpoint SHA/readback is reported
in the session reply after successful ordinary fast-forward publication.

## 2026-11-14 Fortaleza — Audit improvements and plan status recheck

User requested an explanation of audit improvements and the current plan. Live
Git confirmed clean local/remote quad-templates49dd050, mainf6050ec1 and unchanged
draft PR214 head7cd5014. Rechecked physical convexity admission and CLI refusal
in both snapshots; both findings remain open. Exact Actions43539017852 remains
completed success, with no new test execution or scientific qualification here.
Execution priority remains bounded convexity repair, live complete curved-patch
R2, then actual mixed-element history R3. Original TRI epochs do not close QUAD
M7. Consolidated current status/evidence and smaller review packages are still
needed; high-valence sheet approval remains separate. No implementation, model
campaign, hosted workflow trigger or merge. Roadmap scope/criteria unchanged.


## 2026-11-14 Fortaleza — Execute audit P0 and restore one current state

User authorized incorporating the audit findings and continuing implementation.
Pinned clean canonical3809eb7, mainf6050ec1 and draft PR214 head7cd5014 before
edits. Created the visible primary feature branch for the bounded convexity
repair. Classified the change as an admission-contract defect repair: retain
original012/023 expressions first, add123/301 at unchanged1e-14 before any
observer registration; physical metrics and production sources remain intact.

New60-case fixture fails on the unchanged original class with the preserved
concavity error, then passes20accepted/40rejected under Linux GCC13.3, Windows
GCC16.1 and MSVC19.44 Debug C++17. Existing physical ownership/lifecycle oracles
remain and additionally require the full fixture. Configured LLVM22 analysis
passes for element/new header via actual GCC metadata. Initial inherited format
violations and a rejected /mnt/c/c setup path remain recorded; explicit touched-
file formatting preserves whitespace-removed text identity. No native failure
is hidden or oracle/tolerance weakened.

Roadmap/dashboard now name finite P0→live curved-patch R2→mixed-history R3.
Archived the former STATE byte-for-byte at the same relative-link depth and
replaced the current entry with one concise active item. Legacy evidence scope,
interrupted prior build and scientific decisions remain explicit. Full current
native regression, complete model ownership and whole-probe analysis plus fresh
remote gates are pending at this candidate commit; no stage closure/integration.


## 2026-11-14 Fortaleza — P0 admitted and research merge revalidated

Code53d5bef and documented exact candidatea2c42776a16cc5e03d643ce916e5c6d81f0aa5dc retain the original
concavity failure and pass60 focused cases per LinuxGCC/WindowsGCC/MSVC profile.
Exact full GNU candidate regression85CTest/527Python and both original physical
model modes passed with no failure/error/skip. Configured source/header/whole-
probe LLVM22 analysis passed. Rechecked literal Linux header patterns to remove
regex-dialect ambiguity, retaining previous records without suppressing checks.
Initial Windows clang-format PATH discovery failure was resolved using the
existing installed19.1.5 formatter in a child process; unchanged normal hooks
and independent LLVM22 staged checks pass. No global environment change.

PR216 candidate push43582204121 and PR43582214884 each completed all4jobs with
nativeLinux/Windows, complete baseline/tooling and fresh original Eistute/Book
frozen scientific equivalence. Captured positive nonempty5/4mesh comparisons,
exact OBJ/acceptance and verified exact boundaries. Scoped source/owner and
regression review found no additional P0 blocker; no independent scientific
advisor approval is inferred. Remote main/base/head and exact local seal were
verified before manual merge; no automatic merge workflow or paid runner.

Research merge49c9dc3be66dab2f4839e0ab661065a1ec5c5ba3 has the identical qualified candidate tree.
Safely advanced the primary quad-templates ref without checking out old source,
then repeated full local85CTest/527Python on the exact merge, both model modes,
with no failure/error/skip. Postmerge run43582873180 completed all4jobs. Main
f6050ec1 and larger draftPR214 remain preserved. Six-area code/test/contract/doc/
science/known-inventory audit is retained in the delivery receipt.

P0 is closed only in its existing UV admission scope; broad M4 sanitizers/
denials, physical Jacobian/global topology, literal1993 and high-valence science
remain open. Final documentation checkpoint records these exact identities,
not a new scientific qualification for its own SHA. Next active deliveryP1:
refresh older PR214 against current canonical repair, then one live complete
curved manifold QUAD/AFT patch; afterward two accepted mixed-historyR3 epochs.


## 2026-11-14 — P1 real application implementation

Verified clean synchronized8fe561b/mainf6050ec1, no active development/test
process to interrupt. P0 retained. Implemented an explicit serial opt-in CLI
case on actual production curved Bezier geometry, selectively reusing the
pinnedPR214 AFT execution/seam/coverage helper pair; no wholesale merge/rebase.
Real application generates42QUAD/36originalAFT TRI/69owned nodes and publishes
a typed Patch-linked SubMesh with nonoverwriting OBJ/UV export. Existing Python
production control-net oracle independently verifies geometry, orientation and
boundary; injected precommit failure preserves a prior nonempty physical owner
and node observers. Fixed16 source sampling/vertexmean is explicit experimental
policy, not AdaptCurve/1993 or adaptation. Sourcef074e3a passes86CTest/527Python
with no failures/errors/skips; configured analysis passes4changed TUs. Retained
initial build/output and minor shell-quoting setup errors; no weakened oracle.
Final head/Windows/frozenTRI remote/integration and memory qualification remain
pending. Continue this functional delivery; no new research phase or main change.


## 2026-11-14 — Controlled P1 delivered through PR217

Candidate0999769 and identical-tree research merged39bbc447f88e179c3c4ee674bd9309f59c18eed each pass86CTest/
527Python with no failures/errors/skips. Actual Linux/Windows application
produces42QUAD/36originalAFT TRI/69nodes with16boundary edges; independent
production-control-net audit, unique physical IDs and nonempty-owner rollback
pass. Clang18 address/leak instrumented case and refusal exits are clean; real
UAF control is detected. Full remote candidate/PR and merged4job checks pass,
including fresh frozen Eistute/Book with QUAD compiled and TRI selected.
First remote reference admission failed before comparisons because only the
two new configs/quad assets were not listed; preserved log and added exactly
those reviewed paths, retaining frozen model/profile/tolerance/oracle guards.
Selective PR214 helper reuse only; no wholesale merge or model changes.
Scoped P1 one-shot application is integrated; default build stays TRI and mode
is explicitly gated. Fixed16/vertexmean is not AdaptCurve or1993 validation.
No global XYZ/sheet or broad memory qualification, no P2/mixed epoch claim.
Next technical delivery: use this actual typed mesh as two accepted adaptive
history epochs. Checkpoint is brief documentation/evidence, not new science.

## 2026-11-14 — P2d0 synthetic preflight and P2d1a physical source residual qualified

PR223 feature f1ea9332 (research merge 82522e05) qualified synthetic metadata
epoch-parent/mesh/topology/source/policy invariants with 14 negative cases and
fault-before-record-commit rollback. Its first exact-SHA CI failed the strict
architecture inventory because tests/quad/CMakeLists.txt changed; refreshed
ONLY the retained actual CMake SHA-256, without weakening the inventory
algorithm or production TRI checks. New exact candidate CI43605731184: 4/4
jobs, 85/85 root CTest, 527/527 Python, native Linux/Windows and frozen TRI.
These synthetic metadata transitions count as zero adapted QUAD epochs.

PR226 feature 53091439 (research merge c78a4445) added independent
source-parameterized physical residuals on the real 42QUAD/36AFT TRI
controlled candidate; native QUAD bilinear face geometry is never split for
the estimator, TRI remains barycentric, and old original Bezier control-net
is evaluated again at 354 deterministic UV sample points. Face4 maps
to real native QUAD cell13, ordinal6, depth2; face74 is maximum AFT TRI
error near UV(0.2,0.1). The true C++ application, independent Bernstein/OBJ
Python oracle and Linux/Windows artifacts agree: QUAD max0.0026204483,
AFT TRI max0.0463899583, sampled RMS0.0130653586. Identical physical
OBJ SHA-256 cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0
retained; original TRI unchanged. Exact feature CI43606747684: 4/4 jobs,
18/18 QUAD native per OS, Linux ASan/UBSan/leak, 85/85 root CTest,
527/527 Python and frozen original Eistute/Book TRI scientific parity.

Independent supplementary topology/area audit: QUAD 25% UV area and
29.6% faceted XYZ area, versus AFT TRI 75% UV and 70.4% faceted XYZ.
Unweighted squared sampled residual is ~99.53% TRI/AFT; a coarse facet
area-weighted sampled squared residual is ~99.84% TRI/AFT. Neither is
a continuous area integral. Native CaptureLeafPolygons excludes leaves
touching source boundary: refining an existing interior QUAD leaf alone
cannot increase the original 25% QUAD UV coverage. The next P2d1b experiment
must compare actual boundary/AFT-dominated and interior QUAD native-tree
refinements with original contours, quality, UV/XYZ and retry evidence.

Research evidence: evidence/P2D0_P2D1A_QUALIFICATION_20261114.json;
canonical R3 issue221. Important negative scientific status:
real_tree_edits=0, adaptive_epochs=0; no production mixed-history adapter,
source AdaptCurve equivalence, approved quality policy, full M7/R3,
1993 equivalence, nonmanifold global welding, all-QUAD or anisotropy.
Main remained outside these research deliveries. This documentation-only
checkpoint adds no scientific qualification to its own commit SHA.


## 2026-11-14 — P2d-1b0/1 real native source refinement and connected QUAD disk

PR227 exact feature4dba0421807047975a2163c917bd8bcd802bca8c
merged9259de230c3da24ffd4dbced65beae7375c3fc46 after
CI43609586259 PASS4/4, native QUAD Linux/Windows 18/18 each, 85
root CTests, 527 Python, Linux sanitizers and frozen original TRI.
The previous real source-error candidate's interior cell13
subdivision gives 22 original Quadtree leaves, 54 emitted UV QUAD
but unchanged 0.25 UV area. AFT-dominated source cell6 instead
creates a boundary QUAD island: prospective area0.265625, native
`EmitLeafQuads` rejects `Boundary vertex is not manifold`
and zero illegal faces are published. Exact negative witness pinned.

PR228 exact feature0c9bdc7f7562ce2c9633b4b44bb07fe7039b16a8
merged092b9adfa0f9f03d4c28b5218759b7e89cf5b199 after
CI43618564496 PASS4/4, Linux/Windows real application, Linux
ASan/UBSan/leak, frozen TRI and full 85 CTest/527 Python.
A native three-cell band driven by the actual AFT source error
subdivides original cells6/7/9 and balances the original
Quadtree 19→28 leaves. Real `CaptureLeafPolygons` /
`EmitLeafQuads` passes disk and produces 62 UV QUAD, area
0.328125 (32.8125%). Independent Python reassembles the
original 8×8 dyadic source grid: 21/64 eligible cells,
four-neighbor connected, no enclosed holes. The accepted
initial physical OBJ is unchanged at SHA256
cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0
on all Linux/Windows/ASan outputs. This is a topology-only
candidate without new native AFT or physical QUAD/TRI SubMesh:
`actual_aft_retriangulations=0 adaptive_epochs=0`.

Draft PR229 opens the next bounded gate: original native AFT
reconstruction and full typed physical candidate from *identical
independently rebuilt* native band trees, candidate-only OBJ,
independent source/quality audit, physical failure/rollback.
Even successful staging must not be mistaken for an accepted
adaptive epoch. Main TRI behavior remains unchanged. Evidence:
evidence/P2D1B0_P2D1B1_NATIVE_TREE_BAND_20261114.json;
canonical R3 issue221 remains OPEN. This documentation-only
checkpoint has no scientific qualification for its own SHA.

## 2026-11-14 — ChatGPT GitHub continuation: P2d-1b2 positive physical candidate

Read canonical STATE/roadmap/protocol/journal and exact GitHub PR and CI status.
Verified feature PR229 head bada655ae68a635f4b9664a05b2ab261d2d8d94c
passed GitHub Actions #43619762822 four/four jobs, Linux GCC and Windows
MSVC full physical application and native tests, Linux ASan/UBSan/leak,
85/85 root CTests, 527/527 Python and frozen Eistute/Book original TRI
parity. Native Linux, sanitizer and Windows logs independently reported
93 physical nodes, 62 genuine QUAD and 44 native-AFT TRI, original 16
source boundary edges, valid exported candidate 76b0b4de...0d7afd6;
initial 69/42/36 mesh OBJ unchanged cbf6cd63...90295e0. Maximum
sampled source residual changed 0.0463899582705 to 0.0367706981989;
RMS 0.0130653585529 to 0.007863932397 uses different 354/486
sample sites and is NOT a common-sample scientific convergence claim.
PR229 concurrently merged to quad-templates at
289b6be6e97f787b53471255f9d30fbf3777fbba; no exact-merge CI
was independently established in this session.

Audited P2d-1b2 test false-green logic: previously a reconstruction
exception with status=rejected could pass the positive regression.
Created branch quad/p2d1b2-positive-physical-gate-20261114 from
original feature bada655a; committed only Python test changes at
71dde5d2a443b48a8e4a9a84dca07f5d7bb64901; opened draft PR230.
The new positive guard requires actual staged physical OBJ and
source-specific 93-node/62-QUAD/44-TRI topology; a deliberate well-formed
negative checks that the rejection-only path remains valid as a
negative but cannot pass the positive gate. The maximum sampled residual
positive witness is source-specific; no general scientific threshold
or RMS convergence requirement was added. After concurrent PR229 merge,
retargeted PR230 base to canonical quad-templates with only one Python
file affected. The PR230 exact-feature CI, code review and merge are
NOT verified. No full native local run was performed; a local raw-file
syntax download attempt failed due unavailable DNS, not a passing check.

Published explicit scope/evidence JSON, updated STATE and this append-only
journal on the research branch; main remains
f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94. A physical unaccepted
candidate is NOT an accepted second adaptive epoch.
Science issue221 remains open: original AdaptCurve provenance, paired
previous-state-driven accepted epochs, owner/observer transactional
publication, comparable source integration error and policy approval
are still missing. High-valence scientific sheet/weld decisions, 1993
equivalence, all-QUAD and anisotropy remain separately open.
Next: qualify PR230 exact feature SHA in Linux/Windows/sanitizer/frozen TRI,
then promote only its scoped test to quad-templates after review and
design the first actual mixed state transition with independent common-grid
error/quality/complexity evidence. Do not touch main/default TRI.

## 2026-11-14 — Current continuation: independent same-site proof, second error-band native trial

Verified live research quad-templates and preserved main
f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94. Exact feature
1efb13b6a6fb46fca77deba81aa405db5bff90d5 of PR231 passed
Actions #43620929978, four/four jobs: Linux/Windows actual controlled
physical candidates, Linux ASan/UBSan/leak, 85/85 root CTests,
527/527 Python and frozen original Eistute/Book TRI parity.
Independent Bernstein control-net same 4096-site UV metrics verified:
maximum 0.0656412209316 -> 0.0516074134575; RMS uniform UV
0.0172952038547 -> 0.0125180008382; source differential-area
weighted RMS 0.0159812656640 -> 0.0118103246430.
Merged PR231 at 4b7f485a0df2c5108dbd822f337d2e38bba2947a. Source
remains controlled fixed16; staged mixed 93-node/62-QUAD/44-AFT-TRI
physical candidate is not accepted mixed adaptivity. PR230 was
closed without merge due a duplicative positive staging check
after PR231 integration; its extra synthetic rejection-only unit
was not ported and must not be reported as qualified.

Created isolated source-only P2d-1c0 branch and PR232.
Its original measured staged physical candidate has new worst
AFT triangle face 103 near UV (0.8,0.1), source level-2 grid
cell (3,0). An independent 8x8 dyadic surrogate retains the
previously refined (1,1),(0,0),(1,0),(0,1) cells. Six isolated
offline Python tests locally PASS: current first 28-leaf/21/64
QUAD UV, single next error-cell 31-leaf/22/64 disconnected/
diagonal vertex reject, two alternative two-cell bridges
34 leaves/24/64 connected, three-cell band 37 leaves/26/64
connected, plus malformed input/duplicate/vertex-link controls.
None of these synthetic source-grid leaves are falsely called
native generated QUAD physical faces or accepted epochs.
First source commit 7a42a49 passed #43622937311 four CI
jobs BUT those jobs did not actually execute the new 6-case
script; preserved the coverage deficiency, amended the existing
real Linux/Windows/ASan controlled-application regression to
invoke all six in feature e0621a9b8b2675c60ba5bfd3cd0dfe0e395b01af.
Exact revised CI #43624052194 was ongoing at checkpoint,
NOT a verified pass. PR232 remains DRAFT/UNMERGED.

Started stacked native P2d-1c1 draft PR233, current feature
8b62e77bb6de98ce284881c42d17f5ce18afe96f:
a real original native Quadtree is reconstructed from the
current previous 28-leaf source band for each measured next
AFT error alternative, and original source methods perform
real second corner, west, north and both bridge edits with
2:1 balancing and actual `CaptureLeafPolygons` /
`EmitLeafQuads`. Python independently correlates four
genuine C++ outcomes with the separate source-only grid and
checks previous physical element/node observer identity and
explicit rejection for isolated corner. No second original
AFT exterior triangulation, physical third mesh, acceptance
policy, owner transaction or actual accepted adaptive epoch
is implemented. Native C++ compilation, exact-feature CI
and runtime evidence for PR233 have NOT been run/verified;
because its PR initially targets the stacked PR232 feature
branch, it does NOT yet satisfy the workflow
`pull_request` branch filter requiring quad-templates.
Retarget and execute exact CI only after PR232 is qualified/
merged. No local native C++ compilation was performed.

Next: finish PR232 exact six-case CI, review/merge its strictly
bounded source-only oracle, then retarget PR233 to canonical
quad-templates and require Linux/Windows real native output,
ASan/UBSan, full root/tooling and original frozen TRI.
Any native failure remains reported as rejected, not converted
to success. After native disk qualification pursue original AFT
physical reconstruction per variant, common-site source error,
warpage/Jacobian/cost and strong-exception owner transaction
before scientific mixed epochs. R3/M7 issue221 remains OPEN,
adaptive_epochs=0; global nonmanifold sheets, full AdaptCurve,
1993 historical equivalence, all-QUAD, anisotropy remain open.

## 2026-11-14 — Correction: exact P2d-1c0 CI-qualified merge and measured native P2d-1c1 alternatives

Earlier continuation explicitly retained first P2d-1c0 run's missing six-case
test invocation. Corrected feature e0621a9b8b2675c60ba5bfd3cd0dfe0e395b01af
then executed all six standalone dyadic tests as part of actual Linux,
Windows MSVC and Linux ASan/UBSan/leak controlled applications; exact
Actions #43624052194 completed 4/4 success including 85/85 root CTests,
527/527 Python tooling and original Eistute/Book frozen TRI parity.
PR232 was merged to quad-templates at
a03938627ab8bf2aeadc04d1c238c2eb693d651f.
This is bounded source-grid topology, not a generated second native AFT
physical mesh. Exact evidence: evidence/P2D1C0_SECOND_BAND_DYADIC_PREFLIGHT_20261114.json.

PR233 was retargeted to quad-templates only to trigger exact-source pull_request
CI. First workflow #43624612764 failed real application C++ compilation due to
incorrect const pointers passed to legacy non-const Vertex::getX()/getY().
No previously failed CI was relabeled as passing. Narrow source
correction 7b536dc901cae1e8b9410f6fbd9f3540c20dba09 retained
the same source cell/geometry/policy and corrected native Linux and
Windows actual application plus Linux ASan/UBSan/leak reported identical:
second source corner only 31 leaves/0 emitted QUAD/0.34375 possible
UV (rejected), west bridge 34 leaves/75 emitted QUAD/0.375 UV,
north bridge 34 leaves/71 emitted QUAD/0.375 UV, both bridges
37 leaves/82 emitted QUAD/0.40625 UV. The source physical prior
staged 93-node/62-QUAD/44-AFT-TRI owner and its observers remain
unchanged, confirmed with independent Python source-grid cross-check.
Corrected workflow #43624756858 passed native Linux/Windows and
original frozen TRI equivalence; full root CTest/tooling remained
IN PROGRESS at this checkpoint, so no complete 4/4 qualification
or merge is claimed for PR233.

R3/M7 still 0 accepted adapted QUAD/TRI epochs. No second AFT
exterior physical reconstruction, repeated accepted MixedEpoch,
scientific error/quality/complexity policy, original AdaptCurve,
model-global high-valence weld, all-QUAD, anisotropy or 1993
equivalence. Main remains f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.
Next: qualify complete PR233 exact CI and review its final
post-PR232 merge diff, then attempt actual second AFT physical
reconstruction for native west/north/both and independent same-site
geometric-quality/cost gates with fail-closed owner/OBJ publication.

## 2026-11-14 — P2d-1c1 final qualification and new physical AFT P2d-1c2 proposals

Confirmed previous exact-source feature 7b536dc901cae1e8b9410f6fbd9f3540c20dba09
PR233 CI #43624756858 4/4 SUCCESS, root 85/85 CTests and 527/527 tooling
Python, Linux/Windows genuine native/controlled app, Linux sanitizers and
frozen original Eistute/Book TRI source parity. Reviewed net source diff
(only C++ controlled research source, Python independent app oracle and
bounded research doc); merged PR233 into quad-templates as
15a57f3604c9fc8b072762ed10f3219aa12c9ad7.
No main/production TRI changes.

Started distinct branch
quad/p2d1c2-real-second-aft-physical-candidates-20261114 from exact
research merge 15a57f36 and opened draft PR234. New C++ implementation
retains actual previously refined native Quadtree alternatives for
original full native makeTemplateBasedMesh TRI reference front and
OwnedQuadAftFront AttemptExteriorTriangulation, constructs owned typed
real Bezier QUAD/TRI candidate and exports only after complete mixed
topology, orientation, original boundary, AFT closure and physical
facet/source validation. A disconnected proposal produces explicit
reason and no OBJ; none is published as Patch/SubMesh accepted epoch.

Independent Python OBJ/Bernstein oracle was extended to inspect
three candidate files, original 16 boundary edges, mixed UV disk,
QUAD signed Jacobian/warpage, true four-node QUAD physical interpolation
and the **same 4096 UV source sites** for maximum XYZ, uniform RMS
and physical-differential-area-weighted RMS. Preserves previous P1
and first staged physical SHA and immutable node/element observers
on failed/successful candidate probes. Source-only six-case dyadic
negatives still executed in actual app regressions.

Exact PR234 feature 32e4653ff80947498c39953ce53f50af618203e9
CI #43663198795: Linux GCC QUAD/native/controlled app and Linux
ASan/UBSan/leak SUCCESS, Windows MSVC same SUCCESS, frozen original
TRI equivalence SUCCESS; root TRI baseline/tooling Linux job still
IN PROGRESS at session checkpoint, so **do not call PR234 fully
qualified or merged**.

Measured actual new physical candidates on both Linux and Windows:
- isolated new source corner refused, no output;
- west: 109 nodes, 75 QUAD/50 AFT TRI, UV area .375,
  4096-site max .026268569305, uniform RMS .010189890795,
  source-area RMS .009960083459, SHA ca08918f6d71fa67...4274ee;
- north: 107 nodes, 71 QUAD/54 AFT TRI, UV area .375,
  max .026268569305, uniform RMS .009580048644,
  source-area RMS .009233319235, SHA 6eb4faedeaab44fb...e26d500;
- both: 117 nodes, 82 QUAD/52 AFT TRI, UV area .40625,
  max .026268569305, uniform RMS .009459332494,
  source-area RMS .009155128673, SHA b77afb530724f38f...3724bd36c.
All have 16 source boundaries, positive minimum QUAD scaled
Jacobian .567009347 and min warp cosine .997012647.
The first staged physical baseline was 93 nodes, 62 QUAD/44 TRI,
source-area RMS .011810324643. This is **fixed-grid geometric
approximation evidence**, not continuous error bound, FEM solution
error, valid scientific acceptance policy or two accepted epochs.
Complete hashes and exact source available in
evidence/P2D1C2_SECOND_PHYSICAL_AFT_TRIALS_20261114.json.

Next: finish exact-head CI #43663198795, source readback/PR review
and only then consider merge to quad-templates. Study alternative
multiobjective error, QUAD coverage, element counts and physical
quality; devise fault-injected accepted owner transaction and
previous-accepted-state-driven mixed epochs. R3/M7 issue221 remains
OPEN, adaptive_epochs=0. Full production AdaptCurve, original 1993
policy, global nonmanifold sheet pairing, all-QUAD and anisotropy
are still outside certified research candidate.

## 2026-11-14 — Final exact P2d-1c2 CI and physical research integration

Corrects the previous explicitly pending P2d-1c2 checkpoint: exact
source 32e4653ff80947498c39953ce53f50af618203e9 completed
Actions #43663198795 4/4 SUCCESS. Linux GCC and Windows MSVC
native/controlled original AFT produced three distinct physical
mixed QUAD/TRI candidate OBJ each with original 16 boundary
edges and typed positive physical/source oracles. Linux
ASan/UBSan/leak PASS, independent 64×64 (4096 common sites)
Bernstein source residual PASS. TRI root baseline 85/85 CTests
and 527/527 Python tooling PASS; frozen original Eistute/Book
TRI scientific equivalence PASS. Explicit isolated source corner
rejected without physical OBJ. Exact emitted west/north/both
candidate SHA-256/element counts/errors and scientific cautions
remain in evidence/P2D1C2_SECOND_PHYSICAL_AFT_TRIALS_20261114.json.

Reviewed PR234 exact changed-file set (one bounded native research
C++ unit, one independent Python application oracle, one research
protocol) and merged into quad-templates at
672aa297352d0ee316c57f347e7cd5f69e4f86d1.
main remains f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.
The three candidate physical meshes are not accepted QUAD/TRI
history epochs: R3/M7 issue221 OPEN and adaptive_epochs=0.
Next bounded work: independently profile finite-grid source-error,
typed physical quality, complexity/QUAD UV-area and QUAD-count
objectives without silently declaring a preferred scientific
policy; develop fault-injected atomic prior accepted mixed owner
transaction only after explicit research decision. No full
production AdaptCurve or nonmanifold global welding/all-QUAD/
anisotropy/literal 1993 reconstruction.

## 2026-11-14 — P2d-1c3 explicit profiled source-OBJ Pareto CI handoff

Exact P2d1c2 physical original AFT candidate merge
672aa297352d0ee316c57f347e7cd5f69e4f86d1 is research-only;
main TRI still f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.
Created branch quad/p2d1c3-independent-multiobjective-pareto-20261114
and draft PR235, exact latest feature
27851df2625e0c0b37e12023af699a01f3d0304c.
The one-file Python pure dominance oracle
tests/quad/independent_pareto.py accepts only measured real physical
face/node/UV area/error/Jacobian/warpage objectives and validates
typed totals, finite positive values, full observation keys, and
order-invariant fronts. Actual controlled application OBJ oracle
independently integrates the signed QUAD polygon UV areas directly
from every physical OBJ; computes two explicitly separate
source-specific objective profiles: UV-area vs the same profile
with additional QUAD count. Six unit controls are invoked in
actual Linux/Windows/ASan application regression, not merely
present but unexecuted.

From real P2d1c2 4096 identical UV sites, the area profile
has the expected non-dominated band/north/both, with north
dominating west because both have 125 total physical faces
and .375 QUAD UV area but north has 107 vs west 109 nodes
and lower source-area RMS. When QUAD face count is itself an
additional maximization objective, west has 75 vs north 71
true QUAD faces, so all four become non-dominated. The
result is *profile-dependent*: never convert to implicit
adaptive scientific acceptance policy. Same-site source
geometric interpolation RMS is not a continuous source bound
or PDE solution error. Physical QUAD global minima can mask
local quality degradation; no prior accepted owner transition,
adaptive_epochs=0.

At checkpoint exact feature [CI #43664129060](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43664129060)
had Linux native and real application including six explicit
Pareto tests and ASan/UBSan/leak SUCCESS, frozen original TRI
scientific parity SUCCESS, but Windows controlled application
and Linux root baseline/tooling jobs were still in progress.
No full 4/4 qualification, merge or new accepted owner is
asserted. Registered pending exact science evidence in
evidence/P2D1C3_PROFILED_PARETO_20261114.json.
Next: finish full exact-head PR235 CI, check final changed-file
set, only then merge to quad-templates if passing. Follow with
P2d1c4 accepted-owner state machine, strong-exception rollback
and two real previous-accepted-source-driven mixed transitions,
without changing default TRI or incorrectly closing R3/M7 issue221.

## 2026-11-15 — P2d-1c3 qualified and five-fault P2d-1c4a reversible real-owner trial

PR235 actual-physical-OBJ Pareto source
27851df2625e0c0b37e12023af699a01f3d0304c completed exact
CI #43664129060: 4/4 jobs SUCCESS, 85/85 root CTests, 527/527
Python tooling, native Linux and Windows real physical QUAD/AFT
applications plus Linux ASan/UBSan/leak, frozen original Eistute/
Book TRI equivalence. Its six independent adversarial Pareto
tests explicitly ran in actual Linux, Windows and sanitizer apps.
The area-based source-specific profile finds north dominates
west because error and node count improve for the same total
125 physical elements and .375 QUAD UV area. Adding QUAD face
count as a separate objective makes all four candidates
nondominated; this is profile-sensitive diagnostic evidence,
not an acceptance policy. Reviewed net code (one Python
controlled app test, pure independent Pareto oracle, separate
six-case unit and research document); merged research PR235
at ab1dc62a815f3d56c9b25845bec00863730ddcd5.
Updated evidence/P2D1C3_PROFILED_PARETO_20261114.json.

Source architecture audit read original
include/data/patch/patch.h and src/data/patch/patch.cpp,
include/data/mesh/sub_mesh.h and src/data/mesh/sub_mesh.cpp,
include/data/node_adaptive.h and src/data/node_adaptive.cpp.
Patch/SubMesh register separate non-owning forward/back
observers with noexcept setters; SubMesh owns nodes and
elements, whose exact ordered borrowed observer lists must
survive failures. Previous physical OBJ must not be changed.

Created isolated
quad/p2d1c4a-real-owner-transaction-rehearsal-20261115,
draft PR236. The real P1 69/42/36 has already been physically
published as Patch/SubMesh when the trial generates the true
source-error native 93/62/44 successor via original AFT
and independently clones all typed nodes/elements.
The C++ trial injects five intentional failures before the
forward owner swap and checks the previous nonempty live
owner, every node pointer, ID, XYZ, element pointer, every
ordered observer list and previous OBJ bytes. A real
forward/back noexcept pointer swap is rehearsed and reverted,
with a destructor guard to restore previous owner after a
validation failure. Independent Python requires exact owner
receipt in both accepted and rollback cases plus eight
falsified receipts that must each be rejected. No next OBJ
publication, owner archival, implicit epoch increment or
scientific acceptance policy. Detailed limits:
docs/research/quad/P2D1C4A_OWNER_TRANSACTION_REHEARSAL_20261115.md.

Exact latest PR236 feature
5c8bc5ae563fdcad9518091e16a9cecf391ca55c,
CI #43703415674: native Linux app and Linux
ASan/UBSan/leak PASS, native Windows controlled app PASS,
frozen Eistute/Book TRI parity PASS. Independent forged
receipt oracle eight/eight PASS in both Linux Release and
sanitizer execution. Root TRI baseline/tooling Linux
job remained IN PROGRESS at this checkpoint, so NO 4/4
qualification or PR236 merge is asserted. Retain
evidence/P2D1C4A_REAL_OWNER_TRANSACTION_REHEARSAL_20261115.json,
and update the pending qualifier only after all exact-head
jobs really pass.

Next engineering: finish PR236 exact CI, review and integrate
if qualified. Then separately implement controlled source
selection and atomic/recoverable actual physical OBJ + owner
publication, immutable prior accepted typed history,
post-publication and mid-publish failure injection,
and two truly accepted previous-state-driven distinct
QUAD/TRI adaptations with advisor-approved numerical
criteria. Until then adaptive_epochs=0 and R3/M7 issue221
OPEN. No main/default TRI modification or full production
AdaptCurve, nonmanifold high-valence weld, all-QUAD,
anisotropy, historical1993 equivalence claim.

## 2026-11-15 — Qualified final real owner rehearsal P2d-1c4a and research merge

This append explicitly supersedes the earlier pending CI status:
actual previous-owner feature
f55b8e4aec4c06eb6603f3cf6f6de54d3fdf1f81 passed
Actions #43704424433 **4/4**. Linux GCC and Windows
MSVC real original AFT controlled QUAD/TRI app/native tests,
Linux ASan/UBSan/leak and independent eight forged receipt
negative controls all passed. Eistute/Book frozen original TRI
science parity passed; root baseline 85/85 CTests and 527/527
Python tooling tests passed. Exact independent two Linux
Release/sanitizer JSON outputs reported a genuine published
P1 previous owner 69/42/36, new source-error-driven typed
real AFT candidate 93/62/44, exactly 5 injected
prepublication fault rejections, one real noexcept pointer
swap **reverted** to P1, and 0 accepted adaptive epochs.

The previous exact-source head 4b544600 was correctly
rejected by original GCC application compilation because
the legacy ElementAdaptive::GetId is non-const, while the
new previous-element observer witness used a const pointer.
Fixed narrowly at f55b8e4a by a local mutable observer
pointer, without production SDK or algorithm change.
The final variant also checks prior node Ga/Gd/Ha/Hd
curvature scalars, element ID and area, exact ordered
node observers, all node identity and XYZ, original
published OBJ bytes and source error newly measured
from the ACTUALLY published old Patch/SubMesh pointer.
No rejected/source-staged candidate was counted as a pass.

Audited final PR236 changed files: one controlled QUAD
research C++ unit, its actual independent application
Python test and bounded protocol; no production TRI files.
Merged to quad-templates as
8a451eee7fad416d36604a61afd35412c65cd72a.
Evidence/STATE/roadmap updated at
evidence/P2D1C4A_REAL_OWNER_TRANSACTION_REHEARSAL_20261115.json.
Main remains f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.

Scientific limitation persists: this is deliberately a
reversible owner TRANSACTION REHEARSAL, not an adopted
previous-state-driven accepted adaptation. It publishes
no second output and does not own/archive two actual
committed adaptive transitions. Even after successful
node/observer/OBJ invariance, the filesystem-memory
transaction, post-publication crash/recovery, accepted
epoch state machine, immutable source/control-net and
original curve provenance and scientifically preapproved
error+quality+complexity policy remain unimplemented.
R3/M7 issue221 OPEN, adaptive_epochs=0. Fixed16
research chart is not original production AdaptCurve;
high-valence Eistute/Book global welding, historical
1993 equivalence, all-QUAD, anisotropy unproved.

Next: P2d-1c4b separately specify a real accepted
mixed epoch archive and source-history replay,
two distinct later mixed adaptation transitions
selected from the actual previous published mixed
state, original AFT physical independent witnesses,
failure injection after in-memory swap and during
output staging/publication, and a pre-registered
scientifically approved candidate selection policy.
Do not silently choose north or both from a single
Pareto profile; preserve true QUAD area vs QUAD count
and common-grid source error quality tradeoff.

## 2026-11-15 — advancement review, local alignment and Blender inspection

Reviewed live canonical `392d02c0dc1fd52bcc6cb83320469d1143636ef6` and
fast-forwarded the clean primary checkout from `3beec583` (162 commits behind).
Other branches/worktrees were preserved. Remote main remains
`f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; PR214 and PR225 remain drafts
with their separate targets. No implementation or scientific policy was changed.

Live Actions API confirms exact PR236 feature `f55b8e4a` run #43704424433
and exact research merge `8a451eee` run #43705007549 completed 4/4 SUCCESS.
The reviewed canonical head has no source/test/workflow changes relative to
that feature in the inspected paths. Focused source review confirms a real
published-P1 source-error measurement and reversible successor-owner rehearsal,
not accepted mixed epochs. R3/M7 issue221 stays OPEN, adaptive_epochs=0.

Downloaded the exact Windows controlled-application artifact. Independently
counted and SHA-256 hashed five original OBJ files: 69/42/36, 93/62/44,
107/71/54, 109/75/50 and 117/82/52 nodes/QUAD/TRI, all boundary16.
Locally replayed the existing receipt verifier on real normal/rollback stdout,
rejecting eight forged variants per run. An initial helper import-path setup
failure was corrected locally; no test implementation was changed. Imported
the five meshes into installed Blender 5.3.0, preserved source geometry/face
cycles and UV without remeshing, separated objects by translation, saved and
visually checked `build/quad-review-20261115/APMesh_QUAD_review.blend`.
The scene distinguishes P1 from unaccepted candidates and labels zero epochs.
Local build artifacts and helpers remain untracked.

Corrected stale current-state prose that still described PR236 as draft/CI
pending, retained the failed intermediate GCC evidence, and added live
research-merge CI readback. Changed documentation: STATE.md,
IMPLEMENTATION_ROADMAP.md, this append-only log,
evidence/P2D1C4A_REAL_OWNER_TRANSACTION_REHEARSAL_20261115.json and the
bounded STATUS_REVIEW_20261115.md. The first commit attempt was rejected by
the staged-whitespace hook because this log retained an extra blank line at
EOF. Explicit normalization was confined to this log; the five-file quality
whitespace check, staged hook and evidence JSON syntax checks then passed.
No local native build, CTest, sanitizer, full historical oracle or
new CI campaign was run; this documentation checkpoint does not qualify its
own revision scientifically or close P2/R3/M7.

Exact next action: specify P2d-1c4b accepted typed-state/archive ownership,
immutable source fingerprints and memory/file publication fault/recovery
matrix. Record the advisor-approved error/quality/complexity policy before
accepting two distinct transitions driven by each actual preceding accepted
mixed state. Do not infer policy approval from Pareto profiles. Preserve the
separate production AdaptCurve, high-valence sheet ownership, historical 1993,
all-QUAD and anisotropy gates. Commit this documentation checkpoint to
quad-templates and verify remote readback before claiming persistence.

## 2026-11-15 — clarify fixed boundary sampling versus original exterior AFT

Read-only follow-up at canonical `0ee67f33cd51c48a55d07cd337a896168bb6e1b2`:
the controlled Blender meshes use quarter-parameter fixed16 source sampling
in `research/quad/controlled_patch_application.cpp::MakeSourceTree`. Their
`Generate` path seeds `OwnedQuadAftFront` and calls
`AttemptExteriorTriangulation`, which invokes original `makeGeometryBasedMesh`
and conditionally original `makeTopologyBasedMesh`. Its declared diagnostic
scope excludes `improveMesh` and `fillMesh`. Thus original exterior advancing
front is already present, while the original curve-adaptation pipeline is not
integrated into this live case. The finite P1/P2 scope isolates mixed-element
construction, interface checks and publication/history work; it does not prove
that fixed sampling is required by the algorithm. Separate PR214 R2c7/R2c9
evidence records real all-side original curve-adaptation/physical-chart trials.
Do not conflate those detached trials with accepted application integration.

Updated STATE.md and appended this clarification only; no roadmap sequencing,
scientific policy or source change. Remote research and main were unchanged;
PR214 remains draft at 7cd5014. PR225 advanced separately to 6873195 and was
preserved. Latest exact research-merge CI remains successful #43705007549;
no new native tests or CI campaign were run. Apply two-file whitespace/staged
checks before committing this documentation handoff. The exact next P2d-1c4b
action and real-boundary integration obligation remain as previously recorded;
adaptive_epochs=0 and R3/M7 remain open.

## 2026-11-15 — prioritize original real-boundary application integration

The user requested the implementation sequence after questioning the fixed16
boundary. Reviewed canonical `2b5eadfdbedd1b4169d4866c1680ecbe1f666b98`,
unchanged main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, current source,
state/roadmap and latest handoff. PR214 remains draft at 7cd5014 and PR225
remains separate at 6873195. Latest research merge CI #43705007549 is still
successful; no source integration or new native/CI campaign occurred here.

Adjusted execution order: one active functional delivery is now original
real-curve boundary integration into actual opt-in curved manifold QUAD/AFT
generation and physical publication. The source-driven native boundary/tree
must replace both fixed quarter-parameter sampling and prescribed tree edits
in the new path, while fixed16 stays a named regression. Reuse original curve
policies/configuration and compatible reviewed PR214 helpers, not its whole
draft or a new discretizer. Preserve default TRI and all current evidence.

Added REAL_BOUNDARY_APPLICATION_PLAN_20261115.md with finite source identity,
nonuniform/reversed traversal, seam/UV/XYZ, negative/rollback and exact-revision
acceptance gates. STATE.md and IMPLEMENTATION_ROADMAP.md now put this delivery
before P2d-1c4b; accepted-history/publication, recovery, scientific selection
and two actual successive accepted mixed transitions remain required afterward.
No new numerical policy is approved. Whole-model high-valence sheet decisions,
1993 equivalence, all-QUAD and anisotropy keep their separate gates.

Reconciled MILESTONE_STATUS.md: its old priority still named completed P2d-1b2
as next, and its M7 row incorrectly said physical AFT reconstruction was absent.
The current M5/M7 rows now distinguish detached real-boundary trials, live
fixed16 application, physically staged candidates and zero accepted epochs.
No prior append-only history or negative evidence was removed.

Exact next action: trace original GeneratorAdaptive::AdaptCurve inputs/outputs
on the same curved source/initial state/configuration, choose compatible source
boundary helpers and implement the bridge in one feature PR to quad-templates.
No further fixed16 candidate expansion is the next functional delivery.
This session changes five documentation files only. Selected whitespace and
staged checks passed for all five files; all five added relative links resolve.
Commit the checkpoint and verify remote readback before claiming persistence.
Implementation/native gates remain unexecuted for the new delivery;
adaptive_epochs=0 and R3/M7 issue221 OPEN.

## 2026-11-15 — functional delivery priority confirmed

The user explicitly prioritized real-curve QUAD/AFT application integration
over continued fixed-fixture exploration and repeated planning/audits. Updated
STATE.md: isolate concrete defects or necessary prerequisites, correct and
validate them within a bounded scope, then return directly to this functional
objective. Scientific authorization, original policies, ownership contracts,
negative evidence and mandatory closure gates remain unchanged. The exact next
implementation action remains the real source-partition bridge in one feature
PR. No source changes, native tests or new CI campaign occurred in this
preference checkpoint; validate these two documentation files and verify remote
readback after commit. Base b8fa113; main remains f6050ec. R3/M7 open,
adaptive_epochs=0. No additional experiment or milestone was opened.

## 2026-11-15 — original-curve QUAD/AFT executable implemented, qualified feature PR238

Implemented the authorized functional delivery in the primary checkout on
quad/real-boundary-application-20261115; feature commits bfd501a then
79828fcbfc1c4aa20d84576e58f1a3ef8fe2592a, reviewable PR238 to quad-templates.
Actual original serial Generator curve policies/configuration, native refined
tree, source parameters/IDs/XYZ/intervals and original AFT geometry/topology
feed a typed physical initial QUAD/TRI mesh. Snapshot values outlive retired
curve samples; no source sampled-node/native-cell pointer escapes. Replay
preserves original cell IDs, counter, subdivision chronology and ordered leaves.
The old fixed16 mode and default TRI remain preserved. No new scientific
selection/acceptance rule, tolerance, historical input or oracle was changed.

Measured real layout: 37 nodes/16 QUAD/28 AFT TRI; 12 original boundary
intervals, four nonuniform sides, 16 native leaves. OBJ SHA-256
3fbb0c312b81406fb60813caa3ef4b3e76b0b7922208801494b2be61d9d5b03a
matches GNU, MSVC Debug and Clang ASan/UBSan/leak. Fixed16 retains
cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0.
The last locally selected original source attempt has a globally rejected TRI
reference; reference_tri_accepted=0 remains in receipt/OBJ. A coarse accepted
TRI source had only four intervals/four leaves/no interior templates. The new
initial research layout does not override original rejection or count as an
accepted mixed epoch. mixed_adaptive_epochs=0, R3/M7 #221 OPEN.

Exact79828fc: local GNU Release, MSVC Debug and Clang ASan/UBSan/leak pass
fixed16 and real application normal/rollback/existing-output checks; each
profile runs 12 actual source captures/six valid reversed captures/108 corrupt
source-tree negatives. Independent Bernstein/OBJ/source checks reject nine
corrupt artifacts per normal and rollback run. Required root local CTest
passes 85/85; exact hosted run43716128507 passes 4/4, root85/85 and Python527/527.
Local GNU and hosted frozen Eistute five/Book four accepted/rejected states
retain all OBJ bytes, acceptance fields and verified exact boundaries. Local
configured LLVM22.1.8 analysis of five changed TUs emits no diagnostics under
unchanged project filters. Commands/hashes, source scope and open coverage
are recorded in REAL_BOUNDARY_APPLICATION_CLOSURE_20261115.md and its JSON receipt.

Retained failures: initial const legacy getter/config admission issues,
misread original edge len=-1 phase, overly restrictive uniform/source-TRI
preconditions, sequential-ID assumption and a mistargeted Python corruption.
First bfd501a CI3/4 failed explicit new config-asset admission before frozen
comparisons; only that exact new path was admitted. First local delivery
adapter compiled but stopped before CTest on inventory75->85; a fresh85 plan
then passed. LLVM18 could not parse the current ExcludeHeaderFilterRegex;
its zero exits were NOT analysis passes. Installed LLVM22 with actual native
configured metadata passed without disabling a check or changing config.

Created a separate local Blender5.3 inspection scene from the exact OBJ,
showing fixed16 beside the real boundary and its 12 source samples. A separate background process created a new file; automation did not replace
the previous saved scene. The new scene was opened and visually inspected in
Blender. Visualization is not an oracle. Local outputs/raw failures
remain under ignored build/quad-review-20261115 and compiler-specific build
directories; no private machine paths or large binary artifacts are committed.

Concurrent main advanced to ef40c0fc16e6913eb8941f2860ef0deb1ee6bd89 through
documentation-only PR237; preserved without merging unrelated changes into
research. Frozen reference remains f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.
This canonical checkpoint updates STATE/roadmap/milestone/research evidence
only; implementation stays visible in the primary feature checkout. Code,
contracts, tests, docs, scientific scope and unresolved coverage were reviewed.
Independent approval, research integration and exact merge validation remain
unperformed; no M7/full-science or main qualification is claimed.

Exact next action: independently review PR238 at qualified79828fc, integrate
only after required approval/gates, then qualify the research merge before
the queued P2d-1c4b accepted-history/publication work. Keep one active item;
do not start another fixed16 experiment or unrelated audit campaign.

Auxiliary checkpoint documentation attempt: `python tools/quality.py docs`
did not pass in the isolated worktree below `build/`: initial output-directory
absence was corrected, then Doxygen could not resolve three unchanged API
evidence references. Doxyfile excludes `*/build/*`. This is not a successful
documentation build or a new code failure; required integration documentation
checks remain pending from a normally located checkout. Staged whitespace,
JSON syntax and changed-document local targets are checked separately.

## 2026-11-15 ? clarify the actual source-to-mixed execution sequence

The user questioned why the displayed mesh did not show progressive curve
refinement. Verified exact feature 79828fc source/config and retained Windows
reference artifacts; no new native execution. `RunRealBoundaryPatch` runs the
original TRI Generator first, captures curve/native-tree attempts, selects the
last locally selected source with a complete global outcome, then calls mixed
Generate once. Source-step progression is 0: five nodes/four TRI/four boundary
intervals; 1: five/four/four; 2: 21/28/twelve. Step 2 is globally rejected under
the original criterion. The displayed mixed result is 37 nodes/16 QUAD/28 AFT
TRI using that step-2 boundary, not a succession of mixed accepted states.
Confirmed counts by parsing retained OBJ faces and counting singly incident
undirected edges; checked the OBJ source header and RunRealBoundaryPatch.

Corrected the user-facing completion claim: actual curve-discretization reuse
works, but curve refinement is currently driven by the preceding TRI reference,
not by curvature/error on the newly generated mixed mesh. Full coarse-to-fine
mixed feedback remains unimplemented. STATE now states this explicitly. No
formula, code, acceptance policy, experimental scope or prior failure changed.
Remote research e651ec2, main ef40c0f and feature 79828fc were rechecked; PR238
remains open with four successful exact-feature jobs. This explanation does not
rerun or newly certify native, sanitizer, Doxygen or scientific gates.
Next: review the bounded bridge with these limits, integrate only under required
gates, and continue the queued accepted-history/mixed-feedback work with its
scientific approvals. Do not equate one adapted-source export with a completed
adaptive mixed generator.

## 2026-11-15 - investigate coarse curved boundary, return PR238 to draft

User reported that the curved source and progressive meshing behavior were
not represented as expected. Verified feature79828fc, research4d0b404 and
main ef40c0f against live remote. Inspected ModelCurvaBezier, initial meshing,
stable-mode setup, AdaptCurve, RefineCurveSamples, target rebuild and mixed
entry point. Retained CSV/log/OBJ show two final points per curve at step1,
four at step2; pre-consistency targets 8/7/7/7 are clamped to 4/4/4/4. The
curved side has three segments, not twelve; twelve is the four-side total.
Step2 was rejected (growth7, improvement0.456174, score-2.85629). Mixed
publication subsequently uses that source and runs once, with no mixed feedback.
Analytic midpoint/chord distance is0.375; 10,001 samples against exported
curve-0 segments give sampled maximum0.06280875228120662 near t0.1846.
No continuous bound or acceptance tolerance is inferred. Actual intermediate
curve/surface pass counts before rebuild remain unmeasured.

Returned PR238 to draft and superseded integration-ready status in state,
roadmap and milestone register. Added CURVE_DISCRETIZATION_DIAGNOSIS_20261115.md.
Existing source/identity/tree tests do not prove curve approximation or mixed
convergence. Next bounded code action is pass-by-pass parameters/counts and
step/attempt/stop provenance, then correction of the proven cause. Keep prior
accepted mixed-state feedback, estimator/selection approval, ownership/history
and publication gates; do not tune density/acceptance to improve a picture.
No source/formula/configuration/default TRI changed; no new native tests or
scientific qualification. Prior exact-feature evidence retains its bounded
scope; mixed epochs remain zero and functional behavior correction is pending.
Validate changed docs, push canonical checkpoint and verify readback.

## 2026-11-15 - correct curvature clipping and export each physical generation step

Implemented native value observations and domain-selection identity atb0e7852,
analytic-model-first visualization at047c165, then final original-curvature
profile/audit correction ate90d5a30963ed0ade9683c69a530847709188fe3 (draft PR238).
The user initially preserved controls, subsequently explicitly rejected the
stable point clipping. Current opt-in case selects existing legacy curvature
flow; default TRI configurations/formulas are unchanged. Native source points
now reach native tree/QUAD/original-AFT unchanged: curved9 then65, straight5
then17. Four steps/eight OBJ files retain all TRI reference outcomes. Primary
step1 is165 nodes/120 QUAD/68 TRI; generated rejected-source steps2/3 are
953/784/224. Actual reference error increases0.125829 ->0.382516 there; mixed
accepted epochs remain0. Full mixed feedback/approved selection is still open.

Confirmed old stable rejection comes from coherence1.03086 >0.20, not directly
from negative score under ACCEPTANCE_MODE0. Target5.77422 vs28 elements creates
overshoot penalty. New geometric sampled curve distance falls to0.00820232 then
0.000136785; no continuous bound or acceptance tolerance is inferred. All four
sides are Bezier objects but only one is curved; straight-side point growth
occurs in the surface pass, with collinearity retained.

Exacte90 local GNU/MSVC/ASan pass both profiles, actual normal/rollback/negative
histories, six source captures/three reversed/54 native negatives per profile;
eight original-profile OBJ files are byte-identical across profiles. Exact85/85
local and CI43750977300 4/4 pass, including85/85 hosted and527 Python. Native
images matchb0e7852; unchanged-code configured LLVM22 four-TU and local frozen
Eistute5/Book4 evidence is reused with hashes, and final hosted frozen TRI is
independently green. Fixed16 bytes stay unchanged. See portable JSON/review.

Blender5.3 scene with analytic source and four steps saved; opening requested.
User Escape interrupted final visual confirmation; no further UI actions.
Earlier three-step scene was separately inspected. Retain domain-identity and
rounded-OBJ development failures. Doxygen reproduced three unchanged missing
API evidence references in the normal checkout too; prior nested-worktree-only
explanation was incomplete. No Doxygen pass, independent approval, merge,
post-merge/native CRT closure, accepted mixed feedback or1993 equivalence.

Source remains visible in primary feature checkout. Canonical checkpoint is
status/evidence only. Main ef40c0f and other concurrent PRs were preserved.
Next: review profile/export/source identity, resolve required open gates before
integration, qualify any research merge, then continue actual accepted mixed
state/error/selection work under its scientific approval requirements.

## 2026-11-15 - measure TRI/mixed error and localize compounded refinement

User asked whether step1->2 discretization grew too fast and requested TRI vs
QUAD/TRI error. Verified featuree90d5a3, research808e7fa and main ef40c0f from
remote; prior exact-feature checks remain4/4. Read original trace: curve9 ->
curve-pass17 ->surface-pass65, eight->64 boundary intervals; mixed188->1008
faces and165->953 nodes. No controls or source implementation changed.

Measured the eight existing physical OBJ files at identical64x64 and128x128
UV midpoint grids against the original analytic Bernstein surface. TRI uses
barycentric, QUAD inverse-bilinear interpolation; RMS weighted by source area
Jacobian and percentages normalized by source opposite-corner diagonal sqrt8.
At128: step1 TRI0.2147235%, mixed0.1987092%; step2/3 TRI0.03841344%,
mixed0.02185673%. Initial outputs identical2.7178804%. Mixed has2.62x/2.83x
nodes, so no equal-cost efficiency result. Step1 maximum mixed error is slightly
higher even though RMS is lower. Step3 repeats the rejected candidate, not a
new accepted mixed epoch. Same source boundary is preserved by both layouts.

Exact equality with the unchanged existing mixed kernel for every actual mixed
stage/grid; initial equality control and missing-face coverage negative pass.
The local read-only kernel explicitly supports TRI-only sampling without
changing face search/tolerances/weights; no source helper/oracle was edited.
Raw script/logs remain ignored; portable receipt stores script and input hashes.
Native TRI curvature index0.125829 ->0.382516 increases while geometric RMS falls:
these are distinct objectives; no mixed curvature index is supplied or approved.

Added comparison/report/receipt and this state checkpoint. No native generation,
C++ tests, compiler, CI rerun, scientific policy or integration occurred. Review
mixed geometry/curvature/cost criteria and use matched budgets before efficiency
claims. Preserve existing profile/export delivery and R3/M7 gates.

## 2026-11-15 - native aggressiveness sensitivity; count savings versus accuracy

User requested a less aggressive generation test and clarified limits mean
node/element counts. Read live research05b0628, featuree90d5a3 and main ef40c0f;
source worktree stayed clean. Existing C++ library/flags were reused for a small
isolated GNU Release process entry. Default curve base1.414213562 control matches
all eight qualified OBJ exports and curve trace byte-for-byte. Only process-local
inputs vary; no engine/default source or scientific tolerance was edited.

The preregistered base1.10 treatment increased straight-side points5->9 and
17->57, and mixed nodes165->185/953->1073. Its factor also affects coarsening:
flat-segment base*external becomes0.88, reversing growth in requested length.
A separately recorded neutral floor1.0 was consumed (curve factors1.0), but
all eight exports were unchanged. One final coarser fixed external factor1.5
was recorded before execution to cross the exported subdivision plateau.
Total four native cases, no additional sweep. First compilation missing the
private research include stopped before generation; corrected include only and
retained run1. Invalid factor0 rejects before generation and preserves control.

Coarser stages1/2/3: curved3/5/9 points,33/615/843 nodes,16/548/772 QUAD and
24/122/126 TRI. Same-site128-grid RMS percentages0.830346/0.290323/0.267236,
versus control0.198709/0.0218567/0.0218567. Step2 saves35.47% nodes but has
13.28x geometric RMS and TRI minimum shape quality0.0398114 versus0.245704;
QUAD corner Jacobian minimum0.520605 versus0.851067. The interior still jumps
16->548 QUAD. Considering nodes/RMS alone, coarser stages2/3 are worse than
control step1. No optimal/default setting is inferred; coarser first stage may
only suit a looser as-yet unspecified geometric target.

All exported states pass existing independent UV/source/disk checks and sampled
coverage; new mixed metrics exactly match the unchanged64/128 kernel. Paired
control/neutral metrics reuse byte-identical data. This does not prove global
physical bounds or continuous error. Coarser reference TRI steps are accepted,
but no mixed scientific acceptance follows. New MSVC, ASan, CTest/CI, peak memory,
runtime benchmark and equal-error optimization were not performed. Prior source
qualification remains its own unchanged scope.

Added study, portable receipt and current state/roadmap evidence. Raw programs,
configs/plans/logs and copied OBJ files remain in ignored experiment directories.
No variant was adopted and no integration/stage closed. Next: separate boundary
fidelity and interior size-field damping, specify geometry/quality/growth targets
on actual mixed states and obtain the required scientific/independent review.


## 2026-11-16 - explain boundary versus interior refinement and step2 override

User asks why the interior grows faster than the curve and whether AFT controls
both. Read exact feature e90d5a3 source and retained coarser native CSV/OBJ without
rerunning generation. Correct prior wording:33 ->615 are total mixed nodes.
Boundary intervals8 ->10, source leaves16 ->136, QUAD16 ->548. Domain uses old TRI
surface-curvature/size inputs, separate from one-dimensional boundary intervals;
QUAD templates precede the exterior original AFT reconstruction.

New concrete finding: configured patch bounds1.5 do not keep the domain factor
constant. Existing step2 ranked-patch override lowers it to1.0 here; raw domain
CSV confirms1.5 ->1.0 and smoothed h mean0.280969 ->0.0901984. No counterfactual
isolates that rule from changed previous-TRI inputs, balancing and template
selection. Append exact measurements, artifact hashes and source mechanism to
the sensitivity report; preserve prior observations and refine state/roadmap.

Remote main ef40c0f, canonical entry fbf38b5 and feature e90d5a3 were checked.
PR238 remains draft with4/4 successful existing exact-feature checks; unrelated
PR214/225 remain untouched. No production code/default or formula changed. No
new native run, CTest, sanitizer, CI, merge, scientific adoption or closure.
Documentation/whitespace and checkpoint checks are recorded by the commit.
Next action: reconcile configured-factor semantics and the historical step2
override, classify intended policy versus a behavior-changing defect repair,
then define the smallest authorized correction/test without changing TRI by
accident. Mixed adaptive feedback/acceptance remains open.


## 2026-11-16 - opt-in domain bounds repaired, tested and opened in Blender

User authorizes fixing the conflicting step2 factor, repeating tests and showing
all steps in Blender. One work item: a behavior-changing configured-factor defect
repair under new curved_bezier_bounded_domain_vertex_mean_v1. Existing historical
TRI, original-curves/fixed16 cases, formulas, ordering, acceptance/stopping and
ownership remain unchanged. New case clamps the ranked step2 override into the
configured interval. Feature source e8ac72e plus generated inventory refresh gives
exact delivery d59a513a04ea8c9573e006789641f4adbeecedee, pushed to draft PR238.

Actual factors1.5/1.0/1.5 ->1.5/1.5/1.5, curved points3/5/9 unchanged. Mixed nodes
33/615/843 ->33/281/797; step2 QUAD548 ->242 and source leaves136 ->67. Step2
geometric RMS0.290323% ->0.420207%, TRI minimum shape0.0398114 ->0.135358,
QUAD minimum scaled Jacobian0.520605 ->0.429872. Step3 RMS0.275132%,797 nodes,
TRI minimum0.0398114. Counts improve at a cost in geometric error; no uniformly
better or optimal mesh is claimed. Paired TRI/mixed64/128 sampled error and quality
receipts retained; old metrics reused only for identical inputs. Old default and
old coarse each reproduce all eight prior OBJ bytes. New mixed kernels exactly
agree with the existing independent common-grid implementation.

Exact final revision: GNU Release, MSVC Debug and Clang ASan/UBSan/leak detection
pass five-case old/new tests, rollback and corruption controls. Profiles agree
on all case reports/OBJ hashes. Each also passes fixed16, original/stable traces,
six native source captures, three reversed captures and54 negatives. Required
baseline85/85 passes via validation_session, report1794828785596882800-532fdd13;
six configured LLVM22 TUs have no visible first-party diagnostics. New GNU TRI
Eistute5/Book4 exactly match frozen f6050ec OBJ/acceptance with boundary coverage.
Exact hosted CI43859454045 completes4/4 SUCCESS. Added opt-in case explicitly to
the scientific comparison's reviewed config assets; no other guard relaxed.

Retain initial header-format hook failure, stale architecture inventory gate,
two harness-copy BOM syntax failures before native execution and direct protected
Blender binary access denial. Apply only the indicated bounded corrections:
format the new method; regenerate changed source/hash inventory; copy scripts
with explicit encoding; use the installed application launcher. No hidden native
retry, tolerance relaxation or permissions change. No new Doxygen/full CRT gate;
prior limitations and independent approval remain open.

Blender5.3 scene created from actual final MSVC archive, eight objects/four states,
analytic model at left, TRI above mixed. Source geometry is not scaled/smoothed.
Opened and visually confirmed the correct named window, enlarged and saved its
viewport. File:build/quad-domain-bounds-d59a513/QUAD_TRI_domain_bounds_steps_analytic.blend.

Remote main ef40c0f and canonical entry2136130 remain distinct; concurrent work
on unrelated branches and PR214/225 was inspected and untouched. Updated state,
roadmap, delivery report and two portable receipts; no merge, stage closure,
accepted mixed feedback epoch or post-merge/main qualification. Next: independent
review of PR238, then resolve retained integration gates. A later h-growth policy
requires declared geometry/quality/cost targets and scientific alignment; fixed1.5
is not adopted as an optimal default. R3/M7 remains OPEN.

Final checkpoint whitespace check exposed CRLF in the copied comparison receipt.
Normalize that new file to LF and verify identical parsed JSON before publication;
retain the rejection as a documentation failure, not a native test failure.


## 2026-11-16 - prioritize local bidirectional curve-transition-interior balance

User observes a coarse-looking curve beside increasingly refined interior and
requests a balance factor that can improve boundary discretization when transition
elements suffer, while avoiding excessive low-curvature refinement. Prioritize
that functional coupling; the completed factor-bound repair alone does not solve
it. No new algorithm or numeric threshold was adopted in this session.

Read current remote state and exact d59a513 source. Existing stable-mode density/
structural responses are not generally active in the current legacy research
case. ComputeCurveDomainBalance returns1 for nonpositive target h, matching the
neutral1 in all corrected-run records; this is not evidence of measured balance.
Current regional coupling statistics use TRI FaceList and source history remains
TRI-driven, not actual mixed feedback. No new native execution or measurement.

Add LOCAL_BALANCE_COUPLING_PROPOSAL_20261116.md with a concrete local size/geometry/
quality feedback contract, shared-curve synchronization, units, graded neighbors,
bounded/hysteretic requests and cause checks for poor AFT/transition elements.
A straight interval may need local compatibility points; a distant high-curvature
region must not force uniform global refinement. Missing measurements are
unavailable, not a pass. Retain all existing defect-repair outputs and failures.

Plan one opt-in coupling capability, rather than another global-factor sweep.
Next: align the physical metric, local neighborhood and error/quality/spatial/
per-step controls with advisors, then implement the bounded mixed-feedback slice.
This is a scientific proposal under AGENTS.md; no formula, weights, limits,
acceptance/stopping policy or mixed scientific adoption is implied by the user's
direction alone. Preserve original curve algorithm, quadtree/templates, AFT,
shared identities and rollback/rejected trace contracts.

Remote main ef40c0f, canonical entry c37201a and feature d59a513 verified; PR238
remains draft with4/4 existing exact-head checks successful. PR214/225 untouched.
Changed proposal/state/roadmap/session documentation only. No native build, test,
CI or new Blender scene; existing85/85/three-profile evidence is not extended to
this proposal. Documentation whitespace/link and scope review precede checkpoint
publication. Independent review, Doxygen/CRT and R3/M7 remain open.


## 2026-11-16 - preserve native TRI and QUAD templates in Blender history

User requests the template reference before any next algorithm step. No balancing
implementation or scientific decision is advanced. Extract six canonical native
quadtree neighbor signatures from the unchanged d59a513 GNU engine library.
Original makeTemplateBasedMesh yields TRI2/3/6/6/5/6; EmitLeafQuads with the live
vertex-mean rule yields QUAD4/11/8/12/11/16. Output is normalized for display;
actual nodes/faces are retained. These are representative implemented families,
not proof of every rotation/quality branch or per-step usage of all six. Exterior
AFT triangles are dynamically generated, not these fixed interior templates.

Bounded standalone native exporter compiled/executed successfully. Twelve planar
audits check coordinates/indices, positive area, boundary/manifold/connected disk
and Euler contracts; a reversed-face negative is rejected. Retain the first
checker-selection failure: the physical curved-patch helper rejects flat UV
coordinates under its different input contract. Switch explicitly to a planar
auditor, without altering native output. No application/source change, native
regression campaign, new CI or scientific qualification.

New Blender5.3 file QUAD_TRI_history_with_templates.blend contains the original
analytic/four-step generation scene and a separate labeled template gallery.
Original file hash and all original mesh coordinate/connectivity snapshots are
unchanged. Opened and visually confirmed all12 TRI/QUAD panels with split-side
highlights. Stored portable catalog, image/source/compiler receipt and Blender
recipe under docs/research/quad/visual plus TEMPLATE_GALLERY_20261116.md.
Local blend/raw files remain in ignored build/quad-template-catalog-20261116.

Remote main ef40c0f, canonical entry20c37c6 and feature d59a513 checked; existing
PR238/214/225 and source branch untouched. Update state/roadmap and append this
checkpoint; Python syntax, documentation whitespace/links and metadata scope
checked before publication. No merge or stage closure. Next remains the local
coupling proposal with advisor-aligned metrics/criteria, retaining PR238 review,
Doxygen/CRT and R3/M7 OPEN.


## 2026-11-16 - clarify structural versus numerical1993 template correspondence

User asks whether the Blender templates match the1993 article. Re-read current
checkpoint and M1 source/centroid reviews, verified original PDF SHA25649d297e2...
and5439448 bytes, rendered/read all printed page288 and Figure7 detail through
installed Poppler. Default Python lacked PyMuPDF; no package installed. Public
coauthor bibliography confirms citation only, not template topology. Local scan
and renders remain untracked and are not redistributed.

Confirm six split-neighbor families/QUAD intermediate polygon connectivity and
printed order T1,T2,T4,T3,T5,T6 versus gallery source-number order. Distinguish
article lower-row intermediate polygons from gallery final subdivided QUAD faces.
Numerical centroid equation remains unspecified in the paper; current vertex mean
is not generally area centroid. TRI quality-dependent centers/diagonals also
prevent a literal-coordinate reproduction claim. The diagram supplies no numeric
point oracle. Added this comparison and limits to TEMPLATE_GALLERY_20261116.md;
no historical formula adopted, scientific milestone closed or file regenerated.

Remote main ef40c0f, canonical entry d6eeb3d and feature d59a513 verified. PR238
remains draft with four existing exact-head checks successful. Source and gallery
geometry unchanged; no new native build/tests/CI or Blender action. Documentation
checks and remote checkpoint readback only. Next remains advisor alignment of
historical point formula/local coupling criteria and existing PR238 review, with
M1 partial and R3/M7/known Doxygen/CRT obligations retained.


## 2026-11-16 - align generated template meshes and intermediate polygons

User clarifies that the desired reference is a combined view: last TRI/QUAD
examples with intermediate polygons immediately below in the same scene/file.
Extend only the isolated native extractor to emit CaptureLeafPolygons cycles;
no production source or balancing algorithm changed. Original12 template arrays
are byte/value-identical; add six polygon panels1/3/2/3/3/4 and audit all18 planar
disks. Native compile/export completes successfully against the unchanged d59a513
GNU library. This is diagnostic/presentation evidence, not a new scientific gate.

Add extended portable catalog, receipt and three-row Blender recipe. New scene
shows TRI in orange, QUAD in teal and source polygons in purple, aligned by T1-T6.
Source history file and mesh snapshots are unchanged; its analytic/four-step
history remains in another scene within the new file. Opened the correct Blender5.3
window and visually confirmed all18 panels together. Old gallery files preserved.
Result:build/quad-template-catalog-20261116/with-polygons/QUAD_TRI_templates_and_polygons.blend.

Entry canonical90fdd5d, feature d59a513 and main ef40c0f remain distinct. No new
application build/regression/CI, scientific centroid approval or stage closure.
Check Python syntax, documentation whitespace/links and remote readback for the
checkpoint. Next remains local coupling/advisor alignment and PR238 review;
this requested historical visualization is completed first. M1/R3/M7 and known
Doxygen/CRT limitations remain open.


## 2026-11-16 - clarify historical mixed regions and missing exterior pairing

User asks whether the article mixes QUAD/TRI in all internal quadrants. Re-read
complete scanned pages289-291 with installed Poppler and prior page288, verify
primary PDF hash49d297e2..., and inspect exact d59a513 current exterior AFT and
candidate face assembly. Source interpretation supports mixed final elements,
not unrestricted mixed templates in every interior cell. Interior QUAD branch
subdivides source polygons into QUADs; remaining-region boundary contraction can
join triangles into QUADs when its quality condition permits and retain TRI
otherwise. Page289 explicitly reclassifies a geometrically internal-looking
cell near a reentrant contour as boundary, so that region is not a uniform ring.
Do not count quadtree boxes as finite-element QUAD merely from the drawing.

Record a concrete gap: current AttemptExteriorTriangulation and candidate assembly
append original AFT triangles without the historical optional remaining-region
pair-to-QUAD treatment. Seeded QUAD plus exterior TRI is not full1993 equivalence.
Add this to the existing M5 coverage inventory and gallery comparison record;
no new algorithm, threshold or historical scientific approval. Keep balancing
feedback separate from element-type pairing. No source/Blender change, native
build/test or new CI. Scanned pages/renders remain local/untracked.

Entry canonical aa1d9fd, feature d59a513, main ef40c0f and PR238 current status
verified. Existing PR238 four-job qualification remains its own scope, draft and
unmerged. Check documentation whitespace/links and remote readback. Next stays
advisor-aligned local coupling and PR238 review; M5 historical pairing coverage,
M1 point rule, R3/M7 and Doxygen/CRT remain open.


## 2026-11-17 - realign implementation around integrated mixed filling

User requests implementation/documentation alignment with the discussion. One
work item: engineering preparation of actual mixed fill, followed by actual mixed
accepted-state/error feedback and then local curve-transition-interior balancing.
The previous balance-first successor is explicitly deferred, not deleted. No
historical numerical pairing rule or new adaptive factor is activated.

Implement value-only CollectBoundaryPairCandidates and integrate two source-scoped
CSV inventories into each real-boundary archive. Record actual adjacent exterior
TRI source faces/vertices/shared edge/four-node boundary cycles, not invented
accepted QUAD elements. No-seed initial TRI source states are not applicable.
Candidates may conflict/be geometrically bad; selected0/not_evaluated is explicit.
No mesh/source/acceptance mutation or physical owner transfer. This completed-
output inventory is not the article's in-front algorithm or a greedy postprocessor.
Implementation contract preserves distinct future native-template/AFT-pair origins
and requires reversible physical publication before a selected pair can be used.

Initial local commit6c5ec716f4262a2011f6087b16635f186e00416c passed85 and native
three profiles. Git CLI push and PR edits were refused403; the authorized GitHub
connection can write contents. Publish identical tree00315980ea56546c7393d0b4fb20f7684a9273ec
as7fc988d30b27f08f620a68e4804ce453270774bd with screened metadata and a leased
fast-forward update. Preserve6c5ec71 on local branch quad/local-mixed-prepublish-20261117;
synchronize the clean working branch by creating the published-head tracking
branch without changing file contents or overwriting concurrent work. No machine
credential/permission changes or force push. Exact-head checks repeated after
remote commit identity changed. Retain the first refused publication and bounded
payload/schema transport failures before ref update; none is native qualification.

Exact7fc988d local85/85, GNU Release/MSVC Debug/Clang ASan+UBSan/leak histories,
source controls and new read-only diagnostics pass. Each profile has four topology
cases/five invalid controls and old six captures/three reversed/54 negatives.
Independent CSV reader checks actual OBJ adjacency/orientation/cycle boundaries;
four forgeries per bounded normal/rollback are rejected. All five cases/40 prior
OBJ files per profile remain byte-identical. All profile case reports and new CSV
bytes agree. Current-GNU frozen Eistute5/Book4 exact OBJ/acceptance and verified
boundaries pass. Two configured LLVM22 TUs/header consumers have no visible
first-party diagnostics on the identical source tree. Local report1794907572218082900-2b73e7b8;
exact hosted run44055409865 completes4/4 SUCCESS. No extra scientific sweep.

Update README/source implementation contract on the feature, canonical state,
roadmap, deferred balance proposal, realignment plan and portable receipt. Code,
contracts, real/negative tests, documentation, scientific scope and remaining
failure/coverage obligations reviewed explicitly. No scientific stage closure,
merge, full CRT/Doxygen qualification, mixed accepted epoch or new Blender mesh.
Existing centroid/M1, full M5/M7, Doxygen/CRT and independent review remain open.

An async factual question asks whether advisors aligned Figure11 shape threshold,
UV/XYZ interpretation and pair priority; no answer/approval is recorded. AGENTS.md
requires explicit advisor alignment before numerical changes. Next concrete
step: settle those choices, then implement in-front selection/typed reversible
pair publication with TRI fallback. Keep new balancing policies after that fill
capability. Source/canonical head, branches and open PRs were checked; unrelated
PR239/225/214 untouched. Canonical entry15e469d, source base d59a513 and main
ef40c0f are retained separately; checkpoint publication/readback is explicit.

The first documentation whitespace invocation used the source worktree rather
than the canonical documentation worktree and stopped on a missing canonical-only
file. Correct the working directory; the seven-file check then passes without
content relaxation. This is a tooling-scope failure, not a native test failure.


## 2026-11-17 - decide the opt-in pair quality space and deterministic ordering

The user asks for technical guidance and explicitly delegates these adjustments.
Resolve the prior generic questionnaire with physical_angle_pair_v1, documented
in MIXED_FILL_PAIR_POLICY_20261117.md: retained S<=1.5, physical XYZ corner
angles, existing four-corner UV and physical validity, minimum S_XYZ, exact-tie
physical edge ratio then original frontier order and stable source IDs. Preserve
valid TRI when no acceptable pair exists. This is an experimental curved-surface
choice, not formal advisor sign-off or source-certified1993 XYZ reproduction.
No numerical selector, formula/tolerance/adaptive change or source publication.

Read actual archived MSVC Debug candidate CSV and stage OBJ data from exact
source7fc988d: original-default/original-coarse/bounded-coarse adapted steps1-3,
including rejected TRI reference stages. Deduplicate full XYZ/UV/connectivity:
9 observations contain7 distinct geometries and760 overlapping topological pair
observations. Existing validity plus angular rule:244 UV-eligible,138 XYZ-eligible,
108 UV-only,2 XYZ-only. UV-invalid410/physical-invalid180 overlap. Among61 base
TRI observations with multiple common alternatives, score-space ranking differs
in15; these diagnostic keys do not exercise the future full live-front rank.
No pair is selected or accepted; candidate counts cannot predict disjoint QUADs.

Command python build/quad-pair-policy-20261117/compare.py computes both spaces
from unchanged source-scoped OBJ nodes. Three analytic controls: squareS1,
sheared physicalS1.7048327646991335, inverse-chart physical-squareS1 despite
distortedUV. Count consistency and input CSV/manifest SHA-256 assertions pass.
Portable JSON retains analyzer/source/input hashes, witnesses, controls and
limitations. Analyzer/raw archives remain local, not a self-contained rerun
bundle. The parameterization examples support metric choice, not global error,
convergence, optimality, continuous validity or full1993 reproduction.

Fresh remote audit: main ef40c0f, feature7fc988d, canonical entry c05ff0b, open
draft PR238 and exact source4/4 SUCCESS run44055409865. Other open PR239/225/214
untouched. No new native build/generation,85-test baseline rerun, sanitizer/CI run
or Blender session. Prior exact-source evidence remains scoped to read-only
inventory. A PowerShell rg wildcard path was rejected by Windows; corrected
file discovery has no bearing on scientific validation.

Update canonical state/roadmap/implementation/realignment and append this entry;
preserve prior history. Check documentation whitespace, local links, JSON,
non-documentation identity and neutral publication metadata, then publish the
canonical checkpoint through the authorized GitHub connection and verify remote
SHA/blob readback. CLI write access was previously refused403; no retry or
credential change. This is a decision/diagnostic checkpoint, not stage closure.

Next concrete action is the opt-in original-front implementation with distinct
AFT-pair provenance, reversible physical owner transaction, TRI fallback and
positive/rejected/tie/rollback contracts, then finite native/exact-head gates.
No additional generic questionnaire on these three choices. M1 point convention,
M5/M7, accepted mixed epochs, local sizing feedback, Doxygen/full CRT,
independent review and integration remain open.


## 2026-11-17 - audit continuity and deliver incremental physical-angle pairing

User requests plan update, audit to date and continuation. Read current canonical
protocol/state/roadmap/log and separate modernization sources; verify clean local
worktrees, actual main/research/feature refs and open PR/checks. Git read initially
reset; use connected GitHub reads and subsequent bounded fetch without changing
credentials or overwriting concurrent work. One active item remains mixed filling.

Audit confirms prior real-curve/QUAD/AFT capability and read-only7fc988d candidate
inventory, not an implemented selector. Implement the existing user-delegated
physical_angle_pair_v1 behind separate curved_bezier_live_pairs_vertex_mean_v1.
Add synchronous empty-by-default AFT triangle observation after face ownership,
including the shortcut; an exception aborts the disposable one-shot owner. Select
among actual already-emitted neighbors, preserve original TRI trajectory, require
existing UV/physical validity and S_XYZ<=1.5, exact-tie edge ratio/current edge
order/source IDs, and consume TRI once. Preserve unmatched TRI. Build a new typed
physical owner with separate native-template/AFT-pair origins and prepublication
validation/fault rollback; retain source node IDs and shared curve partitions.

Add source scaffold OBJ, source-scoped live event/stage CSV and final-face origin
comments. Track independent replay of every actual alternative, score/validity,
choice, disjoint consumption, resulting faces and origin IDs. Reject six forged
source/cycle/score/face/generation/acceptance records. Add native shape/chart,
competing-choice, three rank-tie/three bad-topology cases and four shortcut/
cleared/throwing-observer cases. Keep old malformed topology/source/reversed,
initial/rejected source states and nonempty owner histories.

Preserve failed development logs: wrong AssertionError catch, ambiguous fixture
names and a declared-but-undefined legacy helper, strict formatter literal reflow
and PATH lookup, stale architecture inventory before baseline, and the older
owning-snapshot warning exposed by expanded header analysis. Correct precise
causes, retain the independent snapshot via owning range construction, and keep
configured diagnostics. Scoped formatting retains tokens; no broad format/tidy
fix or scientific tolerance change. Inventory regeneration preserves35 contracts/
277 anchors. A bounded shell metadata-query quoting failure changes no profile.

Local source5203c0e publishes identical tree as140ed85 through the authorized
GitHub connection; CI registration and architecture receipt follow as8f7b7d5 and
0417a5a. Preserve unpublished local identities on local backup refs. Exact0417a5a
passes85/three native/frozen scopes. Synchronizing canonical3cf8d21 into the
feature resolves one add/add implementation-document conflict while preserving
native/test inputs; identical merge tree publishes as518a7a4 with both parents.
Repeat exact-head checks. Hosted44178168367 fails before science comparison
because the exact new config is absent from the reviewed asset list. Retain its
decoded job log/hash; add only that reviewed asset and keep the unreviewed-config
negative rejection. No unchanged failed campaign retry or hidden fallback.

Final exact feature6f4ef473b2d248548632d4e0f358f8eea4749f86/tree56412019 qualifies
the bounded slice: local85/85 report1794950586476829500-eb4b3a1e; GNU13.3 Release,
MSVC19.44 Debug and Clang18.1 ASan/UBSan/leak real/new/prior/fixed16/source/rollback
histories pass. Forty old OBJ per profile match7fc988d; twelve new history OBJ
match across profiles. All trace lineage/topology/selection agrees; four MSVC
score fields differ by at most4.440892098500626e-16. Configured LLVM22 five-TU
coverage reuses four unchanged native TUs and repeats the affected first-party
test headers on final head without a line filter, passing. Current GNU Eistute5/
Book4 match frozen f6050ec OBJ/acceptance and verified boundaries. Exact hosted
44179166105 completes4/4 SUCCESS, including live-pair Linux/Windows/sanitizer
audits and full baseline/science. Prior-head results are not substituted.

Measured adapted paired counts2/0/3, nodes33/281/797, final QUAD18/242/727 and
TRI20/66/124. Step2 rejects42 UV unions and24 angular shapes. Same-site24x24
source-area RMS increases approximately0.0927% at step1 and0.0000506% at step3;
step2 is unchanged. Preserve this negative/tradeoff result; neither node-count
control, global-error improvement, optimality nor accepted mixed feedback is
demonstrated. Source adaptation remains TRI-driven, mixed_adaptive_epochs=0.

Explicit closure audit covers code/owners, tests, contracts, documentation,
scientific scope and failure/coverage inventory. Update canonical state/roadmap,
implementation contract, finite audit and portable evidence; append this entry.
Publish/read back the canonical checkpoint with a leased fast-forward and clean
worktrees. Native tests and GitHub write access are available. No new Blender
display, main modification, integration, full CRT/denial/Doxygen closure or
independent approval. Unrelated open PRs remain untouched. Next: independent
review/research integration qualification of PR238, then actual mixed accepted
error feedback, then local curve-transition-interior balance. Keep M1/full M5/
R3/M7 and isolated topology-phase-only coverage explicitly open.


## 2026-11-17 - independently review PR238 and repair bounded integration prerequisites

User requests continuation and explicitly authorizes two separate technical
reviewers. Recheck clean source6f4ef47, canonical fae255e, main ef40c0f, PR238,
reviews/threads and exact CI44179166105 success. No external review submission
or independent advisor approval is fabricated. Baseline report hash and current
three native application image hashes match the qualified receipt; no identical
native campaign is repeated for the initial source review.

Ownership review traces owner-before-callback, exception disposal, copied
captures, stable source observers, typed owners and reciprocal retirement;
no concrete bounded defect. Retain ordinary observer-abort/allocation-denial
coverage limits. Scientific review verifies85 exact IDs, histories/retries,
physical rule, independent checks, native/frozen evidence and negative error
results. It identifies the still-required three documentation references and a
nonblocking unaccounted-extra-CSV-row checker gap.

Run unchanged Doxyfile from normal checkout:2742 diagnostics including the three
unresolved API links. Replace exactly those links with immutable ef40c0f targets
whose Git blobs match. Afterward zero unresolved refs; generated index.html has
all three hrefs; all remaining2739 diagnostics match exactly. Full Doxygen
continues to exit1 (2731 undocumented API and8 other unchanged diagnostics).
No suppression, relaxed warning policy, input exclusion or full Stage8 success.
Independent follow-up explicitly accepts the specific reference/rendering
prerequisite repair; broader debt remains open and earlier wording is disposed
explicitly in STATE/roadmap rather than silently waived.

Harden tracked Python checker with unique full-scope grouping before replay,
no-seed refusal and total220-event accounting. Add extra foreign-scope/initial-
stage records to existing six negatives:8/8 reject with2/0/3 selected pairs and
nonempty rollback. This development uses the unchanged qualified MSVC app; old
GNU/ASan results remain old-checker evidence. Exact follow-up local b9fd49e
changes only docs/API_CONTRACTS.md and the checker; technical re-review finds
both findings resolved. Reconcile canonical fae255e documents into the candidate
without native/scientific source changes. Record reviewed blobs and conditions.

Next is final remote-head qualification, guarded quad-templates integration and
exact post-integration validation before a subsequent stage. This entry does
not claim those unexecuted results, modern-main integration, numerical adoption,
advisor approval, a Blender display or whole scientific/CRT/documentation closure.
Keep one package and preserve broader M1/M5/R3/M7, continuous validity and full
new-path denial obligations. Authoritative closure results follow the actual gates.


## 2026-11-17 - qualify and integrate reviewed PR238, then revalidate research merge

After independent reviews and measured bounded API-reference/complete-CSV fixes,
publish identical reviewed candidate tree81ecc5bf as f2bd90daf46e7c4a7011e948d6ec72189a568d32,
parents reviewed6f4ef47/canonical fae255e. Local c84255b and preceding unpublished
b9fd49e/follow-up history remain on a local backup branch; remote commit identity
is recorded separately. Screen parent/tree/publication metadata and leased ref.
Candidate85/85 report1794954722678277300-22fc9dd8 and actual corrected checker
executions on GNU/MSVC/Clang ASan+UBSan/leak pass:220 events,8 rejected controls,
normal/unpaired/nonempty rollback. Images match6f4ef47; production/native/config/
scientific inputs are unchanged. Older six-control results retain their scope.
Exact hosted44190789988 completes4/4 SUCCESS. No new numerical policy.

Recheck remote fae255e/f2bd90d/main ef40c0f, PR identities, clean tree and exact
four checks. Mark the reviewed PR ready and use expected-head guarded merge
into quad-templates only. PR238 merges as d251f19139267ad3b0cd3515aade0a23fed560ca,
parents fae255e/f2bd90d and exact qualified tree81ecc5bf. Verify remote readback.
No force update, automatic main merge or unrelated branch modification.

The qualified-main helper is explicitly main-only and inapplicable to this
research branch. Verify identical merge/head trees and clean checkout, snapshot
all2637 tracked file hashes/mtimes, switch directly to exact merged research
commit without first checking out an old base, and verify all bytes/write-times
preserved. Fast-forward the separate canonical worktree. No hook bypass or
modernization-main ref/checkout change. Current actual artifact images match.

Exact research merge passes85/85 report1794955203909230300-f1cb064c. Execute
source/reversed/negative native contracts, corrected8-control live checker and
actual original/stable accepted/rejected/retry histories on GNU13.3, MSVC19.44
Debug and Clang18.1 ASan/UBSan/leak. All pass. Native reuse is documented for
identical inputs/images, not a claim that binaries were recompiled on this SHA.
Hosted push44192096506 checks exact d251f19 and completes4/4 SUCCESS, including
fresh compiler/native/sanitizer, full baseline and frozen TRI evidence.

Keep full Doxygen exit1/2739 other unchanged diagnostics; the specific three
reference/rendering obligation is repaired and independently inspected. No
diagnostic suppression, false full documentation pass or stage closure. Retain
ordinary observer abort/new-path denial/full CRT coverage gaps. Mesh2/0/3 pair
counts,33/281/797 nodes and sampled error increases remain; adaptive_epochs=0.
No source physics, thresholds, acceptance/stopping or default TRI changes.

Explicit closure audit covers code, tests, contracts, documentation, scientific
scope and known failure/coverage inventory. Record candidate/merge receipts,
source hashes and passed versus retained scopes; update STATE/roadmap and link
older candidate/review checkpoints to this qualified integration. Publish and
read back the canonical documentation checkpoint; leave the primary worktree
on the current quad-templates research branch without rewriting native inputs.
Next is R3 actual mixed-state/error observations and retained-history connection
before scientifically aligned mixed acceptance and local sizing. Broader M1/
M5/R3/M7, continuous validity, full CRT/denials/Doxygen remain open. No new Blender
display, main integration or claimed scientific optimum. One package closed.

## 2026-11-17 - clarify article-style mixed generation before adaptive feedback

The user corrects the meaning of "real mesh": generation by the 1993 mixed
TRI/QUAD procedure, not just real Bezier geometry or a paired TRI-driven output.
Recheck clean quad-templates d5b6175 and live remote equality; main remains
ef40c0f. Fresh delivery audit observes concurrent draft PR239 at e20d77e and PR225 at
7fe0f39 (both advanced since entry), and PR214 at 7cd5014. Leave all three
unrelated branches untouched. Research merge CI44192096506 remains SUCCESS.

Directly inspect the primary seven-page scan (SHA-256 recorded in
ARTICLE_MIXED_FRONT_TARGET_20261117.md), printed pp288-290 and Figures7/10/11.
The article chooses the best triangle and prospective adjacent alternatives on
its two other sides, evaluates shape, then updates the front for the selected
TRI/QUAD. Inspect original makeMesh and the research observer: current TRI
front mutation precedes pairing of already committed triangles. Also retain
the unresolved original geometry-phase/existing-node candidate-search and
centroid differences; current tests do not establish historical equivalence.

Correct STATE and the current roadmap queue: one active successor is an opt-in
prospective mixed-front path and validated static mixed mesh/Blender output.
R3 mixed-state/error feedback and local size coupling follow this output.
Preserve the qualified prototype/default TRI, all integration receipts, sampled
error increases, zero mixed adaptive epochs and full M1/M5/R3/M7/native limits.
Do not transfer prior test passes to the unimplemented path or promise a date.

Native Windows Poppler rendered pages5-6 successfully after a failed WSL
pdftoppm attempt (tool absent). Keep local logs; redistribute no paper pages.
Documentation-only session: no native build/test, algorithm change, newly
generated mesh or Blender display. Next action is the explicit opt-in mixed
contraction implementation and its bounded output gates, not another R3-only
preparation package. Commit the canonical checkpoint with leased remote update
and verify readback before reporting persistence.

## 2026-11-18 - implement prospective mixed front and display actual output

Resume canonical868f518/main ef40c0f and the article-style functional priority.
Keep one source feature and preserve concurrent PR239/225/214. Implement opt-in
existing-node UV contraction using native leaf neighborhoods, maximum included
angle, two prospective neighbor alternatives and planar S<=1.5. Select first,
then commit the TRI/QUAD contour update. Preserve default TRI, old pair mode,
source curves and native templates. Record source-ID/side ties and experimental
vertex-mean/curved-lift scope without claiming formal advisor approval.

Generate33/281/797 nodes,24/249/738 QUAD,8/52/102 TRI;191 commits and194 OBJ frames.
Independent replay checks search/shape/ranking/front/source identity and8 forged
traces. Native controls cover direct QUAD, retained TRI, poor union, island,
precommit abort and deterministic retry. Initial list/tuple checker comparison
fails; normalize representation only. Initial MinGW direct launch produces no
compiler artifact; retain it without a compiler-pass claim.

Publish treeecd7662e as b434034 (local e1f1281 retained), draft PR240. Baseline
first stops on stale inventory; regenerate with35 contracts/277 anchors intact,
then pass85/85 at b434034. Hosted44271313083 rejects the unregistered new config
before frozen science. Register only that reviewed asset; final b3d2fbc (local
111764e retained) differs only in workflow metadata and passes exact local85/85
and hosted44271951483 all4 jobs. Hosted native contracts19/19 on both platforms;
GNU/MSVC/ASan+UBSan+leak article reports agree with8 forgeries and rollback.
Frozen Eistute5/Book4 science and configured LLVM22 full affected-TU/header/new-
contract analysis pass. No diagnostics suppressed or numerical policy relaxed.

Local MSVC source/reversal/negative, old/new modes and original accepted/rejected/
retry histories pass. Compiled inputs/image are identical across b434034/b3d2fbc;
do not claim fresh compilation on the CI-only follow-up. Local GNU and sanitizer
Windows-mount runs stop on denied directory rename; sanitizer normal generation/
replay completes, rollback publication fails. Later jobs are unstarted. Retain
both failed prefixes as incomplete local gates, not replaced by hosted passes.

Same24x24-site independent source-area RMS versus unpaired output rises1.1217%/
0.1323%/0.3667%; node counts unchanged. Preserve these tradeoffs. Blender5.3
comparison includes analytic model, TRI/mixed histories,18 template/polygon panels
below and actual-commit animation. Initial installed UI is hung and packaged
execution denied. The user closes it and explicitly requests retry; the launcher
then creates the new file and its actual window visibly shows the mixed meshes
and templates. Render inspected, historical file hashes preserved.

Audit code/tests/contracts/docs/scientific scope/failure inventory in
ARTICLE_MIXED_FRONT_DELIVERY_20261118.md and its portable receipt. PR240 remains
draft/unmerged. Next: independent mixed-front review, local-filesystem failure
disposition and required exact research-integration/post-merge gates. R3 and local
balancing follow qualified integration. Full M1/M5/R3/M7, smoothing/continuous
validity, new-path full CRT/denials and Doxygen2739 remain open. Commit/read back
the canonical checkpoint; primary checkout retains the visible source candidate.

## 2026-11-18 - explain pure TRI versus mixed generation with named references

User requests detailed technique comparison. Recheck canonical660d0ad and source
b3d2fbc/PR240 draft/unmerged, read current state and actual archived outputs.
Inspect original ideal-vertex, geometry/topology and improveMesh calls versus
the prospective two-neighbor mixed contour commit. Record unchanged original
curves/quadtree inputs, denser midpoint/center templates, planar UV selection,
curved XYZ lift and zero accepted mixed adaptive epochs.

Read-only counts: pure TRI17/78/223 nodes and24/144/430 elements; mixed33/281/797
nodes and24/249/738 QUAD plus8/52/102 TRI. Existing mixed-region checker rejects
pure TRI by design. Preserve its contract; use separate barycentric TRI
interpolation at all576 fixed UV sites against independent Bernstein XYZ and
Jacobian weights. RMS reductions10.6418%/20.1228%/21.9994% describe these different
density/smoothing outputs, not equal-cost or isolated QUAD advantage. Stage1
maximum error rises despite lower RMS. Earlier small RMS increases compare to
the unpaired mixed layout, not pure TRI, and remain valid negative evidence.

Add TRI_MIXED_COMPARISON_20261118.md and method/input-hashed JSON, update STATE.
No algorithm, controller, test/oracle relaxation, native rerun, new mesh or
Blender change. Native85/85 and hosted4/4 retain their exact prior candidate
scope. Next remains independent PR240 review, local-filesystem failure
disposition and exact research-integration/post-merge gates, then R3/balancing.
Publish/read back the canonical documentation checkpoint without source changes.

## 2026-11-18 - audit poor straight-boundary elements against actual interior size

User requests why straight-side quality remains poor and asks to include interior
contribution. Recheck canonical894a71a and source b3d2fbc/PR240 draft/unmerged.
Read original curve/surface passes, factor/balance policies, current candidate
and archived source traces. No source edit, native generation or policy change.

Measure every actual boundary edge, its mixed incident face and the nearest
native QUAD layer via shared-edge face adjacency, all in physical XYZ. Compare
boundary chord with native vertex extent along the chord tangent. Straight
partitions retain3 points/two length1 intervals at every stage; original curve
pass gives0/1, surface pass and final budget retain0/0.5/1. Ratios grow3.74-4.26,
7.32-7.68,13.26-15.35; minimum incident physical angles fall38.46,20.83,8.11deg.
Final straight TRI quality is0.223-0.226 and altitude about0.10. Curved-side final
ratios3.07-3.79. Preserve per-interval hashes, faces and method in the audit JSON.

This confirms a local size/transition mismatch; no single-cause proof for every
bad face. Original surface-curvature adaptation is present, but actual mixed
face quality and nearby native QUAD sizes do not return as curve-interval sizing
requests. New contraction preserves source edges and cannot subdivide them.

Update STATE, roadmap and the prior coupling proposal: keep PR240 review/gates
as one active item, record this quality limitation, then prioritize an opt-in
local curve/transition size package before the full R3 mixed-error controller.
Use original analytical rediscretization and shared synchronization, geometry-
justified local refinement/coarsening and bounded grading. Thresholds/hysteresis
remain scientific proposals requiring alignment; no arbitrary factor adopted.
No tests rerun or previous pass scopes extended. Publish/read back checkpoint.

## 2026-11-18 - revalidate1993 procedure before inventing adjustment policies

User rejects invented adjustments and asks precise decisions using the1993 mixed
technique incrementally with original code and existing flags. Recheck remote
canonical f1094d1, source b3d2fbc/PR240 draft, main ef40c0f and hosted4/4 success.
Other PR239/225 advance independently and remain untouched. Read current state,
roadmap/protocol and source. Withdraw the prior proposed-controller priority;
retain its measured mismatch and proposal text as history, not adopted policy.

Verify original paper SHA49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5.
Native Poppler renders printed pp287-288; visually inspect complete pp287-290
including Figs7/10/11, classification and smoothing. No scan redistributed.
Paper prescribes0.2 contour-edge clearance reclassification. Current boundary
classification uses missing side neighbors, including research capture; no
equivalent clearance stage. Read-only actual native-box/source-face audit finds
0/0/25 offending used leaves out of4/44/175 at stages1/2/3. Both minimum-cell
and center-distance control yield25 at stage3, all on straight intervals:
length0.5 UV, threshold0.1, minimum distance0.0625. No cells changed or new mesh.
Largest-interior versus boundary-cell size cap passes in all three archives;
native source checks2:1 adjacency. Existing mixed front's two prospective
choices/S<=1.5/one polygon update sequence remains coherent at its bounded scope.

Paper also describes interior-node smoothing; new mixed output has none. Source
TRI improveMesh and smoothing flags do not directly smooth the reconstructed
mixed graph. Vertex-mean center remains an explicit unconfirmed interpretation
of the paper's polygon centroid; keep M1 numeric oracle ambiguity. Record source
hashes/anchors and avoid claiming a numerical historical reproduction.

Audit flag consumers: current factor bounds1.5/1.5 fix the final curve factor;
sensitivity alone cannot change it. Count rebuild requires both budget-driven
and point-budget gates; legacy default budget-driven0 makes a minimum alone
insufficient. Source-tree quality/depth paths are conditional, not a replacement
for paper clearance. Mixed research generation structurally uses templates;
do not describe template-off or mixed smoothing control as implemented. No flag
sweep, algorithm/threshold edit, native build/test rerun or new mesh occurred.

Add ARTICLE_CONFORMANCE_REVALIDATION_20261118.md/JSON; correct current STATE and
roadmap, explicitly supersede coupling proposal/audit recommendations. One next
action: documented clearance stage in the opt-in candidate with a retained
witness, coherent template/front interfaces and default TRI preserved; then
documented mixed smoothing/effective controls and M1 disposition. Independent
review, local filesystem and exact integration gates remain. New controller/R3
work is outside current scope. Publish/read back this documentation checkpoint.

## 2026-11-18 - add visible generation-stage error and quality diagnostics

User requests actual error and element quality in the results. Keep one PR240
work item and the current article-completion priority. Audit remote canonical
2c71f1b, main ef40c0f and concurrent PR239/225/214; leave them untouched.
Implement bounded engineering-only reporting/viewer changes at exact9ca6deb.
No native algorithm, configuration, source history or acceptance edit.

Add per-step paired TRI/mixed RMS/max and per-type quality, physical angles/edge
ratios, full per-face identities, native logged TRI reference fields and explicit
null mixed adaptive error. Bind report to manifest/source mesh hashes. Five
analytic/scope controls pass warning-as-error. Exact local baseline85/85 passes;
no stage qualification. Existing archive replay verifies191 commits/eight forged
traces without new rollback; six adapted geometry rows match earlier independent
comparison. Exact hosted44296219310 all4 checks pass; GNU/MSVC/ASan fresh native
histories each verify191 commits, eight forgeries and rollback. No local rebuild.

Create and visually verify Blender5.3 numeric and quality-colored scenes with
eight unchanged meshes, original analytic model, eighteen native template/source
panels below and original actual-commit animation. Prior blend hash unchanged.
Final mixed RMS0.00726210 but global minimum angle1.34deg demonstrates that lower
sampled error does not imply satisfactory worst elements. Keep native TRI adaptive
and diagnostic geometric errors distinct. Add methods/evidence; update STATE.

Retain initial ResourceWarning repaired by closing CSV files, outer artifact
logging NameError after successful Blender creation, and cropped preview repaired
only in new artifact. Prior WSL rename failures, article clearance/smoothing/M1
center ambiguity and independent integration review remain unresolved. Keep draft
PR240 unmerged; no roadmap or modernization history change. Exact next action is
documented contour-clearance repair with the retained witness and default TRI
preserved, then mixed smoothing/effective controls. Publish/read back canonical
checkpoint; primary checkout keeps the visible source feature branch.

## 2026-11-18 - distinguish primary global curvature error from geometric RMS

User asks whether global error is the principal indicator. Read current canonical
407ba79 and exact source9ca6deb; remote main ef40c0f, PR240 draft and concurrent
PR239/225/214 unchanged. Original native CSV confirms global curvature errors
0.314848,0.139436,0.0538754,0.0303172. Verify source ErrorGlobal and stopping
comparison against GlobalErrorTarget. Existing reporter maps this CSV field to
tri_reference_adaptive_error; Blender calls it TRI adaptive curvature E. Explain
that this is the primary current convergence error and needs clearer prominence;
RMS/max geometry distance and element quality serve different purposes. Neither
replaces it. Actual mixed global curvature error remains unavailable; the TRI
reference is not mixed convergence evidence. Do not convert the legacy normalized
index into an ordinary geometric percentage or claim a new estimator.

Documentation-only clarification; no source/viewer/artifact change or new native
generation/tests. Previous exact9ca6deb four remote checks reverified success,
with no qualification transferred. Preserve current article-clearance/smoothing
priority, independent review, local failures and broader gates. Publish/read back
STATE and this append-only entry; no roadmap or modernization history change.

## 2026-11-18 - deliver a complete explained Blender presentation

User requests a new Blender with all existing results/templates and explanations
for unfamiliar terms such as RMS. Verify canonical ec59235, source9ca6deb, main
ef40c0f and draft PR240. Concurrent PR225 advances to c08e359; leave it and other
branches untouched. Existing exact-source hosted44296219310 checks remain4/4.

Create a new personal Portuguese presentation from preserved output, not a new
meshing run. Six scenes show the analytic model/eight stages, separate type and
quality colors,18 TRI/QUAD/source-polygon panels immediately below, a larger
catalog with actual usage, real UV-cell maps and retained commit animation.
Prominent global errors are TRI-only; mixed global curvature error stays missing.
Eight reading cards and detailed FAQ explain RMS, max distance, native global
index, separate Q/J, angles/edge ratios, UV/XYZ, quadtree, AFT, S and source-center
limits. Include original numeric reports and per-face data beside the blend.

Reconstruct family signatures from archived boxes, independently match all initial
QUAD faces to included cells and verify template plus actual front counts.
Observe T1:4 at step1; T1:35/T2:6/T4:3 at step2; T1:173/T6:2 at step3. T3/T5
remain reference diagrams. No per-step original TRI family inventory is asserted.
Verify16 native mesh instances/face connectivity,18 panels, eight card bounds,
input snapshot retention and unchanged reports. A later save changes the old
source path; its blend1 matches the exact captured input. Leave both untouched.
Inspect all five image views and
the new file open in Blender5.3. Retain absent-kind extractor failure repaired
using polygon arity, missing render wires, overlapping navigation label and
inactive-scene matrix overlay correction. Only display geometry is added.

No first-party source/estimator/policy change, native build/tests or generation;
previous exact-source checks are reverified, not extended. Record delivery/evidence,
STATE and this log; leave roadmap/modernization history unchanged. Next remains
documented contour-clearance repair, then mixed smoothing and M1 disposition.
Mixed global error, independent review, local WSL and wider gates remain open.
Commit/read back the canonical checkpoint; keep visible source on its PR branch.

## 2026-11-18 - make the delivered and pending plan explicit

User is lost between the planned technique, implementation and presentation.
Read current protocol/state/roadmap and named evidence; verify canonical8184416,
source9ca6deb/draft PR240 and main ef40c0f. Concurrent PR239/225 advance to
22cd921/d4e373a; leave them and PR214 untouched. Source remote four checks remain
successful. No tests, generation, scientific decisions or first-party code changes.

Add a compact current-plan reading guide and status table at the start of STATE;
link it from the full roadmap without changing milestone scope or order. Explain
that original curves/templates and prospective mixed static output are implemented,
while complete1993 conformance and mixed adaptive closure are not. Recent Blender
and metrics deliveries do not repair the generator. Keep missing contour clearance,
actual mixed smoothing, historical center interpretation and mixed global error
separate. Preserve draft review/integration, local WSL and full historical gates.

One next implementation action remains documented contour-clearance classification
with the retained witness. Then mixed smoothing/control/center disposition, real
history regeneration/comparison and finite required gates, independent review and
research integration, followed by aligned mixed-state/error/adaptive work. No new
controller or factor sweep. Source feature branch remains visible; canonical docs
and modernization main have distinct roles. Publish/read back this documentation
checkpoint. The summary adopts no new scientific policy or stage qualification.

## 2026-11-18 - implement the explicitly confirmed contour-clearance interpretation

User authorizes the current order and requests descriptive questions before
scientific uncertainty. Verify canonical a3e16e4, source9ca6deb and main ef40c0f;
concurrent PR239/225/214 untouched. Explain minimum cell-to-segment versus center
distance and UV/XYZ scope; user confirms minimum distance to finite segment in UV
as the proposed aligned decision. Keep factor0.2/strict inequality and original
TRI/curve/acceptance policies. No later smoothing choice is inferred.

Implement explicit read-only policy in capture/emission/dispatch; article front
uses the selected seed's own active interface and original outer contour. Avoid
staging the old classification-dependent TRI bridge for this value-owned path;
old bridge/observer behavior remains. Add source policy metadata, six native
geometry/witness cases, two dispatch cases and independent actual-cell auditing
plus three forged policy receipts. Exact source published/read back11dcaa7,
tree5dc1ff44ad0bd9c7d22fb1efba99da0d22cc8182 on draft PR240.

Retain failures and repairs: Windows small macro in new test; new filtered test
called the unfiltered helper default; unqualified Ninja/compiler/tool environment;
formatting hook; first85-test baseline invalidated by source identity changing
during formatting/commit. No hidden retry or suppressed diagnostic. After stable
identity, exact local85/85, native19/19 (leaf36/dispatch14), source-boundary contract,
old live-pair application and fresh183-commit/186-frame/11-forgery/nonempty-rollback
history pass. Configured changed production/header/geometric analysis passes.
Expanded full adversarial-fixture scan fails an old invalid-enum negative control;
retain it unresolved for review rather than hiding/removing it.

Exact hosted44401586214 all4 checks pass; GNU/MSVC/ASan each match the183 commits,
11 forged traces and rollback. All four TRI and first three mixed OBJ outputs
are byte-identical to9ca6deb. Step3 excludes exactly25 cells and uses150 interior
leaves;689 nodes/630 QUAD/102 TRI. Boundary angle8.11->10.37deg improves, but RMS
0.00726210->0.01182093 and edge ratio8.70->15.08 worsen. Retain all counterevidence;
no complete1993 reproduction, new mixed error, overall improvement or stage closure.

Update repair/evidence, current plan/state/roadmap and PR description. Reread the
retained printed-p290 smoothing paragraph: incident-element vertex-coordinate
mean, four/five repetitions, original contour fixed, planar problem. Next ask
explicitly about UV versus projected XYZ, unique incident vertices/multiplicity,
and pass count/update order; a UV/distinct/five-simultaneous proposal is pending.
No mixed smoothing is implemented before that response. Independent review,
adversarial-analysis disposition, M1 centers, local WSL, full historical/native
and exact integration/post-merge gates remain open. No new Blender or main merge.
Commit/read back this canonical checkpoint; retain the visible source PR branch.

## 2026-11-18 - implement the explicitly confirmed mixed UV smoothing contract

User adopts the descriptive UV/distinct-neighbor/five-simultaneous proposal,
including opposite QUAD corners, fixed original contour, analytic XYZ lifting
and existing validity/rollback. No new thresholds, relaxation, pass selection,
curve rediscretization, balancing controller or adaptive policy is authorized.
Read canonical432f13a, verify source11dcaa7/main ef40c0f and concurrent PRs;
preserve their advances. Implement value-owned smoothing and native arithmetic/
malformed/failure controls, actual per-pass geometry checks and complete source
history export. Add independent synchronous replay/Bernstein lifting,11 old plus
5 new trace-forgery negatives and per-pass error/quality. Keep original TRI.

Publish/read back implementationc3ddc06 then finalbeb2aee on draft PR240,
tree99da71296c0ebee57a02d762ff45a0bf4cb0bd3f. Initial new CheckFacet array call
fails compilation and is corrected to existing FaceUv. First exact baseline
stops before tests because the retained CMake inventory hash is stale; refresh
that hash only, then exact final85/85 passes. Native MSVC20/20, fresh183 commits,
15 actual smoothing passes,11+5 forged traces/nonempty rollback,6 source captures/
54 controls, old live-pair220 events/eight forgeries and configured changed
application/header/native-fixture analysis pass. Explicitly verify all code/test/
input/image bytes unchanged fromc3ddc06 when reusing native evidence atbeb2aee.
Final hosted44408768431 all4 checks pass; GNU/MSVC/ASan ordinary application
reports agree. No hidden retry, diagnostic suppression or unexecuted gate claim.

All four original TRI outputs and186 pre-smoothing commit frames are byte-identical
to11dcaa7. Counts remain33/281/689 nodes,24/249/630 QUAD and8/52/102 TRI. All15
passes retain fixed boundary/connectivity. Native/independent UV agreement is
2.22e-16. Minimum global angles improve but minimum QUAD J falls in all stages;
stage2 RMS worsens and stage3 boundary angle worsens. Retain nonmonotonic passes;
do not choose the best column retrospectively. Mixed global curvature error is
still unavailable; accepted mixed epochs0. Original TRI global values unchanged.

Build a new personal Blender5.3 file with eight outputs,18 before/pass states,
retained18-panel templates/source polygons and embedded Portuguese term/limit
guide. Correct the initial-step label to explicitly unsmoothed. Inspect two
rendered views and observe the new file open in the GUI; old presentations are
not overwritten. Update current state/overview/roadmap, delivery/evidence and PR.

Closure audit covers code/value ownership, controls/history/boundary contracts,
metrics/documentation and scientific scope. Draft/unmerged; no whole-stage or
main integration. Retain prior adversarial invalid-enum analysis, WSL output
failures, independent review, historical centers and full native/CRT/oracle/general
geometry gates. Exact next action: resolve template-center interpretation against
the primary source, asking descriptively before a new scientific choice; then
review/qualify static research integration before aligned mixed-error/adaptive
work. Commit/read back this canonical checkpoint; source stays on PR240 branch.

## 2026-11-18 - trace Step1/Step2 boundary faces and advance center review

User authorizes the next center-review action and asks why boundary QUAD at
Step1 become mainly TRI at Step2. Read canonical53b3266/sourcebeb2aee and verify
remote main ef40c0f, concurrent PR239 db6906d/2253549760/2147cd5014 and exact
hosted44408768431 successful. Leave concurrent work unchanged. Read-only source/
native archive audit separates template faces from prospective front commits,
independently derives original contour edges and reconstructs222 source polygons.

Step1 template16/front8Q8T and contour8Q0T; Step2 template242/front7Q52T and
contour2Q8T. All three straight sides in Step2 use TRI on their original edges;
two boundary QUAD remain on curved v0. Inner interface16->56 and outer8->10;
the application reconstructs each mixed layout. All16 alternatives for the eight
outer-edge TRI fail convexity or S1.5; e.g. S1.7048327646991335. No clearance
cells excluded in either step, no face-kind changes from smoothing. Preserve
quality limitation; this explanation is not optimality or a solved imbalance.

Verify original1993 PDF hash and reread full printed287/288; polygon-centroid
wording has no equation. Locate1987 publisher source but full-text/PDF access
fails; do not replace it with secondary citations. Compare actual retained
mean centers with existing independent signed-area formula: Step1 0/4 differ,
Step2 18/62 (max0.003882062460937146 UV), Step3 0/156. No alternative mesh or
quality gain is claimed. Send descriptive scientific question recommending
existing area centroid in UV as explicit experiment with real before/after
validation, explain ambiguity and ask before any formula change; answer pending.

Create inspected two-panel UV provenance plot and source/hash-bound evidence.
Correct diagnostic's initial assumption about commit/output face ordering by
matching exact cycles; native export groups physical face kinds. No source repair,
new native build/tests, generated mesh, Blender edit, policy change or merge.
Audit contracts/scientific scope/docs and preserve prior checks as retained only.
Next await center decision, implement/compare only the approved slice, then
independent review/static research integration. Mixed global error/epochs0,
old enum diagnostic/WSL failures and wider historical/native/exact merge gates
remain. Commit/read back state and append-only log on quad-templates.

## 2026-11-18 - adopt area-centroid UV policy and compare actual mixed histories

User explicitly selects the proposed area centroid in UV as aligned experimental
decision and asks to continue. Read canonicalf321ca3/sourcebeb2aee/main ef40c0f;
verify concurrent PR239/225/214 advances and leave them intact. Reuse the existing
signed-area point routine only through a new opt-in article selector. Preserve
the old mean selector and all other modes, source TRI, curves/synchronization,
quadtree/templates/order, S1.5, clearance0.2, approved five-pass smoothing and
adaptive acceptance/stopping. Existing point validity/tolerance remains unchanged.

Publish/read back exact15e2915, tree57e98001503559e458bf42cb3e3a1b8e594d1686,
on draft PR240. Add independent exact-Fraction source-polygon centroid checking
and three point forgeries, including a real asymmetric center replaced by the
old mean; retain11 front and5 smoothing forgeries/nonempty owner rollback.
Record choice in native trace and OBJ metadata; refresh retained architecture
hashes before the stable exact baseline. No alternative formula or hidden retry.

Final local85/85, native MSVC20/20, source6/3reversed/54 negatives, prior live-pair
220 events/eight forgeries and all four configured changed/newly linked TU/header
analyses pass. New image's old mean selector reproduces all8 old OBJ scopes
byte-identically. Fresh area application reconciles222 polygons,183 commits,
15 passes and11+5+3 negatives with rollback. Exact hosted44440173309 all4 pass:
GNU/MSVC/ASan reports agree;85 baseline/527 Python controls and frozen Eistute5/
Book4 exact OBJ/acceptance/boundaries pass. No required gate fails in this slice.

Only Step2 changes:18 initial centers and271 post-smoothing interior sites;
counts/contour/connectivity/source leaves/front choices remain identical. Step2
RMS0.01289868039->0.01289667137 and angle9.58768997->9.59283006deg improve
slightly, minimum QUAD J0.224087726->0.223536909 worsens slightly. Steps1/3
geometrically identical. This does not repair transition quality or prove global
benefit/historical equation/mixed convergence. Mixed global curvature error is
still unavailable, accepted mixed epochs0; original TRI errors unchanged.

Create a new four-scene Blender5.3 with current real outputs/all actual passes,
six mean/area comparison meshes, metric guide and previous template reference
explicitly labeled. Inspect comparison render/UV plot and observe the new file
open in the GUI. Keep previous files intact. Update delivery/evidence/plan/state
and PR; audit code/value ownership/tests/contracts/docs/scientific scope and
known coverage. No merge or whole-stage closure. Experimental center choice is
settled; no repeated scientific selection question. Next independent static PR240
review and old enum-analysis/WSL disposition, then exact research integration/
post-merge gates. Retain historical identity, full native/CRT/oracle and later
actual mixed-global-error/adaptive work. Commit/read back canonical checkpoint.

## 2026-11-18 - prepare static PR240 review and qualify native Linux output routing

User asks to continue the stated review/finding-disposition plan. Read canonical
93ae272/source15e2915/main ef40c0f and verify current PRs/checks. Source remains
clean and unchanged; PR240 draft, no GitHub reviews, exact44440173309 successful.
Prepare a24-file SHA-bound ownership/regression packet. Present a concrete user
choice for two separate reviewers versus external human review; prior two-reviewer
authorization concerned PR238. No reviewer is started without that choice and
no primary audit is labeled independent approval. Choice is pending at checkpoint.

Inspect old WSL GNU/Clang denied directory-renames and preserve all failed/partial
prefixes. Rebuild exact15e2915 under the existing GNU13.3 Release and Clang18.1
Debug ASan/UBSan/leak cache profiles/flags. Explicitly place outputs under
/home/apmesh on native Linux filesystem, source still v9fs. Start23:11:53 Fortaleza
(correct the initially reported23:15); finish in242.285seconds. Keep300-second
child caps/current checker caps and first-failure/process-group cleanup. All13
steps per profile pass: compiler/filesystem, build, front/smoothing build/run,
source contracts and article/live-pair/bounds/fixed16/original-boundary histories.
All three current article reports GNU/ASan/MSVC match in their recorded fields;
183 commits,11+5+3 forged traces and nonempty rollback. No hidden retry/fallback,
new generator rule, permissions change or claim that old DrvFS was repaired.

Retain expected enum diagnostic: scoped fixed-int enum value127 in a deliberate
unsupported-mode test. Source identical since11dcaa7; native rejection checks
run in the retained20-test scope. Clang documentation distinguishes this warning
from necessarily undefined behavior; C++ fixed-enum/cast rules support the proposed
technical classification. Do not add a fake enumerator, remove the control or
suppress the warning. Raw full-fixture analysis still exits1; independent review
must explicitly dispose it. No unilateral required-gate waiver or full-analysis
pass. Preserve previous unrelated/native/historical limitations.

Whole changed-file whitespace24/C++ format14 checks pass without edits. Check
current source hashes/image identity and reuse exact85/20/hosted4/frozen TRI
evidence without rerunning it. Read-only merge-tree preflight has no conflicts;
prospective tree differs from candidate only in QUAD documentation. No remote
merge, source mutation or post-merge tests. Audit code/owners/contracts/tests/
docs/scientific scope and known coverage; broader native/CRT/oracle, historical
identity and mixed global error/adaptive epochs0 remain open. Append readiness
evidence/state/plan and commit/read back canonical checkpoint. Next selected
independent review route on exact15e2915, findings/disposition, then required
research integration/post-merge gates. No Blender change or whole-stage closure.

## 2026-11-19 - independent PR240 reviews and qualified static research integration

User explicitly authorizes two separate PR240 reviewers. Pin reviewed source
15e2915/tree57e9800 and canonical fccab6b; audit remote main/branches/open PRs/
exact checks before delivery. Both ownership/lifetime and scientific/regression
reviews find no blocking static-package defect; persist their complete reports.
Dispose intentional fixed-int enum negative input while retaining raw additional
full-fixture analysis exit1. Qualify only the native-Linux publication route;
old DrvFS failures, exact-tie replay/allocation/transaction coverage limits remain.
Technical review is not advisor alignment, GitHub approval or whole-stage closure.

Mark PR240 ready and merge exact15e2915 as51d51f6423abd0208b250f0bbb0291364852cab1
into quad-templates. Verify parents fccab6b/15e2915 and prospective tree51e2efa;
only QUAD docs differ from candidate. Release secondary canonical checkout at
its unchanged commit; guard direct primary research checkout, preserving all2456
non-QUAD-doc tracked files' bytes/size/mtime. Main ef40c0f and concurrent PRs stay
untouched. No code/scientific formula, policy, ordering or synchronization change.

Start exact-merge validation06:27 Fortaleza. Full baseline85/85, native MSVC20/20,
source contracts and all five existing application cases pass. Initial WSL call
selects nonexistent Ubuntu, starts no test and is recorded as launcher error;
inventory confirms Ubuntu-24.04 and the invocation is explicitly corrected.
No test retry/fallback occurs. Existing GNU13.3 Release and Clang18.1 Debug
ASan/UBSan/leak profiles each pass13 steps with native-Linux outputs, same flags,
300-second child bounds and first-failure stop; correct Linux run180.937seconds.
Qualified native image/cache hashes remain identical. All local article reports
agree on183 commits,15 passes,11+5+3 forgeries and nonempty rollback. Raw436 files
are hashed. Exact hosted44496523827 completes4/4 SUCCESS,85 baseline/527 Python,
native20 GNU/MSVC, actual GNU/ASan/MSVC article equality, frozen Eistute5/Book4
OBJ/acceptance/boundary parity. Retain unchanged-source configured analysis and
24-file whitespace/14-file format evidence without relabeling them as reruns.

Closure audit covers code/owners/tests/contracts/docs/scientific scope and known
failure/coverage inventory. Bounded static integration is complete, while full
M1/M5/R3/M7/historical/native-CRT/general-geometry and Doxygen obligations remain.
Mixed global curvature error is unavailable; accepted mixed epochs0. No new mesh
or Blender presentation. Update STATE/roadmap/current summary and portable
review/integration evidence; commit and verify canonical remote checkpoint.
Next bounded R3 action binds actual mixed-state/error/quality observations to
retained histories. Ask a descriptive scientific question before adopting mixed
curvature estimator/controller or changing acceptance/stopping; no balancing law.

## 2026-11-19 - bind actual mixed observations to retained source history

User asks to continue the canonical next bounded R3 prerequisite. Audit live
main ef40c0f/canonical f470bbd/open PRs/current checks; preserve concurrent work.
Classify reporting engineering and a reporting defect repair: old report hides
logged TRI error for rejected attempts. Change only tools/quad_generation_metrics.py
and its existing reporting controls. Bind full step/epoch/retry/domain identity,
source accepted/rejected reasons, previous/retained accepted source and actual
TRI/mixed hashes; export history.csv/JSON and explicit Markdown identities.
Measure changes against the previous accepted source, never a rejected predecessor.
Expose rejected original TRI curvature values only after matching original CSV
key, mesh counts and finiteness. No global mixed error or adaptive epoch inferred.

Source b9717e4/tree2846af0 passes local85/85 and11 reporting tests including12 new
malformed-history/reference/observation variants. Recompute only diagnostics on
three already-qualified real archives: current article8, original-curvature
rejection8 and stable-retry6 TRI/mixed observations. All22 geometry/quality/count/
OBJ hashes are exact against f470bbd; source bytes are unchanged. Original rejected
TRI errors0.382516 and retry0.171223 are newly exposed. Protected2454 non-document/
non-reporting files and qualified native MSVC image are unchanged. Hosted exact
44499733650 passes4/4, native20 GNU/MSVC,11 reporting controls,85/527 and frozen
Eistute5/Book4 OBJ/acceptance/positive-boundary equality. Audit code/tests/contracts/
explanations/scientific scope and retained failure/coverage inventory before merge.

Integrate PR241 as5fe2e6fb102176657ca975286d22672709a6c755; verify parents f470bbd/
b9717e4 and identical candidate tree. Direct guarded research checkout preserves
all2676 tracked files' bytes/size/write-times. Start post-merge checks06:55 Fortaleza;
actual85/85,11 controls/22 archive observations pass again. Exact push44500775417
finishes4/4 with the same native/reporting/baseline/scientific scopes. No repeated
local C++ build/analysis/sanitizer campaign, new generation or Blender display.
Old enum-analysis/DrvFS and historical/native-CRT/allocation/transaction/exact-tie/
Doxygen limitations remain; main/concurrent PRs untouched. Bounded reporting
prerequisite complete; full R3/M7/mixed global error/accepted epochs0 remain open.

Ask a descriptive scientific question proposing both-diagonal comparison of the
existing Gaussian witness against analytical curvature on archived real meshes.
Response is pending; no new operator, diagonal policy, acceptance or controller
adopted. Next await that alignment before dependent scientific implementation.
Update STATE/roadmap/current summary/evidence, commit canonical checkpoint and
verify remote readback. Documentation checkpoint does not relabel its own SHA
as another exact native/scientific execution.

## 2026-11-19 - approved same-node both-diagonal Gaussian comparison

User explicitly adopts comparison of both diagonals without adaptation changes.
Read current canonical3052a7c/main ef40c0f/plan/session and audit live remote PRs/
checks before edits. Concurrent PR239 advances independently; never overwrite it.
Add only read-only tools/quad_diagonal_curvature.py and six controls to the
existing reporting suite. Generated native probe calls unchanged P2b header;
rotate copied QUAD cycles for1-3, keep TRI and all source files intact. Independent
cosine-law/Heron per-node primitive/density check plus exact Bernstein derivative
Gaussian reference; plane/sphere/paraboloid/saddle, rotation/scaling/pure-TRI and
malformed controls. Separate boundary turning from interior Gaussian differences.
No normalization, diagonal selection, mixed operator or generation-policy change.

An initial shell-quoting preparation error starts no compiler/test; correct with
file-based CMake preparation and retain the observation. Exact d2eb15e/tree db83723
qualification actually runs09:10:17-09:12:49 Fortaleza (announcement09:09).
Local85/85 and17 controls pass. Compile actual MSVC19.44.35229/GNU13.3/Clang18.1
ASan/UBSan/leak probes and compare22 retained real observations/4227 node
observations per profile. Both diagonals verified against the independent oracle;
three native malformed controls refused per profile. Input hashes/bytes unchanged.
Pure TRI diagonals exactly equal; maximum cross-profile density delta2.0322e-12.
Create/check UV scatter at common zero-centred per-step scales; raw node CSV/JSON,
compiler commands and logs retained locally with portable hashes/summaries.

Current mixed Steps1/2/3 diagonal gaps max0.345818/5.438697/1.819897; witness signs
opposite at8/25,82/271,139/675 interior sites. Step2 node115 analytical-0.556463,
0-2+4.270546,1-3-1.168151; Step3 node15 has the inverse sign-choice problem.
No fixed diagonal wins every measure; these are diagnostic counterexamples, not
a proof against all triangulated operators or a replacement scientific law.
Candidate44521151484 passes4/4 with17 controls,native20,85/527, existing article
histories and frozen Eistute5/Book4 exact OBJ/acceptance/boundary parity.

Audit code/value ownership/tests/contracts/docs/scientific scope/known inventory,
then integrate PR242 as7ccd8d769536b291a2264b140fa4acfc76f3960a. Verify parents
3052a7c/d2eb15e and identical tree; preserve2679 tracked files' bytes/size/mtime.
Exact post-merge09:18:27-09:20:14 local85/17 and all three current-source
22-observation/negative checks pass with identical probe images. All18 numerical
exports match the candidate byte for byte. Hosted exact44522539529 completes
4/4 SUCCESS. Hosted checks do not run the specific generated both-diagonal native
probe; that actual scope is local three-profile evidence. No new generation,
Blender, production-TU analysis or broad native-CRT qualification claimed.

Bounded diagnostic comparison complete. Retain old enum/DrvFS and historical/
allocation/transaction/exact-tie/general-geometry/Doxygen limits, full R3/M7,
unavailable mixed global error and accepted mixed epochs0. Original ErrorGlobal
also uses mean curvature below the Gaussian threshold; this Gaussian-only witness
cannot silently replace it. Next prepare a reference-backed mixed Gaussian/mean
operator contract, including adjacency/area/angle/boundary conventions and these
sign-flip fixtures, for explicit alignment before adoption. No further global-factor
or generation sweep. Update STATE/roadmap/current summary/evidence, commit and
verify canonical remote readback; docs checkpoint is not a new native execution.

## 2026-11-19 - specify mixed Gaussian/mean operator before scientific adoption

User asks to continue the stated contract/specification step. Read canonical
bfaded7/main ef40c0f/plan/latest session, inspect clean primary tree and live
branches/open PRs/exact7ccd8d7 four successful checks. Keep one documentation-only
scientific-proposal item; no code, native experiment, generation or policy change.
Read full legacy angle/area/adjacency/analytical/global aggregation call chain,
typed Quad geometry and prior diagonal counterexamples. Record source hashes.

Source-level inference: legacy discrete mean3*signed-normal-angle-sum/area has
1/s^2 scaling on fixed adjacency/tolerance/concavity branches; analytical mean
has1/s. Vector angle and area access show no hidden length factor. No scaled
native fixture runs, historical transcription defect or repair is claimed. Kim
reference full PDF returns403; abstract is not sufficient to decide its equation.
Original node/submesh aggregation remains literal; mixing geometrical K^2/H^2
needs an explicit normalization decision before a true mixed global error.

Consult primary Cazals/Pouget2003 fitting/rank/conditioning text and official CGAL
jet-fitting algorithm/sample/orientation/numerical documentation. Journal2005
metadata is distinct from inspected2003 full text. Polygon-Laplacian alternatives
are identified by primary abstracts; full PDFs exceed tool size limits, so no
detailed coefficient audit is asserted. No new external dependency or copied code.

Prepare concrete, unadopted quadratic-jet candidate: uniform six-coefficient
least squares; query plus distinct coface one-ring vertices including opposite
Quad corners, one complete two-ring expansion for insufficient/frame/rank failure;
PCA rough normal, deterministic tangent frame, normalized XYZ, small SVD/full rank,
explicit machine-epsilon guards, condition/residual/fitted-offset reporting and
final fitted-normal sign check. Estimate geometrical K/H at all mixed-chart nodes,
including boundary/incident-TRI nodes, in separate value records. Preserve default
TRI and stored curvatures. Unavailable remains explicit, never zero/analytic/diagonal
fallback or dropped global coverage. No diagonal/remeshing invariance overclaim,
finite-fit accuracy/convergence guarantee, global normalization or adaptive use.

Document independent matrix/known-frame/full-pipeline/cylinder/rigid/scale/normal/
coverage/negative and actual22-history gates for a future adopted implementation.
Prior85/17/three-profile/hosted4 evidence remains pinned to its original revision;
no new native tests are run or claimed for an unimplemented operator. Audit docs,
source consistency, scientific scope and known inventory. Update STATE/roadmap/
current summary/evidence; commit and verify canonical remote checkpoint. Next
request explicit scientific adoption/revision of the complete bounded candidate.
Prior approval of the diagonal experiment is not approval of this method. Full
R3/M7/global-error/accepted-epoch0/historical/native-CRT/retained failures stay open.

## 2026-11-19 - adopted quadratic-jet implementation and retained accuracy limits

Researcher explicitly adopts Section4 of the operator contract. Preserve one
read-only scientific candidate, initial unavailability, original TRI/generation/
selection/smoothing/acceptance and no global aggregate/adaptive acceptance.
Read canonical a72bdf1/main ef40c0f and live PR239/225/214/prior exact checks;
feature PR243 contains isolated standard-library PCA/SVD/value records, native
probe, independent characteristic-eigenvalue/Householder-QR audit and exports.

First MSVC contracts fail the exact one-sided paraboloid expectation (exit1).
Stop, retain original streams/command/result, and prove six sampled points also
belong to a cylinder. Full rank6/condition2393.06 does not identify the intended
paraboloid. Keep estimator unchanged; exact symmetric support and mandatory
negative accuracy counterexample replace the unjustified expectation. No new
conditioning cutoff, error-based expansion, analytical or diagonal fallback.

Initial published d1970a1 exact baseline stops at stale architecture before85
CTest. Regenerate only the tests/quad CMake hash; reviewed production inventory/
contracts unchanged. Publish corrected f2dbd47/tree7ef3e90 and align same-tree
local source with2691 tracked bytes/sizes/mtimes preserved. Exact local85/85
and527 tooling, MSVC22/22,182 native checks/six reference controls/22 actual
histories/30 altered records per MSVC/GNU13.3/Clang18.1 ASan/UBSan/leak pass.
Scoped LLVM22.1.8 analyzes both new consumers/headers using actual commands,
no suppression. Direct staged call outside profile lacks clang-format; configured
staged check and normal hook pass. No unavailable tool is called a pass.

All18 numerical exports remain byte-identical to preliminary results. Cross-
profile maximum K/H differences are5.69e-14/4.41e-11. All initial five-node
snapshots unavailable; later archive nodes full rank. Current Step3 mixed
boundary median absolute K/H errors1.30926/1.68638 remain visible. Both earlier
diagonal witnesses now have explicit jet/analytical values; no universal accuracy
claim. PR243 stays draft, estimator/global/adaptive adoption unqualified.

Audit code/value ownership/tests/contracts/docs/scientific scope/known inventory;
record commands/hashes/failures/results. Final hosted44551769795 readback
completes4/4 SUCCESS on exact f2dbd47: native22 each Linux/Windows, actual
22-observation/30-forgery jet archives on both plus sanitized Linux,85/527 and
strict frozen Eistute5/Book4 OBJ/acceptance/boundary parity. Superseded d1970a1
run44551318672 is cancelled, not a pass. No integration/main validation/new generation/
Blender/full native CRT/transaction qualification. Keep historical M1/M5/R3/M7,
legacy mean/normalization questions and prior enum/DrvFS/Doxygen failures.
Ask descriptively for the next scientific decision: compare uniform complete
two-ring support with the unchanged candidate on the same histories, with possible
oversmoothing and no adaptation. Await answer; do not execute an unadopted variant.
Update canonical state/roadmap/overview/evidence, commit and verify remote readback;
the documentation checkpoint is not a new native exact-head qualification.

## 2026-11-19 Fortaleza /2026-11-20 UTC - complete second-ring comparison

Researcher explicitly adopts uniform complete two-ring comparison on the same
histories, degree2/uniform weights/all other fit choices; no movement/generation/
adaptation. Read canonical ef122c7/main ef40c0f and current source f2dbd47/PR243.
Concurrent PR239/225 heads advanced independently; preserve them and PR214.
Keep one diagnostic item. Add separately selected immutable complete-two-ring
path, probe/report option, paired coverage/error/support/radius/condition exports
and controls showing both resolved ambiguity and increased quartic local bias.

First Python run fails at covariance eigen audit on exactly diagonal repeated
tangent spectrum, spurious cubic-acos split9.5591e-10>unchanged1e-10 budget.
Stop, preserve original streams/result/command and native exact diagonal evidence.
Repair independent reference with scaled Givens/Sturm, repeated/zero/dense-known
controls; Householder QR/native estimator/budgets unchanged. No silent retry,
new condition/accuracy cutoff or support fallback. Nine Python and203 native
checks pass, including the retained original sparse ambiguity.

Publish c93a383/tree55da4ba on existing draft PR243; exact same-tree local
alignment preserves2692 tracked bytes/sizes/mtimes. Exact local85/85 (527 tooling),
MSVC22/22 CTests, and203 native/9 Python/22 paired stages/44 evaluations/60
altered-record refusals per MSVC/GNU13.3/Clang18.1 ASan/UBSan/leak pass. Scoped
LLVM22.1.8 analysis passes both actual consumers/header; CMake/inventory unchanged.
All22 original per-node observations per profile and all nine CSV files remain
exact against f2dbd47. Cross-profile max K/H differences5.69e-14/4.41e-11.

Actual final mixed boundary K median error worsens1.30926->1.49756; H improves
1.68638->0.996686 while9/14 boundary H queries worsen. Interior median K/H
worsen0.000432107->0.00145775 /0.00142232->0.00491119. Among689 sites, K/H errors worsen
at620/607 respectively, with selected gains retained. Boundary maximum
errors worsen despite improved conditioning and larger physical sample radius.
This is not a global error or a proof of one unique failure cause. Initial five
nodes remain unavailable; later archive nodes available under both policies.

Audit code/value ownership/contracts/tests/docs/scientific scope/known inventory.
Final hosted44658134604 readback completes4/4 SUCCESS at exact c93a383:
Linux/Windows native22,44 two-policy evaluations/60 refusals on each and sanitized
Linux, root85/527 and frozen Eistute5/Book4 exact OBJ/acceptance/boundary parity.
PR243 stays draft; no independent integration approval/research merge/post-merge
or main closure claimed. No new meshes/Blender, estimator/global/adaptive adoption,
legacy mean repair or full CRT/allocation/transaction/geometry qualification.
Retain prior failed expectations/inventory/enum/DrvFS/Doxygen evidence and full
M1/M5/R3/M7 scope. Next present scientific tradeoffs and explicitly settle boundary
locality/initial coverage before any new formula/experiment/global aggregation;
do not silently promote uniform rings or start another sweep. Save canonical
checkpoint and verify remote readback; docs SHA is not newly tested natively.

## 2026-11-20 Fortaleza - original curve and mixed transition quality audit

The researcher requests a renewed plan and source audit with the original core
preserved, prioritizing poor elements near curves. Read canonical cb3d1cd,
main ef40c0f and draft PR243 c93a383 with four successful exact source checks.
Keep one read-only diagnosis. Measure four archived steps,48 curve-pass events,
six source contour audits,32 paired intervals and14 final boundary curvature
queries. The initial list-order check fails because the final OBJ lists faces
in a different order. Compare oriented face multisets as the existing smoothing
contract does and complete the audit with unchanged inputs.

The three straight sides each keep two segments of physical length1. Final mixed
interior median edge is0.06549. Straight-side midpoint fan reaches22 faces vs9
in TRI. Under two degree minimum angles occur in faces that only touch the
boundary at vertices. These already exist before smoothing. Smoothing worsens the
worst contour-edge angle but improves the worst vertex-only angle on this case.
The largest bounded curvature errors occur on curved side0. Both existing fits
stay unavailable on Step0 and neither drives the generated mesh.

Verify all12 realized curve factors and three domain factors equal1.5. The common
clamp masks a sensitivity-only adjustment. Keep prior default-bound legacy
reconstruction growth to112 intervals and rejected Steps2/3 visible. Recommend
one opt-in article-front comparison with the existing legacy default bounds after
scientific alignment, preserving acceptance and all generation formulas. Report
quality/growth and failed candidates. Further estimator sweeps are deferred.
Update state, plan, overview, diagnostic and evidence. No native rebuild, new
generation, application changes, integration or phase closure is claimed.

## 2026-11-20 Fortaleza - one same-case legacy bound comparison

Researcher adopts comparison of legacy default0.80–1.12 against fixed1.5 and
prioritizes graded curve-to-interior and interior-to-curve influence. Read
canonical0387aaa, main ef40c0f and draft PR243 c93a383 exact four-check status.
Run the same qualified PR240 MSVC Debug application image once, with only the
bound pair and output path changed in an untracked config. Exit0 in81.18s within
existing180s. Archives all four stages. No candidate rerun or configuration sweep.

Source Step1 accepts (0.125829) and provides the published165-node mixed mesh.
Step2/3 each reach953 nodes/112 contour segments and are source-rejected at
0.382516. Both rejected mixed geometries match. Original curve passes show
Step2 curved9→17→65 points and straight5→5→17 each. Legacy Step2 improves the
vertex-only transition angle and neighbor size ratio, but worsens the worst
contour-edge angle. Accepted Step1 is also worse by both angle minima. Validate
12 archived contour bindings, fixed smoothing contour/connectivity,96 staged
curve records and accepted-output byte equality. Retain all rejected data.

Close the shared bound trial. Next trace the local native surface-informed
subdivision at Step1→2 before proposing a coordinated sizing change. Preserve
original core and distinct regional refinement. No new native build, default
policy, mixed acceptance, integration or broad test campaign. Update and verify
canonical state, roadmap, overview, session and scoped archive evidence.

## 2026-11-20 Fortaleza - native interval trace and final element quality

Researcher requests the planned trace and emphasizes final shape and angle
quality. Read canonical533c85a and draft PR243/c93a383 with exact original
checks. Build one isolated C++17 MSVC Debug observer, no production or
configuration-rule edits. Native replay exits0 in47.94s with identical eight
snapshots, manifest, curve stages, pair CSVs and last accepted mixed output.
Reproduce both original rejections. The native interval audit verifies28 Step2
requests, zero endpoints,29.6985% length requests and no new points from
neighbor restriction. Match raw/smoothed native sizing to104 accepted TRI
faces by UV overlap. A second incrementally instrumented replay exits0 in44.71s
with identical geometry and trace rows. All63 prior accepted TRI nodes match the
Step1 OBJ. All20 unique matched contour sites carry a nonzero TRI Gd or Hd while
their curve copies already hold zeros before reconstruction. Fresh interior
curve nodes also initialize their discrete curvature fields to zero.

Evaluate6206 archived mixed faces, by region/type and smoothing phase. Keep
TRI angle/shape gains alongside contour QUAD angle/Jacobian losses. Worst
elements and distributions are required comparative evidence for next fixes.
Next seek adoption of single-patch opt-in accepted TRI values at exact sites,
with linear interpolation of signed channels on new bracketed same-side sites.
No production change, new acceptance cutoff,
fresh full baseline or hosted campaign, or phase closure. Retain the isolated
debugger-free observer and raw logs locally, publish the scoped evidence and
verify the canonical documentation checkpoint.

## 2026-11-20 Fortaleza - adopted accepted-TRI handoff trial and shape evidence

Researcher explicitly adopts one opt-in same-side interpolation comparison.
Use separate local MSVC C++17 executable and Step2 research guard. Hand off
accepted TRI contour measurements by identity and XYZ, use exact parameter
matches or linear signed-channel interpolation inside the same curve side.
Capture values without editing accepted nodes. Single execution completes in
42.31s under180s. Check24 exact/eight interpolated sample values,28 consumed
pairs, four identical Step0/1 mesh files and original contour bindings.

Requests change on every interval but restriction still adds no points.
Step2 grows by one additional straight interval/node and is source-rejected
at0.381381 vs accepted0.125829, as is Step3. Worst Step2 shape changes
negligibly. Last published Step1 is byte-identical to the retained control.
Close this trial and retain negative evidence without a new scientific run.

Read archived smoothing passes. Step2 fixed contour QUAD minimum J loses shape
on the first pass (0.394→0.158), while vertex-only TRI benefits. Map Step3
worst early TRI to commit106, curved surface lifted from a long edge to a
short exposed template edge, and the final worst TRI to commit48. Target the
local transition for the next bounded size audit and proposal. Preserve default
TRI and keep final shape by type/region and worst tails visible. No new baseline
CTest or CI qualification, no tracked app changes, no accepted mixed epochs.

## 2026-11-20 Fortaleza - local transition shape and front-order experiment

Read the Step 2/3 native archive and match individual faces through all
five smoothing passes. Observe the distinct 1.42-to-6.99 and 6.95-to-1.87
degree TRI witnesses and the contour QUAD loss. Trace the isolated
five-vertex, four-collinear-site pocket back to front commit 73.

The researcher prioritizes transition generation and approves one bounded
deferral trial. Use the existing TRI radius score threshold 0.05 for a TRI
connecting an original contour vertex to an exposed seed interface.
Build an isolated MSVC Debug C++17 application based on c93a383 and run the
fixed 1.5 case once. Exit zero in 22.08s. Step 3 changes order after 221
deferrals and 15 full-sweep releases. Exact final coordinates, cyclic
oriented connectivity, smoothing trace, numerical quality and four original
TRI OBJ files are preserved. Nine boundary forgeries are rejected. The
same critical faces survive. Preserve the negative trial without promotion.
The [report](MIXED_TRANSITION_SHAPE_20261120.md) gives comparison and scope;
no full CTest, frozen additional models or hosted candidate qualification.

Next specify one local pre-front spacing comparison based on the native
curve subdivision and neighboring quadtree sizes, then seek alignment.
Defer testing the literature-backed smoothing guard until after transition
work. No mixed global error/adaptation adoption or integration.

## 2026-11-20 Fortaleza - define a bounded native contour spacing trial

Bind the planned local transition comparison to the retained Step 3
curve-3 sample and exposed template edge [13, 349]. Recompute its physical
edge sizes and check the stored arc midpoint against the analytic patch.
The original 1-unit straight interval would become two approximately
0.5-unit chords using one binary split. Record the existing parametric
curve-stage partition and distinguish the hypothetical triangle from an
actual generated face.

Propose one Step 3, attempt 0, native post-restriction split followed by
the same restriction and curve sample publication. Ask for explicit
scientific alignment before making that C++ change. The isolated trial
would recalculate the native source tree and follow the original TRI
step decision. The planned comparison checks growth, original and mixed
error diagnostics, degree and shape tails and spacing across regions.
The [design receipt](LOCAL_CONTOUR_SPACING_TRIAL_DESIGN_20261120.md)
records the evidence and exact scope. No new native build, test, or
candidate generation. The prior negative front order result is retained.

## 2026-11-22 Fortaleza - preserve the curve and audit template sizes

The researcher chose to keep the native contour partition and investigate
template size. Close the proposed curve subdivision without a native run.
Inspect and hash-bind Steps 1-3 of the retained fixed 1.5 application.
Attribute all 172 exposed seed edges to their intermediate polygon
half-sides. Check the area-centroid oracle, clearance and exact fixed
contour coordinates. The three short Step 3 pocket edges come from T1
on width-0.0625 native leaves. The existing clearance removes a closer
fine strip. The front bridges the remaining scale mismatch.

On the archived boxes, group the four seeded siblings in a read-only
layout calculation. The existing T6 regenerates the same 16 QUADs and
boundary segments. Grouping the adjacent excluded siblings as well
preserves the 2:1 condition and gives a T5 interface of two 0.0625-UV
edges in place of four 0.03125 edges. Check equal seed UV area and exact
identity of all other exposed edges in the calculation. The
[audit report](TEMPLATE_INTERFACE_SIZE_AUDIT_20261122.md) records the
limits, candidate scope and evidence. No C++ changes, new native runs,
CTest or hosted qualification. The next scientific decision is one
two-block opt-in replay with the original contour retained.

## 2026-11-22 Fortaleza - execute and compare the approved two-block layout

The researcher approves one native comparison of the two specified sibling
blocks with the original curve fixed. Use an isolated C++17 MSVC build from
c93a383. A derived value snapshot omits only the two subdivision events in
the mixed Step 3, retry-0 replay. The real reference TRI history precedes
that replay and is accepted with 430 TRI and curvature error 0.0303172.
The curve trace, four TRI OBJ files and Step 0-2 mixed outputs agree byte for
byte with the retained native control.

The application exits zero in 16.48s. Verify 217 leaves, 619 seed QUADs,
equal seed area, exactly four-to-two exposed edge replacement and original
contour positions/identities. Independently replay 106 front commits, five
smoothing passes and reject nine boundary forgeries. The three pocket TRI
disappear. Final contact angle rises 3.10 to 5.45 degrees and the mesh loses
seven elements. The same distant triangle still reaches 1.87 degrees in
the final mesh. The [report](TWO_BLOCK_TEMPLATE_TRIAL_20261122.md) records all
tradeoffs, including interior QUAD angles and sampled geometry.

Retain the case-specific experimental source locally and record the measured
result in canonical documentation. No full CTest or new hosted qualification.
The next work item is a scientifically aligned smoothing comparison for the
limiting corner, retaining separate TRI and QUAD shape observations.

## 2026-11-22 Fortaleza - diagnose smoothing losses and preserve adaptive goal

The researcher requests mixed adaptation and good shapes wherever feasible.
Bind the Step 2 boundary QUAD and two-block Step 3 corner TRI to their
original first-pass displacements. On archived start frames, move one
vertex at a time for geometry measurement only. One full corner move
drops the TRI to 2.61 degrees. A half move for the Step 2 QUAD preserves
its shape while improving adjacent elements. The strict scoring proposal
has an admissible fraction for 79 of 179 and 8 of 112 nonzero moves,
respectively, in these independent observations.

Specify one scientific comparison using the same five UV passes, fixed
contour, deterministic staged targets, up to four trial lengths per node,
incident physical TRI/QUAD shape and minimum-angle checks, and restoration
on whole-pass geometric rejection. Await explicit alignment. The new
[design receipt](MIXED_SMOOTHING_SHAPE_DESIGN_20261122.md) is read-only
with no native run. Resume the previous-mixed-state feedback contract
after this bounded item. Current curve subdivision is inherited from
TRI and does not satisfy the two accepted mixed epochs required by #221.

## 2026-11-22 Fortaleza - measure curve-to-interior gradation on existing meshes

The researcher requests that local interior size and neighboring curvature
can influence straight as well as curved contour intervals. Preserve
different target sizes with a gradual transition. The read-only
[gradation audit](MIXED_BOUNDARY_GRADATION_20261122.md) checks exact source
and incidence at 46 intervals in four retained mixed meshes. A physical
curved-to-straight contour step grows to 3.66 in Step 3. The largest
adjacent face-size ratio in the near curved-end straight-half profile
falls from 5.40 to 4.86 in the already measured two-block control pair
with byte-identical source vertices. Record sides, endpoint-only fans
and analytic Gaussian samples separately.

Retain local gradation and shape diagnostics in the existing smoothing
comparison and in the adaptive feedback work. Existing TRI size
gradation is a candidate prerequisite, while a mixed two-way size rule
requires scientific alignment. No new C++ change or native run. No CI
or CTest qualification.

## 2026-11-22 Fortaleza - run first mixed-state geometric feedback experiment

The researcher asks for functional mixed adaptation and selects the bounded
geometric pilot. Publish the policy-neutral topology of previous mixed faces
and original intervals in draft PR247, source 94dc35a. Native MSVC graph probe
and independent archive audit agree on all 46 intervals and 3,518 links.
Reject four malformed connectivity cases per mesh. Keep exact integration
and scientific gates open.

Run the local single native pilot from the actual Step 2 mixed mesh. Use
its highest residual of each typed face, three local 1.35 size passes and
the original curve interval subdivision. Record eight face-to-curve
decreases and 39 decreases total. Two candidate face requests reach the
same depth-4 leaf. The first stops the attempt before tree edits or front.
An independent archive diagnostic finds seven distinct eligible cells and
binds the failed face to the capped leaf. All eight earlier/current TRI and
mixed reference snapshots and original curve trace match bytes. No new
candidate geometry, error/shape comparison or accepted mixed epoch.

The [pilot report](MIXED_GEOMETRY_FEEDBACK_PILOT_20261122.md) preserves
the first failure and its hashes. Seek alignment for one attempt preserving
the cap while applying eligible requests. Keep the smoothing trial queued.

### Same session - approved second replay preserving depth cap

Keep depth 4, retain the first failure unchanged and run the approved second
pilot on a distinct archive. Preserve a first C2662 build failure; the
non-const legacy depth getter needs the same observer type as existing
callers. The corrected native executable exits zero in 25.39s. Log two
capped requests, seven direct eligible edits, 88 instead of 67 leaves and
eight transient native interval divisions. The accepted source TRI outputs,
mixed reference history and source curve trace remain byte-identical.
Native front reaches smoothing. Its current geometry check rejects an
inverted or collapsed UV QUAD. No published pilot mesh, comparable final
error, or accepted mixed epoch. The next decision is a one-comparison
last-valid-position safeguard for the existing geometric validator.

## 2026-11-23 Fortaleza - connect published mesh improvements to the mixed pilot

Review primary work on constrained Laplacian motion, local surface
parametrization, Jacobian distortion, mesh gradation and interpolation
error. Keep the current curve, quadtree/templates and 1993 mixed front.
On the archived data, record the eight requested contour fractions
and compare idealized half-arc division. Re-evaluate scaled first-pass
displacements on two retained mixed meshes. Local minimum shape
and common-site XYZ RMS can move in opposite directions. Preserve the
initial diagnostic ordering mismatch and its corrected oriented
connectivity test; no scientific generator change follows.

The [report](MIXED_ADAPTATION_LITERATURE_20261123.md) recommends one
cap-preserved reconstruction with a last-valid-position control and
local shape-checked moves from the same starting mesh. Obtain alignment
before running this treatment. Follow with requested-versus-realized
gradation measurements and mixed acceptance qualification. No new
native generation or accepted mixed epochs. PR247 d206862 now has
four verified hosted checks, for its adjacency scope.

## 2026-11-23 Fortaleza - one capped mixed replay with guarded smoothing

The researcher approves the proposed paired test. MSVC Debug C++17 builds
the isolated target and runs the built-in Bezier case once. It reproduces
seven tree edits, 88 balanced leaves and eight original curve midpoint
insertions at cap 4. All four sizing traces, the eight ordinary OBJs and
the curve history preserve their respective references byte for byte.

Both arms start with a valid 375-node, 397-face geometry. Independent
replay confirms the first unguarded Jacobi pass inverts a corner of
QUAD 315 in UV. The last valid control is the original frame. Five
guarded passes complete and produce a typed experimental successor
with unchanged 18-segment contour and face connectivity. Independently
replay the 473 accepted moves and verify physical and parametric geometry.
Worst TRI transition angle 4.10 to 5.09 degrees, unchanged worst contour
QUAD 22.33 degrees, area-weighted XYZ RMS 0.00665882 to 0.00627204 and
unchanged sampled maximum. Neighbor-size median rises while p95 falls.
The [comparison](MIXED_SMOOTHING_PILOT_COMPARISON_20261123.md) retains
the rejected pass and the remaining quality limits.

Next match requested to realized spacing on the retained candidate by
contour interval and face region. Examine the role of binary splits and
leaf quantization before aligning a change to sizing. No mixed epoch
accepted. No full delivery regression, sanitizer/CRT or remote CI was
run on the isolated trial.

## 2026-11-23 Fortaleza - trace realized spacing and set reuse requirements

The researcher approves measuring the retained candidate and asks that the
result support long-term use. Replay 39 typed graph updates and pair ten
source intervals, eight binary divisions and all 17 face residual sites.
The [audit](MIXED_SIZE_REALIZATION_20261123.md) records five unmet split
intervals and seven face sites above the target despite a leaf edit.
Both capped requests realize face sizes within target. After smoothing,
face-to-face p95 improves, the median contour-to-face size ratio grows,
and the limiting 5.09-degree TRI lies outside the recorded sample sites.

Retain two corrected audit failures (initial quadrature resolution and
receipt path shadowing). No native rerun, source change, scientific rule
adoption or accepted mixed epoch. Next align a physical sizing contract
using existing curve/tree operations, shared-curve synchronization and
output quality, with additional geometry coverage before adoption.

## 2026-11-23 Fortaleza - cross-check mixed sizing on a second model and seams

The researcher authorizes additional comparisons to improve long-term
adaptation and bad elements. Select Ribbed Bracket patch 12 by the
analytic normal screen and run the prior isolated binary once. Ordinary
mixed Step 1 has lower sampled area-weighted RMS and poorer worst TRI
angle and gradation than TRI. Ordinary mixed Step 2 exits at UV QUAD 483
before mixed feedback. Preserve all prefix evidence and no native retry.

The [report](MIXED_SIZING_CROSS_CASE_20261123.md) verifies four symmetric
aligned/reversed M4 seam controls and 68 archived Ribbed pairwise intervals.
Shared curve geometry can match while face sizes differ by 5.84. The first
query on patch 12 found no degree-two seam; the real incidence instead has
two degree-three curves. Record a clean distinction between the paired
controls and the experimental live path.

Seek alignment for one guarded ordinary Step 2 run from a valid starting
mesh, ahead of a new sizing rule. No implementation change, matrix
qualification, GPU/Blender work, native shared-curve run or mixed epoch
acceptance in this comparison.

## 2026-11-23 Fortaleza - guard ordinary mixed Step 2 in the second geometry

The researcher approves the bounded second geometry comparison. Patch
12 uses the same input and controls as the failed run. A copied isolated
MSVC Debug executable compares both smoothing arms from the validated
ordinary Step 2 initial mesh. Control pass one reproduces UV QUAD 483.
Guarded passes one to five are valid; the independent audit replays 303
moves and verifies typed topology, native contour and unchanged reference
prefix. Preserve the application evidence and separate the early
diagnostic exit from adaptive acceptance.

The [comparison](RIBBED_MIXED_STEP2_SMOOTHING_20261123.md) retains the
unchanged 3.79-degree TRI next to a QUAD 4.18 times smaller, unchanged
QUAD minimal angle, reduced geometric RMS and mixed gradation effects.
Next audit existing residual and neighbor coverage on the two
predecessors before aligning the size conversion. No new size law,
feedback execution, full delivery matrix or accepted mixed epoch.

## 2026-11-23 Fortaleza - clarify curvature-driven sizing before the mixed front

The researcher asks whether curvature can improve element shape at
generation. The [source audit and replay](MIXED_FRONT_CURVATURE_SIZING_20261123.md)
distinguish native upstream curve/tree curvature adaptation from
existing-vertex UV mixed contraction. Replay all 39 original
propagation updates and inspect two guarded archives. The worst TRI
receives no reduction in either archive. In Ribbed it is four edges
from the nearest seed, with two smaller contour targets on an
analytically straight side. In Bezier it is seven edges away.
Use these observations to align a native pre-front size proposal
before changing candidate selection. Only read-only evidence and
documentation changed. No new native execution or mixed acceptance.

## 2026-11-23 Fortaleza - compare one explicit transition TRI size request

The researcher approves the paired Ribbed test after the read-only
comparison predicts identical eight-interval split masks and 17 versus
21 face requests. Execute one isolated MSVC application from the same
guarded Step 2. Verify those requests, the 22 identical curve segments,
common predecessor, negative unguarded passes and two sets of five
valid protected passes. One extra leaf and ten extra faces follow the
new seed; the old TRI footprint is entirely QUAD in the control. The
augmented result retains some TRI coverage there. Both global worst
faces agree in UV and XYZ, and the QUAD minimum worsens relative to
the previous mesh. Record a small RMS advantage with no advantage at
the sampled maximum for the larger mesh. No mixed acceptance.

Keep the residual-only case as the simpler comparison baseline. Align
a bounded next sizing rule from the measured source chords and template
edges of both limiting faces before smoothing. See the
[paired trial](RIBBED_PREFRONT_SHAPE_TARGET_20261123.md).

## 2026-11-23 Fortaleza - measure the limiting child arcs for the next comparison

The researcher requests the next test. Bind the native arc audit to the
retained original residual-only candidate and verify analytic arc lengths.
Both TRI-adjacent targets are already met; the worst QUAD uses a 1.02021
arc against a 0.62666 target. The [audit](RIBBED_LIMITING_CHILD_ARC_20261123.md)
estimates two 0.51 children at the existing native subdivision parameter.
Propose one additional split on that edge of the degree-one curve. Hold
the scope decision before native execution. No newly generated mesh or
accepted mixed epoch.

## 2026-11-23 Fortaleza - one additional native point at the worst Ribbed QUAD

The researcher approves the exact one-child experiment. Reconstruct
only that variant, compare to the archived residual-only arm, and
keep the common Step 2, native size requests, cap and realized 133
leaves exact. The two native children are within target. One point
and one TRI are added. Both sets of five smoothing passes are valid;
the previous unguarded control failed on its first pass. Global QUAD
minimum angle improves, but a replacement TRI in the split region
makes its local minimum slightly worse. The limiting TRI is unchanged.
See the [result](RIBBED_SINGLE_QUAD_EDGE_SPLIT_20261123.md).

Keep the variant as evidence. Next trace the unchanged TRI's short
template edge and prospective front choices with the existing satisfied
contour sizes. No general curve policy, full matrix or mixed acceptance.

## 2026-11-23 Fortaleza - trace the limiting Ribbed TRI to an exposed T1 edge

Record the 99 front commits on one diagnostic native replay of the
23-segment variant. Independent replay confirms unchanged original
outputs and operation 27. Among three active valid points, the native
selection gives the best 6.33-degree physical TRI for the short base.
All preceding states of that base offer no better TRI or eligible
QUAD. The [trace](RIBBED_LIMITING_TRI_FRONT_TRACE_20261123.md) also
predicts a balanced sibling grouping with the existing T2 pattern
and twice-longer contour-facing template edges. It remains an
unexecuted scientific proposal, with no mixed epoch accepted.

## 2026-11-23 Fortaleza - group one approved Ribbed parent on the copied tree

The researcher approves one comparison using the unchanged 23-segment
curve. MSVC completes one isolated run. Preserve all physical requests
and cap, verify the four changed leaf IDs and the 2:1 condition, validate
all 97 commits and the complete guarded/unguarded pass frames. The
target block emits four to two contour-facing edges, twice as long.
The old limiting TRI footprint is now one 64.31-degree QUAD while
the global TRI minimum moves to another section at 6.86 degrees.
See the [comparison](RIBBED_SINGLE_PARENT_TEMPLATE_TRIAL_20261123.md).

Retain the measured gains and unchanged global QUAD minimum. The
next item is a reusable local selection rule with fine-resolution
counterexamples and a second geometry, pending scientific alignment.
No rule adoption, mixed acceptance or full delivery qualification.

## 2026-11-23 Fortaleza - replay a reusable template grouping selector

The researcher requests the next step. The [read-only selector](MIXED_TEMPLATE_GROUP_SELECTOR_20261123.md)
reproduces the prior Ribbed experimental parent and identifies a
different parent for the 6.86-degree TRI. A T6 reconstruction leaves
the limiting Bezier edge unchanged. Existing residual-demand replay
protects eight Bezier face observations; an injected control protects
the Ribbed positive group. Record the first console summary failure
and corrected deterministic audit. Await alignment for one native
case with the exact numerical scope. No mixed epoch accepted.

## 2026-11-23 Fortaleza - execute automatic grouping on both sides of the Ribbed transition

The researcher authorizes continuing the experiments. The unchanged
selector chooses one new parent per native reconstruction. Group 62
removes the first thin TRI. Vertex and connectivity comparison finds
the next limiting TRI already present at the same contour point.
Repeat the selected grouping on parent 71 using the first result.
The two native images preserve curve, cap and original requests.
Both target TRI footprints become QUAD and the final mesh is 28
faces smaller. The global limiting TRI moves elsewhere, at 7.04
degrees. See the [native comparisons](RIBBED_AUTOMATIC_TEMPLATE_GROUP_TRIALS_20261123.md).

Next package regional quality and bounded rollback as a reusable
opt-in trial and validate a broader control set. No automatic
mixed acceptance, estimator adoption or full validation matrix.

## 2026-11-24 Fortaleza - audit the transition plan and implement a regional comparator

The researcher requests a plan audit and continuation. Verify remote main,
quad-templates, open PRs and the two independent mixed research branches.
Find a common-region validation gap before rollback. Draft PR 263 adds
read-only regional/global comparison at fixed analytic UV sites. Run four
focused and 17 existing Python tests on exact head 00cac043, the eight
reports with identical old global grid values, and six retained mesh
comparisons. The [audit](TRANSITION_REGIONAL_COMPARISON_AUDIT_20261124.md)
records a Ribbed shape/error trade-off and a positive Bezier regional
reference with an unchanged global minimum. Preserve the original
wrong test diagnostic and whitespace check, both corrected.

Proceed to a reversible native candidate using these measurements.
Align the experimental decision for a regional shape/error trade-off.
Fresh native cross-model qualification and mixed acceptance remain pending.

## 2026-11-24 Fortaleza - audit the research path to an accepted mixed history

Reviewed remote main ef40c0fc, quad-templates ce33b5e7, open PRs and their checks,
issue 221, native real-boundary rollback code, the curve/front experiments, shared
seam measurements and fixed-region comparisons. Three relevant draft heads each
showed four successful hosted checks. Found conflicting active priorities in the
short guide and roadmap, and a fixed historical PR in the handoff instruction.
Updated those entry points and STATE. The [short plan](CURRENT_PLAN_OVERVIEW_20261118.md)
now records the single active experiment, negative controls, predeclared transfer
comparison, TRI baseline and the scientific exit. Historical evidence and unmet
qualification gates remain available. Documentation-only audit; no native build,
new geometry, admission formula or accepted adaptive epoch.

## 2026-11-24 Fortaleza - stage and reject a native mixed transition trial

Reproduce the retained Ribbed patch 12 predecessor in one MSVC application
invocation, select grouping from its emitted front, record a finer-size veto
and stage the physical successor. Inject rejection after staging and verify
previous owner, ordered observers and OBJ preservation. Regional minimum
angle 6.86 to 43.44 degrees, global TRI minimum 6.86 to 6.87, both
sampling grids show a regional geometric RMS reduction, and the ordered
23-interval curve agrees exactly. See the [report](REVERSIBLE_TRANSITION_TRIAL_20261124.md)
and its receipt for exact hashes, commands, the missing-config invocation
and configured contract coverage. The trial code and meshes remain local.
Checkpoint next alignment on scientific admission, then external transfer.
No accepted mixed epochs or full validation matrix.

## 2026-11-24 Fortaleza - freeze the grouping rule and reproduce the second-model veto

Record the researcher-approved conservative decision before running the second
model. The Ribbed positive cases pass and reversed and arc-split cases fail.
Synthetic grid disagreement returns inconclusive. Fresh CurvaBezier reproduces
eight exact meshes and the Step 3 trace. The limiting TRI's T6 edge is unchanged
under single grouping, so the selector returns no action. The archived manual
two-group variant passes the frozen comparator; it motivates one scoped neighbor
selection experiment. Draft PR 264 at e1775f38 has five passing tests with hosted
checks in progress. [Scope and receipt](GROUPING_ADMISSION_AND_TRANSFER_20261124.md).
No adaptive epoch or new native candidate acceptance.

## 2026-11-24 Fortaleza - stage the automatically selected adjacent group

The researcher approves the bounded CurvaBezier Step 3 transfer. The selector
identifies the unique finer neighbor, predicts T6 to T5 and vetoes an injected
fine request. The native application stages both groups while retaining the
reference owner and OBJ. Independent checks replay 106 front commits and five
smoothing passes and reject nine forged boundaries. Rules at grids 24 and 48
classify the final mesh as eligible. The regional final angle improves from
6.99 to 8.24 degrees and the global minimum is 1.87 degrees in both cases.
MSVC evidence and the corrected Python import are recorded in the
[transfer report](ADJACENT_TEMPLATE_GROUP_TRANSFER_20261124.md). PR 264 has
four successful hosted checks. Continue with portable experimental wiring.
No accepted mixed epochs.

## 2026-11-24 Fortaleza - wire the portable CurvaBezier grouping trial

Publish the runner and its dependencies as draft PR 265 at da4501a4. The exact
MSVC suite selects the eligible candidate, retains the original OBJ after a
forced rejection and prevents staging under a finer request. The output path
contains spaces and the runner starts outside its checkout. The native source
contracts and 26 Python tests pass. The earlier candidate and grid reports
match. [Runner and evidence](CURVABEZIER_GROUPING_RUNNER_20261124.md).
Hosted checks pending at checkpoint. No accepted mixed epochs or integration.

## 2026-11-24 Fortaleza - repair the runner baseline gate

The first PR 265 workflow failed the retained production inventory at root
CTest 84/85. Restore shared configuration bytes and scope the plan handoff
to the experimental staging subprocess. Exact corrective revision d6170d04
repeats the three selected OBJ hashes, passes configured 527 tooling, 26
reporting tests and 54 original source negatives. The new workflow passes all four hosted checks, including 85 CTests and 527 tooling tests.
[Review and evidence](CURVABEZIER_GROUPING_REVIEW_20261124.md).
No independent approval, integration or accepted mixed epochs.

## 2026-11-24 Fortaleza - retain the native mixed owner through a failed attempt and retry

Verify PR 265 remains green and unreviewed. Draft PR 266 at d7ab5327 moves the
mixed predecessor into the native attempt scope and copies its curve/tree
source. The injected fault temporarily switches the patch link and restores
the previous owner and OBJ before retry. The MSVC runner suite and 54 source
negatives pass; selected output hashes and the candidate reproduce the
preceding run. [Evidence](CURVABEZIER_OWNED_PREDECESSOR_20261124.md).
No independent approval, durable adaptive commit or accepted mixed epochs.

## 2026-11-25 Fortaleza - persist and recover the CurvaBezier selection

Verify PRs 265 and 266 remain green. Draft PR 267 at 0fd8ae1e stages the
selection record before the materialized OBJ, verifies native mesh/front
identities and provides a recovery command. Test interruption on both sides
of the record commit, corrupt artifacts and legacy records. The exact
MSVC executable from PR 266 reproduces and recovers each native outcome.
[Evidence](CURVABEZIER_SELECTION_RECOVERY_20261125.md).
No integration, accepted mixed epochs or full adaptive owner transaction.

## 2026-11-25 Fortaleza - measure curvature and size requests on the recovered mixed mesh

Regenerate and recover the exact CurvaBezier grouped output from PR 267.
Apply the existing native quadratic jet and independent oracle under both
recorded policies to TRI, the mixed predecessor and the recovered mesh.
All nodes have estimates, but boundary K/H accuracy remains inadequate for
global qualification. The complete second ring changes the balance of
errors. Recompute the approved geometric pilot requests on the recovered
mesh and obtain the same 13 positions and physical sizes in eight leaf
boxes as on its predecessor. [Evidence](RECOVERED_MIXED_CURVATURE_20261125.md).
Next run the bounded native geometric handoff. No accepted mixed epochs.

## 2026-11-25 Fortaleza - measure matched native feedback from recovered CurvaBezier

PR 268 at 7fea0630 applies three native leaf edits per arm under the original
cap. Eight requests saturate. Both successors preserve the contour and seed
cycles, then worsen final shape and deviation. The trace first diverges at
transaction 9 because the former valid apex falls outside the smaller
candidate neighborhood. Exact native suite and independent audits pass.
[Report and evidence](NATIVE_RECOVERED_GEOMETRIC_FEEDBACK_20261125.md).
Keep the two negative candidates, align the planned search-only comparison,
and count zero accepted mixed epochs.

## 2026-11-25 Fortaleza - generate a native mixed successor with curve feedback

PR 268 is green at 7fea0630. Draft PR 269 at 219183c7 keeps three native
leaf edits and reproduces all 106 front operations with the preceding
lookup boxes. Applying ten original interval splits gives 24 contour
segments. Retain the standard pass-one smoothing rejection. The guarded
comparison stages a valid 813-node, 852-face mesh and five valid passes.
The fine-grid geometric RMS decreases from 0.00971171 to 0.00296791. Retain
the boundary QUAD minimum-angle decrease and the different next requests.
Final MSVC runner, real source contracts and 30 reporting/recovery tests
pass. The final executable reproduces all three native dispositions.
For six of the ten split intervals, a child still exceeds the target
arclength. The next face requests reach six distinct eligible leaves.
Exact PR 269 hosted run 45543991736 completes four successful checks.
[Report and commands](FEEDBACK_SEARCH_AND_CURVES_20261125.md).
Next align admission, extend comparative coverage, and qualify the
staged source for a subsequent native generation. Zero accepted mixed
adaptive epochs and no global mixed curvature qualification.

## 2026-11-25 Fortaleza - compare mixed admission evidence and exercise shared sources

Recompute both residual-only native archives and their original TRI
controls on common UV grids. Geometric RMS improves with growth on both
models and local minimum contour-edge QUAD declines. Draft PR 270 at
dc6025e8 adds a read-only shared source witness. The Ribbed two-patch
excerpt stops at original zero error. The curved pair reaches native
capture and is refused for original corner ID discrepancies at
identical XYZ. Default TRI reaches step 3 on that same input. Verify
1, 4, 16 and 64 real seam edges with opposite directions and track the
accepted corner ID differences at every step. Exact MSVC default source
regression passes with 54 negative controls. [Report and receipts](MIXED_FEEDBACK_ADMISSION_SHARED_SOURCE_20261125.md).
Next qualify native curve and patch-corner provenance before shared
binary subdivision. Admission criteria and global curvature are still
open, and zero mixed adaptive epochs are accepted.

## 2026-11-25 Fortaleza - deliver visual evidence for both mixed feedback cases

Render two plates from the archived CurvaBezier, Ribbed and shared TRI
source files. Verify all six comparison OBJ hashes and four accepted
seam incidence archives. Highlight the corner QUAD on each experimental
successor, using the same UV frame for predecessor and successor.
Reopen the three-scene Blender 5.3 file and verify its face cycles, vertex
counts and camera extents. [Report and artifact hashes](MIXED_FEEDBACK_ADMISSION_SHARED_SOURCE_20261125.md).
PR 270 has four green exact-head jobs. Shared mixed capture, the admission
rule and global mixed curvature remain open. Zero mixed epochs accepted.

## 2026-11-25 Fortaleza - revise transfer qualification for mixed feedback

Audit the current model and accepted-step restrictions. The archived
CurvaBezier/Ribbed successors used distinct experimental drivers.
Read-only replay of the common sizing logic yields 13/10 and 17/8
face/curve requests on the archived inputs. A conforming unit plane with
zero residual at all indicator sites still yields three face and two
curve requests. Retain it as a negative control for the trigger.
[Generalization gate and evidence](MIXED_FEEDBACK_GENERALIZATION_20261125.md).
Use one native opt-in entry for both development cases and align a frozen
policy before reserved cases. Preserve shared-curve and two-epoch gates.
No new native execution, threshold or mixed scientific acceptance.

## 2026-11-25 Fortaleza - run portable feedback on two native predecessor geometries

Draft PR 271 at e470cbe2 reuses the native original curve and quadtree source
and the existing mixed sizing pilot on CurvaBezier Step 3 and Ribbed patch
12 Step 2. Both candidates stage through the same MSVC binary. Preserve
original accepted TRI, predecessor and tree bytes, and reject an altered
tree before feedback. Sampled RMS and TRI shape improve while minimum QUAD
angles deteriorate. Retain each first-pass unguarded rejection and the five
guarded passes. Compare actual child arcs with requests, and measure the
dimensionless residual for the next decision without selecting a threshold.
The new native suite, source contracts, legacy grouping and 30 Python tests
pass locally. [Report and receipt](PORTABLE_MIXED_FEEDBACK_20261125.md).
The researcher selects relative geometric residual as the first trigger
to study, with shape assessed after generation. Qualify the parameterized
trigger while threshold and growth remain open. Do not count a staged
successor as an accepted epoch. The shared-curve gate,
owned native successor reentry and global curvature remain open.

## 2026-11-25 Fortaleza - independently replay recent Codex feedback progress

The researcher requests a verification of recent local progress. Review PRs
263--270 and build exact dc6025e8 in Linux GNU C++17 Release. Reporting,
native source, grouping/rejection/recovery and all four feedback-mode
observations reproduce. A local sanitizer build succeeds but LeakSanitizer
aborts the initial reference due to its ptrace runtime limitation; retain
that failure without qualifying memory or relaxing detection.

Before checkpoint publication, detect canonical e04db5dc and new PR 271
e470cbe2. Incorporate the concurrent work, rebuild its exact source and
rerun 30 Python controls, six source captures/three reversals/54 negatives,
the full grouping application suite and the new portable suite. CurvaBezier
and Ribbed source hashes, successor hashes and paired grid-48 reports
exactly match the prior MSVC receipt. The altered tree is refused before
feedback. Inspect successful hosted portable Clang ASan/UBSan/LSan and
frozen TRI logs. The final hosted read confirms all four jobs successful,
including Windows; the earlier pending observation is retained as history.

[Audit and evidence](INDEPENDENT_FEEDBACK_AUDIT_20261125.md).
The active next item remains relative geometric trigger qualification,
not reimplementation of the common entry. Preserve no-action, regional
shape/growth, realized-size, shared-source and two-epoch limits. No source
merge, threshold adoption, main update or PR-state change was made.

## 2026-11-25 Fortaleza - qualify the relative mixed refinement trigger

Implement the aligned geometry-first trigger behind explicit tolerance on
draft PR 272 at 7d17c5d3. Test flat no action, graded influence on a flat
neighbor, rescaling and invalid parameters. The same native image
reproduces both zero-tolerance successors, rejects the foreign tree and
records a native no-action Ribbed source. Measure the four threshold
breakpoints and one selective CurvaBezier reconstruction. It reduces
RMS by 23.8 percent with 6.6 percent more faces and preserves the
minimum contour-edge QUAD angle. All local native and 33 Python tests pass.
[Report and receipt](RELATIVE_MIXED_TRIGGER_20261125.md).
PR 271 completes four hosted checks. Tolerance adoption, quality admission,
reserved cases, shared curves, subsequent epochs and curvature remain open.

## 2026-11-25 Fortaleza - compare a common relative tolerance across both native inputs

Verify four exact-head checks for PR 272. Use the retained MSVC image
to stage the one missing selective Ribbed geometry. The QUAD-only
arm gives 604 faces, 19 contour segments and 13.0 percent smaller
geometric RMS. Match complete ordered requests for the five common
tolerance intervals to all native outcomes or no action. Retain regional
angle and shape losses and the first-pass unguarded smoothing rejection.
The initial read-only matcher fails its tuple-to-array comparison;
the canonical JSON replay succeeds. [Report and receipt](COMMON_RELATIVE_CALIBRATION_20261125.md).
Next align regional quality and growth before freezing any common
tolerance for reserved inputs. No mixed adaptive epochs accepted.

## 2026-11-25 Fortaleza - evaluate regional quality floors and localize the limiting TRI

Draft PR 273 at c06f69fe implements the approved floor study as a read-only
assessment. Configure each angle and shape floor and the growth limit
explicitly. Across eight archived evaluations, a zero-floor control
isolates the budget. Predecessor-derived floors block both selective
candidates. The identical CurvaBezier interior TRI is present in both
seed regimes. It measures 6.37 degrees before guarded smoothing and
8.04 after it. Six directed controls and 39 Python checks pass.
[Report and receipts](REGIONAL_QUALITY_GUARDS_20261125.md).
Next trace native creation and the adjacent size change. No new native
run, adopted quality profile or accepted mixed epoch.

## 2026-11-25 Fortaleza - retain the guarded birth front and localize the missed pair

Draft PR 274 at 84113d9c exposes the guarded birth trace. Selective
CurvaBezier source and candidate stages reproduce byte for byte.
Replay 112 transactions independently and reject a forged active edge.
The limiting TRI appears at operation 83. At operation 13, the chosen
base could form a QUAD of S = 1.50 using alternate active local vertices.
Local native regressions and 39 Python controls pass.
[Evidence](GUARDED_INTERIOR_FRONT_TRACE_20261125.md).
The researcher approves testing remaining local pairs only on a TRI
fallback. Candidate selection and scientific acceptance are unchanged
in this checkpoint.

## 2026-11-25 Fortaleza - compare additional local pairs on the same native input

Draft PR 275 at 779ac343 implements the approved opt-in experiment. Compare
the same executable and input on both arms. Operation 13 creates the single
replacement QUAD. The limiting interior TRI disappears. Final interior TRI
minimum angle rises from 8.04 to 14.36 degrees, while interior QUAD minimum
angle falls from 50.86 to 44.57 after smoothing the same birth face. Both
arms have 737 nodes and 16 contour segments. Sampled geometric RMS increases
about 0.064 percent. The predecessor-derived profile still blocks the
candidate. The native and portable regressions pass and the two control
wrapper failures are retained with a successful independent artifact readback.
[Report and receipt](ADDITIONAL_LOCAL_PAIRS_20261125.md).
Next align one native transfer comparison on Ribbed Bracket. No profile
adopted and zero mixed adaptive epochs accepted.

## 2026-11-25 Fortaleza - transfer additional local pairs to Ribbed Bracket

Run the approved comparison with the exact PR 275 image, matched Step 2
requests and archived baseline. The experimental run stages. Both sides
have 623 nodes, 22 contour segments and the same sampled source and leaf
tree. Three fallback QUADs appear. The final interior TRI minimum angle
falls from 18.37 to 10.90 degrees, and shared-site geometric RMS rises
35.49 percent. Independent replay passes 100 operation checks and rejects
a forged score. Two initial analysis failures are retained. The final
readback verifies exact coordinates and oriented face cycles. The first
replacement accounts for about 91 percent of the net squared-error
increase. [Transfer and receipt](ADDITIONAL_LOCAL_PAIRS_RIBBED_20261125.md).
Keep minimum-S fallback experimental and align a local relative deviation
and physical size test. No policy adopted and zero mixed epochs accepted.

## 2026-11-25 Fortaleza - screen prospective QUAD geometry on both development fronts

Assess all 12 eligible QUADs in the two original histories at matched
footprints with five, 64 and 256 samples. Two improve local geometric RMS
and ten degrade it. The maximum sampled deviation normalized by the
active physical edge separates both groups over all three sampling sets.
The proposed single development ceiling is 0.045. The initial screen
stopped on a nonconvex union without a shape score. The corrected replay
and 24 scale controls pass. [Report and receipt](PROSPECTIVE_PAIR_GEOMETRY_SCREEN_20261125.md).
PR 275 hosted matrix is 4/4 on its exact head. Await alignment on the
new native criterion. No new native run, policy or accepted mixed epoch.

## 2026-11-25 Fortaleza - implement and run the prospective geometry screen

Implement the opt-in 0.045 active-edge criterion in draft PR 276 and keep
the original shape and tie rules. Both focused native inputs stage. CurvaBezier
reproduces its prior additional-pair output. Ribbed blocks the two harmful
early operations and keeps one eligible replacement at operation 61. Its
final interior TRI angle and count reproduce control, with slightly lower
sampled RMS. Retain the initial native population-contract rejections and
the initial Python tuple/list check failure. The pure-face contract,
boundary controls, ordinary native application and independent archived
decision replays pass. [Report and receipts](NATIVE_PAIR_GEOMETRY_SCREEN_20261125.md).
Next review the scoped changes and align mixed admission. No reserved
geometry or accepted mixed epoch in this experiment.

## 2026-11-25 Fortaleza - certify ordered subdivision on real native boundaries

After alignment on the boundary relationship, implement the optional
refinement certificate in draft PR 277 at 9aabc278. Directed native
replays preserve both PR 276 meshes and certify 2 and 8 insertions.
Six boundary captures validate split and unchanged input with 24 new
negative controls. A foreign bound tree is rejected before feedback.
PR 276 exact-head hosted checks complete 4/4. Archive admission replay
still finds interior TRI angle and shape blockers. The CurvaBezier face
born at operation 81 is the sole interior TRI below both diagnostic floors.
[Report and receipts](CERTIFIED_BOUNDARY_REFINEMENT_20261125.md).
The operation has no eligible extra QUAD. Next inspect the seed edge
from QUAD 204. Mixed owner reentry and acceptance remain open.

## 2026-11-25 Fortaleza - trace the limiting CurvaBezier template edge

Inspect all 81 recorded front states for seed QUAD 204's short edge.
The original TRI already gives the best physical birth angle at that
base. The local fixed-position reconnections preserve group counts only
when the diagnostic floors remain unmet. The balanced parent grouping
projection doubles the UV edge length without removing an active size
request. PR 277 exact-head hosted jobs pass 4/4. Await alignment on the
single native grouping trial. [Diagnosis](CURVABEZIER_OP81_TEMPLATE_EDGE_20261125.md).
No regenerated state or admitted mixed epoch in this checkpoint.

## 2026-11-25 Fortaleza - apply the approved parent grouping in the native trial

Publish the previously local diagnostic and verify it on `quad-templates`
at 84af5cbb. A temporary branch reference allowed the canonical fast-forward
after the earlier ref update errors. Implement the opt-in grouping on the
bound native CurvaBezier Step 3 successor in draft PR 278. Independent
readback verifies four leaves replaced by their parent, identical
requests and certificate, and a refused protected request. The original
operation 81 TRI is absent. The final interior TRI minimum becomes 18.16
degrees; faces fall from 779 to 754 and geometric RMS by about 1.01 percent.
The current quality diagnostic still blocks on interior TRI angle and
shape. [Native comparison](NATIVE_OP81_PARENT_GROUPING_20261125.md).
The operation 74 seed edge comes from leaf 148, whose parent touches the
contour. Next assess the contiguous physical transition.
No accepted mixed epoch.

## 2026-11-25 Fortaleza - diagnose the level-4 to level-3 transition at operation 74

Read the final PR 278 matrix with all four jobs passing, and bind the
archived grouped CurvaBezier front. All 74 front states retain the short
edge without a better closure. Nineteen region-preserving reconnections
and the guarded single-node displacement sweep do not clear both TRI
floors. Project one refinement of the adjoining coarse leaf 154 on the
ungrouped control. Two children satisfy the existing template clearance.
[Transition evidence](CURVABEZIER_OP74_SIZE_TRANSITION_20261125.md).
Await alignment on the single native request. No accepted mixed epoch.

## 2026-11-25 Fortaleza - refine CurvaBezier leaf 154 in the native candidate

Run the original ungrouped screened plan with one additional face request.
The exact PR 278 MSVC image stages the 789-face candidate with the same
certificate and eight new template QUADs on two of the four children.
Both interior TRI in the control are absent in the candidate. The contour-
vertex TRI minimum remains 2.27 degrees. At 2,304 common sites the geometric
RMS falls by 0.71 percent versus the 779-face control. The candidate has no
regional diagnostic veto, with the interior TRI group absent in both the
predecessor and this candidate. [Trial evidence](NATIVE_LEAF154_REFINEMENT_20261125.md).
Exact PR 278 hosted checks remain 4/4. Prepare a prospective mixed admission
and stopping contract using both development cases before reserved runs.
No accepted mixed epoch.

## 2026-11-25 Fortaleza - draft mixed admission and stopping using both development histories

Recompute geometric residual and physical regional shape for five native
staged archives at their original mixed predecessor. Bind the source, mesh
and four native certificates. Reject 24 contour and certificate mutations
in the detached replay. All five improve sampled RMS and maximum deviation.
Only one clears the old diagnostic. It retains 26 of 97 contour-vertex TRI
below 5 degrees. The Ribbed successor improves those transition angles
while making additional low-quality interior TRI. Evaluate the existing
profile and a prospective check of both the count and fraction of faces
below a regional target. Record the proposed safety, growth, stop and
rollback rules for alignment. [Admission draft](MIXED_ADMISSION_CONTRACT_20261125.md).
No new native generation, adopted thresholds, reserved geometries or
accepted mixed epochs in this replay.

## 2026-11-25 Fortaleza - implement opt-in progressive eligibility

The researcher selected progression by stages. Implement the explicit
single-patch assessment above the existing native staging path in draft
PR 279 at f6ae3471. The fresh CurvaBezier candidate, certificate and
original source match the retained run. Ribbed exercises the archived
indexed input. Run 36 local Python checks, two diagnostic blockers, six
archive refusals and an archived no-request control. The first archive
parser treated cached contour metadata as XYZ. Correct the field ranges
and retain that failed invocation in the evidence. Exact-head hosted
checks are running. [Implementation evidence](PROGRESSIVE_ADMISSION_GATE_20261125.md).
Align a numerical profile before moving eligible candidates into native
accepted-owner state. Zero accepted mixed epochs.

## 2026-11-25 Fortaleza - replay one frozen progressive profile across both models

Fix the [common development profile](profiles/progressive_admission_development_v1.json)
before evaluation. Its safety floors, quality targets, geometric gain
and cost limits are identical across the four certified archives.
All improve geometry. All are blocked on transition TRI safety, and
Ribbed also exceeds the growth cap. Match faces by oriented connectivity
after an initial export-order assumption failed. The worst transition
TRI in CurvaBezier and Ribbed already fail at native birth. Confirm 10
local progressive tests and four exact PR 279 hosted jobs. [Replay and
trace](COMMON_PROGRESSIVE_PROFILE_20261125.md).
Compare one common size realization rule before front closure next.
No new generation, reserved case or accepted mixed epoch.

## 2026-11-25 Fortaleza - test one additional native contour division on both development models

Reproduce archived physical curve and face requests. Bind each
limiting transition TRI to a short seed QUAD edge and an original
long contour interval without a size request. Use the common 1.35
selection rule to add one original binary interval division per model.
Face request traces and realized leaf lists remain byte-identical.
The worst TRI at the contour transition improves modestly in both
arms and the original faces are absent. A 4.43 degree interior TRI
remains on CurvaBezier, and Ribbed remains above the growth limit.
Both candidates stage and both remain blocked by the common profile.
[Native evidence](COMMON_TRANSITION_CONTOUR_SPLIT_20261125.md).
Next project coordinated contour and template sizes. Zero accepted
mixed epochs.

## 2026-11-25 Fortaleza - coordinate one protected template grouping with each extra contour split

Use the existing interior grouping on the parent supplying the short
seed edge. Both projections retain 2:1 balance and every active size
request after correcting the clearance metadata lookup. Two directed
native runs keep their certified contour and replace exactly the
proposed four leaves. The projected longer seed edges are present.
CurvaBezier improves the poorest interior TRI and Ribbed improves
its poorest transition TRI. Neither passes the frozen profile.
Trace 44 of 47 and 19 of 19 remaining poor transition TRI to a seed
edge at birth. [Native result and lineage](COORDINATED_TRANSITION_SIZING_20261125.md).
Next project a common correction across the complete interface.
No accepted mixed epoch.

## 2026-11-25 Fortaleza - batch protected template parents and reach the common face budget

Project the full contour-vertex interface with the frozen physical
floors and original protection rules. Stage two additional parents
on CurvaBezier and five on Ribbed with draft PR 280 at 3e01614c.
Both fit 10 percent growth, with 749 and 559 faces. The one-parent
control reproduces seven native artifacts. Duplicate and protected
requests are refused, and the native boundary contracts and ten
progressive checks pass. Shape still blocks both. The remaining
contour-touching parent evidence covers 25 and 14 poor TRI.
[Batch results](INTERFACE_PARENT_BATCH_20261125.md).
Hosted exact-head checks run. Next project the contour-adjacent
handoff. Zero accepted mixed epochs.

## 2026-11-25 Fortaleza - combine protected contour-side handoff with interior grouping

Project five CurvaBezier and one Ribbed contour parents under the same
request guards, clearance and template dispatcher. Draft PR 281 at
acb12e6b stages both cases with exact predecessor and contour evidence.
The transferred regions improve locally and both patches use fewer
elements than their mixed predecessors. Record the RMS tradeoff and
remaining shape veto. Existing-only apex replay finds just one valid
TRI at each worst active base and no TRI above the profile floor.
Native compatibility, three refusals, the boundary contracts and
ten progressive checks pass. [Combined results](CONTOUR_TEMPLATE_HANDOFF_20261125.md).
PR 280 exact checks pass and PR 281 checks are running. Next align
prospective front point placement. Zero accepted mixed epochs.

## 2026-11-25 Fortaleza - test bounded legacy ideal points on both native fronts

Draft PR 282 at ffdf0b26 adds a point only to a sub-floor transition
TRI whose active front supplies no eligible existing apex. CurvaBezier
inserts two points and reduces the number of transition TRI below the
floor, but a later TRI at one of the inserted points is 1.00° at birth
and 1.85° after smoothing. Ribbed inserts no points and reproduces the
control mesh. Both preserve the certified curve, requests and grouped
tree. Both meet growth and remain blocked on shape. Independent archive
replay verifies each insertion. MSVC C++17 builds, original-curve native
controls, progressive Python controls, direct three-stage article
application and byte-identical default replay passed. The build-directory
CTest invocation and validation adapter limitations are retained.
All four PR 281 hosted checks passed. PR 282 hosted checks were running.
[Native results](LEGACY_IDEAL_FRONT_POINT_20261125.md).
Next compare the whole affected closure with and without the point under
one shared rule, pending alignment. Zero accepted mixed epochs.
