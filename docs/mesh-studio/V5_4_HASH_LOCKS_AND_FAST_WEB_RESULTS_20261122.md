# Mesh Studio V5.4 — transitive SHA256 dependency closure and isolated fast source Web lane

**Scope:** source-preserving Studio engineering, 2026-11-22. This is an incremental efficiency/reproducibility stage, **not** a new C++ original geometry or R2.8 scientific LOD admission. No original AFT/Adapter/generator policy, original model, CAD input, accepted research TRI, original source provenance or default VTK picker was modified.

## 1. Confirmed baseline defect and risk

Before this stage `tools/mesh_studio/web/package.json` pinned direct React/vtk.js/Vite/Playwright versions but had **no committed `package-lock.json`**, and the primary CI used `npm install` on each browser run. Python direct requirements for full FastAPI/VTK scientific regression and minimal original-native PDF journal output had no transitive closure, wheel hash or separate Linux/Windows resolution. A repeated cloud CI installation could therefore select different transitives without changing an original C++ source file.

The source-native validation workflow also rebuilt and reran original Eistute/Book AFT and multiple per-attempt forensic studies when **only frontend CSS changed**. A fast frontend/browser test that does not recompile the original C++ is *not* a scientific accepted-source attestation.

## 2. Materialized dependency source locks

