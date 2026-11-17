# Mesh Studio R2.7.18 — original native Adapter closure and C++ node object ownership

**Date:** 2026-11-17. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** #239, draft and unmerged.
**Research scope:** original serial Eistute/Book TRI, opt-in post-commit source
observer and separate provisional Adapter event observer, both disabled by
default. No change to the original mesh generator acceptance policy.

## Research question and evidence separation

R2.7.17 proved that the real accepted UV(0,0) corner's logical native
node ID matches original **edge 0** in 4/4 Eistute and 28/28 Book
patches; it matches the canonical shared **edge 3** sample only 1/4
and 1/28. All corresponding XYZ samples were equal. The source's
`Adapter::AdaptDomain` visits edge 3 in descending curve-parameter
order, omitting the terminal sample, and calls
`Boundary::close(last_curve, reversal)` to connect its final
vertex to the first UV boundary vertex from edge 0.

R2.7.18 deliberately audits two **distinct lifetimes**:

1. **Provisional Adapter local attempt:** executes and observes the
   **actual original** `Boundary::close()` call. It records actual
   returned bool, local attempt number, patch index, adaptive step,
   retry index, count of boundary vertices, first/last UV, the native
   logical ID of the already mapped first boundary node, and the
   original edge-0/edge-3 local-t0 source IDs. It does not mark any
   local attempt as a globally accepted native commit.
2. **Actually accepted native step after `AcceptedMeshScope::Commit()`:**
   a distinct read-only C++ observation finds each accepted
   triangle's real UV(0,0) vertex, independently finds its
   **SubMesh-owned `NodeAdaptive` object** through
   `SubMesh::GetNoh()`, and tests the actual observer adjacency to
   that original triangle via `NodeAdaptive::GetElements()`.
   It then compares C++ object-pointer equality **in memory only**
   against the corner objects of prior accepted patch submeshes and
   against both live original source curve endpoint objects.

Comparing original `TriangleAdaptive::GetNoh()` values does **not**
establish pointer identity, as that function returns a node **by
value**. This experimental observer deliberately reads actual
owned `NodeAdaptive*` pointers from the accepted SubMesh;
**no numeric pointer address is serialized or disclosed**.

The observed pointer equality result is restricted to the current
native source accepted snapshot and live object lifetimes. A
pointer comparison is not a proof of continuous surface matching,
a longitudinal identity across adaptive epochs or a guarantee
of non-manifold welded-node topology.

## Source and provenance architecture

The `AP_MESH_ENABLE_RESEARCH_LINEAGE=ON` guard already requires a
serial, MPI/Omp-disabled research build. The newly instrumented
`src/adapter/adapter.cpp` branch invokes the **same** original
`Boundary::close` and emits `R2718_ADAPTER_BOUNDARY_CLOSE=` JSON
after the call, observing its already owned `vertex_to_node`
map and UV boundary vertex sequence. The corresponding default-OFF
code path preserves the original call, and is not replaced by
the logger. Neither boundary topology nor the adaptive front is
mutated by the observation.

`research/mesh_studio/native_lineage_capture.cpp` appends the
new `r2718_accepted_cpp_node_owner` field to each original
source patch record, and a new typed `r2718_owner_observer`
marker to the accepted-commit header. The field records actual
native ID, SubMesh node slot, real triangle adjacency, C++ pointer
equality with prior accepted patch corner objects, and equality
with the two original live source curve endpoint objects. The
R2.7.12 original schema, original faces/curves and all existing
source gates remain intact.

The original native generator's **complete stderr** is separately
retained as `r2718-<model>-original-native-generator-stderr.log`
rather than extracting unverified lines. Its SHA-256 is recorded
in the original generator's independent source summary and
re-validated against the existing native process
`native_stderr_sha256` digest. This also retains failed,
unselected and retried attempts, not just convenient events.

The independent `tools/mesh_studio/native_boundary_ownership.py`
audits all original retained R2.7.12 face, patch, curve and
post-commit C++ owner bytes before reading raw original stderr.
It requires actual Adapter close markers to have valid source
step/patch and local attempt scopes, authentic first-corner
mapped IDs, no accidental claim of global acceptance, and a real
success return. It then compares provisional source-scope
`(step, patch, node ID)` to real accepted observations.

**A matching attempted closure ID alone is not proof that the
attempt containing that event was selected for the global
accepted native commit.** The report explicitly preserves the
number of provisional events and flags lack of proven local
selection and pointer lifetime across the final commit.
No "success" claim is built by cherry-picking a synthetic
accepted face or by equating equal XYZ to a common C++ object.

