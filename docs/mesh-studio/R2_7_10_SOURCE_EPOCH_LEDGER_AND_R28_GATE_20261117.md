# Mesh Studio R2.7.10 — original source/epoch audit and R2.8 admission ledger

**Date:** 2026-11-17.  
**Repository:** `tiagosombrra/apmesh-modernization`  
**Isolated branch:** `feature/mesh-studio-r27-bvh-20261116`  
**PR:** https://github.com/tiagosombrra/apmesh-modernization/pull/239 — draft, not merged  
**Disposition:** independent source artifacts are real, but **R2.8 scientific LOD acceptance remains BLOCKED**.

## 1. Why this is the next scientific gate

Earlier R2.7.5–R2.7.9 browser checks established small-source original TRI
display-picking agreement with VTK and source-SHA/camera controls. The R2.7.6
study also correctly indexed a larger archived Eistute OBJ without treating
its face-record ordinals as canonical generator IDs. The missing prerequisite
for a scientific LOD claim is **native, independently verifiable adaptive
epoch acceptance and source-face/patch/curve lineage**, not another synthetic
performance benchmark.

A source artifact can be genuine, hash-verified and geometrically useful
while still **not** being an accepted adaptive output. This ledger explicitly
tracks that difference.

## 2. Five real Bézier outputs: one controlled experiment

The source-root `tools/mesh_studio/fixtures/real_p2d1c3` contains five
real C++ application artifacts retained from original PR #235 CI run
https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43664129060
at generator commit
`27851df2625e0c0b37e12023af699a01f3d0304c`.

| OBJ | Physical vertices | QUAD | Native AFT TRI | Total faces | Scientific status |
| --- | ---: | ---: | ---: | ---: | --- |
| control.obj | 69 | 42 | 36 | 78 | Controlled **nonadaptive** output |
| band.obj | 93 | 62 | 44 | 106 | **Staged, not accepted** |
| west.obj | 109 | 75 | 50 | 125 | **Staged, not accepted** |
| north.obj | 107 | 71 | 54 | 125 | **Staged, not accepted** |
| both.obj | 117 | 82 | 52 | 134 | **Staged, not accepted** |

These are five **alternative outputs of one experiment**, not five
independent experimental replicates. They share the fixed16 source
boundary control, a single pinned 4×4 Bernstein Bézier source net
and an independent 64×64 / 4,096-UV-site sampling oracle. The existing
`qualify_real_study()` verifies original SHA-256 digests, source report
digest, UV/XYZ consistency, physical geometry, original source
edge-incidence and area constraints, numerical residuals and
multiobjective profile assertions.

The source report and existing verifier record
**`accepted_adaptive_epochs=0`**. More elements or lower sampled
interpolation error do not establish an adopted adaptive transition.
The group labels `QUAD` and `TRI_AFT` are element **types** on a
single source patch, not independent source-patch IDs. Ordinal face
positions differ among alternative candidate OBJs, and there is no
qualified cross-candidate native face-ID lineage in this corpus.

## 3. Independent larger Eistute archive

The original reference `reference/eistute_stage4.obj` is a real
legacy archive with:

- 3,691 original vertex records;
- 7,184 original TRI face records;
- SHA-256
  `378b62da75400c1bfe6871be29d22d8b14d6d6e054a1fa79de062de35c95f9eb`;
- Git blob SHA-1
  `8f54a95e0192e9af3e76ba5d9f28202cd47dae79`;
- stage-4 archived numerical targets
  (normalized error 0.036712, total reduction 96.3288%,
  q≥0.60 share 58.6303%, mean shared-curve compatibility target 0.0).

The new audit verifies **all OBJ vertex/face records and indices**
as well as the sidecar and matching archived numerical CSV row.
It verifies its original Git blob digest; previous cross-revision
Git checks showed the blob is identical in the published upstream,
original modernization import, and current branch.

**Unresolved historical manifest discrepancy:** `MANIFEST.sha256`
declares `c0c55cbdf473233408dd21a9a17b542adee12f969e187abaea8116f103080e18`
for the same path, which differs from the actual/published matching
blob's SHA-256 `378b62da...`. The ledger explicitly checks
that the original historical manifest value **remains untouched** and
records the mismatch rather than silently rewriting the manifest.