Generated on GitHub-hosted Node 22/npm 10 and Python 3.13, with pip 25.3 and **pinned pip-tools 7.5.2**. Original package **direct versions unchanged**. Every Python profile was resolved with `pip-compile --generate-hashes` on its designated OS, then installed successfully from those hashes using `pip --require-hashes` and passed `pip check`. npm produced a native lockfile v3 with registry integrity metadata and passed `npm ci`, source JS contracts and Vite/TypeScript production compilation. Full original raw bootstrap [#45071366154](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45071366154) **4/4 SUCCESS**.

| Profile, exact current source file | Packages | Distribution SHA-256 records | Original file SHA-256 |
| --- | ---: | ---: | --- |
| `tools/mesh_studio/web/package-lock.json` (Node/npm v3) | **141 transitive** | npm registry integrity for all 141 (SHA512 fields) | `12f5a67d1b56007022f5843cbad324c0df987df006b9eac6591247f16cf38a90` |
| `tools/mesh_studio/locks/requirements-web-ci-linux-py313.lock` | **32** | **888** | `efef5b213afddd7c78c57c14992ac7027f18a8a4f471ab796f99ef947bba3674` |
| `tools/mesh_studio/locks/requirements-web-ci-windows-py313.lock` | **32** | **888** | `5ea079f9f6b0e7000ae5735d3928252a06141c84032b5a1fd70a57c4a33fd06f` |
| `tools/mesh_studio/locks/requirements-native-pdf-ci-linux-py313.lock` | **15** | **674** | `641291f83b5dea1b97223529fcb98172508b531cc7d4855e57ab9743892f5d28` |

The first bootstrap [#45071070289](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45071070289) correctly failed on **two workflow harness mistakes**: comparing serialized npm object property order rather than mappings, and calling an unsupported `piptools --version` entrypoint. These were corrected without changing original project packages, successfully rerun in [#45071158217](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45071158217), and rerun after adding chunked public artifact transfer in [#45071366154](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45071366154). No failed bootstrap is misrepresented as code-scientific success.

**Admission security:** chunked bootstrap logs expose *only public dependency-lock content*, not credentials, source C++ private data or original scientific model secrets. Lockfiles were committed to the experimental research branch through the authenticated GitHub file API after digest checks; no GitHub Actions job was granted write permissions or merged source automatically. SHA256 digests and exact direct versions are independently guarded by `tools/mesh_studio/dependency_lock_audit.py` and adversarial `test_dependency_lock_audit.py` (direct drift, untrusted npm registry, missing hash, missing file).

**Cross-platform line-ending repair:** the original Windows bootstrap artifact emitted CRLF and had original raw SHA-256 `963c4f6f54f4e531d8f32dceea29da2300c649b324398e3c5df5abba2ccb194e`; its **identical pinned requirements and wheel hashes** were normalized once to Git-source-canonical LF (new SHA-256 `5ea079f9f6b0e7000ae5735d3928252a06141c84032b5a1fd70a57c4a33fd06f`). Added explicit `.gitattributes` `text eol=lf` for Web `package.json`, `package-lock.json`, all three lock files and direct Python requirement manifests, plus actual-byte negative regression tests. An earlier Windows checkout had also altered npm source SHA through automatic CRLF conversion despite equivalent dependency semantics. The new exact source Windows+Linux LF gate is required to confirm byte identity; **do not confuse EOL normalization with a scientific method or dependency upgrade.**

**Limitations:** npm integrity and Python wheel hashes protect *declared package artifacts*, but do not independently certify the security of all packages, OS libraries, GPU drivers, reproducible C++ object bytes, full SBOM/licenses or air-gapped installation. Python Python 3.13 lock is OS-specific; using Linux hashes as Windows scientific certification is prohibited. Browser API's existing three minimal direct Python packages remain an independently reviewable minimal-runtime lock candidate if reducing fast lane startup time becomes material.

## 3. Exact-source CI installation changes

The existing `.github/workflows/mesh-studio-validation.yml` now:
- Enforces `python -m tools.mesh_studio.dependency_lock_audit` before installing source scientific requirements.
- Installs the Linux or Windows matching complete Python lock with `pip install --require-hashes`, then `pip check`. Original source numerical tests and original C++ native accepted/rejected study are **not skipped** for changes to those source declarations.
- Installs the separate Linux native original-source PDF profile by its 15-package hash lock and `pip check`, instead of resolving dependencies anew.
- Uses `setup-node` npm dependency caching and `npm ci` (not `npm install`) for source-vetted browser E2E.
- Retains all actual original C++ Adapter/AFT/header/model/config/QUAD triggers and **all previous original native source and browser provenance controls**; the original mandatory browser `needs: native-lineage-optin` relationship is unchanged.
- Excludes **only** `tools/mesh_studio/web/src/style.css` beyond previously exempt readme files from expensive original C++ replay, because CSS cannot alter the original native mesh. The new FAST lane still tests the resulting UI. Core source identifiers, browser source provenance parsers, native scene import and source-certified publication TS files are **not** excluded.

## 4. Source-scoped FAST UI gate (no misleading source qualification)

New `.github/workflows/mesh-studio-fast-web.yml` is a distinct **read-only, cancellable** workflow on Web/UI/API changes, with exactly the same source-locked npm and Linux Python dependency profile. It runs source lock audit, `npm ci`, TS/Vite build, JS geometry/source contracts and a bounded subset of hosted Chromium P1/staged controlled-original source tests (real P1 XYZ+UV dual view, source IDs, V2 transport, cancellation, read-only source-UV vector download). It explicitly labels **original C++ native science NOT_EXECUTED** and **physical GPU / R2.8 scientific LOD NOT_QUALIFIED**.

**Safe initial split only:** a pure `style.css` edit triggers fast UI testing without original C++ rebuild. Any original C++ or scientific/native-provenance code edit still triggers the full expensive source-native workflow. For arbitrary other frontend TS edits, both workflows currently trigger; **a broad fast/native source-impact split remains OPEN**, to be performed only with an independently negative-tested allowlist. Do not silently exclude unknown new TS files from original source scientific checks.

## 5. Qualification gates and remaining work

- **Dependency hash generation and clean install:** PASS, four GitHub-hosted bootstrap jobs on exact SHA `957dc02a86be110c3f5b21899928fc1dc4b805b9`.
- **Independent code-level lock guards:** ADDED, subject to the full scientific regression and adversarial test receipt for the exact merged research-branch source SHA.
- **Main scientific original-native/source-bound Chromium with new locks:** AWAIT exact-head 4/4 success. The prior [V5.3 code #45043785743](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743) fully qualified the *old* direct-only installation; do not transfer its 4/4 status to this locked source revision.
- **FAST source-scope Chromium: PASS** [Actions #45071845616](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45071845616), exact code SHA `9d63b2b93176f95ffe2815690f54208228ce57db`: installed SHA256-hashed Linux Python + npm integrity-locked Web dependencies, independent profile audit, TS/Vite build and JS source contracts, and **18 hosted Chromium tests passed (0 skipped)** over original-source P1/staged XYZ+UV, V2 transport, cancellation and real UV SVG. The job itself explicitly emitted `V54_ORIGINAL_CPP_NATIVE_CI_QUALIFICATION=NOT_EXECUTED`: it must not substitute for original compiled Eistute/Book native provenance.
- **Broader CI isolation:** OPEN; constrain all safe frontend-only paths with explicit risk review, change classifier/negative fixtures, measured total runtime and mandatory independent original-native requalification before any protected merge.
- **Review and supply-chain:** reviewer sign-off, pinned workflow action SHAs, SBOM/license inventory, CVE triage, offline vendor wheelhouse, signed build and physical Windows GPU/RSS/VRAM remain OPEN.

Scientific status unchanged: original accepted Eistute/Book TRI step **[1] only** per original process; R2.8 LOD BLOCKED without at least two genuinely accepted same-process epochs, descendant face identities, continuous geometry error bounds and an independently qualified physical seam policy. No tag, release or main merge; PRs #239/#244/#245 remain DRAFT.
