# Mesh Studio R2.7.3 — paired repeated XYZ BVH vs native VTK

**Date:** 2026-11-16.
**Isolated branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Exact code tested:** `fe608ca172b1ff4a0a11e78014e04374784ff32f`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43915414238
**CI result:** scientific Python/VTK regression Linux **PASS**, Windows **PASS**,
TypeScript/Vite build and CPU contracts **PASS**, Chromium **28 passed /
3 optional tests skipped**.

## Question and study scope

Does the experimental Worker-based source-face BVH deliver faster *picker-call*
interaction than native `vtkCellPicker` on the currently available
**real source** P1 (controlled) and Band (staged, not accepted), with only
native AFT TRI visible?

The result is restricted to the current Linux hosted Chromium instance.
Neither candidate represents the 50k or 500k *real* APMesh workload, and
the two source files do **not** constitute independent generator trials.

## Executed paired protocol

- Both sources identified by exact original source SHA-256:
  - P1: `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
  - Band: `76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`.
- Source geometry is visualization Float32, not a scientific curved-surface oracle.
- Real original TRI-only rendering: P1 36 TRI/42 warped QUAD excluded,
  Band 44 TRI/62 warped QUAD excluded. QUAD visibility is **off** for both methods.
- Two concurrently warmed Chromium pages share fixed source, viewport
  dimensions and snapshot-verified XYZ camera pose. The *same pixels and
  original IDs* are checked in both.
- Three distinct BVH-positive, off-boundary original source-face IDs were
  selected deterministically from a bounded pixel grid and confirmed by VTK
  before measurement. This conditions the study on successful BVH hits;
  it **does not** represent the distribution of all screen pixels.
- Each method had **two excluded warm-up calls per face**. There were
  **eight** paired rounds, with AB/BA alternation and reversed pixel order
  on alternate rounds: 3 faces × 8 rounds = **24 paired calls per model**,
  **48 pairs** overall. Source IDs matched in every measured pair.
- All camera snapshots were compared before and after; any face mismatch,
  source SHA mismatch, camera divergence or missing timing fails the test.
- Durations are measured **inside the browser picker click callback**,
  using its existing `data-last-picker-wall-ms`. They do **not** include
  the Playwright click action, user input latency through OS dispatch,
  React commit, visible paint or GPU presentation.
- Percentiles are empirical **nearest-rank** p50/p95, not confidence
  intervals. Raw per-pair times, method order, face ID and pixel are retained.

## Exact results (CI #43915414238)

| Model | Method | n | p50 picker-call ms | p95 picker-call ms | min ms | max ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| P1 | BVH Worker | 24 | 20.2 | 20.9 | 17.9 | 21.3 |
| P1 | Native VTK | 24 | 0.5 | 0.7 | 0.3 | 0.8 |
| Band | BVH Worker | 24 | 20.0 | 21.7 | 18.7 | 21.8 |
| Band | Native VTK | 24 | 0.5 | 0.7 | 0.4 | 0.9 |

Paired differences (**BVH minus native VTK**, preserving paired order and
original source face):

| Model | Pairs | p50 additional ms | p95 additional ms | Selected original face IDs |
| --- | ---: | ---: | ---: | --- |
| P1 | 24 | 19.7 | 20.4 | 68, 76, 69 |
| Band | 24 | 19.5 | 21.1 | 94, 104, 95 |

CI log markers: `R273_PAIRED_REAL`. Full receipts written and attached by
Playwright:

- `test-results/r273-paired-p1-real-tri-only.json`
- `test-results/r273-paired-band-real-tri-only.json`

The separate source-local 60-ray evidence from R2.7.2 was rerun in the same
CI: `R272_REAL_SOURCE_PROFILES`, 60/60 matched across five original files.
The R2.7.2 single-click viewport tests also reran successfully.

## Decision

**Correctness: PASS within the narrow sampled TRI-only real source scope.**
**Performance advantage: NOT DEMONSTRATED; observed disadvantage.**

The native VTK call was much faster in every paired sample. The approximately
20 ms BVH call duration is consistent with browser Worker message scheduling
overhead dominating small meshes, but this experiment does **not yet isolate**
the internal Worker query time from the message round trip in the *viewport*
trace. Do not report a causal proof or a generalized break-even size.

**Keep the native `vtkCellPicker` enabled by default.** The optional BVH
remains behind `?xyzPicker=bvh`; reject unsupported geometry or any visible
warped QUAD and preserve native fallback.

## Unclosed performance and scientific gates

1. Independently qualified, larger *real APMesh* TRI-containing models
   with defensible source hashes; do not relabel the synthetic 50k/500k
   stress cases as real source data.
2. Repeated per-click **Worker CPU time vs message round trip** in the
   same visual ray path, separate from VTK picker time; examine scheduling
   overhead and alternative main-thread fast-path designs.
3. Multiple hosts/browsers with documented hardware, complete
   input-to-visible-paint response, correct handling of close/reload/
   cancellation, GPU/frame timing and stable interaction under load.
4. Reliable native RSS, Worker-owned arrays, browser heap and GPU VRAM
   profiles. The current typed buffer count and optional Chromium
   `performance.memory` are insufficient for total memory.
5. VTK intersection equivalence for visible nonplanar Bézier QUADs and
   patch-incidence ambiguity, or explicit continued exclusion.
6. Geometric coarse LOD with surface error bounds, original-face
   completeness and patch/seam constraints (a later R2.8 gate).

These results are a **negative performance acceptance receipt**, not an
authorization to optimize scientific topology, to enable BVH by default,
to publish speedup or to advance R2.8 geometric LOD.

**Source isolation:** only `tools/mesh_studio/web` and
`docs/mesh-studio` were modified. No APMesh C/C++ generator code,
scientifically certified QUAD source, `main`, release or tag.
PR #239 remains draft for independent review.
