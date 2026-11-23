# V5.11 — one-port compiled local research reviewer, original C++ evidence retained

**Date:** 2026-11-23. **Classification:** local, source-locked development/review software only. **Not** a signed installer, offline dependency bundle, production deployment, authorization boundary for malicious local users, authenticated multitenant web app, hardware benchmark, original C++ compilation or scientific R2.8 acceptance.

## Why this is the next finite product gate

[V5.9](V5_9_ORIGINAL_NATIVE_LOCAL_REVIEWER_RESULTS_20261123.md) qualified an actual read-only source-attested Eistute/Book browser workflow on Windows/Linux. [V5.10](V5_10_LOCAL_SECURITY_AND_PHYSICAL_REVIEW_PROTOCOL_20261123.md) hardened Host, Origin, fetch-site, method, response headers and local server access. Both still executed **Vite development mode** on `127.0.0.1:5173` and FastAPI separately on `127.0.0.1:8765`. Vite dev includes development-time transforms, a HMR/WebSocket surface and a second process a researcher should not need just to inspect verified source data.

**V5.11 compiles the exact source-locked frontend with TypeScript and Vite, inventories every emitted file by SHA256 and serves the generated static bytes from the existing 13-package minimal FastAPI Python environment, under the same origin as the scientific API: `http://127.0.0.1:8765`.** It launches **no Vite dev server, no Vite HMR, no server on port 5173**. The previously existing frontend source/UX, per-corner UV and original C++ scientific evidence are unchanged.

A latent static-build TypeScript issue was found: the pinned Vite request type did not expose `headers` and `method` in the local dev guard because `@types/node` is not among the audited installed npm packages. V5.11 now narrows the HTTP request shape *only for these three used properties* rather than introducing an unaudited npm dependency.

## Commands for an independent source reviewer

Obtain the exact preserved ten-file **original C++ accepted Eistute/Book corpus ZIP** from the existing personal Drive doctoral folder `Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`. Its exact ZIP name is `apmesh-studio-v59-original-native-reviewer-corpus-7d41ab8.zip`; locally archived size **784,614 bytes**, SHA256 **`a8564310bf28cb8ec26aaa5f71b67399a374433f06181d7f598f7070fd9d8523`**. Extract it at the repository root with the subfolder `build/v59-native-reviewer/`. The sources must pass the existing `v59_reviewer preflight` SHA256 and *independently reopen raw original native C++ postcommit NDJSON*, not merely a browser-uploaded scene manifest.

Required for the **initial build**: official CPython **3.13**, Node **22**, npm **10** and network for the exact source-hash-installed dependencies. Run from repository root:

**Linux**
```bash
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher build
python3.13 -m tools.mesh_studio.local_reviewer_launcher preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher original-smoke
python3.13 -m tools.mesh_studio.local_reviewer_launcher serve
```

**Windows PowerShell**
```powershell
py -3.13 -m tools.mesh_studio.v59_reviewer preflight
py -3.13 -m tools.mesh_studio.local_reviewer_launcher build
py -3.13 -m tools.mesh_studio.local_reviewer_launcher preflight
py -3.13 -m tools.mesh_studio.local_reviewer_launcher original-smoke
py -3.13 -m tools.mesh_studio.local_reviewer_launcher serve
```

Playwright Chromium browser binaries (only for `original-smoke`, not normal manual inspection) may be installed from the web directory using `npm exec playwright install chromium`. After `serve`, open **http://127.0.0.1:8765/** in a physical local browser; Ctrl+C stops the sole API/static server. Port `5173` must remain unbound in this mode. This differs from legacy V5.10 Vite development mode, whose UI was `http://127.0.0.1:5173`.

`build` runs the actual source-audited 13-hash-pinned minimal Python environment installation and npm `ci --ignore-scripts`, then `npm run build` (full TypeScript validation and Vite static bundling). Every output asset in `dist/` is registered in `.apmesh-local-review-inventory.json` by its exact filename, byte length and SHA256, linked to the npm package-lock SHA. `preflight` independently reopens every generated asset, rejects unexpected or symlinked files, modified contents and unauthorized package-lock drift, and confirms the static local ASGI import dependency closure remains **FastAPI alone**. The inventory is **self-created and is not a trusted software signature**. The `build` command neither compiles original C++ nor qualifies a new adaptive epoch.

`smoke` starts the single local server and checks the genuine source catalog, P1 SVG exact bytes, the compiled HTML/script/style assets, the benchmark page, no dev HMR routes, 11 live negative HTTP access attempts (host/origin/cross-site/POST/hidden path/URL-encoded traversal), same-origin CORS and port 5173 absence. `original-smoke` first independently reauthenticates the **original retained C++ source** and additionally executes the *unchanged* two V5.9 browser source tests plus two V5.11 no-HMR/static security browser tests against that same backend/static port. The original accepted source remains step `[1]` only. The CI separately checks both port 8765 and port 5173 are unbound **after** shutdown.

## Source geometry and scientific claim boundary

| Model | Original accepted C++ global step | Actual original TRI | Native source patches | Original vector SHA256 |
| --- | --- | ---: | ---: | --- |
| Eistute | [1] | 1,168 | 4 | `c3757577ddc6cc147a029303be4bbe60fa0a87e4063829257ef7f7d91764bd66` |
| Book | [1] | 4,256 | 28 | `8d639313d8ade37fd4a8b0347fe5787d5d2db15296f0d3e6c6844e6abb39b248` |

The V5.9 E2E selects genuine original Eistute source patch 3/element 5350/native node 200 and Book patch 27/element 4250/native node 909; source-accepted face/node UV identity is independently matched to original C++ raw accepted NDJSON and file bytes. Original C++ generator **is not reexecuted in V5.11**. Source faces are not asserted to be physically welded across patch boundaries. No independently accepted second original source epoch, descendant face ancestry, continuous geometric CAD error, anisotropic source tensor, all-QUAD method or validated R2.8 LOD.

