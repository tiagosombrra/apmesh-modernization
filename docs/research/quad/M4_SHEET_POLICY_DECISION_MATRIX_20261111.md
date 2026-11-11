# M4 — Scientific decision matrix for real-model patch-sheet junctions

**Research note, 2026-11-11.** This file is **not a scientific approval**,
a topology implementation or a new physically joined QUAD/TRI mesh. It
summarizes the deterministic, source-linked evidence from [M4 physical
diagnostics](M4_EXTERNAL_BEZIER_PHYSICAL_DIAGNOSTICS_20261111.md) and
[the conservative incidence graph](M4_SHEET_INCIDENCE_GRAPH_20261111.md)
for advisor review. The [exact evidence](evidence/M4_SHEET_INCIDENCE_GRAPH_20261111.json)
and PR #210 CTest/JSON/DOT artifacts remain the reproducible controls.

## What the graph proves—and does not prove

Every physical curve ID originates from a production \`Geometry\` owned by
\`PatchReader::ReaderFilePatches\`. All five canonical seam sites per incident
patch are evaluated using the **actual** production \`PatchBezier\` surface.
Independent indexed Bezier controls and Bernstein derivatives, tangent
direction, UV boundary winding and patch-inward physical sector vectors
are audited. Two experimental interior-point choices yield the same curve
incidence classifications.

This is **sampled physical compatibility and source incidence**, not a
certificate of globally nonsingular parametrization, CAD sheet identity,
two-manifold topology, consistent global orientation, or conforming
finite-element mesh. A shared \`CurveAdaptive*\` does not imply its many
incident patches share the same \`NodeAdaptive*\`.

## Decision table

| Model | Source patches | Shared junction | Geometry-only candidate pairings | Quarantined high-valence combinations | Approval needed |
|---|---:|---|---|---:|---|
| Eistute | 4 | One curve incident to 4 patches | 0 (no degree-two curves) | 6 possible incident pairs | Decide whether the axis is a nonmanifold junction, disjoint sheets or explicitly paired continuations |
| Book | 28 | One 28-owner spine | 0 (no degree-two curves) | 378 possible incident pairs | Identify which pages/sheets, if any, are topologically joined; do not pair by proximity alone |
| Ribbed Bracket | 13 | Four 3-owner curves plus 17 degree-two curves | 17 ordinary two-owner candidates | 12 possible triple-incidence pairs | Review each ordinary pair and define the three-way wall/rib/topology semantics independently |

On Ribbed Bracket, the 17 eligible two-owner edges produce four
**candidate-only** components: ten patches \`[0,1,2,3,4,5,6,7,8,9]\` and
three individual patches \`[10]\`, \`[11]\`, \`[12]\`. The existence of
a component does **not** transfer ownership, weld nodes, or prove a
closed manifold. The pairwise physical inward sectors span approximately
90° at 14 ordinary shared curves and 180° at 3, as measured on the
original vertex-mean physical sample at the edge midpoint. The former
are geometric creases and the latter locally opposite sectors; a
sharp crease by itself is not a reason to discard a genuine sheet edge.

There are **396** quarantined unordered pairs across the high-valence
curves. They are **possible comparisons**, not 396 malformed edges or
396 rejected physical surfaces. The number of permissible global sheet
pairings cannot be inferred from this count.

## Required advisor decisions before any welding code

1. **Sheet semantics per curve, not a global rule.** For each high-valence
   curve, explicitly label each incident \`(patch_id, side)\` as belonging
   to an intended surface sheet; say whether continuity is a two-owner
   manifold edge, nonmanifold branching junction, physical intersection
   or coincident but distinct chart boundary. Avoid inferring identity
   solely from 3D coincidence.
2. **Orientation and physical normal policy.** Preserve both the
   source-controlled canonical curve parameter direction and the
   patch-boundary winding. Decide whether each approved patch pair needs
   an orientation reversal; check corresponding normals along the full
   shared curve, not just a midpoint. Eistute has strongly rotating
   patch normals, invalidating a universal positive-world-Z gate.
3. **Node ownership and edge subdivision.** Only after a versioned
   pairing decision should the research implementation derive canonical
   boundary node identity and consistent subdivision across both owner
   patches. At nonmanifold junctions, ownership may be shared by an
   explicitly approved set of more than two patches or kept split; the
   current one-to-two manifold pairing API is intentionally conservative
   and cannot decide this.
4. **Quality and rollback.** Independent QUAD and experimental M5 TRI
   polygons must be validated in XYZ for curvature-adapted refinement,
   edge conformity, positivity of relevant Jacobians, consistent
   winding, observer/owner lifetime and rollback on rejected attempts.
   Current 69-node per-patch physical candidates do **not** satisfy
   these model-wide proof obligations.
5. **Historical technique fidelity.** The 1993 paper's intended
   Delaunay insertion and contour contraction are not validated by
   the M5 local Lawson experiment. No centroid choice, combined
   historical algorithm or all-QUAD mode may be approved implicitly.

## Proposed versioned scientific decision input (NOT approved yet)

Once the advisors make specific choices, a dedicated *research-only*
configuration can record, for each source model:

\`\`\`json
{
  "schema": 1,
  "model_sha256": "<source-model-bytes-sha256>",
  "curve_id": 0,
  "incidences": [
    {"patch": 0, "side": 0, "sheet_id": "review-required"}
  ],
  "approved_pairings": [],
  "junction_kind": "UNDECIDED",
  "approval_status": "PENDING_ADVISOR_REVIEW"
}
\`\`\`

This is **illustrative schema**, not a real accepted mapping. The future
validator must reject missing/extra incidences, duplicate or overlapping
pairings, source SHA changes, incompatible orientation, C0 cracks,
unsynchronized UV seam nodes, ambiguous high valence, and any attempt
to weld without an explicitly approved versioned sheet decision. It
must not alter production TRI.

**Next scientific gate:** Prof. Joaquim Bento / Prof. Creto Vidal
review the source model semantics at the high-valence curves, starting
with the 4-owner Eistute junction, then the Book spine and Bracket
triple junctions. This review is distinct from proving a new QUAD/TRI
generator and from separately adapting Hermite \`ModelPneu\`/\`ModelNariz\`.
