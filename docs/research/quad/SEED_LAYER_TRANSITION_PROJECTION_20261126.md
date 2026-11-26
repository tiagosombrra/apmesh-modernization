# Project one layer of template quadrilaterals in the transition

This is the approved read-only successor to the
[failed front-only closures](MIXED_CLOSURE_REFUSAL_REPLAY_20261126.md).
The CurvaBezier and size-driven Ribbed Bracket native controls
come from [PR 292](https://github.com/tiagosombrra/apmesh-modernization/pull/292).
Bind the original source snapshot, tree, candidate, curve proof
and birth coordinates. Retain the positively selected Ribbed
interior point and all analytical contour samples.

## Feasible local replacements

Start with the isolated front cycle. Vary the subset of its
adjacent front-generated faces and the nonempty subset of the
first template layer. A template is eligible for the projection
only if it shares an outer edge with the selected front faces.
Keep the complete directed outer boundary of the enlarged patch.
Enumerate convex TRI and QUAD on retained UV sites under the
article S ≤ 1.5 shape screen. The physical checks use the frozen
minimum angle and shape metrics, every covered size request,
all unchanged incident faces and the frozen total face budget.
The search uses a disk closure with no new points. The second
pass tests all original interior sites, then subsets of removable
interior sites. A protected point can never be retired.

| Local quantity | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| One-layer cavity choices | 92 | 64 |
| Feasible witnesses or minimal candidate per tested subset | 2 | 46 |
| Nearby template QUAD involved in chosen witness | 4 | 2 |
| Retired interior interface vertices | 3 | 1 |
| Local faces before → after | 8 → 6 | 4 → 3 |
| Lowest local birth angle before → after | 2.53° → 15.86° | 11.91° → 25.96° |
| Lowest local angle at archived smoothed positions | 3.25° → 16.28° | 11.91° → 23.64° |
| Global face count before → after / cap | 731 → 729 / 805 | 541 → 540 / 601 |

The counts sum over the selected cavity and subset choices.
No tested layout retains every original interior interface
vertex while attaining the frozen checks. The smallest measured
retirement is three vertices for CurvaBezier and one for Ribbed.
These are seed interface sites strictly inside the replaced disc.
No unaffected face references them. No point on the native
analytic curve moves or disappears. The CurvaBezier patch uses
six TRI. The Ribbed patch uses two QUAD and one TRI and retains
its previously inserted interior point. The physical request 503 on
the boundary of the Ribbed birth patch remains at 0.29349 against
0.33409; the final-position projection keeps its prior value.
No previously met request is lost on either full stitched mesh.

## Whole-mesh cross-check

Stitch the selected cavities into the archived birth mesh and
into the archived smoothed placement. The latter uses existing
coordinates with the new connectivity. It is a separate
projection; no smoothing or native successor is run here.
Check exact outer directed boundary, source sample identity,
positive areas, matching area, zero new overlap, common-grid
surface error and disk incidence. The stitched OBJ files remain
local and are measured on the identical, bound analytic chart.
The all-vertex solver is separately controlled by a planar
centre-preserving case, an insufficient face budget and a
deliberately small physical size request.

At the archived smoothed positions, the area-weighted geometric RMS
on the 48 × 48 grid changes from 0.006621758 to 0.006622043
for CurvaBezier and from 0.020102640 to 0.020102170 for Ribbed.
The maximum deviation is unchanged in both models. The global
worst angles improve from 3.25° to 3.78° and from 11.91° to 11.97°.
Other faces still violate the frozen admission profile. There are
zero accepted mixed epochs. The local topology proof qualifies a
next experiment and does not validate a whole-mesh policy.

Alignment requested for a guarded native trial. Only retire a
vertex when every incident face is part of the replaced cavity
and the vertex is neither a certified contour point nor the
retained Ribbed point. Verify external face identity, sizes,
quality, error and growth after the existing native smoothing.
Keep rollback and the default TRI path. The native owner
implementation, general selection rule, shared curves, owner
reentry, reserved cases and global mixed curvature remain open.
The archived exact PR 292 hosted checks completed successfully.
[Projected witnesses, source hashes and checks](evidence/SEED_LAYER_TRANSITION_PROJECTION_20261126.json).
