# APMesh Mesh Studio — scientific inspection and publication modules S0–S5

## V5.11 — modo recomendado para a revisão local: frontend compilado em uma só porta

Para inspecionar o STUDIO sem executar o **servidor de desenvolvimento Vite/HMR**, utilize a V5.11 na raiz do repositório (Python 3.13, Node 22 e npm 10 no build inicial). Após compilar, toda a interface e a API compartilham somente `http://127.0.0.1:8765/`. O launcher é **local e voltado à pesquisa**, não um instalador assinado nem um serviço seguro para a internet.

```bash
python3.13 -m tools.mesh_studio.local_reviewer_launcher build
python3.13 -m tools.mesh_studio.local_reviewer_launcher preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher serve
```

No Windows PowerShell, use `py -3.13` no lugar de `python3.13`. Para uma revisão **automatizada com fontes C++ originais**, extraia primeiro os dez arquivos de `build/v59-native-reviewer/` do pacote preservado no Drive pessoal e execute `python3.13 -m tools.mesh_studio.local_reviewer_launcher original-smoke` (Chromium Playwright instalado). O comando não gera novos epochs nativos, mas reaudita o C++ original e faz a jornada Eistute/Book no navegador.

[**Protocolo V5.11 e recibos Linux/Windows**](../../docs/mesh-studio/V5_11_STATIC_SINGLE_PORT_REVIEW_PROTOCOL_20261123.md): **[CI 3/3 aprovado](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45165895108)**, 36 controles Python + 4 testes de navegador em **cada OS**, e **terceira auditoria independente com sete arquivos compilados absolutamente idênticos entre plataformas**, SHA256 do inventário `ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5`. O Vite `5173` continua reservado para os scripts **legados de desenvolvimento** e **não deve estar ativo** ao executar este modo compilado. A validação humana em máquinas físicas e a revisão de licenças continuam pendentes; R2.8 científica continua bloqueada.


## V5.10 — inicialização local protegida e revisão independente

O `local_launcher` agora oferece uma variante da API protegida por Host e Origin exatos (`127.0.0.1:8765`), com Vite restrito a `127.0.0.1:5173` e oito testes HTTP hostis contra ambos os serviços. A [V5.10 foi validada no Linux e no Windows](../../docs/mesh-studio/V5_10_LOCAL_SECURITY_AND_PHYSICAL_REVIEW_PROTOCOL_20261123.md): 24 testes Python + 2 testes de navegador por sistema e os oito bloqueios HTTP observados. **Execute pelo launcher**, não exponha `web_api:app` diretamente como serviço protegido e não use `localhost:5173` como endereço alternativo. O sistema continua em modo Vite de desenvolvimento, sem autenticação de produção.

Para a **avaliação independente em equipamento físico**, siga o protocolo V5.10: extraia o corpus original C++ da pasta privada de experimentos do Doutorado, execute `python3.13 -m tools.mesh_studio.v59_reviewer preflight`, `local_launcher setup`, instale o Chromium do Playwright e execute `v59_reviewer smoke`. No Windows PowerShell use `py -3.13`. A revisão por pessoas em máquinas físicas permanece **não realizada**, mesmo após o CI 2/2 aprovado. R2.8 científica segue bloqueada.

## V5.9 — reproducible full original-native source reviewer on V5.8 launcher

In addition to the lean research startup, V5.9 validates a finite **real original C++ accepted Eistute/Book step-1** browser task: original NDJSON/SVG/manifest source-SHA re-audit, original P1 linked XYZ/UV quality and source face, Book/Eistute source patch/triangle/native node and curve sampling, original vector SVG downloads, staged/nonaccepted guardrails and negative forged LOD/UV. **Both Ubuntu and Windows CI PASS**, including cross-platform canonical source SVG bytes and clean server shutdown. Use the pinned ten-file source corpus and the `python3.13 -m tools.mesh_studio.v59_reviewer preflight` / `smoke` commands described in [V5.9 research review protocol](../../docs/mesh-studio/V5_9_ORIGINAL_NATIVE_LOCAL_REVIEWER_RESULTS_20261123.md). This does not recompile native C++ or authorize physical machine GPU/LOD claims.


## V5.8 — inicialização segura do STUDIO de pesquisa

