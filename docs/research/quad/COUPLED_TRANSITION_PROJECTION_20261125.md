# Project contour and template grading at two transition patches

This read-only comparison binds the native CurvaBezier and Ribbed
archives from [PR 291](https://github.com/tiagosombrra/apmesh-modernization/pull/291).
The original sources, candidate, birth mesh, tree and curve proof
match the recorded hashes. The seed projection reproduces the 631
CurvaBezier and 456 Ribbed QUAD by normalized oriented geometry.
The template-clearance factor and the physical arc-to-edge trigger
of 1.35 are inherited from the previous tools.

## Native edits in current scope

Project the adjacent certified arc splits and the owners and
neighbors of their short seed edges. Reverse the retained groups
to recover the pre-group leaf partition and verify its leaf count.
Require four disjoint leaves, request protection and native 2:1
balance before proposing another group. At the two selected
footprints, zero groups pass. In the CurvaBezier corner, grouping
would affect requests 646 and 648. In Ribbed, grouping the
newly refined parent would affect 478, 486, 488, 503 and 504.

The arc candidates use the archived native split positions and
independently integrated physical lengths. A disk face bound drops
only the edited intervals' clearance constraints for its upper
seed-vertex set, retaining the guaranteed seed faces as a lower
QUAD count. These are bounds for the projected vertex layouts,
without introducing new interior vertices.

| Projection | CurvaBezier corner | Ribbed transition strip |
| --- | ---: | ---: |
| Face bound for one arc split / profile limit | 749 / 805 | 567 / 601 |
| Face bound for two arc splits / profile limit | 750 / 805 | 568 / 601 |
| Representative arc-to-seed ratio before → after split | 2.17 → 1.09 | 4.00 → 2.00 |
| Native additional group projections passing preconditions | 0 | 0 |

The CurvaBezier ratio is for the first bottom child interval. Other
bottom intervals have a similar ratio, while the arc on the left
side remains at about 3.97 times the support edge even after a split.
The affected seed edges remain present in every projected combination.
The Ribbed representations would exceed the existing three-child
request limit. The curves remain projections, including those above
the current request limit. No new scientific limit was activated.

## Local fixed-interface feasibility

For each admissible geometric arc layout, take the front faces
incident to the edited endpoints and repeat with one edge-neighbor
expansion. Keep the directed cavity boundary and all projected
interface sites. Enumerate disks with TRI and QUAD, convexity and
the article's UV QUAD shape rule (S ≤ 1.5). Check both physical
safety metrics and the median physical edge against every request
in each covering face. The calculation includes hypothetical
layouts above the Ribbed parser limit. It uses only already bound
surface samples and the projected arc points.

| Observed count or best ratio across the layouts | CurvaBezier | Ribbed |
| --- | ---: | ---: |
| Finite conforming layouts examined | 93,830 | 13,442 |
| Layouts meeting the physical shape floors | 144 | 0 |
| Layouts meeting the physical size requests and shape floors | 0 | 0 |
| Best worst incident size / requested size, shape ignored | 1.814 | 1.282 |

The counts sum across cavity widths and arc variants. A cavity may
include more than the first failed region. For Ribbed, the directly
improved request 478 is outside this tested front cavity and remains
bound to the seed geometry. The cavity covers other oversized sites,
including requests 488 and 503 in the broader variant. The results
only bound the tested cavities and vertex sets. They do not rule out
other seed arrangements, interior points or global front trajectories.
This is not a prediction of the native face selection or of geometry
after smoothing.

Five read-only controls exercise feasible, size-blocked and
face-budget-blocked square closures and the two foreign image
refusals. Independent incidence and area reconstruction verifies
the 44 retained best witnesses. No native execution or new
executable took place for this checkpoint. No mixed adaptive
epochs were accepted.

## Next experiment awaiting alignment

Compare the existing guarded ideal point in the mixed advance with
a trial allowing it to activate on an unresolved physical size
request in the affected TRI or QUAD region. Start with the existing
point placements and one introduced site per attempt. Reconstruct
the full candidate and retain it only after a compatible local
closure and the unchanged size, shape, geometric error and face
budget checks. Preserve native curve proof, TRI behavior and
rollback. This is a proposed change in selection scope. The existing
[ideal-point results](GUARDED_IDEAL_FRONT_CLOSURE_20261125.md) concern
selected TRI and do not resolve the present size-driven cases.
Shared curves, owner reentry, reserved cases, full closure and
global mixed curvature remain pending.
[Projection and controls](evidence/COUPLED_TRANSITION_PROJECTION_20261125.json).
