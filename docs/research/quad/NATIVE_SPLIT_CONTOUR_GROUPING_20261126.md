# Run three contour parent groups on the certified split curve

The approved native trial applies the three parent groups from
the [split-base projection](SPLIT_CONTOUR_PAIR_REPLAY_20261126.md)
to the [732-face CurvaBezier control](CONTOUR_BIRTH_REPLAY_AND_SPLIT_20261126.md).
It uses the exact research image for
[PR 297](https://github.com/tiagosombrra/apmesh-modernization/pull/297)
at `0ad5b7bdf7af9504b739f0dc85172d832c3ea8f1`. The only plan
additions are the existing contour parent operations on
`[0.375, 0, 0.5, 0.125]`, `[0.5, 0, 0.625, 0.125]`,
and `[0.625, 0, 0.75, 0.125]`. The front rule, sizing requests,
curve certification, and full admission profile still apply.

## Matched native results

| Measurement | Certified split control | Three contour groups |
| --- | ---: | ---: |
| Ordered original-curve samples | 22 | 22 |
| Native tree leaves | 202 | 193 |
| Seed QUAD | 631 | 607 |
| Total faces | 732 | 707 |
| TRI | 82 | 80 |
| QUAD | 650 | 627 |
| Minimum angle range at the six targeted contour QUAD | 33.13°–37.14° | 48.93°–63.34° |
| Contour-edge QUAD below the 45° regional angle target | 10 | 5 |
| Interior QUAD below their 45° regional angle target | 6 | 8 |
| Faces below a physical safety floor | 31 | 31 |
| Area-weighted RMS on the same 48 × 48 grid | 0.006619929 | 0.006674683 |
| Maximum sampled geometric deviation | 0.043991119 | 0.043991119 |

The native leaf boxes and seed faces match the grouping projection.
Five of the six chosen faces match its local candidate footprints.
The full native front closes and the six targeted faces meet the
45-degree angle target after smoothing. All 22 ordered curve
samples retain their parameter, UV, physical coordinates and
node ID. Physical request inputs match byte for byte, and all
seven physical size measurements match the control. The contour-edge
QUAD angle count block clears. The trial introduces no new
full-profile blocker. The sampled RMS increases by about 0.83 percent.

## Remaining shape limits

The same 31 birth footprints are below a physical floor in both
final meshes. Thirty are TRI touching the contour by a vertex
only, and one is an interior TRI. Sixteen of the boundary TRI have
a vertex on `v = 1`. Corner faces can contribute to two sides.
The interior TRI remains at 12.07 degrees.

The existing interior QUAD angular block persists. Two additional
interior QUAD fall below the regional angle target near the
`u = 0.375` end of the modified strip. One is a template face and
one comes from the front. The worst interior QUAD has identical
birth geometry in both runs and starts at 28.98 degrees. The
guarded control reaches 40.38 degrees after smoothing. The
grouped run reaches 31.64 degrees, with the difference visible
in the first guarded pass. Both outcomes pass the physical floor
and fall below the regional angle target.

## Verification and next action

The single native attempt stages, verifies the curve certificate and
replays the original TRI source binding. No production source changes
are part of this comparison. The local profile adapter reports required
tools unavailable and no baseline manifest. The four exact-head
checks on PR 297 pass. Full-stage qualification remains open.
[Native result, request and smoothing receipts](evidence/NATIVE_SPLIT_CONTOUR_GROUPING_20261126.json).

Retain this fixed-contour grouping as the development control for
the six targeted bases. Start with the 16 persistent TRI touching
`v = 1`. Map their birth operations to the corresponding contour
and exposed template edges, and check whether their physical size
ratios or the active-front choices explain the safety-floor defects
before aligning a new intervention. Retain the interior QUAD angle
block, shared curves, owner reentry, reserved cases and global mixed
curvature in the remaining scope. Zero mixed epochs are accepted.
