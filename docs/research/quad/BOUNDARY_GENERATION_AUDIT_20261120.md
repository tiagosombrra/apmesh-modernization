# Curve sampling and boundary transition audit

20 November 2026, Fortaleza. Read-only analysis of the retained `builtin:curva_bezier` article-front history. Generation evidence comes from the PR240 application archive. The curvature records are pinned to `c93a383e2775d33eb8a7e5f28cbc410e3d98593d` (draft [PR243](https://github.com/tiagosombrra/apmesh-modernization/pull/243)). Each statement below concerns this one patch and the recorded configuration.

## Where the imbalance is introduced

1. **The source contour is coarse relative to the interior.** The original generator runs `AdaptCurveByCurve`, then `AdaptCurveBySurface`, then `AdaptDomain`. All four sides are represented by cubic Bézier curves. Side 0 is geometrically curved and the other three are straight. From Step 1 to Step 3, side 0 grows from 3 to 5 to 9 points, while the straight sides each retain three final points. At Step 3, the curve-only pass keeps 5 points on side 0 and reduces each straight side from 3 to 2. The surface pass produces the final 9 and 3 points respectively. The parameter lists are identical at the surface and final-budget observations. The contour audit verifies original sample identity, exact XYZ and oriented intervals on both exported TRI and mixed meshes.
2. **Mixed reconstruction makes that size contrast more visible.** The application captures the selected TRI source contour and native quadtree. The mixed front connects the original contour to the template region on replayed leaves, then runs five fixed-contour UV smoothing passes. At Step 3 the two segments of each straight side are each 1.0 physical model unit. The median edge with both endpoints off the contour is 0.12795 in TRI and 0.06549 in the final mixed mesh. The same straight segment is therefore 7.82 and 15.27 times the respective medians. These are descriptive ratios. Edge distributions differ between a triangular mesh and a mixed mesh.
3. **A contour-edge metric alone misses most of the fan.** The midpoint of straight side 3 touches 9 faces in TRI and 22 in TRI/QUAD, in each case including the faces that use its two contour edges. Across the patch, 45 TRI and 94 mixed faces touch a contour vertex without using any contour edge. Their smallest angles are below two degrees. Those faces need their own column when comparing quality. Angle and edge ratio can move in different directions during smoothing.

Step 3 measurements in physical XYZ from the same original contour:

| Measurement | TRI source | Mixed before smoothing | Mixed after smoothing |
| --- | ---: | ---: | ---: |
| Nodes | 223 | 689 | 689 |
| Contour intervals | 14 | 14 | 14 |
| Median edge with both endpoints off contour | 0.12795 | 0.06375 | 0.06549 |
| Smallest angle on a face using a contour edge | 7.90° | 10.37° | 9.15° |
| Worst edge ratio on these faces | 5.31 | 4.69 | 6.13 |
| Smallest angle on a face touching contour by vertices only | 1.71° | 1.42° | 1.87° |
| Worst edge ratio on these faces | 4.57 | 15.08 | 11.05 |

The straight-side fans are present before smoothing. The worst contour-edge angle is on curved side 0 in each Step 3 snapshot. Poor generation quality is therefore visible in both the coarse straight-side transition and the curved side, through different measurements.

## Which controls can affect this case

`curved_patch_article_front.conf` selects `ADAPTIVE_MODE=legacy` and sets both `PATCH_FACTOR_MIN` and `PATCH_FACTOR_MAX` to `1.5`. `ComputeCurveAdaptationFactor` applies `CURVE_FACTOR_SENSITIVITY` before clamping to those same bounds. The logs confirm `1.5` on all 12 adapted curve records and all three selected domain invocations. Changing only curve sensitivity under this fixed interval cannot change the resulting curve factor. Curve point budgeting requires both `BudgetDrivenAdaptation` and `CurvePointBudgetMode`. Setting the second flag alone in the current profile does not establish that the budget path runs. The existing `ComputeCurveDomainBalance` also returns `1.0` when passed a nonpositive target size, so a logged `1.0` cannot serve as proof of a well-graded mixed transition. The diagnostic compares actual edges and faces instead.

The earlier default-bound control on this Bézier model, using the existing legacy reconstruction, reached 112 boundary intervals on its Step 2 candidate and the TRI source rejected Steps 2 and 3 for increased global error. This is a different exterior reconstruction. It is practical evidence against assuming that simply restoring the ordinary factor bounds will give a better accepted history in the article-front mode. The [domain factor record](DOMAIN_FACTOR_BOUNDS_REPAIR_20261116.md) retains the intended scope of the existing clamp.

## Curvature and initialization

The 14 Step 3 boundary nodes were aligned by OBJ ID with both earlier jet reports. The evidence records UV, XYZ, support coordinates, physical distances, condition, analytic and estimated K/H per node. The largest bounded K and H errors occur on the curved side (OBJ nodes 681 and 680 respectively). For node 681, enlarging support increases its physical radius from 0.2735 to 0.5451 and reduces its condition number from 238.14 to 146.04. Its absolute K error increases from 6.2414 to 7.1104. This is consistent with a loss of locality and does not attribute the error to one component of the fit. The jet reports run on completed snapshots and cannot have caused the observed faces.

Both existing fits lack enough positions on the five-node Step 0. Keep the original coarse Step 0 and its explicitly unavailable diagnostic as the proposed baseline for the next generation comparison. Mixed global curvature error remains unavailable. Decisions about a mixed startup estimator or how to begin mixed acceptance belong to a later scientific step.

## Proposed next comparison for alignment

Prioritize generation quality ahead of another curvature estimator experiment. Keep the original curve, domain, accepted/rejected lineage and stop machinery as the source, then evaluate the opt-in mixed generation using both contour-edge and vertex-only transition metrics. Preserve `S <= 1.5`, contour clearance, centroid, smoothing and all original formulas in this comparison.

Use one article-front configuration comparison based on the two existing bound profiles: the archived fixed `1.5` case and one candidate with the explicit `PATCH_FACTOR_MIN/MAX` overrides removed (legacy defaults `0.80` and `1.12`). Use the same model and run settings. Both curve and domain factors may change. This comparison measures their combined effect and cannot identify a curve-only intervention. Record curve and surface passes, factors, nodes/faces and growth, source acceptance/rejection reason, boundary and transition worst/median quality, and interior quality. Keep all rejected evidence. If the candidate repeats the existing growth or rejection problem, stop the configuration experiment. Use that outcome to decide whether the next proposal should target grading at the mixed interface or enable an existing curve-budget path in a separately controlled profile. No further sweep or policy follows automatically from this audit.

## Evidence and limits

The [numeric receipt](evidence/BOUNDARY_GENERATION_AUDIT_20261120.json) binds four archived steps, 48 curve-pass records, six original-source contour audits, 32 contour intervals paired across three snapshots, and 14 boundary curvature queries. It includes per-interval quality, source logs, input hashes and supporting coordinates. The first local audit compared face lists in export order and failed. The corrected check compares multisets of oriented face tuples, matching the existing smoothing contract. Inputs were hash-checked before and after. No native build, generation, new scientific rule, merge or Blender scene was run for this read-only audit. Prior PR243 validation keeps its original source scope. The default TRI implementation and feature branch are unchanged.
