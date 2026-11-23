# Shape-checked smoothing on the capped mixed feedback pilot

Recorded 2026-11-23 Fortaleza. One approved experimental replay of
[built-in curved Bezier feedback](MIXED_GEOMETRY_FEEDBACK_PILOT_20261122.md),
using the sizing requests and depth-4 limit of the capped attempt.
The [literature review](MIXED_ADAPTATION_LITERATURE_20261123.md)
motivates the local constraints on a Laplacian displacement. The
[numerical design](MIXED_SMOOTHING_SHAPE_DESIGN_20261122.md) supplies
the predeclared physical shape tests.

## Procedure and provenance

Build the MSVC Debug C++17 ap_mesh target from the isolated experiment
based on `94dc35a6c84899fb36eea86c1d352b0842ba3bcf`.
The [receipt](evidence/MIXED_SMOOTHING_PILOT_COMPARISON_20261123.json)
records the build and application arguments, source and artifact hashes,
pass ledger, independent checks and scope. The local audit also stores
p05/median/p95 per region and type for every retained frame.

The application runs once, exits zero in 32.69 s under 180 s and
reproduces all four capped request traces byte for byte. Seven feasible
leaf edits produce 88 balanced leaves from 67. Two face requests stay
at the cap. The eight original binary divisions retain all ten source
identities and produce 18 contour segments (four sides 7, 3, 4, 4,
previously 4, 2, 2, 2). Both smoothing arms start from the same valid
375-node geometry with 64 TRI and 333 QUAD. They keep the same faces
and those 18 segments fixed in UV and XYZ.

The control uses the existing fixed-contour Jacobi mean. The first pass
makes UV QUAD 315 concave, using zero-based article face numbering.
The independent replay reproduces a signed UV corner determinant
change from +0.001953125 to -0.00012723570024328606. The last valid
control frame is pass zero and equals the initial OBJ.

The guarded arm freezes the same mean destinations at the start of
each pass. It visits interior nodes in increasing order and tries
full, half, quarter and eighth moves, with analytic surface lift.
Each accepted move improves at least one incident worst shape score
and preserves the other worst scores within numerical tolerance.
Full native geometry checks run before smoothing and after each pass.
All five guarded passes pass the native checks. Independent tests
validate the analytic lift, connectivity, area, winding and contour
identity. They replay the shape scores and fractions of all 473
committed moves. There are 233 distinct positions changed in the
final frame. Typed output matches oriented faces and coordinates of
the guarded frame. Its source metadata retains the original 67
Step 2 leaves. The attempt ledger supplies the 88 candidate leaves.

## Result on the identical initial mesh

All angles are physical angles in degrees. Transition in this table
means a face with a contour vertex and no contour edge. Neighbor size
is the median physical edge length of each face. The ratio compares
sizes across a shared edge.

| Measure | Last valid control | Guarded pass 5 |
| --- | ---: | ---: |
| Worst TRI angle, contour edge | 9.83 | 13.50 |
| Worst TRI angle, transition | 4.10 | 5.09 |
| Worst TRI angle, interior | 16.23 | 18.67 |
| Worst QUAD angle, contour edge | 22.33 | 22.33 |
| Worst QUAD angle, transition | 63.00 | 66.31 |
| Worst QUAD angle, interior | 24.06 | 30.86 |
| Lowest TRI shape score q | 0.11994 | 0.13319 |
| Lowest QUAD corner scaled Jacobian | 0.37380 | 0.37380 |
| Highest QUAD longest/shortest edge ratio | 5.30064 | 4.52850 |
| Adjacent face size ratio, median | 1.05573 | 1.09897 |
| Adjacent face size ratio, p95 | 2.13186 | 1.89696 |
| Adjacent face size ratio, maximum | 4.36686 | 4.09981 |
| Maximum sampled XYZ deviation | 0.03768417 | 0.03768417 |
| Surface-area-weighted XYZ RMS deviation | 0.00665882 | 0.00627204 |

The error uses the same 576 UV sites and the analytic Bezier
surface in both arms. RMS is the square root of the weighted mean
of squared XYZ distances. The guarded arm reduces the area-weighted
RMS by 5.81%. The unchanged maximum, still-small transition angle
and increased median neighboring size ratio are retained. The
previous Step 2 mixed mesh has 301 faces and an area-weighted RMS
of 0.01289667 on these same sites. Its comparison to the 397-face
candidate includes both sizing and smoothing. These distances are
in model length units and do not measure global curvature error.

## Disposition and next action

The guarded run provides a valid experimental successor to measure.
The eight original reference OBJs and the curve trace match byte
for byte. Keep the original TRI path and all accepted reference
archives. The guarded treatment stays in the isolated trial and
has zero accepted mixed adaptive epochs. Hosted checks for PR247
refer to its separate graph candidate. This experiment covers one
model and does not qualify the full native/CRT/sanitizer matrix or
the mixed acceptance policy.

Next, audit the recorded requested and realized spacing of each
split contour interval and each requested face region on this
retained candidate. Compare physical sizes at the same locations
before and after reconstruction and relate discrepancies to the
existing ratio 1.35, binary curve splits and the depth cap. Keep
the request, legal discrete choice and resulting neighbor sizes
visible separately. Use that evidence to align the next numerical
sizing decision before changing any sizing or acceptance rule.