O novo launcher local, auditado em Linux/Windows, executa a interface React/vtk.js e a API FastAPI com um ambiente Python **mínimo de 13 pacotes**, derivado dos locks com hashes; **PyMuPDF e VTK não são instalados no ambiente local da API**. A aplicação permanece em desenvolvimento, com portas estritamente `127.0.0.1`, e o gerador científico C++ não é executado pelo launcher.

A partir da raiz do repositório, com Python 3.13, Node 22 e npm 10:

```bash
python3.13 -m tools.mesh_studio.local_launcher preflight
python3.13 -m tools.mesh_studio.local_launcher setup
python3.13 -m tools.mesh_studio.local_launcher serve
```

No Windows PowerShell, troque `python3.13` por `py -3.13`. Para verificar e encerrar ambos os serviços automaticamente, use `smoke` no lugar de `serve`. Abra `http://127.0.0.1:5173`. [Evidências, escopo e riscos da V5.8](../../docs/mesh-studio/V5_8_MINIMAL_LOCAL_LAUNCH_AND_SOURCE_LOCK_RESULTS_20261123.md). **Não é distribuição de produção, lançamento oficial nem evidência de LOD.**


**Current project roadmap and 2026-11-20 wide audit:** [Mesh Studio Master Plan V5](../../docs/mesh-studio/MASTER_PLAN_V5_AUDIT_AND_RECOVERY_20261120.md), with the [current evidence/qualification index](../../docs/mesh-studio/README.md). Previous planning and research documents are retained as dated historical evidence.

The Studio Python/Web modules live under `tools/mesh_studio/`. The isolated research PR #239 also includes **default-OFF, compile-time guarded observation changes in original C++ source files** and separate serial research executables; these do not authorize production numerical-policy changes, public releases or merges. Do not claim that the complete Studio PR has zero edits outside this Python directory.

## Initial research-safe deliverables

- Synthetic immutable V1 fixture corpus and standalone oracle in `fixtures/`.
- Scientific typed `MeshDocument` with source vertices, typed TRI/QUAD faces, per-corner UV and explicit patch/source provenance.
- Bounded Wavefront OBJ importer with distinct legacy APMesh counting dialect and synthetic JSON sidecars.
- Headless vector-only SVG figure generation using actual source UV coordinates. An SVG with raster data or active content fails audit.
- Regression against 10 known-valid and 6 deliberate-invalid synthetic cases, parser mutations and figure deterministic reproduction.

```sh
python tools/mesh_studio/fixtures/generate.py
python tools/mesh_studio/fixtures/validate.py
python -m unittest tools.mesh_studio.test_studio -v
python -m tools.mesh_studio.cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --svg build/mesh-studio/synthetic_hybrid_uv.svg
```

All generated synthetic results must remain explicitly labeled **SYNTHETIC**, not reported as output from the actual APMesh generator. The original source `P1` model, real all-quad algorithm, anisotropic generator, vector PDF, GUI and scientific multi-epoch comparison are *not* claimed by this S0/S1 starter.

A generic OBJ lacking UV is parsed for geometry, but is not silently projected to fake UV coordinates. The importer does not infer source curve topology or model-global welding from coincident XYZ positions.

## S1b: reproducible synthetic technique storyboards

The three new storyboards are **synthetic instructional scenes**, not a capture
of generator execution, nor results measured in the paper. They are standalone
SVG path/polygon/ellipse vector drawings and require no Qt/VTK/GPU:

```bash
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards -v
python -m tools.mesh_studio.fixtures.validate
python -m tools.mesh_studio.storyboard_cli all --output-dir figures/mesh_studio
```

The command generates:

- `hybrid_synthetic.svg`: six illustrated stages of the existing 1-QUAD/8-TRI fixture, including a separate biquadratic *synthetic* lift in the last panel; the quadtree and front stages are **simulated** rather than recorded AFT operations.
- `all_quad_synthetic.svg`: actual 2x2 quad-grid boundary incidence (8 boundary edges) compared with a **fixed** five-edge disk where conforming all-quad is impossible under stated assumptions; necessary, not sufficient, existence criterion.
- `anisotropy_synthetic.svg`: exact unit ellipses for the prescribed synthetic metrics `I` and `diag(16,1)`; no APMesh anisotropic adapter is claimed.

