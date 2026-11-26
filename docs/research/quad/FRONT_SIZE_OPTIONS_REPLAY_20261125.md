# Replay the front choices at oversized transition faces

[Origin of the size requests](MEASURED_SIZE_GROUP_TRIAL_20261125.md)
documents the two archived single-patch development runs. This replay
checks CurvaBezier operation 1 at requests 646 and 648 and Ribbed Bracket
operation 62 at request 478. It reconstructs the directed active front
from the original contour and the committed face prefix and reproduces the
native maximum-angle apex and prospective pair witnesses. It verifies the
source, request map, front trace and before-smoothing mesh against the
archived evidence before evaluating alternatives.

## Existing vertices

The replay enumerates TRI and two-TRI QUAD unions from the existing
first nonempty leaf neighborhood. It preserves convexity, the article
shape rule and the additional-pair geometry screen. The original two
pair choices keep their original exception to that screen. The
comparison includes scores within 2e-15 of the article shape limit
to avoid excluding a threshold case by Python rounding. On the
recorded base, all active vertices are then checked as an upper scope.
At the critical state, every other active base is also checked with
the original leaf neighborhood. A comparison retains only physical
faces covering the affected requests and verifies the median physical
edge against all requests the face contains. It also applies the
frozen TRI and QUAD safety floors for angle and shape. This is a
single-face feasibility check on an archived state, with a separate
historical scan for one edge. It does not replay alternate complete
advancing-front trajectories or guarantee that a different initial
partition will pass whole-mesh admission.

| Measurement | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Affected request size | 0.07104 and 0.07243 | 0.38298 |
| Native face median edge | 0.13681 | 1.04038 |
| Native face minimum physical angle | 22.33° QUAD | 13.54° TRI |
| Active vertices at the critical state | 116 | 40 |
| Other directed bases considered | 115 | 46 |
| Size-and-shape matches at the critical state | 0 | 0 |
| Recorded states scanned on the same base | 1 | 62 |
| Best target-covering size on the base over those states | 0.13681 | 0.64853 |

The Ribbed base is an exposed seeded QUAD edge. All three sides of
the same limiting TRI are present by operation 62. Changing to either
of its other bases reproduces the same closure there. The smaller
earlier QUAD reaches 43.55°, but measures 0.64853 against 0.38298
and has article score on the 1.5 rounding boundary.

CurvaBezier's two requests belong to the same level-4 leaf at the cap.
The first advancing base is the unsplit original contour interval 0,
with UV endpoints (0, 0) and (0.128500796854496, 0), and a physical chord
of 0.27316. The Ribbed request starts in level-2 leaf 11 and after the
native subdivision lies in level-3 leaf 150, below the same level-4
cap. Subdividing the leaf alone can still leave it in the contour
clearance band. Measure the actual front and final faces to decide
whether either edit realizes the requested physical size.

## Handoff and validation

Alignment requested for two matched native arms using existing
subdivision primitives. Bisect CurvaBezier's original contour interval 0
by arc length in one arm. In the other, try one further native
subdivision of the Ribbed leaf containing request 478, stopping at
level 4 and restoring 2:1 balance. Verify original source and curve
invariants, measure all affected face sizes both at birth and after
smoothing, and compare shape, sampled geometric error and face count
against the exact controls. Keep the frozen thresholds and face
budgets. The two paths test room to refine at different stages;
the experiments do not establish a common automatic selection rule.

The read-only replay and its input/metric verification pass. The
first invocation treated the built-in model identifier as a file
path and failed before replay. The corrected invocation delegates
source verification to the existing evaluator and completes both
cases. No native generation, new executable or full closure
validation was run for this checkpoint. Zero mixed adaptive epochs
were accepted. Shared curves, owner reentry, reserved cases and the
global mixed curvature norm remain open.
[Replay evidence and input hashes](evidence/FRONT_SIZE_OPTIONS_REPLAY_20261125.json).
