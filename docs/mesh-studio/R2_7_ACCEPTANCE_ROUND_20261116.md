# Mesh Studio — R2.7 acceptance round (not general real-mesh acceleration closure)

**Date:** 2026-11-16.
**Isolated branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Validated code SHA:** `6b7dc807116a8ddb0967ad0a2a7e24674bc2dc1c`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43871741968
**Result:** Linux scientific regression **PASS**; Windows scientific regression **PASS**;
production TypeScript/Vite build and R2.6/R2.7 contracts **PASS**; Chromium
**22 passed, 3 optional cases skipped**.

## Confirmed R2.7 deliverables

- General *experimental*, face-bounded (100k) source-ID-preserving CPU BVH,
  offloaded to a browser module Worker and opt-in at `?xyzPicker=bvh`.
- Rejects unsupported/nonfinite/degenerate inputs, nonplanar or invalid QUADs,
  duplicate source-face IDs and conflicting ray intersections, with native
  `vtkCellPicker` fallback; source-owned buffers are not transferred.
- Removed a full JS-array vertex copy during finite-coordinate validation.
- Added negative/occlusion CPU fixtures, real Chromium Worker tests and a
  controlled real P1 pixel-selection A/B receipt.
- Fixed Studio CI so R2.7 branch pushes are tested, independently of the
  earlier fixture-first branch. No change to generator sources or root main.

## Real P1 finding: conservative fallback, not an accelerated BVH success

The browser test used the controlled original P1 OBJ SHA-256:
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

P1 has 42 original QUAD and 36 original native AFT TRI faces. On this input,
`opt_in_worker_qualified=false`, so the opt-in browser path **correctly**
retained `VTK_CELL_PICKER`. One selected real face, original source-face ID
**36**, was confirmed against the same-position native VTK control.
The positive ID agreement demonstrates selection/fallback behavior only;
because both paths were VTK for this source, it **does not** qualify general
BVH-vs-VTK real-model speed, coverage or improved memory.

Evidence log within CI browser-spike:
`R27_REAL_P1_XYZ_AB` and artifact
`test-results/r27-real-p1-xyz-pick-ab.json`.
The separate planar/occluded two-face fixture does exercise the actual
Chromium Worker and checks source IDs, depth-order selection, filters,
ambiguity and unchanged original buffers.

## Explicitly not accepted

1. R2.7 BVH accelerated picking on **real P1** (the current strict planar
   eligibility gate rejected it); do not default-enable this path.
2. Any comprehensive real multi-patch BVH index coverage, warped Bézier QUAD
   policy, shared-curve incidence semantics or multiple-ray A/B distribution.
3. End-to-end click-to-paint latency, GPU frame presentation, native RSS/VRAM,
   allocation distributions, physical Windows GPU and browser portability.
4. Coarse geometric LOD or error-bounded simplification of 500k source faces.
5. Source-generator modification, QUAD scientific acceptance, merge into main,
   tags, release or installer.

## Next executable round

**R2.7.1 real geometry qualification:** select a provenance-verified real
source whose TRI/planar-QUAD topology can be indexed without reinterpretation,
then compare multiple interior rays, near-edges, occlusions and visibility
filters against VTK and independent analytic fixtures. Where warped QUADs
occur, introduce an explicit render-equivalent facet policy and prove it
against the underlying cell selector **before** admitting those faces.
Record index-build memory/time separately from each query, test cancellations
and preserve source face/patch ownership.

**R2.8 remains blocked** on source-specific geometric simplification contracts:
original-face lineage, surface distance and normal bounds, patch and seam
preservation, overlap ambiguity and independently verified reconstruction
error. Original-face partitioning from R2.6 is not geometric LOD.

See `R2_7_BVH_QUALIFICATION_PROTOCOL_20261116.md` for reproducible commands
and necessary future gates.
