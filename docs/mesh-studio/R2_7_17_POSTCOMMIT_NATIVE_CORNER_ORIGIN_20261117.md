# Mesh Studio R2.7.17 — real native accepted-corner source observation

**Date:** 2026-11-17. **Research branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** #239 draft/unmerged. **Scope:** C++ serial original TRI
`GeneratorAdaptive`, in the already OFF-by-default post-commit
R2.7.12 source-lineage exporter only.

## Specific native identity question

Real original R2.7.15 and R2.7.16 Eistute/Book source snapshots show a
single original source curve (slot 3) on patch-local edge 3 of every
patch, with nonreversed incidence. All 4 Eistute or 28 Book patches
share the same real curve sample chain and original XYZ. However,
its `t=0` endpoint has one **different native logical ID** per patch;
all 10/12 other samples have an ID shared by the respective patches.
Original native sampled geometry and canonical t match pairwise
exactly for these one-step observations.

The serial `Adapter::AdaptDomain` currently walks edge-3 source
parameters in reverse order **excluding its last endpoint**, then
`Boundary::close()` closes the UV contour using the first boundary
vertex previously created on edge 0. This mechanism could produce
an accepted UV(0,0) vertex whose copied original ID belongs to
edge-0's source endpoint rather than shared edge-3's first point.

This stage tests that explanation against actual source-curve point
IDs and actual accepted native face-corner IDs, with no correction.

## New real C++ observer, observational boundary and schema

`research/mesh_studio/native_lineage_capture.cpp` is compiled only
with `AP_MESH_ENABLE_RESEARCH_LINEAGE=ON` in a **serial**, isolated,
opt-in native research build. The default is OFF; MPI/OpenMP with the
observer are still rejected. The existing emission site remains
**after the actual** `AcceptedMeshScope::Commit()`, with its existing
`noexcept` failure handler. No original C++ generator, Adapter,
Boundary, AFT, curvature, policy, budget, quadtree, native face
constructor or scientific file writer is changed.

Within each real native accepted R2.7.12 patch's original
`source_curves` incidence, the new optional append-only field
`r2717_original_curve_endpoints` records **both live, original
source point-list endpoints**: original sample ID, XYZ, actual stored
parameter, and original point-list slot. These values are read from
`CurveAdaptiveParametric` and its live `CurveAdaptive` samples,
without sorting, copying into a mesh, editing a point, or retaining
an address. Source curve sample count must agree with its stored
parameter count; invalid/absent original source samples invalidate
**optional research capture only**, never the accepted step.
The original header explicitly declares
`r2717_corner_observer=native_postcommit_source_curve_endpoints_v1`.

The enclosing R2.7.12 schema and accepted face records are preserved
for backward-compatible parsing. The raw original R2.7.12 NDJSON
will now include **additional** post-commit source evidence, so
its new SHA cannot be confused with prior R2.7.12 original snapshots.
The raw bytes and SHA-256 of **each new original source snapshot**
remain mandatory and self-contained. The existing native comparison
still independently verifies numerical neutrality against a
separately compiled instrumentation-OFF real generator.

## Independent R2.7.17 original-source validator

`tools/mesh_studio/native_corner_origin.py` begins with R2.7.12's
complete original accepted NDJSON and source-bound digest re-audit,
then rechecks each native source face, patch and curve record. It
fails closed for missing observer header/fields, corrupt/non-finite
source samples, missing or ambiguous actual accepted UV(0,0) corner,
and inconsistent samples for a source curve owned by more than one
patch.

For each source patch the original face UV(0,0) vertex's **real
accepted native logical ID and XYZ** are compared to the two
original live curve samples incident to that patch's local UV(0,0)
corner: local source edge 0 and local source edge 3. The observer
respects the recorded original incidence reversal when interpreting
local parameter zero. Individual per-patch records and aggregate
match counts are preserved, including differences. A desired
edge-0 match is **not** hard-coded as a condition for a tool PASS.

`test_native_corner_origin.py` exercises nine **explicitly
synthetic** parser and classification tests only. They check
two-patch edge-0 identity, reversed endpoints, alternative real
edge-3 identity, missing observer records, cross-owner spoofed
samples, invalid parameter, ambiguous UV corner and contradictory
native XYZ. Synthetic fixtures do **not** count as proof of native
generator behavior.

## Real CI acceptance and exclusions

The `native-lineage-optin` job compiles the actual serial native
original generator and runs Eistute and Book with their **original
research article configurations**, independently validates the
new R2.7.17 observation for each source-verified accepted step,
and retains `build/r2717-native-corner-origin.json` as a separate
14-day Actions artifact. It must also re-pass the original
R2.7.12/R2.7.13 acceptance, native OFF/ON 21+17 source scientific
output-file byte parity, independent Linux/Windows Python regression
and actual Chromium browser CI.

Reproduce after Eistute/Book native source evidence has been
generated with the R2.7.17 opt-in C++ observer:

```bash
python -m unittest tools.mesh_studio.test_native_corner_origin -v
python -m tools.mesh_studio.native_corner_origin \
  --directory build/r2712-native-evidence \
  --output build/r2717-native-corner-origin.json
```

**A successful audit is observation, not physical ownership proof.**
Neither original C++ pointer address equality nor an independent
instrumented trace of `Boundary::close()` is reported here. Even
exact original ID and XYZ equality in one accepted snapshot does
not prove global physical welding across patches, an immutable
source-point alias, nonmanifold sheet topology, or cross-epoch
descendant correspondence. No native nodes are merged or renumbered.

R2.8 scientific LOD stays **BLOCKED** (only one original accepted
native step per Eistute/Book, no proven cross-epoch descendants
or continuous surface error bounds). Physical Windows GPU
present/RSS/VRAM is a separate unresolved gate. VTK remains the
default, both experimental BVHs opt-in/bounded; PR stays draft,
unmerged; no tags or release.

## Qualification log

R2.7.17 implementation submitted for full experimental qualification.
**No real native PASS or corner-origin match result is claimed until
a successful run and independently inspected original native
R2.7.17 marker establish both models' measured counters.**
