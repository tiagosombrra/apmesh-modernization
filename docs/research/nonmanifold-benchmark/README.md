# Non-manifold benchmark corpus and reverse-patch feasibility

**Status:** scientific priority is ORIGINAL complex CAD. **Four byte-verified MAMBO STEP originals (M5/S40/S27/M3) have now PASSED native Open CASCADE import, topology profiling and source-rendered visual evidence**; no original multi-sheet positive or APMesh accepted meshing demonstrated. R2/R3 synthetic fixtures remain tests only. Updated 2026-11-16.
**Frozen planning base:** main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Research branch:** `research/benchmark-corpus-reverse-patches`, draft PR #225.

## S3.K original MAMBO native CAD admission and sampled UV trim (2026-11-16)

[The original-native S3.K checkpoint](S3K_ORIGINAL_NATIVE_CAD_ADMISSION.md) now **actually imports all four byte-pinned original MAMBO STEP files** using local CadQuery/Open CASCADE, rather than relying on source-only GitHub text and synthetic fixtures. [Machine-readable original native receipt](evidence/s3k/original_native_execution_receipt.json): 196 original faces, 45 independently audited planar BP patches, 152 original interface edges correlated to native TopoDS entities, 62 excluded first-ring face IDs and 29 native cylindrical supports crosschecked. **M5** actual source `ADVANCED_FACE #3493/#3976` yields a source-identified **14-patch partial BP (6 planar + 8 curved)** with 176 global controls and 16 independently verified same-index source generator controls. [Native trimmed UV receipt](evidence/s3k/original_m5_native_uv_4_sectors.json): all 648 original-cylinder interior samples `IN`, all 352 boundary samples `IN`/`ON`; maximum native projection distance 0.000395427371 mm and guarded support radial upper 0.000395428371 mm against the **pilot** 0.001-mm budget. Six sectors per face also passed [separate native receipt](evidence/s3k/original_m5_native_uv_6_sectors.json). Two-sector fit was correctly rejected. The research suite with all originals available: **164/164 PASS, 0 SKIP, 0 FAIL** following four test-only original-input corrections and 13 new S3.K controls. **These are still partial CAD patch atlases, not full manifold or non-manifold source models or accepted APMesh TRI/QUAD meshes.** Third-party original source bytes and industrial-derived BP geometry remain outside this public branch; redistribution-rights review, S40 complex trim decomposition, true external 3+-sheet non-manifold positive and production C++ regression remain OPEN. PR #225 stays draft.

## S3.J bounded Bernstein cylinder support enclosure (2026-11-16)

[Implementation, numerical derivation, scope, and local test closure](S3J_RADIAL_SUPPORT_ENCLOSURE.md) now attach a **degree-six Bernstein convex-hull radial deviation enclosure** to the existing source-identified S3.I partial BP. On the author-generated native OCCT half-cylinder, the 6-cylinder-patch joint BP has a maximum **guarded numerical radial support upper of 0.000584520795 mm** against a separately fixed **0.001-mm pilot budget**; the independent source/native original curve constraints, axial separability, angular wedge, canonical global controls and BP identities are rechecked. An [independent source-side result on pinned original M5 STEP entities](evidence/s3j/original_m5_bernstein_reference.json) yields source ideal-Hermite guarded upper values **0.006239878152 / 0.000395428370 / 0.000078310235 mm** for 2/4/6 sectors per face. **These are not native-imported M5 BP patch results or formally directed-rounding certified continuous Hausdorff bounds**. Numeric floating-point Bernstein subdivision uses an explicit margin and bounds only the analytic cylinder support, not the imported trimmed OCCT face. The research suite was run locally: **151 discovered / 143 PASS / 8 explicit original-input SKIP / 0 FAIL**; frozen production regression and original M5/S40 native integration remain BLOCKED. PR #225 stays draft, with no production/QUAD code changes.

## S3.I source-identical planar/cylinder BP shared-control gate (2026-11-16)

