# APMesh Mesh Studio — Product architecture and independent regression audit

**Audit date:** 2026-11-15. **Code under audit:** `feature/mesh-studio-fixture-first-20261114` at `8ee14e64221212247485bcd4318a871bb1cc8c5f`. **Audited source archive SHA-256:** `fb17a6cb5a5f6baed9dd0c71dbc4e154fd33f4096259b46fa6151a7503a98760` (`APMesh_Mesh_Studio_S0_S5d_Real_Candidates.zip`). **Status:** audit-only findings and a proposed frontend architectural decision; no production generator or UI migration implemented.

## Executive finding

The source-aware scientific Python engine and 2D-vector publication components are useful and locally regression-qualified. A complete, modern, cross-platform interactive product is **not** qualified. The current QtWidgets/PySide6/PyVistaQt GUI has only 5% statement execution coverage in the local suite, cannot be launched in the current environment, and has no dedicated GitHub Actions workflow. A web-first frontend proof-of-concept should precede further product expansion; do not rewrite the already verified numerical logic in JavaScript.

## Independent executed regression

| Gate | Direct evidence | Result |
| --- | --- | --- |
| Clean extraction | 149 source and artifact entries, no ZIP traversal | PASS |
| Full Python tests | 9 module-based unittest suites, **191/191 methods pass** on Python 3.13.5/Linux | PASS |
| Synthetic fixture oracle | 10 valid plus 6 expected invalid and 8 synthetic history rows | PASS |
| Statement coverage | 69% non-test code; importer 91%; quality 94%; scene model 95%; desktop GUI 5% | MEASURED, not a correctness certificate |
| Real S5d CLI | Regenerated report JSON, CSV, 2 SVG and 2 PDF byte-identically to archived outputs | PASS |
| Real OBJ provenance | SHA-256 of control, band, west, north, both equal between original Linux CI ZIP, Windows CI ZIP and committed Studio sources | PASS, 15 hashes / 5 unique artifacts |
| Vector figures | Two single-page PDFs contain zero embedded raster images; two SVGs contain zero raster `<image>` elements | PASS for those 2D publications |
| Qt interactive launch | Explicit smoke returns code 2, missing optional PySide6/PyVista/PyVistaQt; no GUI receipt | NOT EXECUTED |
| Studio GitHub Actions | No Studio-specific workflow/run on branch; only QUAD research workflow configured | NOT EXECUTED |
| Exploratory scale | 3,600 / 25,600 / 57,600 QUAD import and scene batches; import approximately 0.10 / 0.36 / 0.88 seconds; cumulative process peak RSS 98 / 130 / 196 MiB | LIMITED, not a GPU/UX/500k qualification |

The first `unittest discover -s tools/mesh_studio` invocation did not supply a package import root and failed; qualified module-name invocation passed. Introduce a documented, isolated `pyproject.toml`/CI test entrypoint.

## Confirmed defects and blockers

**P0 — Actual scientific source schema missing.** `import_obj._read_sidecar` accepts only `apmesh.meshstudio.synthetic.v1` with `synthetic=true`. A real sidecar schema is rejected as `unsupported_sidecar_schema` even when its OBJ SHA-256 is valid. Generic OBJ grouping does not identify original source patches, shared curves or non-manifold ownership. The real multi-patch/fan28 capability remains synthetic only.

**P1 — Scientific metadata is mutable after qualification.** `MeshDocument` is a frozen dataclass but embeds `tuple[dict, ...]` as `source_curves`. A valid shared-curve fixture's dictionary was changed after import, while the stored OBJ source hash remained the same. Replace with deeply immutable, canonical typed records and a whole-scene metadata hash.

**P0 — No true source method timeline.** S1b stages are explicitly simulated, not observed original generator events. Final mesh OBJ cannot reconstruct decision order, accepted/rejected candidate epoch lineage, metric source or rollback events.

**P0 — Final app UX and distribution missing.** QtWidgets application code exists but has never passed Windows/Linux GUI smoke, actual physical mouse selection, GPU compatibility or packaging tests. No signed installer, dependency lock or startup guide validated for non-developers.

**P0 — Real all-quad and anisotropy unavailable.** The tested source is one original controlled Bezier patch and staged physical QUAD/AFT candidates, not a six-cell factorial algorithm comparison. The accepted adaptive epoch count is zero. The finite 4096-site error is neither a continuous bound nor a PDE solution error. Five meshes belong to one controlled evaluation and are not statistically independent repeated runs.