The reference is a **saved stage-4 candidate**, not an independently
verified accepted transition. In fact, all **three archived CSV rows**
matching stage `4`, `7184` TRI and the pinned numerical targets record
`budget_final_status=rejected`, `step_mode=refine` and
`stop_reason=hybrid_criterion_rejected`. This is **stronger documentary
evidence of source-reported rejection**, now checked by the ledger, but
it does **not** constitute an independently replayed native event trace.

The original stage counter is not a native acceptance decision oracle.
Face order in an OBJ is not a canonical cross-epoch generator face identity.
The archive contains no independent per-face patch and shared-curve
semantic records that would establish continuous nonmanifold sheet
correspondence.

Its archived recorded compatibility target is a claim about the
historical run, **not** a newly measured interpatch error bound or
a direct Bezier continuity proof by Mesh Studio.

## 4. Implementation

`tools/mesh_studio/source_epoch_inventory.py`

- Reuses **the existing real-source independent oracle**,
  `real_candidate_study.qualify_real_study()`, rather than
  building a weaker substitute for 4×4 Bernstein source geometry;
- pins original generator commit, CI run, Linux/Windows archive IDs,
  generator report SHA and five exact source OBJ digests;
- writes a read-only JSON classification for each candidate with
  original physical inventory, source error measurement classification
  and explicit absence of accepted adaptive-epoch numbers;
- independently checks the original Eistute archive and historical
  manifest contradiction; does not import or normalize its original
  face IDs into the P1/Band viewport source-ID contract;
- defines an explicit `r28_gate` blocked on the five requirements
  listed below. It rejects a manually edited ledger that incorrectly
  claims accepted adaptive epochs, five independent runs,
  accepted candidate states, cross-epoch face IDs, continuous error
  qualification or legacy archive admission.

`tools/mesh_studio/test_source_epoch_inventory.py`

The scientific regression runner now discovers eight bounded tests,
including negative probes for forged accepted states, forged independent
runs, fabricated lineage/bounds, mutated archived OBJ bytes and
deterministic read-only admission. Mutation testing operates on
in-memory dictionaries or temporary file copies only.

**CI integration:** `.github/workflows/mesh-studio-validation.yml`
on Linux reconstructs
`build/mesh-studio/r2710-source-epoch-inventory.json` and
retains it as a short-lived
`mesh-studio-source-epoch-inventory-<SHA>` Actions artifact.
Linux and Windows scientific regression jobs exercise the new Python
tests. Existing Chromium/VTK/Worker tests continue unchanged.

Run from the repository root:

```bash
python -m tools.mesh_studio.source_epoch_inventory \
  --output build/mesh-studio/r2710-source-epoch-inventory.json

python -m unittest tools.mesh_studio.test_source_epoch_inventory -v
```

This is a **read-only data analysis**. Neither the five original
candidate OBJ files nor the Eistute archive, C++ scientific generator,
published manifest or main branch is changed.

## 5. Exact R2.8 scientific admission blockers

Current gate `apmesh.meshstudio.r28.scientific_lod_admission.v1`
has `eligible_for_r28_lod=false` because:

1. **NO_ACCEPTED_ADAPTIVE_EPOCH:** five alternatives have zero adopted
   adaptive epochs; an archived Eistute candidate is not evidence of an
   accepted epoch;
2. **NO_NATIVE_EPOCH_TRACE_AND_DECISION_ORACLE:** absence of a qualified
   native, generation-attested acceptance-event trace;
3. **NO_MULTIPATCH_GENERATOR_FACE_PATCH_CURVE_LINEAGE:** missing original
   source-face identities linked across accepted epochs and shared
   source-curves/patch ownership;
4. **NO_QUALIFIED_LARGER_ACCEPTED_SOURCE:** no larger authenticated
   accepted mesh demonstrating the intended source topology;
5. **NO_CONTINUOUS_GEOMETRIC_ERROR_BOUND:** existing 4,096-site
   discretely sampled Bernstein error is useful but does not establish
   a continuous, patch-aware geometric error bound.

All five blockers must be addressed **with new independent native
generator evidence**, not with altered status strings, a larger OBJ
count or a software-generated LOD visualization. Performance/VRAM,
actual GPU-presented frame latency and physical Windows/Linux
workstation runs remain additional independent qualification gates.

## 6. Decision

This stage consolidates source evidence and makes scientific admission
machine-checkable. It **does not authorize** R2.8 geometric decimation,
source patch welding, all-quad meshing, anisotropic claims, default
fast XYZ picker promotion, synchronous cap increase, merge, release
or C++ generator changes.
