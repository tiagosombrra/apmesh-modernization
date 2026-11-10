# M3: real Quadtree visual evidence (2026-11-10)

The new research-only quad_tree_visual_export executable uses the **actual C++ legacy Quadtree** from the existing TreeFixture, not a Python recreation of its classification. Its center leaf is further refined, producing 19 source leaves: 7 included by the existing neighbor-based QUAD classifier and 12 excluded boundary leaves. The included area is 0.25 UV units squared. Both explicitly experimental center-point rules emit 42 conforming four-node QUAD faces.

The exporter calls CaptureLeafPolygons, EmitLeafQuads, Validate and WriteObj. It saves tree_visual.svg (three labeled runtime panels), tree_regions.csv (actual leaf IDs, levels, bounds, classifier types and region flags), quads_vertex_mean.obj and quads_area_centroid.obj, plus manifest.json. A separate Python test audits the **actual generated outputs**: 19 leaves, 7 interior, 12 excluded, 42 quads, 53 shared UV vertices, positive face areas, Euler disk and boundary incidence, 0 emitted TRI, source classification area and SVG parity.

**CRITICAL:** Excluded boundary leaves have not been triangulated. Their rendering in pink cannot be called a Delaunay result. There is no physical UV-to-XYZ, completed historical hybrid mesh or production all-quad mode in this change. The chosen centroid rule remains a *test-only* explicit witness and is not historically approved.

With AP_MESH_QUAD_WITH_TREE=ON, the standalone native suite increases from 8 to 10 CTest entries. Linux GitHub Actions archives a runtime SVG, two OBJ, CSV and manifest as quad-real-tree-visual-SHA with a 14-day retention. This provides a provenance-backed image for visual validation, instead of relying exclusively on source-derived diagrams.

Usage:

    cmake -S tests/quad -B build/quad-visual -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAP_MESH_QUAD_WITH_TREE=ON
    cmake --build build/quad-visual --parallel 2
    ctest --test-dir build/quad-visual --output-on-failure --no-tests=error

Inspect build/quad-visual/real_tree_visual/tree_visual.svg and both OBJ files in ParaView, Blender or a browser. The actual patch is a controlled square fixture, not the physical Eistute/Book models. Next scientific step is historical exterior Delaunay triangulation and contour contraction with explicit seam verification, **before** an optional selectable all-QUAD extension. Production TRI defaults remain unchanged.
