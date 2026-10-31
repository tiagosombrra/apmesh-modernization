# Front-edge cell and midpoint provenance before root retirement

Classification: engineering-only source diagnosis and documentation. Entry:
PR #131 main `0ed10cfaa6d346af1185ad61837baf08e83d2862`. No production,
fixture, configuration, formula, ordering, template or scientific policy change.
No new native diagnostic context or custom geometry campaign is executed.

## Result and scope

Template-front edges and generated edges obtain their cell observations through
different paths. Under coherent exact dyadic unit-root geometry, an initial
template-front raw ideal stays in the closed root, possibly on its border.
Generated-edge midpoint lookup alone supplies no corresponding clearance bound
for the next ideal. Neither finding establishes that a new ideal is selected
outside strict root interior or that native retirement is universally unreachable.

This audit assumes the previously admitted UV-square caller/prefix, finite
nondegenerate geometry, live endpoints/cells and complete coherent cardinal and
shared-slot state. A mathematical deduction under those assumptions is distinct
from measured path coverage or a proof for all floating-point inputs. Direct API
setters, stale/rebound cells, nonfinite coordinates, arbitrary contours and the
previously refused prefixes cannot be used to bypass these assumptions.

## Midpoint and cache lineage

Both template makeE and the two native makeMesh Edge constructions use the real
Edge constructor. It calls setVertices, which prepares an arithmetic midpoint
and vector, changes endpoints/bounds and commits the caches. The constructor
starts with null cell and null curve. These template/generated paths do not
call makeParamMid. Boundary construction is separate: it binds the live outgoing
curve and evaluates an oriented curve-parametric midpoint/normalized size.

setCell assigns a borrowed cell pointer; it does not change the midpoint. The
native geometry phase adds/removes observations and constructs new vertices and
edges, without moving admitted existing endpoint coordinates. A matching Edge
returned by findEdge retains its original direction, midpoint and cell. The
later fillMesh/improveMesh sequence, including coordinate/cache refresh during
smoothing, is beyond this pre-improvement inference. Public endpoint setters
alone do not establish cache coherence for an arbitrary external mutation.

Prefix subdivision refreshes registered edge cells through setChildrenEdges and
native findCell; its default remains enabled. Neighbor balancing precedes native
outer vertex/edge and internal template creation. This does not introduce uniform
refinement or substitute the standalone tree execute path.

## Complete outer-template slot map

Let C be the creating non-boundary leaf. Native outer vertices are its four
corners and, where shared topology requires them, side midpoints. With bottom-left
v0, bottom-right v2, top-right v4 and top-left v6, odd vertices v1/v3/v5/v7 are
the corresponding side midpoints. The directed edges have left normals outward
from C; they are axis-aligned, not arbitrary diagonals.

| Slot | Directed endpoints | Left normal | Neighbor for front test | Cell assignment at creation |
| --- | --- | --- | --- | --- |
| 0, bottom | v1 if present, otherwise v2; to v0 | (0,-1) | bottom.front | Coarser of C and neighbor; equal level chooses neighbor |
| 1, bottom | v2 to v1 | (0,-1) | bottom.back | back neighbor; requires two neighbors |
| 2, right | v3 if present, otherwise v4; to v2 | (1,0) | right.front | Coarser of C and neighbor; equal level chooses neighbor |
| 3, right | v4 to v3 | (1,0) | right.back | back neighbor; requires two neighbors |
| 4, top | v5 if present, otherwise v6; to v4 | (0,1) | top.front | Coarser of C and neighbor; equal level chooses neighbor |
| 5, top | v6 to v5 | (0,1) | top.back | back neighbor; requires two neighbors |
| 6, left | v7 if present, otherwise v0; to v6 | (-1,0) | left.front | Coarser of C and neighbor; equal level chooses neighbor |
| 7, left | v0 to v7 | (-1,0) | left.back | back neighbor; requires two neighbors |

makeOuterEdges skips cells for which inBoundary is true. At each creation site,
the edge enters the template front only if the listed neighbor Q is inBoundary.
addFront marks that same object free/in-boundary without recomputing M or cell.
Shared nonnull edge slots retain their original creation/attachment. The separate
internal template edges are tree-owned and receive their creating cell, but
makeInitialFront imports only getFront, not every tree-owned internal edge.
Their ownership or cell assignment alone does not make them selector bases.

inBoundary tests missing cardinal neighbors. Its geometric meaning as touching
the root perimeter depends on the admitted complete cardinal graph; it is not
an arbitrary Boundary-contour test. All eight literal slot/front/cell rules are
retained even where the conditional geometry below excludes a configuration.

## Conditional template bound and the remaining border case

Consider exact geometry of a coherent dyadic square partition of [0,1] squared,
with valid positive cardinal overlap/coverage, the admitted level/count balance
and correctly shared slots. A non-boundary leaf C of side s has clearance at
least s from every root side: each corner coordinate lies on its dyadic s grid,
and none of its sides touches the root perimeter.

If an adjacent leaf Q were finer than C, its side would be at most s/2. Its
tangential projection overlaps C inside C's tangential extent, and its outward
normal extension from C is at most s/2. It therefore cannot reach any root side.
With a complete graph it could not satisfy inBoundary. Consequently a neighbor
Q that actually satisfies the template-front test is equal or coarser than C.
In particular, a finer back-neighbor on a two-neighbor side cannot create a
template front under these assumptions. This is a conditional geometric
deduction, not permission to delete the corresponding native branches.

