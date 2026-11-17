# Mesh Studio R2.7.9 — source-locked camera and desktop-report integrity gates

**Date:** 2026-11-17. **Research branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** https://github.com/tiagosombrra/apmesh-modernization/pull/239 (draft, no merge).

## Aim: qualify the protocol, not the generator or graphics hardware

The R2.7.8 protocol confirms positive TRI selections at one default XYZ
camera and keeps the physical GPU benchmark open. This stage addresses
**a different source of silent overclaiming**: relying on one favorable
camera direction, comparing different click pixels under the same face
label, or pooling non-paired and unordered browser observations.

No code in the C++ generator, geometry importer, geometry processing
algorithms or default VTK picker is changed.

## 1. Multi-camera behavior on original research-source faces

`tools/mesh_studio/web/tests/viewport-r279-multicamera.spec.ts`
operates only on the two already pinned source meshes:

- **P1:** single controlled physical-generation output SHA
  `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
  It has original TRI and curved nonplanar QUAD. This is **not**
  evidence of two accepted adaptive epochs.
- **Band:** staged/unaccepted output SHA
  `76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`.
  It must never be relabeled as an accepted adaptive epoch.

For each source, the same three viewport implementations
(`?xyzPicker=sync`, `?xyzPicker=bvh`, and native/default VTK) use the
verified original source SHA and exact matching viewport sizes.
The camera poses are deterministically generated from the original
XYZ camera recipe with **0°, +18°, and −18° azimuth around global Z**.
Each pose is installed through Mesh Studio's real
`restore-cameras` control with the source-bound saved camera schema,
rather than changing the internal VTK object from the test.

The test rejects divergent pose snapshots. For every pose it locates
**two distinct positive interior source TRI face IDs** on a fixed
screen-coordinate grid, verifies that the synchronous picker,
real Worker, and VTK select the **same original face at the exact same
pixel**, and verifies post-click inspector identity.

With curved source QUAD faces made visible, both experimental paths
must **decline the partial TRI-only BVH** and fall back to native VTK
without claiming any QUAD ray-index equivalence. Re-hiding the QUADs
must recover the original TRI selection, and all three camera poses
must remain unchanged after the interaction.

Expected tested scope if the full test passes: **2 models × 3 poses ×
2 face pixels × 3 picking methods = 36 exact-ID positive comparisons**,
plus native fallback probes. The test is intentionally not a uniform
screen-pixel or complete occlusion benchmark.

## 2. Offline physical desktop report protection

R2.7.8's read-only `scripts/audit-r277-report.mjs` already required
three source faces, **72 measured records/model**, honest GPU/RSS/VRAM
flags, and matching empirical p50/p95. R2.7.9 adds:

- the original picked (x, y) screen-coordinate pair for every sample;
- exact per-original-face pixel pairs and strictly positive viewport
  dimensions, so methods cannot quietly use different click pixels;
- the complete **three pre- and three post-measurement XYZ camera
  snapshots**, each checked against the declared source-bound pose;
- reconstruction and exact verification of the **rotated and reversed
  A/B/C sample order**, rather than verifying only that all combinations
  appear somewhere in the output;
- negative mutation tests for reordered measurements, pixel changes,
  nonmatching camera poses and incomplete per-method snapshots.

The existing desktop Playwright test now writes these additional
fields itself. This is an additive **new required receipt contract**;
a pre-R2.7.9 report lacking camera/pixel details fails closed rather
than being silently considered an equivalent measurement.

**Important distinction:** a locally produced JSON file, even if
internally consistent and SHA-256 hashed, is not an independent
attestation of physical GPU identity. The audit remains
`REPORT_ONLY_NOT_PHYSICAL_GPU_MEMORY_OR_SOURCE_ACCEPTANCE`.

## 3. Scientific and performance boundaries

The BVH intersection currently uses display Float32 polygons, **not**
an independent Bezier patch/curve surface oracle. VTK reference
agreement establishes only display-face behavior for selected pixels.
It cannot certify seamless nonmanifold patch welding, boundary
tolerances, continuous surface error, Jacobians or anisotropy.

Neither simulated Playwright pointer clicks nor two
`requestAnimationFrame` callbacks establish physical operating-system
input-to-GPU-present latency. The software-rendered hosted Chromium
CI remains separate from an operator-attested, physical WGL/Vulkan
display machine. Process/Worker RSS and GPU VRAM are not measured by
this stage; their qualification bits remain false.

Original Eistute stage-4 archive remains a *saved candidate*, not
automatically an accepted transition. Historical SHA-256-manifest
discrepancy remains unmodified. The 7,184-face reference has no
authenticated original APMesh generator face/patch IDs in its OBJ and
continues to be excluded from current controlled P1/Band source tests.

## 4. CI and local command contracts

- The ordinary `npm run test:contracts` runs the offline report
  mutation suite and will reject incorrect A/B/C source/pixel/camera
  evidence.
- The ordinary `npm run test:e2e` runs the new three-pose, two-source
  GUI parity tests in hosted Chromium. Their JSON attachments record
  the complete source face IDs, poses, and selected pixels.
- The headed physical desktop command is unchanged:
  `npm run test:r277:desktop`, followed by
  `npm run audit:r277:desktop -- test-results/r277-desktop-p1-abc.json test-results/r277-desktop-band-abc.json`.
  These remain **unexecuted as physical GPU validation** until the
  operator runs them on a real, documented workstation.

No default selector promotion, main-branch merge, tag/release, C++
scientific generator changes, synchronous 2,048-face cap increase, or
R2.8 geometric LOD acceptance is authorized by this document.
