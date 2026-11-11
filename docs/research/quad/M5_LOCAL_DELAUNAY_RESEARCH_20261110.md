# M5 research-only constrained locally Delaunay exterior test — 2026-11-10

**Historical status: NOT reproduced.** This is an additional checked geometric research prototype on the same actual C++ 19-leaf Quadtree, not production QUAD, not the 1993 Delaunay point-insertion / contour-contraction algorithm and not a physical UV-to-XYZ mesh.

## Input provenance

The existing native `quad_tree_visual_export` C++ executable produces the fixed real-Quadtree 19-leaf snapshot: seven QUAD candidate cells and twelve external cells; 42 QUAD UV elements occupying 0.25 of the unit domain. The already qualified M5 center-fan test produces 60 external TRI and records a 20-edge matching seam, unit area and four negative mutations. This test runs **after** those two exact provenance gates and reads their actual OBJ and CSV outputs, not an independently invented set of QUAD coordinates.

## Candidate algorithm (not claimed historical)

1. Recover all source C++ QUAD vertex IDs and quadtree leaf corners without changing the 53 existing vertex coordinates or 42 four-node faces.
2. Split each exterior leaf perimeter at every collinear neighboring edge vertex. Ear-clip each convex polygon retaining all split boundary vertices, yielding 36 external TRI and 69 UV vertices overall.
3. Treat the 20-edge QUAD/TRI interface plus 16 outer domain edges as constrained edges. Deterministically optimize flippable unconstrained TRI diagonals using exact-rational incircle and CCW orientation predicates with Lawson flips. **Eight** positive flips occur in the frozen fixture, and **24** flippable internal edges pass the final local Delaunay condition for each independent center-point rule.
4. Audit the full mixed disk: 42 source QUAD + 36 research TRI, positive area, 0.25+0.75=1 total, no duplicate/orphan vertices, consistent shared winding, 20-edge connected closed seam, 16 domain edges, Euler V-E+F=1, no hanging vertices and five deliberate malformed mutations.
5. Produce two OBJ files, comparative SVG and JSON receipt in the native CTest artifact. The exported actual C++ QUAD face IDs remain unchanged. Preserve both explicit unapproved center-point alternatives separately.

A deterministic angle-based local comparison improves the smallest TRI corner angle from approximately **8.130102°** after ear clipping to **12.528808°** after eight flips. The earlier center-fan had 60 TRI; this new prototype has 36 without artificial leaf-center nodes. These are one fixed normalized UV geometry and a constrained **local** Delaunay property, **not** proof of historical boundary-contraction fidelity, physical element quality, unrestricted robust geometry or convergence.

## Historical source gap / application boundary

The 1993 article specifies exterior Delaunay triangulation and contour contraction. The current APMesh legacy source `src/crab_mesh/aft/advancing_front.cpp` uses a front-based mesh construction with `makeInitialFront`, `findBestVertex` and `makeMesh` methods; being an advancing front does **not** establish that it implements the article's Delaunay / contraction algorithm. The 1987 Baehmann text and the numerical centroid/degenerate region rules are still awaiting research verification and Bento/Creto's approval.

The user-approved sequence remains **historical_hybrid_1993 first**, then **all_quad_extension** as a separately selectable extension. Both options remain architecture proposals, not available production CLI modes. The `main` and current TRI default are preserved.

## Reproducibility and acceptance

Run `ctest --test-dir build/quad-ci-linux --output-on-failure` with `AP_MESH_QUAD_WITH_TREE=ON`; the new `quad.m5.local_constrained_delaunay` depends on the existing M5 fan exporter. Read generated `real_tree_visual/hybrid_research_local_delaunay_{vertex_mean,area_centroid}.obj`, `research_local_delaunay_comparison.svg` and `research_local_delaunay_manifest.json`. The full Linux GCC and Windows MSVC native CTests, full TRI 78 CTest/527 Python/7 CLI denials and frozen Eistute/Book exact parity remain mandatory before research-branch merge. Production main and default TRI must remain unchanged.

**Next scientific gate:** independently verify 1993 point insertion, constraint construction and contour contraction against source text and advisers. Then compare geometric/physical quality on actual model boundaries; only after historical-hybrid acceptance should the all-QUAD extension be implemented.
