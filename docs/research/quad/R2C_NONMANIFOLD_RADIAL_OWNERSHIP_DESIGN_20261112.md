# R2c preflight — nonmanifold radial edge incidence and physical ownership

**Research design only (2026-11-12). NOT APPROVED, NOT IMPLEMENTED.**
This is the engineering follow-up to draft PR #214's original-source Bernstein
radial-sector audit. It does not permit merging that PR or publishing a model-wide
mixed QUAD/TRI mesh. The signed interval report and exact model source hashes
must be independently reviewed first. The original TRI generator remains the
default and `quad_uv` remains disabled.

## Grounded production ownership boundary

- `MeshAdaptive` owns a **vector of `unique_ptr<SubMesh>`**, and individual
  `SubMesh` objects associate with a `Patch*`; the source architecture is
  not one universal global `SubMesh` with all model elements.
- `SubMesh` owns a vector of `unique_ptr<NodeAdaptive>` and a separate
  vector of `unique_ptr<ElementAdaptive>`. Elements may observe local or
  separately live external nodes. Destruction and move assignment require
  elements to retire before their node owners.
- `Patch::SetSubMesh` and `SubMesh::SetPatch` are **distinct observer
  links**; preserving both on rejected candidates is a mandatory gate.
- `research::QuadrilateralAdaptive` is a typed four-node `ElementAdaptive`,
  not a three-slot original AFT `Face`. The production `Adapter` still
  assumes original TRI on some historical branches and must not silently cast
  experimental QUAD elements as `TriangleAdaptive`.

**Consequences:** Never publish one candidate `SubMesh` for all 4 Eistute
patches or 28 Book patches as if it were one production-owned chart. Candidate
per-patch `SubMesh` instances require a distinct, explicitly owned
model-wide seam-node identity/commit mechanism before any cross-patch
connectivity can be asserted. Arbitrarily making one patch's `SubMesh` own
all shared nodes and letting other patches borrow them creates unwanted
cross-`SubMesh` lifetime coupling and is not approved.

## Two separate graphs, not a conventional two-sided edge everywhere

1. **Source incidence hypergraph:** source model SHA, original
   `Geometry` curve index/identity, each incident `(patch_id, side)`,
   original parameter interval, reversed flag, canonical traversal and
   source node provenance. Never identify curves by coincident XYZ alone.
2. **Radial fan around each source interval:** a read-only cyclic sequence
   of each directed `(patch_id, side, local_segment)` incidence. The
   Bernstein sign witness can support preservation of the geometric
   cyclic sequence on a curve interval, but it cannot decide physical
   sheet continuation. Use `radial_next` only as an *ordered observation*,
   not as `halfedge.twin` or evidence of material continuity.
3. **Sheet policy:** an independent, **advisor-reviewed and
   model-source-SHA-bound** map describing which incidences belong to each
   intended sheet/junction and what kind of connectivity is approved.
   An unreviewed model has no approved `twin` or shared physical node
   ownership at high-valence curves.
4. **Per-chart QUAD/AFT seam:** the already studied oriented boundary
   between interior QUAD and exterior AFT TRI is different from
   inter-patch nonmanifold source-curve incidence. Do not conflate their
   edge or vertex identifiers.

A valence-4 or valence-28 curve cannot be represented correctly as a
single pair of manifold twins. Some independently approved configurations
may use no pairings at all, multiple explicitly classified continuations
or true branching radial junctions. The data structure must retain all
incidences and must not invent any pairing from proximity or radial rank.

## Proposed immutable decision record (schema concept, not accepted input)

```json
{
  "schema_version": 1,
  "model_sha256": "<exact tracked original .bp bytes>",
  "curve_index": 0,
  "source_epoch": "<same coherent generator epoch>",
  "junction_kind": "UNDECIDED",
  "approval_status": "PENDING_ADVISOR_REVIEW",
  "incidences": [
    {
      "patch_index": 0,
      "side": 3,
      "reversed": false,
      "sheet_id": null,
      "node_sharing_policy": "UNDECIDED"
    }
  ],
  "approved_continuations": [],
  "evidence": {
    "interval_proof_sha": "<verified PR commit>",
    "radial_cycle_sha256": "<canonical source-derived record>"
  }
}
```

