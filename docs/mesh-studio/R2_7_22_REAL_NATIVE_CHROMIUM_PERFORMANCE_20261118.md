# Mesh Studio R2.7.22 — real original accepted TRI scene performance and robustness

**Date:** 2026-11-18. **Repository:** `tiagosombrra/apmesh-modernization`.
**Branch:** `feature/mesh-studio-r27-bvh-20261116`; **PR #239 draft/unmerged**.
**Input status:** real original **serial C++ postcommit accepted TRI** Eistute
(1,168 faces, 4 source patches, 11 shared-curve samples) and Book
(4,256 faces, 28 patches, 13 shared-curve samples), each **one** genuine
accepted adaptive epoch. Neither accepted-epoch history nor geometry
algorithm is changed by the performance instrumentation.

## Scientific and engineering goals

Performance is evaluated on actual source-bound Eistute/Book scenes, **not**
on the 500k synthetic grid. The native XYZ VTK canvas and its camera must
remain intact across 10 repeated patch changes in each genuine source
model. The UV chart must follow the selected original patch, while
the source-curve sample selection must synchronize both VTK overlays
without welding any native nodes.

The research has three **separate** evidence classes:

1. **Source-bound deterministic storage and CPU typed-array capacity:**
   `native_scene_perf_budget.py` independently reconstructs the
   actual accepted TRI source JSON from the original native C++ NDJSON,
   checks the export JSON contents and SHA, and predicts *only* the
   explicit Float32/Uint32/Uint8 allocations for actual face/patch
   display and sampled native seam lines. Counts are derived from
   original accepted face IDs. These are **not** live RSS, GPU VRAM or
   browser heap measurements.
2. **Actual hosted Chromium timing and live JS heap snapshots:**
   `viewport-r2722-real-original-performance.spec.ts` downloads the
   **same native source artifact of this exact Actions run**, imports
   its original JSON through the real STUDIO opt-in workflow
   `?nativeScene=1&nativePerf=1`, and measures source read,
   source contract validation, original accepted TRI seam checks,
   VTK setup/synchronous render-call CPU durations, and the
   *controller-included* input-to-double-requestAnimationFrame
   readiness time. It exercises **10 patch changes and 6 sample
   changes per genuine source model**, preserves the XYZ canvas
   in the same model, and records separate Chromium CDP
   `Performance.getMetrics` `JSHeapUsedSize` and
   `JSHeapTotalSize` before import, after import and after
   interaction. **These CDP metrics are not process RSS or VRAM.**
3. **Independent report/source audit:**
   `native_browser_perf_audit.py` checks the original exact
   JSON SHA/byte count against the native source-built budget,
   both actual original model names/accepted native epochs/face
   inventory/patch counts/seam counts, expected explicit
   VTK typed buffers and ten/six latency sample distributions
   against recomputed medians and p95, rejects nonfinite,
   missing or forged measurements, rejects any physical GPU or
   LOD certification claim, and ties the report to the **same
   GitHub commit SHA**. The release gate fails if the
   original same-run native scene artifact is absent.

### Causal and timing limitations

The measured `setInputFiles` → two RAF wall interval and UI
interaction samples include **Playwright and browser scheduling**
overhead. Double RAF is **not** a demonstrated time of final
GPU present. The VTK synchronous `render()` JavaScript call
can submit GL work asynchronously; it is **not** a hardware
GPU pipeline duration. A single hosted run yields a descriptive
sample median/p95 only, **not** a confidence interval or
statistically controlled hardware benchmark. Different
systems, drivers, background load, window composition
and GPU architecture will produce different timings.

CDP's JS heap samples are snapshots influenced by garbage
collection, so a positive heap delta is **not proof of a
memory leak**. Conversely, a stable heap does **not** prove
absence of retained VTK WebGL resources. Estimated
`Float32Array`/index buffers are not total browser memory
and should never be reported as RAM/RSS/VRAM.

The actual accepted source JSON also carries the original
R2.7.19 sample IDs, R2.7.20 exact per-face native IDs,
R2.7.21 directly observed patch-local native TRI seam
edge identity and original source SHA. No OBJ face ordinals,
synthetic geometry, rejected native trials or arbitrary
surface welding can be substituted.

## Concrete fail-closed implementation

The `browser-spike` GitHub Actions job explicitly
`needs: native-lineage-optin`. It only starts after the
original compiled C++ GeneratorAdaptive replay,
source NDJSON SHA audit, independent accepted geometry
validation, and original Eistute/Book 38-file scientific
OFF/ON parity all succeed. It downloads the **original
`r2720-native-accepted-scene.json` artifact from the same
workflow SHA** plus the independent real-source CPU
transfer-capacity receipt. It explicitly refuses missing
files rather than silently skipping real performance.

