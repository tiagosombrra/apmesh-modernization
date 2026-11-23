# Mesh Studio V5.8 — minimal local read-only API and one-command loopback launcher

**Date:** 2026-11-23. **Status:** implemented and Windows/Linux verified; optional foreground Ctrl+C behavior added after initial certification and must be rechecked on final source code SHA. **Not a release**, signed installer, local network-access authorization, original native C++ scientific experiment, real GPU test, or R2.8 LOD.

## 1. Why V5.8 exists

The V5 master plan explicitly prioritizes a usable, reviewable product workflow over repeatedly adding source instrumentation. The older `tools/mesh_studio/web/scripts/start-windows.ps1` installs **all** original science/CI packages, including PyMuPDF 1.26.7 (AGPL/commercial dual licensing) and Python VTK, even though the actual read-only local FastAPI endpoints use pure Python scientific modules and **FastAPI** alone as an external imported framework. The historical launch also used `npm install`, which is not the exact source-locked `npm ci` path.

V5.8 introduces **`python -m tools.mesh_studio.local_launcher`** as a deliberately bounded **development/research launcher**. It does not delete existing scientific dependencies, change the original C++ generator, modify numerical scientific method, alter the React frontend or reclassify an accepted TRI source epoch.

## 2. Prerequisites and commands — project repository root

- Official CPython **3.13**, not MSYS2/UCRT64 Python for Windows scientific wheels.
- **Node 22** with **npm 10**, exactly as enforced by the launcher. Later Node/npm majors are not silently accepted.
- An internet connection for the *first* source-hash-checked Python/npm installation. The resulting development environment is **not** an offline/signed installer.
- Fixed local ports **127.0.0.1:8765** (FastAPI) and **127.0.0.1:5173** (Vite). The launcher rejects ports already in use; does not listen on LAN.

**Linux:**
```bash
python3.13 -m tools.mesh_studio.local_launcher preflight
python3.13 -m tools.mesh_studio.local_launcher setup
python3.13 -m tools.mesh_studio.local_launcher smoke
python3.13 -m tools.mesh_studio.local_launcher serve
```

**Windows PowerShell (from the repository root):**
```powershell
py -3.13 -m tools.mesh_studio.local_launcher preflight
py -3.13 -m tools.mesh_studio.local_launcher setup
py -3.13 -m tools.mesh_studio.local_launcher smoke
py -3.13 -m tools.mesh_studio.local_launcher serve
```

`preflight` verifies the exact committed Node/npm/Python versions, all original V5.4 transitive hashes/manifest closures, source-dependency import graph and OS-specific Python lock. `setup` creates only `tools/mesh_studio/web/.venv-local-readonly` and local `node_modules`, derives the minimal API transitive pin-and-hash subset, runs `pip install --require-hashes` followed by `pip check`, then `npm ci --ignore-scripts`. `smoke` starts both servers, verifies the read-only health, Vite proxy, all five original catalog entries, P1 quality and true-vector SVG, invalid model/query rejection, then terminates both and verifies no orphan ports in hosted CI. `serve` starts the same checked foreground local research service until Ctrl+C; it does not automatically open untrusted websites. Open **http://127.0.0.1:5173** in your browser.

**Important:** `serve` runs **Vite development mode**, not a production/release build. Neither a source-lock nor loopback binding alone is proof against all malicious websites, local same-user processes, browser security issues or tampering. Do not expose the service on `0.0.0.0`, reverse-proxy it publicly, ship `.venv` or `node_modules`, or claim production authentication from these checks.

## 3. Minimal dependency and licensing boundary

Source: **unchanged V5.4/V5.6 OS-specific Python 3.13 hash locks**, whose entire source manifest closure is audited before projecting packages. This is an **allowlisted lock subset** and not a new set of hand-selected versions or unconstrained `pip install`. Exactly **13 pinned Python distribution records** are installed:

| Package | Version | Purpose |
| --- | --- | --- |
| fastapi | 0.128.2 | Read-only HTTP API |
| uvicorn | 0.48.0 | Local ASGI server |
| starlette | 0.50.0 | HTTP/ASGI framework |
| pydantic / pydantic-core | 2.14.4 / 2.50.5 | Data validation |
| anyio / h11 / click / idna | 4.16.0 / 0.16.0 / 8.5.1 / 3.20 | Server/runtime transitives |
| annotated-doc / annotated-types | 0.0.7 / 0.8.0 | API/validation metadata |
| typing-extensions / typing-inspection | 4.16.0 / 0.4.5 | Typing/validation |

