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

**Open qualification gates:** npm dependencies could not be downloaded in
this tool environment. Consequently TypeScript source parsing is executed,
but `npm run build`, actual WebGL scene, vtk.js picking in Chromium,
Playwright E2E, cross-platform GPU and 50k/500k datasets remain **NOT RUN**
until the dedicated CI completes. The frontend's screenshot output must not
be represented as a vector figure. The existing Python publisher owns
SVG/PDF/LaTeX production.

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
