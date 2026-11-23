# Guarded smoothing on ordinary mixed Step 2 of Ribbed Bracket

Recorded 2026-11-23 Fortaleza. One approved comparison that addresses
the [failure in the second geometry](MIXED_SIZING_CROSS_CASE_20261123.md).
The [receipt](evidence/RIBBED_MIXED_STEP2_SMOOTHING_20261123.json)
binds the source snapshot, executable, fixture, native command,
frames and independent diagnostics.

Build the isolated MSVC Debug C++17 target. Route the first accepted
ordinary opt-in Step 2 to the same paired smoothing comparison used
by the [original capped pilot](MIXED_SMOOTHING_PILOT_COMPARISON_20261123.md).
Both arms share the real native tree output, area-centroid templates,
mixed advancing front, and 14 fixed source boundary segments on
the single zero-based patch 12. The initial mesh passes native
geometry checks and has 525 nodes, 60 TRI and 487 QUAD.

The control reproduces the original diagnostic on its first pass,
UV QUAD 483. A replay from the identical geometry confirms at
least one corner determinant changes from positive to negative.
The failing corner goes from 0.0078125 to -0.0004359422284843789.
Pass zero is therefore the last valid control. The guarded arm
completes five valid passes, with 303 committed displacements
independently checked against their fractions and neighborhood
shape scores. The typed OBJ matches the final oriented topology
and physical positions and keeps the native contour sites.

| Observation | Last valid control | Guarded pass 5 |
| --- | ---: | ---: |
| Minimum TRI angle (degrees) | 3.79134 | 3.79134 |
| Minimum QUAD angle (degrees) | 26.18180 | 26.18180 |
| Minimum TRI shape q | 0.11387 | 0.11387 |
| Minimum QUAD corner scaled Jacobian | 0.32484 | 0.32484 |
| Adjacent face size ratio p95 | 2.55659 | 2.59502 |
| Maximum adjacent face size ratio | 6.42755 | 6.18678 |
| Area-weighted sampled XYZ RMS | 0.02761938 | 0.02738423 |
| Maximum sampled XYZ deviation | 0.12330782 | 0.12330782 |

The same 576 UV sites evaluate both geometric deviations, in model
length units. Guarded smoothing reduces geometric RMS by about
0.85 percent. The maximum size contrast improves and the 95th
percentile worsens slightly. The worst TRI and QUAD keep their
original shape metrics. Smoothing is a useful safeguard here and
leaves the worst transition element in place.

The limiting TRI is already present before smoothing. Its three
UV/XYZ positions remain exactly fixed by the accepted moves. It
links one contour vertex at (0.5, 1) to a short edge. That edge
is 0.12501 in XYZ, while the other edges measure 1.44359 and
1.35972. Its neighbor across the short edge is a QUAD whose
median physical edge length is smaller by a factor of 4.18. The
two contour segments incident to the TRI's contour vertex each
have physical chord 2.0. These measurements locate a discrete
front/template/contour size mismatch. They do not establish that
an extra curve split by itself improves it.

## Scope and next action

The build exits zero in 7.53 s and one native comparison exits
zero in 14.15 s within its 180 s limit. All five previously
retained ordinary OBJ files and the manifest prefix match byte
for byte, including the TRI Step 2 reference. Exit zero records
a valid, isolated comparison. The application deliberately stops
after the guarded typed observation, before publishing a normal
final mesh or performing the downstream feedback pass. The full
native, CRT, sanitizer and hosted matrices do not qualify this
trial. No mixed epoch was accepted. Global mixed curvature
error remains open.

Next, evaluate the existing mixed residual and typed neighbor
requests on this valid predecessor as well as on the original
Bezier predecessor. Check whether the current targeting reaches
the 3.79-degree pocket or leaves a gap like the 5.09-degree
pocket in the original case. Match requested physical sizes to
the curve blocks and native leaf actions, and use the measurements
to align one local conversion proposal before generating its
candidate. Compare the pocket and its neighbors as well as whole
mesh shape, geometric deviation and counts. Keep the original
TRI workflow and the curve, quadtree, templates and advancing
front as reconstruction primitives.
