# Try one ideal point at an unmet physical size request

The approved experiment follows the [fixed-interface projection](COUPLED_TRANSITION_PROJECTION_20261125.md).
[Draft PR 292](https://github.com/tiagosombrra/apmesh-modernization/pull/292)
at `4f29dd06b087f4fb0fb299924d39f825ae2ccb96` adds the opt-in `size_driven_ideal_point` native plan.
For an eligible TRI or QUAD, it checks the median of its physical
edges against every contained size request. The current ideal point
placements use the existing leaf-width fractions 1, 1/2, 1/4 and 1/8.
At most one point can be introduced per generated candidate.

Every position must pass the first TRI validity and shape check.
Then reconstruct the remaining front twice using the existing
selection. The proposed closure must fit the frozen face budget
and realize the original triggering requests and all requests in
the replaced region. Incident faces on both sides of a shared edge
count, including pre-existing seed faces. The changed patch holds
its directed boundary, the physical safety floors and comparable
regional shape limits. Remeasure the affected sizes on the final
smoothed surface. Keep the existing full-mesh admission for shape,
geometry and growth. On failure before staging, retain the original
source and do not publish a successor OBJ. The default TRI path and
the prior experimental selectors retain their previous behavior.

## Matched native result

The current no-option CurvaBezier and Ribbed geometries use 731 and
540 faces. Both budgets remain 805 and 601. The one-point legacy
shape-triggered comparison inserts at CurvaBezier operation 91,
with 733 faces, and leaves all three requests of interest oversized.
It inserts no point on Ribbed and retains the 540-face candidate
byte for byte.

| Measurement | CurvaBezier size-driven | Ribbed Bracket size-driven |
| --- | ---: | ---: |
| Triggered operations | 2 | 1 |
| Positions examined | 8 | 2 |
| Inserted points retained by the local guard | 0 | 1 |
| Final staged faces | no candidate | 541 |
| Final contour samples | control stays at 19 | 26, unchanged |
| Accepted mixed adaptive epochs | 0 | 0 |

On CurvaBezier, the two targets at operation 1 measure 0.13140
against 0.07104 and 0.07243. Operation 58 measures 0.16295
against 0.09779. Four first triangles fail geometry or shape, one
point is unavailable and three complete closures fail the physical
size check. The isolated normal and smoothed frames both match the
control byte for byte. No staged candidate or front export exists.

In Ribbed, operation 6 begins with a QUAD of size 0.39059 and
request 503 asks for 0.33409. The half-width placement at UV
(0.7188815923873335, 0.03125) passes. It replaces one QUAD and
two TRI with two QUAD and two TRI. The four birth angles are
25.05°, 25.44°, 38.17° and 49.90°. One new QUAD covers the
request at birth, size 0.29349. A TRI covers it after smoothing,
with size 0.18923 and minimum angle 36.76°. All 26 directed
contour sites and the seeded topology are preserved.
The final requests met increase from 10/17 to 11/17.
Sampled geometric RMS at 48 × 48 moves from 0.02010729
to 0.02010264. Maximum deviation stays 0.10748411.

The Ribbed transition TRI below a safety floor decrease from 13
to 11. The worst final transition TRI moves from 11.97° to 11.91°
and other full-mesh shape limits still block admission. The target
improvement is local to the tested point.

## Remaining advancement constraint

The worst transition TRI in both current meshes contains no
physical size request. In CurvaBezier it is 3.25°; in Ribbed it is
11.91°. With the actual recorded active fronts, the quarter-width
positions yield valid initial TRI of 40.11° and 51.17°, respectively.
The separate legacy native trials try both the quarter- and
eighth-width positions on these same polygons and refuse their
complete closures for shape. This differs from a placement that
fails before making the first TRI.

Next reproduce the two failed legacy closures from their recorded
front states and identify the first replacement region and metric
that causes refusal. Check whether the existing TRI/QUAD choices
can close those regions without exporting the flaw to a neighboring
face. This read-only result should guide any further mixed-front
selection proposal before another native rule. Global mixed
curvature error, shared curves, owner reentry and reserved cases
remain open.

## Validation and closure

Both no-option controls reproduce eight archived artifacts per model
byte for byte. The zero-budget and duplicate-policy plans are refused.
The exact source passes native bound-source, original-curve and
certificate checks, 15 progressive tests, six sizing tests and the
direct three-stage article rollback. A separate planar GCC fixture
exercises guard rejection and single-point publication from a chosen
QUAD with the same header. The initial geometric run and the final
run with the explicit trace label produce identical numerical
outcomes and smoothing frames. The final native evidence binds both
source files and the measured executable. The primary local
validation adapter lacked its tools and iteration baseline. Full
stage validation and independent review remain pending; the feature
remains a draft. [Hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45790071630).
[Native receipts and witnesses](evidence/SIZE_DRIVEN_IDEAL_POINT_20261126.json).