[Research-only joint atlas construction and independent native audit](S3I_SHARED_PLANAR_CYLINDER_BP_GATE.md) now union a source-original-EDGE_CURVE keyed planar bicubic quad and cylindrical approximations into one indexed partial BP. A source-native OCCT imported, **author-generated manifold half-cylinder STEP** yields 1 planar + 6 cylinder patches = **7 partial patches, 84 global controls, two original source generator edges and 8 proven identical control IDs**, with a **0.000584520 mm maximum sampled distance to the actual trimmed native cylindrical face** under a prespecified 0.001-mm pilot budget. Four cylinder sectors fail that budget and six pass. The S3.H PCURVE reader now recognizes only rigorously checked clamped, two-pole degree-one B-spline equivalents of a straight constant-U line, as encountered in this Open CASCADE export. The local research suite was **133 discovered / 126 PASS / 7 original-source SKIP / 0 FAIL**. Original industrial M5/S40 STEP-native execution remains **NOT RUN**; the original M5 source-only 8-cylindrical-patch estimate is not an admitted native atlas. No continuous error certificate, full CAD conversion, APMesh TRI/QUAD acceptance or original 3+-sheet positive is claimed. Draft PR only.

## S3.H M5 original-entity-constrained cylinder BP pilot (2026-11-16)

[Source constrained bicubic report and regression contract](S3H_M5_SOURCE_CONSTRAINED_CYLINDER.md) and its [pinned original M5 independent numeric sampling evidence](evidence/s3h/original_m5_cylinder_source_sampling.json) now resolve both M5 circular trim-arc *directions* from the actual source STEP entities (original faces `#3493`/`#3976`, sweep ±2.102093169774461 radians). The tested source-only cubic-Hermite sector candidate meets an experimental **0.001 mm sampled-error budget** with **4 sectors per original face** (8 BP patches across the two source faces; max sampled error approximately 0.0003954274 mm); 2 sectors fail at approximately 0.0062398772 mm. A separate executable Python BP generator, independent analytic oracle and adversarial controls have **19 directed checks: 18 PASS / 1 SKIP**, with a total local research suite of **115 discovered / 109 PASS / 6 original-source SKIP / 0 FAIL**. The BP produced *locally* uses an author-generated synthetic STEP; original M5 BP generation in local OCCT, source/native UV trim validation, cross-atlas planar index unification, continuous fit bounds and accepted APMesh mesh generation remain **NOT RUN**. Original external multi-sheet source admission remains **OPEN**. No third-party original STEP bodies are committed.

## S3.G original cylinder generator and native support audit (2026-11-16)

[Measured source-constraint results and native support gate](S3G_CYLINDRICAL_SOURCE_CONSTRAINTS.md) now directly screen 44 planar-to-cylinder `EDGE_CURVE` identities from the pinned originals. All 44 match source-cylinder axial generator/radius constraints within a predeclared source numeric tolerance, based on [the independent original-source oracle](evidence/s3g/original_cylinder_source_axis_oracle.json). [The original topology screen](evidence/s3g/original_cylinder_source_topology.json) finds 2 source rectangular cylinder candidates in M5, none of the 8 first-ring S40 cylinders, 2 in S27, and 4 in M3. M5's two candidates each need angular subdivision (minor generator separation ~2.1021 rad), and S40 needs trim/split-edge decomposition. A new fail-closed source/native-support crosscheck verifies radius, axis and native S3.F face binding on an author-generated half-cylinder; [synthetic control evidence](evidence/s3g/synthetic_native_support_receipt.json). Research local tests: **96 discovered / 91 PASS / 5 explicit SKIP / 0 FAIL**, not full production regression. Industrial original M5/S40 native S3.G import, source p-curve/UV trim proof, original shared-control patch construction and accepted APMesh meshes remain **NOT RUN** in this execution. No third-party original STEP bytes redistributed; PR #225 stays draft.

## S3.E native source-entity interface correspondence (2026-11-16)

[The S3.E conservative source/native gate](S3E_SOURCE_NATIVE_INTERFACE_GATE.md) compares exact original STEP `ADVANCED_FACE`, `EDGE_CURVE` and vertex identities to *uniquely inferred* imported TopoDS candidate faces and edges, confirming adjacent BRep support categories before independently audited partial BP emission. **Executed native test is an author-created half-cylinder only**: 1 eligible planar source face, 4 source-to-excluded interfaces, 2 adjacent cylindrical interfaces and 1 independently audited partial planar BP. A source-entity cubic feature curve oracle, raw SHA-256 and ambiguous/coincident geometry rejection are mandatory. [Synthetic numeric receipt](evidence/s3e/synthetic_half_cylinder_native_evidence.json). All four original MAMBO native imports and original S3.E correspondence runs in this execution remain **NOT RUN** (original STEP bytes unavailable); 67 local tests = 64 PASS, 3 SKIP; no production CTest, no curved neighbor patches, no global STEP/native excluded-neighbor bijection and no APMesh TRI/QUAD accepted generation. S3.F remains blocked pending original native input and constrained cylindrical neighbor fit.