**P0 — Scale not qualified.** Importer has a hard 20 MiB file limit; UV scene batches duplicate vertices by face corner. No proven 50k/500k user-interactive target, chunked streaming, LOD or bounded browser memory protocol.

**P1 — Scientific/editorial UX still incomplete.** Vector PDF/SVG/CSV/LaTeX are reproduced; an interactive multi-panel journal composer and actual observed method step export do not yet exist. VTK shaded 3D exports are raster and must remain labeled as such.

## Technology review / proposed ADR, pending implementation proof

Qt 6 is not obsolete: Qt 6.12 LTS (2026) includes modern Qt Quick/QML and GPU-accelerated UI, while traditional QtWidgets remains suitable for native desktop. Our actual implementation uses native QtWidgets, not Qt Quick, and is not qualified as a full product. Do not generalize its limitations to the Qt framework.

**Recommended test-first target:** React + TypeScript + Vite user interface, vtk.js renderer (WebGL qualified first), Python/FastAPI versioned scientific service retaining the existing import, geometry/quality/provenance and journal output engines. Use structured typed arrays and source-ID mapping, not a lossy OBJ conversion in the browser. Prefer locally served Web UX for research iteration and collaborator access; test Tauri 2 as a later offline desktop wrapper (Python sidecar, capabilities, signed installers), not a first milestone. Keep QtWidgets only as an optional diagnostic legacy shell. Note vtk.js is explicitly a subset of native VTK: do not promise equal filters or native-scale performance without benchmark.

Alternatives: Qt Quick/QML if the Web picking/LOD gates fail, and Electron + Chromium when consistent runtime takes priority over WebView memory footprint. Choice of wrapper must be decided after cross-platform measured prototypes.

## Revised stop/go roadmap

1. **R0 (repair & CI):** deep-immutable real mesh provenance contract; patch/curve incidence semantics; `pyproject.toml`, pinned dependencies and dedicated Studio CI Linux/Windows; negative input tests and reproducible CLI commands.
2. **R1 (Web vertical slice):** real P1 plus one staged candidate, dual XYZ/UV vtk.js panes, typed QUAD/TRI layer switch, exact original face ID picking, linked quality inspector and camera recipes; strict statuses. Use Playwright for actual browser interactions and screenshot baselines; preserve mathematical data and SVG/PDF generator in Python.
3. **R2 (data size):** 1k/50k/500k inputs with source-sensitive owners, bounded typed-array transfer, benchmarked memory/latency/FPS and LOD/streaming; do not remove the 20 MiB OBJ cap without replacing it with bounded alternate import policy.
4. **R3 (scientific trace):** real multi-patch/non-manifold topology contract, opt-in generator event emission under distinct review, observed vs simulated stages, accepted/rejected lineage and rollback. Do not touch generator main/TRI defaults in Studio branch.
5. **R4 (article production):** dynamic panel composer, anisotropic tensor legend when original metric fields are available, 3x2 matrix with NOT_AVAILABLE, accessible UI, settings/presets and true-vector audit.
6. **R5 (distribution):** choose Tauri or alternative only after successful Web proof, Python sidecar packaging, loopback origin/token controls, licensing/SBOM, smoke on Windows/Linux and reproducible release artifacts.

### R1 acceptance, before selecting a permanent frontend

- Two original OBJ datasets display correct TRI/QUAD counts, UV/XYZ and SHA, preserving original face IDs and patch ownership when available.
- Clicking one face in 3D selects exactly the same source face in UV and shows verified metrics; filters, cameras and scene reload function in a **real browser**, not a mocked function call.
- Browser-to-Python API responses match existing golden scientific JSON without reimplementing the algorithms in TypeScript.
- Run 20 browser E2E negative/positive cases, independent Python golden tests, and a recorded GPU/OS compatibility matrix.
- Run at least one Windows reference load/picking/rotation performance test with 50k elements and an explicitly reported 500k load/LOD feasibility test; set quantitative SLAs after baseline measurement.
- Figure export invokes existing audited SVG/PDF/CSV/LaTeX engine; no false vector claim for shaded 3D outputs.

**Unmodified:** `src/`, `include/`, QUAD algorithm code, `quad-templates` and `main`. **Not claimed:** new Web UI, installed Qt application, real source timeline, actual all-quad/aniso algorithm, or new Studio CI validation.