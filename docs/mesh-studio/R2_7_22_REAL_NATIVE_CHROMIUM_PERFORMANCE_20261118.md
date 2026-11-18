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

**Implementation added.** Native and browser evidence
must be reviewed from the exact passing four-job
GitHub Actions run before this R2.7.22 revision
can be called source-bound **hosted performance
qualified**. Physical Windows GPU/present/RSS/VRAM
remains **UNQUALIFIED** regardless of hosted success.

Scientific geometric R2.8 remains **BLOCKED**:
neither model has two independent accepted native
adaptive epochs, cross-epoch original face/curve
descendant identities or certified continuous
geometric error bounds. No C++ generator acceptance
policy change, source mesh rewrite, weld,
`main` merge, tag or release.
