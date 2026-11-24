# Mesh Studio developer reference

Start with the [canonical runbook](../../../docs/mesh-studio/README.md). The older developer/research commands below are not current reviewer instructions. [Original full README](https://github.com/tiagosombrra/apmesh-modernization/blob/74f80e8136c2d836acbb6e307f8c2f552ea6c3c5/tools/mesh_studio/web/README.md).

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

## V5.2 original accepted Eistute and Book TRI vector article figures

V5.2 is **a separate real original C++ accepted-TRI source track**.
Its [method, source hashes, figure inventory and limitations](../../../docs/mesh-studio/V5_2_ORIGINAL_ACCEPTED_NATIVE_TRI_VECTOR_RESULTS_20261120.md)
are not interchangeable with P1's earlier vector export.

1. In Mesh Studio choose **Abrir estudo TRI original aceito**, or open
   `/?nativeScene=1`. Upload `r2720-native-accepted-scene.json` from the
   **same** original GitHub Actions V5.2 research ZIP.
2. In the native panel, upload **all three** other files together:
   `manifest.json`, `eistute-accepted-step1-uv.svg` and
   `book-accepted-step1-uv.svg`. The source artifact's original native
   C++ pipeline regenerated and audited these exact files from its retained
   postcommit `r2712` NDJSON; the browser will not do an unauthenticated
   raw JSON -> SVG source certification.
3. The client hashes the exact uploaded scene and each SVG, checks original
   source model/config/raw face SHAs against the scene, verifies all original
   per-patch source face identities and UV coordinates in the vector polygons,
   and rejects raster/scripts/external dependencies or false LOD claims.
   The browser then previews and permits downloading the current model's
   **genuine 2D vector patch-local UV** figure.

**Caveat:** a sufficiently malicious user could forge a mutually matching
scene JSON, manifest and SVG; the browser only guarantees **internal file
integrity**, not authentic original C++ execution. Original source acceptance
is established by the upstream same-run native generator and independent raw
NDJSON audit in CI, not by file declarations or user-controlled hashes.
No physical native seam welding, multi-accepted-epoch lineage, continuous
geometric error, anisotropic/ALL-QUAD method, vectorized 3D renderer, or
scientific R2.8 LOD is implied. Browser test fixtures based on synthetic
generated inputs never substitute the real same-run original C++ artifacts.
