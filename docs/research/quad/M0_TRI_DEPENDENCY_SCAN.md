# M0 targeted TRI-only dependency scan

**Date:** 2026-11-08  
**Frozen source ref:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`  
**Method:** GitHub Git-tree inventory and exact read-only source-file inspection. Counts below are lexical occurrences of specified tokens in the selected files; this is **not** a whole-repository call-graph proof or a runtime test. No production code modified.

## Tree coverage

- The recursive Git tree returned **2,589 entries**, `truncated=false`.
- **164** C++ files under `src/` and `include/` matching `.cpp/.cc/.cxx/.h/.hpp`: 76 C++ implementation units and 88 headers. These are a current file-name census, not an assertion that all 164 files are compiled in the serial target.
- A **targeted sample of 15 existing** high-risk files was read and searched; one attempted `src/adapter/domain_uv_cache.cpp` path was absent (the header `include/adapter/domain_uv_cache.h` exists). The resulting sample is incomplete by design.
- Important limitation: the old architecture inventory’s historical file counts are not substituted for this current tree; generated/probe/parallel caller closure requires separate analysis.

## Selected source occurrences

| File | `TriangleAdaptive` mentions | Explicit pointer/reference TRI casts | `FaceList` / `Face*` | Relevant observation |
| --- | ---: | ---: | ---: | --- |
| `src/crab_mesh/aft/quadtree_cell.cpp` | 0 | 0 | 11 | T1–T6 currently emit triangle `Face` via quadtree patterns |
| `src/crab_mesh/aft/quadtree.cpp` | 0 | 0 | 8 | Tree combines triangulated template faces into AFT path |
| `src/crab_mesh/aft/advancing_front.cpp` | 0 | 0 | 21 | Geometry/topology filling and smoothing assume triangular `Face` |
| `include/crab_mesh/aft/face.h` | 0 | 0 | 2 | Explicit 3-vertex representation |
| `src/adapter/adapter.cpp` | 16 | **10** | 24 | Both previous-mesh UV input and physical output use TRI casts |
| `src/data/triangle_adaptive.cpp` | 24 | 0 | 0 | Node observer lifecycle and 3-node geometry |
| `src/curvature/adjacent.cpp` | 6 | **1** | 0 | Snapshot path casts base `ElementAdaptive` to TRI |
| `src/generator/generator_adaptive.cpp` | 39 | **25** | 0 | Quality, output, curvature/error and mesh accounting hotspots |
| `src/input_output/write_obj_file.cpp` | 2 | **1** | 0 | Separate OBJ writer also assumes triangular elements |
| `include/data/element_adaptive.h` | 0 | 0 | 0 | Base API does not advertise generalized vertex count/UVs |
| `include/data/triangle_adaptive.h` | 12 | 0 | 0 | Three nodes with UV parameters |
| `include/data/mesh/sub_mesh.h` | 1 | 0 | 0 | Polymorphic elements owned by unique pointers, lifetime contract TRI |
| `src/data/mesh/sub_mesh.cpp` | 0 | 0 | 0 | Owner container needs contract-specific proof for QUAD |
| `src/crab_mesh/aft/face.cpp` | 0 | 0 | 2 | Triangle face computation and ownership |
| `src/curvature/curvature_discrete.cpp` | 0 | 0 | 0 | Polymorphic curvature accumulation still needs math audit |

**Important:** In the selected source sample, 37 syntactic TRI pointer/reference casts were found (10 + 1 + 25 + 1). These are **lexical matches, not 37 distinct runtime defects**. Other casts and triangle assumptions in unscanned files remain unknown. `TriangleAdaptive` and `Face` counts are not exhaustive.

## Exact hotspots

- `src/crab_mesh/aft/quadtree_cell.cpp`: `makeMeshType1..6` at lines 342, 474, 539, 657, 788, 857; selection at line 1766. Tree leaves touching `inBoundary()` return before template emission.
- `src/crab_mesh/aft/advancing_front.cpp`: `AdvancingFront::execute` starts around line 1498; filling stage around line 1574.
- `src/adapter/adapter.cpp`: TRI cast sites around lines 991, 1005, 1087–1091, 1357, 1367 and 1464–1468; new `TriangleAdaptive` construction around lines 1081 and 1460.
- `src/curvature/adjacent.cpp`: `static_cast<const TriangleAdaptive&>` at line 8 in the snapshot path.
- `src/generator/generator_adaptive.cpp`: TRI OBJ output around line 7444; TRI quality/shape statistics around line 7779; additional casts around lines 6361–6387.
- `src/input_output/write_obj_file.cpp`: independent triangular writer; do not overlook when adding QUAD output.

## Gate impact

M0-G7 remains **PARTIAL**, not completed: a static token scan does not prove dynamic reachability, full source coverage, scientific preservation or lifecycle safety. The practical integration seam is a separate UV QUAD representation and an explicit opt-in path, **not** a fourth vertex added to the current triangle `Face`.

Before merging a QUAD feature, enumerate and qualify all production consumers of `ElementAdaptive` and `Face`; verify relevant control/call paths and actual native tests. The existing source inventory and modernization gates continue to apply independently.

**Evidence pointers:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md), [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md), [M0_EVIDENCE.md](M0_EVIDENCE.md).

## Session 2026-11-08-04 - expanded production-name scan

The unchanged 164-file `src/include` tree was searched for `TriangleAdaptive` and
explicit static/dynamic/C-style casts. Ten files contain the name; the current
line-based cast query finds **38 occurrences**, adding the checked cast in
`src/input_output/incidence_snapshot.cpp` to the earlier targeted 37. This is
lexical query coverage, not an exhaustive semantic proof of aliases or loops.

Three additional named source responsibilities were inspected:

| Source | Observation | QUAD implication |
| --- | --- | --- |
| `src/generator/initial_mesh.cpp` | Initial submesh construction explicitly creates four TriangleAdaptive elements with three UV slots | Initial-state topology requires its own typed QUAD route |
| `src/estimate/initial_mesh_estimate.cpp` | Initial estimate mesh construction is triangular | Sizing/estimation must retain a justified topology contract |
| `src/input_output/incidence_snapshot.cpp:90` | Dynamic cast rejects non-triangles with `Incidence snapshot requires triangles`; three UV/node slots are serialized | Independent boundary/physical/UV validation export must support QUAD before multipatch claims |

The directory-wide name search closes the missing lexical sample for these
identifiers only. G7 still requires a semantic disposition of reachable serial
consumers and implicit three-node loops, distinguishing topology from physical
XYZ dimensionality. No production change or runtime QUAD compatibility follows.

## Session 2026-11-08-05 - semantic serial disposition

The [reviewed serial contract register](M0_SERIAL_TRI_CONSUMERS.md) and
[machine-readable source/compile receipt](evidence/M0_SERIAL_TRI_REGISTER_20261108.json)
supersede the partial G7 disposition above for the frozen serial entry only.
All 38 named explicit casts have dispositions: 16 selected serial, 17 excluded
by the configured preprocessor and five compiled entries with no selected serial
caller identified. Producer/consumer, implicit three-node loops, ownership,
metrics, curvature and export responsibilities are reviewed separately from
XYZ/cubic/quadtree dimensions. This completes the named M0 static register;
runtime QUAD, arbitrary external/parallel callers and scientific equivalence
remain future milestone gates. Earlier lexical and failed-check records remain
historical evidence, not stronger claims.
