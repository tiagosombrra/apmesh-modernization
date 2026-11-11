# M4 — Sheet-aware patch/curve incidence graph, with no node welding

**11 November 2026. Status: new isolated research candidate, unqualified until
its exact-head CI and scientific review.**

## Goal and admitted evidence

The preceding M4 gate, PR #209, qualified read-only physical evaluation of all
45 real external Bezier patches (Eistute 4, Book 28, Ribbed Bracket 13) on two
experimental UV center rules. Their per-patch samples are from the real
production \`PatchReader::ReaderFilePatches\` and \`PatchBezier::Parameterize\`,
\`Qu\`, \`Qv\`, independently checked against bicubic Bernstein. This milestone
does **not** generate a conforming global mesh. It derives a **bipartite
incidence hypergraph**, not a fictitious ordinary graph edge for a 28-owner
curve.

- Patch nodes: stable source patch IDs \`patch:0...\`; incidence nodes:
  \`patch:<id>:side:<0..3>\`; physical curve hypernodes: existing production
  \`Geometry\`-owned \`curve_id\`, verified against independently canonicalized
  source \`.bp\` control nets.
- For each incidence preserve \`curve_reversed\`, patch boundary orientation
  relative to the canonical Bezier control direction, and **five ordered
  native UV sample IDs and physical XYZ values**.
- For each *measured pair* of incidents to the same production curve store
  maximum sampled XYZ gap, minimum aligned canonical tangent cosine,
  orientation signs and the angle between patch-inward physical sectors in
  the plane normal to the curve tangent at midspan.
- **Degree 1:** legitimate exterior boundary, not a welding candidate.
  **Degree 2:** geometrically plausible *review candidates* only if C0
  samples/tangents match, sectors are nondegenerate and noncoincident, and
  patch boundary orientation signs are opposite. Otherwise report the
  observed reason for blocking or manual orientation review.
  **Degree 3, 4, 28:** every pair is explicitly **QUARANTINED**. Even
  apparently coincident and tangent-compatible sectors are not paired.
- Candidate-only patch connected components are a **diagnostic**, not actual
  topological connected components, nor an instruction to weld.
- A fail-closed explicit selection API rejects high-valence, unknown,
  duplicated or unapproved incidences. It never creates physical
  \`NodeAdaptive\`, even when an external scientific approval flag is set.

## Numerical safety and independent controls

Sampled geometry is checked against the unchanged independent source
Bernstein basis; physical curves and their direction come from the
production C++ \`Geometry\` registry, *not* point-coordinate guesses.
The five samples and their UV order are exact source identities.
Diagnostic \`1e-7\` XYZ gap, \`1-1e-7\` tangent cosine, and \`1e-3\`
radian noncoincident sector thresholds are explicitly **not approved mesh
quality or welding tolerances**. Do not reuse to adopt nodes automatically.
The graph records ambiguous/degenerate/ill-oriented interfaces as such.

The new script consumes the **existing, tested** M4 physical-output
directory from CTest \`quad.m4.external_bezier_physical_diagnostics\`, instead
of launching another C++ mesh run. Its own root CTest explicitly declares
\`DEPENDS\` on that upstream test, and fails if evidence is absent. Tests
include nine admissibility/negative controls **per real model**, including
high-valence welding rejection, missing approval, fabricated IDs, physical
crack, inverted curve tangent, overlapping inward sector, same-direction
boundary orientation and a positive degree-two synthetic geometry that
**remains only a candidate**. Both unapproved centroid cases must yield
identical incidence classifications.

## Deliverables and review gate

The test writes six bounded JSON hypergraphs, six Graphviz DOT diagrams and a
central \`m4_sheet_incidence_manifest.json\`, stored as a 14-day GitHub
Actions artifact. Result counts and curve-degree distributions are checked
against the versioned 4/28/13 patch fixtures and independent source
incidence census. The diagrams are for topology review, **not** valid
exportable manifold meshes or welded finite elements.

Expected root suite expands from **84 to 85 CTest** with existing 527 Python
tooling tests, seven application CLI invalid-mode controls, 13 native QUAD
standalone checks each on Linux GCC and Windows MSVC, strict frozen TRI
Eistute/Book equivalence and feature/merge exact-head artifact provenance.
Do not record an unrun gate as successful. No original TRI/production source
is changed. The existing optional GDB backtrace may be recorded
\`NOT COLLECTED\` without changing CTest requirements.

## Scientific questions still requiring approval

The Eistute axial 4-way, Book spine 28-way and Ribbed Bracket triple-incident
curves need a *deliberate* distinction among sheet continuation, actual
intersection/junction and intentionally separate physical sheets. Geometric
C0/tangent/sector compatibility at finitely many samples **cannot decide
sheet topology**; graph visualization and automated suggestions do not
substitute the source model's semantic sheet IDs or an advisor-reviewed
construction. Patch-normal rotations do not imply Jacobian sign errors.
Only after an approved sheet topology can synchronized boundary node
ownership, hanging node prevention, rollback and physical element lifecycle
be implemented.

Hermite \`ModelPneu\` and \`ModelNariz\` remain separate typed-adapter work,
\`Bolha\` is unverified in tracked sources, the 1993 historical Delaunay
insertion/contour contraction and a selectable all-QUAD generator are
unimplemented. Do not touch modernization \`main\`.
