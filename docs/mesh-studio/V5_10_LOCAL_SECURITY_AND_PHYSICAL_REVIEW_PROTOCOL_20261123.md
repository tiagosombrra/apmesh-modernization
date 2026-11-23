# Mesh Studio V5.10 — local-only security and independent physical reviewer protocol

**Date:** 2026-11-23. **Status:** security implementation under source-code review; the physical reviewer approvals in this document **are blank by design** until real humans on independent physical machines perform them. This is a **research-mode** acceptance protocol, not a penetration test, a signed installer, legal distribution approval or an original C++ R2.8 multi-epoch LOD qualification.

## 1. Exact scope and demonstrated threat boundary

V5.8 exposed a read-only source-locked FastAPI API and a Vite development server on `127.0.0.1:8765` and `127.0.0.1:5173`. V5.9 reaudited the *genuine retained original C++* Eistute/Book step-1 NDJSON and original native SVG against their fixed immutable SHA256 and completed real hosted Chromium review on both OS.

**Finding:** The standalone FastAPI `app` had CORS allow-listing but did not independently validate HTTP `Host` / `Origin` or HTTP fetch-site. A CORS policy by itself is not authentication and is not a substitute for Host validation when DNS rebinding or malicious websites may access a developer's machine. Vite likewise runs as a **development server**, and its documented default hostname set includes localhost derivatives/IPs; it is not a production hardened file server. <https://www.starlette.io/middleware/> and <https://vite.dev/config/server-options> describe these boundaries.

**V5.10 implemented a narrowly scoped fail-closed local-launcher gate**:

- `tools/mesh_studio/local_loopback_guard.py` wraps the ASGI app **only for the launcher** (`tools.mesh_studio.web_api:local_app`). It accepts **exactly** Host `127.0.0.1:8765`, no duplicate Host/Origin/fetch-site headers, no foreign Origin, no `Sec-Fetch-Site: cross-site`, and only GET/HEAD/OPTIONS. It rejects upstream WebSocket with close 1008. It emits no-store, nosniff, DENY framing, same-origin resource policy and no-referrer HTTP headers for protected responses. The upstream FastAPI application and original scientific unit-test paths are intentionally untouched.
- The Vite development configuration retains a fixed **127.0.0.1:5173** bind, strict port, explicit allowedHosts, strict CORS origin and early HTTP middleware that rejects unexpected Host, Origin, fetch-site and write verbs. The Vite API proxy changes the upstream HTTP Host to `127.0.0.1:8765` rather than forwarding the frontend Host `127.0.0.1:5173`.
- The V5.8/V5.9 combined local launcher checks **eight actual live HTTP rejections** (four API, four Vite): invalid Host, external Origin, cross-site fetch metadata and POST; and explicitly verifies the legitimate browser CORS origin is still accepted. A separate stdlib ASGI test suite covers duplicate headers, unsupported verbs and WebSocket rejection.
- The V5.9 **original C++ source** reviewer is rerun against that same protected pair: genuine source P1 linked XYZ/UV and SVG, staged Band not accepted, original Eistute 1,168 native TRI/4 patches and Book 4,256 TRI/28 patches, exact original element/node identities, SHA-verified UV vector downloads and forged-source negatives.

**Not proven or protected by these gates:** a malicious process already running under the user's OS account; unsafe browser extensions; the whole Vite dev toolchain and HMR websocket upgrade threat model; outdated device firmware; package supply-chain compromises despite lock verification; LAN/public deployment or reverse proxies; user-uploaded malicious files outside strict current source contracts; physical GPU measurements; code signing/automatic updates; original C++ numerical algorithm quality; or production authentication. A direct, nonlauncher invocation of `tools.mesh_studio.web_api:app` **does not use the guard**. Always use the documented launcher; do **not** expose the API or Vite server publicly.

## 2. Reproduce the real source run locally

