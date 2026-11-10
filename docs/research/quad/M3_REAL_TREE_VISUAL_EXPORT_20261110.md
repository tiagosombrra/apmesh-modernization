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

## CI and merge receipt

[PR #199](https://github.com/tiagosombrra/apmesh-modernization/pull/199) merged into research at `799dd62f7e3dd9145fcc120c5c6daae09c8e01bb` with exact candidate-tree equivalence. [Premerge #42892551246](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42892551246) SUCCESS (GCC/MSVC 10/10 native each, full TRI 78/78, Python 527, CLI 7, strict frozen Eistute/Book reference). [Real binary SVG/OBJ/CSV/JSON artifact #13798922455](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42892551246/artifacts/13798922455) retained 14 days and reproducible from source. [Post-merge #42894221887](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887) in_progress at checkpoint. The 12 outer leaves have **no generated TRI**. [Audit evidence](evidence/M3_REAL_TREE_VISUAL_20261110.json).

## Independent exact-merge verification closed

After the PR #199 integration, the separately triggered [CI #42894221887](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887) finished **SUCCESS** on `799dd62f7e3dd9145fcc120c5c6daae09c8e01bb`: native Linux/Windows 10/10 each, TRI 78/78 CTest, Python 527, seven CLI negatives, Eistute 5 / Book 4 strict scientific equivalence. The [post-merge actual C++ visual artifact #13798814198](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42894221887/artifacts/13798814198) is the preferred review asset (14-day retention). The already recorded initially pending status is a historical checkpoint, not a remaining blocker.