## S3.F bounded source-to-native first-ring STEP face IDs (2026-11-16)

[Implementation and admission limits](S3F_FIRST_RING_FACE_CORRESPONDENCE.md) extend S3.E from native adjacent support types to **injective original excluded-neighbor `ADVANCED_FACE` IDs ↔ directly adjacent `TopoDS_Face` IDs**, anchored by the same certified original `EDGE_CURVE` and native `TopoDS_Edge` identities. A four-face author-generated half-cylinder source/OCCT import verifies 1 planar candidate, 3 excluded neighboring face IDs (1 cylinder, 2 planar) and 4 original linear boundary anchors; an independently recomputed report confirms all first-ring claims. [Local receipt](evidence/s3f/synthetic_first_ring_receipt.json). A source-only [pinned M5/S40/S27/M3 reachability prediction](evidence/s3f/original_step_first_ring_prediction.json) identifies 7/18/14/23 excluded first-ring source face IDs, respectively, **without importing originals natively**. Current research unit test discovery: **80 total / 76 PASS / 4 SKIP / 0 FAIL**. Industrial first-ring native mapping, complete curved-face geometry, BP/mesh acceptance, original 3+-sheet validation and the full production regression remain OPEN. No source STEP bytes were redistributed.

## S3.D original-feature cubic identity gate (2026-11-16)

[The bounded source-curve study](S3D_FEATURE_CURVE_GATE.md) now identifies all **152 original candidate-to-excluded EDGE_CURVE** entities as 3D master `LINE` segments: 108 connect to excluded planar faces, 44 to cylindrical faces. A second, connector-side numerical check of the pinned original source evaluates endpoint-to-master-line residuals and cubic de Casteljau samples; see [per-model numeric receipt](evidence/s3d/original_step_curve_oracle.json) and [per-edge source identity inventory](evidence/s3d/original_step_interface_inventory.json). A separate research-only canonical cubic control indexer and directed negative tests are committed. Local research suite: **55 cases / 53 PASS / 2 explicit original-asset SKIP**. This qualifies bounded *source-graph linear feature compatibility*, NOT imported CAD/BRep source-edge ID bijection, adjacent curved-face fitting, complete BP patch atlas, accepted TRI/QUAD generation or external genuine non-manifold source admission. Research PR remains draft.

## S3.C original STEP source-graph gate (2026-11-15)

[Source-specific S3.C evidence, 45 candidates and the 152 original candidate-to-excluded feature edges](S3C_ORIGINAL_STEP_SOURCE_GRAPH.md) is now committed, with [machine-readable pinned STEP entity receipts](evidence/s3c/original_step_candidate_summary.json), a standalone original STEP source-graph screen and a fail-closed native partial-BP batch. All four original STEP *texts* were inspected through pinned GitHub source files and the source-graph eligibility counts match the earlier S1 native results (M5 6, S40 9, S27 20, M3 10). The actual original CAD source files were not imported or converted in this runtime. Local controls: **46 cases / 45 PASS / 1 explicit original-source SKIP**, not the complete production scientific regression. No external genuine non-manifold positive, complete CAD atlas, accepted TRI or QUAD mesh is claimed.

## S3.B bounded curved-face feasibility (2026-11-15)

[The S3.B original-CAD support/trim screen, cylindrical approximation pilot and indexed derived-seam atlas](S3B_CURVED_FEASIBILITY.md) are now committed with **19 directed S3.B local tests** passing, in addition to 11 S3.A controls. Four independently audited synthetic quarter-cylinder atlases (1, 2, 4 and 8 patches) demonstrate decreasing sampled error and exact indexed shared *derived* seam controls. The actual M5/S40/S27/M3 original STEP faces were **NOT** converted in this runtime; source-to-feature boundary compatibility, external original 3+-sheet admission and APMesh TRI/QUAD accepted generation remain OPEN. This is a separate scientific research activity, not production C++ modernization.

## S3.A bounded original-CAD partial atlas (2026-11-15)

A new isolated [source-identity-preserving planar quad to indexed BP extractor](S3A_ORIGINAL_CAD_PLANAR_ATLAS.md) and its independent native BRep auditor have been committed. Eleven local directed tests passed on authored controls; the four pinned industrial original CAD files were **not executed through this new converter** in this delivery. Source images and S1 native import evidence below remain valid; complete curved/trimming decomposition, external 3+-sheet topology, APMesh accepted TRI and future QUAD modes remain OPEN.

## S1 native original CAD evidence (2026-11-15)

**First actual complex-source gallery:**

