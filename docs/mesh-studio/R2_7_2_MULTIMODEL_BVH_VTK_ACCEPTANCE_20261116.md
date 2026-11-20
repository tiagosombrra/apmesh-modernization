# Mesh Studio R2.7.2 — real-source BVH/VTK diagnostic acceptance round

**Date:** 2026-11-16. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Exact code revision tested:** `87e6eeed4dbc7a30b75b054558d77c18d9ae86fd`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43886817088
**Validation:** Linux scientific regression PASS; Windows scientific regression PASS;
TypeScript/Vite production build PASS; CPU R2.6/R2.7 contracts PASS;
real Chromium **26 passed, 3 optional cases skipped**.
The earlier instrumentation-only run also passed:
https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43886668168
(25 browser tests passed, 3 optional skipped).

## What was implemented and exercised

- The experimental Worker reports its **worker-local BVH index build wall time** and
  **worker-local query wall time**, with separate main-thread preparation,
  copied input byte count, and main-thread `ready` message round trip.
- Every direct `pickWithMeasurement` sample reports Worker compute time,
  message round trip, outcome and explicit timeout/unavailable status.
  Existing production `pick` behavior and source face IDs are preserved.
- Browser viewport diagnostics record the **picker-call wall time** and exact
  original source face ID. These are not click-to-React-paint or GPU presentation times.
- Five real source files were replayed with 12 non-edge source-local TRI rays
  each: **60/60 exact IDs matched**, without accepting a visible warped QUAD.
  One controlled P1 and four *staged/unaccepted* candidate meshes are not
  five independent generator experiments.
- Two actual real-model Chromium viewports (P1 and Band) used explicit opt-in BVH,
  QUAD hidden, fixed model/camera visibility and the same pixel for native VTK
  A/B comparison. **Three distinct original IDs per model matched**, with no
  false-positive background hit.

## Worker build / ready measurements from CI #43886817088

These figures are **one hosted Linux Chromium run, not repeated distributions**.
`ready` includes preparation, browser Worker setup, transfer and scheduling;
the worker-local build time is separately measured. The byte count is only
the copied typed-array payload, **not total Worker index memory or system RSS**.

| Source | Native TRI | Curved QUAD excluded | Worker build ms | Ready round-trip ms | Copied input bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Controlled P1 | 36 | 42 | 1.2 | 7.5 | 2,950 |
| Band (staged) | 44 | 62 | 1.1 | 6.5 | 4,018 |
| West (staged) | 50 | 75 | 1.2 | 6.1 | 4,737 |
| North (staged) | 54 | 71 | 1.2 | 6.2 | 4,697 |
| Both (staged) | 52 | 82 | 1.3 | 5.8 | 5,086 |

## Six real Chromium viewport pixels with exact native VTK agreement

The test attempted 34 deterministic pixels for each model before finding
three **distinct** BVH interior TRI source IDs. Only successful, non-boundary
BVH IDs are in this small diagnostic table: it is **selection-biased**, not
a statistically valid full-screen performance distribution.

| Real model | Original face | BVH picker-call ms | Native VTK picker-call ms | Identity |
| --- | ---: | ---: | ---: | --- |
| P1 | 68 | 25.5 | 1.1 | match |
| P1 | 76 | 19.8 | 0.4 | match |
| P1 | 69 | 18.8 | 0.4 | match |
| Band | 94 | 26.0 | 1.4 | match |
| Band | 104 | 16.2 | 0.4 | match |
| Band | 95 | 20.1 | 0.4 | match |

**Observed decision:** the Worker path is materially **slower** than native
VTK for these small, real TRI-only viewports. Do not claim BVH speedup from
bounded local geometric traversal alone: the browser message/scheduling
overhead dominates this sample. No default-on acceleration, automatic
heuristic or break-even threshold can be justified by these six picks.

## Scientific and resource guardrails

- P1 original source SHA-256:
  `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
  Staged Band/West/North/Both source SHA and status are checked against the
  read-only catalog within the 60-ray CI test.
- Each source QUAD remains non-coplanar under the strict R2.7 tolerance and
  is excluded from BVH. **With QUAD visible, Worker picking returns
  `ambiguous`, and native VTK remains authoritative.**
- No scientific geometry/surface quality is inferred from Float32 picking
  success. Source seams, shared curves and non-manifold physical ownership
  must not be welded, synthesized or silently changed.
- `performance.memory` is only an optional Chromium main-thread JS heap
  estimate; it does not include trustworthy Worker RSS, browser total
  native memory, GPU VRAM or independent physical Windows hardware.
- This round did not measure end-to-end input-to-paint time, actual GPU FPS,
  rigorous independent ray/Bezier surface oracles, sustained workloads,
  or valid geometric coarse LOD.

## Decision / next R2.7.3 gate

**Status: bounded diagnostic acceptance, not a general performance release.**
The opt-in R2.7.2 implementation passes the stated correctness and
telemetry tests, but provides **negative small-mesh performance evidence**.

Next, construct a **repeated and paired** A/B protocol with warm-up,
fixed cameras/pixels, explicit worker startup exclusion, sample-order
controls and p50/p95 ranges. Extend to source-qualified, larger real
TRI-containing inputs if available; never substitute a synthetic scaled
fixture for genuine APMesh scientific data. Measure wall latency including
UI paint separately from picker-call time, and obtain declared host/browser,
total native RAM/Worker memory and GPU observations where supported.

Until there is measured break-even benefit and scientific/topological
qualification, default to `vtkCellPicker`; keep experimental BVH behind
`?xyzPicker=bvh`. R2.8 *geometric* LOD and curved QUAD index admission
remain blocked pending independent equivalence and error-bound contracts.

**Source changes:** `tools/mesh_studio/web/` and `docs/mesh-studio/` only.
No generator C/C++ change, QUAD certification, `main` merge, tag or release.
