# Isolated UV QUAD prototype

This C++17 prototype generates real four-node planar elements from a conforming
polygon disk. Its core UV library has no dependency on `Face`, `TriangleAdaptive`,
Eigen or the production application. The optional tree bridge below links the
existing legacy component. UV mesh ownership is by value; connectivity uses
stable vertex indices. The current TRI executable and its build remain unchanged.

`Subdivide` takes polygon connectivity and **one explicit interior point per
polygon**. It creates an edge midpoint once per canonical endpoint-ID pair,
reuses that index across adjacent polygons and emits one quadrilateral per
original corner. It validates the complete local result before returning it;
exceptions leave the input unchanged. A point strictly inside a polygon may
still produce a concave quad and is rejected by the output validator.

There is no default centroid computation. The caller supplies the chosen point,
so adopting a numerical centroid definition remains an explicit scientific
decision. Figure 7 connectivity is exercised with injected positive test points,
not presented as a historical numerical coordinate oracle.

## Build and run

From the repository root in a configured GCC/Ninja environment:

```sh
cmake -S tests/quad -B build/quad-uv -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/quad-uv --parallel 2
ctest --test-dir build/quad-uv --output-on-failure --stop-on-failure --no-tests=error
build/quad-uv/quad_uv_demo build/quad-uv/two-cells.obj
```

With checked MSVC:

```powershell
cmake -S tests/quad -B build/quad-uv-msvc -G "Visual Studio 17 2022" -A x64
cmake --build build/quad-uv-msvc --config Debug --parallel 2
ctest --test-dir build/quad-uv-msvc -C Debug --output-on-failure --stop-on-failure --no-tests=error
build/quad-uv-msvc/Debug/quad_uv_demo.exe build/quad-uv-msvc/two-cells.obj
```

The demo subdivides two adjacent squares into **8 quads /15 vertices**, area 2,
12 boundary edges and 10 interior edges. Its shared side uses the same vertex
IDs on both cells. Output is standard OBJ with UV represented as XY, Z=0 and
four indices per face; no triangle writer or hidden triangulation is used.
The demo refuses an existing output path. Use a new filename for another run.

## Validator contract and scope

`Validate` checks finite UVs, valid/nonrepeated indices, unique coordinate-to-ID
correspondence, strict convexity/CCW orientation, opposite shared-edge
incidences, at most two incident faces, no hanging nodes, crossings, overlaps or
unused vertices, manifold boundary vertices, connectedness, disk Euler
characteristic and independently supplied expected area. Coincident IDs are
rejected rather than welded by coordinates. Holes/disconnected domains are
deliberately outside this initial disk API.

The research tolerance is explicit and relative to the squared domain extent;
it does not replace any production acceptance tolerance. This implementation
uses exhaustive geometric comparisons for small research fixtures, not a
production spatial index or adaptive exact predicates. Allocation failure
campaigns, extreme-coordinate robustness and complete-process memory safety
are not qualified by ordinary contract tests.

The standalone native suite includes all six transcribed pattern graphs under
48 rotations/reflections, analytic square connectivity/areas, a 19-quad 2:1
transition, ID permutation/scaling/translation, 32 bounded grids, invalid
geometry/topology, failure/input preservation and OBJ precision/I/O controls.
These are separate from the production 75 CTest /527 Python baseline.

## Read-only bridge to the existing quadtree

`quadtree_quad.h/.cpp` now captures actual `QuadtreeCell` leaves and their
reciprocal neighbor lists. It classifies all 16 split-side signatures into
T1-T6, rotates the recorded polygon graphs and assigns shared vertex IDs from
the root's dyadic hierarchy. It preserves the source leaf order and existing
empty-neighbor boundary exclusion, and does not sort, refine or publish TRI
objects in the source tree. Invalid/nonreciprocal or unbalanced trees fail
explicitly. Relative depth above 30 is outside this first bridge contract.

