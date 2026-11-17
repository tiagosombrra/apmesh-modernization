# Execution plan: external benchmark corpus and reverse-patch feasibility

## 2026-11-17 S3.X — Original S40 post-repair native gap and margin audit

[Original S40 S3.X report](S3X_S40_POST_REPAIR_NATIVE_GAP_AND_MARGIN.md) validates the byte-pinned repaired 148-patch research atlas without adding new faces: **21/43 original STEP faces represented, 22 pending** (13 planar, 6 cylindrical, 3 B-spline), with 16 pending faces one original edge away and six two edges away. Source-native graph 43 faces / 117 edges / 77 vertices; no 3+-incident original edge (S40 remains a manifold control). Stress checking the two repaired shared degree-five spline source edges uses **1,935** original native planar and **1,935** cylinder boundary samples, plus **3,375** samples on the 15 changed older cylinder patches; none classified OUT. Float-guarded bivariate Bernstein radial bound is **0.000980524 mm**, leaving only **0.000019476 mm** under the unchanged 0.001-mm experimental budget; **not** formally interval-certified or a continuous trimmed-face equivalence proof. Next S3.Y prioritizes original planar six-edge faces `#1827/#1907/#3044` (four circular source edges and six source-edge connections each), requiring canonical indexed curve-segment reconciliation and independent native coverage before patch admission. Directed tests: **159/159 PASS** in four completed selections (70 S3.S–U; 30 S3.V; 36 S3.W; 23 S3.X). One combined run timed out; do not claim a single full-suite pass. No APMesh C++ TRI/QUAD execution, genuine original non-manifold positive, or `main` merge. Keep PR #225 draft.

## 2026-11-17 S3.V original S40 planar B-spline native-trim blocker

## 2026-11-17 S3.W — Original S40 #85/#2096 shared spline repair pilot

