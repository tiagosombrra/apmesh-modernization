# R2.E1 — Direct inspection of seven original complex HexMe/MAMBO STEP sources

**Performed:** 2026-11-15; **source of inspected text:** connected GitHub repository files `cgg-bern/hex-me-if-you-can` pinned at commit `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
**Scope:** parse the exact upstream STEP entity text through GitHub connector, count distinct ADVANCED_FACE entities per explicitly referenced EDGE_CURVE through FACE_BOUND / EDGE_LOOP / ORIENTED_EDGE. This is a **static source-text screen**, **not** native Open CASCADE import, source-image rendering, geometric contact detection, free-edge/watertight proof or external model admission.

| Original STEP model (HexMe) | Original file bytes* | Git blob SHA-1 | Faces | Edge curves | Distinct face users per edge: 1 / 2 / >=3 | Native CAD support-surface entities |
|---|---:|---|---:|---:|---|---|
| `i01o_m1.step` | 176092 | `f0738514abc86cb0de9875bba500b7a005a54068` | 42 | 114 | 0 / 114 / 0 | 30 revolution, 12 plane |
| `i03o_m3.step` | 245700 | `e472dd5b717b2fdbc7d2bd3e030a856a257d0cb3` | 60 | 169 | 10 / 159 / 0 | 34 plane, 26 cylinder |
| `i05o_m5.step` | 276412 | `d72e5e3cb3de9ebdec80253cfa9b57fa1b7132f7` | 41 | 102 | 23 / 79 / 0 | 13 plane, 17 cylinder, 10 cone, 1 torus |
| `i15o_s8.step` | 125386 | `48f3f1f74ea25baa93d88dbe736f24e8e42836d8` | 34 | 94 | 3 / 91 / 0 | 26 plane, 8 cylinder |
| `i22o_s27.step` | 177702 | `48ada34a4d2fb038ff91131300c6262a9faec217` | 52 | 144 | 0 / 144 / 0 | 34 plane, 18 cylinder |
| `i25o_s40.step` | 216438 | `917ef72a0a91b8b3e7d16e8009a1b1655154174a` | 43 | 117 | 0 / 117 / 0 | 26 plane, 14 cylinder, 2 B-spline with knots |
| `n10o_qtorus_cyl.step` | 160441 | `08e16cb29f491cce88a6aaa0e881c668257bf940` | 12 | 33 | 21 / 12 / 0 | 6 plane, 3 cylinder, 3 torus |

*The bytes are the **upstream GitHub contents API reported file sizes**, not a locally downloaded artifact measurement. Git blob SHA-1 is **not** the SHA-256 of raw source bytes. Original file downloads and hashes remain open.

For all seven, the bounded reference traversal resolved all FACE_BOUND/EDGE_LOOP/ORIENTED_EDGE references and every explicit EDGE_CURVE was used at least once. `i03o_m3` has 10 repeated edge uses within individual face loops, M5 23, S8 3 and Quarter Torus 9. These repeats are **not** multiple distinct incident faces. Their native seam/periodic geometrical significance needs independent kernel inspection.

All six industrial MAMBO originals expose one `MANIFOLD_SOLID_BREP` and one `CLOSED_SHELL` entity. Quarter Torus additionally contains four `OPEN_SHELL`, two `CLOSED_SHELL` and five `SHELL_BASED_SURFACE_MODEL` entities across STEP representations, so its entity counts cannot be naively treated as one valid sewn shape.

**Source metadata directly confirmed:** all six named MAMBO industrial source files and Quarter Torus declare **Apache-2.0** in their per-file HexMe YAML. A license declaration is not yet a reviewed rights/redistribution approval. The GrabCAD Turbo, Tire and Alcoa Bracket examples declare **GrabCAD Terms**, and DLR-F6 declares **Unknown - AIAA-DPW/DLR**: rights gate BLOCKED.

## Scientific interpretation (negative evidence must be retained)

- **Zero** of the screened source STEP edge IDs is explicitly used by 3+ distinct ADVANCED_FACE entities. **This is not proof that the complete geometry is manifold**, since different edge IDs can represent coincident curves, and STEP entities may represent multiple shape structures. It is a reason not to promote these seven original files to external multi-sheet positives.
- More surface faces and intricate CAD geometry do **not** imply 3+-sheet junctions. These models are a **geometric-generalization cohort** (high curvature, B-splines, feature density), not an already admitted **non-manifold generalization** cohort.
- Cylinders, cones, toroids and rational/NURBS entities cannot in general be represented exactly by one polynomial bicubic Bézier net under ordinary nondegenerate parameterization. Approximate fitting with **predeclared error** and feature identity, or bounded subdivision, must be evaluated; never relabel a sample mismatch as exact.
- HexMe publishes **volumetric tetrahedral** meshes with CAD feature tags and three tet-meshing policies. Their tetrahedral cells cannot be compared directly to our surface TRI/QUAD quality without a shared evaluation domain. The CAD source topology and tagged *feature preservation* may be useful independent reference information. See Beaufort et al., *Hex Me If You Can*, Computer Graphics Forum 2022, DOI `10.1111/cgf.14608`.

## Reproducibility of the screen

Local independent research script added: `probes/step_graph_screen.py`; standard library only. It takes permitted local STEP source files, computes **actual local raw SHA-256**, and emits the same scoped entity counts and warnings. Six local synthetic reference-graph tests passed in `probes/test_step_graph_screen.py`, including genuine 3-face identity, coincident separate IDs, repeated single-face uses, invalid header, duplicate entity ID and unsupported vertex loops.

    python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_step_graph_screen.py' -v
    python docs/research/nonmanifold-benchmark/probes/step_graph_screen.py path/to/licensed/original/i05o_m5.step --output build/research-industrial/m5.json

**Reproduction gate not yet executed:** the seven original CAD bytes have not been materialized in the local runtime, so the newly committed Python analyzer has been run only on synthetic tests; it has **not** been run against the seven original files. The seven source-file counts in this report came from the connected GitHub files and a separate reference graph traversal on their text. Native OCC imports, visualizations, bounding boxes, full semantic topology checks and raw model SHA-256 are **NOT RUN**. This must not be silently upgraded to a final G2 decision.

## Next concrete source-specific inspections

1. **MAMBO M5:** native STEP import and render full CAD; classify each of the 41 original faces and 102 edges by curve type, seam, loop, local parameterization and feature tolerance. Attempt bounded four-sided decomposition of a representative toroidal/conical/cylindrical face with an independent geometric error measurement; document failure too.
2. **MAMBO S40:** inspect the two B-spline surfaces' degrees, knots and trims, degree reduction/fitting budgets and four-sided topology. No assumption that B-spline is itself polynomial bicubic.
3. **MAMBO S27:** feature-density and open-loop/orientation/face adjacency test on its 52 faces, plus feature-curve graph for eventual QUAD/TRI comparison.
4. **MAMBO M3:** native classification of the ten one-face-use edges and possible seam geometry, then controlled decomposition pilot.
5. **Independent external non-manifold source:** keep the positive benchmark search separate; do not generate external positives by unconstrained tolerance-based welding.

**Disposition:** R1 v2 cohort identified; R2 original STEP **static** data for seven assets recorded; R2 CAD-kernel/source-identity review OPEN; full R3/R4/R5 and paper generalization BLOCKED pending evidence. See `SCIENTIFIC_MODEL_SELECTION_V2.md`.