`CaptureLeafPolygons(tree)` returns ordered polygons and value-only source
metadata. Its `interior_points` is deliberately empty. `EmitLeafQuads(tree,
selector)` asks the caller for one point per polygon, uses `Subdivide` and
checks output coverage against the sum of the included leaf rectangles. The
captured source has no retained tree/cell pointers. Selector references are
valid only during the callback; the callback must not mutate the source tree.

Enable the standalone bridge and its actual legacy component:

```sh
cmake -S tests/quad -B build/quad-tree -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAP_MESH_QUAD_WITH_TREE=ON
cmake --build build/quad-tree --parallel 2
ctest --test-dir build/quad-tree --output-on-failure --stop-on-failure --no-tests=error
build/quad-tree/quad_tree_demo build/quad-tree/adaptive-tree.obj
```

The adaptive demo constructs the existing quadtree through its public API,
with a closed unit-square boundary, subdivides one actual interior leaf and
emits **42 quads** from a **19-leaf** tree. The included interior area is 1/4;
the excluded boundary leaves are not filled. The demo explicitly injects
vertex-mean points as synthetic test data, not an application centroid policy.
MSVC supports the same option using the generator/configuration above.

The extra native suite checks 30 bridge outcomes: actual uniform/adaptive trees,
all 16 masks, unchanged existing TRI owners/geometry/stats, unchanged list order,
selector failures and malformed/unbalanced neighbor graphs. The original 117
UV outcomes remain a separate unchanged test entry. Legacy-component warnings
remain visible; no production source, diagnostic or historical oracle is changed.

Next integration work is the approved point-selection policy and historical
oracle completion, followed by an opt-in call from the application pipeline.
Physical QUAD elements, XYZ mapping/curvature, boundary completion, multipatch
synchronization and repeated adaptation remain later milestones. This library
is not yet selected by the application CLI and is not a complete patch mesher.

## R1 research-only template mode selection (2026-11-11)

`interior_template_dispatch.h/.cpp` adds a **per-attempt** choice on the **same
actual refined Quadtree**: `LegacyTri` calls the existing
`Quadtree::makeTemplateBasedMesh()` once; `ExperimentalQuad` calls
`EmitLeafQuads()` with an explicit caller-selected numerical interior-point
rule and produces an **owned, value-only UV mesh**. In QUAD mode it does not
publish any TRI faces, edges or vertices in the legacy tree, and rejects a
tree whose legacy TRI templates are already published. The caller cannot
choose a second mode in the same dispatcher session.

The experimental result retains a **one-to-one original source cell, T1–T6 pattern, source leaf ordinal and polygon ordinal per emitted QUAD**, proving that every face can be traced back to an eligible real interior leaf; its ordered provenance is checked against an independent source capture in the native fixture. It also lists the **directed one-owner boundary edges**
of the QUAD region, by the original UV vertex IDs. These are useful as a
future QUAD–TRI front handoff contract, but **are not yet inserted into
`AdvancingFront`**. The research-only result flags remain
`live_aft_interface_published=false` and
`physical_elements_published=false` on both paths. The original CLI
still refuses `MESH_ELEMENT_KIND=quad_uv`; neither historical point rule
has been scientifically approved.

`tests/quad/interior_template_dispatch_contracts.cpp` compares real
uniform and refined Quadtree source trees (16 or 42 experimental QUAD
respectively), 16/20 oriented region boundary segments, a direct reference
TRI template publication, and adversarial/missing-policy/rollback cases.
It runs under `AP_MESH_QUAD_WITH_TREE=ON` on native GCC/Linux and
MSVC/Windows. This is **R1's first isolated selection contract** rather
than completed R2 physical hybrid generation. No production `src/` or
`include/` file is changed.

The next slice must publish the QUAD region in a truly typed intermediate,
seed the **existing exterior TRI AFT** with this same region's boundary,
and avoid double-filling the 0.25 example domain. Then publish real
four-node elements beside exterior TRI in a `SubMesh`; only after that
positive end-to-end gate may the application QUAD CLI be enabled.
