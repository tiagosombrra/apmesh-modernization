# Additional local TRI pairs in the mixed advancing front

2026-11-25 Fortaleza. [Draft PR 275](https://github.com/tiagosombrra/apmesh-modernization/pull/275)
head `779ac3437a7ab7099dda3d26c8deb478892dc922`.
[Machine-readable receipt](evidence/ADDITIONAL_LOCAL_PAIRS_20261125.json).

## Controlled experiment

With the approved option enabled, the existing selection runs first. When
it resolves to a triangle, examine the remaining apex and companion pairs in
the same local search. Choose the lowest score among eligible quadrilaterals
at S <= 1.5, with exact ties resolved by existing vertex order, side, and
companion order. With no eligible pair, keep the original triangle. The
native standalone feedback application exposes the option through a verified
predecessor plan. Normal generation keeps the original selection. The option
changes advancing-front selection in the experimental run.

Both arms use the same Windows MSVC Debug C++17 executable, CurvaBezier
predecessor, size requests, contour records, ordered leaf tree and template
cycles. Both apply the same guarded smoothing rules. Each uses one direct
leaf edit, 226 resulting leaves, and 16 contour segments. The control front
reproduces the [archived native trace](GUARDED_INTERIOR_FRONT_TRACE_20261125.md)
byte for byte. The first difference occurs at operation 13. That operation
adds the only replacement QUAD, with the predicted vertices and S = 1.50.
Independent replay validates 111 experimental operations and rejects a
forged score. The limiting interior TRI from operation 83 is absent.

## Physical mesh after guarded smoothing

| Metric | Control | Additional pairs |
| --- | ---: | ---: |
| Nodes | 737 | 737 |
| TRI / QUAD / total faces | 104 / 676 / 780 | 102 / 677 / 779 |
| Minimum interior TRI angle | 8.04 degrees | 14.36 degrees |
| Minimum interior TRI shape | 0.22575 | 0.37719 |
| Minimum interior QUAD angle | 50.86 degrees | 44.57 degrees |
| Minimum interior QUAD scaled corner Jacobian | 0.71806 | 0.69133 |
| Minimum contour-vertex-only TRI angle | 2.27 degrees | 2.27 degrees |
| Minimum contour-edge QUAD angle | 19.44 degrees | 19.44 degrees |
| Sampled surface deviation RMS | 0.00907325 | 0.00907903 |
| Maximum sampled surface deviation | 0.04419218 | 0.04419218 |
| Largest measured adjacent size ratio | 8.92960 | 8.92960 |

Surface deviation uses the same 2,304 UV sites and is measured in model
units. The RMS increase is about 0.064 percent. The limiting interior QUAD
has identical vertices and birth coordinates in both arms, with a birth
angle of 41.30 degrees. The altered adjacency changes the smoothing outcome
for this face. The new limiting interior TRI also exists in the control,
and its individual final angle decreases from 17.43 to 14.36 degrees.
The regional TRI minimum rises because the former limiting face is absent.
Both arms still record a rejected first unguarded smoothing pass and five
guarded passes. The predecessor-derived quality profile still blocks the
experimental candidate on minimum interior TRI angle and shape. That
profile remains an assessment control. Accepted mixed adaptive epochs: zero.

## Verification and next comparison

The build, ordinary native article regression, six real boundary source
captures and 54 negative controls, 39 focused Python tests, and the directed
portable native suite pass locally. The suite checks default CurvaBezier
and Ribbed Bracket runs, the relative no-action path, malformed tree input,
and replay of the experimental CurvaBezier geometry on the same executable.
The first control wrapper failed before execution on a log-name collision.
The next invocation completed the native process, then its Python check
failed on a stale artifact path. A separate readback verified the completed
artifacts against the immutable archive. Both wrapper failures are retained
in the receipt. Hosted check status is recorded in the receipt.

A read-only scan of 74 TRI fallbacks from the independent native Ribbed
Bracket archive finds eligible alternative pairs at operations 1, 3 and 61.
These are opportunities in the original front. An earlier replacement can
change the later front and therefore the final counts. The next comparison
is a single paired native Ribbed run with this same option and no recalibration,
after scope alignment. Measure birth and post-smoothing quality by region,
surface deviation, growth, and the exact boundary and tree replay. Retain
the reserved-model, shared-curve and two-epoch checks before broader adoption.