Each `.svg` has an adjacent `.audit.json` with SHA-256, panel count, provenance
and the mathematical control data. SVG passes the existing raster/active-content
check, but **no PDF/PGF/LaTeX export has been qualified**. PNG files included
with the release example are previews, not the publication originals.

The metric example uses `Metric2D` defined in `metric2d.py`; original field
frame, units, tensor source and rotation must be supplied when real APMesh
measurements eventually become available. Local geometry is not a proof of
continuous physical Jacobian validity. All-quad and tensor-driven adaptation
remain scientific development goals, not released generator modes.

## S2: independently testable physical/UV quality and indexed topology

No Qt, VTK, NumPy or GPU is needed to analyze the initial fixture corpus.
The analysis API never silently converts a QUAD into TRI elements in the
canonical mesh. For a nonplanar QUAD its reported area is explicitly the sum
of the two discrete facets along diagonal `(0, 2)`, **not** the original
curved surface area. A planar Jacobian score is `null` for nonplanar cells.

```bash
python -m unittest \
  tools.mesh_studio.test_studio \
  tools.mesh_studio.test_storyboards \
  tools.mesh_studio.test_quality_analysis -v
python -m tools.mesh_studio.analyze_cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --output build/mesh-studio/synthetic_hybrid_quality.json \
  --metric-diagonal 16 1
```

`quality_analysis.analyze_mesh()` reports normalized triangle mean-ratio
(shape only), physical facet area, planar-QUAD minimum scaled Jacobian,
relative coplanarity, indexed topology and separate distributions. The
historical article's triangle quality score is **not automatically equal**
to the independently defined mean ratio here. No common TRI+QUAD quality
average is produced.

An optional `source_normal(u,v)` callback audits physical facet orientation
only at the two facet centroids of a QUAD; it does not prove global
orientation of a Bezier surface. The callback and optional 2D SPD field are
caller-supplied, not authenticated measurements of the generator. An
anisotropic field must explicitly declare `metric_frame='uv'`, and the
example CLI metric is labeled USER_SUPPLIED_NOT_ORIGINAL_GENERATOR_FIELD.

OBJ groups are **not necessarily patch IDs**. In the controlled P1 export,
`QUAD` and `TRI_AFT` classify cells of the same source patch. The topology
report therefore contains group-local connectivity and an additional joined
**indexed** face-complex assessment when no patch-owner sidecar exists.
Neither indexed joining nor coincident XYZ values authorize welding of
nonmanifold source sheets. Synthetic multi-patch examples use validated
sidecar ownership to prevent accidental global identity inference.

The report is suitable for measurement and diagnostic presentation, not yet
scientific certification. Vector figure generation remains S1/S1b. Source
P1 integration, actual recorded adaptive epochs, all-quad execution,
tensor-driven generation, PDF/PGF publishing and desktop GUI remain open.


## S3: controlled real P1 source integration (not a synthetic fixture)

The exact PR #217 `accepted.obj` from the successful Linux/Windows source CI is
checked into `fixtures/real_p1/`. The original OBJ has 69 physical nodes, 42
interior QUAD and 36 native original AFT TRI; the 16-edge outer boundary and
20-edge QUAD/TRI interface are independently audited. Its original SHA-256 is
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

Run the source control-net oracle, geometry, connectivity, quality and **real**
UV publication figure from the repository root:

```bash
python -m tools.mesh_studio.real_p1_cli --output-dir /tmp/apmesh-real-p1-figure
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards tools.mesh_studio.test_quality_analysis tools.mesh_studio.test_real_p1 -v
```

The output is a true-vector UV SVG, a repeatable JSON scientific audit and a
SHA-256 manifest. It is **not** a 3D shaded vector export, continuous Jacobian
certificate, accepted hybrid adaptive history, global non-manifold welded mesh,
all-quad result or anisotropic method output. The TRI and QUAD groups classify
**element types**, not two different physical source patches.


## S4: optional physical XYZ / source UV desktop viewer

The **headless** `scene_model.py` preserves original source IDs, separate TRI/QUAD
faces, per-corner UV and camera/visibility recipes pinned to the input OBJ SHA.
`scene_vtk.py` and `render3d_cli.py` provide native VTK 3D previews **as raster
PNGs**, with audit JSON. Do not label these screenshots vector figures.

```sh
python -m unittest tools.mesh_studio.test_desktop_stage -v
python -m tools.mesh_studio.render3d_cli \
  tools/mesh_studio/fixtures/real_p1/accepted.obj \
  --png build/mesh-studio/p1_real_xyz.png
```

