# Trace the persistent TRI on the straight side of the grouped control

The replay binds the 16 failing CurvaBezier TRI with a vertex on
`v = 1` to the exact native archives of the
[707-face grouped candidate](NATIVE_SPLIT_CONTOUR_GROUPING_20261126.md).
The grouped contour, accepted source capture, requested sizes,
and grouped quadtree remain fixed. This comparison measures
the states in which the TRI originate.

## Birth and source sizes

| Measurement | Observed value |
| --- | ---: |
| TRI failing at birth and after smoothing | 16 |
| Minimum-angle range at birth | 2.53°–12.46° |
| Minimum-angle range after smoothing | 3.25°–12.47° |
| TRI with an exposed template edge | 16 |
| Operations using that exposed edge as their native base | 15 |
| TRI sharing the same central curve point | 12 |
| Points on the straight certified side | 3 |
| Physical length of each existing straight-side segment | 1.0 |
| Physical length of the corresponding template edges | 0.06516–0.12574 |
| Incident curve length divided by template edge length | 7.95–15.35 |

The curve endpoints and central sample lie on the same straight
physical side. These numbers diagnose a size mismatch even on a
straight source curve. Each triangle connects an exposed edge of the
template interface to one of the three samples. The 12-triangle
cluster attaches to the central sample. Neither curvature of the
side nor smoothing is needed to explain why the failure is already
present when these native triangles are created.

## Alternatives in the same native front states

The MSVC probe changes access to the replayed header without changing
the native selector or validity logic. The archived initial TRI,
their direct pair decisions and the directed base reproduce in
all 16 operations. A reversed-base negative control is refused.

Across 817 active-site checks, each of the 16 bases has exactly
one native-valid apex. It is always the one selected in the archive.
The 13 other QUAD constructions with native-valid TRI decompositions
fail the article UV shape rule. Broader vertex search and a different
ranking of the existing candidates therefore leave these archived
decisions unchanged.

The native ideal-point offsets yield a valid first TRI above
the physical floor in 12 operations. Four operations have no
passing initial face from those offsets. The first-face measurements
do not determine whether adding any of these points would produce
a complete acceptable remainder of the front.

## Verification and next action

The standalone C++17 probe builds under MSVC with warnings treated
as errors. The source, candidate, ordered certificate and archived
birth layout match the grouped inputs. All four
[exact-head PR 297 checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45806459734)
pass. The local validation adapter has unavailable tools and no
baseline manifest. This replay changes no production source or
native admission rule.
[Exact measurement and probe receipts](evidence/PERSISTENT_STRAIGHT_SIDE_TRI_20261126.json).

The proposed native comparison splits each of the two straight-side
intervals once with the existing arc-length subdivision. The other
curve sides, contour parent operations, and quality and error profile
remain fixed. Compare the six protected improved QUAD and the
persistent TRI in the full output before broadening the experiment.
