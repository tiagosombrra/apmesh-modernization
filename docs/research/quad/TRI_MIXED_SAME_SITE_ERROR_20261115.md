# Same-site TRI versus QUAD/TRI error diagnostic - 2026-11-15

Scope: read-only measurement of the eight already exported physical states at
feature e90d5a30963ed0ade9683c69a530847709188fe3. No new mesh generation,
compiler, native test, acceptance control or scientific tolerance was changed.
This answers the refinement-growth and error-comparison questions.

## Refinement growth

The curved boundary step1 output has9 points/eight intervals. At step2 the
curve pass returns17 points/16 intervals, then the surface pass65 points/64
intervals. Both complete outputs are retained without the old point budget.
The interval count grows8x in one outer step because two sequential passes
compound refinement. Mixed faces grow188 ->1008 (5.36x); nodes165 ->953 (5.78x).
This is aggressive growth, not evidence by itself that the extra work is wasted.

## Common metric and reproducibility

Compare Euclidean XYZ interpolation error against the same original Bernstein
surface at identical uniform-UV midpoint grids64x64 and128x128. TRI uses
barycentric interpolation; four-node QUAD uses the existing inverse-bilinear
weights. The presented RMS is weighted by the analytic surface Jacobian:

`RMS_area = sqrt(sum(|S(u,v)-S_h(u,v)|^2 * |Su cross Sv|) / sum(|Su cross Sv|))`.

Percentages are `100 * RMS_area / sqrt(8)`, where sqrt(8) is the distance between
opposite physical source corners, in source units. This is a sampled geometric
metric, not curvature error, a finite-element solution error, a continuous bound,
a convergence-order estimate or an acceptance policy. Midpoint sites do not
sample the boundary itself; the earlier curve-distance diagnostic remains separate.

The local read-only analysis uses the existing independent_common_grid kernel
without its requirement to have both TRI and QUAD sample regions for TRI-only
input. Count integrity, finite geometry, source derivatives, tolerances, face
search and weights remain unchanged. The original helper file is untouched.
All six actual mixed-stage/grid measurements are exactly equal to the unmodified
helper. Initial TRI/mixed files give identical metrics. Removing an initial TRI
face is rejected for an uncovered source site; no failed point is skipped.
Script SHA and every input OBJ hash are retained in the JSON receipt. Local
command: `python build/quad-error-comparison-20261115/compare.py`. Existing kernel:
`tests/quad/independent_common_grid.py`, function `common_grid_source_error`.

## Measured128x128 results:16,384 identical source sites per mesh

| Step | TRI nodes/faces | Mixed nodes/QUAD/TRI | TRI RMS, source units | Mixed RMS, source units | TRI RMS / corner diagonal | Mixed RMS / corner diagonal |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 5/4 | 5/0/4 | 0.07687326654 | 0.07687326654 | 2.7178804% | 2.7178804% |
| 1 | 63/104 | 165/120/68 | 0.006073297775 | 0.005620346123 | 0.2147235% | 0.1987092% |
| 2 | 337/560 | 953/784/224 | 0.001086496058 | 0.0006182017603 | 0.03841344% | 0.02185673% |
| 3 | 337/560 | 953/784/224 | 0.001086496058 | 0.0006182017603 | 0.03841344% | 0.02185673% |

Mixed RMS is7.458% lower at step1 and43.101% lower at step2, but it uses2.62x
and2.83x as many nodes. This is not an equal-cost efficiency comparison. From
step1 to2, mixed RMS falls approximately89.0% while node count grows5.78x.
At step1 the sampled maximum actually rises slightly: TRI0.02008810114 versus
mixed0.02018096207. At step2 maxima are0.004797344775 and0.004606095132.
A lower RMS therefore does not mean improvement under every metric.

Both meshes retain exactly the same source boundary at each step. Differences
in this comparison concern their interiors and discretization costs. Step3
repeats rejected step2; neither is an accepted mixed transition.

Grid64 area-weighted RMS pairs (TRI,mixed), source units:
step0 (0.07685632274,0.07685632274),
step1 (0.006068792810,0.005618884318),
step2/3 (0.001082033888,0.0006190044308).
The RMS ordering persists at both grids. Two grids do not establish a continuous
error bound or a general advantage of QUAD over TRI.

## Curvature indicator is a different objective

The original TRI reference reports relative surface-curvature indicators
0.314848,0.125829,0.382516,0.382516 over steps0..3. Its indicator increases at
step2 while the measured geometric RMS decreases in both outputs. This explains
why a geometrically closer proposal can still be rejected by the current TRI
reference. There is no corresponding approved production mixed curvature
estimator yet; do not assign these TRI values to the mixed reconstruction.

Next functional decision: design a preregistered refinement/acceptance criterion
for the actual mixed flow that distinguishes geometric fidelity, curvature and
cost. Match node/element budgets before making efficiency claims. No new point
cap, growth factor or acceptance threshold is selected by this measurement.
The existing draft PR238, integration/documentation gates and R3/M7 remain open.
