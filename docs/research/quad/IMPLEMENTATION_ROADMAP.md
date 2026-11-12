# Plano de pesquisa e implementação QUAD — APMesh

**Estado:** M0 technical baseline inventory **qualified with documented serial-scope exceptions**; no QUAD algorithm implementation in the production pipeline. **Criado em:** 2026-11-08. **Revisão científica prevista:** 2026-11-11 com Joaquim Bento e Creto Vidal.
**Branch:** `quad-templates`; **baseline imutável de origem:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (PR #183).  
**Auditoria:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md). **Fonte histórica:** Bento et al., *Combinação das Técnicas de Quadtree e Delaunay para Geração Automática de Malhas de Elementos Finitos*, SIBGRAPI 1993, Figura 7 e seção sobre contorno.

## Continuity and mandatory research handoff

**Canonical current state:** [STATE.md](STATE.md) — read this before interpreting any milestone in this roadmap.  
**Conversation/agent workflow:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md) — mandatory at each substantial QUAD session.  
**Append-only activity:** [SESSION_LOG.md](SESSION_LOG.md).  
**Current M0 gate evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md).

**2026-11-08-03 measured update:** M0 remains OPEN. A preserved local MSVC C++17
build and Eistute/Book captures have verified log/binary identities and offline
comparison evidence: 9 states, 45 exact scientific artifacts and 123 positive
boundaries. GCC/Linux, full research-branch CTest/Python and applicable memory
qualification remain pending. The Windows doctor/profile failure is retained;
see the [review receipt](evidence/M0_MSVC_REVIEW_20261108.json).

