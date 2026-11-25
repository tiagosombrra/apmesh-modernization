# Prospective geometry screen for additional advancing-front pairs

2026-11-25 Fortaleza. Source and archived native traces are bound to
[PR 275](https://github.com/tiagosombrra/apmesh-modernization/pull/275)
head `779ac3437a7ab7099dda3d26c8deb478892dc922`.
[Screening receipt](evidence/PROSPECTIVE_PAIR_GEOMETRY_SCREEN_20261125.json).

## Paired development study

Read the native birth traces without changing their decisions. Inspect 104
TRI fallback windows on the original selective CurvaBezier front and 74
on the original Ribbed Bracket both-seed front. Four windows yield 12
distinct shape-eligible QUADs. Repeat the search over 81 TRI fallbacks on
the Ribbed experimental history to cross-check its three recorded choices.
All alternate vertices are constrained by the existing local search and
the existing S <= 1.5 shape test.

Compare prospective QUAD interpolation with the analytic Bézier surface.
For each QUAD, use the same sites on the completed original birth mesh to
label improvement or degradation of local, area-weighted geometric RMS.
Use the five existing pilot sites and independent 8 by 8 and 16 by 16
sets of cell-center samples in the QUAD's interpolation coordinates.
Two candidates improve on all three sets. Ten degrade on all three.
The completed original mesh is an offline comparison only. The prospective
signal itself needs the active edge, candidate vertices and analytic
patch, all available at the current front operation.

| Denominator for maximum XYZ deviation | Largest relative error among improvements | Smallest among degradations |
| --- | ---: | ---: |
| Median physical edge length of prospective QUAD | 6.481% | 3.705% |
| Median physical edge length of originally selected TRI | 4.264% | 4.609% |
| Physical chord length of active edge | 3.946% | 4.887% |

All rows use the extrema over the three sampling sets. The candidate's
own size gives overlapping ranges. The physical active edge gives the
widest measured gap and uses the same denominator for every alternative
at that operation. Scaling the node and analytic coordinates by 0.001 and
1,000 preserves the five-site ratios and classifications in 24 controls.
Reusing the existing 1.35 size-grading ratio as an isolated prospective
QUAD-to-TRI size cap would block one improvement and allow four
degradations. It was designed for grading and is a countercheck here.

## Proposed native verification

Use the existing five-site maximum XYZ deviation divided by the length of
the already selected physical base edge. A common development ceiling of
0.045 lies inside the measured gap. Only apply the screen to optional
additional pairs, then select the eligible pair with the existing lowest
S and tie order. Keep the TRI fallback when no additional pair passes.
The original local pair decision and the edge order remain in force.

At the archived front states, the mask retains the CurvaBezier candidate
at operation 13, removes all Ribbed alternatives at operations 1 and 3,
and retains the Ribbed candidate at original operation 61. The Ribbed
experimental archive records that same candidate at operation 60. The
mask is predictive only on the recorded states. After the first changed
decision, a native front may visit different states and produce other
faces. The ceiling comes from two development cases and requires a
separate reserved-case qualification.

Await alignment on the prospective ceiling and scoped native comparison.
The next native test uses one executable and unchanged input plans on
both development cases, saving every local screened decision, the native
birth and final meshes, regional quality and common-site deviation. Sampled
geometric deviation and a global mixed curvature error remain distinct.
There were no new native runs or accepted mixed adaptive epochs in this
screening study. The earlier development code remains draft and passed
all four hosted jobs on its exact head. The first read-only invocation
failed on the existing oracle's missing score for a nonconvex union.
The completed command handles that return before comparing to S <= 1.5.