The optional GUI source is available in `desktop_app.py` (PySide6 + PyVistaQt),
with 3D/UV linked face IDs, TRI/QUAD toggles, camera recipes and interactive
cell inspection. Install only after resolving and validating exact Qt/VTK
version constraints on the target host:

```sh
python -m pip install -r tools/mesh_studio/requirements-desktop.in
python -m tools.mesh_studio.desktop_app --obj tools/mesh_studio/fixtures/real_p1/accepted.obj
```

**Qualification limit:** Native VTK EGL rendered successfully and all S4 headless
tests passed. A PySide6/PyVista/pyvistaqt desktop run was NOT executable in this
environment, so interactive cell picking, Qt ABI and close/reopen memory behavior
are UNQUALIFIED until an actual GUI smoke run. See
`docs/mesh-studio/IMPLEMENTATION_S4_20261114.md`.

## S4b: bounded Qt GUI qualification gate (not passed without Qt)

S4a remains verified by VTK headless rendering and scene-model regression.
The **actual** PySide6/PyVista/PyVistaQt window is a separate, pending gate.
The automated S4b smoke below opens two Qt-backed VTK panes, toggles the source
face layers, selects an indexed face via Qt and the VTK cell-data callback,
preserves camera recipes, renders a screenshot, then closes the widgets.
It does **not** claim to calibrate a physical mouse click, or provide an
independent repeat-open/close Windows GPU endurance qualification.

```bash
python -m pip install -r tools/mesh_studio/requirements-desktop.in
# Linux with Xvfb/GLX availability:
xvfb-run -a python -m tools.mesh_studio.desktop_app \
  --obj tools/mesh_studio/fixtures/real_p1/accepted.obj \
  --smoke-output build/mesh-studio/qt-smoke.json
```

On Windows, invoke the same Python command in a regular desktop session without
`xvfb-run`. A PASS receipt is emitted **only after** real PySide6 and both VTK
widgets execute; missing dependencies return exit code 2, with no false PASS.
The programmatic pick callback is distinct from real physical mouse selection,
which still requires a separate interactive acceptance test.

## S5 pilot: publication-grade vector figure and experiment registry

Install the optional publication dependencies independently of the GUI:

```bash
python -m pip install -r tools/mesh_studio/requirements-publishing.in
python -m tools.mesh_studio.publish_cli --output-dir build/mesh-studio/paper-figure
python -m unittest tools.mesh_studio.test_publication -v
```

The source-bound command uses the **real PR #217 controlled P1** OBJ and its
verified generator receipt. It produces a journal-width (178 x 108 mm) PDF,
SVG, LaTeX `figure*` insertion snippet, CSV of 36 source TRI Studio-computed
mean-ratio scores, a replayable JSON recipe, a PDF/SVG structural audit and an
explicit six-cell topology x sizing comparison registry.

No qualified tensor-driven or all-QUAD results exist yet. The real fixed16
P1 source is deliberately **outside** the isotropic/anisotropic factorial
comparison, rather than being misrepresented as isotropic adaptation.
Nonplanar original Bézier QUAD cells are not given a planar scaled-Jacobian
score; the source's continuous surface validity is still not certified.

The SVG/PDF output is vector-only, not a three-dimensional shaded render.
Verification checks PDF image XObjects and inline images, SVG `<image>`/script
and remote asset references, actual physical paper size and embedded PDF fonts.
The PDF and SVG remain byte-for-byte reproducible in the qualified local
Python/Matplotlib environment, but release builds must pin their own tested
dependency versions. The LaTeX smoke uses `pdflatex` when available.

## S5b: source-safe multi-model mock figures and experiment histories

S5b adds **two reproducible true-vector figures** for researching figure
composition before comparable real QUAD/TRI, all-QUAD and anisotropic method
outputs exist:

```bash
python -m tools.mesh_studio.compare_cli --output-dir build/mesh-studio/s5b_mock_comparison
python -m unittest tools.mesh_studio.test_multi_model_publication -v
```

- `topology_gallery.{pdf,svg}` uses **three distinct synthetic** square-domain
  OBJ fixtures (8 TRI, 8 TRI + 1 QUAD, 4 QUAD) and independent per-panel
  plot extents. It does **not** imply matched geometry, element budgets or
  actually executed source algorithms.
