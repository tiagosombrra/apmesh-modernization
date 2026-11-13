# R2c-1 — source-bound high-valence sheet review, not physical admission

**Research-only engineering implementation, 2026-11-13 UTC.**

## Scope and source evidence

The new `tests/quad/test_r2c1_sheet_review.py` consumes **only** the
qualified R2c-0 original-source records created in the same workflow from
real `GeneratorAdaptive`, actual model bytes, native signed Bernstein
orientation witnesses, and independently matched M4 `PatchReader` source
incidence graphs. It does not invent a sheet mapping from coordinates,
radial angle or a reconstructed mesh.

The exact source record is rechecked against the retained R2c-0 manifest,
its per-model SHA-256 blob and pending-policy SHA, model-byte hash and
source log hash. Every original source interval has an ordered radial
cycle, strictly increasing source parameters and original physical node
IDs; geometric `radial_next` is never interpreted as `halfedge.twin`.
The entire source record and proof are embedded in the review packet and
locked by a canonical SHA-256 digest. Eistute has 4 incident source
patches/10 original source intervals (40 radial adjacency records), and
Book has 28/12 (336). These are numeric geometric radial-order witnesses,
not physical mesh topology.

## Deliverable: one immutable review packet per source model

Each `r2c1_<model>_review_packet.json` contains:

- Original model, source CTest log, M4 incidence graph, source record and
  radial-cycle digests; `Geometry` curve registry index, original
  epoch/retry and original source Bézier interval boundaries
- All exact source `(patch_index, side, curve_reversed, winding_sign)`
  incidences and copied source physical node IDs, no dangling C++ pointer
- Source Bernstein signed interval metrics, unambiguously separated from
  the scientific **sheet/junction decision**, which remains
  `junction_kind=UNDECIDED` and
  `review_status=PENDING_ADVISOR_REVIEW`
- Five review questions about junction semantics, incidence sheet
  identities, physical normal/orientation compatibility, shared node
  ownership and original source interval subdivision policy, all null
  and requiring external scientific determination
- Explicit false fields `scientific_admission`,
  `physical_node_welding`, `manifold_twin_authorized` and
  `physical_SubMesh_published`.

The public review packet contains NO scientifically approved continuation
groups, review signatures, fabricated advisor declarations or physical
node-owner instructions. Substituting even one field of a packet fails the
source-bound packet validator; the packet is regenerated from original
evidence rather than edited in-place to authorize connectivity.

## Unapproved draft syntax and rejection policy

A separately validated **draft** may express a test-only proposal for
pairwise continuation, a branching group of three or more incidences or
the explicit alternative of independent charts. Group members must
reference real original `(patch, side)` source incidences in canonical
radial order and cover the complete currently qualified original source
interval partition. A member cannot appear twice or in two competing
groups within the same current draft. This deliberately conservative
constraint forbids unsupported variable-interval topology changes; any
future sheet topology with changes along a source interval requires a
separate reviewed source-gate design.

The only permitted group orientation field is
`REQUIRES_SCIENTIFIC_REVIEW`, and the only permitted node owner field
is `UNASSIGNED`. The draft must say `DRAFT_NOT_APPROVED` and keep
reviewer evidence null, `scientific_admission=false`,
`physical_node_welding=false`, `manifold_twin_authorized=false`,
`physical_SubMesh_published=false`. Structural validation returns
`DRAFT_REQUIRES_INDEPENDENT_SCIENTIFIC_APPROVAL` even when a *synthetic
test-only* pair or branching group passes its syntax checks. Such a
passing unit test is NOT a real Eistute/Book topological decision and
must never be published as an actual review outcome.

The CI also rejects stale source hashes, forged review findings, changed
curve/epoch/retry, missing/reversed/duplicated incidence, invalid radial
successor, fake source physical node IDs, invalid group arity, overlapping
source members, partial/duplicated interval coverage, wrong junction
kind, any bypass of normal review and any attempt to set shared node
ownership or approved physical welding. The regression script fixes
**49 negative controls for each original model, 98 in all**, in addition
to a positive synthetic *draft-structure* test for each model (both
must return no scientific/physical admission). Controls are required
by the separately named GitHub Actions step, downstream of the R2c-0
source-derived JSON creation, with bounded 14-day retention artifacts.

## Scientific handoff: required independent decisions

For the Eistute 4-owner axis and Book 28-owner spine, an independent
scientific/model-owner review must determine:

1. Does the source curve represent distinct charts, a true nonmanifold
   branching junction, selected sheet continuations, or a combination?
   Identify **all** affected original `(patch_index, side)` incidences
   in a signed source-model versioned decision.
2. For every intended physical connection, what is its boundary
   orientation relation, normal compatibility and material/sheet
   meaning along the **whole** original source curve?
3. Which original source nodes remain separate, which nodes (if any)
   need one model-global owner, and how is ownership/lifetime staged
   across distinct patch-owned `SubMesh` objects?
4. Must connectivity/subdivision vary within a source curve? If so,
   define a new interval-qualified policy; do NOT pretend the current
   all-interval syntax can express it.
5. What source model SHA, reviewer identity/evidence and approval
   provenance authorize the *future* engineering step? String flags
   alone never count as review evidence.

These choices are **not yet supplied or independently approved**. The
Ribbed Bracket's original valence-3 curve intervals also lack the
source-wide Bernstein evidence used here, so it is not silently covered.

## Closure boundary

The R2c-1 deliverable is a read-only *review and candidate draft gate*.
It does NOT implement an approval-verification authority, accept a real
scientific decision, create a shared `NodeAdaptive` owner, weld edges,
or publish any global QUAD/TRI `SubMesh`. The original production TRI
generator, `main`, historical 1993 algorithm, default application
mode and `quad_uv` remain unchanged.

After obtaining genuine externally reviewed scientific semantics,
a separate versioned admission gate must authenticate evidence, enforce
cross-patch orientation/ownership invariants and reject partial or
conflicting node-sharing decisions. Only then may R2c-2/3 consider
model-wide staged owners, atomic commit/rollback, repeated adaptive
epochs and native ASan/UBSan verification.

**Qualification:** retain exact candidate source SHA and independent
push/PR run IDs, the root log `R2C1_SHEET_REVIEW` marker, source model
counts and controls. The presence of a draft implementation or passing
earlier R2c-0 CI cannot establish exact-head R2c-1 qualification.