## Threat and retention limits

Static one-port mode reduces the Vite dev/HMR exposure, but cannot authenticate already-malicious local processes or browser extensions. Files are SHA checked on each response, strict known path allowlisting, read-only endpoints, loopback-only Host and Origin guards; this remains a **developer/research preview**, not a production security penetration test. It has **no code signing, offline reproducible installer, legal license distribution certificate or external web deployment approval**. The original ten-file ZIP is privately preserved in Google Drive, with upload/download byte equality previously verified. Native GitHub historical Actions source artifacts expire after 14 days and an automatic CI job referencing them must continue to fail closed after expiration, not substitute unverified sources.

[Issue #255](https://github.com/tiagosombrra/apmesh-modernization/issues/255) remains OPEN until an **independent human on actual physical Windows and Linux machines** reproduces this exact one-port compiled workflow and signs the dated review. The manual physical checklist is the same substantive source-identity/UV/graphics/useability checklist from V5.10, with the **V5.11 single origin and built-asset source hashes** recorded. GitHub-hosted Windows/Linux + software-emulated Chromium **is not physical GPU/VRAM/RAM or independent usability attestation**. [Issue #250](https://github.com/tiagosombrra/apmesh-modernization/issues/250) still requires distribution license scope and notices. [Issue #251](https://github.com/tiagosombrra/apmesh-modernization/issues/251) still requires paper format/adviser decisions. Do not merge the stacked PRs, ship an installer, tag/release or claim scientific R2.8 LOD.

## CI and build equivalence — final certified source results

Initial complete source code [GitHub Actions #45164240240](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45164240240) **2/2 SUCCESS**, Ubuntu 24.04 and Windows Server 2022, implementation SHA `7ff171203f44e07d551c4ea14af66d43d6d30d2c`. Both systems had **35 Python unit/adversarial PASS**, **4 actual hosted Chromium PASS**, original C++ source reauthentication, exact original accepted Eistute/Book SVG downloads, **7 statically compiled assets**, 13 Python API packages, 11 hostile HTTP controls and no HMR WebSockets or external network requests. **Cross-platform aggregate build inventory SHA differed**: Linux `ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5`, Windows `d103d157c4b6fdb8709577b64d9d1c746c1b179d037e6f0fd80fac61410d38d3`. The initial 2/2 result **certifies per-host integrity, not byte-identical compiled artifacts across hosts**.

A follow-up CI records per-asset SHA for both builds and preserves complete `dist/` contents to diagnose and correct any differences. **Do not mark cross-platform bundle equivalence PASS unless complete original build bytes are compared and independently reproduced after the correction.** All later status/results must be added with a date, exact SHA and grounded Actions/artifact links.


### Final independently rechecked same-code results — 2026-11-23

**[GitHub Actions #45165895108](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45165895108): 3/3 SUCCESS**, exact *tested implementation and CI code SHA* **`4f361d9b1e754c1e128ae74a42eb4173822bcaf6`**. The two OS jobs **both passed** **36 Python/adversarial tests and four *mandatory actual hosted Chromium* tests each**, including original C++ postcommit source reauthentication, accepted Eistute/Book real source identities, SHA-pinned SVG downloads, P1 linked XYZ/UV, staged Band not accepted, 11 hostile HTTP security/path negative probes, absence of any Vite dev/HMR/remote network, only a built static UI from the minimal 13-package Python API. Both locally bound ports were verified free after subprocess teardown, with no claims of physical workstation GPU.

The **third independently hosted Ubuntu comparison job** (not merely two independent self-passed host tests) downloaded the Windows and Linux source/UI artifacts **from the same exact tested commit** and **reopened and SHA-256-checked every one of the actual compiled file bytes**, the complete per-host build inventories, original raw C++ source-reopening receipts and genuine original browser source receipts. **All seven compiled assets and both inventory manifests matched exactly**, with one SHA256 on **both** platforms:

`ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5`

Root cause of previous failure: Windows Vite generated **CRLF and a single CRCRLF** in `index.html` and `bench.html` (all **five generated JS/CSS assets were already byte-identical**). An initial normalization attempt accidentally used double-escaped **literal** `\\r` and `\\n` sequences in both the normalizer **and its unit test**; the independent third job detected this false negative and refused acceptance. That defect was corrected to actual Python carriage-return/newline byte escapes, the adversarial unit now exercises real CRLF/CRCRLF, and **only generated HTML** is normalized idempotently to `LF` before inventory creation. No original C++, source UV geometric coordinates, document source identities, JS/CSS data or earlier certified native PDFs were changed.

Evidence downloads (each automatically expires **2026-12-07**; not a formal binary release):

- [Cross-host exact built-byte and original C++ source comparison proof #14814783677](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45165895108/artifacts/14814783677)
- [Windows compiled source/UI and original native reviewer receipts #14813893782](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45165895108/artifacts/14813893782)
- [Linux compiled source/UI and original native reviewer receipts #14812454836](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45165895108/artifacts/14812454836)

**Disposition:** V5.11 compiled one-port *research software reviewer* implementation is **source/asset/runtime/cross-OS byte certified** for the exact tested commit, **not signed, distributable, authenticated for production or verified by an independent physical reviewer**. The previously original C++ source acceptance remains only global step `[1]` per model; the R2.8 scientific LOD gate remains BLOCKED. Original C++ source artifacts were **reopened**, not scientifically recompiled/reaccepted in V5.11. Original ten-file source corpus remains privately archived and roundtrip byte-verified in the personal doctoral Drive; do not publish a private link in a public repository.
