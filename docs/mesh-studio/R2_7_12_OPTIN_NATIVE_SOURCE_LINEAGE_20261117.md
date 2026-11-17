# Mesh Studio R2.7.12 — opt-in original native accepted-epoch lineage sidecar

**Date:** 2026-11-17. **PR:** #239, research draft.  
**Worktree:** `feature/mesh-studio-r27-bvh-20261116`.  
**Scope:** serial original TRI `GeneratorAdaptive` **observability only**.
Neither original scientific policy nor the original OBJ format is changed.

## Scientific motivation

R2.7.11 located the actual native `AcceptedMeshScope::Commit()` and
`AcceptedStepCommitted` event. It also established that historical
`WriteMesh()` exports original node coordinates and connectivity,
**but discards native per-face element IDs, owning patch IDs and
original curve incidence**. Inferring native face IDs from OBJ record
positions is invalid, particularly across different adaptive steps.

R2.7.12 adds an optional research stream that samples the **live,
already committed native mesh**, not a rejected trial or a synthesized
surface. R2.7.10's P2d-1c3 five-candidate QUAD/AFT experiment remains
a separate single experiment with zero accepted adaptive steps.

## Native build flag and exact event location

`CMakeLists.txt` adds
`AP_MESH_ENABLE_RESEARCH_LINEAGE`, **OFF by default**.
Enabling it with MPI or OpenMP is a configure-time error: the initial
capture scope is real serial TRI generation only. It adds
`research/mesh_studio/native_lineage_capture.{h,cpp}` exclusively to
the explicitly configured engine, and defines
`AP_MESH_RESEARCH_NATIVE_LINEAGE=1` only for that engine.

Within `src/generator/generator_adaptive.cpp`, the only opt-in
call is after the unchanged true
`accepted_mesh = accepted_scope.Commit();` and the existing
`GlobalOutcomeKind::AcceptedStepCommitted` notification.
The hook reads `*geometry` and `*mesh_` while these native owners
are alive. There is **no hook on rejected candidates**, and no
acceptance-score, smoothing, adaptation policy, growth cap,
quadtree, AFT, convergence or scientific output modification.

Even if an optional snapshot cannot be written, the exporter is
`noexcept` and reports `R2712_NATIVE_LINEAGE_ERROR` rather than
changing the committed mesh. Optional observation failure is a
**failed evidence capture**, never evidence that the native step did
not commit.

To permit export, the researcher must additionally set the
`APMESH_RESEARCH_LINEAGE_DIR` environment variable to an explicit
local output directory. Without the flag **and** the environment
setting no sidecar is emitted. Payloads have bounded original patch,
curve, node and triangle counts. Completed output is written as
binary-LF NDJSON via a local pending file and renamed only on
successful completion; the export refuses an existing destination.

## Exact NDJSON data contract

Schema `apmesh.meshstudio.r2712.native_lineage_ndjson.v1`:

1. **Accepted header:** actual step and retry index; existing typed
   research outer session/epoch/retry if present; source patch/curve
   counts and explicit `scientific_lod_admitted=false`.
2. **One patch record per source patch:** original source **patch
   slot** plus the native patch's `GetId()`; number of owned
   submesh nodes and faces; four ordered original source-curve
   incidences, each with canonical **source curve slot**, native
   curve `GetId()`, patch-local edge number and
   `IsCurveReversed()` orientation.
3. **One face record per real native TRI:** its owning source patch
   slot, native patch ID, local element slot, actual
   `ElementAdaptive::GetId()` and three original node IDs, native
   double-precision XYZ coordinates and native per-corner UVs
   (`TriangleAdaptive::GetParametersN1/N2/N3`).
4. **Completion footer:** exact patch/face/node record totals and
   an explicit refusal of full cross-epoch certified face lineage.

The source curve slot is canonical **within the Geometry object**,
because it is derived by matching actual pointers from the geometry's
curve registry and the patch's four native curve incidences. Repeated
native `GetId()` values are preserved rather than fabricated as
unique keys; the independently scoped `(patch_slot, element_slot)`
is unambiguous within a single snapshot.