Both Linux and Windows source-derived virtualenvs were checked against an **exclusion list**: `pymupdf`, `vtk`, `matplotlib`, `pillow`, `numpy`, `reportlab`, `pypdf`, `httpx`, `fitz` were **not installed in this specific isolated API environment**. The static AST closure audits imported local modules reachable from `web_api.py` and fails closed if an unreviewed third-party or dynamic import is added. This is **not a claim** that every scientific test, standalone native PDF publisher, desktop GUI or eventual distribution avoids PyMuPDF, or that the entire JS package tree has no licensing obligations.

The npm browser dev dependency closure is still sourced from the exact 141-entry lock; `npm ci --ignore-scripts` eliminates untrusted npm lifecycle script execution at install time. It is not proof of a minimized final Vite production browser bundle. The separate [V5.6.1 installed-license review](V5_6_1_INSTALLED_LICENSE_EVIDENCE_RESULTS_20261123.md) and [Issue #250](https://github.com/tiagosombrra/apmesh-modernization/issues/250) remain OPEN for final distributed product licensing, notices, actual shipped dependencies and the isolated scientific PDF PyMuPDF path.

## 4. Actual source code CI and receipts

[GitHub Actions #45151258482](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45151258482) **2/2 SUCCESS** on original implementation/CI SHA `de9013a499c73e583a789b517d501259b3987040`, Linux Ubuntu 24.04 and Windows Server 2022, 9 synthetic/adversarial test methods **each** plus an actual clean local process/HTTP/browser-dev smoke each:

| Control | Ubuntu 24.04 | Windows 2022 |
| --- | --- | --- |
| Exact V5.4 npm + Python source lock admission | PASS | PASS |
| Python 3.13 + Node 22/npm 10 enforced | PASS | PASS |
| Thirteen source-hash-pinned Python API packages, no PyMuPDF/VTK | PASS | PASS |
| Frontend clean `npm ci --ignore-scripts` | PASS | PASS |
| Real FastAPI + Vite loopback listener startup / proxy | PASS | PASS |
| Source catalog P1 and staged candidate labels, accepted epochs=0 | PASS | PASS |
| Original P1 quality and genuine vector SVG, actual SHA header equality | PASS | PASS |
| Invalid model 404 and invalid geometry query 422 | PASS | PASS |
| Both subprocesses terminated; 8765/5173 not left listening | PASS | PASS |
| Original C++ scientific accepted mesh regenerated in this quick CI | **NOT EXECUTED** | **NOT EXECUTED** |

**Linux** derived runtime lock SHA256: `f69d43c8413f329ff9b7d3103f1d85a0003e3649f83d1495957a85e82fa2c5b3`; **Windows**: `64daacf1e156720e22b562725d990581f9dda4ae37c982698bcfc19d64eeb7f9`. These differ by OS-specific header binding to independently certified source lock even though the 13 package versions match. Linux/Windows fixture corpus and scientific Python computations were unchanged.

The startup script's Ctrl+C cleanup UX improvement was committed **after** the first all-green code SHA. The final branch/source SHA must independently pass the same lightweight two-platform matrix before the review is considered complete.

## 5. Open, non-equivalent gates

- **Native C++ science and R2.8 geometry LOD:** Still only original accepted step `[1]` per same-process model; no accepted face ancestry or continuous CAD error proof. The new launcher does not invoke original C++ and must not claim source-epoch qualification.
- **Native Eistute/Book GUI task:** The original native accepted scene is **manually imported** from the previously certified CI files in the existing frontend. V5.8 verified initial catalog/source/UV endpoints but did **not** automate that native browser upload and source certificate in a local clean-install workflow. Existing source-browser V5.7 4/4 CI is a separate complete native-source qualification.
- **Reviewer acceptance:** A nonauthor reviewer must reproduce local setup and core research workflow on a real Linux and Windows development machine. Hosted CI tests are not human usability testing, physical Windows GUI/GPU, network threat-model signoff or signed/distributable packaging.
- **Reproduction and release:** Not yet a signed, audited, reproducible, minimized distribution with verified legal notices. PyMuPDF is isolated out of the *minimal local API only*, not removed from scientific CI; Issue #250 must remain OPEN.

**Disposition:** source-hash-bounded, low-dependency Windows/Linux local research launch is implemented and source-verified under the matrix; **not production** and **not scientific LOD**. No merge, tag, release or change to default VTK picker.
