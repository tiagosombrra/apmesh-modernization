# QUAD visualization and two selectable research modes — 2026-11-10

## User-selected sequence

1. **historical_hybrid_1993**: faithfully reproduce the original method, combining quadrilateral patterns in interior quadtree cells with exterior Delaunay triangulation and contour contraction. The published method is not guaranteed to be a full-domain all-quad technique.
2. **all_quad_extension**: subsequently build an optional conforming full-QUAD extension, including boundary treatment and physical UV-to-XYZ mapping. This is new research and **not** the historical method.

Both labels are **design names only**, not working runtime CLI flags. Do not change the TRI default, enable positive `quad_uv` in production, or select an unapproved centroid formula.

## Existing real C++ UV meshes

The test-only `quad_visual_export` executable links the existing `apmesh_quad_uv` and `apmesh_quad_experimental_point` C++ libraries and calls **actual `Subdivide`, `Validate`, and `WriteObj`**. It emits 12 portable OBJ snapshots, for the six proposed Figure 7 patterns T1,T2,T4,T3,T5,T6 (four, eleven, twelve, eight, eleven, sixteen quads) using the two explicitly named, unapproved interior-point witnesses. These are **parametric UV** (OBJ XY, Z=0), not physical elements of Eistute or Book. It is invoked by standalone `quad.m1.visual_obj_export` CTest. Native test count rises from 7 to 8.

To reproduce locally:

```bash
cmake -S tests/quad -B build/quad-visual -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/quad-visual --parallel 2
ctest --test-dir build/quad-visual --output-on-failure --no-tests=error
# Open the 12 OBJ files in build/quad-visual/visual_uv_objs/ with ParaView or Blender.
```

For rapid human visual comparison, [Figure 7 UV template gallery](figures/M1_UV_6_PATTERNS_20261110.svg) depicts the original six schematic polygon graphs and their subdivisions under both rules. **This SVG is an independent geometry rendering**, not a trace of compiled C++; the 12 C++ export OBJs are the execution evidence. A separate ChatGPT offline HTML/PNG/OBJ gallery is provided in the companion session.

## Scientific visual review gates

- M1: compare each schematic graph against the printed Figure 7, verify vertex and shared-edge identities, full unit-area coverage, four corners per face and positive orientation for the UV experiments. This validates bounded **local prototypes**, not complete mesh generation.
- Historical hybrid 1993: later show the **actual application** quadtree, interior QUAD cells, external TRI cells, contour contraction and real boundary. The paper's Figure 8 is historical reference only, not current APMesh output. This step remains **not implemented**.
- All-QUAD extension: only after the historical mode, display the **same physical model** with zero triangles and compare geometric boundary conformity and element quality. This mode remains **not implemented**.
- Both modes: demand UV/XYZ distinction, scientific point-rule review, deterministic exports, quality diagnostics, memory ownership/rollback and native TRI regression.

The original 1993 PDF SHA-256 and Figure 7 were verified in PR #197. The polygon centroid equation is still awaiting adviser review. Avoid labeling any research witness as definitive historical centroid.
