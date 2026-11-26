# Replay QUAD choices on the six certified split bases

This replay binds the six contour bases from the
[certified curve split trial](CONTOUR_BIRTH_REPLAY_AND_SPLIT_20261126.md)
to the exact native birth coordinates, directed active front and
leaf boxes. The MSVC probe uses the native `Choose`, `Best`,
`Valid` and `Shape` functions. The probe header changes only the
access specifier. It reproduces all six chosen faces and their two
direct proposals. A reversed base is refused before measurement.

| Native operation | Distinct pairs with valid triangle decompositions | Pass native UV rule and physical validity | Chosen physical minimum angle | Best eligible physical minimum angle |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 27 | 3 | 37.14° | 37.14° |
| 6 | 21 | 3 | 35.20° | 35.20° |
| 7 | 17 | 3 | 33.74° | 33.74° |
| 8 | 15 | 3 | 33.17° | 33.17° |
| 9 | 12 | 3 | 33.13° | 33.19° |
| 10 | 10 | 3 | 33.46° | 36.34° |

The exhaustive active-site pairing gives 102 distinct
operation/pair records. Eighteen pass the native `S <= 1.5` rule
and the physical corner validity check. All 18 already lie in
the native initial and companion neighborhoods. None reaches
the 45-degree angle target. Ranking the current sites by physical
angle would change at most the last two of these local decisions
and would leave the new QUAD under the regional angle target.

## Template interface geometry

All 18 eligible faces have an opposite edge on the exposed
template interface at `v = 0.0625`. Its physical length is
0.49 to 0.51 times the certified contour base. Combining two
contiguous template sides at the same depth gives one local
geometric witness per base, with angles between 84.72 and
88.74 degrees. Each such witness would skip the intervening
active template vertex, so it is a geometry probe outside
the current native front validity.

An independent template projection matches all 631 original
seed QUAD. It then tests the three nearest four-sibling parents
in all seven nonempty combinations with the certified contour
fixed. Every combination preserves 2:1 and avoids the existing
physical requests. The joint projection moves the exposed
interface to `v = 0.125` and gives 193 leaves and 607 seed
QUAD. Each of the six bases has two possible locally eligible
projected faces. All 64 combinations of those options have
disjoint interiors and avoid the projected seed faces. The
best combination has individual minima from 56.38 to 66.83
degrees. This verifies compatibility of the six footprints.
It leaves native front ordering, closure of the remaining
area, smoothing and full-profile admission to native testing.

## Verification and next step

The exact archive, opposite-edge incidence, original template
projection and all four hosted checks of PR 297 were verified.
The local validation adapter reports unavailable tools and
a missing baseline. The standalone C++17 MSVC probe builds
with warnings treated as errors. The initial placement observer
passed curve sites where the projection expected directed edges.
The corrected invocation matches the native seed and completes
all placement and overlap checks.
[Replay and projection evidence](evidence/SPLIT_CONTOUR_PAIR_REPLAY_20261126.json).

The proposed native comparison uses only the three existing
contour parent group operations. Hold the 22 certified
curve sites, front selection and acceptance profile fixed.
Check the same six bases, adjacent transition regions, total
faces, preserved size requests and geometric error.
