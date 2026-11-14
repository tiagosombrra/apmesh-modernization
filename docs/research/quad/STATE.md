# APMesh QUAD — current state

Updated2026-11-14 Fortaleza. Canonical branch: `quad-templates`.
Main remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

## Completed bounded repair

**P0 is integrated through [PR216](https://github.com/tiagosombrra/apmesh-modernization/pull/216)**,
research merge `49c9dc3be66dab2f4839e0ab661065a1ec5c5ba3`. Physical QUAD construction now refuses concave,
collinear, crossing and inverted UV cycles using all four existing-threshold
corner checks before observer publication. Original012/023 expressions, physical
metrics, production TRI, input and boundary policies remain unchanged.

- Unchanged original source fails the new concavity witness; failure retained.
- Linux GCC13.3, Windows GCC16.1 and MSVC19.44 Debug C++17 pass20accepted and
  40rejected cases each, with observer pointer/order/list-slot preservation.
- Exact candidate `a2c42776a16cc5e03d643ce916e5c6d81f0aa5dc` and exact research merge each pass85 CTest/527
  Python with no failures/errors/skips, including both original physical model
  modes, original fault slots and negative file mutations.
- Configured source/header/whole-probe analysis passes. Candidate push/PR and
  merge remote runs each complete four jobs successfully; fresh Eistute/Book
  frozen OBJ, acceptance and positive boundary comparisons pass.

[Delivery receipt](evidence/FOUR_CORNER_ADMISSION_DELIVERY_20261114.json) ·
[Repair/evidence](FOUR_CORNER_ADMISSION_20261114.md) ·
[Roadmap](IMPLEMENTATION_ROADMAP.md) · [Milestones](MILESTONE_STATUS.md) ·
[Protocol](CONTINUATION_PROTOCOL.md) · [Journal](SESSION_LOG.md).

## Controlled P1 integrated — mixed P2 prerequisites delivered, R3 still open

[PR217](https://github.com/tiagosombrra/apmesh-modernization/pull/217) is merged at `d39bbc447f88e179c3c4ee674bd9309f59c18eed`.
The real `ap_mesh --config` controlled case produces 42 physical QUADs,
36 original-AFT triangles, 69 owned nodes and 16 source boundary intervals on the original
curved ModelCurvaBezier. Independent Bezier UV/XYZ/winding/topology checks,
positive quality, stable identities and nonempty publication rollback pass.
Exact candidate 0999769 and exact merge each pass 86 CTest /527 Python.
Linux/Windows application checks and Linux frozen TRI equivalence pass.
Clang18 ASan/leak checks and a real UAF control pass in this bounded case.
See [evidence](evidence/P1_CONTROLLED_APPLICATION_20261114.json) and
[build/config instructions](../../../configs/quad/README.md).

Default builds retain TRI and QUAD refusal. This one-shot case requires
`AP_MESH_ENABLE_EXPERIMENTAL_QUAD=ON` plus the named fixed16/vertex_mean policy;
it does not run AdaptCurve or adaptive history. First failed CI admission for
two new config assets was preserved and corrected explicitly, without weakening
reference or scientific checks. Main and the unmerged larger PR214 are preserved.

**P2 functional target:** retain this typed hybrid SubMesh as actual history
for two different accepted adaptive epochs, including typed curvature,
quality, reconstruction, retry/rollback and export. P2a/P2b/P2c and
P2d-0/P2d-1a engineering prerequisites are now integrated; no actual
mixed adaptive epoch has yet been accepted.

## Mixed-history infrastructure — P2a/P2b/P2c integrated

[P2a PR218](https://github.com/tiagosombrra/apmesh-modernization/pull/218)
merged as \`d40114ed2dc9def294b382557a571e5b62285b83\`.
It qualifies a bounded typed physical SubMesh clone, partial-construction
fault rollback, Patch observer restoration and independent element/node
identities. Original PR synthetic-merge CI: 4/4 success, Linux ASan/UBSan/leak success,
85 baseline CTests and 527 tooling Python.

[P2b PR219](https://github.com/tiagosombrra/apmesh-modernization/pull/219)
merged as \`21ba08e55e014d5c9fa7533c9f7361ad4c98c7dc\`.
It qualifies a research-only polygon-aware 3/4-node vertex-link/topology
auditor and a *triangulated metric diagnostic*, cross-checked from original
OBJ via independent Python cosine-law/Heron calculations. Five malformed
cases are refused. The real 69-node controlled patch has 16 boundary and
53 interior vertices; its barycentric angle-defect witness sums to 2*pi.
Original PR synthetic-merge CI: four successful jobs including Linux sanitizers and unchanged
frozen TRI scientific parity. Neither contribution changes the original
triangle-specific \`Adjacent\`/\`CurvatureDiscrete\` path.

**CI provenance correction:** Previous P2a/P2b PR workflows used GitHub's
synthetic pull-request merge checkout and did not assert exact feature-head
identity. Their passing checks are valid for the corresponding tested trees,
not proof that the runner checked out their stated feature SHA. P2c changes
all three candidate checkouts and artifact names to the actual PR head SHA,
with an explicit clean-worktree identity check. Do not retroactively relabel
the prior candidate runs.

**P2c integrated** via [PR220](https://github.com/tiagosombrra/apmesh-modernization/pull/220),
merge `535acf7b3ba68dd1ee1267e682f2991a89214a87`. Its real controlled
physical QUAD corner-normal metric has minimum scaled Jacobian `0.567009347`,
minimum split-normal cosine `0.999145645` and maximum physical edge ratio
`3.309653057`, each independently checked against original Bernstein-control
Bezier derivatives. Four physical-negative cases are rejected. Exact feature
source `bd6135cd4c6ec30f4e3de3bf94593d106002c8b9` passed [CI
#43603290586](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43603290586):
4/4 jobs, Linux/Windows application, ASan/UBSan/leak, 85 root CTests,
527 Python tooling and original frozen Eistute/Book TRI equivalence. The
updated workflow now confirms actual feature-head source SHA at all candidate
checkouts and labels artifacts by that SHA. The output physical OBJ SHA-256
remains `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
See [P2c scope](P2C_TYPED_PHYSICAL_QUAD_QUALITY_20261114.md).
The previous two PR CI checkout identity limits remain documented above;
P2c rechecks their integrated code in the current exact feature tree.
**P2/R3 and M7 remain OPEN:** no two distinct adapted and accepted
QUAD/TRI mesh epochs, no production mixed curvature or rejection policy. The
[next constrained implementation issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
requires two real previous-state-driven accepted mixed epochs with independent
provenance, quality, rollback and default TRI equivalence.
Do not confuse P2a/P2b test passes with completed adaptive history.

## P2d-0 and P2d-1a integrated — no accepted adaptation epochs

[P2d-0 PR223](https://github.com/tiagosombrra/apmesh-modernization/pull/223)
merged at \`82522e0588a650b3c6421565883506a0f0cde831\`;
its exact feature source \`f1ea9332fa4d322f4578d3b6c46475776efa424f\`
passed [CI #43605731184](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43605731184):
4/4 jobs, Linux/Windows native, original frozen TRI, 85 root CTests
and 527 Python controls. The first run failed strict architecture
inventory after adding the native test; the retained CMake SHA-256 was
**corrected without relaxing the inventory test**, then all gates passed.
P2d-0 is a synthetic-only lineage metadata gate with fourteen negatives;
its fabricated three receipts must never count as adaptive epochs.

[P2d-1a PR226](https://github.com/tiagosombrra/apmesh-modernization/pull/226)
merged at \`c78a4445424d027d7a32a54e419fb129e3ef6622\`.
Exact feature \`530914390c44916067f258f18e2cba1cae61959f\`
passed [CI #43606747684](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43606747684):
4/4 jobs, 18 native QUAD CTests each Linux/Windows, genuine
\`ap_mesh\` application, Linux ASan/UBSan/leak, 85 root CTests,
527 tooling Python and frozen original TRI Eistute/Book parity.
The original physical OBJ remains byte-identical across both systems
(SHA-256 \`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0\`).

This **read-only source error indicator**, evaluated on real physical
nodes, QUAD bilinear sampling and AFT TRI barycentric sampling, reports
\`354\` samples: \`0.0026204483\` maximum interior QUAD error,
\`0.0463899583\` maximum exterior AFT TRI error and
\`0.0130653586\` global sampled RMS. The maximal QUAD is face4,
native source cell13 / leaf ordinal6 / depth2; the worst TRI/AFT
is face74 near UV (0.2,0.1). An independently computed
**UV-area** audit finds only \`25%\` QUAD coverage versus \`75%\`
TRI/AFT; approximately \`29.6%\` versus \`70.4%\` of the faceted
physical area. TRI/AFT contributes \`~99.53%\` of the *unweighted
sampled squared* residual and \`~99.84%\` of a supplementary
coarse physical-face-area-weighted sampled estimate. Neither
value is a certified surface error integral or general policy.

This imbalance is structural: \`CaptureLeafPolygons\` excludes all
quadtree leaves touching the source boundary. Refining only an
existing interior QUAD leaf cannot by itself enlarge the current
25% UV footprint. P2d-1b must compare **actual native tree/AFT
refinement** of (a) the maximal-error QUAD interior and (b) the source
leaf containing the maximal-error AFT triangle; evaluate both
source-surface error and QUAD area coverage without pretending that
more QUAD faces imply QUAD dominance. The initial fixed16 source
boundary still does **not** run \`Adapter::AdaptCurve\`.

**R3/M7 remains OPEN:** no second candidate tree has been changed
or accepted here (\`real_tree_edits=0 adaptive_epochs=0\`). No
general nonmanifold sheet welding, literal 1993 method, all-QUAD
or anisotropic acceptance is claimed. See [bounded evidence and
independent numerical caveats](evidence/P2D0_P2D1A_QUALIFICATION_20261114.json)
and the [canonical issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Explicit remaining limits and history

P0 closes one UV admission defect, not whole M4 or continuous physical Jacobian,
global topology, all-QUAD or production readiness. Broader native sanitizer/
allocation-denial/general-geometry coverage, historical1993 point/formula
approval, model-wide node ownership and high-valence sheet decisions remain open.
The prior interrupted544/922 build remains unqualified; fresh successful reports
above have their own exact identities. Stale R2c19/20 legacy evidence identities
remain explicitly historical rather than silently certified.

The former state is [preserved byte-for-byte](STATE_HISTORY_20261114.md), source
3809eb7 Git blob `bbc4260a41cd92e43ecc0451830e645f4bb9f883`.
The [audit](STATE_PLAN_AUDIT_20261113.md) and append-only journal retain failures
and scope corrections. This final checkpoint changes documentation/evidence
only; its own SHA is not a new scientific or complete-process qualification.
