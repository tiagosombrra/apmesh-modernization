# Mesh Studio R2.7.7 — local physical desktop qualification package

**Date:** 2026-11-16. **PR:** #239, research draft.
**Status:** executable local qualification infrastructure; **no physical GPU run is claimed by CI**.
**Final validated source SHA:** `5a19cb9238683ef54db3acf85f647a8d1902699c`.
**Final CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43946262768
(**38 Chromium passed, 5 skipped**, Linux/Windows scientific regression,
production TypeScript/Vite build and CPU contracts PASS).


## Why a separate physical-desktop gate exists

R2.7.3–R2.7.6 established fast, correct original-face TRI selections for a
tightly bounded opt-in main-thread BVH on a Linux **hosted Chromium** runner.
They also detected approximately 19–21 ms Worker round trips under real
Playwright pointer events on tiny real sources. A two-RAF render-opportunity
proxy was measured, **not the GPU-presented frame**.

Those findings cannot identify performance on an actual Windows WGL GPU,
desktop display, multiple OS/browser/GPU configurations, browser process
memory, native VTK/Worker RSS or graphics VRAM. These gates remain open.

## What this package implements

1. `src/r277Probe.ts`: bounded browser capability report containing WebGL
   vendor/renderer, optional `WEBGL_debug_renderer_info`, browser version
   string, CSS viewport, device-pixel ratio, hardware concurrency and
   optional Chromium JS heap estimate. Known software renderer strings
   (SwiftShader/llvmpipe/lavapipe, etc.) are flagged. A GPU name by itself
   **does not prove physical display output**; unknown unmasked renderers
   are not silently promoted to hardware.
2. `tests/viewport-r277-capabilities.spec.ts`: CI smoke for the capability
   contract. It **always reports `physicalDesktopCertified=false`** and
   `gpuPresentedFrameMeasured=false`, with total RSS/Worker RSS/VRAM null.
   Default native VTK must remain untouched.
3. `playwright.r277.config.ts`, `scripts/run-r277-desktop.mjs` and
   `tests/viewport-r277-desktop.spec.ts`: separate headed Chromium
   protocol with mandatory, explicit local operator attestation. The
   launcher **refuses CI, headless commands and missing GPU/driver/refresh
   metadata**. The test refuses HeadlessChrome and obvious or unknown
   software/unverifiable WebGL renderers rather than treating a software
   pipeline as a physical GPU run.
4. Local tests compare `?xyzPicker=sync`, `?xyzPicker=bvh`, and native
   `vtkCellPicker` on the same real P1 and staged/unaccepted Band TRI-only
   source snapshots. They check original SHA-256, three different
   source-face IDs per model, exact XYZ cameras and viewport dimensions,
   two warm-ups per face/method, eight rotated/reversed measured rounds,
   plus face details in the inspector. Any mismatch **fails** the run.
5. Raw JSON contains a full browser environment report, an **operator-
   declared** GPU/driver/refresh rate, CDP GPU device descriptors and
   selected JS heap/task metrics where available, Long Task API samples
   where available, each raw source-ID and timing observation, p50/p95,
   and explicit qualification flags. A local Playwright browser trace ZIP
   captures browser task/interaction activity; neither the trace nor
   two requestAnimationFrames alone proves physical GPU presentation.

## Running the protocol on a physical Windows workstation

From the repo root, in **PowerShell** (not MSYS2 Python):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/mesh_studio/web/scripts/start-windows.ps1 -SetupOnly

Set-Location tools/mesh_studio/web
& .\.venv-science\Scripts\Activate.ps1
npm install --no-audit --no-fund
npx playwright install chromium

$env:APMESH_R277_PHYSICAL_DESKTOP = "I_CONFIRM_PHYSICAL_WORKSTATION"
$env:APMESH_R277_GPU_MODEL = "Replace with installed physical GPU model"
$env:APMESH_R277_GPU_DRIVER = "Replace with physical GPU driver version"
$env:APMESH_R277_DISPLAY_REFRESH_HZ = "60"