The native even-slot rule then attaches Q; the smaller-neighbor case is excluded
by the front condition. M lies on their shared axis-aligned side segment, and N
points from C into Q. The existing construction I=M+height(Q)N places the raw
ideal on Q's opposite side, within Q's closed box and hence within the closed
root. It may reach the root border. This deduction does not prove exact native
arithmetic for arbitrary depths, malformed slots, tolerance-induced geometric
inconsistency or nonfinite/degenerate inputs.

Strictly exterior raw template-front ideals are thus excluded by this conditional
exact-geometry argument, but the original guard uses !root.in and also targets
border points. A border ideal still needs a normally completed empty-survivor
scan, both native ideal vetoes to pass and successful adoption/return. Complete
root boundary segments and their point-proximity veto are a separate obligation;
closed-root containment does not settle this remaining guard case.

## Generated-edge provenance and possible displacement

The original caller root-domain guard precedes both generated Edge constructors.
Provided the admitted existing vertex set lies in the closed root, a borrowed
best inherits that position and a fresh best must pass strict root interior
before edge construction. The first new Edge is directed base V1 to best; the
second is directed best to base V2. Their arithmetic midpoints therefore lie in
the closed convex root under that finite endpoint assumption. This is not a
claim that both endpoints lie in the same leaf or that all native inputs satisfy
the assumption automatically.

Each Edge is adopted in innerEdges, added to edges and queued under the existing
policy before quadtree->findCell. The latter queries root->findCell(e), which
tests only e->getMid() with out. It recursively tries bottom-left, bottom-right,
top-right and top-left, returning the first accepting leaf. out expands each
cell by TOLERANCE_AFT. At seams/halos, several cells may accept M; native order
selects among them. Lookup is neither whole-edge containment nor a nearest- or
smallest-cell optimization. It must not be replaced by one to obtain coverage.

The returned leaf becomes the borrowed Edge cell before edge registration along
its ancestor chain. A missing result returns without resetting an existing cell;
a new Edge would remain null. A coherent complete partition and a valid finite
root-contained M with positive tolerance provide the intended lookup context.
This source audit is not an exception/registration/lifetime qualification, and
a null/stale cell followed by makeIdealVertex is not an admissible witness.

For the next finite nondegenerate base, the raw construction is still I=M+hN,
with h from the attached leaf and N from that generated Edge's direction. A
midpoint accepted by a leaf or its halo does not imply h is at most M's distance
to every root side. Even strict midpoint inclusion in a leaf would not give that
root-clearance inequality for a boundary-adjacent leaf.

For root bounds (lx,ly,ux,uy), the exact-geometry border/exterior conditions are

`h Nx <= lx-Mx`, `h Nx >= ux-Mx`, `h Ny <= ly-My`, or `h Ny >= uy-My`.

At least one holds exactly when finite I fails strict root interior; strict
inequalities identify strict exterior. A sufficient direction-independent bound
for closed-root containment is h<=d, where d is the minimum of the four root
clearances of M; h<d suffices for strict interior. Native midpoint lookup does
not establish either bound. These are analytic conditions, not a fabricated
mesh/context or proof that a generated base with such displacement is reached.

Creation, queue insertion and cell attachment do not guarantee a later selector
call on that Edge: a later existing-vertex selection can remove a matching edge
from front/rejected and mark it nonfree before it is popped. Only a popped
non-marker base invokes findBestVertex. A constructed generated Edge or empty
second-pass entry therefore does not qualify generated-base selection.

## Evidence, delivery and disposition

The [source facts and slot matrix](stage3/front_edge_provenance/source_facts.json)
record 85 scoped anchors across six files, all eight slot rules and five native
ordering groups. Replay checks source identity, scoped uniqueness, positions and
order; it does not prove whole-program alias invariants or floating-point bounds.
The [compact summary](stage3/front_edge_provenance/summary.json) identifies the
initial source-audit seal. Local build/front-edge-provenance-audit retains the
entry/source/replay/command records and exact-head/main delivery evidence.

Prior source-audit and native geometry records remain immutable and are checked
without a new custom native campaign. Production, fixtures, existing accepted/
rejected traces, all 66 protected raw article inputs and scientific baselines are
unchanged. Require the existing 73 CTest entries and 380 Python tests on exact
delivery head and merged main, source/slot/order replay, unchanged tracked
non-documentation and application identity, whitespace, inventory/contracts and
staged-byte/metadata audits. Check remote main, all branches, PRs and checks before
integration. No new scientific run, sanitizer/lifetime qualification or supported
application defect is claimed.

The bounded provenance audit is complete. No admissible retirement witness or
universal unreachability theorem is established; the preserved four-context
observation remains borrowed-only with zero retirements. Stage 3 stays open with
37 numbered qualified slices; stages 0-2 retain measured closure and 4-11 remain
pending. No code, template or domain policy change follows from this source map.

Next single item: source-only audit of the root-border point-to-edge proximity
veto, including endpoint and tolerance cases, before any further retirement
measurement. Keep fixtures, numerical order, thresholds and policy unchanged.
