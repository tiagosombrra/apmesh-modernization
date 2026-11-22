# Mesh Studio R2.7.11 — audit of actual native TRI acceptance lifecycle and historical epochs

**Date:** 2026-11-17. **PR:** #239 (draft, unmerged).
**Scope:** read-only bridge from exact original research-native CI reports and
source code to a machine-checkable **historical** acceptance ledger. No new
GeneratorAdaptive run or generator patch in this stage.

## The native acceptance decision exists and is observable

Current `src/generator/generator_adaptive.cpp` has one serial
`accepted_mesh = accepted_scope.Commit();` within
`if (score_ok || small_mesh_progress_override)`. An existing
`GlobalOutcomeKind::AcceptedStepCommitted` record follows the
actual commit. On rejection, it calls
`restore_geometry_submeshes(geometry, accepted_mesh)`, then
`restore_curve_snapshots(geometry, accepted_curve_snapshots)`,
then records `GlobalOutcomeKind::RejectedStepRestored`.

The existing `research/quad/global_outcome.h` implements a
no-allocation, bounded `GlobalOutcomeLog` with **capacity 128** and a
truncation flag. An event recorded without a real `Commit` is not
accepted. A candidate saved as OBJ after rejection is **not** an
accepted epoch.

The native original TRI `GeneratorAdaptive::WriteMesh(MeshAdaptive*, int)`
does hold element and patch data in memory but **only serializes OBJ
vertex positions and triangle connectivity**. It deduplicates vertices
by original `NodeAdaptive::GetId()`, then writes `f` records using
local ordinal indices. It **does not serialize**
`ElementAdaptive::GetId()`, `Patch::GetId()` or oriented
source-curve membership with each face. Hence even original
native application output cannot be interpreted as a cross-epoch
source-face ID oracle from OBJ record position alone. The bridge now
checks this exact original writer overload and fails closed if the
writer changes. An **optional, separately validated native face/patch
lineage sidecar** is needed in a later step, not silently inferred
from these OBJs.

R2.7.11 verifies original source Git blob hashes, existence, uniqueness
and relative order of these hooks. These static checks establish the
location of the real producer branch, **not execution of the code**.

## Archived source-qualified native TRI results already exist