**Limitations:** this is a *source ownership observation*. Matching
source curves between two patches does not by itself certify globally
welded physical nodes. Merely recording IDs at two different epochs
does not prove that the generator's element IDs persist or that a
specific triangle is a descendant of another triangle. Native
per-face patch provenance and UV/XYZ are stronger data than an OBJ
ordinal, but still require an independently validated cross-epoch
correspondence rule. There is no continuous Bezier bound, anisotropic
metric proof or approved nonmanifold sheet welding in this stage.

## Native real-C++ replay and independent validation

`tools/mesh_studio/verify_native_lineage.py` runs the existing
`tests/quad/generator_outcome_probe.cpp` executable in a fresh
temporary directory using its original Eistute or Book
`configs/<model>/article.conf`, modifying **only paths to the
same absolute original input and temporary output**. The probe
already registers real typed research outer events and executes the
original serial `GeneratorAdaptive`, with the existing
`real_generator_outcomes=1` marker.

The independent Python verifier refuses a run unless:

- the original C++ generator process exits successfully and the
  bounded global acceptance hook reports at least one committed
  step and a real restored rejection;
- the number of newly produced accepted-step sidecars equals the
  C++ event count; no `.pending` files or exporter errors survive;
- every sidecar includes a genuine scoped event, all original
  source patches (Eistute 4, Book 28), all original source curves
  (13/85), four ordered oriented patch curve incidences, all
  source-local face slots, finite original XYZ/UV, exact counts
  and a complete last footer;
- a source curve slot maps to one native curve ID across
  all incidences (even if separate curves share a display ID);
- original source SHA-256, input/config/executable SHA-256,
  stdout/stderr SHA-256 and each original sidecar SHA-256
  are recorded, not inferred from filenames.

The test suite
`tools/mesh_studio/test_verify_native_lineage.py` contains **10
explicitly synthetic parser tests**, including duplicate JSON keys,
truncation, false LOD admission, spoofed curve incidences, wrong face
ownership, missing face slots and corrupted coordinates. These
fixtures test the validator's rejection logic only; they **do not**
represent generated meshes or performance experiments.

The Mesh Studio GitHub Actions workflow now includes an isolated
`native-lineage-optin` job: it configures and builds the **real C++**
generator in serial opt-in mode and runs both original models,
publishing qualified JSON receipts separately from Chromium and
other scientific regressions.

## Reproduction

From repository root on Linux with CMake, a C++17 compiler and Python:

```bash
cmake -S . -B build/r2712-native \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DAP_MESH_USE_MPI=OFF -DAP_MESH_USE_OPENMP=OFF \
  -DAP_MESH_ENABLE_LTO=OFF \
  -DAP_MESH_ENABLE_RESEARCH_LINEAGE=ON

cmake --build build/r2712-native \
  --target quad_generator_outcome_probe --parallel 3

python -m tools.mesh_studio.verify_native_lineage \
  --exe build/r2712-native/bin/quad_generator_outcome_probe \
  --root . --model eistute --out-dir build/r2712-native-evidence

python -m tools.mesh_studio.verify_native_lineage \
  --exe build/r2712-native/bin/quad_generator_outcome_probe \
  --root . --model book --out-dir build/r2712-native-evidence
```

**This real opt-in job has now passed**, including the source-bound
independent receipt verifier on both original model inputs. The exact
original source snapshots recorded below are new generation results,
not synthetic unit-test fixtures and not historical OBJ ordinals.

## Admission status

**R2.8 scientific LOD remains BLOCKED**, irrespective of new
source sidecars. The next gates require at least two authentic
committed epochs on each original model, verified cross-epoch
face/patch and source-curve descendant correspondence, shared-curve
physical topology and continuous geometric error bounds.
Physical GPU-present, RSS/VRAM and browser deployment remain
separate experimental hardware gates.

Keep PR #239 a research draft; do not merge, tag, release or enable
a new default selector based on opt-in provenance instruments.

## Measured real C++ source evidence — first full CI completion

