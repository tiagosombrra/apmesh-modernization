# Test two arc-length splits on the straight side of the grouped mesh

The approved run retains the
[707-face grouped control](NATIVE_SPLIT_CONTOUR_GROUPING_20261126.md)
and appends one native arc-length split to each of the straight-side
source intervals 10 and 11. The trial uses the verified MSVC C++17
research image for [PR 297](https://github.com/tiagosombrra/apmesh-modernization/pull/297)
at `0ad5b7bdf7af9504b739f0dc85172d832c3ea8f1`. All earlier
contour groups, sizing requests, selection logic, and the named
admission profile remain in force.

## Matched native measurements

| Measurement | Grouped control | Two straight-side splits |
| --- | ---: | ---: |
| Certified contour samples | 22 | 24 |
| Native leaf boxes | 193 | 193 |
| Seed QUAD | 607 | 639 |
| Total faces | 707 | 743 |
| Total QUAD | 627 | 661 |
| Total TRI | 80 | 82 |
| Below-floor TRI incident to the straight side | 16 | 8 |
| Faces below any physical safety floor | 31 | 23 |
| Minimum angle at the six earlier corrected contour QUAD | 48.93°–63.34° | 48.93°–63.34° |
| Contour-edge QUAD below the 45° target | 5 | 7 |
| Area-weighted RMS on the same 48 × 48 grid | 0.006674683 | 0.003674192 |
| Maximum sampled geometric deviation | 0.043991119 | 0.018789543 |

Each unit-length segment becomes two segments of approximately
0.5. The original 22 samples retain their parametric and physical
positions. All original source node IDs are certified and unchanged.
Two earlier inserted samples on side 3 receive different IDs when
the new samples are allocated. The added sites are on `v = 1`.
The physical requests and all seven size measurements match exactly.
The six previously improved QUAD retain their individual angles.
The sampled RMS falls 44.95 percent and the sampled maximum falls
57.29 percent relative to the grouped control.

The leaf boxes and grouping journal match byte for byte. The
existing UV clearance rule admits eight previously excluded
leaves in the nearby row and adds 32 seed QUAD. This accounts
for 32 of the 36 additional faces. The seed projection reproduces
both native layouts and locates the added row between
`v = 0.875` and `v = 0.9375`.

All 16 previous failing straight-side footprints disappear.
Eight new below-angle-floor TRI at that side form the residual
group: four at its old central sample and two at each new sample.
The other 15 below-floor footprints persist. The contour-vertex
TRI shape-floor block clears, and the angle-floor block remains.
The interior TRI and interior QUAD angle blocks remain. The
complete 743-face mesh stays blocked under the frozen profile.
Zero mixed adaptive epochs are accepted.

## Two contour QUAD restore the regional count block

The two outer straight-side child intervals now carry QUAD with
physical minimum angles of 44.95627 and 44.96744 degrees. They
pass the 22.5-degree physical floor and miss the separate
45-degree regional target. The native predecessor has six
contour-edge QUAD below target. The trial has seven, up from
five in the grouped control. This count restores the contour-edge
regional block even though the six earlier corrected edges remain
above target. The two new angles and scaled Jacobians are fixed
from birth through all five guarded passes.

The MSVC replay reproduces operations 17 and 20. They select
additional pairs with `S = 1.5` and local relative residuals below
the original 0.045 limit. The probe enumerates 37 and 12 valid
triangle-pair constructions on the existing active sites. The
chosen QUAD is the only article-eligible option in each operation.
The exact archived pair residuals reproduce. Both diagonals in
either fixed footprint give a contour TRI above its 30-degree
target and a second TRI below its 15-degree safety floor.
Their second-face angles range from 12.46 to 14.75 degrees.

## Verification and next action

The native attempt, curve certificate, regional and clearance
audits, guarded-pass measurements, and existing-site replay
complete. All four exact-head PR 297 checks pass. The local
validation adapter is missing required tools and a baseline
manifest. This comparison changes no production code or cutoff.
[Native and replay receipts](evidence/NATIVE_STRAIGHT_SIDE_SPLIT_20261126.json).

Use the 24-sample run as the next development control. Project
the smallest change to an existing interior site that can bring
either corner QUAD to 45 degrees with the contour fixed. Check
every affected neighbor and the current shape, size, and geometry
contracts. Record feasibility before any native placement change.
The eight residual straight-side TRI and independent full-profile
validation remain open.
