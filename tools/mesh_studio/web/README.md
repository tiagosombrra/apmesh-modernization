# Mesh Studio Web R1 (research vertical slice)

This code is an **unqualified browser frontend candidate**, not a released application.
It preserves Python as the source of mesh topology/metric computations and never
converts accepted/rejected source candidates into accepted adaptive epochs.

Run from the repository root in two shells:

```bash
python -m pip install -r tools/mesh_studio/requirements-web-ci.txt
python -m uvicorn tools.mesh_studio.web_api:app --host 127.0.0.1 --port 8765
```

Then in another shell:

```bash
cd tools/mesh_studio/web
npm install --no-audit --no-fund
npm run dev
```

Open http://127.0.0.1:5173. The browser communicates only with the local
read-only API through a Vite proxy; no third-party source URL or user-supplied
filesystem path is allowed. No analytical metrics are recalculated in JS.

**Traceability:** the two viewports share `source_face_ids`; each picking
operation maps the vtk.js visible-cell index back to the original Python face
ID. Per-corner UV coordinates are intentionally retained; coincident XYZ
coordinates across patches are never welded.

**Current verification as of 2026-11-20:** the earlier setup-only
statement below this version history is obsolete: actual TypeScript/Vite build,
vtk.js source-ID selection and Playwright E2E ran on hosted Chromium.
The exact prior certified code revision `772ae52198b74384532f1d0daecd073cc4f84a81`
passed [all four CI jobs](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44726631849):
520 Python tests on both Linux and Windows, real original C++ scientific
provenance/neutrality and 55 hosted Chromium tests (5 intentional skips).
The current [V5.1 source cache and vector research workflow](../../../docs/mesh-studio/V5_1_SOURCE_CACHE_AND_VECTOR_STUDY_WORKSPACE_20261120.md)
adds measured cold/warm Python API speed, real browser cancellations,
the Python-owned source UV SVG download and discoverable original accepted
TRI scene import. **Requalify V5.1 on its own exact HEAD before citing its
new browser controls as passed.**

Hosted Chromium uses a software renderer; no physical GPU, real Windows
WGL/VRAM/RSS, a real 500k source-approved mesh, geometric LOD, or packaged
offline release is certified. The frontend screenshot remains raster, while
the audited `/publication.svg` source UV output is genuinely 2D vector.

**Stop/go:** do not retire Qt diagnostic files or choose a packaging wrapper
until actual browser selection, filter changes and camera operations are
observed and measured.

## R1.1 local installation (Windows UCRT64, PowerShell)

MSYS2/UCRT64 `python.exe` may not have `pip` and must not be used for the
Python VTK wheels. This version includes an **opt-in** Windows setup/launcher
that uses `py.exe -3.13` and its own `web/.venv-science` (not the MSYS2 Python).
From the extracted project root in an MSYS2 terminal:

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/mesh_studio/web/scripts/start-windows.ps1
```

From PowerShell, execute the same command without `powershell.exe` by invoking
`& .\tools\mesh_studio\web\scripts\start-windows.ps1`. The script installs
packages only within its venv and project-local `node_modules`, starts both
servers bound to `127.0.0.1`, and does not modify the C++ generator. Use
`-SetupOnly` to install without starting servers, and `-SkipInstall` to reuse an
existing venv. Do not use this flag until dependencies have been installed.

R1.1 preserves the OpenGL context when toggling TRI, QUAD or edges, saves two
camera poses keyed by the exact source OBJ SHA-256 in browser localStorage and
restores only matching, finite, non-degenerate camera recipes. Both XYZ and UV
use the original `source_face_id` for picking and selection.

The new `.bin` geometry endpoint is a **Float32 rendering transport**, not a
numerical data source. Python still verifies the original OBJ and supplies
scientific metrics in full source precision. Binary transfers are bounded to
32 MiB and retain per-corner UV geometry without patch welding. The original
JSON endpoint remains for compatibility and independent verification.

## R2 preflight (not an interactive 500k qualification)

Run `python -m tools.mesh_studio.scene_benchmark --cells 1000 50000` from the
repository root. It constructs **synthetic** regular QUAD grids to measure
serialization size and preparation time. These results cannot establish
source-generator quality, browser FPS, GPU footprint or acceptable interaction
with 500,000 real elements. The latter remain a separate qualification gate.

## V5.1 local research publication workflow

Choose an original source P1 or a staged study candidate in the left catalog,
inspect the XYZ and UV viewports and a source face, then select
**Exportar figura UV vetorial (SVG)**. The read-only source-locked API delivers
a 155 × 120 mm pure-vector UV figure; the SVG embeds original OBJ SHA-256,
source classification, and the explicit zero accepted adaptive-epoch status.
A staged candidate stays labeled **NOT AN ACCEPTED ADAPTIVE EPOCH** in the SVG.
The browser does not recompute scientific quantities or download third-party
font assets; system/local font fallbacks replace the former remote font import.

The separate **Abrir estudo TRI original aceito** section provides Eistute/Book
step-1 original native TRI visualization using a manually supplied original
CI-exported JSON. The browser checks its declared original-source and face
contracts but cannot by itself attest the underlying C++ NDJSON SHA without
the original raw files. Do not compare it as an accepted LOD against P1.

To reproduce the local API timing diagnostic from the repository root:

```bash
python -m tools.mesh_studio.benchmark_web_cache --pairs 16 --output build/mesh-studio/v5-source-web-cache-benchmark.json
```

This diagnostic uses original P1 and unaccepted Band source OBJ and measures
in-process FastAPI TestClient request duration with cache forcibly cleared
versus warm; it is **not** a TCP, browser paint or GPU performance benchmark.
Browser and numerical integration tests remain required before release.