- `epoch_timeline.{pdf,svg}` imports the eight explicitly invented history
  rows, traces **accepted states only**, and shows rejected candidates as X
  markers. Invented time/error values are not numerical research findings.
- `study_matrix.json` keeps all six topology × sizing scientific comparison
  cells `NOT_AVAILABLE`. The authentic one-shot P1 is separately recognized
  outside these adaptive-study cells, after exact control-net/receipt checks.
- `include.tex` embeds both vector figures in two-column LaTeX; `*.recipe.json`
  and `*.audit.json`, CSV tables and SHA-256 provenance enable repeated export.

The S5b CSV reader deliberately **rejects real-claiming rows** because the V1
synthetic history format lacks a source model digest, metric definition and
software/environment identity. Later real experiments require a separate
versioned, provenance-checked schema. Never edit these fixtures to make actual
comparisons look available.

Desktop S4b remains **not qualified**: source-preserving Qt interaction needs
actual PySide6/PyVistaQt installation and Windows/Linux smoke runs. The
headless S5b tooling does not change this pending status.

## S5c: versioned, source-bound experiment ingestion

S5c introduces a separate, strict, standard-library scientific experiment
manifest (`experiment_run.v1`), with an optional published JSON Schema for
interop. The loader resolves **only** hash-bound, bounded files below the
specified repository root. Schema validity does **not** qualify scientific
measurements. A real source claim is only independently qualified when a
matching dedicated oracle is available.

```bash
python -m tools.mesh_studio.experiment_cli \
  tools/mesh_studio/fixtures/experiments/real_p1_pr217.json \
  --output-dir build/mesh-studio/s5c_real_p1

python -m unittest tools.mesh_studio.test_experiment_ingest -v
```

P1 original source verification requires its exact CI artifact geometry hash,
original generator report hash, source and candidate revision, GitHub Actions
run/artifact IDs, original Bezier control-net oracle, 42 QUAD, 36 native AFT TRI,
69 nodes and 16 outer edges. Three explicitly defined, Studio-recomputed
metrics are checked against declared values and stable equation identifiers.
There is **no** source-proven timing, all-QUAD technique, tensor adaptation,
model-source file hash, or accepted adaptive epoch in this P1 record.

The importer therefore emits `REAL_P1_GEOMETRY_AND_SPECIFIED_METRICS_VERIFIED`
and a six-cell `NOT_AVAILABLE` comparative study matrix; P1 remains an excluded
controlled run because its policy is **fixed16/vertex_mean**, rather than
isotropic or anisotropic adaptation. Arbitrary new source runs may be ingested
as `SOURCE_PROVISIONAL_NOT_SCIENTIFICALLY_QUALIFIED`, never silently promoted by
self-declared metrics or CI names. An adaptive accepted epoch or anisotropic
source-metric claim requires a *new* independently reviewed oracle/trace
contract and is deliberately refused in S5c.

See `docs/mesh-studio/IMPLEMENTATION_S5C_20261114.md` for the source
limitations and negative-first research audit. The S4b interactive Qt smoke is
still pending; an exit code of 2 for unavailable PySide6/PyVistaQt is not a PASS.

## S5d: five real, source-qualified QUAD/TRI mesh candidates

This source-specific study imports five **real** OBJ artifacts from one
controlled Bezier source run (the fixed16 P1 control and four staged physical
candidate meshes), reconstructs the 64x64 identical-site source-geometry
residual and reports the two approved-for-diagnostics Pareto profiles.

```bash
python -m tools.mesh_studio.real_study_cli \
  --output-dir build/mesh-studio/real-candidate-study
python -m unittest tools.mesh_studio.test_real_candidate_study -v
```

The command generates a source-qualified JSON receipt, CSV source residual
measurements, true-vector scientific PDF/SVG figures and LaTeX include file.
It does not select a winner, adopt a candidate mesh, or assert accepted
adaptation history, all-QUAD generation, anisotropic adaptation, mesh-wide
nonmanifold welding or independent statistical repetitions.
See `fixtures/real_p2d1c3/README.md` and
`docs/mesh-studio/IMPLEMENTATION_S5D_20261115.md`. The controlled Qt desktop
smoke S4b remains unqualified until tested with actual PySide6/PyVistaQt.
