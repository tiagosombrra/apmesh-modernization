# Mesh Studio R2.7.21 — original accepted nonwelded TRI seam-edge visualization and synchronization

**Date:** 2026-11-18. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR #239:** draft, unmerged. **Source:** actual compiled original serial
GeneratorAdaptive Eistute and Book accepted TRI, read-only opt-in
`?nativeScene=1`; not a generic OBJ reconstruction or geometric LOD.

## Motivation and scientific admission

R2.7.20 imported and displayed the real accepted native XYZ and per-patch
UV TRI faces with exact original patch, element, vertex ID and source SHA.
R2.7.19 retained original source curve sample correspondences, but displaying
consecutive sampled points as arbitrary line chords would not, by itself,
demonstrate that they form **actual native accepted TRI mesh edges**.

This R2.7.21 stage adds an **independent actual-edge admission check**
before drawing a source seam. It preserves the scientific distinctions:

- **Canonical original source curve** and its fan-wide source patch incidence.
- **Independent native physical patch-local vertices**, each with original ID,
  XYZ, UV and owning patch, not welded by XYZ equality.
- **Actually accepted source TRI edge**, a real pair of local native node IDs
  in one original triangle from the same original source patch.
- **Experimental VTK display line** along that proven native mesh edge,
  never a source Bézier curve evaluation or newly allocated global C++ edge.
- **Selected original sample**, a canonical source parameter with a
  per-patch original native node. VTK float32 is display only.

No claim is made about persistent native C++ pointer identity, surface
continuity between patches, a global UV atlas, or cross-epoch ancestry.

## Actual native source edge auditor

`tools/mesh_studio/native_seam_edges.py` independently reconstructs
and re-verifies the entire accepted source evidence by replaying the
R2.7.20 native scene exporter and all its original raw NDJSON SHA, source
curve sample and actual C++ corner owner gates. It builds **patch-scoped**
native accepted TRI edge indexes from the original face corners. Every
source curve's consecutive sample pair is checked for:

1. Same original accepted step, model and source face NDJSON SHA.
2. Source patch incidence completeness at every sample ordinal.
3. Original per-patch native node ID and XYZ membership in a real
   accepted TRI face (with original double precision).
4. Existence of the real accepted native TRI edge connecting the two
   consecutive original sample IDs **within the same patch**.
5. Explicit non-admission of global welded nodes or descendants.

The report `build/r2721-original-native-seam-edges.json` includes each
actual original edge's original adjacent element slots and sample IDs;
the generated GitHub Actions artifact has 14-day retention. No
changes to the scientific generator or any historical source artifacts.

## Experimental UI

`tools/mesh_studio/web/src/nativeSeamTrace.ts` repeats the native
actual-edge gate against the **imported** original scene, failing closed
rather than drawing a fictitious chord if the source sample vertices
do not share a real accepted TRI edge.

`nativeSeamVtk.ts` visualizes verified native segments with separate
VTK display-only line cells, retaining all source patch incidences,
even when physical XYZ overlap. Teal marks edges from the other
patches, yellow the current patch, red the selected source sample.
No C++ global node ID is created or rewritten. Selection coordinates
are projected only for VTK; the original identity panel reads
the source JSON numbers.

`NativeAcceptedScenePanel.tsx` now synchronizes original source
curve, sample, owning patch and face:
- Select a patch: select a real accepted face incident to that patch's
  current source sample and switch the local UV chart.
- Select the sample parameter: select a real accepted native
  face with that patch-local sampled node ID and XYZ and update
  the highlighted XYZ/UV sample marker.
- Pick an original native TRI face: resolve its actual source patch,
  and only if a real original source sample occurs at an actual
  corner does its sample selection synchronize. A face without
  such incidence is explicitly marked as unrelated to that
  selected source curve.
- Change the shared original source curve: preserve its own original
  incidence and reset the selection without borrowing a foreign
  sample ID.
- The original accepted face inspector shows the original
  `(patch_slot, native_patch_id, element_slot, native_element_id)`
  and original per-corner node/XYZ/UV, not the VTK cell ordinal.

The original P1/candidate XYZ and UV viewports remain completely
unchanged. The additional native scene is **only visible at
`?nativeScene=1`**. The VTK native picker remains default and
bounded experimental BVHs are unaffected.

## Reproducibility and adversarial gates

Native original C++ source CI step:

```bash
python -m tools.mesh_studio.native_seam_edges \
  --directory build/r2712-native-evidence \
  --output build/r2721-original-native-seam-edges.json
```

The Linux and Windows Python suites include six new synthetic adversarial
cases for source-edge existence, forged source sample XYZ and SHA,
crosspatch incomplete incidence, same-patch native node XYZ conflicts
and nonwelded identity. These synthetic tests are parser contracts,
**not additional scientific source observations**.

The hosted Chromium suite includes explicit opt-in, original
XYZ/UV per-patch seam overlay counts and synchronized patch/sample/face
selection, 28-patch Book fan completeness, and a forged case
where both source sample nodes appear in actual TRI faces but
never form **the same accepted TRI edge**. The latter must
be rejected before presenting any fabricated seam line.

All four jobs must pass at the exact source commit before
qualification; a default production frontend build is a
separate required gate.

## Limits and next research action

Eistute and Book still each have **one genuinely accepted original
native adaptive epoch**. These patches contain original
accepted native TRI face/edge provenance but do **not** prove
cross-epoch source curve ancestry or a continuous
source-to-approximation geometric error bound.

A current browser scene cannot claim hardware GPU present
timestamps, GPU VRAM, browser/Worker RSS or performance on
a physical Windows GPU until those measurements are performed.
R2.7.22 should instrument explicit display/interaction
benchmarks for real accepted scenes, then schedule physical
GPU tests. R2.8 scientific LOD stays **BLOCKED**.

The research PR remains draft/unmerged. No main merge, tags,
releases, source acceptance changes, physical node welding,
or promotion of staged/rejected experiments occurs in this step.