![Four original MAMBO industrial models, rendered from their byte-exact STEP originals](gallery/source_cad/mambo_originals_native_gallery.png)

- [Full S1 native CAD audit](S1_NATIVE_ORIGINAL_CAD_AUDIT.md) — original file raw SHA-256, original Git blob SHAs, Open CASCADE solid validity, full face-edge-use histogram, edge degeneracy, support-surface types and per-face complexity.
- [Four native source-specific image pairs and combined gallery](gallery/source_cad/mambo_originals_native_gallery.png) — real CAD import, **not APMesh surface TRI/QUAD meshes**.
- [Native importer/render + feature-incidence source](probes/native_source_audit.py), [7 scoped local regression controls](probes/test_native_source_audit.py), [machine-readable receipts](evidence/s1/native_source_summary.json).
- Per-file rights are still not reviewed for redistribution; **raw CAD source STEP files are NOT in this repository**. Import, native B-Rep validation and rendered provenance pass only for these four; independent external non-manifold G2, general bicubic conversion and TRI R5 remain OPEN.

## Scientific priority correction — 2026-11-15

**The primary scientific candidates are complex ORIGINAL CAD assets, not three-box, T-Junction or Cross-Junction synthetic controls.** The latter remain conversion/regression fixtures only. Do not use their success counts as external topological generalization. The scientific benchmark needs two separately labeled external populations: geometric-complexity CAD controls versus genuinely original multi-sheet non-manifold sources; currently zero externally validated multi-sheet positives.

- [Reprioritized scientific plan](SCIENTIFIC_MODEL_SELECTION_V2.md): source-real geometry before new synthetic models, per-asset rights, graphical source provenance, native CAD and independent non-manifold gates.
- [Direct seven-asset original STEP screening](R2_COMPLEX_CAD_STEP_SCREEN.md): seven exact pinned STEP entity graphs inspected; no explicitly 3+-face shared EDGE_CURVE identified, but geometric coincidences and native topology still not checked.
- [First complex-source cohort](COMPLEX_CAD_SOURCE_SHORTLIST.csv): MAMBO M5, S40, S27, M3 PRIMARY; M1/S8 SECONDARY; Quarter Torus ADVERSARIAL. Original CAD image slots remain **PENDING** until real models can be imported and rendered.
- [Source STEP reference graph analyzer](probes/step_graph_screen.py), [six local controls](probes/test_step_graph_screen.py): standard-library-only independent reproduction tool. Raw SHA-256 is computed only when actual local original bytes are acquired; it is NOT inferred from upstream Git blob SHA.
- **No new APMesh TRI/QUAD output or external model admission** is claimed from this screening.

## Evidence and review sequence

1. [R0 baseline audit](R0_BASELINE_AUDIT.md): historical Book/Eistute/Decor model identity, frozen main and concurrency; **no fresh production regression**.
2. [R1 source discovery](R1_DISCOVERY_REPORT.md): 40 individually traceable candidates (29 HexMe original CAD files, six Fusion Energy procedural scripts, five upstream Thingi10K invalid-input leads).
3. [R2 topological screening](R2_TOPOLOGY_SCREEN.md): eight structurally traversable original STEP edge-use graphs; one torus/vertex-loop limitation; five local CadQuery pinned-source mirrors. Explicit STEP edge identity is **not** the same as geometrically coincident edges from separate solids.
4. [R2 native-kernel interface proof](R2_NATIVE_INTERFACE_PROOF.md): three-cuboid STEP export/import and 4 reconstructed spatial-interface sheets; 15 native/JSON controls passed; G2 remains blocked.
5. [R2 kernel-valid non-manifold BREP control](R2_VALID_NONMANIFOLD_BREP.md): one constructed four-face shared topological edge; 19 local controls including native BREP export/import; external G2 still blocked.
6. [R3 analytic bicubic pilot](R3_ANALYTIC_BICUBIC_PILOT.md): 4 indexed BP patches, 52 unique control vertices, one canonical 4-incident C0 boundary; 13 new controls and 32 total R2+R3 local tests passed. Not an external admitted model or APMesh mesh generation.
7. [R3 curved bicubic pilot](R3_CURVED_BICUBIC_PILOT.md): curved spatial cubic C0 with four true kernel face incidences and one reversed local orientation; 12 new tests and 44 local R2/R3 tests; no external CAD conversion.
8. [R3 representability matrix](R3_REPRESENTABILITY_MATRIX.md): explicit supported, negative, blocked and untested cases.
9. [R3.C2 T/Cross partial contacts](R3_PARTIAL_CONTACT_PILOT.md): native face Common/Cut, source-to-subface provenance, 5/10 exact rectangular BP patches, 2/4 triple-incidence curves; 19 new local controls.
10. [R3.C2 case matrix](R3C2_CASE_MATRIX.md): accepted, explicitly rejected and not-yet-supported trims and near-contact controls.
11. [Scientific visual gallery](gallery/README.md): attributed source imagery and author-authored schematic with available/unsupported representation stages.
12. [Candidate register](candidate_register.csv): all 40 are still DISCOVERED; 13 are annotated with screening observations and one extra torus limitation, but no G2 or complete G1-G7 admission.
13. [Execution plan](PLAN.md), [model admission protocol](MODEL_ADMISSION_PROTOCOL.md), [candidate source inventory](CANDIDATE_SOURCES.md) and [risk/decision register](RISK_AND_DECISION_REGISTER.md).

