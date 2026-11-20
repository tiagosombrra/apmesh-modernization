# Mesh Studio V5.1 — measured source cache, offline Web export and research UX recovery

**Date:** 2026-11-20. **Branch:** `feature/mesh-studio-r27-bvh-20261116`, PR [#239](https://github.com/tiagosombrra/apmesh-modernization/pull/239), DRAFT / UNMERGED. **Roadmap:** [V5 audit and recovery](MASTER_PLAN_V5_AUDIT_AND_RECOVERY_20261120.md). This is a **product/engineering-only** increment. Original C++ Adapter, AFT, generator acceptance, original models/configs, source scientific results, original Eistute/Book accepted epoch counts and default VTK picking remain unchanged.

## 1. Measured — source-hash-verified, same-process HTTP-internal cache benefit

Added `tools/mesh_studio/benchmark_web_cache.py`, independent offline tests `test_benchmark_web_cache.py`, and a dedicated Linux scientific CI step/artifact using **exact source OBJ** in the fixed original study catalog.

Method preregistered in benchmark docstring/source: 16 pairs for each real original **P1** and staged, **unaccepted Band**; API `/faces/0` and `/quality`. Alternating cache-disabled-proxy/warm ordering, full cache clear before each disabled sample, and one untimed priming call before each warm sample. **All** timed requests include source SHA-256 re-reading and validating the pinned original OBJ. Request response JSON must match exactly across every sample; missing/mutated/foreign source aborts the benchmark. Percentile: sorted nearest-rank p95. P50 is median; keep raw times per case in the Actions artifact.

The measurements below come from **actual [GitHub Actions #44747081730](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44747081730)**, exact tested code SHA `0bc9d3fac0024da8d9d4f62e247ac8123c7091df`: **4/4 completed SUCCESS** — scientific Python **528 passed / 4 optional skipped Linux**, **528 passed / 10 environment-skipped Windows**, source-native original C++ PASS and **60 Chromium passed / 5 intentionally skipped**. This code includes the cache, source-vector SVG export, browser cancellation and research study control. The subsequent offline-font-removal change and its dedicated new Chromium case require **separate final-head CI** [#44747343921](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44747343921), not covered by the first green run.

| Real input / endpoint | Cache-disabled-proxy p50 / p95 (ms) | Warm cache p50 / p95 (ms) | Interpretation |
| --- | ---: | ---: | --- |
| Original P1 face 0 | **3.3943 / 6.0902** | **0.7907 / 1.3665** | About **4.3x p50 improvement** in this runner-only proxy |
| Original P1 full quality | **4.7898 / 5.3299** | **2.2527 / 2.3314** | About **2.1x p50** |
| Staged Band face 0 | **4.3661 / 4.9548** | **1.1280 / 1.5720** | About **3.9x p50**, still an unaccepted candidate |
| Staged Band full quality | **6.2409 / 6.8265** | **2.7815 / 3.2027** | About **2.2x p50** |

**Limitations:** cache-disabled proxy is **not the historical unmodified Git commit**; this is one hosted Linux Python process using FastAPI **TestClient**, not TCP/network/cross-process, browser click, UI paint, Windows physical GPU or GPU-present timing. Paired observations in one process are **not independent replications**, and reported ratios do not establish a general SLA or effect across machines. No unverified negative mode is discarded. Original quality data stays Python-only and cached by exact source path+SHA, with independent mutations/fail-closed checks.

## 2. Implemented research Web capabilities (subject to exact-source Chromium qualification)

- **Source-bound original UV vector SVG export:** new read-only `GET /api/v1/models/{catalog_id}/publication.svg` route reuses the existing audited `svg_figure.render_uv_svg()` and `audit_svg()` Python math/figure engine, not a new browser numeric metric. Fixed **155 × 120 mm** `SVG` consists of native vector polygons/text; no embedded images, scripts, event handlers or remote URLs. The endpoint returns SHA-256 for original OBJ and final SVG, safe source-hash-bearing download name, status header and embedded machine-readable XML metadata. It labels original P1 **CONTROLLED ORIGINAL — NO ADAPTIVE EPOCH** and Band/West/North/Both **STAGED CANDIDATE — NOT AN ACCEPTED ADAPTIVE EPOCH**. Unknown source id and changed same-name OBJ fail closed. No accepted-original Eistute/Book scene is deceptively represented as a P1 export.
- **Actual UI workflow:** source catalog -> verified XYZ/UV and original face selection -> original backend metric inspector -> *Exportar figura UV vetorial (SVG)* downloads exact currently selected catalog source. The download is a truthful **2D UV figure**, not a shaded 3D full-vector PDF, full multi-panel composer, continuous Bezier Jacobian certificate or claimed adaptive improvement.
- **Original native accepted scene discoverability:** a clear, reversible *Abrir estudo TRI original aceito* control opens the **separate** native Eistute/Book accepted-TRI inspector and retains the older `?nativeScene=1` opt-in. Native accepted original step 1 is **not merged with P1 or staged candidate source identities**. The user must upload the source-bound original native CI JSON locally. The browser validates the imported JSON's **declared** source identities/curves structurally but cannot independently authenticate original raw C++ SHA without additional source bytes. This is **a new usable entry point, not a certified automatic native dataset importer**.
- **Stale-request cancellation:** source document/model change uses AbortController for catalog, XYZ, UV and face requests; stale face detail is additionally rejected if original SHA/face ID no longer matches the selected source. Old source response errors cannot overwrite the newer active view. Playwright adversarial tests interrupt slow original requests while changing model.
- **Offline-first:** removed the sole observed remote Google Fonts CSS `@import`. No external font files are bundled. Browser test refuses any external HTTP(S) domain request when loading original source. Standard locally installed/system font fallback remains. Network behavior is a tested scope, **not an assertion about every optional browser integration**.

**New regression files:** `test_benchmark_web_cache.py` (4), `test_web_publication.py` (4), `web/tests/viewport-v5-source-request-races.spec.ts` (2), `web/tests/viewport-v5-article-source-export.spec.ts` (4). Browser specs require actual Chromium test execution before any pass claim. Existing Web tests, scientific Python and original-source C++/model parity remain required.

### Preserved original raw benchmark distributions

- Exact original [GitHub Actions V5 benchmark artifact #14633327746](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44747081730/artifacts/14633327746), original ZIP **2,423 bytes** containing the **15,602-byte source-bound JSON** with raw observations, alternating AB/BA order, original source SHA and full limitation labels.
- Original downloaded ZIP SHA-256 `7b8853e2b93f7bc0f32ed9d494daadb1e99efb54d2d0a53fba39ea5b0191e649`. Retained **byte-identical** in private personal doctoral Google Drive `Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados` as `apmesh-studio-v51-source-web-cache-0bc9d3f.zip`, then downloaded back and rehashed at **2,423 bytes** with the **identical SHA-256**. No private Drive URL is published in public repository documentation.
- These receipts demonstrate one hosted Linux source-verified TestClient benchmark run, **not** independent cross-host or complete user event-to-GPU measurement.

## 3. Open end-to-end P0.B gates

1. Source-bound **original accepted** TRI Eistute/Book -> independently source-authenticated original per-face XYZ + per-patch UV + exact native original face/curve identity -> independently audited original-triangle vector export. Do not infer this from synthetic upload or source P1 SVG.
2. Proper provenance-aware single Study Workspace, richer geometry/metric panels, keyboard accessibility, accepted/rejected attempt timeline and validated error recovery; existing native scene remains a separate upload component.
3. Offline distribution with deterministic JS and transitive Python locks, licensing/SBOM, portable Windows/Linux installations, accessible no-network smoke.
4. Cross-process real API p50/p95 with more repetitions/hardware, peak RSS/Worker/GPU, real source 50k+ (if source certified), independent vector PDF journal pages and accepted original Eistute/Book metric definitions.
5. PR review slicing and independent scientific reviewer decision on original AFT underresolution/transition floor **before** any acceptance change. R2.7.35 segment/native node pointer test only if a falsifiable, approved scientific question would be resolved.

**Scientific status unchanged:** each original native Eistute/Book model has only global accepted original step [1]; separate Eistute article/min13 processes are not two accepted epochs. R2.7.34's coincident XYZ seam vertex sets do not prove physically welded native node ownership or continuous surface error. **R2.8 scientific LOD BLOCKED. Original VTK picker default unchanged. PR #239 stays DRAFT and UNMERGED; no tag, release or main merge.**

## 4. Exact-state next checkpoint

Qualify the full new V5.1 implementation at one exact source SHA with the complete 4-job CI (Python Linux/Windows, native original C++ parity/lineage, Chromium E2E including negative races/offline/vector download). Re-open the raw benchmark artifact and retain its exact ZIP hash in the experiment evidence index. Once verified, report actual measured CPU cache benefit separately from first successful native article figure and browser user journey. If any test fails, repair within V5.1 without altering original scientific policy.