## Fail-closed test and scientific CI obligations

`test_native_boundary_ownership.py` provides **12 synthetic unit
tests only**: valid accepted SubMesh owner adjacency; actual
provisional closure parsing; extra retries not promoted to
global commits; injected fake acceptance; bad owner adjacency;
native ID mismatch; impossible node slot; missing C++ observer;
falsified native ID comparison; duplicate JSON keys; missing
real event; and observed pointer aliasing reported without
topological certification.

The isolated native source CI must run:
- Recompile the actual original serial Eistute and Book
  `GeneratorAdaptive`, with opt-in observation ON.
- Verify their original genuine accepted/rejected/restored
  outcomes, R2.7.12 face/curve/source/acceptance SHA-pinned
  receipts, R2.7.13 scientific OFF/ON raw-byte parity and
  R2.7.14–R2.7.17 native source diagnostics.
- Execute the new R2.7.18 auditor on both native source sets
  and preserve a 14-day JSON receipt, while preserving full
  raw original stderr plus raw source NDJSON in the original
  7-day source-evidence artifact.
- Re-run independent scientific regression tests for
  Linux/Windows and real Chromium browser tests.

Reproduction after original C++ source capture:

```bash
python -m unittest tools.mesh_studio.test_native_boundary_ownership -v
python -m tools.mesh_studio.native_boundary_ownership \
  --directory build/r2712-native-evidence \
  --output build/r2718-boundary-cpp-ownership.json
```

## Independently inspected authentic native preflight — not final CI

