# M3 opt-in application dispatch — integration design and first gate (2026-11-09)

**Status:** architectural review only; not yet code or tests. Main and default TRI path remain unchanged.

## Verified integration sites

- `src/main.cpp` calls `apmesh::application::RunApplication` in `src/application/run_application.cpp`.
- `RunApplication` currently accepts `ap_mesh --config CONFIG`, calls `LoadRuntimeConfig`, `ApplyRuntimeConfig`, `MakeGenerationContext`, and then `GeneratorAdaptive::Execute`. Changes to the default CLI transcript and accepted syntax would affect frozen scientific comparisons.
- `RuntimeConfig` and `LoadRuntimeConfig` are in `include/application/runtime_config.h` / `src/application/runtime_config.cpp`. `apmesh::io::ValidateConfigValue` in `include/input_output/input_validation.h` rejects unknown keys, so adding a new option requires deliberate parser and negative-input tests. `USE_TEMPLATE` presently selects a historical template behavior (`y/n`) and **must not be repurposed** to choose TRI versus QUAD.
- `GeneratorAdaptive` owns the adaptive execution lifecycle. Existing `AdvancingFront` has `getQuadtree()` and constructs/refines the legacy tree before the TRI template/AFT path in `src/crab_mesh/aft/advancing_front.cpp`. Its source quadtree has nontrivial ownership, so the experimental call must be observation-only and have bounded lifetime.
- The integrated `research/quad/quadtree_quad.h` exposes `CaptureLeafPolygons(Quadtree&)` and `EmitLeafQuads(Quadtree&, PolygonPointSelector)`; the point selector is **mandatory**. `research/quad/tree_demo.cpp` uses a synthetic vertex mean only in a test fixture; it is not an approved scientific centroid and cannot silently become the default production method.

## Next implementation slice (M3-1)

1. Add a **strictly separate, opt-in research mode** for UV QUAD inspection; the existing `--config` TRI invocation without an experimental selector must take the identical production control flow and emit byte-identical references.
2. Select TRI/QUAD orthogonally to `USE_TEMPLATE`, and fail closed on unknown flags/values or missing point policies. Avoid adding `research/quad/*.cpp` to the default production source glob, and never use synthetic vertex means as a scientific default.
3. For a real generated patch, capture the non-mutated `Quadtree` at a deterministic lifecycle checkpoint before owner transfers/free; invoke the integrated bridge with a caller-approved explicit interior-point callback and value-owned UV result. Preserve existing TRI publication and rollback semantics; do not return raw tree pointers.
4. Store experimental interior-only UV output explicitly marked as **partial** and separate from regular article outputs. Its current single-disk convexity requirement and excluded boundary cells must be checked rather than hidden. No 3D output is represented as physical four-node elements.
5. Add positive/negative tests for default TRI unchanged, opt-in selection, unknown/missing policy rejection, 2:1 leaf conforming connectivity, no source mutations after success/exception, and output refusal for invalid/incomplete domains.
6. Require Linux/MSVC compile, standalone two-entry QUAD contracts, the existing 75 CTest/527 Python controls, and frozen Eistute/Book acceptance, OBJ and boundary comparisons on the **exact implementation commit**. Preserve first-failure logs and run separate memory/provenance checks for new owners/borrowed observers.

## Explicit scientific gate

There is no approved default `PolygonPointSelector` in the checked-in research code. The numerical interior-point formula, admissible polygon set and tolerance/degeneracy handling require independently documented scientific choice/validation. M3-1 may implement a mechanically validated selector/dispatch surface **without issuing QUAD elements as scientifically approved output** until that choice is confirmed. Do not conflate old paper graph pattern agreement with numeric centroid acceptance.

## Evidence and boundaries

- [Post-merge exact-head CI receipt](POSTMERGE_CI_20261109.md): existing UV bridge and TRI invariance passed.
- `main` is out of scope; new implementation must occur on a small feature branch targeting `quad-templates` with its own PR.
- M1 historical numeric oracle PARTIAL; M2 topology PARTIAL; M3 application opt-in not yet implemented; M4 physical XYZ, M5 full boundary, M6 shared-curve multipatch and M7 adaptation remain pending.