[**GitHub Actions #44130426062**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44130426062)
validated code revision
`3f30f854395d30c7f7935839dd4f804f6962f12c`.
All **four** jobs finished **SUCCESS**:

| Evidence | Actual result |
| --- | --- |
| Opt-in serial original C++ engine compilation | **PASS**, real `quad_generator_outcome_probe` |
| Original source Eistute replay | **1 accepted step**, **3 rejected/restored**, **1,168 accepted TRI**, **4 source patches**, **13 source curves** |
| Original source Book replay | **1 accepted step**, **2 rejected/restored**, **4,256 accepted TRI**, **28 source patches**, **85 source curves** |
| Independent native sidecar verification | **PASS** both models; real typed global commit/restore event matches sidecar count |
| Linux scientific/VTK Python suite | **254 tests run; 4 optional skipped; PASS** |
| Windows scientific Python suite | **254 tests run; 10 environment-dependent skipped; PASS** |
| New synthetic parser negative controls | **10/10 PASS** in both Linux/Windows unit suites |
| Chromium/VTK/Worker/multi-camera suite | **42 PASS, 5 intentional skips** |
| Production TypeScript/Vite build and earlier source contracts | **PASS** |
| Physical GPU, RSS/VRAM, real presented-frame latency | **NOT MEASURED** |
| Two consecutive original accepted epochs per model | **NOT OBSERVED** |
| Cross-epoch face descendant lineage and R2.8 scientific LOD | **NOT QUALIFIED** |

Actual stdout markers from the real compiled native generator:

```text
R2712_NATIVE_LINEAGE_QUALIFIED={"accepted":1,"cross_epoch_lineage_qualified":false,"faces_per_accepted_step":[1168],"model":"eistute","restored":3,"second_epoch_seen":false,"source_curves":13,"source_patches":4}
R2712_NATIVE_LINEAGE_QUALIFIED={"accepted":1,"cross_epoch_lineage_qualified":false,"faces_per_accepted_step":[4256],"model":"book","restored":2,"second_epoch_seen":false,"source_curves":85,"source_patches":28}
```

The Linux Actions job retained the two source-qualified JSON
reports in artifact
`mesh-studio-r2712-native-original-source-3f30f854395d30c7f7935839dd4f804f6962f12c`
(artifact ID **14348759115**, short-lived 7-day retention).
The reports pin the original model input/config, actual research
executable, resolved configuration, stdout/stderr and NDJSON source
hashes. They do **not** replay a second accepted epoch.

The original **scientific/default build remains untouched by the
opt-in path** when `AP_MESH_ENABLE_RESEARCH_LINEAGE=OFF`; the
research-only module and hook are behind compile-time guards.
A separate exact native **default-off-vs-opt-in scientific binary
parity campaign** remains valuable future evidence, not a proven
result of the current opt-in-only C++ build.

**Scope decision:** the result closes native *single-accepted-snapshot*
per-face ID and source patch/curve observation for two real models.
It does not close acceptance of a second epoch, cross-epoch face
identity persistence, nonmanifold sheet node welding, continuous
Bezier error/anisotropy, physical GPU memory or R2.8 LOD approval.

## Raw source evidence retention amendment

The first passing native job verified each original NDJSON sidecar and
printed its SHA-256, but the per-model temporary working directories
were then destroyed and the Actions artifact contained only
the two JSON summary reports. **A summary hash alone is not sufficient
for external inspection of individual native face records.**

R2.7.12 therefore adds explicit post-verification persistence:
`verify_native_lineage.py` retains **each exact original NDJSON byte
stream** in the CI evidence directory and records its filename and
SHA-256 in the source-bound summary. The operation refuses overwrites
and rehashes each retained file. The separate command

```bash
python -m tools.mesh_studio.audit_retained_native_lineage \
  --directory build/r2712-native-evidence
```

reopens **both real native source files**, independently reparses all
face/patch/curve records, cross-checks their SHA-256 and all measured
source counts against their summaries, and refuses missing,
modified or unindexed sidecars. Four additional **synthetic negative
unit tests** protect that audit against false completeness and
forged count/byte claims. The CI artifact now includes **both raw
`.ndjson` and summary `.json`** and is uploaded only when the
real native jobs and the retained-byte audit succeed.

This audit establishes agreement between an original source-bound
summary and the retained bytes. It does **not** independently
authenticate a compiler executable that was not itself retained;
the CI run logs, original pinned code SHA, executable SHA recorded in
the summaries, and reproducible native build commands remain separate
elements of the provenance chain.

The amended raw-retention CI result must be checked separately from
the original passing #44130426062 before any claim that archived
per-face NDJSON evidence is downloadable.