[Original GitHub Actions run #44192451844](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44192451844)
at code revision `d2e433d8ae52312e3f84d669aba9fc5b5a0cacd4`
successfully completed the **actual compiled original serial C++
native-lineage job**. Its retained original, source-bound raw C++
postcommit NDJSON and full generator stderr were downloaded
as original source ZIP artifact #14376578452 and re-parsed
independently. Raw original ZIP SHA256:
`d61616b889378d69167403f6bd23704ba164c8feea8a1a8fc1ab1fe00f06f5f8`.

| Actual original observation | Eistute | Book |
| --- | ---: | ---: |
| Real provisional `Adapter::AdaptDomain` boundary closes across all steps/retries | **104** | **84** |
| Actual successful `Boundary::close()` return values | **104/104** | **84/84** |
| Local closure events scoped to globally accepted *step number* 1 | **24** | **28** |
| Original accepted native adaptive steps | **1** | **1** |
| Live accepted original SubMesh corner C++ owners examined | **4** | **28** |
| Actual owned-corner node ↔ real accepted triangle observer adjacency | **4/4** | **28/28** |
| C++ node pointer aliases among prior observed patch SubMesh owners | **0** | **0** |
| Accepted C++ node object pointer equal to either live source-curve endpoint object | **0** | **0** |
| Two *original source curve* endpoint pointers identical (edge 0 / edge 3) | **1/4** | **1/28** |
| Accepted patch corner ID corroborated by same-step/same-patch provisional `Boundary::close` | **4/4** | **28/28** |
| Same native ID provisional closure witnesses on accepted step 1 | **24** | **28** |

For Eistute, the original 24 same-step closure events consist
of **six local attempts per original patch**, not 24 accepted
patch meshes. All four original accepted patch IDs were observed
in those six provisional closures. The original Book native
step 1 had **one** matching closure per patch.

Actual Eistute provisional closure events by adaptive step:
**step 1: 24, step 2: 8, step 3: 8, step 4: 64**. Actual Book
events by step: **step 1: 28, step 2: 28, step 3: 28**.
Later steps were not accepted in the original native experiment;
neither rejected candidate IDs nor raw C++ object pointers are
promoted to accepted Mesh Studio ancestry.

Independent byte-level source verification:
- Eistute authentic native original stderr SHA256:
  `e49e97045b15b208afda998ebee9eef5f916b6440d47c4739a11f86ba67260b9`;
  real original accepted C++ NDJSON SHA256:
  `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`.
- Book authentic native original stderr SHA256:
  `0e03e7c84fcd02ee3bdc8b9e82a40aacd041d99706102fecbb27cc02115e06cd`;
  real original accepted C++ NDJSON SHA256:
  `e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a`.

Both stdout/stderr and accepted NDJSON hashes were independently
recomputed from the **raw GitHub original byte artifact** and
matched the original native source-bound summary. This is
positive evidence of authentic C++ pointer comparison and actual
provisional closure execution, but is **not a final R2.7.18
all-jobs PASS** until the added R2.7.18 validator, source
artifact and full Linux/Windows/browser workflow
at its exact source revision complete successfully.

## R2.7.18 original compiled C++ native and numerical qualification

The **actual native R2.7.18 workflow job** and both independent
scientific regression jobs at source revision
`f87528c293fbf73837f73e911cc2e1a1129c9ece`
completed **SUCCESS** in [Actions #44192959042](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44192959042).

- Linux scientific regression: **316 Python tests run, 4 optional skipped, PASS**.
- Windows scientific regression: **316 Python tests run, 10 environment skipped, PASS**.
- Compiled actual original C++ Eistute and Book TRI with opt-in
  read-only `Boundary::close` and accepted C++ SubMesh ownership
  observers: **PASS**.
- Original R2.7.12 source SHA, all genuine accepted faces,
  R2.7.14–R2.7.17 source audits, the new original-stderr
  authenticity gate, and R2.7.18 independent source-pinned
  ownership validator: **PASS**.
- Actual Eistute OFF/ON scientific outputs **21/21 byte-identical**;
  actual Book **17/17 byte-identical**.
- Chromium: **42 browser smoke tests PASS**; the
  `browser-spike` job completed SUCCESS.
- **Whole Actions #44192959042: 4/4 jobs SUCCESS**, independently
  observed at exact tested source revision
  `f87528c293fbf73837f73e911cc2e1a1129c9ece`.

The exact `R2718_ORIGINAL_BOUNDARY_CPP_OWNERSHIP` marker:
- Eistute original accepted step 1: **4 actual owned,
  triangle-adjacent accepted corner objects; 0 cross-patch
  observed C++ pointer reuse; 4 original accepted native IDs
  correlated to same-step provisional Adapter closures;
  104 total original provisional closure events.**
- Book original accepted step 1: **28 actual owned,
  triangle-adjacent accepted corner objects; 0 cross-patch
  observed C++ pointer reuse; 28 original accepted native IDs
  correlated to same-step provisional Adapter closures;
  84 total original provisional closure events.**

The full independent source-bound R2.7.18 report retains every
original event and every actual accepted node observation, explicitly
declares no global node welding and no observed continuity of
the provisional C++ pointer into global acceptance.
No ID or geometry change was applied.

Two new original GitHub Actions ZIP artifacts were copied to
the authenticated personal doctorate Drive results folder,
then **downloaded again** and verified as exact original bytes:

| Source artifact | Original ZIP bytes | Original artifact and Drive-readback SHA256 |
| --- | ---: | --- |
| R2.7.18 original report #14378930063 | 5,254 | `bce1eb6b0eeada6027947b33e03875d3b98c3d69be9e4f451ec52459ea5c890c` |
| R2.7.18 original raw accepted native NDJSON plus source-bound summaries **and complete original process stderr** #14377818017 | 279,380 | `c984adf6f01c63fb87caaf7ad009c62b2401e9ca1e8a0802469ef5a37e0a3e5b` |

The raw artifacts were retrieved and re-parsed independently;
source-bound original process stderr and raw accepted NDJSON
SHA-256 values matched their original native summaries.
Private Drive URLs are not embedded in potentially public repository
documentation. The original native data is deliberately retained
separately from the derived JSON to support independent re-audit.

**Scientific decision:** R2.7.18 confirms actual **local
SubMesh-owned physical node objects** (at original accepted
UV(0,0) corners) and real provisional runtime invocation of
`Boundary::close` with the edge-0 ID carried into the
first local boundary node. It does not certify cross-patch
physical node welding, exact surviving attempt-pointer
continuity across acceptance, or any LOD descendant.
No numerical generator policy or original science output changed.

## Admission and limitations

**R2.7.18 certified PASS for actual one-epoch native closure
observation and C++ corner-owner identity** on original Eistute and
Book, with all four independent Actions jobs successful.
The scientific conclusion is grounded in directly observed C++
pointer-comparison results, actual provisional closure events,
exact source digests and full raw-stderr and native-NDJSON archives.
This does not certify which original local attempt was selected
or pointer identity through rollback and final commit; it does
not certify general global node welding, cross-epoch descendants
or continuous source-surface fidelity.

VTK remains native/default, both BVH selectors experimental and
bounded/opt-in, PR #239 draft/unmerged, no main merge, tag
or release. R2.8 scientific LOD remains **BLOCKED** until
multiple genuinely accepted original native adaptive epochs,
verified cross-epoch face/curve descendant identity,
continuous geometric error bounds and physical Windows
GPU/present/RSS/VRAM measurements.