**2026-11-08-04 measured update:** [PR #184](https://github.com/tiagosombrra/apmesh-modernization/pull/184)
integrates bounded GNU validation portability into the research branch at
`a29711bea1e38f6a1ea49dde443f0ae58ebadfa7`. Exact head/merge Linux regression passes
75 CTest / 527 Python (all original 526 plus one new control). Strict Linux article
comparison passes 9 states / 45 exact artifacts / 123 positive boundaries; preserved
MSVC evidence remains separate. M0-G6 applicable memory disposition and M0-G7
semantic caller inventory remain pending, so M0 stays OPEN and M1 is not admitted.
See the [GNU qualification receipt](evidence/M0_GNU_QUALIFICATION_20261108.json).

At session end, write a verified GitHub checkpoint: update the canonical state,
append the session log and record executed/unexecuted gates. Update this roadmap
only for an actual milestone transition, changed approved scope or adjusted gate.
New ChatGPT/Codex sessions must resume from these files and current remote commits,
not from assumed recall of earlier conversations. The protocol is not an automatic
scheduler: a connected actor must perform the write. If tools are unavailable,
report that the checkpoint could not be persisted.


## 2026-11-12 — R2b2 real model-wide source axial curve valence 4 (Eistute) and 28 (Book) discovered; sheet pairing separate from source identity

The exact original source `5952a0ea6acfa408e352dc82cb36c68a6d98d7d7` was double-qualified ([feature CI #43256219375](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43256219375), [PR #43256234958](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43256234958), **4/4 each**, 87 root CTest, 527 Python, native GCC/MSVC QUAD 16/16 each, frozen TRI Eistute/Book science parity). It built the FULL actual original source PatchReader incidence graph: Eistute **4 patches, 13 curves, one curve shared by all 4**; Book **28 patches, 85 curves, one curve shared by all 28**; every patch has one true same-epoch original Adapter boundary record, no synthetic cross-epoch stitching. Requiring pairwise opposite boundary traversal for ALL incident patch pairs produced 6 and 378 orientation rejections respectively **before inspecting any source XYZ**. This is not evidence the source geometry is wrong: an edge with valence >2 has no globally valid all-pairs opposite orientation.

The current isolated feature `1535b51ee42d19a406effbea36570514c4641bfb` now audits **source node ID, curve parameter/index, XYZ equivalence for all incidences independent of sheet traversal**, and separately counts same/opposite orientation pairs. It marks central high-valence group as requiring explicit **per-sheet patch sector pairing** and does not blindly weld all patches. New strict required CI [feature #43257927657](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43257927657), [PR #43257943351](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43257943351) PENDING; never claim geometry matching until those exact measured markers are present. Continue to preserve original within-patch source QUAD/AFT physical evidence without calling full 4/28 global mesh accepted. Actual per-sheet topology, all-patch adapted QUAD/AFT, typed mixed physical `SubMesh`, atomic retry rollback, sanitizer lifetime and 1993 numerical policy remain open. `main` and `quad_uv` unchanged, PR #214 draft.

## 2026-11-12 — Shared central high-valence original curve identity reconciled; model-wide source complete, global hybrid still blocked

Research [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), head `1d46ba4abce35cc5a28ec214c0d5787414928889`, passed exact [feature CI #43267126924](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267126924) and [PR CI #43267143566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43267143566) **4/4 EACH**, native Linux+Windows QUAD **16/16** each, root Linux CTest **87/87**, Python **527/527**, original frozen Eistute/Book TRI scientific equivalence PASS. In first coherent actual original GeneratorAdaptive epoch, ALL **4 Eistute** and **28 Book** patch incidences agree in the original central shared curve's **sample parameters, original source NODE IDs and XYZ** after using the ORIGINAL curve's terminal owner ID, rather than the AFT corner's alias ID from the next side. Original source ID mismatches previously observed as 6 Eistute/378 Book now **ZERO**, with new invalid terminal-ID/XYZ controls PASS; no production changes. The measured original high-valence radial fan contains Eistute 4 distinct sectors (min 1.5708 rad) and Book 28 distinct sectors (min 0.0318123 rad); no coincidence/XYZ mismatch at one original sampled curve parameter, but nonmanifold edge/vertex incidence policy is UNDECIDED and **automatic pairing/welding disabled**.

**Next active implementation:** execute true original source-adapted T1–T6 QUAD + original exterior AFT and independent PatchBezier physical XYZ checks on **ALL 4/28 real patches** of a single coherent epoch, capturing explicit accepted/rejected/partial owner cleanup. Qualify per-curve radial ordering over multiple actually sampled parameters and the appropriate nonmanifold fan incidence without converting source curve identity into global `SubMesh` ownership prematurely. Only then R2c typed mixed four-node physical `SubMesh` transactional publication/rollback, repeated adaptation and sanitizer lifetime gate. Historical 1993 numerical point method not advisor-approved, production main and disabled `quad_uv` unchanged, research PR draft.

## 2026-11-12 — Source-exact dynamically adapted AFT physical PatchBezier XYZ accepted for two real patches (R2b2 bounded)

Feature `24349b74befb2308bb3d6202f747998def5eedd3` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) passed exact [feature push #43246304785](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246304785) and [independent PR #43246317558](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43246317558), **SUCCESS 4/4 each**, Linux GCC / Windows MSVC native QUAD 16/16 each, root 87/87, Python 527/527, frozen original Eistute/Book TRI scientific equivalence PASS. Actual original per-model dynamically adapted `Adapter::AdaptCurve` boundary with native parametric midpoint/length and Quadtree geometry generated **Eistute 472 interior QUAD + 152 original exterior AFT TRI** and **Book 188 QUAD + 100 exterior TRI**, each with closed/watertight *within-patch UV* interface. Every UV face and all 40 Eistute/36 Book original boundary source nodes were subsequently tested against independently loaded real `PatchBezier::Parameterize/Qu/Qv` and original source curves in 3D: **Eistute 1096 oriented physical facets, minimum alignment 0.760759, max source node XYZ discrepancy 8.97016e-15; Book 476 facets, minimum alignment 0.999823, max error 2.48253e-16.** Both independent CI root logs explicitly report `dynamic_physical_admitted=1`, `negative_controls=1`, `rejection=none`. Three negative cases explicitly reject a corrupted source node, inverted TRI and invalid UV.

**Next active gate R2b2→R2c:** prove actual original dynamically adapted **shared curve edge/sample identity and XYZ orientation across patches and sheet incidences** for **all 4 Eistute and 28 Book patches**, record every admitted/rejected interface; avoid interpreting one patch/model as full external model mesh. Then design/test typed physical mixed QUAD/TRI `SubMesh` publication and atomic previous accepted mesh rollback, repeated adaptive loops and native sanitizer lifetime qualification. Research numerical centroid/1993 point rule remains unapproved, and production `quad_uv` CLI and `main` remain unchanged; PR #214 unmerged until independent complete scientific review.

## 2026-11-12 — R2b2 true dynamically adapted source QUAD+original AFT exterior accepted (bounded UV only)

Research [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) head `1f2da57ff4dc4dd6dde358ede0efd772da3fb3ba` passed exact [feature CI #43206236696](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206236696) and [independent PR #43206246419](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43206246419), **both 4/4**: native GCC/MSVC QUAD **16/16 each**, Linux root CTest **87/87**, Python **527/527**, frozen source TRI scientific parity **PASS**. Original `GeneratorAdaptive` source chart is now reconstructed including actual curve-generated `Edge::makeParamMid` parametric midpoints and normalized edge lengths, and fed into two independent owned copies of the genuine original refined Quadtree. Legacy native TRI templates seed the reference seam; selected T1–T6 QUAD feed original exterior AFT in the second copy. Every original strict UV gate passed in **one** actual dynamically adapted source chart per external model: **Eistute 40 original curve boundary sites, 130 leaves, 472 QUAD + 152 exterior TRI**; **Book 36 sites, 64 leaves, 188 QUAD + 100 exterior TRI**. Both `admitted=1`, `rejection=none`; these values are measured and retained in verbose CI logs, not theoretical estimates.

**New primary open gate is PHYSICAL XYZ of these exact source dynamic QUAD/TRI faces**, checking native `PatchBezier` and curve-node source correspondence plus per-face normal/Jacobian orientation, then full external model patch shared seams and physical typed `SubMesh` transaction/rollback (R2c). Previously all 4 Eistute and 28 Book source patches mapped through physical Bézier under a different fixed 16-segment research contour; that is not full dynamic output proof. Numeric arithmetic midpoint still experimental, not 1993 historical formula. Independent repeated-in-process memory sanitizer gate remains open. Keep draft PR, source TRI and production `main`, CLI `quad_uv` disabled.

## 2026-11-12 — R2b2 original Adapter parametrically curved source tree replay exactly qualified (not yet full curved AFT)

Feature `76250559951b5ac0e45982d0c86606d001feb53a` on [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) now captures original serial `CurveAdaptiveParametric` boundary edge UV midpoints from native `makeParamMid()` and pre-generation normalized arc lengths as values, then mirrors the exact native per-attempt refined Quadtree leaf hierarchy, cell depths, 2:1 neighbors and original boundary edge-cell ownership on separately owned objects. The bounded real `GeneratorAdaptive` test uses **one nontrivial dynamically adapted source chart each** from Eistute and Book, rejecting a mutated source boundary. This is not the independent fixed 16-site research contour and does not borrow original curve pointers. [Feature CI #43204053789](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43204053789) and [PR CI #43204061864](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43204061864) both **SUCCESS 4/4**, native GCC/MSVC QUAD **16/16** each, root CTest **87/87**, Python **527/527**, frozen TRI science parity **PASS**. Preserve **all** root/source scientific acceptance thresholds.

**Active R2b2 blocker:** The original exterior AFT has NOT yet been run and fully qualified on these reconstructed *actual adapted* Eistute/Book source charts; next seed native T1–T6 QUAD interiors in the independent real cloned tree, run original exterior AFT, verify front drain, every original QUAD seam, area/overlap and physical `PatchBezier` UV–XYZ geometry, preserving prior accepted source TRI and fail-closed same-owner retry. The previous fourth successive in-process fixture SIGSEGV remains unresolved until native sanitizer qualification. Only then research PR merge review and R2c typed physical mixed `SubMesh`; production `main`, historical point rule and disabled `quad_uv` unchanged.

## 2026-11-12 — R2b2 first original Adapter owned native hierarchy and QUAD/AFT replay candidate (not yet certified)

Feature `458cbea21e8330e23cdd5b3ca9c89f38d0c1d20d` in draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) now has a native `source_tree_replay` research-only utility that reproduces the actual original `Adapter::AdaptDomain` boundary, copies all native refined-cell subdivisions with independent owners, validates exact cell leaf-neighbor geometry and rejects tampered source UV, before independently invoking existing native TRI templates vs selected QUAD T1–T6 and original AFT exterior on a real single-patch Adapter fixture. No production default code is changed. The first feature `8f48280b` was blocked by a research-only C++ getter constness compile failure; source `458cbea2` repaired it. Current exact feature/PR native Linux and MSVC QUAD + frozen TRI have passed; **root CTest and Python are pending**. Do not equate a four-corner single-patch Adapter witness with curved Eistute/Book: a later gate must replay the actual multi-site `CurveAdaptiveParametric` source with independent midpoint and arc-length semantics before source-exact original AFT acceptance. Preserve failure evidence and fourth-consecutive-process lifetime risk; never advance R2c on an unqualified replay.

## 2026-11-12 — Actual live Adapter source contour and bounded original AFT Bezier physical trials now exact 4/4 (R2b2 partially qualified)

Research [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) source `8b0a774f463ce450aedeee216d978965428ef481` passed exact [feature #43198429209](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198429209) and [PR #43198438695](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43198438695) **SUCCESS 4/4**, native Linux/Windows QUAD **16/16 each**, root Linux **87/87 CTest**, Python tooling **527/527** and frozen Eistute/Book TRI scientific parity. Actual real original serial `Adapter` source boundary/curve samples/physical node IDs/UV orientation are now copied read-only before original Quadtree refinement, correlated to the same refined source tree and true global attempt callback ordering. An intentional pre-refinement exception passes with zero refined snapshots and unchanged accepted patch mesh. The new source-physical evidence log explicitly reports **Eistute 4 mapped / 0 rejected**, **Book 28 mapped / 0 rejected**, plus a built-in curved patch mapped, but these **all use a separate fixed 16-segment research UV source contour and DO NOT yet use actual Adapter adaptivity for the owned QUAD/AFT**.

**Next specific R2b2 integration:** Construct research-owned exact original-source per-attempt refined tree and curve boundary using immutable real Adapter capture (no borrowing live owner across retries); run original AFT exterior around selected QUAD interiors with native physical Bézier curve endpoint/orientation/XYZ, UV coverage and late-rejection rollback. Investigate separately the earliest fourth-successive single-process fixture SIGSEGV using memory diagnostics; the later fixed `snapshots.front()` zero-snapshot test defect was a distinct error. Only then research-only merge PR #214 and exact postmerge certification; then R2c typed mixed `SubMesh`, repeated adaptation and eventually `quad_uv` CLI, all still blocked by independent scientific acceptance.

## 2026-11-12 — R2b2 live original Adapter curve boundary observer (strict retry identity)

Experimental opt-in research `AdapterBoundaryCapture` is implemented in [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214), source `3330e0ed9dfa771ad2c38813697ba7b0fa7b83c7`. It copies the true original four curve sides and sampled `NodeAdaptive` values as they are emitted by serial `Adapter::AdaptDomain`, before Quadtree refinement; the real `GeneratorAdaptive` observer checks exact native `Boundary` vertex/edge continuity to the same subsequently refined Quadtree. It does not substitute any source curve sampling or change default original TRI. First candidate `7797b8b2` reproduced two genuine instrumentation blockers: a fourth repeated test scenario native segfault and Eistute reuse of a logical patch/retry tuple, which cannot serve as a unique per-callback ID. Architecture source inventory SHA needed updating; an additional workflow generation defect was repaired in `7dcb67d8`. Latest source uses strict callback chronology and a **separately registered** pre-refinement exception test. None of these mean complete R2b2 physical mesh integration or established ASan/UBSan lifetime safety.

**Current test gate pending:** exact latest feature/PR 4/4 on `3330e0ed` (Linux+Windows native 16/16 QUAD each, root 87 CTest including real Generator outcomes Eistute/Book and separate boundary-abort, 527 tooling Python, frozen TRI Eistute/Book parity); review the new per-patch physical admission output. Preserve the original observed fourth-scenario segfault as unresolved repeated-run memory risk. After these pass, require source-native selected QUAD/AFT completion using **the actual captured Adapter per-attempt contour and compatible live refined tree**, not fixed 16-site synthetic source, and complete late-failure acceptance tests before research-only R2b2 merge and physical R2c. No production `quad_uv` CLI, no historical 1993 point rule approval.

## 2026-11-12 — R2b2 source Bézier admission evidence; real Adapter contour remains open

Draft [PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) source `c103c77d5c390873760744912533ecaf7dd5a2a9` passes exact [feature #43189723674](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43189723674) and [PR #43189733267](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43189733267) **SUCCESS 4/4 each**: Linux+Windows native QUAD 16/16 CTest, root 86/86 CTest, Python 527/527, frozen Eistute/Book original TRI parity. The actual native R2b2 AFT generates positive/nonoverlapping exterior TRI around source QUAD interior; original QUAD split edge identity and oriented seam are preserved. Controlled abort after TRI face emission rejects retry and destroys partial AFT owner.

The new bounded source physical probe passes on one native curved Bezier patch and at least one per source Eistute/Book model; it maps direct AFT UV faces via real `PatchBezier::Parameterize/Qu/Qv` and source curve evaluations and protects original `SubMesh` pointer. The test attempts 4+28 external patches but admits only existence (`mapped >= 1`) and does not persist complete accepted/rejected counts. No full model-wide hybrid guarantee, no physical QUAD/TRI publication. Original fixed 16-segment UV boundary is a research chart, **not the actual `Adapter::AdaptCurve` ordered sample stream**. This is a **qualified bounded physical-source gate** but not complete R2b2 or R2c integration.

**Next actionable R2b2-live-Adapter:** capture the original Adapter's ordered UV boundary and source CurveAdaptiveParametric parameter IDs/orientations on a real physical patch for a concrete adaptation attempt; reconcile exact AFT outer contour and QUAD split region on the same tree without source TRI interior publication; exercise late rejection preserving previously accepted source patch mesh/curves. Quantify accepted/rejected physical patch counts per Eistute/Book and independently evaluate Jacobian/orientation/coverage. Keep PR #214 draft/unmerged until this admission; preserve production `main`, historical 1993 point rule pending, and disabled `quad_uv` CLI.

## 2026-11-12 — R2b1 exact postmerge qualified; R2b2 native exterior draft

[R2b1 exact merged-source Actions #43138162247](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43138162247) is confirmed **SUCCESS 4/4 on `8da5e523531b3579d9bacd69bbfe16ec96efe76d`**, with native Linux/Windows 16/16 QUAD CTest each, root 85/85 CTest, 527 Python controls and frozen TRI Eistute/Book parity. The older pending sentence below is an immutable earlier observation, not the present R2b1 status.

**Active next research stage:** [draft PR #214](https://github.com/tiagosombrra/apmesh-modernization/pull/214) on feature `quad/integration-r2b2-exterior-aft-20261112`, candidate `319cfc90e34530b220ff55c7e9febc951572e78a`, invokes original AFT geometry/topology on a live owned reversed QUAD front and measures actual exterior TRI incidence, exact source perimeter, positive signed triangle UV areas, total patch area and unmoved QUAD seam points. A separate convex polygon clipping audit detects TRI/TRI and TRI/QUAD positive-area overlaps, including three synthetic positive/adversarial cases. Fixed native predecessor `28ee9b3` passes 16/16 native CTest on GCC and MSVC, including strict closed front, opposite seam ownership and UV area balance. **Current exact overlap revision CI pending** and must be measured, not inferred from predecessor success. All code in research/test only; no production source or CMake changes.

**Gate still open:** native overlap revision full feature + PR jobs, independent patch containment and real Bézier patch UV/physical XYZ validation, failed-AFT rollback/lifetime and physical mixed publication. Continue R2b2 research only, then R2c owned mixed four-node `SubMesh`, later repeated adaptivity and real Eistute/Book models. No all-QUAD output, numerical 1993 approval or global high-valence welding is implied.

## 2026-11-11 — R2a qualified, R2b1 merged; next R2b2 exterior TRI completion

**R2a research front geometry:** [PR #212](https://github.com/tiagosombrra/apmesh-modernization/pull/212) merged at `eabc5201eadfe016c2b9698d43648c9ea7062109`; exact [postmerge CI #43131307374](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43131307374) **SUCCESS 4/4**, native QUAD GCC/MSVC **15/15 each**, root **85/85 CTest**, Python **527/527**, frozen TRI Eistute/Book parity. Source-matched original TRI AFT front vs new QUAD one-owner UV boundary tested for midpoint splitting, opposite winding, exact coverage and negative cases; **no actual AFT edge publication** in R2a.

**R2b1 active owned frontier:** [PR #213](https://github.com/tiagosombrra/apmesh-modernization/pull/213) merged into `quad-templates` at `8da5e523531b3579d9bacd69bbfe16ec96efe76d`, feature `eafaeb5bd15abea8effd5fc06994346eb657da0c`. Both [direct CI #43137020105](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137020105) and [PR CI #43137083615](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43137083615) **SUCCESS 4/4** with 16/16 QUAD native CTest Linux/Windows, 85/85 root CTest, 527/527 tooling Python and exact scientific TRI equivalence. Exact [merged-source CI #43138162247](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43138162247) **still in progress (3/4)** when this roadmap entry was committed; **do not mark postmerge qualified yet**.

R2b1 is **engineering-only, no production change**: research derived `OwnedQuadAftFront` stages actual native `Vertex`/`Edge` objects owned by the original AFT with reversed QUAD interface direction, one canonical pointer per UV seam vertex, real exterior `QuadtreeCell` observer, unchanged patch boundary, 13 positive/negative tests and preflight rejection/repair, on uniform/refined source Quadtree and synthetic nonuniform UV boundary. It deliberately **does not** execute `makeGeometryBasedMesh` / `makeTopologyBasedMesh` or publish a full mixed-element mesh. [R2b evidence](evidence/R2B_OWNED_AFT_FRONT_20261111.json) and [STATE](STATE.md) retain exact status.

**Next active R2b2 work:**

1. Certify PR #213's exact merged-source 4/4 gate first.
2. On an isolated feature branch, execute the **original exterior TRI AFT geometry/topology phases** using R2b1's real seeded, reversed interface. Do **not** call the normal TRI template publication again; keep existing production generator unchanged.
3. Capture native positive **nonzero TRI** output, original exterior region area and preserved QUAD interior area; check full patch UV coverage, zero overlay, no invalid/inverted TRI, no dangling QUAD seam segments and exact reversed TRI/QUAD boundary ownership with shared midpoint identity.
4. Preserve physical curve-adaptive edge sampling, AFT retry and owner lifetime; negative tests for failed AFT, fake cells, incomplete seam, repeated attempt and partial TRI publication. Keep QUAD seam vertices **locked from AFT smoothing**, or postpone smoothing until a separately validated mixed-element owner policy exists.
5. Only **R2c** may publish owned physical four-node `QuadrilateralAdaptive` with exterior TRI in one typed `SubMesh`; repeated adaptations, actual Eistute/Book full model and CLI `MESH_ELEMENT_KIND=quad_uv` admission are later gates.

No high-valence sheet welding, all-QUAD requirement or advisor-approved 1993 numerical point rule is presumed. The default TRI path and modernization `main` remain frozen.

## 2026-11-11 — R1 qualified research handoff; actual AFT integration is R2

The first user-aligned **R1 native template selection** has been implemented
and merged by [PR #211](https://github.com/tiagosombrra/apmesh-modernization/pull/211)
into `quad-templates` at exact merged source
`254d5f9aadf8cbac5e0f31780b69fb564291d2a5`.
[Feature CI #43104622677](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104622677),
[PR test-merge #43104631590](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43104631590)
and [exact merged-source CI #43106047878](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43106047878)
each passed **4/4 jobs**, with **14/14 QUAD native GCC and 14/14 MSVC
CTest**, **85/85 full root CTest**, **527/527 tooling Python**, and
frozen Eistute/Book TRI science parity. The architecture inventory
build-input SHA-256 was repaired without relaxing any gate.

**Qualified scope:** The same actual C++ Quadtree may be used to
choose either original TRI templates or research QUAD UV emission *for
the eligible interior*, preserving per-face source cell / T1–T6
provenance, explicit experimental point-rule selection, one-owner
directed QUAD region interface and 12 positive/adversarial test
controls. The per-attempt dispatcher fails closed against double
publication. This is **not** a live `AdvancingFront` QUAD integration,
not physical hybrid element output, not an enabled CLI mode, not
approved 1993 centroid policy and not global welded surface topology.

**Next active work item R2a:** implement a **read-only source-linked
front geometry comparison** of the QUAD boundary and
`Quadtree::GetFrontEdges()` under identical real adapted/refined
source trees, including exact split midpoint coverage, opposite AFT
winding, orientation and negative tests. Follow
[R2 design and ownership contract](R2_LIVE_AFT_QUAD_INTERFACE_DESIGN_20261111.md)
for the subsequent R2b/R2c owned AFT and typed physical mixed SubMesh.
Do not release `MESH_ELEMENT_KIND=quad_uv` before full-patch R2
acceptance. See [measured R1 evidence](evidence/R1_INTERIOR_TEMPLATE_DISPATCH_20261111.json).

## 2026-11-11 course correction — opt-in interior template replacement is P0

The clarified feature target is **replace the existing TRI Quadtree template
faces by QUAD template faces in each eligible patch interior only when
explicitly selected**, keeping the original discretized curves, boundary
samples/orientation, adapted tree and existing AFT TRI completion unchanged
unless a minimal strictly isolated integration seam requires adaptation.
This is initially **QUAD-dominant**, not all-QUAD. Preserve default
`MESH_ELEMENT_KIND=tri`, separate `USE_TEMPLATE` behavior, frozen
TRI tests and original accepted/rejected scientific states.

**[Detailed code audit and gap/priority register](OPTIN_QUAD_IMPLEMENTATION_AUDIT_20261111.md)**:
existing 1993-proposed QUAD graph tests and native UV/physical prototypes are
valuable, but the normal application still rejects `quad_uv` and publishes
only 3-node `Face`/`TriangleAdaptive`; the actual QUAD-vs-TRI template
switch and nonduplicating QUAD/AFT interface are unimplemented.

**Corrected critical path R0–R4** (original M0–M9 research history is
preserved; the R gates refine practical priority rather than erase it):

1. **R0**: baseline and explicit selection contract, TRI exact parity,
   `USE_TEMPLATE` orthogonality, named experimental centroid provenance.
2. **R1**: use the **same real Quadtree** to select the T1–T6 QUAD
   template emission in place of TRI interior, without double-publishing
   the same region; positive 2:1/edge/orientation/topology tests.
3. **R2**: opt-in **real physical QUAD** plus existing AFT exterior
   TRI on a complete curved patch; preserve existing curve sampling and
   patch boundary, use typed element publication and an explicit shared
   QUAD–TRI interface; no unsupported claim of application readiness
   before a successful live `ap_mesh --config` run.
4. **R3**: mixed-element history, error/quality/adaptation, ownership,
   repeated retries/rollback; demonstrate at least two live iterations.
5. **R4**: live complete Eistute/Book/Ribbed Bracket trials with preserved
   source curves, boundary conformity, physical quality and frozen TRI
   regression; report global node-sharing semantics honestly.

**Not on the initial critical path:** new high-valence **sheet pairing**
or global welding policy; those investigations in PR #210 remain diagnostic
evidence. The original article's exact centroid/topological interpretation
and Delaunay/contour-contraction remain scientific approval gates, not
permissions to silently change an algorithm. Hermite Pneu/Nariz, all-QUAD
and anisotropic models remain separate research work.

**Next implementation package:** an isolated candidate that proves actual
live interior QUAD substitution in the Quadtree while the TRI template
path is disabled *for the same leaves*, then integrates a typed QUAD/legacy
AFT transition. Do not enable `quad_uv` in the user-facing CLI merely
because a read-only observer emits a correct standalone OBJ. Native tests
or source-scoped CI are required on any subsequent code change.

## 1. Decisão arquitetural

Implementar QUAD como caminho científico **opt-in**, isolado da modernização atual (Stage 3). Preservar o algoritmo TRI, oráculos de Eistute/Book, contratos de memória e o comportamento de configuração `template_mode` (y/n). O mecanismo de seleção de espécie TRI/QUAD é **ortogonal** à seleção de aplicação de templates.

A infraestrutura existente permite reutilizar:

- `Quadtree::refineAccordingToNeighbors()`;
- `Quadtree::makeTemplateBasedMesh()` e criação/compartilhamento de arestas e vértices externos;
- classificação T1–T6 em `QuadtreeCell::makeTemplateBasedMesh()` baseada em quatro listas de vizinhos;
- infraestrutura de parametrização UV das superfícies e amostras canônicas de curvas compartilhadas.

**Não reutilizar como se fossem genéricos:** `Face` (3 vértices), `TriangleAdaptive` (3 nós), leitura de malha anterior no `Adapter` (casteada para TRI), adjacência da curvatura e métricas/OBJ do `GeneratorAdaptive`.

**Atenção:** o artigo de 1993 pode produzir malhas *quad-dominant* ao combinar triângulos do contorno; ele não garante *all-quad* para todos os domínios. A escolha de alvo deve ser deliberada, com os casos não satisfeitos explicitados.

## 2. Organização e fluxo Git

- Branch científica permanente: `quad-templates`.
- A modernização continua em `main`, **sem** implementação QUAD experimental.
- Para cada marco: `quad/m01-pattern-oracle`, `quad/m02-uv-topology`, etc.; abrir PR com **base `quad-templates`**, revisão de escopo, testes e evidência. Não abrir PR para `main` por padrão.
- Dois worktrees locais, com diretórios separados. Exemplo:

```bash
git fetch origin
git worktree add ../apmesh-quad quad-templates
git worktree list
```

- Antes de absorver uma correção da `main`, congelar evidências por SHA, medir o diff, reexecutar o gate TRI e os novos gates QUAD. Não usar merge/rebase automático indiscriminado.
- Manter registros de oráculos em `docs/research/quad/evidence` e testes em `tests/quad`, sem editar as evidências fechadas da linha de modernização.

## 3. Anatomia do código a alterar, em ordem

| Ordem | Módulo | Estado atual | Mudança deliberada |
|---|---|---|---|
| 1 | `quadtree_cell.cpp` | T1–T6 triangulares e seleção por vizinhança; células `inBoundary()` ignoradas | Expor classificação `LeafPattern` com orientações; **não** mudar os métodos TRI |
| 2 | Novo `research/quad` e `tests/quad` | Inexistentes | Tipos UV/IDs, padrões poligonais do artigo, conversão polígono→QUAD e validador |
| 3 | `quadtree.cpp` | Compartilha vértices/arestas externos; gera `Face` | Acesso controlado aos dados de folhas e emissão QUAD em malha UV própria |
| 4 | `advancing_front.cpp` | AFT preenche região restante com TRI; `fillMesh` e `improveMesh` triangulares | Estratégia explícita para *boundary gap*, quad-dominant/all-quad; integração não invasiva |
| 5 | `element_adaptive.h` e nova `quadrilateral_adaptive.h/.cpp` | Contrato base incompleto para 4 nós/UV | 4 nós, UVs, área/normal/qualidade, observadores e falhas transacionais |
| 6 | `adapter.cpp` | TRI→`Face` na leitura e `Face`→TRI na saída | Caminho QUAD fisicamente tipado, preservando modo TRI; modos mistos suportados quando habilitados |
| 7 | `curvature/adjacent.cpp` + `curvature_discrete.cpp` | Acesso triangular e adjacência angular | Estratégia validada para valência e ângulos de QUAD; comparar oráculo analítico/discreto |
| 8 | `generator_adaptive.cpp` | Qualidade, erro, exportação, estatísticas e repetição triangulares | Oráculos e relatórios específicos TRI/QUAD; rollback e reentrada para múltiplas iterações |
| 9 | `cmake/Quality.cmake` | Registro dos gates de regressão existentes | Adicionar gates QUAD com rótulo `research-quad`, separados dos gates históricos |

Não editar arquivos de `main` a partir do worktree QUAD. Um novo `src/*.cpp` entra automaticamente no `ap_mesh_engine` por `GLOB_RECURSE`; manter o protótipo inicial em `research/quad` para não modificar a compilação da aplicação até a decisão M3.

## 4. Marcos com entregáveis e critérios objetivos

| Marco | Nome | Entregável verificável | Critério de saída |
|---|---|---|---|
| **M0** | Baseline e oráculos | Relatório completo de compilação GCC/MSVC, 75 CTest e 526 controles Python como referência a verificar, Eistute/Book, hashes e corpus | **Não avançar** sem baseline local reproduzido e documentação das exceções |
| **M1** | Reconstrução histórica T1–T6 | Inventário da Figura 7, polígonos padrões, rotações/reflexões e exemplos unitários | Os seis casos e orientações previstas conferem com o artigo; sem topologia inventada |
| **M2** | Topologia QUAD UV | `UvVertex`, `UvQuad`, registro de arestas/pontos médios e validador independente | Cobertura, área positiva, orientação, contagem de incidências, ausência de T-junctions; fuzz/negativos |
| **M3** | Emissor de templates de quadtree | Seletor TRI/QUAD opt-in, emissor QUAD para folhas internas e validação T1–T6 | Resultados TRI *byte-equal* no modo padrão; QUAD interior conforme em casos 2:1 |
| **M4** | QUAD físico | `QuadrilateralAdaptive`, UV→XYZ, normal/área válidas, exportação QUAD em prova isolada | Teste plano e curvo; 4 nós/UV; falhas de alocação e destruição sem observadores pendentes |
| **M5** | Tratamento de contorno | Política escolhida: combinar TRI na borda (*quad-dominant*) ou preencher com QUAD (*all-quad*) | Malha de patch completo, sem vazios, sobreposição, inversão nem divergência de IDs |
| **M6** | Conformidade multipatch | Compartilhamento canônico de curvas, sincronização e orientação invertida | 2 patches e 3 incidentes, 1:1 de pontos físicos e arestas, sem subdivisão local divergente |
| **M7** | Adaptação reiterada | Entrada QUAD como histórico, métrica de tamanho e erro, retry/rollback, relatórios | Pelo menos 2 iterações sucessivas; rejeição não publica malha; gates TRI protegidos |
| **M8** | Modelos e ablação | Conjunto de modelos controlados e CAD; TRI/quad-dominant/all-quad; custo/qualidade/erro | Protocolo reproduzível com seeds, hashes, gráficos e limites declarados |
| **M9** | Anisotropia (opcional para primeiro paper) | Campo métrico e propostas de templates orientados; testes de alinhamento e razão de aspecto | Efeito anisotrópico demonstrado no espaço físico; resultados comparados isotrópico/anisotrópico |

**Marcos M0–M3** são o primeiro lote viável de implementação com risco controlado. **M4–M7** dependem de engenharia de ciclo de vida e de uma decisão topológica explícita para a região de fronteira. **M8–M9** são investigação científica, não compromisso de performance antes de medir.

## 5. Portas técnicas de aprovação

### G0 — Baseline intacto

1. Build serial Linux GCC C++17 e Windows MSVC C++17; registrar compilers/options.
2. CTest completo e os controles Python realmente executados no commit da linha QUAD; guardar stdout/stderr, SHA, tempo, ambiente e fixture. Os números 75/526 são **evidência documental prévia**, não resultados desta criação de branch.
3. Eistute e Book: comparar saídas científicas aceitas pela linha de modernização, incluindo IDs, contagem, qualidade e limites — não trocar tolerâncias para passar.
4. ASan/LSan e CRT/checked-MSVC nos casos relevantes; não inferir segurança MPI/OpenMP.

### G1 — Template historical oracle

- Para T1–T6, publicar lista ordenada de vértices UV, polígonos, orientação, incidências esperadas e topologia final.
- A equivalência triangulada observada no código é **de classe de vizinhança**; diferentes diagonais, centro otimizado e contagem atual não são evidência de identidade literal com a publicação de 1993.
- A subdivisão centro/pontos médios só é aceita se cada polígono tiver centro válido, sem elemento côncavo/invertido; o registro de midpoint deve identificar a mesma **aresta canônica** em células adjacentes.

### G2 — Integridade UV

- Verificações sobre orientação CCW, área, degenerescência, interseção, incidência 1/2 em bordas/interior e não existência de *hanging nodes*.
- Metamórficos: rotações 90/180/270°, reflexão quando aplicável, escalonamento uniforme, permutação de IDs sem mudar topologia.
- Fuzz com níveis quadtree e padrões de vizinhança permitidos; entradas adversariais e falha explícita, sem sucesso vazio.

### G3 — Integridade física e de memória

- Elementos físicos em `SubMesh` devem possuir `unique_ptr<ElementAdaptive>`, nós proprietários e observadores cuja vida é estritamente menor que a dos nós.
- Testar 4 nós iguais/degenerados, reordenação, rejeição no construtor, falhas de adoção/clonagem, destruição e realocação.
- Normal/área em superfícies parametrizadas potencialmente não planares deve ter definição explícita e independente de eventual triangulação auxiliar.
- Normal/erro geométrico devem referir-se ao domínio físico, não somente à qualidade UV.

### G4 — Fronteiras e adaptação

- AFT atual é triangular. Não declarar “all-quad” quando a transição preserva TRI.
- Em curva física compartilhada, uma inserção canônica deve chegar a todas as superfícies incidentes, com orientação e IDs consistentes.
- Para atualização adaptativa, QUAD precisa de regra própria para tamanho local/curvatura e histórico; dupla iteração é obrigatória.
- Falhas ou reprovações devem preservar o estado anteriormente aceito.

## 6. Testes prioritários e fixtures

| Fixture | Problema isolado | Requisito |
|---|---|---|
| `quad_t1_uniform` | célula sem vizinhos subdivididos | quatro elementos QUAD esperados se padrão central do artigo for escolhido |
| `quad_t2_one_side` | uma lateral dividida | continuidade da lateral com a célula adjacente |
| `quad_t3_opposites` | duas laterais opostas | ausência de malha não conforme |
| `quad_t4_adjacent` | duas laterais adjacentes | orientação após rotação |
| `quad_t5_three_sides` | três laterais | midpoint com único ID |
| `quad_t6_four_sides` | quatro laterais | incidência correta para os oito segmentos |
| `quad_uv_grid_2to1` | folhas de níveis diferentes | cobertura + ausência de T-junctions |
| `quad_parametric_plane` | mapeamento UV→XYZ | área/normal/qualidade correspondentes ao plano |
| `quad_parametric_curved` | superfície curvada | comparação com referência geométrica independente |
| `quad_two_patches_reverse` | curva compartilhada invertida | mesma segmentação física |
| `quad_three_patches_incident` | junção não manifold | incidência em todos os patches, sem divergência |
| `quad_reuse_reject_retry` | segunda adaptação e falha | último resultado aceito intacto |

## 7. Experimentos para o paper

- **E0:** TRI atual — baseline original.
- **E1:** QUAD no interior por templates + transição mista quando necessária.
- **E2:** malha *all-quad*, somente se implementada e qualificada.
- **E3:** QUAD anisotrópico, somente após validação do tensor de métrica e do refinamento orientado.
- Variáveis controladas: modelos, número de patches, curvas compartilhadas, tolerâncias de erro, orçamento, threads, semente, plataforma e compilador.
- Medidas: falhas, conformidade, valência/singularidades, ângulos, *scaled Jacobian*, forma física, área, razão de aspecto, erro de aproximação de posição/normais, tempo, memória e elementos. Comparações TRI/QUAD exigem equivalência de erro, não igualdade ingênua de contagens.
- Modelos iniciais: patch plano; superfície cilíndrica/selada; dois patches com inversão de orientação; três patches não manifold; Eistute/Book **somente se a entrada/representação e os oráculos forem compatíveis**.
- Publicação: distinguir **reprodução de templates 1993**, **adaptação de engenharia para superfícies** e **eventual novidade de sincronização multipatch/anisotropia**; revisar estado da arte para testar novidade.

## 8. Critérios de parada

Bloquear avanço do marco em caso de: regressão não explicada do modo TRI; topologia com fendas/interseções/IDs divergentes; atribuição de ownership ambígua; falta de oráculo independente; falha de rollback; entrada multithread não qualificada; ou declaração de qualidade/anistropia não sustentada pelas medidas.

Nunca flexibilizar critérios científicos ou prolongar limites de tempo silenciosamente para concluir um marco.

## 9. Perguntas que precisam de decisão na reunião de 11/11

1. O primeiro paper deve perseguir **quad-dominant** ou **all-quad**? Quais triângulos residuais são aceitáveis?
2. Os seis templates QUAD de 1993 devem ser reproduzidos literalmente primeiro ou podemos reformular a subdivisão de polígonos quando houver centros com qualidade inferior?
3. Qual restrição é prioritária: conformidade em curvas 2-patch, casos não manifold (>2), ou erro geométrico?
4. O algoritmo de borda de 1993 (Delaunay + merge) é suficiente para a primeira validação, ou devemos buscar um preenchimento QUAD nativo?
5. É aceitável adiar anisotropia para o segundo estágio do artigo, mantendo modelos novos e métricas amplas já na primeira submissão?
6. Quais modelos/CAD e métricas os professores consideram indispensáveis como comparação externa?

## 10. Primeira execução prática (somente após G0)

- Criar `tests/quad/` e `research/quad/` no ramo de trabalho M1, sem alterar `src`.
- Implementar primeiro uma representação de padrões que não depende de `Face` ou `TriangleAdaptive`.
- Criar oráculos das seis classes de vizinhança, suas rotações e reflexões, com saídas visualizáveis SVG/OBJ 2D.
- Testar conectividade, midpoint e cobertura antes de tentar integrar `QuadtreeCell`.
- Revisar o PR contra a branch `quad-templates`, entregar evidência e somente então iniciar M2/M3.

**Registro de honestidade:** este documento é um plano com auditoria de código e evidências históricas. Não afirma execução dos 75 CTest /526 Python, compilação nativa nem implementação QUAD, que continuam pendentes.

## 2026-11-08-05 measured milestone transition

M0-G6 applicable memory and G7 frozen serial contract inventories are complete
in their declared scopes. Reuse source-bound Node22; reject stale UV/Linux
dependencies and refresh current UV21 plus the unchanged separate UBSan/LSan
32-production/five-terminal matrix per profile. Preserve actual negatives,
accepted/rejected traces, scientific comparisons and all earlier failures.
The [memory receipt](evidence/M0_MEMORY_APPLICABILITY_20261108.json),
[serial register](M0_SERIAL_TRI_CONSUMERS.md) and dated [closure audit](M0_EVIDENCE.md)
record exact limits. The current regression count is 75 CTest /527 Python,
retaining all original 526 plus one engineering regression. Before publishing
this checkpoint, require the complete regression on its committed revision;
missing/failing evidence blocks admission. Main and Stage 3 remain unchanged.

The next work item is M1 primary-source reconstruction: independently verify
the ordered T1-T6 polygon vertices, orientations, incidences and symmetries from
Figure 7. No connectivity may be invented from the existing triangular emitter.
This admission does not approve a new geometry/curvature formula or settle
quad-dominant versus all-quad. Unresolved topology/scientific choices require
adviser alignment before executable fixtures/emission. No QUAD code exists yet.

**Measured checkpoint gate:** `5b928375d3033a0ab67150987123b8956562a362` passes
75 CTest /527 Python with zero failures/skips; [closure receipt](evidence/M0_CLOSURE_20261108.json).
M0 is qualified in its declared serial scope. Final documentation publication
retains the exact-head full-regression and remote-readback guard. M1 source
reconstruction is next; no QUAD algorithm/scientific choice is approved here.

## 2026-11-08-06 M1 primary-source progress

M1 is **PARTIAL / REVIEW PENDING**, not closed. The original seven-page scan is
identified by hash; Figure 7 is visually transcribed in the
[historical review](M1_HISTORICAL_ORACLE_REVIEW.md), ordered JSON and SVG.
Printed order is T1,T2,T4,T3,T5,T6 under current code labels; T5 has no center
junction. Conditional later-subdivision counts are 4,11,12,8,11,16. Schematic
documentary checks pass 48 D4 observations/16 split signatures and detect six
altered records. These do not establish an approved executable scientific oracle.
The paper does not provide a numeric coordinate or centroid-formula table,
and its boundary procedure may retain triangles. Review the explicit graph,
normalized embedding and centroid interpretation with advisers before M1
executable fixtures; M2 and the boundary target remain unadmitted. Production,
TRI references, main and modernization obligations remain unchanged.

## 2026-11-08-07 implementation steering and UV prototype

The user prioritizes executable QUAD work and reports existing adviser alignment;
specific numerical decisions will follow. Candidate `quad/m01-uv-prototype`
implements an isolated value-owned UV mesh, canonical edge-midpoint registry,
polygon-to-four-node-QUAD subdivision, disk topology/area validator and OBJ demo.
Supplied interior points keep the unspecified centroid policy outside the API.
The six graph fixtures execute with injected positive points, not historical
numerical centroid claims. This supersedes the earlier blanket waiting step for
engineering implementation; it does not adopt an unsupplied scientific formula.

Native evidence: 117 outcomes per Linux GCC13.3, Windows GCC16.1 and checked
MSVC19.44 Debug; actual 19-quad 2:1 seam, 32 bounded grids and malformed controls.
The eight-quad demo has identical OBJ bytes on all three platforms. M1/M2 remain
partial pending review/numerical-oracle and further qualification; full baseline
75/527 and exact-head/remote gates still apply. After review and binding the
reported scientific decisions, connect actual internal quadtree leaves to the
UV emitter through the planned opt-in path. No physical/boundary/multipatch/
adaptation integration or default TRI change is included.

## 2026-11-08-08 actual quadtree leaf connection

The primary implementation checkout is now `quad/uv-leaf-bridge` so the source
is visible in the current workspace; historical main is preserved. The new
read-only bridge maps actual leaves/neighbors into T1-T6 polygon graphs and
the existing UV QUAD emitter, preserving boundary exclusion and source identity/
order. Caller-selected points keep the scientific rule explicit. All 16 masks,
147 native core/bridge outcomes per three compiler profiles and a 42-quad,
19-leaf adaptive demo are measured; default TRI source and policies are unchanged.

M3 now has a working leaf bridge but remains partial: no application opt-in
entry, physical QUAD/XYZ, full boundary, shared-curve or adaptation integration.
M1/M2 numeric/coverage exits remain. Bind the reported adviser decisions and
qualify application selection separately; do not infer full patch meshing from
the interior disk demo. Exact-head baseline and remote review/checkpoint gates
remain mandatory; see the [bridge receipt](evidence/QUAD_LEAF_BRIDGE_20261108.json).
## 2026-11-10 — Seleção científica de modos e validação visual

O objetivo do doutorado, conforme decisão do pesquisador, é **reproduzir primeiro o método híbrido de 1993** (templates QUAD em células interiores e processamento externo Delaunay/contração de contorno) e **desenvolver depois uma extensão totalmente QUAD**, selecionável de forma explícita. Isso não altera o TRI atual como comportamento padrão; os dois modos ainda precisam ser implementados e validados na aplicação real. Não se deve tratar a etapa totalmente QUAD como se estivesse descrita integralmente no trabalho original.

O M1 tem agora [uma galeria visual persistente](figures/M1_UV_6_PATTERNS_20261110.svg), um [exportador C++ reprodutível](../../tests/quad/visual_export.cpp) e um [plano de validação visual](MODE_CHOICES_AND_VISUAL_REVIEW_20261110.md). **São malhas UV de pesquisa**, não resultados físicos do pipeline completo. A entrega do modo híbrido exige, além dos templates, classificação de células do quadtree real, fronteira TRI gerada e sincronização/mapeamento físico, acompanhados de evidências visuais e científicas. A extensão totalmente QUAD só seguirá depois da validação híbrida, com interface de escolha e testes separados.
## 2026-11-10 — M5 interface research experiment on real C++ Quadtree

[PR #200](https://github.com/tiagosombrra/apmesh-modernization/pull/200) extends real Quadtree candidate visualization (PR #199) with a separate *experimental, nonhistorical* exterior triangulation gate. The actual C++ interior has **42 QUAD** covering 0.25 UV area; the new center-fan **60 TRI** cover remaining 0.75. The combined 81-vertex graph has 20 conforming QUAD/TRI interface edges in a single closed loop and 16 outer edges; four negative geometry mutations reject. [Premerge exact-head CI #42898041678](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42898041678) completed four successful jobs: native GCC/MSVC 11 CTests each, TRI 78 CTest, 527 Python, seven CLI denials and Eistute/Book strict reference parity.

**This is not historical Delaunay nor boundary contraction** and does not close M5 or enable any production mode; it is a reproducible interface/provenance and visual-quality subgate. The next approved research increment must locate/implement faithful outer-region Delaunay and contour contraction under separately recorded historical/adviser criteria, preserve these seam and area invariants, and only then consider mapped physical output. Historical-hybrid first, selectable all-QUAD later remains the user's direction. See [M5 experiment](M5_EXPERIMENTAL_EXTERIOR_INTERFACE_20261110.md).
## 2026-11-10 — M5 research candidate for local constrained Delaunay (PR #201)

[PR #201](https://github.com/tiagosombrra/apmesh-modernization/pull/201) adds a reproducible, **research-only** exterior optimization on the actual 19-leaf C++ Quadtree source, carrying forward 42 native QUAD and the already proven QUAD/TRI 20-edge interface. The new optional research test constructs 36 exterior TRI by ear clipping and applies eight exact-rational Lawson flips. The full UV mixed disk has 69 vertices, area 1.0, positive orientation, and five mutation rejections. The exact candidate passed native GCC/MSVC **12/12 CTest**, full 78/527/7 TRI/tooling/CLI and Eistute/Book scientific parity. This **does not reproduce the 1993 point insertion or contour contraction**, nor certify physical 3D boundaries, historical centroid choice, multipatch and production mode.

**Next:** research the 1993/1987 source methods and approve geometric/methodological rules with Bento and Creto. After approved historical hybrid physical output and visual inspection, implement a distinct selectable all-QUAD extension and repeat all scientific gates. No alteration of `main` or the existing TRI default.
## 2026-11-10 — M6 synthetic analytic UV-to-XYZ bridge, research only (PR #202)

The user-approved delivery order stays **historical hybrid 1993 first**, then a separately selectable **all-QUAD extension**. Research-only PR [#202](https://github.com/tiagosombrra/apmesh-modernization/pull/202) validates an analytical surface lift of the same real C++ 42 QUAD + M5 research 36 TRI with 69 vertices and 20-edge seam, not a real APMesh curved model. Two unapproved centroid rules and three synthetic graph curvatures were tested, including positive tangent normals, orientation, faceting diagnostics and eight malformed controls. All exact-head GCC/MSVC 13/13 native CTest, root TRI 78/527/7 and Eistute/Book frozen scientific parity passed at [Actions #42941827778](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42941827778). Merge `b48526ab22f7190679cd37c61a12005687666c5f` preserved modernization main.

**Next:** inspect and call existing `PatchBezier::Parameterize` / `Qu` / `Qv` on independently audited real model fixtures in a bounded research-only prototype, without creating physical mesh ownership prematurely; then apply the separately approved historical Delaunay and boundary-contraction rules. [Detailed M6 limitations](M6_SYNTHETIC_ANALYTIC_XYZ_20261110.md).

## 2026-11-11 — M4 bounded native physical ownership subgate (PR #205)

After the already-qualified [built-in physical model mapping PR #204](https://github.com/tiagosombrra/apmesh-modernization/pull/204), [PR #205](https://github.com/tiagosombrra/apmesh-modernization/pull/205) adds a **research-only** `apmesh::quad::research::QuadrilateralAdaptive : ElementAdaptive`, holding four borrowed nodes with failure-atomic NodeAdaptive observer registrations. A real SubMesh owns 69 nodes and 78 physical mixed elements (42 research QUAD, 36 existing TriangleAdaptive) on the actual native C++ Quadtree and M5 Lawson research mesh. Both unapproved centroid witnesses are checked, together with 276 reverse links, four injected construction rollbacks, invalid-node/UV/geometric cases, ownership-preserving SubMesh moves, source ID and 20-seam/16-boundary conformity, and six altered-OBJ negative cases. The exact PR feature head `1366ce697a5d04156ba58bb890c989f711d39f93` passed all [Actions #42999207821](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42999207821) gates: root 81 CTest, 527 Python tooling, seven CLI negatives, GCC/MSVC standalone QUAD and frozen Eistute/Book TRI equivalence. Merge to research branch only: `4ffd9cdac09d99352e0500df8a0b5467054949c3`. Postmerge [Actions #43000273810](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43000273810) must be confirmed separately.

**M4 still PARTIAL.** This proves bounded four-node physical **observer/owner lifecycle in a research fixture**, not production element publication, exact curved finite-element Jacobian integration, imported CAD boundary fidelity, multipatch shared-curve synchronization, retry/rollback across failed adaptive steps or historical 1993 centroid/Delaunay/contour contraction. Neither full QUAD nor all-QUAD is available in production. The next engineering experiment should isolate real model boundary sharing and mixed physical mesh failure rollback, while the scientific method choice remains independently pending. See [M4 ownership contract](M4_FOUR_NODE_PHYSICAL_OWNERSHIP_20261111.md) and [evidence](evidence/M4_FOUR_NODE_PHYSICAL_OWNERSHIP_20261111.json).

## 2026-11-11 — Model catalog and high-valence curve constraints (PR #206)

The user requested QUAD/TRI feasibility across Eistute, Book, Pneu, Bolha and all available models. [PR #206](https://github.com/tiagosombrra/apmesh-modernization/pull/206) adds a source-only, independently sampled [model audit](M4_MODEL_CATALOG_AND_BOUNDARY_RISKS_20261111.md) and [persistent bounded evidence](evidence/M4_MODEL_CATALOG_BOUNDARY_RISKS_20261111.json). Exact feature `b2d8f02fc4966a6cdab3c2e02a453cf1d0961718` passed all four [Actions #43009461867](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43009461867) jobs including 81 root CTest, 527 Python tooling, seven CLI negatives, seven malformed .bp controls, native Linux/Windows research QUAD and strict scientific Eistute/Book TRI parity. Integrated into `quad-templates` at `eb28df95c150e6ed4825271d86c67b9c7f498732` and left `main` untouched.

**New blockers:** Eistute 4-way and Book 28-way control-curve incidence, Ribbed Bracket four 3-way curves, per-sheet nonmanifold welding, strong Eistute normal rotation (sampled only), unimplemented `PatchHermite` physical QUAD adapter for Pneu/Nariz, missing tracked `Bolha` identity. **No full-model hybrid has yet been produced.** After the existing physical M4 witness, the next research gate is actual external `.bp` model loading and per-patch candidate export against a **pairwise Bezier control fixture**, followed by intentional multi-sheet seam reconciliation for Eistute/Book, and then a distinct Hermite evaluation. No historic Delaunay/contraction, production QUAD or all-QUAD claim is approved.

## 2026-11-11 — M4 real external physical diagnosis closed; global meshing remains open (PR #209)

Research-only [PR #209](https://github.com/tiagosombrra/apmesh-modernization/pull/209) merged at `ff97e9c15d2b652433ecb494a90822fce88bea1b`. Exact-source [Actions #43046674566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43046674566) passed four jobs, 84 root CTest, 527 Python, native Linux/Windows QUAD and frozen scientific TRI parity. All 45 tracked external Bezier patches were evaluated using the real PatchReader and sampled independently, yielding 90 patch-local physical QUAD/TRI OBJ witnesses for two unapproved point rules. The evidence is retained in [JSON](evidence/M4_EXTERNAL_BEZIER_PHYSICAL_20261111.json) and the [scientific scope report](M4_EXTERNAL_BEZIER_PHYSICAL_DIAGNOSTICS_20261111.md). These are not joined full-model conforming meshes. Eistute has a 4-owner curve, Book a 28-owner curve, and Ribbed Bracket four 3-owner curves; Eistute also presents strongly rotating differential normals. Default TRI main remains unchanged.

**2026-11-11 M4 sheet-incidence engineering subgate QUALIFIED (not global meshing):** [PR #210](https://github.com/tiagosombrra/apmesh-modernization/pull/210) adds a **read-only source-linked patch–curve incidence hypergraph** consuming the earlier production `PatchReader`/`PatchBezier` physical samples. It records all 45 real Eistute/Book/Ribbed Bracket patch sheets, oriented canonical five-site physical boundaries, tangent/sector compatibility and exact curve valence. All **396 possible high-valence pair comparisons are quarantined**, while the 17 ordinary two-owner Ribbed Bracket curves are only diagnostic geometry candidates, not approved welding edges. Cross-center graph classifications and 27 controlled admission checks passed. Exact feature and [postmerge source CI #43057855090](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090) passed **85/85 CTest, 527/527 Python**, Linux/Windows native QUAD, CLI invalid-mode and strict frozen TRI Eistute/Book parity. See [persistent numeric evidence](evidence/M4_SHEET_INCIDENCE_GRAPH_20261111.json), [graph scope](M4_SHEET_INCIDENCE_GRAPH_20261111.md) and [advisor decision matrix](M4_SHEET_POLICY_DECISION_MATRIX_20261111.md).

**Next M4 scientific gate:** obtain source-model/advisor-reviewed sheet classification for Eistute's 4-way curve, Book's 28-way spine and Ribbed Bracket's four 3-way junctions. No point/tangent sampling can unambiguously decide the underlying sheet topology. Require **explicit, source-SHA-bound, non-overlapping curve pairing decisions and orientation contracts**, then build/test separate canonical node ownership, synchronized boundary subdivision and rollback. Until then, node IDs remain patch-local and **no model-wide conforming QUAD/TRI is claimed**. Follow with a separately typed `PatchHermite` physical adapter for Pneu/Nariz. The original 1993 Delaunay insertion/contour contraction, centroid approval and production/all-QUAD remain open; Bolha remains unidentified.
