# Mesh Studio — R2.7.1 qualified partial real-P1 XYZ BVH

**Date:** 2026-11-16. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Exact browser-tested code commit:** `83451c4c79871e6e30a07d38cc535308869cf852`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43877326929
**Result:** Linux scientific regression PASS; Windows scientific regression PASS;
TypeScript/Vite production build PASS; CPU R2.6/R2.7 contracts PASS;
Chromium **24 passed, 3 optional tests skipped**.

## Source-specific diagnosis

Original controlled real P1 OBJ SHA-256:
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

- 69 original XYZ vertices; 42 native QUAD and 36 native AFT TRI faces.
- All 42 original QUADs are non-coplanar under the R2.7 flat-quad tolerance,
  so R2.7 strict all-faces BVH correctly rejected the mesh.
- Those 42 QUADs still satisfy the source-indexed convexity checks, but this
  **does not** certify them as valid planar quadrilaterals or smooth Bézier
  surfaces and **does not** authorize an invented diagonal decomposition.
- R2.7.1 preserves strict rejection of invalid connectivity, bow-ties,
  nonfinite coordinates, duplicate source IDs and degenerate original TRI.

## Implemented fail-closed partial-index contract

`buildXyzBvh(data)` remains strictly all-or-nothing by default; the browser
Worker explicitly opts in to `allowUnindexedWarpedQuads`.

- Full original connectivity and source-face identity are validated before
  building; source vertices remain untouched and are transferred as copies.
- The real P1 Worker builds an index for **36 original TRI**, excluding **42**
  warped QUAD. Worker coverage explicitly reports
  `sourceFaces=78, indexedFaces=36, excludedQuadFaces=42`.
- If the QUAD layer is **visible**, all BVH picks return `ambiguous` and
  the UI selects via `vtkCellPicker`. This is necessary because excluded
  curved QUADs could obscure indexed TRI.
- If the QUAD layer is **hidden**, qualified original TRI rays may return
  original source-face IDs from the Worker. Misses, ambiguous edges and
  errors still fall back to native VTK. The underlying indexed geometry is
  for selection only and is never a scientific surface or adaptive solver.
- Pure-QUAD warped inputs without any qualified indexed face still reject
  the Worker rather than constructing an empty index.

## Executed evidence

1. R2.7.1 Chromium test traversed the **36 real native P1 TRI** using
   near-centroid rays in XYZ. All 36 selected their corresponding original
   source-face IDs; no mismatches. All 36 rays returned `ambiguous` if the
   QUAD layer was made visible. Source SHA, buffers and IDs were preserved.
2. Actual real-P1 viewport A/B with QUAD hidden:
   - Original source face **#68** was selected with method
     `EXPERIMENTAL_XYZ_BVH_WORKER`.
   - At the same page dimensions and pixel, after loading a native-picker
     viewport with the same visibility, `VTK_CELL_PICKER` selected the
     exact same original face **#68**.
   - The automated search considered 13 candidate screen points to find
     one qualifying interior TRI; this **single positive match** proves
     UI integration only, not a statistically valid speed claim.
   - CI log marker: `R271_REAL_P1_TRI_VIEWPORT_AB`.
     Captured attachment: `r271-p1-tri-only-viewport-ab.json`.
3. CPU negative fixtures retained strict rejection of malformed source QUAD,
   but admitted a safe TRI-only index alongside warped convex QUAD, without
   accepting a pick while any excluded QUAD could be visible.

## Not qualified

- Native BVH selection when curved QUAD is visible (intentional VTK fallback).
- Curved Bézier surface equivalence, multi-patch overlapping source sheets,
  general real mesh family coverage, and independent numerical source oracle.
- Memory footprint of source plus index, worker startup and total click-to-paint
  latency distributions, real GPU FPS or physical Windows GPU checks.
- Original curved QUAD triangulation, scientific all-quad generation, anisotropic
  adaptation, source generator runtime changes or geometric LOD.

## Next gate: R2.7.2

Collect deterministic multi-pixel, multi-model A/B samples for original source
TRI-only visibility; separate Worker build cost, warm-pick latency and
native-picker baseline, including boundary and overlap fallback receipts.
Measure declared hardware/browser memory separately from script-only estimates.
Any extension to visible warped QUAD requires independently reviewed VTK
render/intersection equivalence and source-identity preservation.

**Release decision:** R2.7.1 is a qualified *narrow TRI-only source slice*,
not a broad BVH release. Keep `?xyzPicker=bvh` opt-in and PR #239 draft;
no merge to `main`, release, tag or source-generator modification.
