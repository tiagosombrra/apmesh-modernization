# Common relative tolerance comparison on the development cases

2026-11-25 Fortaleza. The exact [draft PR 272](https://github.com/tiagosombrra/apmesh-modernization/pull/272)
head `7d17c5d368b179e903665ba1658637c2a6c76d42` has four successful
[hosted jobs](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45585487055).
[Machine-readable receipt](evidence/COMMON_RELATIVE_CALIBRATION_20261125.json).

## Complete development comparison for the current seed rule

With a fixed input, the active seeds change only when the common tolerance
reaches that input's maximum TRI or QUAD relative residual. The strict
greater-than rule places the exact endpoint in the interval above it.
The two inputs therefore have five joint intervals, with fixed requests
within each. Recheck complete face sites and sizes and ordered curve
interval requests to link each interval to a measured mesh.

| Common tolerance interval, rounded | CurvaBezier Step 3 | Ribbed Bracket patch 12 Step 2 |
| --- | --- | --- |
| [0, 0.034342) | Both seeds | Both seeds |
| [0.034342, 0.060309) | TRI seed | Both seeds |
| [0.060309, 0.064942) | TRI seed | QUAD seed |
| [0.064942, 0.094719) | No requests | QUAD seed |
| [0.094719, infinity) | No requests | No requests |

The receipt retains the exact endpoints. In this table, no requests
means the predecessor remains in place. Numeric replays verify the
no-action intervals. Prior native Ribbed at tolerance 1 separately
demonstrated the no-action application path.
The single missing active regime was a native Ribbed trial at the
recorded TRI breakpoint 0.06030906936233993, leaving the QUAD seed active.
The exact MSVC image from the previous trials staged that successor.
It reproduced the original TRI, mixed predecessor and tree witness.
It sent seven face and five curve requests, with one capped request
and three distinct leaf edits. The tree grew from 112 to 121 leaves
and the contour from 14 to 19 segments. The unguarded smoother rejects
at pass one on face 528. Five guarded passes complete.

## Physical and regional tradeoffs

RMS and maximum geometric distance use the same 2,304 UV sites for each
paired comparison. Element counts, angle, TRI quality and QUAD scaled
corner Jacobian are reported from the native typed meshes and their
own underlying analytic surface. Values are in model units for distance
and degrees for angle. Groups are by contour-edge incidence,
contour-vertex-only incidence or interior.

| Geometry and seeds | Final faces | Face growth | Geometric RMS reduction | Minimum contour-edge QUAD | Minimum interior QUAD | Minimum interior TRI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CurvaBezier input | 732 | 0 | 0 | 19.44 | 64.41 | absent |
| CurvaBezier both | 796 | 8.7% | 32.3% | 18.57 | 27.63 | 8.04 |
| CurvaBezier TRI | 780 | 6.6% | 23.8% | 19.44 | 50.86 | 8.04 |
| Ribbed input | 547 | 0 | 0 | 26.18 | 26.45 | 26.57 |
| Ribbed both | 648 | 18.5% | 36.8% | 25.34 | 26.71 | 18.37 |
| Ribbed QUAD | 604 | 10.4% | 13.0% | 25.34 | 26.45 | 18.37 |

Both selective candidates reduce the sampled maximum distance and
maximum adjacent size ratio versus their respective mixed source.
Ribbed QUAD-only changes the RMS from 0.02748807 to 0.02390935 and the
maximum sampled distance from 0.12561818 to 0.12408875.
Its contour-edge QUAD minimum angle drops from 26.18 to 25.34.
The minimum scaled corner Jacobian for that group rises from 0.41805
to 0.42054. The two measurements can disagree. A previously absent
face class is recorded and has no predecessor minimum for a direct
comparison. For each active regime at least one comparable regional
angle or shape minimum worsens. Under a strict veto on any worse
regional minimum, none of the active variants would be admitted.

## Scientific gate

A common selective interval is observed on the two development
inputs. The interval is evidence about these two inputs only.
It is a useful operating point for an aligned admission study.
Quality policy choices are an absolute per-kind/per-region floor
with improvement for regions already below it, or a strict relative
regional-minimum veto. An admission policy also needs a growth
budget and a decision for new type/region classes. Before reserving
runs, specify those checks independently of candidate outcomes and
fix the tolerance for all held-out cases. The two-model comparison
adopts no floor, tolerance, growth cap or acceptance decision.
Shared-curve generation, owned mixed successor reentry, global mixed
curvature and accepted mixed epochs remain open.

The first archive matching script compared native tuples with JSON
arrays and stopped. The corrected script matches complete normalized
records without relaxing any numerical check. Both logs and the sole
new native run are bound in the receipt. Production and experimental
source were unchanged for this comparison.
