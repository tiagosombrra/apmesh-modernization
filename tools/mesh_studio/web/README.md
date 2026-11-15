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
