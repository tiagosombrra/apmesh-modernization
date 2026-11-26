# Test physical quality at the prospective front choice

[Draft PR 297](https://github.com/tiagosombrra/apmesh-modernization/pull/297)
at `0ad5b7bdf7af9504b739f0dc85172d832c3ea8f1` adds the certified
single-patch feedback option `trial_front_shape_floors`. The
article selector first uses its current UV rule and pair checks.
When that selection is a QUAD below a physical floor, the original
TRI for the same base is used only if it passes both existing
physical TRI floors. This occurs before the front update. The size
and closure logic sees the resulting selection as usual. A closure
preview uses the same local rule. The trace retains the rejected
QUAD and the initial TRI. The mode is opt-in and the existing
progressive profile still evaluates the completed candidate.

## Matched native comparison

| Measurement | CurvaBezier control → trial | Ribbed Bracket control → trial |
| --- | ---: | ---: |
| Initial TRI substituted for a QUAD | 0 → 4 | 0 → 0 |
| Below-floor faces at birth | 38 → 34 | 16 → 16 |
| Below-floor faces after smoothing | 35 → 31 | 12 → 12 |
| Below-floor QUAD with a contour edge after smoothing | 4 → 0 | 0 → 0 |
| TRI with a contour edge below the 30° regional target | 7 → 11 | 3 → 3 |
| Whole-mesh minimum angle after smoothing | 3.25° → 3.25° | 11.91° → 11.91° |
| Total faces | 731 → 735 | 541 → 541 |
| QUAD | 648 → 644 | 483 → 483 |
| Area-weighted RMS on the same 48 × 48 grid | 0.006621758 → 0.006621166 | 0.020102640 → 0.020102640 |
| Maximum sampled geometric deviation | 0.043991119 → 0.043991119 | 0.107484106 → 0.107484106 |

CurvaBezier diverges at operation 1 with the same incoming front.
The four replacements occur at operations 1, 5, 6 and 7. The
native result splits each original QUAD footprint into two TRI.
All other 727 faces keep exactly the same birth connectivity
and positions. No new below-floor face appears at birth.
The final TRI at the four affected contour edges have angles of
18.61° to 20.27°. They meet the 15° safety floor and remain below
the 30° regional target. The 11 contour-edge TRI below target
exceed the eight in the previous TRI reference, triggering the
unchanged regional count rule even though the minimum contour-edge
TRI angle stays at 16.42°. The original QUAD angle and shape
blockers in this region are cleared. The complete candidate is blocked.

Both possible diagonals were checked at the four affected footprints
in the original and final site positions. The selected diagonals
pass the local safety floors. The opposite diagonals give contour
TRI of about 12.53° to 13.63° at birth. Neither split at these
fixed four sites reaches the 30° edge TRI target. The Ribbed
enabled run has zero switches and reproduces its control mesh
and front trace byte for byte. Both trials preserve certified
contour sites, tree and request inputs, and all previously met
physical sizing requests. Zero mixed adaptive epochs are accepted.

## Validation and next action

The MSVC 19.44 x64 C++17 Debug application builds. The initial
combined command then fails because the existing application
build does not define the standalone front-contract target. The
standalone C++17 contract compiles and passes under UCRT GCC
16.1 with warnings treated as errors. The separately built MSVC
real-boundary contracts and the direct three-stage application
rollback pass. Each feature-off control matches 11 archived
files, and two malformed feature plans are refused. All 31
local Python controls pass. The local validation adapter reports
unavailable tools and a missing baseline manifest. Independent
review and full-stage qualification remain open.
[Exact evidence](evidence/FRONT_BIRTH_SHAPE_TRIAL_20261126.json).
[Exact-head CI](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45806459734).

Replay the four recorded CurvaBezier front states and inspect
which already-active vertices can attain the regional angle target
with the same contour edge and native front validity. If the
current sites are insufficient, use the result to locate the
responsible transition sizing or neighborhood constraint before
proposing a new selection rule. Keep the physical floors and
regional targets in force.