The real native Chromium test is one bounded serial test;
local runs without the native artifact explicitly **skip
this test only** while keeping all previous browser contracts
available. **CI must supply the original artifact**.
The independent Python report/source auditor then runs
within that browser job and a 14-day Actions artifact
retains both the original hosted measurements and the
audited source-bound receipt. The native job independently
retains the transfer-capacity JSON. Linux and Windows
Python scientific suites add synthetic **negative
contracts only**. No browser-hosted runner qualifies
a real Windows GPU.

Opt-in import/renderer dataset metrics are visible only
when the user adds `&nativePerf=1` to the original native
scene URL. The native XYZ display keeps one stable VTK
canvas/camera on source patch changes. Changing models
is allowed to create a new context and is not considered
a failure of patch-context persistence. Existing P1
viewports, source-ID picking, VTK default and bounded
experimental BVH modes are untouched.

## Reproduction

On the same GitHub workflow, after native accepted
C++ source output and `r2720-native-accepted-scene.json`:

```bash
python -m tools.mesh_studio.native_scene_perf_budget \
  --original-directory build/r2712-native-evidence \
  --scene build/r2720-native-accepted-scene.json \
  --output build/mesh-studio/r2722-visual-transfer-budget.json
cd tools/mesh_studio/web
npm run build
npm run test:e2e
cd ../../..
python -m tools.mesh_studio.native_browser_perf_audit \
  --report build/mesh-studio/r2722-original-chromium-performance.json \
  --scene build/r2720-native-accepted-scene.json \
  --budget build/mesh-studio/r2722-visual-transfer-budget.json \
  --output build/mesh-studio/r2722-chromium-audit.json
```

Original source and browser reports must be archived with
their **exact source-commit and artifact ZIP SHA**. Any
client-side import is structural validation: only the
original source-bound native C++ artifact independently
establishes accepted scientific provenance.

## Physical workstation qualification — mandatory outstanding gate

Actual **interactive Windows desktop GPU** testing must
record OS and driver versions, adapter vendor/device and
hardware capabilities; at least five real launches,
camera pan/orbit/zoom, sample and patch selection and
close/reopen cycles; repeated model imports and
controlled same-workload latency distributions;
verified WebGL context-loss recovery, graphics
present timestamps, process private bytes/RSS,
browser and worker process breakdown where available,
GPU per-process VRAM/dedicated/shared memory and
resource release after closes. Include source SHA,
environment specification, raw traces and independent
screenshot verification. A hosted Ubuntu Chromium
runner, virtual X server or synthetic GPU smoke
does **not** substitute for physical WGL/DXGI
measurements.

## Qualification status
cation — 2026-11-18

**QUALIFIED for source-verified hosted Chromium timings and exact source
buffer estimates; NOT qualified for physical Windows GPU performance.**

