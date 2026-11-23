# Mesh Studio V5.9 — real original C++ source reviewer journey on the lean local API

**Date:** 2026-11-23. **Engineering scope:** a finite Windows/Linux clean-install reviewer task, not a newly generated/accepted native C++ epoch. The original C++ source snapshots come from the **same** pre-certified original scientific source run [#45147268663](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45147268663), exact source code SHA `7d41ab8ec55b34bf879f9efc2a547168e50143de`. **R2.8 scientific LOD remains BLOCKED.**

## 1. What is verified — exact source admission rather than user-provided JSON trust

The review flow reads two original native GitHub Actions artifacts:

- [V5.7-era original scene/figure artifact #14805520368](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45147268663/artifacts/14805520368): original `r2720-native-accepted-scene.json`, `v52-native-accepted-uv-publication/manifest.json`, two source-accepted Eistute/Book patch-local UV SVG files.
- [Identical-original-run original C++ postcommit artifact #14805181312](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45147268663/artifacts/14805181312): both accepted-step-1 NDJSON records, both native-lineage audit JSON files and both actual generator stderr logs.

**`tools/mesh_studio/v59_reviewer.py`** requires exactly ten files, with independently pinned full byte length and SHA256 each, no extra file and no symlink, and independently invokes the **original** `audit_accepted_native_publication` on the retained C++ postcommit evidence. The auditor rederives the scene from raw original C++ accepted face keys, source native node/UV/curve identities, compares actual published source SVG geometry and checks its original bound manifest. A matching scene+manifest pair **alone** cannot certify C++; no new C++ run is pretended.

Important identities:

| Original source file | Exact bytes | SHA256 |
| --- | ---: | --- |
| Eistute original C++ accepted NDJSON step [1] | 599,332 | `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6` |
| Book original C++ accepted NDJSON step [1] | 2,155,188 | `e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a` |
| Combined original accepted source scene JSON | 1,716,994 | `eb72cb058fef2a7632e09f5a3572f39e32f4d9038780cce05337d1afd86f2816` |
| Source-locked vector SVG manifest | 3,778 | `85e2df4d178bb277c15989d6893903be0e69e1fe37b162ca1dc675e0afe59aee` |
| Original accepted Eistute vector SVG | 536,961 | `c3757577ddc6cc147a029303be4bbe60fa0a87e4063829257ef7f7d91764bd66` |
| Original accepted Book vector SVG | 1,980,092 | `8d639313d8ade37fd4a8b0347fe5787d5d2db15296f0d3e6c6844e6abb39b248` |

The other four files (native-lineage reports, original stderr logs) have separately pinned SHA256 in the executable source inventory. This is **historical source read-back**, not fresh compilation, a proof of cross-epoch lineage, a geometric error bound or a physically welded mesh.

**Retention limitation:** the GitHub Actions source artifacts have 14-day retention, expected through **2026-12-07**. The CI uses `actions/download-artifact` pinned by full SHA, with a fixed run ID, artifact names, `actions: read` and exact expected file bytes; after expiration it **fails closed** rather than substituting unverified data. For longer-term reproduction, save the ten-file original reviewer corpus ZIP separately (already prepared for the user, byte-identical original files, with manifest); extract under the project root to `build/v59-native-reviewer/`. No changes to source C++ or original published V5.3/V5.7 PDFs are necessary.

## 2. Reproduce local source reviewer workflow

Prerequisites: official CPython **3.13**, Node **22**, npm **10**, Chromium Playwright browser installed by npm (initial installation requires network); standard browser graphics are not physical GPU performance evidence.

From the repository root, after extracting the corpus archive:

**Linux**
```bash
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_launcher setup
cd tools/mesh_studio/web && npm exec playwright install chromium && cd ../../..
python3.13 -m tools.mesh_studio.v59_reviewer smoke
```

**Windows PowerShell**
```powershell
py -3.13 -m tools.mesh_studio.v59_reviewer preflight
py -3.13 -m tools.mesh_studio.local_launcher setup
Push-Location tools/mesh_studio/web
npm exec playwright install chromium
Pop-Location
py -3.13 -m tools.mesh_studio.v59_reviewer smoke
```

The V5.9 `smoke` invokes the **real V5.8** already tested local launcher and retains its Python 13-package source-hash-locked environment, FastAPI port **127.0.0.1:8765** and Vite dev port **127.0.0.1:5173**. It does not install PyMuPDF, VTK or the native publishing stack in the local API environment. The launcher starts both servers, verifies pinned P1/local status + vector SHA, runs **only** the V5.9 real-source browser test with the existing two servers, then stops both even when that browser test fails. A separate CI step verifies neither port remains bound.

The browser test (not a synthetic fake C++ fixture) visits the real source P1, selects an original face from UV and verifies the **same ID** in both XYZ/UV views, checks Python quality and original P1 SVG source hash, then switches to real staged Band and confirms it **is not an accepted adaptive epoch**. It opens the native source viewer, imports the certified Eistute/Book original scene and both original SVGs plus manifest, switches Eistute source patch **3** and Book source patch **27**, checks accepted original TRI totals **1,168** and **4,256**, source fan marker original native node ID, native element ID membership in the real accepted C++ face tuples, 3 UV/XYZ corner rows, independent source NDJSON SHA and downloads both original source vector SVGs with **byte-exact SHA**. For adversarial controls it rejects a forged source JSON SHA, a manifest with falsely claimed scientific LOD and a changed SVG native-node identity even after a valid upload is already present.

A success response proves the **reviewed local software path** and retained original artifacts, not authenticity of any arbitrary user file, or certified physical workstation GPU.

## 3. Current actual CI result and boundaries

[GitHub Actions #45157755246](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45157755246) **2/2 SUCCESS** at implementation SHA `2db09df200eee31ce9a7cc5fe10aa2e0ffd35ae9`; both Ubuntu 24.04 and Windows Server 2022 initially ran **15 Python unit/adversarial tests** (9 original V5.8 plus 6 new V5.9, including an **actual** original CPP source reaudit); the final implementation added a sixteenth canonical-XML unit test, then **2 real hosted Chromium tests PASS per OS**, using the minimal 13-package local API setup, Vite, source-bound P1, actual Eistute/Book, SVG downloads and three forbidden-source negatives. Clean server shutdown and port-free checks PASS.

Actual source face demonstration from the browser:
- Original Eistute `patch_slot=3`, source accepted element `5350`, observed native source node `200`, 1,168 original TRI.
- Original Book `patch_slot=27`, source accepted element `4250`, observed native source node `909`, 4,256 original TRI.
- Both original-source vector SVG downloaded **byte-for-byte identical** to the pinned files (digests above). Repeated C++ compilation was intentionally avoided.
- Browser test recorded no requests to third-party web domains.

**Additional P1 source SVG reproducibility defect found and FIXED.** The first host-specific output had Linux SHA256 `c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe` vs Windows `4ccadf2649247606f3eae107f957514d4bd5e2e37776a90992cf7746d78ff44c`. Both raw P1 SVG files were downloaded from [Linux artifact #14809287765](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45158229599/artifacts/14809287765) and [Windows artifact #14809856571](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45158229599/artifacts/14809856571). **The sole byte difference** was the XML declaration's line ending (`LF` on Linux vs `CRLF` on Windows), exactly one extra `\r` byte. Independent byte replacement on the downloaded original output yielded exactly identical content. `svg_figure.write_canonical_svg` now writes an explicit fixed XML UTF-8 declaration plus `LF` as bytes and is used by both the primary headless source vector renderer and the API's final metadata-rewrite path. An added adversarial/canonical newline test and original P1 browser contract require **the same complete source vector PDF-free SVG SHA on Linux and Windows**. No UV doubles, source triangles, identity keys, or original accepted native artifacts were changed.

**FINAL [GitHub Actions #45158811660](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45158811660) is 2/2 SUCCESS**, Ubuntu 24.04 and Windows Server 2022, on actual code SHA **`ed4ca10854d8fbff5227220c97dc93f5b4c791c3`**. Both OS have **16 Python unit/adversarial tests PASS** (including real source raw C++ re-audit and canonical XML declaration) and **two real Chromium Playwright reviewer tests PASS**; no skipped reviewer browser cases. Both P1 actual emitted source SVGs now have identical SHA256 `c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe`, with identical original native Eistute/Book vector hashes as before, no remote HTTP requests and no orphan ports. The original C++ scientific generator was not recompiled in this lean viewer workflow, and hosted browser software rendering is not qualified physical GPU.


## 4. Hard exclusions and review status

- The project remains a **DRAFT research branch**, not `main`, a release, signed installer or deployment. The original native code scientific policy, original V5.3 and V5.7 PDFs, point ownership, per-corner UV and default source picker have not been modified.
- **Scientific R2.8 LOD remains BLOCKED.** Only accepted source step `[1]` per original Eistute/Book same-process run, no accepted descendants, physical welding of native C++ node owner pointers or continuous CAD error certificate.
- Original source files were generated by prior real C++ workflow, **reopened in V5.9**, but the newly created minimal API CI did **not** rerun original C++. No cross-machine independent scientific reexperiment or physical GPU/VRAM/RSS performance is claimed. The Playwright graphics renderer is a hosted CI/software-emulated environment.
- Product reviewer signoff on a physical Windows and Linux workstation is **OPEN**, including real browser context, local filesystem deployment and use. Licensing and distribution completeness remain [Issue #250](https://github.com/tiagosombrra/apmesh-modernization/issues/250). The native printed Book figure venue/adviser decision remains [Issue #251](https://github.com/tiagosombrra/apmesh-modernization/issues/251).
- **Important:** this lane only runs for its named branch and explicitly listed source/controller changes; original C++ scientific changes in `src/**`, `include/**`, `configs/**`, `input_models/**`, `research/quad/**` must retain the separate **full original SOURCE_NATIVE workflow trigger**. Source CI cannot be replaced by a stale historical artifact in those cases.

**Disposition:** The finite hosted original-C++-artifact-to-minimal-software-to-browser reviewer path is implemented and **2/2 PASS** on Linux+Windows. The P1 on-demand source SVG cross-platform byte mismatch is **FIXED and EXACT-SHA CERTIFIED**. Physical desktop/human reviewer signoff and actual deployment security/license completeness remain OPEN. Original C++ R2.8 scientific LOD is still BLOCKED. Do not mark Stage 3 production or R2.8 LOD complete.
