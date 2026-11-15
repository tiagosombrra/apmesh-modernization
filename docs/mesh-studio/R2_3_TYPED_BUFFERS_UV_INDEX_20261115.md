# Mesh Studio R2.3 — typed VTK buffers and conservative UV picking

Implementation branch: `feature/mesh-studio-fixture-first-20261114`.
Source review parent: `60bbcae48524ac8e330861f6cdbc2dc4ff99fe34`.

## Changes

- Replace repeated `Array.flat()` + `Float32Array` reconstruction with an exact
  preallocated Float32 buffer cached by immutable **render geometry identity**.
  Color and connectivity arrays are assembled directly into preallocated typed
  arrays, once per visibility mask. The physical/UV source arrays remain intact.
- Replace linear selected-face lookup with an original-ID-to-index map scoped to
  the current model. This does not infer patch identity by spatial proximity.
- Add an **optional** bounded UV spatial hash for planar, nondegenerate 2D
  faces; on overlaps, shared-face edges, unsupported sizes or failed coordinate
  projection the original VTK cell picker remains authoritative. The index
  is strictly a renderer interaction accelerator, never a geometry validator.
- Preserve source-face IDs through visibility filtering and linked XYZ/UV
  selections. A rendering preview is not a scientific result; there is no
  adaptive epoch, all-QUAD or anisotropy claim.
- Record picker strategy and number of UV candidates examined, in addition
  to synchronous selection duration. The new observations remain separate
  from numerical quality, true GPU frame presentation and overall UI latency.

## Mandatory verification

The GitHub workflow must pass Python/VTK science tests on Linux and Python
contracts on Windows and a real Chromium build/E2E. Playwright covers typed
buffer identity, face ID mapping, visibility, ambiguous-overlap fallback and
50k synthetic source-ID-linked UV selection. Timing measurements are not
compared to fixed thresholds because shared hosted runner load varies.

**Limits:** No GPU VRAM, 500k or Windows workstation qualification. No
true multiresolution mesh LOD because arbitrary face subsampling would leave
holes and break the scientific interface. Instead prefer chunked native mesh
representation with exact face-level selection or a separately audited LOD
mapping that never claims the preview represents full topology.