npm run test:r277:desktop
```

The GPU model, driver and refresh-rate values **must be replaced with the
machine's actual values**. The example `60` is not an asserted refresh
rate for any user workstation. A physical monitor/desktop session is
mandatory; headless CI, remote software rendering and a virtual display
do not satisfy the gate.

The local launcher starts the same project API/frontend as the existing
Playwright configuration using loopback ports 8765/5173. The scientific
C++ mesh generator is **not executed or modified**.

For a physical Linux workstation with a visible desktop session, set up
the environment separately, install the pinned Python dependencies and
frontend packages, install headed Chromium and set the same four
`APMESH_R277_*` variables before running `npm run test:r277:desktop`.
Do not use Xvfb/virtual GPU output as a physical GPU measurement.

## Exact saved results and classification

Files are saved **locally** under `tools/mesh_studio/web/test-results/`:

- `r277-desktop-p1-abc.json`
- `r277-desktop-band-abc.json`
- `r277-local-p1-chromium-trace.zip`
- `r277-local-band-chromium-trace.zip`

These local reports may include device and OS fingerprints and UI traces;
review before sharing. They are **not automatically attached to PR #239**
or uploaded to any remote account.

For the unprivileged CI smoke only,
`r277-ci-capability-preflight.json` is retained in the regular short-lived
CI artifact. The CI **skips** the two physical desktop tests by design.

All local reports explicitly retain:

- original source SHA and source face IDs;
- source classification (**controlled P1 vs staged/unaccepted Band**);
- browser-reported WebGL renderer versus operator-declared physical device;
- p50/p95 of picker callback and event→two-RAF *render opportunities*;
- signed and raw per-method observations;
- `hardwareGpuPresentTimestampVerified=false`;
- `totalBrowserRssMeasured=false`;
- `workerRssMeasured=false`;
- `gpuVramMeasured=false`;
- `largeRealAcceptedPatchMeshTested=false`.

These fields must **not** be flipped merely because a local headed test
passes. Separate OS/GPU instrumentation and an independently verified
GPU-present timestamp are required for such claims.

## Research guardrails and next evidence

- Native VTK remains the **default**. The synchronous bounded BVH cap stays
  2,048 faces / 8,192 vertices / 1 MiB input, and opt-in Worker remains
  limited to its own qualifying source faces.
- Curved QUAD visibility/patch ambiguity is still VTK-owned. The tests
  avoid claiming continuous Bézier surface intersection equivalence.
- The larger, archived **Eistute stage-4 candidate** is not a certified
  accepted adaptive epoch and has no canonical generator source IDs
  recoverable from its OBJ alone; it cannot silently enter the current
  scientific P1/Band catalog. Its published Git blob identity is verified,
  while the historic MANIFEST.sha256 mismatch remains explicitly recorded.
- GPU-present timing (e.g. authoritative OS compositor/driver tracing),
  independent browser/Worker process RSS, GPU VRAM and workload-specific
  remote sessions remain separate manually captured records before
  promoting an experiment to an accepted physical GPU benchmark.
- A second independently specified physical host/browser is needed to
  bound browser-event scheduling effects rather than extrapolating
  hosted Chromium behavior.
- R2.8 geometric LOD remains blocked pending independently validated
  source-face lineage, acceptable error bounds, seams and patch continuity.

**No automatic merge, main changes, release/tag or scientific C/C++ generator
changes are part of R2.7.7.**

## Final CI acceptance and unresolved physical evidence

The full final run #43946262768 passed on the current implementation
(excluding subsequent docs-only edits). The normal Chromium browser probe
reported:

- WebGL available: **true**;
- unmasked renderer: `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)`;
- `softwareSuspected=true`;
- `machineQualified=false`, `gpuPresentQualified=false`.

**38 browser tests passed and 5 were intentionally skipped**, including
the two tests requiring a physical headed desktop. The fail-closed
launcher tests passed: unattended CI and absent operator attestation
cannot launch the physical-desktop procedure. The P1/Band exact-source
matching and scientific regression jobs continued to pass.

The hosted software renderer cannot qualify the GPU. The local
three-page method deliberately calls `bringToFront()` before each
measured pointer event; even though browser-local timestamps exclude
that API call, its effects on scheduling/focus may influence the
subsequent measurement. The raw order and browser visibility are retained,
not silently pooled as independent physical machine samples.

**Physical workstation execution has not been performed in this CI**
and there are no generated local physical GPU, OS RSS, Worker memory,
driver-present or VRAM qualification values. The status of those
questions remains **OPEN**, not PASS.