[Bounded source-native S3.W report](S3W_S40_SHARED_SPLINE_SEAM_REPAIR.md) resolves the previous S3.V strict-trim sample failure by **coordinately adjusting the thirty existing globally indexed interior cubic controls** on two original B-spline source edges. This intentionally re-audits fifteen previously admitted cylinder patches (the other 117 old patch nets including the genuine #218 hole remain unchanged), rather than falsely presenting the 132-patch parent as geometrically intact. The new separate 148-patch research child represents 21/43 original STEP faces with 239 exact two-sided indexed seams and 114 open sides; all sampled new planar and old cylinder native UV gates pass. The fixed 0.001-mm budget remains unchanged; modified cylinders have a guarded **bivariate degree-(6,6) Bernstein** support estimate at most 0.000980524 mm, **not** a formal directed-rounding proof or continuous trimmed-face equivalence. [Non-geometric receipt](evidence/s3w/original_s40_nongeometric_receipt.json) records 136/136 directed tests across 70 S3.S–S3.U, 30 S3.V, 36 S3.W isolated runs; a one-shot combined run exceeded its limit. The byte-pinned original third-party STEP and derived BP/viewer geometry stay private pending rights review. Next S3.X: remaining 22 original faces and independent numerical/source-boundary certification; APMesh C++ TRI/QUAD, real 3+-incident non-manifold positive and full original shell remain open. PR #225 stays draft; never merge to main on this evidence.

The [S3.V strict native-trim source report](S3V_S40_PLANAR_SPLINE_TRIM_BLOCKER.md) provides a **148-patch CANDIDATE, NOT ADMITTED**, from original S40 STEP source face #17 and #2092, reusing all frozen prior S3.T boundary integer controls. The source-native 18-edge indexed loops each admit eight convex planar Coons patches, 1,619 candidate controls and 239 exactly two-sided indexed seams. Original native trimmed-face classification: **1,296/1,296 interior IN; 135/704 boundary OUT**; all boundary failures occur on original degree-five 3D B-spline edges #85 (63) and #2096 (72), none on new internal diagonals. The maximum sampled original-native boundary curve distance is 0.00089266861645 mm below the unchanged experimental 0.001-mm budget, but proximity is NOT a substitute for strict native trim membership. Candidate BP remains private; **approved S40 remains 132 patches, 19/43 source faces**. Directed tests on original frozen S40: S3.V 30 PASS; independent S3.S–S3.T 45 PASS and S3.U–S3.V 55 PASS; single combined run exceeded timeout and is not claimed. Next S3.W: coordinate original B-spline #85/#2096 boundary remediation across both incident source patches, preserve exact source-indexed controls and revalidate BOTH native trimmed faces and the historical hole #218. No original STEP, derivative BP coordinates or production C++ code is committed; PR #225 remains draft, no merge.


## 2026-11-17 S3.U — Post-octagon original S40 source-native gap census

[S3.U source/native gap census](S3U_S40_POST_OCTAGON_GAP_CENSUS.md) recomputes the frozen original S40 after S3.T without producing new patches. **132 indexed research patches / 1,527 declared controls represent 19/43 original faces; 24 remain** (15 planes, 6 cylinders, 3 spline surfaces). The full source-native bijection remains 43 faces / 117 edges / 77 vertices. **18 pending faces now share original STEP edges directly with the atlas**, versus 15 before S3.T. Original planar faces #17/#2092 have four already represented neighbors each but require native degree-5 B-spline boundary approximation and exact indexed seam admission; #1279/#1386 are analytic-circle alternatives. Line-only five-edge faces #3269/#3485 require boundary refinement before conforming all-quad partition. Source S40 has no original 3+-incident edge, so is only a manifold control. S3.S–S3.U: 70/70 PASS, separately S3.M–S3.R: 128/128 PASS. The one-shot combined attempt timed out; neither the full C++ suite nor original APMesh TRI/QUAD meshing was run. **Research PR #225 remains draft; no original STEP or derived BP coordinates are publicly committed.**

## 2026-11-17 S3.T — Original S40 two planar source octagons

[Original S3.T native planar admission](S3T_S40_TWO_PLANAR_OCTAGONS.md) adds source `ADVANCED_FACE #912/#3737` as six convex source-vertex quad Bézier patches; **132 indexed research patches, 1,527 declared controls, 19/43 original source faces**. Six original source EDGE_CURVE joins share exact existing global control IDs; four new source-vertex diagonals also share exact IDs. The original S3.R holed region is unchanged. The source/native BRep face/edge/vertex correspondence is independently recovered and trimmed native UV, orientation, and 16 source boundary curves are sampled within a **strict 1e-7 mm planar gate**, tighter than the unchanged experimental 0.001 mm budget. **173/173 directed S3.M–S3.T Python research tests PASS** with byte-pinned original S40 and optional S3.Q baseline; production TRI/QUAD meshing and C++ regressions are NOT RUN. Derived original controls remain private pending rights review; the original STEP is not committed. PR #225 remains draft, no main merge. Next: re-run source gap census (24 original faces excluded) and triage additional planar source regions.


## 2026-11-17 S3.S — complete source/native original S40 gap census

[Source/native original S40 full face and edge audit](S3S_S40_FULL_ORIGINAL_FACE_GAP_CENSUS.md) maps all **43 original source faces, 117 original EDGE_CURVE entities and 77 original VERTEX_POINT entities** uniquely to native Open CASCADE topology using frozen source identity plus edge/face incidence (including distinct same-endpoint circles #378/#1991). The frozen **S3.R atlas remains 126 patches covering 17 original faces**. The **26 excluded faces** comprise 17 planar, six cylindrical and three B-spline-support faces; 15 are directly adjacent to represented source faces and 11 are two original-edge hops away. Original S40 remains a **manifold-only control**, with no 3+-face original edge. Next bounded S3.T: attempt source-conforming planar polygon partition on original faces **#912 and #3737**, both eight-LINE single-wire faces with three original represented-edge neighbors. **17/17 new S3.S PASS; 54/54 S3.R+S3.S PASS; cumulative S3.M–S3.S 143 PASS + 2 optional SKIP, no failures.** An optional-gate rerun timed out; do not call it 145 PASS. No new BP, accepted TRI/QUAD, original nonmanifold positive, C++ production regression or full atlas claim; keep PR #225 draft and original-derived geometry private.


**Classification:** scientific research proposal, NOT a technique-preserving refactor.
**Frozen planning base:** main f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94 on 2026-11-14.
**Working boundary:** documentation and isolated experimental research probes/fixtures ONLY; no production build, Stage 3 modernization or QUAD branch modifications.

## 2026-11-16 S3.R conforming original S40 holed-face integration

[Original S3.R source/native de Casteljau join](S3R_S40_CONFORMING_ORIGINAL_HOLE_JOIN.md) closes the S3.Q indexed interface T-junction blocker without spatial welding: four original generator EDGE_CURVEs #222/#281/#303/#355 induce split propagation across **19 prior parent patches** (77 → 96) and accept the previous 30 holed-face patches into a **126-patch, 1,467-declared-control (1,349 active; 118 retained historical), 179 two-sided-seam** private partial BP, covering **17/43** original S40 STEP faces. The source-indexed historical BP and a separate compact BP with 1,349 active control declarations are equivalent via an explicit deterministic old→new map. The new native audit verifies 12 original boundary edges, 49 hole OUT samples, 34 prior-cylinder child patches, the original sampled boundary and unchanged 0.001-mm pilot radial envelope. **128/128 directed S3.M–S3.R Python tests PASS**; full production C++ and full older Python regression NOT RUN. **Next bounded S3.S:** classify the 26 still-unrepresented original S40 faces by analytic/spline/trim topology, choose and audit one tractable source-indexed candidate, and continue the distinct search for an actual external three-plus-incident source. No complete CAD shell, original non-manifold positive or APMesh TRI/QUAD mesh. PR #225 stays draft pending scientific review; do not merge to main.

## 2026-11-16 S3.Q original hole-preserving isolated BP and S3.R conformity blocker

The [S3.Q original #218 native hole study](S3Q_S40_INNER_WIRE_PRESERVING_ISLAND.md) retains the source 8-edge outer wire and **four-edge inner hole wire** of S40 native face #1. Its **30 candidate patches** (336 isolated controls and 38 indexed seams) pass source/native boundary curves, analytic cylinder-support numerics, and native trimmed UV and hole exclusion at the original 0.001-mm experimental budget. This is an **ISOLATED candidate, not an integrated BP extension**: source-original generator EDGE_CURVE #222/#281/#303/#355 has one cubic side in the previous indexed 77-patch BP versus two sides in the isolated candidate; old cylinder #1986 and planar #1800/#1773 need exact cubic edge subdivision and propagated patch remapping. **The connected admitted S40 atlas remains 77 patches and 16/43 original source faces**, never 107. Directed Python S3.M–S3.Q: 91/91 PASS on the byte-pinned original S40. Next finite **S3.R**: de Casteljau subdivision with source-canonical global indices, exact two-sided native edge correspondence and re-run all native/source UV/error gates before admitting #218. Full APMesh TRI/QUAD and genuine original non-manifold positives remain unverified. Do not merge PR #225.

## 2026-11-16 S3.P original #2457 complement checkpoint

The [S3.P measured source-to-native half-cylinder extension](S3P_S40_COMPLEMENTARY_SPLINE_CYLINDER_ADMISSION.md) preserves the nine original split-edge boundaries of S40 `ADVANCED_FACE #2457`, including three distinct source 3D B-splines, and the exact two globally indexed shared generator controls `#1616/#1753` with prior `#1519`. Source X reference orientations are opposed, producing complementary (not duplicate) native cylinder halves. Source-conforming UV decomposition adds **18 bounded patches** and **24 internal indexed seams**, yielding **77 partial BP patches**, **864 controls**, **16/43 original source faces**. Nine source-to-native `TopoDS_Edge` IDs and both original shared interfaces were checked; guarded Bernstein radial support and actual original native 3D B-spline boundary samples pass the fixed **0.001 mm** experimental budget. The previous **59→77** original BP transformation was audited independently and **61/61 directed S3.M–S3.P Python tests passed**. Full all-suite and production C++ regressions were NOT run. Next S3.Q must handle S40 `ADVANCED_FACE #218` **without losing its real inner loop** and provide topological and geometric coverage tests before admitting any new patch. Full original CAD shells, original external 3+-incident non-manifold positive, accepted APMesh TRI/QUAD, redistribution rights, advisor scientific approval and protected merges remain OPEN.

## 2026-11-16 S3.O original B-spline trim admission checkpoint

[Bounded original S40 #1519 spline-trim experiment](S3O_S40_SPLINE_PCURVE_TRIM_ADMISSION.md) extends the independently indexed partial atlas **43→59 patches, 511→681 global controls, 14→15/43 original source faces**. Source `PCURVE` monotonicity and axial constancy justify a stepped 16-rectangle UV decomposition while retaining distinct original 3D B-spline edges and their exact source/natively shared topology. Eight unique original source boundaries and the two already indexed planar generator feature controls are admitted; 21 new internal seams use identical global integer controls. The 0.001-mm experimental budget is held fixed: 6 central sectors fail, 7 sectors pass guarded radial and native original spline-edge sampled checks. **45/45 S3.M+S3.N+S3.O directed tests passed on the raw-SHA-256-pinned S40 source**. No new claim is made about the unrerun full Python suite or C++ regression. Next bounded S3.P: reconstruct #2457 source spline trims, maintaining previous global feature IDs, then handle hole-bearing #218 separately. Full CAD atlas, genuine external 3+-incident non-manifold positive, APMesh TRI/QUAD mesh acceptance, advisor approval and protected main remain OPEN. Keep derived BP/GLB and third-party source out of public Git pending rights review.

## 2026-11-16 S3.N original #1986 source-trim pilot

[The bounded original S40 S3.N report](S3N_S40_ORTHOGONAL_SPLIT_SOURCE_ADMISSION.md) admits one further source cylinder `ADVANCED_FACE #1986` via its original 8-edge single-wire orthogonal STEP PCURVE polygon. A conforming 18-patch bicubic partition (8 sectors in both long middle bands plus the short outer strips) yields **43 total partial BP patches, 511 global control IDs** for **14 of 43 source S40 faces**. All 8 original boundary EDGE_CURVEs have distinct original/native TopoDS identities and 24 new internal integer-indexed seams; original planar generators #2019 and #2071 retain their 8 existing control IDs. Fixed pilot 0.001 mm passes guarded floating-point Bernstein radius and sampled native trimmed-curve/face audits; this is **not continuous trimmed-surface certification**. **28/28 S3.M+S3.N directed tests passed**. Full accumulated suite timed out, so do not claim a fresh whole-suite pass. Next bounded S3.O target: safely parameterize the source B-spline exterior boundary of #1519, then #2457; keep #218 native inner hole intact. Preserve 29 excluded S40 faces, external true original 3+-sheet admission, full APMesh TRI/QUAD and C++ regressions, independent scientific approval and main separation.

## 2026-11-16 S3.M measured source/native trim checkpoint

The [S3.M original S40 complex trim diagnosis](S3M_S40_COMPLEX_TRIM_INVENTORY.md) confirms one genuine native inner wire on #218 (source loops 8+4), 8-edge spline-trimmed #1519, 9-edge spline-trimmed #2457, and **8-edge all-line/all-circle 3D master geometry with line PCURVEs on #1986**. Nine S3.M directed tests pass; the enlarged whole-suite rerun hit an execution timeout in S3.L, so no 188/188 certification is claimed. Next bounded S3.N: decompose **#1986 first**, preserving each original EDGE_CURVE and shared global BP index, with independent native UV and geometry audits before any admission. Keep original STEP and derived visualization mesh/BP private pending rights review. Other three faces, 30 unrepresented S40 original faces, genuine external 3+-sheet original source, APMesh TRI/QUAD and production C++ suite remain open.

## 2026-11-16 S3.L original S40 second-ring partial BP checkpoint

[The S3.L native S40 pilot](S3L_S40_SECOND_RING_NATIVE_ATLAS.md) advances beyond M5: one original planar generator anchor per cylinder is sufficient only when the second original cylindrical generator is uniquely source-indexed and the native original `TopoDS_Edge` is shared with the second cylinder. Original S40 now has nine exact planar faces plus four bounded second-ring cylinder faces represented by 25 partial Bézier patches, 320 global controls and eight two-sided original feature seams (two cylinder-cylinder). Native original S40 UV classification and guarded radial support meet the predeclared **0.001-mm pilot** budget. The original #3127 3D/2D STEP angle mismatch is **explicitly recorded** and separately gated at 1e-8 rad. 179/179 locally discovered Python research tests pass using byte-frozen external STEP originals. Next bounded S3.M scope is **feature-curve-first partition of the four still-excluded complex native S40 cylinders (#218/#1519/#1986/#2457)** including B-splines, inner trim loops, split edges, original curve identities and independent native face membership. Do not publish/re-distribute third-party-derived BP pending rights review. Maintain remaining original S40 faces, M5 holes, original 3+-incident source admission, TRI/QUAD generation, full C++ regressions and advisor review as separate OPEN gates. Preserve draft PR isolation; do not merge.

## 2026-11-16 S3.K original-native admission checkpoint

[Original-native S3.K report](S3K_ORIGINAL_NATIVE_CAD_ADMISSION.md) supersedes the previous local-source availability blocker for this research runtime. M5/S40/S27/M3 raw STEP SHA-256 digests now match the frozen upstream originals; all four were imported and independently screened, with 45 partial planar BP patches, 152 source/native feature-edge interfaces and 29 adjacent cylindrical supports measured. The actual M5 original source/native joint atlas consists of 14 partial patches (6 planar, 8 cylinder) with original shared integer generator controls; native OCCT UV classification accepted 648 interior and 352 boundary samples for two source cylinders at the fixed pilot 0.001-mm budget. The 164-case Python research suite passed fully with original assets; dormant test-only source-model/skipping defects were corrected. Next scientific work: prioritize original S40 trim/p-curve decomposition and the remaining 33 unrepresented M5 faces, while searching independently for a genuine original external 3+-sheet non-manifold model. **Do not represent partial BP or guarded analytic support checks as complete CAD mesh generation, formal continuous trim certification, advisor-approved scientific tolerance, or C++ production regression.** Keep research PR #225 draft, retain unmodified main/Stage3/QUAD, and do not redistribute original CAD/derivative geometry until rights review.

## 2026-11-16 S3.J quantified radial-support checkpoint

The [S3.J guarded Bernstein polynomial enclosure](S3J_RADIAL_SUPPORT_ENCLOSURE.md) reduces reliance on sampling-only error for **axially separable** bicubic-cylinder candidates: the degree-six squared-radius polynomial is bounded via recursively subdivided Bernstein coefficient hulls, with independently required pilot budget, source-identity checks, explicit floating-point guard and adversarial negative tests. The original M5 source-only reference confirms a four-sector-per-face idealized cubic fits the chosen **numerical radial support** pilot tolerance. The hard scientific next gate is still the **byte-identical M5 STEP native import**, original source-to-OCCT face/edge correspondence, original native UV trim and closest-trimmed-face verification, then closure of all remaining curved/trimmed surfaces before TRI or QUAD mesh admission. This code does not provide formal interval arithmetic, a completed original CAD atlas, any genuine original 3+-incident non-manifold positive, or production modernization. The full source/native acceptance is NOT RUN. Research PR remains draft.

## 2026-11-16 S3.I original-control planar/cylinder partial-atlas pilot

The [S3.I joint source-native BP gate](S3I_SHARED_PLANAR_CYLINDER_BP_GATE.md) resolves the *synthetic/native* cross-surface control-index test: 1 exact planar quad plus 6 cylinder patches share two original STEP generator EDGE_CURVE identities and eight identical global BP vertex indices. The separately imported OCCT BRep provides source-to-native candidate/first-ring mapping and **sampled closest trimmed-face distance**, not a certified continuous or UV trim mapping. One valid OCCT generator PCURVE used an exact degree-one clamped B-spline and exposed an overly restrictive previous LINE-only reader; corrected with strict degree/knot/control checks. Local research unit tests: 133 discovered, 126 passed, 7 original-asset skips, 0 failures. Next mandatory gate: acquire and SHA-256 verify *actual* M5 STEP outside Git, run S3.E/F/G/H/I against original #3493/#3976, record each independent import/trim/fit failure, and only then extend original curved coverage. S40 and independently sourced genuine 3+-sheet model remain open. Keep QUAD/production untouched and PR #225 draft.

## 2026-11-16 S3.H M5 source-constrained cylindrical pilot

[The S3.H pilot](S3H_M5_SOURCE_CONSTRAINED_CYLINDER.md) now derives the physical directed trimmed circle arc from the original M5 `ORIENTED_EDGE`, `EDGE_CURVE`, `CIRCLE` orientation and cylinder `PCURVE` U labels, rather than assuming the minor arc. Both original M5 cylindrical source faces have 2.102093169774461-radian sweeps, opposite signs and the same 15-mm axial generator span. Independent source-entity numerical tests show an **experimental 0.001-mm sampled budget** passing with 4 but not 2 polynomial Hermite bicubic sectors per original face. A fail-closed source STEP → indexed BP candidate converter now preserves S3.D source canonical generator control identities and author-derived seam control indices, with negative and independent analytic checks. Original source M5 *local* conversion remains **NOT RUN**, blocked by absent byte-identical STEP files in this runtime; the source original results were computed through an independent GitHub-connector STEP reference path. Next priority is native Open CASCADE import of pinned original M5, 3D/UV trimmed-domain/edge-orientation verification, S3.E/F/G certificate completion, and explicit shared global planar/cylinder BP index merger before any full atlas/generator claim. S40 complex trims, original non-manifold 3+-sheet positive, APMesh TRI/QUAD and production exact-head gates remain open. Do not modify or merge production.

## 2026-11-16 S3.G source-cylinder feasibility checkpoint

[Original source-cylinder constraint report](S3G_CYLINDRICAL_SOURCE_CONSTRAINTS.md) and two source-reference receipts record the 44 candidate-to-cylinder edges across the four pinned STEP originals. Axial line/radius compatibility is checked against STEP support geometry, not inferred by proximity. Of 29 directly adjacent cylindrical source faces, only 8 satisfy a bounded one-wire/4-edge/two-anchor/two-CIRCLE topology gate; among priority models, M5 contributes 2 and S40 contributes 0. The synthetic native S3.E/S3.F/S3.G crosscheck adds exact STEP→TopoDS cylinder support radius/axis/origin comparison and fail-closed outputs (96 test cases, 91 pass, 5 original-asset skips). **This is not an industrial original native certificate or a fitted Bézier atlas.**

**Next scientific work:** native original M5/S40 STEP files outside Git with pinned raw SHA-256; S3.E/F/G certification per original face and edge; M5 bounded angular U/V decomposition with canonical shared generator cubic control indices and independently checked geometric errors under predeclared budgets. Keep S40 first-ring cylinder and spline trim decomposition as a separate blocked track; do not fill omitted faces or claim complete CAD/non-manifold/accepted TRI/QUAD. Preserve production branch and advisor review gates.

## 2026-11-16 S3.E synthetic-native checkpoint and conditional S3.F

A [research-only STEP-to-native BRep correspondence verifier](S3E_SOURCE_NATIVE_INTERFACE_GATE.md) now fails closed on ambiguous planar source/native matches, mapped TopoDS edge/vertex collisions, incorrect adjacent native support, altered original checksums and incomplete independently audited planar BP attribution. On a *locally constructed* four-face half cylinder, source identity was uniquely related to one planar candidate face, four original straight interface edges (including two native cylindrical neighbors), and an independently audited partial BP. This establishes a reproducible **algorithmic-control result**, not industrial M5/S40 source-to-native bijection. Full local research suite: **67 cases, 64 PASS, 3 explicit original-asset SKIP, zero failing cases**. Original-source-native import/mapping in this execution: **NOT RUN**. Next S3.F requires byte-pinned original imports and fail-closed source/native ID mapping for M5/S40 before constrained excluded-cylindrical patches; scientific source and APMesh TRI/QUAD claims remain conditional. Research PR remains draft.

## 2026-11-16 S3.F research checkpoint

The [S3.F direct first-ring face-ID gate](S3F_FIRST_RING_FACE_CORRESPONDENCE.md) is implemented and tested on an author-generated STEP half-cylinder with native Open CASCADE import, including original-edge identity, strict injectivity, support type, cross-interface consistency and fail-closed reports. The independently inspected original M5/S40 graphs predict 7 and 18 excluded first-ring neighbor faces, respectively, but these are **source-only reachability predictions** and must not be described as native correlations. Next conditional work: obtain byte-identical original M5/S40 STEP files outside Git, execute S3.E and S3.F source-native certificates, document pass/fail and ambiguity by face/edge ID, then attempt constrained cubic surfaces. Preserve historical models, scientific acceptance gates and the unclosed 3+-incident external positive requirement. Production/QUAD stays untouched.

## 2026-11-16 S3.D measured research checkpoint

The [S3.D original feature-curve gate](S3D_FEATURE_CURVE_GATE.md) has directly inspected and numerically screened the 152 original candidate-to-excluded STEP edge identities. All have `LINE` master geometry (108 neighboring excluded planar faces, 44 cylindrical); canonical cubic line representation is analytically exact per edge, with recorded finite STEP master-line and de Casteljau residuals. Source-entity control index construction and its analytic auditor are isolated, with 8 new directed PASS and one real-original SKIP. The next active gate is **source-to-native edge/face bijection and constrained four-sided decomposition of the excluded neighboring faces**, especially M5 and S40. No complete or accepted CAD atlas follows from linear-feature eligibility, and no production/QUAD changes are authorized. Keep the separate third-party original 3+-sheet search open.

## 2026-11-15 priority realignment — source CAD complexity ahead of more synthetic demonstrations

[Scientific selection v2](SCIENTIFIC_MODEL_SELECTION_V2.md) is the authoritative **near-term ordering** without erasing R0-R7 hard gates. R2/R3 three-box, T/Cross and analytic ruled sheets stay as bounded unit/negative fixtures; they are not the primary model roster for a new paper.

**Immediate active work:** source-original CAD cohort MAMBO M5 (mixed cone/cylinder/torus), S40 (B-spline surfaces), S27 (feature adjacency) and M3 (face complexity). Their exact upstream STEP entity graphs have been directly inspected; see [R2.E1 evidence](R2_COMPLEX_CAD_STEP_SCREEN.md). Prioritize true native CAD import and source-specific, reproducibly rendered figures, then a bounded four-sided patch decomposition feasibility audit. Preserve failed/deferred cases.

**Parallel scientific blocker:** find a third-party source with independently verified 3+ incident original surface sheets. Do NOT relabel complexity of manifold CAD as non-manifold incidence or count derived sewing/welding as an original external positive. Keep the older three historical Book/Eistute/Decor models as published comparators.

**Geometry gate:** evaluate rational/NURBS cylinders/cones/toroids and trim loops against the strict polynomial bicubic BP representation; record approximation errors and source-feature constraints with predeclared budgets before fitting. Frozen TRI baseline and mode-specific QUAD/TRI, all-quad and anisotropic comparisons remain downstream and conditional.

## Objectives, exclusions and evidence hierarchy

O1: curate a small, scientifically defensible benchmark covering intended non-manifold shared-curve junctions and appropriate manifold CAD controls.
O2: diagnose topology without silently repairing it; preserve source entity identity and record limits of reconstructibility.
O3: prove a standalone converter to the existing indexed bicubic Bezier BP grammar only for admitted geometries.
O4: qualify existing APMesh TRI execution on the new inputs without altering its algorithms, acceptance criteria or historical models.
O5: define future, separate comparisons for TRI/QUAD, all-quad and anisotropy when their implementation status supports such claims.

Evidence hierarchy: (a) upstream model and metadata identity; (b) independent source-topology oracle; (c) independent geometric-fit oracle; (d) BP validator and source-boundary oracle; (e) APMesh generator execution and exact recorded acceptance; (f) independent output validation; (g) only then cross-method comparisons.

An accepted generator state and a saved rejected candidate are different observations. A candidate OBJ, log or screenshot alone is not proof of success.

## Work packages and mandatory gates

| ID | Work package | Output | Admission / exit gate |
|---|---|---|---|
| R0 | Baseline and concurrency audit | exact main SHA, active PR inventory, current regression contracts, immutable 3-model inventory | document existing status and identify tests; no unsupported claim of having executed them |
| R1 | Scientific taxonomy and benchmark search | authoritative source list, identifiers for ~30-40 preliminary candidates (planning target, not quota), per-file rights | references traceable; source names are not substituted for model IDs |
| R2 | Independent topological classification | edge/face incidence, oriented adjacency, sheet labels, vertex links, boundary and intersection reports | intended junctions distinguished from defects; positive models have nonzero declared shared-curve incidences |
| R3 | Geometry / representation feasibility | 8-12 candidate pilot set (target, conditional), conversion feasibility report, error budget proposal | every selected case is either supported, unsupported with evidence, or blocked with reason |
| R4 | Standalone proof of conversion | source -> feature graph -> bounded four-sided patch decomposition -> indexed BP; sidecar graph metadata | BP grammar valid, all intended source shared curves represented exactly as common curve entities, no implicit topology welding |
| R5 | Controlled APMesh TRI pilot | fresh per-run config/output manifests, independent boundary checks, saved-state/acceptance classification | historical traces unchanged on qualified environment; external generation states and positive incidence coverage actually measured |
| R6 | Research extension and comparisons | separately versioned TRI/QUAD, all-quad, anisotropic evaluation recipes; negative controls | code paths and modes are qualified individually; matched geometry, constraints, output metrics and explicit noncomparability labels |
| R7 | Publication/reproduction freeze | frozen selection, train/dev vs held-out final set, source provenance, raw outputs, negative results | scientific and engineering review; advisor approval; reproducible artifact and limitations table |

R0-R3 can proceed as documentary/diagnostic or isolated experimental research activity without a production C++ code change. R4 is a new experimental subsystem, not a shortcut into Stage 3. R5-R7 have prerequisites and are not authorized merely because this plan exists.

## Execution order and stop conditions

1. Record exact revision and concurrent branches/PRs. Never overwrite anyone else's in-flight code; all changes occur on topic branches with explicit scope.
2. Catalogue individual model IDs and licenses. Keep raw third-party files out of Git until redistribution permissions are confirmed; a reproducible download manifest is preferred.
3. Freeze topology taxonomy BEFORE selecting only successful models. Include positive and adversarial/unsupported cases.
4. Start with an author-constructed analytic four-sided patch fixture, then one independently sourced intended multi-surface junction. Prefer known analytic / STEP B-Rep to arbitrary STL.
5. Prove a common, shared boundary graph before surface fitting. Same geometry with independently fitted near-equal edges is NOT shared-curve compatibility.
6. Produce and validate exact 16-control indexed BP records with canonical side orientation; preserve an external provenance/graph sidecar outside legacy BP.
7. Execute admitted inputs through frozen TRI reference; compare exact historical regression under matching source/binary/config/instrument conditions.
8. Only then create future method-specific QUAD/TRI, all-quad and anisotropic trials with their own eligibility and separate baselines.
9. Hold out evaluation models; log all attempted conversions, rejections, retuning and exclusions. Publish failures and limitations.

Stop R4 for a candidate when there is no defensible finite four-sided bicubic decomposition within a declared geometry budget or if intended junctions cannot be kept as shared entities. Mark UNSUPPORTED, do not modify APMesh input acceptance or secretly rebuild the topology. Stop integration if historical regressions fail or independent output incidence coverage is zero.

## Converter architecture (proposal only)

Raw sources (STEP / B-Rep, then OBJ / STL / PLY)
  -> versioned parser and provenance
  -> independent topology/feature graph (edges, incidences, sheets, vertex links)
  -> constrained surface segmentation and four-sided patch layout
  -> common curve fitting FIRST; compatible per-patch bicubic fitting SECOND
  -> independent geometry + topology oracles
  -> indexed BP writer plus JSON sidecar with source-to-patch mappings
  -> existing BP validator, without changes to production acceptance behavior
  -> separate APMesh execution and outputs

A B-Rep face is not necessarily a single four-sided polynomial patch. Trimmed NURBS, holes, discontinuities, singular parameterizations, periodic surfaces and arbitrary degree require explicit subdivision or must be rejected. For polygon sources, reverse fitting can be non-unique; reconstructed geometry must be identified as an approximation with measured uncertainty.

## Per-model evidence package

Original URI and file ID; author/citation; per-file rights and redistribution decision; raw SHA256; source format, units, scale and normalization transform; topology classification with edge/vertex/sheet incidence; proof of intended junctions; feature graph with labeled curve IDs; chosen conversion algorithm/parameters; BP SHA256 plus sidecar; source-to-patch map; geometric errors and worst-case feature distortion; independent checker report; supported/rejected/blocked status; runtime binaries/config hashes; actual generation acceptance decisions; complete output artifacts and validation results.

Geometry metrics: bidirectional sampled Hausdorff (with sampling convergence/disclaimer), RMS, feature-curve deviation and optional certified bounds if available. Topology metrics: exact discrete incidence and orientation identity; never blend topology and geometric tolerances. Mesh metrics: triangle quality, degenerate/duplicate faces and curve chain agreement; later quad scaled Jacobian, angle, aspect ratio and irregular vertices; metric-space quality for anisotropy. Performance: wall time, peak RSS, element count, degrees of freedom, full hardware/toolchain metadata.

Statistical methodology: stratify by topology and complexity, fixed parameters or documented per-model optimization budget, paired comparisons where domains overlap, uncertainty intervals, and results for every admitted model. Distinguish converter failures from mesher failures.

## Exit conditions and sequencing constraints

- Research documentation gate: committed proposal + risk/decision log + source leads + empty model-level register; no model acceptance claim.
- Curated corpus gate: each named file independently traced, analyzed, and rights reviewed. Dataset publicity is insufficient.
- Converter prototype gate: reproducible positive and negative fixtures; independent topology and geometry checks.
- TRI integration gate: actual accepted states, nonzero shared-incidence checks, exact qualified historical regression, absence of source changes.
- Future-method gate: method-specific numerical and topology/quality oracles; no borrowing TRI evidence for experimental QUAD/anisotropy.
- Publication gate: frozen protocol, independent scrutiny, recorded negative findings, advisor-approved scope, release/license audit.

### External review responsibilities

Computational topology: verify junction semantics, vertex links, orientation and adjacency.
CAD/geometry: validate polynomial representability, trimming and fit error.
Meshing/numerics: validate element metrics and matched baselines.
C++ architecture: approve ownership isolation and fault-injection design.
QA/security: negative controls, hostile malformed inputs, input limits and independent oracles.
Research methods/statistics: freeze datasets, failure denominator, fairness and generalization.
Open-science/licensing: provenance, individual rights, repository separation.
Advisors: decide thesis contribution and any scientific change to the generator.

No review role is claimed to have signed off yet.

## Dependencies

See AGENTS.md, docs/PROJECT_STATE.md, docs/MODERNIZATION_PLAN.md, docs/GENERATION_VALIDATION_CONTRACT.md, docs/API_CONTRACTS.md and DATA_PROVENANCE.md. Never modify the historical publication oracle to accept a new research input.

## Evidence update: one R3 controlled pilot (2026-11-14)

- R0: repository baseline and concurrency documented. No new historical CTest/scientific regression executed.
- R1: 40 traceable leads, none external G1/G2 admitted.
- R2: one locally constructed four-sheet, one-four-incidence Open CASCADE BRep; source CAD had three different edge identities. External G2 still blocked.
- R3: a **single planar analytic reference case** has four exact bicubic patches in the indexed BP grammar (52 unique control vertices; four exact references to central cubic C0; 13 distinct curves), a versioned research BP fixture, an independent de Casteljau + native CAD sample audit, and 13 new local adversarial tests. Entire proposed multi-model R3 work package remains open.
- R4: a narrowly scoped analytic BP writer is available as a **research pilot**, NOT a general CAD reverse converter and NOT an approved production component.
- R5-R7: untouched. No APMesh TRI/QUAD mesh generation or paper comparison for the new control.

See [R3 pilot measurements](R3_ANALYTIC_BICUBIC_PILOT.md) and [scientific gallery](gallery/README.md). Any novel CAD model admission, tolerance/feature semantics or technique change requires independent review and new evidence. No stage closure beyond the bounded analytic control is claimed.

## 2026-11-15 — additional bounded R3 curved control

One synthetic deformation of the R2 four-sheet incidence graph was constructed with a nonplanar cubic Bezier spine and four ruled bicubic sheets. The canonical C0 is used four times by index, with one patch in reverse local parameter orientation. A native kernel Shell has one true four-face edge; BRep export/import preserves that edge. The R3 analytic power-basis auditor and OCCT BRep distance checks pass the bounded sample budgets. The local R2/R3 research bundle passes 44 tests, including 12 new curved/negative tests and a fixed-parameter nonpolynomial exact-representability rejection. Raw outputs are deterministic in two runs. See [curved proof](R3_CURVED_BICUBIC_PILOT.md) and [case matrix](R3_REPRESENTABILITY_MATRIX.md).

No third-party CAD source was converted: **G1/G2 external admission, full R3, general R4, runtime R5 and comparative R6/R7 gates remain open**. This is an author-created analytic control; no source algorithm change, merge, production test or article-level generalization is claimed.

## 2026-11-15 — R3.C2 bounded native partial-face contact experiment

The pinned Fusion Energy T-Junction and Cross-Junction CAD recipes were recreated as separate valid native solids. A subset of source faces underwent explicit OCCT Common/Cut decomposition, preserving source face IDs and rejecting incomplete/ambiguous split cases. One T contact produces 5 planar four-sided sheets and 2 actual three-face native TopoDS edges; two Cross contacts produce 10 such sheets and 4 **distinct** three-face native edges (2 disconnected Shells). An isolated, identity-aware bicubic BP writer creates 5/10 patches with 64/128 distinct global control vertices. Independent native-rectangle/de Casteljau and BRep checks recorded max errors <=3.552713678800501e-15 in measured samples. 19 new and 44 previous local tests pass; STEP and BRep roundtrips and byte-identical regeneration are recorded. A discovered fuzzy Boolean near-gap false positive was closed with a stricter source geometry distance screen at 1e-12, separate from sewing tolerance 1e-8. [Full proof](R3_PARTIAL_CONTACT_PILOT.md), [adversarial matrix](R3C2_CASE_MATRIX.md).

**G1/G2 source-original admission, general curved/trimmed CAD segmentation, full R3, R4 general conversion, R5 APMesh generation, QUAD/anisotropy and historical exact-head regression remain OPEN/NOT RUN.** Do not merge or claim scientific generalization from a local mirrored CAD experiment.


## Measured S1 original-CAD import and native image update (2026-11-15)

**S1 original-source native-import milestone — MEASURED FOR FOUR:** MAMBO M5, S40, S27 and M3 were acquired as byte-exact original pinned STEP source files (all four checked against their Git blob SHA-1 and raw SHA-256), imported into Open CASCADE as valid single-solid B-Reps, and source-specific shaded/face-type native figures were rendered. Six source units/geometry/edge hazards surfaced. Four source-specific native receipts and a visual gallery are versioned in the research branch. Seven additional local mandatory-source tests passed; two local render runs produced byte-identical 13 PNG images. See [S1 native report](S1_NATIVE_ORIGINAL_CAD_AUDIT.md).

**Native edge counts:** M5 has 108 actual native TopoDS edge identities, of which six are degenerate; only 102 nondegenerate edges correspond to its 102 raw STEP EDGE_CURVE records. S40 has 117, S27 has 144 and M3 has 169 native edges, all nondegenerate. No true 3+-distinct-face native TopoDS edge was found. S40 has 3 native BSPLINE faces although STEP has only 2 explicit B-spline support entities.

**S2 visual-source milestone — FIRST TWO VIEWS AVAILABLE:** shaded source CAD and colored source B-Rep support surfaces for all four, with SHA-256 and renderer provenance. Proposed per-face patch atlases and valid TRI/QUAD output figures remain blocked until computed. The gallery must not be described as an APMesh generation result.

**S3 decomposition next:** evaluate planar 4-edge, single-wire face candidates (M5 6, S40 9, S27 20, M3 10) and source feature/trim boundaries. Remaining planar and rational/nonplanar surfaces require explicit decomposition/approximation budgets. Per-file rights signoff remains independent; original external multi-sheet G2 stays empty. The 63 previously recorded R2/R3 source-mirror tests were not rerun in this S1-specific native audit. Production main and QUAD branches were untouched.
