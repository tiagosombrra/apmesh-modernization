# Mesh Studio R2.7.20 — original accepted native TRI XYZ/UV visualization

**Date:** 2026-11-18. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** #239 (draft, no merge). **Research scope:** actual original serial
Eistute and Book TRI accepted snapshots with C++ native lineage capture
**opt-in only**, no new geometry algorithm.

## Research and visualization question

R2.7.19 qualified a true original source curve and local node **identity
inspector**, not an actual Eistute/Book 3D mesh viewer. The original
STUDIO P1/candidate XYZ+UV viewports are **different geometries**.
R2.7.20 supplies independently sourced XYZ/UV triangles from
the actually accepted native C++ postcommit **per-face original
NDJSON** without reusing P1 or fabricating a face mapping.

The distinguishing identity for one visualization cell is the
**real accepted native adaptive step, original patch slot and
original element slot**; the exact original native element ID is
retained with that tuple. Native IDs are not assumed unique
between source patches or persistent between adaptive epochs.
The real original per-corner native node IDs, XYZ doubles and
local UV doubles are retained in the JSON source payload.

## Source-verified exporter

`tools/mesh_studio/native_accepted_scene.py` first re-runs
the retained-original-source and SHA-256 audit, source curve
incidence/UV sampling, corner ID and postcommit C++ owner
verification through the R2.7.19 export. It then reads **each
original accepted source face** from the very same original
NDJSON records and revalidates all original
`(model, accepted native step, original per-face NDJSON SHA256)`
joins. It refuses unverified accepted epochs, foreign patch
owners, noncontiguous original element slots, nonfinite XYZ/UV,
over-limit and JavaScript-unsafe original native IDs, and a
mismatch between original source patch face totals and the
expected source receipt.

Each compact source face is represented as

```text
[patch_slot, native_patch_id, element_slot, native_element_id,
 [[native_node_id, xyz_x, xyz_y, xyz_z, uv_u, uv_v], ... 3 corners]]
```

This format preserves **three original corners per original
triangle**. No node identifiers are silently merged or
assigned new global C++ identities. No OBJ ordinal is used
as a replacement for original source element identity.

The source-bounded artifact
`build/r2720-native-accepted-scene.json` contains one original
scene per genuinely accepted snapshot, and embeds its matching
R2.7.19 verified sample/node identity manifest. It explicitly
declares **no physical welding, no cross-epoch ancestry and
no scientific geometric LOD**. The bounding limit is 9 MB for
the whole JSON and 12,000 TRI faces per source model.

## Browser rendering and interaction

The independent VTK scene viewer is accessible **only** with

```text
http://127.0.0.1:5173/?nativeScene=1
```

It accepts the JSON extracted from the R2.7.20 Actions
artifact. The original P1/candidate viewports and source
face picking remain untouched and keep VTK as their
default picker. R2.7.20 does not modify their API.

The R2.7.20 browser:
- Renders original accepted Eistute or Book native TRI XYZ
  using vtk.js, with patch-dependent display colors,
  and **no shared VTK vertex indices** created across
  original triangles. This is a rendering transport,
  not an assertion about the native mesh's physical
  C++ connectivity.
- Renders **only the selected patch's local UV chart**
  in a separate VTK viewport. This avoids the false
  claim that all source patch UV are one global atlas.
- Uses actual native VTK cell selection for the
  display scene. A picked cell is mapped directly
  to the original `(patch_slot, native_patch_id,
  element_slot, native_element_id)`, and the three
  original node IDs and XYZ/UV are shown independently
  of the approximate float32 rendering buffers.
- Enables a source-curve sample to select a
  **representative accepted face incident to that
  original native node ID**, never generating
  a new source face or setting a fake global node ID.
  If a selected face has no shared source-curve
  incidence, the UI says so rather than inventing one.
- Keeps the current full-source JSON separately from
  its float32 VTK presentation, and clearly warns
  that browser JSON import **does not independently
  authenticate raw native NDJSON** without the
  original bytes. The authenticated original report,
  executable and source files remain in the
  separate scientific pipeline and original archives.

The browser import is structurally bounded and rejects
source hash/epoch mismatches, foreign source patch slots,
duplicate element slots, omitted faces/corners,
inconsistent original native patch IDs, invalid original
XYZ/UV and source sample-to-face mismatches, and any
attempt to assert global welding or LOD.

## Independent CI qualification

The exact source revision under test must satisfy
all four jobs:
1. Original compiled serial C++ GeneratorAdaptive
   execution with real Eistute/Book article configurations,
   original accepted TRI source NDJSON, independent SHA-bound
   R2.7.12–R2.7.19 source and ownership audit and
   new R2.7.20 real XYZ/UV export.
2. Original instrumentation-OFF versus ON numerical parity,
   verifying byte-identical scientific CSV/JSON/OBJ
   outputs, native accepted/rejected/restored step counts.
3. Independent Python negative-contract tests and source
   regression on Linux and Windows.
4. Vite/TypeScript production build and true Chromium
   tests for the explicitly opt-in R2.7.20 XYZ/UV
   scene, original face identity and forged import refusal.

The R2.7.20 original source-derived artifact is retained
for 14 days as
`mesh-studio-r2720-native-accepted-scene-<source-sha>`.
The original raw C++ per-face NDJSON plus complete authentic
native stderr remain a separate shorter-lived Actions artifact,
which must be archived independently for durable reproducibility.

### Explicit exclusions

A true accepted native TRI surface visualization is
**not an adaptive geometric LOD**. Only one genuinely
accepted adaptive epoch is currently available per
original model. We have no independently qualified
face or curve descendants between accepted epochs,
no continuous source-to-mesh geometric deviation bounds,
and no physical Windows GPU present/RSS/VRAM
qualification. The R2.8 scientific LOD remains
**BLOCKED**. VTK default unchanged; experimental
BVHs opt-in/bounded; PR #239 draft/unmerged, no tag,
release or main merge.

## Certification log

Implementation and code contracts committed to the
isolated research branch. The first R2.7.20
attempt that included the viewer reached a
TypeScript implicit-any failure in its browser
build and was **not certified**; this was corrected
before full qualification. Do not mark this
step PASS until the final exact source revision
and all four independent Actions jobs have succeeded,
and real Eistute/Book face and patch counts,
source digests and archived original bytes
have been inspected.
