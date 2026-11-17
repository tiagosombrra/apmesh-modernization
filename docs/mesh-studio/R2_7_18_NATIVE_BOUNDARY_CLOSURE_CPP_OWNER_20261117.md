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

## Admission and limitations

**Stage is implementation-only until full CI finishes**.
The scientific conclusion must be grounded in the exact
observed C++ pointer-comparison results, the actual provisional
close events, their counters and source hashes. Source-level
explanations are only plausible until native evidence confirms
those specific comparisons.

VTK remains native/default, both BVH selectors experimental and
bounded/opt-in, PR #239 draft/unmerged, no main merge, tag
or release. R2.8 scientific LOD remains **BLOCKED** until
multiple genuinely accepted original native adaptive epochs,
verified cross-epoch face/curve descendant identity,
continuous geometric error bounds and physical Windows
GPU/present/RSS/VRAM measurements.
