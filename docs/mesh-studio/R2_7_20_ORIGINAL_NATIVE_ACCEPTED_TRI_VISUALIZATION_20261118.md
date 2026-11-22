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

## Final exact native and Chromium certification — 2026-11-18

**R2.7.20 PASS for original accepted native TRI visualization
and explicit source-face/patch/node identity in the isolated
read-only STUDIO panel**, grounded in
[GitHub Actions #44271230173](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44271230173),
exact tested source revision
`d41c7005e97d5ea8270bc9fe5e1a7066f8857f1e`:
**all 4 independent jobs completed SUCCESS**.

| Independent experiment or regression gate | Result |
| --- | --- |
| Real compiled original C++ serial Eistute native run | **1 accepted** / 3 rejected-restored, **1,168 original TRI**, 4 patches, **292 faces per patch** |
| Real compiled original C++ serial Book native run | **1 accepted** / 2 rejected-restored, **4,256 original TRI**, 28 patches, **152 faces per patch** |
| Original R2.7.12–R2.7.20 real C++ source, owners, curve incidence, UV and native-face identity audits | **PASS** |
| Original scientific OFF versus research-ON Eistute binary outputs | **21/21 byte-identical** |
| Original scientific OFF versus research-ON Book binary outputs | **17/17 byte-identical** |
| Linux Python scientific and negative test suite | **330 run; 4 optional skips; PASS** |
| Windows Python scientific and negative test suite | **330 run; 10 environment skips; PASS** |
| Real hosted Chromium with R2.7.20 source-face and viewport tests | **50 passed; production TypeScript build PASS** |

The tested original native source SHA256 records are:
- **Eistute**, C++ postcommit NDJSON:
  `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`.
- **Book**, C++ postcommit NDJSON:
  `e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a`.

The complete original accepted native scene JSON has exactly
**1,716,994 bytes**, JSON SHA256
`71826a6771f64fa356a3c157d32bc926dddbef60918292f00d33198752ab9305`.
Its GitHub Actions source artifact
[#14412278291](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44271230173/artifacts/14412278291)
is a **214,951-byte ZIP** with SHA256
`ec272047767f1f3baf8d62e2b17138fe8f3af056c20db04b6d5ca2a48a97d4c8`.

A separate true original C++ raw NDJSON / native runtime
stderr research evidence ZIP
[#14413175604](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44271230173/artifacts/14413175604)
has **279,377 bytes**, SHA256
`c7a19227eb79eed4d80594ad5cc3bd0cec656ef197cd3090589ff8cf4b0c7f3d`.

Both ZIPs were downloaded directly from GitHub Actions,
retained in authenticated personal Google Drive folder
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`,
then **retrieved from Drive again**. Independent SHA256
calculations of the downloaded Drive files matched the exact
original GitHub ZIP digests stated above.

**Independent full-source cross-audit:** all **5,424
original TRI faces** from the native source NDJSON were compared
against all **5,424 exported R2.7.20 scene faces**, checking
`(patch_slot, native_patch_id, element_slot, native_element_id)`
and **every original per-corner** `[native_node_id, XYZ, UV]`
value for exact equality, without a float32 round-trip.
**All matched; none was inferred from OBJ ordinals.**
These checks are independent of the browser's approximate
rendering precision.

### Corrected noncertified preflight

An earlier incomplete run #44270473454 encountered a
single frontend TypeScript implicit-any compiler error in
the face corner cross-check. It was corrected before
the exact passing CI above. That earlier run was **not**
used as certified browser evidence.

### Remaining scientific exclusions

The browser structural JSON importer does **not**
cryptographically authenticate the original NDJSON bytes
on its own. The source-authenticated scientific evidence
is the original C++ native capture + independent Python
source SHA audit + permanent archived originals.

The independent R2.7.20 VTK scene uses float32
presentation points and duplicated **display-only**
triangle corners. It does not claim physical C++ node
welding, global UV atlas, equal C++ node pointers,
or continuous geometric quality.

R2.8 scientific geometric LOD remains **BLOCKED**:
only one real accepted native adaptive epoch per model,
no proven cross-epoch face/curve descendants,
no certified continuous source-surface error bounds,
and no physical Windows GPU present/RSS/VRAM qualification.
PR #239 remains **draft and unmerged**;
VTK default and both bounded opt-in BVHs unchanged;
no tags, release or generator policy changes.
