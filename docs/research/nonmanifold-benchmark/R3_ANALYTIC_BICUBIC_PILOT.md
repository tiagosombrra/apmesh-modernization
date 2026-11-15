# R3 — controlled exact planar bicubic Bezier representation pilot

**Date:** 2026-11-14.
**Scientific classification:** standalone analytic control, **not** a general CAD-to-BP converter and **not** an admitted independent external benchmark.
**Research branch:** research/benchmark-corpus-reverse-patches, PR #225 (draft).

## Input and mathematical construction

Input: the locally mirrored three-touching-cuboids R2 geometric interface graph, selected by documented source-region semantics. Four planar source-derived sheets meet at the common spatial line C0 = {(0,0,z): -2.5 <= z <= 2.5} (source units unspecified). The R2 native Open CASCADE control is a valid Shell with four faces and one topological edge with four face incidences. The original three CAD solids retain three distinct edges instead. Do not erase this distinction.

For each sheet, the surface is parametrized by an outward radial vector D in {(0,5),(-5,0),(5,0),(0,-5)} and analytic formula:

    S(u,v) = (u * D_x, u * D_y, -2.5 + 5*v), 0 <= u,v <= 1.

Each bicubic control net is constructed by degree-elevating this bilinear ruled plane:

    P[i,j] = ((i/3) * D_x, (i/3) * D_y, -2.5 + (j/3)*5), i,j in 0..3.

The cubic Bernstein partition-of-unity and linear precision identities imply S(u,v) is reproduced **exactly over the continuous square in exact real arithmetic**. The numeric evaluation reports below test implementation roundoff, not a general signed-distance or Hausdorff bound for curved CAD. No source was automatically fitted or tessellated.

All four patch nets contain 16 vertices; the 4 C0 control vertices at j=0..3 are global indices 0,1,2,3 and each patch uses them at local slots 0,4,8,12. The other 12 controls of each patch are unique, totaling 52 distinct indexed BP vertices. All 4 share the same canonical C0, and 12 external patch sides have unique curve IDs: 13 curves overall. All four C0 uses are parameterized with increasing z. Provenance of the six original face uses is retained in a JSON sidecar; the legacy BP grammar contains no place for such provenance.

## Artifacts and reproduction

- [Source-recipe interface graph / R2](R2_NATIVE_INTERFACE_PROOF.md)
- [R2 kernel shared-edge proof](R2_VALID_NONMANIFOLD_BREP.md)
- [Generated exact analytic BP fixture](fixtures/four_sheet_planar.bp)
- [Builder](probes/build_analytic_bp.py) (standard library plus imported R2 graph validator).
- [Independent evaluator and optional native Open CASCADE comparison](probes/audit_analytic_bp.py).
- [Adversarial tests](probes/test_analytic_bp.py).
- [Scientific visual gallery](gallery/README.md).

From the repository root, with CadQuery/OCP installed:

    python docs/research/nonmanifold-benchmark/probes/interface_graph_probe.py --output build/research-r3/graph.json
    python docs/research/nonmanifold-benchmark/probes/nonmanifold_sewing_probe.py --interface-graph build/research-r3/graph.json --output-json build/research-r3/sewn_report.json --output-brep build/research-r3/source_control.brep
    python docs/research/nonmanifold-benchmark/probes/build_analytic_bp.py --graph build/research-r3/graph.json --out-bp build/research-r3/four_sheet_planar.bp --out-sidecar build/research-r3/four_sheet_planar.sidecar.json
    python docs/research/nonmanifold-benchmark/probes/audit_analytic_bp.py --bp build/research-r3/four_sheet_planar.bp --sidecar build/research-r3/four_sheet_planar.sidecar.json --native-brep build/research-r3/source_control.brep
    python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v

A non-native audit without --native-brep checks the analytic BP and sidecar but does NOT prove conformity with the R2 kernel BRep control. Do not count that weaker mode as full R3 control qualification.

## Local measured evidence

- Python 3.13.5, CadQuery 2.8.0, OCP 7.9.3.1.
- 13/13 newly added R3 positive/negative tests passed; 32/32 combined R2 native/JSON and R3 tests passed locally using exact test files. These exclude the earlier separate STEP structural parser suite and any APMesh repository-wide tests.
- BP: 52 v records, 4 p records, 16 zero-based references per patch; local shared-side control IDs 0,1,2,3 exactly repeated across 4 patches; sidecar shared-curve incidence 4 and 13 distinct curves.
- Independent de Casteljau evaluation of 49 parameter samples per patch (196 total) found maximum absolute coordinate error **2.220446049250313e-16**, within the declared **2e-12 evaluation-screen budget**.
- 25 strictly interior samples per patch were compared to the corresponding native constructed BRep face using BRepExtrema_DistShapeShape; maximum measured distance was **0.0** in this run, under a **1e-9 local geometry-screen budget**.
- The two chosen screen budgets are numerical verification thresholds for this analytic pilot, not a modification of APMesh input, meshing or scientific accuracy policy.
- BP and sidecar reproduced byte-identically in two runs. Raw BP SHA-256: **b4a80203a5202b08a4a64f3be10fe2c8f3da6633dc30f176c19584bde563875d**; sidecar SHA-256: **e25e787ebb7a62e0fcfbdfd7466a8397ffbf6b651638224299036c7b7238ed75**. Native R2 BRep input SHA-256: **10754c555cd43dc1d069bfc33a52b731dfacb37ec533ef1060bde309a26a8a99**.
- Negative controls reject out-of-range BP references, nonfinite coordinates, incomplete patch records, modified shared indices, a perturbed control net even after recomputing the hash, duplicate source-face provenance, false G2 approval, corrupted curve ID and invalid source-interface graph.
- Git blob identity of locally executed code and fixture was compared to staged remote Git tree before commit: builder cccbe97209f3f592dc4e05e162e0ff556d1d3550, auditor fe70ea2d9f90f8c3e0df812c910875a345e205a6, test 10f5fb77cca5ce0f3a4f0ecc48177445df71b041, BP a9a6d9c9178c50e71c182f94e5b92040087ed9d9.

## Limits / decisions

R3 **one controlled planar case passed**, but R3 full proposed *8-12 model pilot set* is not complete; curved, trimmed, non-four-sided, partial overlap, negative/near-coincident controls and per-file rights remain OPEN. Numerical sampling does not certify continuous error for arbitrary CAD.

This is a small **bounded proof of indexed BP representation** and shared boundary identity; not an APMesh LoaderBezierPatchFile integration test, not evidence of successful accepted TRI generation, not a production R4 converter and not scientific validation of QUAD/all-quad/anisotropy. No external G1/G2 rights/topology admission has changed; all 40 candidates remain DISCOVERED. Keep Stage 3 and QUAD PRs independent.

## Next hard gate

R3: define and test curved canonical shared boundaries with independent analytic/original CAD geometry error and potential trim/splitting rejection. R4: design a general-purpose source -> sheet graph -> oriented curve matching -> four-sided bicubic patch writer with strict unsupported-case diagnostics. R5: **only after** admitted model and qualified exact-image local historical regressions, execute the existing frozen TRI generator, accepted/rejected stage trace and independent boundary incidence checker. No merge until suitable research review and required branch qualification.