This is NOT a real Eistute or Book mapping. Never substitute illustrative
patch IDs or fabricated hashes for actual model evidence. Any declared
continuation must also specify the exact boundary orientation relation,
which samples/subdivisions share one node owner, and what to do with
higher-order junction nodes.

## Fail-closed admission gates before any physical welding

1. **Source and identity:** exact model-byte hash, canonical original
   curve identity, unique incidences, matching original source parameters,
   exact generator epoch/retry and no duplicated/missing patch sides.
2. **Geometry and numerics:** finite original Bézier controls, validated
   source-curve/patch XYZ correspondence, a fully classified *entire
   interval* signed radial order audit, and no unqualified
   near-tangency/near-zero interval; re-evaluate at model changes.
3. **Policy:** explicit, independently approved sheet IDs and junction
   semantics. A missing policy fails closed regardless of geometric
   certification. No unreviewed `twin`, auto-pairing, or coordinated
   node ownership; even a geometrically compatible valence-2 interface
   remains a review candidate until its topology is established.
4. **Seams:** canonical source parameter segmentation across every
   approved shared owner; no partial/overlapping segment weld, hanging
   nodes, reversed IDs or accidental XYZ-only coordinate deduplication.
5. **Elements:** full UV boundary closure, source QUAD/AFT interface
   continuity, physical XYZ and Jacobian/orientation quality on
   curved patches, typed QUAD/TRI graph sanity and no same-surface
   element overlap.
6. **Atomic lifetime:** create all model-wide candidate owners and
   per-patch elements off to the side; inject failures at every
   construction/adoption stage; on rejection destroy elements before
   source nodes and preserve the previously accepted `MeshAdaptive`
   and `Patch::GetSubMesh` observers byte-/identity-equivalently.
   Publish only after all cross-patch checks pass; no partially visible
   model epoch.
7. **Regression:** original frozen Eistute/Book TRI parity, native
   GCC/MSVC QUAD, root CTest/Python, sanitizer lifetime for repeated
   mixed adaptive epochs and negative malformed policy controls.

## Engineering sequence after scientific gate and approval

**R2c-0 — read-only fan records:** Build immutable per-source-segment
incidence/radial ring records with `automatic_sheet_pairing_enabled=0`.
Verify valence 4/28 complete coverage and reject malformed source/model
revisions. No `SubMesh` writes.

**R2c-1 — policy validator:** Accept only versioned explicit decisions,
report missing/unapproved/contradictory incidences. No assumption that
`radial_next` implies topological twins.

**R2c-2 — provisional ownership staging:** Introduce a research-scoped
model-level owner lifetime for any *approved* cross-chart shared nodes,
then stage typed per-patch `SubMesh` owners/elements. The staging arena
must survive longer than all borrowing elements; never borrow from
another submesh's eventually replaceable node vector by accident.

**R2c-3 — atomic commit and rollback:** Test completely staged candidate,
then commit all relevant per-patch and model ownership links in one
engineered transaction with rollback to the previously accepted state.
A multi-patch adaptive retry remains a distinct follow-up qualification.

**R2c-4 — independent scientific validation:** Validate Eistute, Book
and a reviewed valence-3 Ribbed Bracket policy; retain a complete
original-source proof ledger and explicit failures. Production mode
remains opt-in until an independently approved release decision.

## Blockers not solved by this design

Book's small sampled radial angle cannot be promoted to an interval
certificate without exact signed Bernstein source logs and numerical
review. Even a complete interval order proof does not prove 3D
non-intersection of entire sheets, specify which Book pages are connected,
approve 1993 centroid or Delaunay/contour-contraction formulas, or
validate external Hermite models Pneu/Nariz and the unidentified Bolha.
No advisor decisions are fabricated in this note.

**Next bounded action:** obtain the final exact CI original Bernstein
metrics for Eistute and Book, then review this preflight as a proposed
(non-binding) architecture before any R2c source code starts.
