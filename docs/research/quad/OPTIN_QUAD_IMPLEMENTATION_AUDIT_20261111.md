# APMesh QUAD — correction-of-course implementation audit

**Date (UTC):** 2026-11-11  
**Evidence class:** Remote source-code and qualified CI review. **No new native test
execution or compiler qualification was performed in this audit session.**  
**Read revision:** research `quad-templates=103bc0282d9d3ca566dcbdf830065459f558a4bf`; preserved modernization
`main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. No open PRs at review.
**Last qualifying source gate:** [PR #210 postmerge](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43057855090),
source `afa15277aef35aa5beae9a980b11e66a74c8dba3`, **4/4 jobs, 85/85
CTest, 527/527 tooling Python**, QUAD native GCC/Linux and MSVC/Windows, frozen
Eistute/Book TRI equivalence. The later commits were documentation/checkpoints.

## 1. The corrected functional contract

User-confirmed goal: **opt-in replacement of existing *triangular*
quadtree-cell template elements by the corresponding *quadrilateral*
template elements in the *interior* of each patch**. Do not replace,
rediscretize or reinterpret the established input-curve, patch-boundary
or adaptation logic. Use the existing APMesh Quadtree and boundary/AFT
pipeline; the exterior region may remain TRI (a **QUAD-dominant** hybrid).
Leave the normal/default TRI path scientifically and byte-for-byte intact.
The selector of element type is **orthogonal** to the existing
`USE_TEMPLATE=y/n` toggle. Do not advertise global all-QUAD or the
historical 1993 exact algorithm as implemented.

This is a *scope correction*, not authorization to change the historical
interior-point formula, frozen oracles, scientific tolerances, existing
curve sharing, element quality scoring or TRI adaptation in production.
An explicitly named research point rule may be evaluated only as a
provisional candidate; it is **not** an approved historical formula.

An independent completed experiment over per-patch UV data is not
equivalent to a live opt-in application-generated hybrid mesh.

## 2. Source-observed process and integration sites

The existing serial/adaptive production path is:

1. `PatchReader::ReaderFilePatches` and `Geometry::VerifyCurveGeometry`
   identify/control shared Bezier curves across patches.
2. `GeneratorAdaptive::GeneratorInitialMesh` establishes an **initial
   coarse four-TRI submesh per patch**; `initial_mesh.cpp` seeds curve
   samples once and reuses shared curve state, observing reversed sides.
   Hence the mnemonic **curves → boundary → interior** refers to the
   *subsequent adaptation* of the coarse mesh, not every initialization
   operation.
3. `GeneratorAdaptive::AdaptCurve` and `Adapter::AdaptCurveBySurfaceOmp`
   already manage curve samples/parameters and can inspect multiple
   incident patches. `ConfigureSharedCurveSynchronization` explicitly
   permits a separate disabled-sync mode that clones shared curves;
   **do not assume every configuration shares physical curve IDs**.
4. `Adapter::AdaptDomain` reads each patch's existing oriented
   `CurveAdaptive` sample sequence and builds the **boundary in UV**,
   preserving source `NodeAdaptive` IDs in submesh-owned copies.
5. `AdvancingFront::execute` runs `quadtree->generate`,
   `refineAccordingToNeighbors`, then, only when `TemplateMode()=="y"`,
   `quadtree->makeTemplateBasedMesh()`. It then runs
   `makeInitialFront`, geometry/topology-based advancing front,
   `fillMesh` and `improveMesh`.
6. `QuadtreeCell::makeTemplateBasedMesh` skips boundary leaves and
   invokes existing triangle `makeMeshType*` implementations in
   eligible interior leaves. `Quadtree::makeTemplateBasedMesh` creates
   shared outer vertices/edges and invokes that legacy TRI operation.
7. `Face` in `include/crab_mesh/aft/face.h` has exactly **three**
   vertex slots. `Adapter::AdaptDomain` casts the old submesh's
   `ElementAdaptive*` to `TriangleAdaptive*`, builds TRI `Face`
   history, and converts each generated `Face` back to a
   `TriangleAdaptive`. This is a **real representation and lifecycle
   boundary**, not simply a missing configuration switch.
8. `src/application/run_application.cpp` **intentionally rejects**
   `mesh_element_kind != "tri"` before `ApplyRuntimeConfig`.
   The existing CLI negative test
   `tests/quad/test_m3_dispatch.py` *expects* that denial for
   `MESH_ELEMENT_KIND=quad_uv` with both values of `USE_TEMPLATE`.

These observations demonstrate that the source TRI pipeline handles the
curve and AFT flow, but the **live opt-in QUAD replacement is absent**.

## 3. Inventory — preserve and reuse

| Area | Actual source/evidence | Measured state | Disposition |
| --- | --- | --- | --- |
| T1–T6 leaf incidence and rotations | `research/quad/quadtree_quad.{h,cpp}`, `tests/quad/leaf_contracts.cpp`, independent Figure 7 research audit | All six *proposed* graph classes, 16 masks and native tree probes covered; human/historical numerical approval still open | **KEEP**, validate against live refined-tree cases |
| UV QUAD topology and midpoint reuse | `research/quad/uv_mesh.{h,cpp}`, `tests/quad/uv_contracts.cpp` | Actual 4-corner QUAD values, edge midpoint deduplication, area/orientation/anti-hanging-node rejection, isolated disk validator | **KEEP**, extend to real partial interior components |
| Live tree snapshot | `CaptureLeafPolygons`, `EmitLeafQuads`, read-only adapter capture hooks | Reads production C++ tree and emits correct fixed small native fixture; **does not adopt faces/edges in AdvancingFront** | **INTEGRATE**, not just observe |
| Explicit point rule | `experimental_point_rule`, `tests/quad/test_m1_point_rule_quality.py` | Vertex mean and area centroid compared experimentally; historical selected formula not approved | **PENDING SCIENCE**, keep both tagged experimental |
| Four-node physical element | `research::QuadrilateralAdaptive`, ownership/observer negative tests in PR #205 | 4-node research element and per-patch physical witnesses qualified, no production mixed-element publication | **KEEP / ADAPT**, verify 3D surface semantics |
| Exterior hybrid prototype | `test_m5_exterior_interface.py`, `test_m5_constrained_delaunay.py` | 42 source QUAD + 36 **experimental** TRI per fixed 69-node UV pattern, 20 interface edges; TRI fan/Lawson is **not the existing production AFT** or proven 1993 boundary technique | **REPLACE WITH LIVE AFT INTEGRATION**, retain fixture only |
| Physical models | PR #209, 45 source-linked Bezier patches, 90 independent patch-local OBJ | Production `PatchReader` sampling/independent Bernstein parity; **no live curvature-driven hybrid adaptive mesh** | **USE AS VALIDATION FIXTURES** |
| Sheet incidence/valence graph | PR #210, 6 graphs / 27 controls / high-valence quarantine | Diagnostics only; 396 possible pairs identified as ambiguous, **not QUAD-interior blockers** | **RETAIN AS LATER GATE**, not critical path |
| QUAD application selection | `RuntimeConfig::mesh_element_kind`, `RunApplication` | `tri` accepted; `quad_uv` fails closed intentionally | **OPEN, top-priority user feature** |
| TRI engine | `QuadtreeCell::makeMeshType*`, `AdvancingFront`, `Adapter`, `GeneratorAdaptive` | Functional research baseline with strict frozen scientific oracles | **PRESERVE DEFAULT UNCHANGED** |

## 4. Critical defects in prioritization and technical gaps

**A1 — P0 — No usable QUAD switch.** The research CLI deliberately rejects
`quad_uv`; no normal application run emits the chosen QUAD templates.
The previous plan treated source-model valence decisions as the next
obstacle without having connected this opt-in functionality.

**A2 — P0 — QUAD geometry has no owned, live interior-front publication
path.** `EmitLeafQuads` only reads the refined tree and emits a separate
`UvMesh`. It does **not** replace `QuadtreeCell::makeTemplateBasedMesh`
outputs, publish the matching physical 4-node elements, or supply the
correct QUAD/AFT common front to the existing advancing front.
Appending its QUADs to an ordinary TRI result would **double-cover the
interior**, which is unacceptable.

**A3 — P0 — TRI-only face and adaptation contracts.** `Face` has
`Vertex* v[3]`, and `Adapter` reads/writes `TriangleAdaptive` by cast.
Some error, metric, smoothing, acceptance, serialization and retry paths
also assume triangular faces. Replacing a Triangle pointer with a
Quadrilateral pointer without an audited typed dispatcher is unsafe.
Do **not** simply reinterpret a four-node element as `Face`.

**A4 — P1 — Fixed synthetic exterior does not implement live boundary
transition.** The 42/36 fixture closes a unit-square example, not an
arbitrary patch boundary with production samples and 2:1 local tree
arrangement. The existing production AFT is the intended triangle
completion path and must consume the chosen QUAD interface exactly once.

**A5 — P1 — Source point/centroid decision is still unapproved.**
Independent candidate rules may be used behind an expressly experimental
name, with measured signed-UV/3D quality and fallback that *reports*
rejection, never silently changes a historical claim.

**A6 — P1 — Interior-disk validator is deliberately narrow.**
The standalone `UvMesh::Validate` requires a connected disk (Euler
condition, no holes); real tree interiors can be empty/disconnected or
form boundaries with more complex topology. The integration must
validate **each appropriate region, against its admitted topology**
rather than broadening the oracle by deleting checks.

**A7 — P1 — Live 2+ iteration adaptive contract absent for mixed
elements.** `Adapter::AdaptDomain` rebuilds prior TRI history and
`GeneratorAdaptive` error/curvature/adaptation code is TRI-oriented.
A first successful static QUAD export is not proof of repeatable
adaptive generation/rollback.

**A8 — P2 — Multipatch graph was promoted to a gate too early.**
High-valence surface incidence can be diagnostic independently of
interior QUAD templates. Existing curve identity, synchronization and
per-patch local boundary behavior should be reused. An explicit
advisor-approved sheet policy is needed **only if** the chosen feature
later changes node welding or promises particular *global manifold*
topology, not to run a QUAD interior template experiment.

**A9 — P2 — Documentation and test names can overstate milestone
readiness.** A passing root 85/85 CTest + 527 Python and 90 patch-local
OBJ witnesses prove the implemented research experiments on the
recorded SHA, **not** an application-accepted QUAD switch, live
arbitrary-boundary hybrid mesh or 1993 exact reproduction. Maintain
distinct gates for research implementation and end-to-end user feature.

## 5. Corrected engineering design — smallest compatible intervention

**Default path**: `MESH_ELEMENT_KIND=tri` (or option absent), unchanged
`USE_TEMPLATE`, `Quadtree` TRI `Face`, `AdvancingFront`,
`TriangleAdaptive`, frozen TRI scientific oracles, outputs and rejected
control cases. No implicit change to `USE_TEMPLATE`.

**Opt-in research path**: `MESH_ELEMENT_KIND=quad_uv` **only when
explicitly enabled with templates**, using a separately configured
and recorded experimental interior-point rule. `USE_TEMPLATE=n`
must have a specified, testable outcome (prefer explicit unsupported
rejection initially; do not produce silently TRI-only output under
an advertised QUAD selection).

1. Preserve `PatchReader`, curve sample and orientation registry,
   initial coarse TRI, `AdaptCurve`, and `Adapter` boundary creation
   on the given `(patch, step, retry)`. Keep default shared-curve
   synchronization behavior, and test the separately disabled variant.
2. After existing refinement and before template publication,
   dispatch **the same interior-leaf mask** either to historical
   `makeTemplateBasedMesh` TRI or research `CaptureLeafPolygons`
   + explicitly labeled QUAD point rule. Do not run both sets of
   interior template faces.
3. Implement an **owned, value-oriented mixed interior-result**
   (canonical UV node IDs, QUAD faces, physical mapping, QUAD/exterior
   interface segments and lifecycle). Seed the remaining TRI AFT
   *from this QUAD interface plus the existing patch boundary*,
   without losing edge orientation or introducing hanging nodes.
   Prototype an internal AFT integration seam rather than globally
   turning triangle `Face` into a four-node type.
4. Adapt `Adapter` to publish a `SubMesh` containing owned nodes
   and genuinely typed `QuadrilateralAdaptive` **alongside** legacy
   `TriangleAdaptive` for the remaining region, with no duplicate
   or discarded elements. Keep observer lifetime and exception/rollback
   contracts. Existing research four-node implementation is a starting
   point, not a production-qualified replacement.
5. Add a typed read path for mixed-element history, metrics and repeated
   adaptation. No `static_cast<TriangleAdaptive*>` on a QUAD.
   Consider separate QUAD behavior for normal/area/error/curvature
   and postprocessing, preserving TRI evaluation.
6. Export physical QUAD polygons with four actual vertex IDs, plus
   TRI at the exterior. Validate all patch and seam metrics against
   real `PatchBezier`, sample-based and more stringent physical
   Jacobian checks as appropriate; avoid claims of globally proven
   positivity from sparse samples.

This is intentionally **QUAD-dominant** and does not require all-QUAD,
new curve triangulation, globally manifold welding, Hermite adaptation,
anisotropic refinement, or a historically unverified implementation of
the 1993 Delaunay/contour contraction.

## 6. Reordered delivery gates (all measurable and fail-closed)

| Gate | Scope / actual user-visible criterion | Required checks |
| --- | --- | --- |
| **R0 — Contract/baseline** | Record default `tri` and `USE_TEMPLATE=y/n`; record explicit `quad_uv` behavior and point-rule provenance | exact-head frozen Eistute/Book TRI equivalence, CTest, Python, CLI positive and negative control baseline |
| **R1 — Native internal replacement** | Real Quadtree emits **QUAD instead of TRI** template interior for same tree, with declared metadata | all T1–T6, 16 split masks, 2:1, shared midpoints, no overlay, area + count, callback failures/rollback |
| **R2 — Live patch hybrid** | `ap_mesh --config` opt-in generates at least one **real 4-node QUAD**, preserves real curve/boundary samples and completes the rest using existing TRI AFT | real curved single patch, 2-patch reversed curve, exact gap closure, no T-junction, AFT front/ownership negatives, OBJ round-trip |
| **R3 — Repeated adaptation** | At least **2 iterations** and safe failed/rejected rerun with mixed-element history | actual `Adapter` / generator run, error/quality checks, previous accepted mesh unmodified, ownership and memory controls |
| **R4 — Full model trials** | Eistute, Book, Ribbed Bracket and valid tracked Bezier variants run using **same adaptive pipeline**; per-patch conformity proven, global semantics reported honestly | model source hashes, counted physical QUAD/TRI, boundary and shared-curve correspondence, orientation/quality/rejection logs; valence is a diagnostic |
| **R5 — Scientific fidelity** | Reconcile Figure 7/centroid and historical exterior against Bento 1993 with advisors | traceable 1993 oracle approval, model/algorithm ablations; distinct from usable opt-in R2 |
| **R6 — Advanced capabilities (optional)** | all-QUAD, anisotropic adaptation, rigorous globally manifold surface node welding, Hermite Pneu/Nariz | separate approval and research plan, never inferred from R2 |

Order R0 → R1 → R2 → R3 → R4 is the immediate user scope.
R5's paper-faithfulness must not be misrepresented or silently
satisfied by an experimental point formula. For an initial
**experimental-only** R2 proof of concept, a named unapproved
point rule is allowed with explicit provenance and closed acceptance;
an approved production/scientific implementation still requires R5.
The repository's previous M0–M9 history is retained unchanged.

## 7. First concrete code package and stop criteria

**Next feature PR (not implemented by this audit):**
`quad/integration-optin-interior-template-switch-<date>`.
Create a typed, research-only `InteriorTemplateResult` from the **same
live adapted/refined tree**, choose TRI/QUAD before template mutation,
keep a separate QUAD publication path with a UV interface/owner manifest,
and add a positive integration test proving actual **nonzero live QUAD
elements and zero overlapping legacy TRI template area**. Do not
make the CLI accept QUAD as “functional” until the first real
patch/AFT physical emission succeeds. Preserve fail-closed
`quad_uv` rejection until that gate closes.

Immediate negative tests: `quad_uv` without templates, missing point
rule, invalid/concave QUAD rule, selector mutation or callback exception,
exterior-only tree with zero interior, disconnected allowed interiors,
shared-edge orientation mismatch, attempted TRI+QUAD double publication,
and repeated-run stale mesh/curve state. Every rejection leaves
the previously accepted legacy generation path unchanged.

**STOP / do not merge:** fail or pending source CI, changes to frozen
TRI artifacts, silent area duplication, omitted contour segments,
hanging nodes, invalid 3D orientation, lifetime/rollback regression,
unjustified 1993 equivalence or unqualified live geometry tests.

## 8. Audit disposition

**Was the implementation “wrong”?** Its research kernels are not
proven wrong by this inspection. **The priority and acceptance gate
were misaligned** with the intended feature: substantial per-patch
physical and high-valence graph work was delivered without enabling
the essential opt-in **interior template replacement**. Preserve these
experiments as reusable validators, but take them **off the critical
path** unless an actual integration failure calls for them.

**Audit-only delivery:** This document and a sequencing correction to
the roadmap; no production C++, TRI template, scientific numerical
formula or test expectations changed. CI of the former source merge is
historical evidence, not a newly executed test on this documentation
revision. No local WSL, MSVC sanitizer, debugger or manual source
build is claimed.
