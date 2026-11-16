# Mesh Studio R2.7.5 — bounded main-thread BVH versus Worker versus VTK

**Date:** 2026-11-16. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Exact validated code SHA:** `00f387fa993e3038e31b7faf1983e2d988ec1281`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43921138389
**Result:** Linux scientific regression PASS, Windows scientific regression PASS,
TypeScript/Vite production build and CPU contracts PASS, Chromium **33 passed,
3 optional skipped**.

## Implemented R2.7.5 prototype

The new `tools/mesh_studio/web/src/xyzBvhMain.ts` reuses
`prepareBvhPayload` and `buildXyzBvh`, but executes the qualified index on
the UI thread **only when the user explicitly requests**
`?xyzPicker=sync`. The separate `?xyzPicker=bvh` Worker experiment and
the default native VTK behavior remain unchanged.

The synchronous path refuses inputs beyond **2,048 faces**, **8,192 vertices**
or **1 MiB total input typed buffers**, before copying/constructing the
index. It preserves original source-face IDs and source-owned buffers.
It validates all original faces before indexing any; nonplanar convex QUADs
may be excluded from the index only under the existing partial-index policy.
**When excluded warped QUADs are visible**, the index returns
`ambiguous` and selection falls back to `vtkCellPicker`. Invalid geometry,
numerical ambiguity, boundaries, misses, unsupported models and exceptions
also fall back without ever inventing a source ID.

Index preparation/construction duration, indexed original face count,
excluded warped QUAD count, picker call duration and direct synchronous
query duration are exposed as explicitly scoped diagnostics. They are
not GPU measurements, a source quality oracle or adaptive mesh evidence.

## Exact provenance and geometry scope

- **P1:** original accepted controlled OBJ SHA-256
  `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`;
  36 source AFT TRI indexed, 42 nonplanar QUAD excluded.
- **Band:** staged **unaccepted** candidate OBJ SHA-256
  `76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`;
  44 source AFT TRI indexed, 62 nonplanar QUAD excluded.

The two models do not constitute independent accepted adaptation experiments.
The experiment is only about selecting existing display Float32 source
facets under TRI-only visibility.

## Executed Chromium A/B/C protocol

Each model's three concurrent viewport pages were configured with
`?xyzPicker=sync`, `?xyzPicker=bvh`, and default native VTK respectively.
They used verified source hashes, identical viewport dimensions, identical
captured XYZ cameras and **the same pixel** under QUAD-hidden TRI-only
visibility. Three **different** original native TRI face IDs per model
were selected from a bounded candidate grid and independently confirmed
by all three selectors before measurement. Each selector was warmed
twice per face; then **8 rounds × 3 faces = 24 matched triples per model**,
with rotated picker order and reversed face order.

- P1 source face IDs: **68, 76, 69**; 24/24 matched triples.
- Band source face IDs: **94, 104, 95**; 24/24 matched triples.
- In total, **48/48 triple observations** matched the exact original
  source face ID and preserved XYZ camera snapshots.
- Additional browser negative/fallback test: visible P1 warped QUAD forces
  native VTK. Exceeding either face or vertex bound is refused before index
  construction. Original coordinate buffers and face IDs remain unchanged.
- The earlier R2.7.3/R2.7.4 real Worker and source-ID regression protocols
  also passed in the same CI execution.

## Observed picker-call durations (single hosted Chromium run)

Times below are within the existing viewport picking callback; **not**
OS-pointer-to-presented-frame times. The synchronous index build is
recorded separately and excluded from warm-pick distributions.
Percentiles are empirical nearest-rank p50/p95, not confidence intervals.

| Source | Selector | Matched calls | p50 ms | p95 ms | Minimum ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| P1 | Bounded synchronous BVH | 24 | **0.1** | 0.2 | 0.0 | 0.2 |
| P1 | BVH via Worker | 24 | 20.9 | 21.3 | 15.2 | 21.4 |
| P1 | Native `vtkCellPicker` | 24 | 0.6 | 1.0 | 0.5 | 2.1 |
| Band | Bounded synchronous BVH | 24 | **0.1** | 0.2 | 0.0 | 0.3 |
| Band | BVH via Worker | 24 | 20.4 | 21.2 | 14.4 | 23.0 |
| Band | Native `vtkCellPicker` | 24 | 0.6 | 1.0 | 0.4 | 1.0 |

Measured index construction, including the bounded input copy:
**P1 1.3 ms**, **Band 0.8 ms** in this single run.
The direct main-thread `pick` query registered p50 rounded to
**0.0 ms** and p95 **0.1 ms** on both models; timing at this granularity
is resolution-limited.

CI log marker: `R275_MAIN_WORKER_VTK`.
Full receipts including original face IDs, pixel coordinates, method order,
per-call times and signed paired deltas were attached as:

- `test-results/r275-p1-sync-worker-vtk.json`
- `test-results/r275-band-sync-worker-vtk.json`

These are captured in the run's `mesh-studio-chromium-<SHA>` artifact,
with the retention window specified by the workflow.

## Decision

1. **Narrow functional correctness: PASS**, for sampled real original TRI
   in the two named source files, with nonplanar QUAD hidden.
2. **Narrow performance finding:** the synchronous method's recorded
   picker-call p50 was lower than both Worker and VTK in this hosted
   Chromium run. The Worker remained much slower on real pointer clicks
   despite a low underlying CPU query time.
3. **No promotion to production or default selection.** The sample
   is restricted to positive interior TRI hits, small meshes, a single
   hosted Chromium environment, and no warm-index build amortization
   or real user input-to-paint timing. A synchronous traversal can
   still block the UI on larger meshes, hence the hard caps.
4. **No scientific quality claim.** The BVH uses rendering Float32,
   not independent Bézier surface, patch/shared-curve or anisotropic
   generator verification. Warped QUADs remain excluded whenever
   visibility could introduce occlusion.
5. **No total RAM/VRAM or physical Windows GPU claim.** Tested Windows
   scientific regression does not validate a native Windows browser/GPU.

## R2.7.6 next gates

Before increasing the source-size caps or enabling any automatic
selection: obtain independently provenance-qualified **larger real**
TRI-containing source geometries; repeat A/B/C on multiple browsers
and a physical GPU workstation; measure Worker queue behavior and
real end-to-end click-to-paint; collect RSS/Worker/VRAM and index
memory; compare different viewport camera/occlusion/overlap scenarios;
prove source-ID and patch/seam preservation under each.

The 50k/500k synthetic cases remain *synthetic* preflights, not proof
of scientific real-mesh speed or LOD. R2.8 geometric LOD remains blocked
pending explicit error bounds and source-face lineage review.

**Isolation:** Only Studio frontend, tests and documentation changed.
Do not merge into main, enable by default, tag, release, or edit the
scientific C/C++ APMesh generator in this research round. PR #239
remains a draft.