Original QUAD research R2c-13 report
`docs/research/quad/evidence/R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS_20261113.json`
was generated at source commit
`082ecd0408d31808dae5d629e711be99fd01d1a7`, successful
[Actions #43502743922](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43502743922),
original artifact #14074978033.

| Original model | Source patch count | Original curve count | Committed original TRI steps | Rejected/restored | Original patch boundary witnesses |
| --- | ---: | ---: | --- | ---: | ---: |
| Eistute | 4 | 13 | [1] | 3 | 960 |
| Book | 28 | 85 | [1] | 2 | 1008 |

These are actual original `GeneratorAdaptive` CI results from the
**earlier** R2c-13 campaign. The GitHub Actions run's successful
conclusion and source commit were verified independently from GitHub
during this stage; the new CI itself only pins/rechecks the archived
report bytes, source code hooks and internal provenance relationships.

Neither model achieved two distinct accepted adaptive steps in the
pinned article profile. No second committed epoch can be inferred from
a saved rejected candidate, successful CTest, source OBJ ordinal,
element-count increase or saved stage index.

The subsequent R2c-14 source rejection forensics was performed in
[Actions #43504972443](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443);
it reported Eistute original step 4 candidate growth **6.17808×**
and Book step 2 candidate growth **4.64615×**, both still rejected.
Forensics provides useful diagnostic metrics but no exact replay of
every original Boolean acceptance subgate.

## Reconcile with R2.7.10: these are distinct experiments

R2.7.10's **one controlled Bézier P2d-1c3 source experiment** has five
physical outputs, four of which are staged/unaccepted and **zero**
accepted adaptive epochs. That experiment is not the original
historical TRI Book/Eistute native adaptation experiment.

It is scientifically correct to say simultaneously:

- Original pinned TRI GeneratorAdaptive research has **one** accepted
  step #1 per Eistute and Book, with earlier archived native event
  evidence and original patch/curve observation witnesses;
- The newer controlled P2d-1c3 QUAD/AFT experiment has **zero**
  accepted adaptive epochs;
- The legacy Eistute stage-4 OBJ is a **rejected historical saved
  candidate**, as recorded by all three matching archived CSV rows;
- No studied native source currently meets the **two accepted epoch
  per original model** criterion and verified per-face/patch/curve
  cross-epoch lineage required for scientific R2.8 LOD.

Original patch-boundary witnesses in R2c-13 are not equivalent to
canonical per-face persistent identities or approved shared-curve
physical node welding.

## Implementation and strict negative controls

`tools/mesh_studio/native_epoch_bridge.py` produces
`apmesh.meshstudio.r2711.native_epoch_evidence_bridge.v1` JSON:

- pins the exact Git blob SHA-1 of the **actual generator source**,
  bounded event hook header, R2c-13 original native evidence JSON
  and R2c-14 rejection forensic JSON; Windows CRLF normalization is
  used **only for comparing the original canonical Git bytes**, never
  to rewrite any source;
- checks `Commit`/accept and restore/reject hook order, uniqueness,
  bounded event-truncation rules;
- independently checks 4/28 source patches, 13/85 source curves,
  step [1], original witness and rejection counts, native run SHA,
  CI run ID/status and original artifact identity;
- reconciles the R2.7.10 P2d-1c3 read-only source inventory and
  asserts it remains zero accepted epochs;
- sets `new_native_execution_in_this_run=false`,
  `original_tri_two_accepted_epochs_per_model=false` and
  `scientific_r28_geometry_lod_admitted=false` without
  a user override.

`tools/mesh_studio/test_native_epoch_bridge.py` adds 12 independent
negative/positive unit tests. It rejects forged second commits,
foreign native revision/artifact, corrupted original model/curve
counts, mutated rejection forensics, missing/duplicated native hook
changed bounded-log capacity, and source writer provenance
assumptions. The writer mutation tests are in-memory source contracts,
not a new native build or modified production output.

The existing Mesh Studio Linux and Windows scientific test discovery
runs this suite. CI Linux also writes and retains a short-lived
`build/mesh-studio/r2711-native-epoch-bridge.json` receipt as a
separately labeled GitHub Actions artifact.

Run at repository root:

```bash
python -m tools.mesh_studio.native_epoch_bridge \
  --output build/mesh-studio/r2711-native-epoch-bridge.json

python -m unittest tools.mesh_studio.test_native_epoch_bridge -v
```

## Next evidence required, not automatically qualified

1. **New native reproducible serial runs** of the unchanged actual
   generator, with bounded, nontruncated acceptance/rejection events
   captured after real commits/restorations, plus source checkout SHA,
   compiler, configuration, and original input hash.
2. **Two distinct original accepted commits per model** with
   strictly increasing actual step and outer epoch IDs, and a
   separate digest for each committed physical mesh. Existing
   historical single-step evidence is useful but insufficient.
3. Native per-face element ID, owning original patch ID, source
   boundary curve ID and oriented incidences, plus exact mapping
   across consecutive **accepted** epochs; OBJ face-record ordinals
   do not substitute.
4. Independent quality/error and shared-curve geometric checks with
   a continuous or demonstrably bounded approximation error.
5. Separately qualified physical desktop/GPU-present/RSS/VRAM data
   before promoting the experimental visualization picker.

**No acceptance gates, adaptive thresholds, source model geometry,
C++ generator, VTK default selection, 2,048-face sync bound, main
branch, or release are changed by R2.7.11.**


## Validated native-ledger CI evidence and unresolved browser gate

Final scientific code revision: `157ef71a9b6e71aa386d30133529bd377d10747c`.

[Actions #44098287002](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44098287002)
has qualified the R2.7.11 Python and original-source bridge test suite
on **Ubuntu 24.04 (244 tests run; 4 optional skipped)** and
**Windows Server 2022 (244 tests run; 10 optional skipped)**.
Both scientific-regression jobs completed **SUCCESS**. The **12/12**
new native epoch/writer tests passed and the Linux read-only
`r2711-native-epoch-bridge.json` receipt was generated as a retained
short-lived Actions artifact.

The exact verified receipt reports original archived committed steps
`{"book":[1],"eistute":[1]}`, with the original Bézier P2d-1c3
qualification separately at zero accepted epochs, and
`native_run_replayed_this_ci=false`,
`original_models_two_commits=false`,
`r28_admitted=false`.

An initial source-anchor audit erroneously matched a prior
`restore_geometry_submeshes` occurrence before the targeted
rejection arm, causing failures on both operating systems in
[CI #44097431643](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44097431643).
The corrected verifier explicitly scopes restoration checks
**after** the current `if (!accepted_step)` branch. No C++ generator
files, numerical acceptance policy, patch geometry or original research
artifacts were changed.

**The Chromium frontend job on the final CI was still pending its
completion at the last recorded check**. Do not cite a successful
browser end-to-end result from this run unless its job finishes.
Previous R2.7.10 browser source-ID and multi-camera regression
remains recorded independently in run #44080872633, not as proof
that a newer run passed.

**Disposition:** original *archived* native TRI one-accepted-step evidence
is internally cross-checked, and source C++ hook location and export
identity gaps are documented. A new independently replayed,
accepted-mesh-native source-face/patch/curve lineage with at least
two committed steps per original model remains OPEN; R2.8 LOD
remains BLOCKED.
