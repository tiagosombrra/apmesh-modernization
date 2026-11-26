# Replay the affected contour bases and test three certified subdivisions

This comparison starts from the
[CurvaBezier front-floor trial](FRONT_BIRTH_SHAPE_TRIAL_20261126.md)
on [PR 297](https://github.com/tiagosombrra/apmesh-modernization/pull/297).
It binds the four contour operations to their archived active front,
quadtree boxes, exact birth vertices, and analytic surface. A
standalone MSVC probe uses the native selector and validity check;
its local header differs only in the access specifier. Each direct
choice reproduces the recorded initial TRI and original QUAD.
A reversed directed base is refused before emitting measurements.

## Existing sites and transition depth

| Operation | Active apex candidates | Native UV-valid | Also physically valid | Best physical minimum angle |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 115 | 22 | 4 | 18.96° |
| 5 | 114 | 14 | 9 | 20.90° |
| 6 | 114 | 11 | 11 | 19.21° |
| 7 | 114 | 7 | 7 | 19.94° |

All 457 candidates were measured. None reaches 30 degrees, even
before applying the validity screens. Enlarging the vertex search
alone cannot meet the target in these archived states. The four
existing native ideal-point offsets were inspected at each state.
On the short base at operation 1, the full offset is valid and
reaches 28.87 degrees. Its physical foot lies at 94 percent of
the chord despite using the UV midpoint.

At operations 5, 6, and 7, the contour chords are about 0.273 in
physical coordinates. A triangle with a 30-degree minimum needs
height at least `L tan(30°) / 2`, about 0.079 for those chords.
The native full offset is one UV leaf wide, reaches an exposed
template edge, and has physical height only 0.048 to 0.052.
This measures the near-interface constraint at that probe.
The smaller native offsets also miss the target.

## Single native comparison after alignment

The approved trial adds one native arc-length subdivision to each
of those three long original intervals, indices 3, 4, and 5. It
retains the short interval, the same physical front rule, and the
original admission profile. All 19 previous curve samples keep
their UV and physical coordinates. There are 22 certified samples
after the refinement. The 202 leaves, their boxes, the native
seed faces, the grouping journal, and the seven physical request
inputs match the control. No previously met size request is lost.

| Measurement | Front-floor control | Three certified subdivisions |
| --- | ---: | ---: |
| Certified contour segments | 19 | 22 |
| Faces | 735 | 732 |
| QUAD | 644 | 650 |
| Faces below a physical safety floor | 31 | 31 |
| Local contour faces across the three original bases | 3 TRI | 6 QUAD |
| Minimum angle range on those contour faces | 18.61°–20.27° | 33.13°–37.14° |
| Area-weighted RMS on the same 48 × 48 grid | 0.006621166 | 0.006619929 |
| Maximum sampled geometric deviation | 0.043991119 | 0.043991119 |

The six new contour QUAD meet their physical safety floors
and remain below the 45-degree QUAD regional angle target. The
count of contour TRI below 30 degrees falls from 11 to eight,
matching the predecessor count and clearing its block. The count
of contour QUAD below 45 degrees rises from four to ten, exceeding
the predecessor's six and triggering a regional regression block.
The short base stays at 18.96 degrees. The full candidate remains
blocked, with zero accepted mixed adaptive epochs.

## Verification and next step

The native probe builds with MSVC C++17 and `/W4 /WX`. The initial
observer stopped on a UV-valid face with an inverted physical
corner. The corrected observer records such candidates as physical
refusals and completes all four archives. The single approved
native split runs on the existing PR 297 image and passes its
curve certificate. No production source changes in this comparison.
All four exact-head checks on PR 297 pass.
[Probe and split receipts](evidence/CONTOUR_BIRTH_REPLAY_AND_SPLIT_20261126.json).
[Exact-head CI](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45806459734).

Inspect the six split-base native QUAD choices at their creation.
Check whether any alternative using the existing sites and the
same UV rule can reach 45 degrees with native front validity.
Use that result to choose between pair selection and local
transition placement before another change to the discretization.
