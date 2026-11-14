# APMesh QUAD — current state

Updated2026-11-14 Fortaleza. Canonical branch: `quad-templates`.
Main remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.


## P2d-1b3 integrated, P2d-1c0 second-source topology preflight active

[PR231](https://github.com/tiagosombrra/apmesh-modernization/pull/231)
merged into research `quad-templates` at
`4b7f485a0df2c5108dbd822f337d2e38bba2947a`.
Exact source `1efb13b6a6fb46fca77deba81aa405db5bff90d5`
passed [CI #43620929978](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43620929978)
**4/4 jobs**: exact-head Linux/Windows real physical app, Linux
ASan/UBSan/leak, 85/85 root CTest, 527/527 tooling Python and frozen
Eistute/Book production TRI scientific equality. Independent Python evaluates
both first original and staged physical AFT+QUAD candidate on the **same 4096
UV sites**, not the unequal 354/486 per-element samples: max XYZ
`0.06564122093 -> 0.05160741346`, uniform-UV RMS
`0.01729520385 -> 0.01251800084`, source-Jacobian-weighted RMS
`0.01598126566 -> 0.01181032464`. These are finite-grid diagnostics
on one original Bezier model, not a continuous bound or adaptive acceptance
policy. The candidate remains `staged_unaccepted` and
`adaptive_epochs=0`. Former draft
[PR230](https://github.com/tiagosombrra/apmesh-modernization/pull/230)
was **closed unmerged as superseded**: its positive-staging requirement is
included in PR231; the extra synthetic rejection-negative control was *not*
integrated or CI qualified and remains an optional independent safeguard.

**Integrated [P2d-1c0 PR232](https://github.com/tiagosombrra/apmesh-modernization/pull/232)**,
exact feature `e0621a9b8b2675c60ba5bfd3cd0dfe0e395b01af`,
merge `a03938627ab8bf2aeadc04d1c238c2eb693d651f`,
implements **source-grid-only** topology preflight for the next
actual staged candidate's maximum original AFT residual: face103,
UV near (0.8,0.1), distinct level-2 source coordinate (3,0).
Six local Python tests passed; the prior exact feature `7a42a496`
had 4/4 green CI but did **not execute** the new test file. The corrected
exact feature `e0621a9b` passed
[CI #43624052194](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43624052194)
**4/4 jobs**, explicitly executing the six independent tests in actual
Linux/Windows/ASan controlled application, 85/85 root CTests,
527/527 Python tooling and frozen original Eistute/Book TRI parity.
[Source-bound receipt](evidence/P2D1C0_SECOND_BAND_DYADIC_PREFLIGHT_20261114.json).
Source-only predicted topology does **not** count as actual native QUAD output.
With the prior 28-leaf/21-of-64 eligible grid, the selected cell alone
predicts 31 leaves/22-of-64 QUAD UV but is correctly **rejected as a
disconnected, diagonal-vertex island**. Two bridge alternatives
(3,0)+(2,0) or (3,0)+(3,1) predict connected 34 leaves/24-of-64;
both bridges predict 37 leaves/26-of-64. These are **necessary dyadic
topology estimates, not actual original C++ Quadtree or native AFT execution**.
[Bounded protocol on draft PR232](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/p2d1c0-second-error-band-dyadic-preflight-20261114/docs/research/quad/P2D1C0_SECOND_BOUNDARY_BAND_PREFLIGHT_20261114.md), not yet on canonical.

**Native implementation proposal [PR233](https://github.com/tiagosombrra/apmesh-modernization/pull/233)**,
head `7b536dc901cae1e8b9410f6fbd9f3540c20dba09`, is
**draft; candidate exact-source CI #43624756858 has Linux/Windows/ASan
success but baseline root job pending**. The first exact-source CI
#43624612764 **failed real C++ compilation** on non-const `Vertex::getX/getY`
accessors; a narrow typed-pointer fix is retained and independently retested. It takes the actual new
physical AFT source residual, reconstructs the real previous 28-leaf native
Quadtree before each trial, and attempts original native
`subdivideToLevel`, `refineAccordingToNeighbors`,
`CaptureLeafPolygons` and `EmitLeafQuads` for corner-only, west,
north and both bridge alternatives. Its real C++ records are independently
cross-checked by the P2d-1c0 dyadic Python oracle and the six negatives.
Actual native Quadtree trials on the previous first 28-leaf tree returned
isolated corner **31 leaves / 0 QUAD (rejected)**; west **34 leaves / 75 QUAD**,
north **34 leaves / 71 QUAD**, and both **37 leaves / 82 QUAD**,
with UV area respectively `0.34375`, `0.375`, `0.375`, `0.40625`.
Identical source-native results on Linux/Windows/ASan, not merely
the previous dyadic predictions. No new physical second AFT reconstruction
or accepted epoch is implemented.

**Next native gate P2d-1c1:** propagate the *current previous physical
candidate* and source-error-selected site to the real native Quadtree,
trial both minimal bridge directions and the three-cell band with original
2:1 balancing and native `EmitLeafQuads`/AFT physical reconstruction.
Independent common-site source error, QUAD Jacobian, warpage, cost,
observer/owner rollback, immutable source/OBJ identities and scientifically
pre-registered acceptance criteria are mandatory. Do not count a source-only
preflight, original fixed16 proposal, or staged physical output as an
accepted mixed history epoch. R3/M7 [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
**OPEN (zero accepted adaptive QUAD/TRI epochs)**; no global Eistute/Book
high-valence weld, 1993 historical reconstruction, all-QUAD or anisotropy
claim. `main` and default TRI remain unchanged.


## P2d-1b2 physically reconstructed — qualified feature CI, adaptive history still OPEN

Research-only full original native AFT physical reconstruction from the real three-leaf
error-selected connected band was merged through [PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229),
research merge `289b6be6e97f787b53471255f9d30fbf3777fbba`.
Exact feature `bada655ae68a635f4b9664a05b2ab261d2d8d94c` passed
[CI #43619762822](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43619762822),
**4/4 jobs**: Linux GCC and Windows MSVC native/real physical application,
Linux ASan/UBSan/leak application, 85/85 root CTests, 527/527 Python controls,
and frozen original Eistute/Book TRI parity. A separate exact-merge CI was not
verified at this checkpoint.

For the original curved Bezier fixed16/vertex-mean source, baseline **69 nodes /
42 QUAD / 36 AFT TRI** and the new staged, **unaccepted** physical candidate
**93 nodes / 62 QUAD / 44 original AFT TRI** both retain 16 original source
boundary edges. Independently audited source UV coverage grew from **25%** to
**32.8125%**; sampled source maximum is **0.0463899583 -> 0.0367706982**.
Sampled RMS is **0.0130653586 -> 0.0078639324**, but comparison uses
**354 vs 486 different sampled sites**, so this is NOT a same-sample convergence
proof. Candidate OBJ SHA-256 is
`76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`;
original OBJ remains
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
[Bounded exact-source receipt](evidence/P2D1B2_REAL_PHYSICAL_CANDIDATE_20261114.json).

**Active next gate (same P2d/R3 milestone):** independent hardening
[PR230](https://github.com/tiagosombrra/apmesh-modernization/pull/230) is a
single-file draft Python negative/positive gate on source `71dde5d2a443b48a8e4a9a84dca07f5d7bb64901`.
It requires real emission (not rejection-only success), the observed typed
93/62/44 topology, a bounded source-specific maximum residual witness, and
an adversarial synthetic rejection. **PR230 has not been CI-qualified or merged.**
Next, qualify/integrate its exact candidate before a distinct independent
common-UV-sample error comparison, complete accepted-owner fault transaction,
scientific quality/error/complexity policy and **two genuinely previous-state-driven
accepted mixed adaptive epochs**. `adaptive_epochs=0`; issue
[#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
remains OPEN. Original fixed16 is not production `AdaptCurve`; no high-valence
model-wide welding, all-QUAD, anisotropy or 1993 method claim. `main` and
original production TRI remain unchanged.

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
merged at `82522e0588a650b3c6421565883506a0f0cde831`;
its exact feature source `f1ea9332fa4d322f4578d3b6c46475776efa424f`
passed [CI #43605731184](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43605731184):
4/4 jobs, Linux/Windows native, original frozen TRI, 85 root CTests
and 527 Python controls. The first run failed strict architecture
inventory after adding the native test; the retained CMake SHA-256 was
**corrected without relaxing the inventory test**, then all gates passed.
P2d-0 is a synthetic-only lineage metadata gate with fourteen negatives;
its fabricated three receipts must never count as adaptive epochs.

[P2d-1a PR226](https://github.com/tiagosombrra/apmesh-modernization/pull/226)
merged at `c78a4445424d027d7a32a54e419fb129e3ef6622`.
Exact feature `530914390c44916067f258f18e2cba1cae61959f`
passed [CI #43606747684](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43606747684):
4/4 jobs, 18 native QUAD CTests each Linux/Windows, genuine
`ap_mesh` application, Linux ASan/UBSan/leak, 85 root CTests,
527 tooling Python and frozen original TRI Eistute/Book parity.
The original physical OBJ remains byte-identical across both systems
(SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`).

This **read-only source error indicator**, evaluated on real physical
nodes, QUAD bilinear sampling and AFT TRI barycentric sampling, reports
`354` samples: `0.0026204483` maximum interior QUAD error,
`0.0463899583` maximum exterior AFT TRI error and
`0.0130653586` global sampled RMS. The maximal QUAD is face4,
native source cell13 / leaf ordinal6 / depth2; the worst TRI/AFT
is face74 near UV (0.2,0.1). An independently computed
**UV-area** audit finds only `25%` QUAD coverage versus `75%`
TRI/AFT; approximately `29.6%` versus `70.4%` of the faceted
physical area. TRI/AFT contributes `~99.53%` of the *unweighted
sampled squared* residual and `~99.84%` of a supplementary
coarse physical-face-area-weighted sampled estimate. Neither
value is a certified surface error integral or general policy.

This imbalance is structural: `CaptureLeafPolygons` excludes all
quadtree leaves touching the source boundary. Refining only an
existing interior QUAD leaf cannot by itself enlarge the current
25% UV footprint. P2d-1b must compare **actual native tree/AFT
refinement** of (a) the maximal-error QUAD interior and (b) the source
leaf containing the maximal-error AFT triangle; evaluate both
source-surface error and QUAD area coverage without pretending that
more QUAD faces imply QUAD dominance. The initial fixed16 source
boundary still does **not** run `Adapter::AdaptCurve`.

**R3/M7 remains OPEN:** no second candidate tree has been changed
or accepted here (`real_tree_edits=0 adaptive_epochs=0`). No
general nonmanifold sheet welding, literal 1993 method, all-QUAD
or anisotropic acceptance is claimed. See [bounded evidence and
independent numerical caveats](evidence/P2D0_P2D1A_QUALIFICATION_20261114.json)
and the [canonical issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## P2d-1b0 and P2d-1b1 integrated — connected native topology only

[P2d-1b0 PR227](https://github.com/tiagosombrra/apmesh-modernization/pull/227)
merged at `9259de230c3da24ffd4dbced65beae7375c3fc46`
after exact [CI #43609586259](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43609586259)
passed four jobs, Linux/Windows native tests, ASan/UBSan/leak,
85 root CTests, 527 tooling tests, and frozen original TRI.
The real Quadtree source cell #13 refinement makes a valid
54-QUAD UV region of unchanged 0.25 area; the higher-error
AFT source cell #6 refinement instead produces 0.265625
prospective area but is **rejected** as `Boundary vertex is not manifold`.
No invalid QUAD island is accepted or published.

[P2d-1b1 PR228](https://github.com/tiagosombrra/apmesh-modernization/pull/228)
merged at `092b9adfa0f9f03d4c28b5218759b7e89cf5b199`;
exact source `0c9bdc7f7562ce2c9633b4b44bb07fe7039b16a8`
passed [CI #43618564496](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43618564496)
4/4 jobs with Linux/Windows native and application, Linux
sanitizers, 85 CTests, 527 Python and strict frozen TRI parity.
A **three-leaf native source refinement band** (#6, #7, #9)
connects the previous isolated boundary child to the original
interior QUAD region: 19 to 28 actual native leaves, 62
**UV-only QUADs**, 0.328125 of the source UV area
(32.8125%, versus 25% initially). An independent exact
8-by-8 dyadic grid oracle verifies 21/64 eligible cells,
four-neighbor connectivity and absence of holes. The original
physical OBJ remains SHA-256
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`
on both platforms and the sanitizer run.

**Scientific limit:** no native AFT or physical SubMesh is
regenerated from the new band in these gates.
`actual_aft_retriangulations=0 adaptive_epochs=0` remains
mandatory. A new draft [P2d-1b2 PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229)
attempts physical reconstruction and must independently
classify any failed candidate; even a physically valid
candidate is not an accepted adaptive history epoch.
R3/M7 remains OPEN.

[Bounded original-topology receipt](evidence/P2D1B0_P2D1B1_NATIVE_TREE_BAND_20261114.json)
and [canonical issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

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
