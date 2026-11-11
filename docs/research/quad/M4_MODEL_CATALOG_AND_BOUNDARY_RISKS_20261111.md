# M4/M5 research model inventory and boundary-readiness audit — 2026-11-11

**Status: source inspection and a new automated admission gate, not hybrid
mesh generation.** The preceding PRs #204 and #205 demonstrated 42 native
C++ QUAD + 36 local-Lawson research TRI, mapped to one built-in curved
Bezier model, and 69 shared physical nodes owned by a SubMesh. The following
models are **not** yet qualified for physical hybrid generation.

## Models versioned as external `.bp` inputs

| Model | Source | Vertex records | Bezier patches | Once-incident control curves | Twice-incident control curves | Curves shared by >2 patches | Highest valence |
|---|---|---:|---:|---:|---:|---:|---:|
| Eistute | `input_models/eistute2.fixed.bp` | 64 | 4 | 12 | 0 | 1 | 4 |
| Book | `input_models/book_v7a.bp` | 340 | 28 | 84 | 0 | 1 | 28 |
| Ribbed Bracket | `input_models/ribbed_bracket_nm_decor.bp` | 125 | 13 | 6 | 17 | 4 | 3 |

All three files contain only the `v` and `p` control records apart from
blank lines and comments. Every `p` refers to 16 ordered control vertices.
The reader `PatchReader::ReaderFilePatches` already supports this file
format, interns coincident control points and reuses curves in the actual
production `Geometry`.

**High-valence boundaries are not automatically input errors.** Eistute
has an axial control curve incident to **four** different patches; Book
contains a common spine curve shared by **28** patches. This can represent
deliberate branching sheets. A general conforming manifold-edge welding
algorithm allowing only two owners **cannot silently merge these patches**.
Ribbed Bracket has a mixture of 17 ordinary paired curves and four
triple-incident curves. The research boundary adapter must retain per-sheet
incidence, explicitly select what is welded and preserve patch-local IDs.

## Differential inspection (candidate diagnostics, not approval)

An independent bicubic Bernstein derivative grid of **9x9 samples per
patch** finds no zero cross-derivative magnitude among the sampled points
in the three versioned models. In Eistute, however, the sampled surface
normal at some corners has a **negative dot product with the same patch's
center normal** in every one of the four patches (60 samples across all
patches). This can reflect a strongly curving surface; **it is not by
itself a proof of an inverted Jacobian**, since a 3D normal may rotate by
more than 90 degrees on an otherwise regular patch. It does disqualify an
unqualified global `normal.z > 0` or fixed center-normal sign test such
as the current bounded single-example research prototype.

Book and Ribbed Bracket have no such center-normal-opposition samples on
this particular 9x9 grid. A finite regularity sample **does not establish
a global Jacobian lower bound** or a conforming final mesh, especially at
high-valence or multipatch edges.

## Built-in C++ model constructors

The 14 `Models3d` factories in `src/input_output/models_3d.cpp` declare
**68 patch constructions: 45 Bezier and 23 Hermite**. These are statically
counted factory calls, not a runtime inventory of valid/connected surfaces.

| Built-in model | Bezier | Hermite | Next adapter |
|---|---:|---:|---|
| `ModelCurvaBezier` | 1 | 0 | Existing qualified M4 fixture |
| `ModelPlanBook` | 5 | 0 | Bezier multipatch |
| `ModelTresPatches` | 3 | 0 | Bezier multipatch |
| `ModelDoisPatchesPlanosCurva1` | 2 | 0 | Bezier shared boundaries |
| `ModelDoisPatchesPlanosCurva` | 2 | 0 | Bezier shared boundaries |
| `ModelUtahteapot` | 32 | 0 | Bezier 32-patch orientation and seams |
| `ModelParaboloide` | 0 | 1 | Hermite geometry adapter required |
| `ModelPneu` | 0 | 2 | Hermite two-patch geometry adapter |
| `ModelLadoDescendente` | 0 | 1 | Hermite geometry adapter |
| `ModelBaseCircular` | 0 | 1 | Hermite geometry adapter |
| `ModelBaseQuadrada` | 0 | 1 | Hermite geometry adapter |
| `ModelBordaCurva` | 0 | 1 | Hermite curved boundary adapter |
| `ModelDoisPatches` | 0 | 2 | Hermite shared boundary adapter |
| `ModelNariz` | 0 | 14 | Hermite multipatch |

No `ModelBolha` constructor or `input_models/bolha` asset appears in
the **currently tracked** branch. The user may have an untracked or other
repository version, but **no identity is inferred here**.

## New automated source-level gate

Run:

```bash
python3 tests/quad/audit_model_catalog.py \
  --root . --report build/local-serial/quad_model_catalog.json
```

The script enforces the current 3-input/45-patch and 14-constructor
45-Bezier/23-Hermite source census, inventories high-valence control
curves, samples 9x9 independent Bernstein cross derivatives, reports exact
source SHA-256, and rejects seven malformed `.bp` mutations. It does not
call a production generator or create a hybrid mesh. GitHub Actions retains
`quad-model-catalog-<SHA>` as a bounded JSON artifact.

## Sequence for actual model-wide QUAD/TRI research

1. **Model loading and per-patch geometry adapter:** use
   `PatchReader::ReaderFilePatches` for the three real `.bp` files and the
   `Models3d` factories for built-in fixtures. Keep `PatchBezier` and
   `PatchHermite` API implementations distinct while sharing a typed,
   serial evaluation contract. Start with a two-patch Bezier fixture,
   then the multi-patch external models.
2. **High-valence and per-sheet boundary reconciliation:** preserve each
   patch's control-curve orientation and determine whether coincident
   parametric boundary nodes are one topological junction or separate
   surface-sheet vertices. The Eistute axial seam, Book spine and Ribbed
   Bracket triple curves are mandatory adversarial examples.
3. **Physical orientation and numerical contracts:** validate local
   `Qu × Qv` rather than assuming world-space +Z or a globally fixed
   normal. Test boundary and interior Jacobians, folded/degenerate faces,
   topology, IDs, nonmanifold edge behavior and edge-curvature faceting.
4. **Prototype outputs:** first export per-patch mixed 3D OBJ with
   provenance. Only emit a **full-model** research OBJ after the complete
   boundary-incidence oracle passes. Cross-patch four-node ownership and
   rollback under rejected adaptation remain separate research gates.
5. **Scientific approval:** the M5 exterior remains experimental local
   Lawson flips, not the historical 1993 point insertion and contour
   contraction. Centroid alternatives remain unapproved. No default TRI,
   all-QUAD, imported production CAD or production adaptation is enabled.

This bounded audit should not be interpreted as homologation of any
Eistute/Book/Bracket, Hermite Pneu or Utah Teapot hybrid mesh.
