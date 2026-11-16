# Mesh Studio R2.7 — opt-in XYZ BVH qualification protocol

Date: 2026-11-16. Scope: isolated Studio branch `feature/mesh-studio-r27-bvh-20261116`.
No source generator changes, QUAD research promotion, merge into `main`, or release are authorized here.

## Decision boundary

The R2.6 structured synthetic 500k ray picker remains a separate, narrowly qualified
experimental path. R2.7 introduces a *general-purpose prototype* for a bounded
real XYZ source-face BVH built inside a browser module Worker. Enable it only with
`?xyzPicker=bvh`; normal viewing keeps `vtkCellPicker` authoritative.

The R2.7 index is display Float32 geometry, not an APMesh numerical or source-curve
oracle. Qualification requires XYZ input, no more than 100,000 faces, exact original
uint32 face identifiers, structurally valid TRI/QUAD cells, distinct vertex IDs,
finite coordinates, nondegenerate faces and strictly convex planar QUADs.
Warped/bow-tie and duplicate-identifier meshes fail closed; indexed overlapping
visible faces or hit boundaries return `ambiguous`, retaining VTK fallback.

The Worker receives *copies* of geometry buffers. The UI does not transfer ownership
of VTK or canonical source arrays. Requests are bounded by a 15 s build deadline,
250 ms pick deadline and at most four simultaneous picks. Camera and visibility
changes invalidate pending asynchronous selections. Index and face identities
must never be inferred from coincident XYZ coordinates across source patches.

## Reproducible gates

From `tools/mesh_studio/web` on the exact branch revision:

```bash
npm install --no-audit --no-fund
npm run test:contracts
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
```

The R2.7 Node contracts cover input validity, warp/re-entrant QUAD rejection,
source-ID preservation, duplicate identifiers, overlap ambiguity, bounded grid
traversal, and occlusion order.

`tests/viewport-r27.spec.ts` separately checks actual Chromium Worker construction,
buffer ownership, front/back face selection, layer filters and boundary fallback.
The real P1 check uses controlled physical source geometry (42 QUAD, 36 TRI,
78 source faces), verifies original hash/IDs and records whether the Worker
qualifies or rejects that particular mesh. The P1 viewport A/B test requires a
*positive original face hit* at one shared pixel and asserts original face ID
agreement with a native VTK selection. Its JSON receipt is stored in
`test-results/r27-real-p1-xyz-pick-ab.json`.

This is one behavioral selection test, not a real-model BVH performance study.
If P1 is rejected and both clicks execute the native picker, the receipt only
proves **fail-closed fallback and face-ID consistency**. A successful native/native
fallback is not evidence that BVH acceleration works on that real geometry.

The CI workflow `.github/workflows/mesh-studio-validation.yml` now includes
the dedicated R2.7 branch in its push filter. Windows hosted Python tests are
not real Windows desktop GPU/WebGL qualification.

## Unclosed gates (must not be relabeled as passed)

1. Independently qualified *real source* mesh on which BVH actually answers
   nonambiguous hits; native VTK agreement across many pixels, both triangle and
   quadrilateral visibility filters, and occluded/overlapping patch-local sheets.
2. End-to-end repeated latency distributions (not just a picker call) with
   fixed viewport/camera/source hash, visible UI paint and separate startup cost.
3. Total resident RAM, JS heap, native allocations and VRAM on declared hardware;
   supported 1k/50k/100k real meshes and host-specific GPU/browser versions.
4. Explicit source-identity and topology contracts before introducing *geometric*
   coarse LOD. R2.6 source-face partitions are not coarse geometry or error bounds.
5. Physical GPU qualification on Windows, including driver/resize/reopen tests.
6. Cross-branch integration review and protected merge only after full scientific
   and UX acceptance. Never silently enable `xyzPicker=bvh` by default.

For performance and science, record absent observations as `NOT_MEASURED`, not
zero or inferred improvement. Do not equate render-dispatch timing with GPU FPS,
or VTK picking agreement with Bézier surface validity.
