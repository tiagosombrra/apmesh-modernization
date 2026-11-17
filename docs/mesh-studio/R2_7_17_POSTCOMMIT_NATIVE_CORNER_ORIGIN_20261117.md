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

## Observed original C++ native evidence — research run (2026-11-17)

[GitHub Actions #44172758604](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44172758604)
at exact tested research code SHA
`7a58278e0ce09158999eee251f11bf3ba0debd7b`
independently completed **native-lineage-optin SUCCESS** and
scientific Python regression **Linux SUCCESS (304 run, 4 skips)**,
**Windows SUCCESS (304 run, 10 environment skips)**. Chromium was
**still in progress at the last verification**; no whole-workflow
all-jobs PASS is inferred before its completion.

The real original native marker
`R2717_ORIGINAL_NATIVE_CORNER_SOURCE` and separately preserved
original R2.7.12 post-commit NDJSON bytes establish:

| Accepted native step 1 source observation | Eistute | Book |
| --- | ---: | ---: |
| Actual source patches / curves | 4 / 13 | 28 / 85 |
| Actual native TRI accepted faces | 1,168 | 4,256 |
| Patches with accepted UV(0,0) ID equal to original edge-0 first-sample ID | **4/4** | **28/28** |
| Patches with accepted UV(0,0) ID equal to original shared edge-3 first-sample ID | **1/4** | **1/28** |
| Accepted UV(0,0) XYZ equal to edge-0 source sample XYZ | **4/4** | **28/28** |
| Accepted UV(0,0) XYZ equal to edge-3 source sample XYZ | **4/4** | **28/28** |

The original shared source curve slot is **3**, attached to
patch-local edge slot **3** on every original patch with
`reversed=false`. The first original Eistute patch has accepted
UV(0,0) ID **21**, equal to both source edges; its second patch
has accepted ID **90**, equal to its source edge-0 sample but
different from the common edge-3 source sample **21**.
In original Book, the first native patch has accepted ID **141**
(equal to both original source edges); its second patch has
accepted ID **181**, equal to edge-0 but different from the
common edge-3 source ID **141**. The same classification holds
for all remaining patches. This is **independently observed
post-commit accepted native identity**, not a synthetic fixture.

The real compiled serial generator OFF-versus-ON numerical
comparison continued to PASS **Eistute 21/21 scientific files
byte-identical** and **Book 17/17**. No acceptance threshold,
restored/committed decision, output geometry or measured original
scientific metric was modified for these profiles.

The source-bound R2.7.17 original report and full raw original
post-commit NDJSON files were archived as **two separate ZIPs**
in authenticated personal Google Drive
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`.
They were downloaded again from Drive and independently compared
byte-for-byte with the original GitHub Actions artifact downloads.

| Original artifact and permanent personal research copy | Bytes | Original GitHub and Drive-readback ZIP SHA-256 |
| --- | ---: | --- |
| R2.7.17 accepted corner-origin report, Actions artifact #14367354818 | 1,694 | `1dafc941f47042c2d4f86b3e4f266a7a3d228ba18ba695ee8bf107b1e6be1f6c` |
| R2.7.17 *original per-face native source* NDJSON plus source-bound summaries, Actions artifact #14367719412 | 269,875 | `a61e8dc0262a366d718b1765b249edf36ca826b2a3f00b684ed6b9c9e689043e` |

The original accepted Eistute NDJSON has SHA-256
`1484a13cee4859f05c875c65fce763ab1ddd7e1e1f96b4fc1f094a81744adcfa`;
the original accepted Book NDJSON has
`a89f4b0a60d90f1fc025f52aaac7c7f1a6a8cf7447a1c3232d8e089d1bfd3457`.
These are newly generated post-commit source snapshots under
the new optional observer, not falsely relabeled legacy bytes.
Private Drive file URLs are intentionally omitted from the
potentially public Git repository.

**Scientific decision:** R2.7.17 source endpoint-vs-accepted
corner identity observation **PASS** for the one accepted original
TRI step of Eistute and Book. The source code's proposed
`Boundary::close()` mechanism is consistent with the data; the
accepted corner's original source edge-0 logical ID is directly
observed. The actual call chain and C++ pointer ownership of
that boundary closure remain **unproven** by this observer.

R2.8 scientific LOD stays BLOCKED; physical GPU present/RSS/VRAM,
two original native accepted adaptive epochs, independent
cross-epoch face/curve descendant identity and continuous error
bounds stay OPEN. No mesh welding, renumbering, source-policy
adjustment, main merge, tag, default-picker promotion or release.
