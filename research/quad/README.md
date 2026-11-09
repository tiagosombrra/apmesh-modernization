# Isolated UV QUAD prototype

This C++17 prototype generates real four-node planar elements from a conforming
polygon disk. It has no dependency on `Face`, `TriangleAdaptive`, Eigen or the
production application. All ownership is by value; connectivity uses stable
vertex indices. The current TRI executable and its build remain unchanged.

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

Next integration work is the approved point-selection policy and historical
oracle completion, followed by mapping real quadtree leaves into this UV mesh.
Physical QUAD elements, XYZ mapping/curvature, boundary completion, multipatch
synchronization and repeated adaptation remain later milestones. This library
is not yet selected by the application CLI and is not a complete patch mesher.