Use a **trusted workstation**, a clean checkout of the [Draft V5.10 branch](https://github.com/tiagosombrra/apmesh-modernization/tree/feature/mesh-studio-v510-loopback-security-review-20261123), official CPython **3.13**, Node **22** and npm **10**; Chromium browser binaries from Playwright. Keep the machine and browser on a trusted network with a normal local user account.

Copy the archived original V5.9 ten-file ZIP from your **private personal doctoral Drive** (`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados/apmesh-studio-v59-original-native-reviewer-corpus-7d41ab8.zip`). Unzip its `build/v59-native-reviewer/` contents at the repository root. Do **not** trust other pasted JSON as original accepted C++ evidence; the preflight checks SHA256 for every original source file and independently reopens the postcommit source. **Do not upload private Drive links into public GitHub issues.**

Linux:
```bash
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_launcher setup
cd tools/mesh_studio/web && npm exec playwright install chromium && cd ../../..
python3.13 -m tools.mesh_studio.v59_reviewer smoke
python3.13 -m tools.mesh_studio.local_launcher serve
```

Windows PowerShell (repository root):
```powershell
py -3.13 -m tools.mesh_studio.v59_reviewer preflight
py -3.13 -m tools.mesh_studio.local_launcher setup
Push-Location tools/mesh_studio/web
npm exec playwright install chromium
Pop-Location
py -3.13 -m tools.mesh_studio.v59_reviewer smoke
py -3.13 -m tools.mesh_studio.local_launcher serve
```

Open exactly **http://127.0.0.1:5173**. Do not use `http://localhost:5173`, which is intentionally not the authorized Host in this strict protocol.

## 3. Manual acceptance — independent reviewer on physical Windows AND Linux

Record a distinct result for **each** physical host. No hosted GitHub Actions runner can be marked as an independent physical reviewer. A reviewer should attest to the original source identities, linked views and UI operability without treating hosted SwiftShader render results as physical GPU benchmarks.

| Control | Objective evidence and acceptance criterion | Windows human | Linux human |
| --- | --- | --- | --- |
| Reviewer identity, consent and machine | Reviewer initials, date, OS/build, CPU, GPU model, RAM and browser version recorded without leaking personal identifiers | NOT RUN | NOT RUN |
| Source integrity | Original reviewer `preflight` PASS, ten SHA-pinned files accepted and original postcommit raw NDJSON independently reopened | NOT RUN | NOT RUN |
| Minimal local environment | Python 3.13 / Node 22 / npm 10, 13 SHA-locked API packages; PyMuPDF/VTK absent from this API venv | NOT RUN | NOT RUN |
| Local control | API and Vite bind only `127.0.0.1`; ports 8765/5173; no unexpected external requests in browser Network panel | NOT RUN | NOT RUN |
| P1 workflow | Open P1, inspect original source quality/triangles and make a UV selection; identical selected original face ID in XYZ and UV | NOT RUN | NOT RUN |
| Staged guard | Select Band, see `STAGED_UNACCEPTED` and zero accepted adaptive epochs; no misleading LOD quality assertion | NOT RUN | NOT RUN |
| Native Eistute | Import exact source scene and vector manifest; 1,168 TRI/4 patches; patch slot 3, source element ID 5350 and node ID 200 | NOT RUN | NOT RUN |
| Native Book | 4,256 TRI/28 patches; patch slot 27, source element ID 4250 and node ID 909 | NOT RUN | NOT RUN |
| Authentic export | Eistute and Book SVG file SHA exactly matches their fixed original V5.2 manifest; no raster/re-generated figure substitution | NOT RUN | NOT RUN |
| Reject hostile traffic | `smoke` reports eight actual API/Vite blocked requests and legitimate local CORS origin PASS | NOT RUN | NOT RUN |
| Cleanup and recovery | Ctrl+C stops both subprocesses and ports 8765/5173 become free; restarting does not alter source SHA | NOT RUN | NOT RUN |
| UI usability | Reviewer can identify where to import a scene, select patch/curve/sample, inspect source ID/UV and download vector without consulting source code | NOT RUN | NOT RUN |

**Optional explicit network-negative checks while `serve` is active** — these must **not** fetch any external URL; all target the user's own localhost.

Linux:
```bash
curl -i -H 'Host: attacker.invalid:8765' http://127.0.0.1:8765/api/v1/health
curl -i -H 'Origin: https://attacker.invalid' http://127.0.0.1:8765/api/v1/health
curl -i -H 'Host: attacker.invalid:5173' http://127.0.0.1:5173/
```

Windows PowerShell:
```powershell
curl.exe -i -H "Host: attacker.invalid:8765" http://127.0.0.1:8765/api/v1/health
curl.exe -i -H "Origin: https://attacker.invalid" http://127.0.0.1:8765/api/v1/health
curl.exe -i -H "Host: attacker.invalid:5173" http://127.0.0.1:5173/
```

Expected: the API rejects incorrect Host with **400** and foreign Origin with **403**; Vite rejects an untrusted Host (normally **403** from its own allowed-host gate). None may return HTTP 200 or source data. Do not run these commands against a publicly reachable service.

## 4. Reviewer report template — explicitly unsigned

```text
Mesh Studio V5.10 — INDEPENDENT PHYSICAL SOFTWARE REVIEW (NOT YET SIGNED)
Reviewer initials:
Workstation: [Windows or Linux], OS/build:
Actual CPU / GPU / RAM:
Browser / exact version:
Project git commit SHA:
Original native source run ID: 45147268663
Original scene SHA256: eb72cb058fef2a7632e09f5a3572f39e32f4d9038780cce05337d1afd86f2816
Fresh source verification (PASS/FAIL):
Minimal local installation + API/Vite smoke (PASS/FAIL):
P1 linked original source faces / Band staging (PASS/FAIL):
Original Eistute source patch 3/Book patch 27 (PASS/FAIL):
Downloaded SVG digests (PASS/FAIL):
Local Host/Origin/security rejection controls (PASS/FAIL):
Ctrl+C and clean process/port termination (PASS/FAIL):
Physical device usability issues and reproduction steps:
Supporting screenshot/log paths (no passwords/personal content):
Reviewer decision (ACCEPT / REJECT / CONDITIONAL / NOT REVIEWED):
Reviewer signoff and date:
EXCLUSIONS: no proof of R2.8 multiepoch LOD, physical source welding,
continuous CAD error, journal layout approval, legal licensing or production security.
```

**Acceptance policy:** a GitHub-hosted CI `PASS` is not a filled reviewer signature. At least one independent real Windows host and one independent real Linux host must be marked with reproducible objective evidence before closing [Issue #255](https://github.com/tiagosombrra/apmesh-modernization/issues/255). Even after review, the app remains **research-only** until a separately approved threat model, distribution policy, legal license notices, hardware verification and release workflow are completed. **No merge to `main`, tag, installer or publication signoff is implied.**
