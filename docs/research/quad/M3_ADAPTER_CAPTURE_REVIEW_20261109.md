# M3-3 design — value-owned QUAD UV capture at real adapter patch sites (2026-11-09)

**Status:** source-backed integration review only. No M3-3 production implementation, approved point policy, physical QUAD or additional test result is claimed by this file.

## Verified call sites

1. `src/adapter/adapter.cpp` `Adapter::AdaptDomainOmp` starts near line 894. It constructs `AdvancingFront avanco` near line 903, calls `ConfigureAdvancingFront(avanco)` near line 904, configures the quadtree and its depth cap, then invokes `avanco.execute(mesh_old)` near line 1038. Output is later inspected as a TRI `FaceList`.
2. The retry-aware `Adapter::AdaptDomain` starts near line 1258. Its nested `run_attempt(..., local_attempt)` constructs another `AdvancingFront` near line 1291, calls the same `ConfigureAdvancingFront` near line 1293, configures a per-attempt quadtree cap, then calls `avanco.execute(mesh_old)` near line 1393. After that, it computes generated quality/transition data and decides whether the attempt should be accepted or retried.
3. `Adapter::ConfigureAdvancingFront`, near line 1719, is the shared configuration seam. It already sets AFT postprocess settings and historical `USE_TEMPLATE`. It does **not** register the new `SetRefinedQuadtreeObserver` by default.
4. PR #187 supplies `SetRefinedQuadtreeObserver` in the AFT class. The synchronous callback runs after successful neighbor refinement and before TRI template publication. Without a callback all existing paths remain unchanged.

Line numbers are navigation aids for the observed research HEAD; search symbols if later edits move them.

## Candidate M3-3 implementation contract

- Introduce an explicit **non-default, observer-only** configuration of the adapter's patch execution, independent of historical `USE_TEMPLATE` and distinct from the presently fail-closed production `MESH_ELEMENT_KIND=quad_uv` option. Do **not** make the CLI pretend it emits QUAD while point, boundary and XYZ contracts remain unsettled.
- The callback may call `CaptureLeafPolygons(tree)` only during the borrow. Store a **value-owned `LeafPolygonMesh`** (vertices, polygon index cycles, origin metadata and counts) and never retain `Quadtree*`, `QuadtreeCell*`, raw `Face*` or references to active AFT lists. Do not silently modify tree order, neighbors, geometry or statistics.
- Thread/attempt boundaries: associate captures with `patch_index`, `adaptive_step`, `retry_index`, and (on the retry-aware path) `local_attempt`. Keep attempted captures separate from accepted mesh publication and do not overwrite the provenance of a rejected candidate. A successful read-only capture must not influence local retry selection, geometry or termination.
- An unsupported/no-interior/malformed tree must return an explicit **experimental-capture** failure or absence, never a fabricated complete patch and never a false TRI failure. State whether that absence is expected, and test it. If the observer raises, preserve strong lifetime cleanup and avoid masking the original generation error.
- Avoid global callback registries and hidden mutable state in OpenMP/serial paths. Prefer scoped callbacks bound to the current adapter/generation request; one callback invocation must not leak into another patch or retry. Real compile+sanitizer qualification remains mandatory for new observers.
- Start with a debug-only, bounded research fixture using the existing Eistute/Book inputs to verify provenance and counts without changing accepted/rejected TRI traces, output OBJ or serialized state. Existing QUAD native tests, 75 CTest, 527 Python, strict Eistute/Book reference comparison and negative/error paths remain admission gates.
- **Scientific stop condition:** captured UV polygons do not constitute a physical quad mesh. Do not choose a numerical interior point from the synthetic demo. Do not emit a complete patch, curved XYZ quads or synchronized shared-curve multipatch results until their independent M1/M4/M5/M6 gates are approved and tested.

## Important API limitation

The current AFT callback receives mutable legacy `Quadtree&` even though the intended operation is observation-only. This contract is tested for existing code but is not enforced by C++ constness. An improvement under M3-3 is to restrict the consumer to a value-owned snapshot or another genuinely immutable view after the synchronous capture, without exposing writable tree pointers outside the callback. Do not claim compile-time read-only enforcement until implemented.

## Research branch and evidence

- M3-2 PR: [#187](https://github.com/tiagosombrra/apmesh-modernization/pull/187)
- M3-2 exact-head passing CI: [#42689321763](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42689321763)
- M3-2 post-merge CI: [#42690813905](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42690813905)
- M3-1: PR #186, fail-closed default TRI selection.
- No mutation of the modernization `main` and no implied completion of M1/M2/M3/M4/M5/M6/M7.
