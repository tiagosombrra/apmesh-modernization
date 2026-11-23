# Mesh Studio Web R1 (research vertical slice)

## V5.10 — inicialização local protegida e revisão independente

O `local_launcher` agora oferece uma variante da API protegida por Host e Origin exatos (`127.0.0.1:8765`), com Vite restrito a `127.0.0.1:5173` e oito testes HTTP hostis contra ambos os serviços. A [V5.10 foi validada no Linux e no Windows (../../../docs/mesh-studio/V5_10_LOCAL_SECURITY_AND_PHYSICAL_REVIEW_PROTOCOL_20261123.md): 24 testes Python + 2 testes de navegador por sistema e os oito bloqueios HTTP observados. **Execute pelo launcher**, não exponha `web_api:app` diretamente como serviço protegido e não use `localhost:5173` como endereço alternativo. O sistema continua em modo Vite de desenvolvimento, sem autenticação de produção.

Para a **avaliação independente em equipamento físico**, siga o protocolo V5.10: extraia o corpus original C++ da pasta privada de experimentos do Doutorado, execute `python3.13 -m tools.mesh_studio.v59_reviewer preflight`, `local_launcher setup`, instale o Chromium do Playwright e execute `v59_reviewer smoke`. No Windows PowerShell use `py -3.13`. A revisão por pessoas em máquinas físicas permanece **não realizada**, mesmo após o CI 2/2 aprovado. R2.8 científica segue bloqueada.

## V5.9 — reproducible original C++ Book/Eistute reviewer journey

The [V5.9 result and exact original-source identities](../../../docs/mesh-studio/V5_9_ORIGINAL_NATIVE_LOCAL_REVIEWER_RESULTS_20261123.md) verify an end-to-end **original-native C++ step-1** source task with the **V5.8 minimal local FastAPI/Vite launcher**, not a new accepted scientific epoch.

Extract the pinned ten-file reviewer corpus archive under the repository root, resulting in `build/v59-native-reviewer/` (including `r2720-native-accepted-scene.json`, two original C++ postcommit NDJSONs, original identity reports/logs, V5.2 manifest and SVGs). Run Python 3.13, Node 22 and npm 10:

```bash
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_launcher setup
cd tools/mesh_studio/web && npm exec playwright install chromium && cd ../../..
python3.13 -m tools.mesh_studio.v59_reviewer smoke
```

On Windows, replace `python3.13` by `py -3.13` and use `Push-Location / Pop-Location` instead of `cd ... && cd ../../..` in PowerShell. This script independently reopens **original raw accepted C++ NDJSON and SVG per-face identities**, opens the actual two local servers and runs browser reviews of P1 linked XYZ/UV source IDs, staged candidate labels, Eistute/Book real original triangles/patches/nodes and authentic vector downloads; then shuts both services down.

**[GitHub Actions V5.9](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45158811660): Linux + Windows 2/2 PASS**, 16 Python unit/adversarial checks plus 2 hosted Chromium tests on each platform. Original P1 source SVG bytes now have canonical Linux/Windows LF and equal SHA256 `c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe`. Original native C++ Eistute/Book source SVGs remain unchanged. The historical original GitHub Actions artifact auto-expires after 14 days; retain the independently SHA-pinned reviewer source bundle locally or rerun the original native workflow and update its source receipt without silently reusing a different native epoch.

The source certificates **do not** mean any random uploaded JSON is trusted by the browser, physical seams are welded, original C++ generated step 2, or real GPU/physical Windows performance is qualified. This is not a signed/offline installer or a production release.


## V5.8 — caminho recomendado para execução local em Linux/Windows

O caminho recomendado agora é **um único launcher de pesquisa com API mínima**, em vez de instalar todo o ambiente científico com `pip install -r requirements-web-ci.txt`. A versão V5.8 usa Python 3.13, Node 22, npm 10 e os locks imutáveis com hashes já auditados. O ambiente local **não instala PyMuPDF nem VTK**, que continuam em fluxos científicos separados.

Execute na raiz do repositório:

```bash
# Linux: substitute python3.13 for py -3.13 on Windows PowerShell.
python3.13 -m tools.mesh_studio.local_launcher preflight
python3.13 -m tools.mesh_studio.local_launcher setup
python3.13 -m tools.mesh_studio.local_launcher serve
```

Abra `http://127.0.0.1:5173`; pressione Ctrl+C para encerrar os dois serviços. Para um teste automático que inicia, verifica e encerra ambos: `python3.13 -m tools.mesh_studio.local_launcher smoke`. Os serviços usam **somente loopback**, e o frontend permanece em **Vite dev**, não em modo de distribuição. [Protocolo, limites, logs Linux/Windows e revisão de licenças](../../../docs/mesh-studio/V5_8_MINIMAL_LOCAL_LAUNCH_AND_SOURCE_LOCK_RESULTS_20261123.md).

**Atenção:** as instruções antigas logo abaixo e o script histórico `start-windows.ps1` permanecem disponíveis para cenários de CI/diagnóstico, mas instalam todo o ambiente científico, incluindo bibliotecas com licenciamento adicional. Não são o caminho recomendado para executar apenas a interface local. A V5.8 não certifica GPU física, instalador, segurança de rede para terceiros ou dois epochs TRI aceitos no gerador original.


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
