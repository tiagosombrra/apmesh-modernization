# Surface-informed curve spacing and mixed element quality

20 November 2026, Fortaleza. This work follows the [single legacy bounds comparison](LEGACY_BOUNDS_COMPARISON_20261120.md). The objective is a usable mixed mesh with acceptable physical shape at the contour, in the transition and in the interior, while retaining the original generator. The [numeric receipt](evidence/SURFACE_CURVE_SPACING_QUALITY_TRACE_20261120.json) holds the source identities and detailed measurements.

## Where the curve growth occurs

The isolated MSVC Debug observer at source `c93a383e2775d33eb8a7e5f28cbc410e3d98593d` reran the existing legacy-bound configuration with a different output path. Only trace reads were inserted in the adapter and its research call site. The application completed in 47.94 seconds within the existing 180-second limit. All eight TRI/mixed OBJ files, the manifest, the curve-stage trace and both pair CSV files match the original run byte for byte. The last accepted mixed output is also byte-identical. Step 2 and 3 remain TRI source rejections at 112 contour intervals and 953 mixed nodes. That parity validates the observer on this replay and leaves the previously retained application and its policy intact.

At Step 2, the surface-informed pass consumes 28 intervals across the four curve sides. Both endpoint discrete curvatures were zero in all 28 intervals. The native analytical value at the midpoint was nonzero in every case. The algorithm chose Gaussian curvature on the curved side and on straight side 3, and mean curvature on straight sides 1 and 2. The same effective curvature factor `2.828427124` and curve factor `0.84` leave the requested length at `29.6985%` of the previous interval length on every side. Different physical lengths still yield different requests.

| Side | Points into surface pass | Points before neighbor restriction | Points after | Requested physical length, median | Adjacent native face-size proxy, median |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0, curved | 17 | 65 | 65 | 0.04066 | 0.05518 |
| 1, straight | 5 | 17 | 17 | 0.14849 | 0.06532 |
| 2, straight | 5 | 17 | 17 | 0.14849 | 0.06787 |
| 3, straight | 5 | 17 | 17 | 0.14849 | 0.08858 |

The two lists of curve parameters are equal before and after `BinTree::Restrict` on all four Step 2 sides. Subdivision requests, rather than the neighbor restriction, account for the `17→65` and `5→17` jumps. This is an observed distinction for this case. The adjacent-domain column uses the 104 faces of the previously accepted TRI patch. The audit identified overlapping intervals on their contour edges and used the existing smoothed target `h` multiplied by the square root of the prior patch area to express its length scale. It is a proxy for the native sizing request, not a measurement of the resulting face edges. The curved side asks for a smaller physical size than its adjacent domain proxy. The straight sides ask for larger sizes. A universal multiplier leaves these two situations unresolved.

The initial observer captured values consumed after the curve-only pass. A second read-only observation inserted a snapshot immediately before that pass, while the accepted TRI patch and curve lists both existed. The replay completed in 44.71 seconds with identical output hashes and identical interval and domain trace rows. All 63 accepted TRI node identities and XYZ coordinates match the previous Step 1 archive. Each of the 20 unique contour sites (24 side incidences, including shared corners) matches an accepted TRI node by ID and XYZ. Every matched TRI node carries a finite, nonzero discrete `Gd` or `Hd`. On the curve instances, both channels are already zero at all 20 sites before the curve-only pass. At parameter `0.128500796854496` on side 0, node ID 9 has accepted TRI `Gd=-13.1012304` and `Hd=3.2148080`, and the matched curve node holds `0,0`. This locates the observed loss at the handoff between the accepted patch and the independent curve samples before the rebuild. Source inspection also shows that `BuildCurveSamples` constructs fresh interior samples by position with zero-initialized curvature, so preserving coincident sites alone would leave new sites uncovered. Zero is a legitimate numerical value if it comes from the measured source.

## What angles reveal about element quality

The archive audit evaluates physical minimum and maximum angles and longest/shortest edge ratio for every mixed face. TRI additionally uses the normalized area-to-edge quality `q`, and QUAD uses the signed corner scaled Jacobian `J` computed with the source normal. Values near one are preferable within each shape metric. A triangle close to collinear has a very small angle and a low area score. An ideal right-angle QUAD can still be very long and thin, so edge ratio stays alongside the angle and Jacobian. Positive sampled corner measures screen observed corners and do not certify the complete curved mapping.

The 6,206 observations cover both profiles, Steps 1–3 and both phases of smoothing. Distinguish contour-edge faces, faces touching the contour at vertices only and interior faces, and keep TRI and QUAD separate. Preserve the worst IDs and the lower and upper tails rather than relying on one aggregate average. The table highlights the fixed `1.5` and legacy Step 2 cases.

| Step 2 region and kind | Fixed 1.5 worst angle before → after | Fixed 1.5 minimum shape score before → after | Legacy after, rejected source |
| --- | ---: | ---: | ---: |
| Contour-edge QUAD | 23.28° → 15.64° | J 0.394 → 0.224 | 38.43°, J 0.389 |
| Contour-edge TRI | 9.83° → 16.00° | q 0.288 → 0.346 | 13.66°, q 0.385 |
| Vertex-only TRI | 4.82° → 9.59° | q 0.135 → 0.272 | 38.34°, q 0.836 |

The fixed profile's worst contour QUAD maximum angle also rises to `164.77°`, and its worst edge ratio stays `8.48` after smoothing. Some TRI groups improve as QUAD groups lose shape. The rejected legacy Step 2 has better values in several groups, yet the worst contour TRI angle drops compared with the fixed candidate and the original acceptance rejects the attempt. The archived fixed Step 3 reaches `1.87°` in a vertex-only TRI. A positive application exit, a valid contour and an accepted TRI source therefore leave mixed element quality work outstanding.

## Next action and quality evidence for a correction

Propose one opt-in single-patch replay of the Step 1 → 2 handoff. Capture value records for the preceding accepted TRI contour keyed by curve identity and oriented parameter, and validate identity and position at the corresponding original sites. Read the accepted `Gd/Hd` exactly where parameter sites match. At a genuinely new site, linearly interpolate each signed channel between the enclosing accepted parameters on the same curve side. Restrict the experiment to the bracketed single-patch case. Reject an experimental input with missing provenance or an unbracketed site before comparing results. Preserve the initial step and the two existing size formulas. This is a proposed source of the input values, with no new estimator, error cutoff or policy. Interpolating coarse accepted values can retain or mix curvature errors, especially near corners. Better spacing and quality remain empirical questions. Explicit scientific adoption is required before implementation or execution.

Compare a future corrected candidate to the fixed `1.5` and legacy references with the same geometric/topological checks, curve and domain traces, growth and TRI acceptance. Include the per-region shape table before and after smoothing and the final mixed mesh's worst elements. Review losses as well as gains, with mixed global error kept separate. This is a reporting requirement on the result, without new scalar acceptance thresholds. No production code change, mixed acceptance decision or new sizing policy is claimed in this checkpoint.