## Limited research probes

Located under `probes/`; not part of the production CMake build:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
python docs/research/nonmanifold-benchmark/probes/export_source_mirror.py --output-dir build/research-r2
python docs/research/nonmanifold-benchmark/probes/cadquery_contact_probe.py
python docs/research/nonmanifold-benchmark/probes/step_structural_screen.py path/to/permitted/original.step
python docs/research/nonmanifold-benchmark/probes/interface_graph_probe.py --output build/research-r2/three_cuboids_interface_graph.json
python docs/research/nonmanifold-benchmark/probes/validate_interface_graph.py build/research-r2/three_cuboids_interface_graph.json
python docs/research/nonmanifold-benchmark/probes/nonmanifold_sewing_probe.py --interface-graph build/research-r2/three_cuboids_interface_graph.json --output-json build/research-r2/sewn_complex_report.json --output-brep build/research-r2/four_sheet_nonmanifold.brep
python docs/research/nonmanifold-benchmark/probes/build_analytic_bp.py --graph build/research-r2/three_cuboids_interface_graph.json --out-bp build/research-r2/four_sheet_planar.bp --out-sidecar build/research-r2/four_sheet_planar.sidecar.json
python docs/research/nonmanifold-benchmark/probes/audit_analytic_bp.py --bp build/research-r2/four_sheet_planar.bp --sidecar build/research-r2/four_sheet_planar.sidecar.json --native-brep build/research-r2/four_sheet_nonmanifold.brep
python docs/research/nonmanifold-benchmark/probes/curved_bicubic_pilot.py --out-dir build/research-r3-curved
python docs/research/nonmanifold-benchmark/probes/audit_curved_bicubic.py --bp build/research-r3-curved/four_sheet_curved.bp --sidecar build/research-r3-curved/four_sheet_curved.sidecar.json --brep build/research-r3-curved/four_sheet_curved.brep
python docs/research/nonmanifold-benchmark/probes/r3c2_native.py --case t_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_native.py --case cross_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_bp.py --case t_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_bp.py --case cross_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_audit.py --bp build/research-r3c2/t_junction.bp --sidecar build/research-r3c2/t_junction.sidecar.json --brep build/research-r3c2/t_junction_interface.brep
python docs/research/nonmanifold-benchmark/probes/r3c2_audit.py --bp build/research-r3c2/cross_junction.bp --sidecar build/research-r3c2/cross_junction.sidecar.json --brep build/research-r3c2/cross_junction_interface.brep
```

The STEP scanner requires Python; the CadQuery probes additionally require CadQuery/OCP. The bounded local R2/R3 suite has **44 passing controls** and R3.C2 adds **19 passing T/Cross source-mirror controls** (**63 total research controls**), including near-contact false-welding rejection. Exact source Git blobs and file hashes are recorded in the R3 curved report. This does not certify the original upstream package or the production APMesh build. See R2 report for command scope, results and missing gates.

## Corpus partitions

HISTORICAL (three original author-created article baselines), SYNTHETIC_POSITIVE (analytic engineering controls), EXTERNAL_POSITIVE (**none admitted**), MANIFOLD_CONTROL (independently classified CAD quality/fitting controls), NEGATIVE_UNSUPPORTED (invalid/ambiguous/vertex-contact cases).

## Scientific boundaries

No production C++, published `.bp`, scientific acceptance policy or numerical oracle has been changed. No third-party raw asset is committed. No external 3+-sheet patch-edge source has been verified. Future reconstruction, conversion, TRI qualification and QUAD/TRI/all-quad/anisotropy work require independent gates and advisor decisions before scientific claims.