[GitHub Actions #44280086289](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44280086289)
completed **SUCCESS — all 4 jobs** at exact tested code/source SHA
`264a15d57d1168b9bbb7512fa8d918648fd4c6ab`. The final revision
corrected the synthetic regression fixture's missing
`native_source_patches` key. The earlier incomplete #44279824404
run **FAILED Linux/Windows regression and is NOT a certified release**,
even though its separate original-native and hosted-browser jobs passed.
All numbers reported below refer **only to the fully green final run**.

| Independent gate | Final source-pinned result |
| --- | --- |
| Actual compiled original serial C++ Eistute | 1 real accepted adaptive step, 1,168 original accepted TRI, 4 source patches, 40 verified shared-source patch-local native TRI edges; 3 rejected/restored candidate steps |
| Actual compiled original serial C++ Book | 1 real accepted step, 4,256 accepted TRI, 28 source patches, 336 true shared-source patch-local TRI edges; 2 rejected/restored |
| Native source SHA / R2.7.12–R2.7.22 original scene capacity | **PASS**, original postcommit source independent audit and true source-bound report |
| Original scientific OFF/ON C++ file-byte parity | Eistute **21/21**, Book **17/17**, total **38/38 identical** |
| Linux Python scientific, contract and negative-gate tests | **352 run, 4 optional skipped, PASS** |
| Windows Python scientific, contract and negative-gate tests | **352 run, 10 environment skipped, PASS** |
| Hosted Ubuntu Chromium, including *real original* Eistute+Book performance test | **55 passed**, real same-run native source import, patch/source-sample interactions and CDP JS heap report PASS |
| Independent hosted report vs native source SHA, measured sample distributions and original buffer sizes | **PASS** |

**Original exact scene JSON:** 1,716,994 bytes;
SHA256 `e671d0bcee10c4cc8f01640372495d053fe28682d9e3ebfae5cecbd670719a45`.
The original accepted C++ per-face native NDJSON hashes remain
Eistute `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`
and Book `e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a`.

### Final real-source Chromium observations

These are **one hosted Ubuntu browser run**, using the real native
Eistute/Book JSON imported into the independent R2.7.21 source viewer.
The patch/source-sample timing below is a **Playwright input-to-double
requestAnimationFrame readiness proxy**, including controller
round trips and browser scheduler interference. It is
**NOT a GPU-present timestamp** and cannot be compared as
a system-independent graphics frame rate.

| Original source | 10 patch changes, median | 10 patch changes, p95 | 6 source sample changes, median | 6 source sample changes, p95 |
| --- | ---: | ---: | ---: | ---: |
| Eistute, 1,168 TRI | **232.1 ms** | **268.7 ms** | **82.4 ms** | **94.3 ms** |
| Book, 4,256 TRI | **232.1 ms** | **232.6 ms** | **82.2 ms** | **94.0 ms** |

The first original 1.717 MB JSON read completed in **4.9 ms**;
full source-identity/structure validation **20.6 ms**;
accepted-native-seam-edge verification **25.1 ms**;
combined pre-React processing **50.6 ms**. The measured
import-to-two-RAF UI readiness interval was **1,285.9 ms**
including automation and scene/GL setup. This interval
does not isolate a GPU draw/present duration.

The real browser CDP `JSHeapUsedSize` snapshots
were **10,521,696 bytes** before original import,
**37,454,440 bytes** after import, and
**32,671,768 bytes** after the bounded model/patch/sample
interaction sequence. These are **one browser's live
JS heap snapshots**, not total browser process RSS,
system RAM, graphics VRAM or an independently proven
resource-leak verdict. GC may have affected the delta.

### Bounded actual source display-buffer capacity

Only explicit CPU Float32/Uint32/Uint8 buffers from the
original faces and their patch-local native shared-source
edge overlays are budgeted:

| Original real scene | XYZ typed buffers | One patch's UV buffers | Original edge-line buffers | Estimated combined modeled display array envelope |
| --- | ---: | ---: | ---: | ---: |
| Eistute | 65,408 B | 16,352 B | 1,440 B | **83,200 B** |
| Book | 238,336 B | 8,512 B | 12,096 B | **258,944 B** |

This modeled envelope excludes the source JSON parsed as
JavaScript objects, WebGL driver/upload copies,
vtk.js internal objects and graphics memory; it is not
a measured total memory ceiling.

### Original artifacts independently preserved and reverified

The following **same exact final Actions run** ZIP artifacts
were downloaded from GitHub Actions, uploaded to the
authenticated personal doctoral Drive
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`,
then downloaded **back from Drive** and their original
ZIP SHA256 digests independently compared **byte-for-byte**:

| Authentic source artifact | Original ZIP bytes | Original GitHub + Drive-readback SHA256 |
| --- | ---: | --- |
| [Raw original C++ accepted NDJSON + original stderr #14417146011](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44280086289/artifacts/14417146011) | **279,373** | `ed6b9ead93d749bc06645e5730e2c8c38045c89d0f0465ff72936c5f0f399284` |
| [Accepted native TRI Eistute/Book source scenes #14415878797](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44280086289/artifacts/14415878797) | **214,946** | `fd163e0f626d61e4a310161171bec5ea06e50155c211e06c7d2f965fd5ec8f97` |
| [Real original native source typed-buffer receipt #14416168298](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44280086289/artifacts/14416168298) | **843** | `4c6521e637487ef2703fc47c8cd20696121b74bf4b0b2e9711cc33462714b1f5` |
| [Original hosted real-source Chromium report + independent audit #14417955381](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44280086289/artifacts/14417955381) | **2,562** | `5680c2e5073c62ac0342cfc058da90e23aefb2c995f766c6c85b5969632e9664` |

The raw Chromium performance JSON SHA256 is
`ca9dd1eb7e84b562210baca91cdce5a35c62b4bd1561477b28eecf35d338604b`
(4,795 original bytes); the independent audit JSON SHA256
is `87a617223657c8c8c1b7c1e06a5315891f0057a0f1215b95fff53fd339b8b651`
(2,156 bytes). The native source original hashes are pinned
in the reports and original C++ runtime artifacts.

### Scientific admission remains blocked

**R2.7.22 delivers measured real-source browser *hosted*
interaction/heap diagnostics and source-derived CPU
display array capacity; it does NOT certify hardware performance
on a physical Windows GPU.** Still required: physical
GPU-present timestamps, controlled Windows device and driver,
process-level RSS/private bytes, per-process GPU VRAM,
graphics context lifecycle/stress under repeated close/reopen,
replicates on additional real systems and independent
hardware-bound qualification. None has been fabricated.

**R2.8 scientific geometric LOD remains BLOCKED:** neither model
has two genuinely accepted adaptive epochs, original cross-epoch
face/curve ancestry and continuous geometric error bounds.
No scientific C++ generator acceptance change, source mesh
rewriting, global node weld, `main` merge, tag or release;
PR #239 remains draft/unmerged. Source VTK picking
remains default with bounded optional experimental BVHs.
