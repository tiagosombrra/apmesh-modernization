# Pre-front sizing comparison with a transition TRI target

Recorded 2026-11-23 Fortaleza. The researcher approves one paired
Ribbed Bracket comparison. The [receipt](evidence/RIBBED_PREFRONT_SHAPE_TARGET_20261123.json)
binds the isolated source, MSVC Debug C++17 image, all request and
geometry files, predecessor and negative outcomes.

## Paired scope and verification

Start both arms from the identical, previously
[validated guarded Step 2](RIBBED_MIXED_STEP2_SMOOTHING_20261123.md):
525 nodes, 547 faces and 14 original curve intervals. Control seeds
are the largest geometric residual on a TRI and on a QUAD. The
augmented arm adds the physical minimum-angle TRI with exactly one
contour vertex, face 522 at 3.79 degrees. The original two seeds,
halving rule, three propagation passes at ratio 1.35, one depth
increment for eligible leaves, and single native binary split per
marked curve interval are unchanged. Use the same depth cap 4,
templates, 1993-style selection and guarded smoothing in both arms.
The ordinary original TRI output stays separate.

The read-only replay predicts 17 versus 21 face requests with the
same eight contour marks in Ribbed. It predicts 13 versus 19 face
requests and 9 versus 12 curve marks in the built-in Bezier control,
which is not generated in the native comparison. Five of eight
Ribbed curve requests in both arms are below half their original
arc length. Full idealized binary fulfillment would add 18 contour
points instead of eight, before any additional conformity costs;
this calculation uses equal halves and was not implemented.
Preserve the initially failed archive comparison between UV
tuples and serialized lists, then normalize through JSON and
reproduce the original read-only targets.

The native build exits zero in 11.82 s. One application with
both arms exits zero in 63.22 s under 180 s. Independent comparisons
match all requested face sizes and original interval split masks
to the replay. The typed predecessor, five ordinary prefix
OBJs and prefix manifest match their references. Both arms produce
22 original-curve segments with identical source rows in UV,
XYZ and identity. Each logs a request stopped by the depth cap
at leaf 87. The augmented arm splits one additional eligible leaf
(ID 65), yielding 136 instead of 133 balanced leaves. Both initial
candidates are valid. In both arms the unguarded smoothing control
fails on pass one (UV QUAD 562 and 570 respectively). All five
guarded passes validate, and the final typed OBJs agree with
those oriented faces and physical vertices. Both are experimental
successors.

## Realized meshes

| Final measurement | Step 2 source | Residual only | Residual plus shape |
| --- | ---: | ---: | ---: |
| Nodes | 525 | 623 | 631 |
| TRI | 60 | 74 | 78 |
| QUAD | 487 | 574 | 580 |
| Global minimum TRI angle (degrees) | 3.79 | 6.33 | 6.33 |
| Global minimum QUAD angle (degrees) | 26.18 | 25.34 | 25.34 |
| Maximum adjacent element size ratio | 6.19 | 5.67 | 5.67 |
| Area-weighted XYZ RMS on 576 common sites | 0.027384 | 0.017303 | 0.017104 |
| Maximum sampled XYZ deviation | 0.123308 | 0.102808 | 0.102808 |

At birth, clipped overlap with the old TRI footprint in UV yields
100 percent QUAD for residual-only, with a 26.16-degree minimum
among overlapping QUAD. The augmented mesh covers 25 percent with
a TRI of 8.03 degrees and the remainder with QUAD, whose lowest
angle there is 89.88 degrees. After guarded smoothing, residual-only
remains entirely QUAD in that footprint (lowest angle 28.99 degrees).
The augmented mesh has about 25.4 percent TRI coverage, minimum
TRI angle 11.38 degrees, and a local QUAD minimum of 64.59 degrees.
The global limiting TRI and QUAD have identical UV and XYZ geometry
in the two final meshes, at locations outside the old TRI footprint.

The extra leaf makes local trade-offs but adds eight nodes and ten
faces versus residual-only. The small RMS reduction coexists with
the same sampled maximum and the same worst physical angles.
There is no observed minimum-angle advantage from adding this TRI
as a seed in this run. Both arms worsen the QUAD minimum relative
to the Step 2 predecessor. The reported lengths measure geometric
deviation and do not define mixed global curvature error.

## Disposition and next action

Retain residual-only as the simpler Ribbed comparison baseline.
Keep the augmented result as evidence and do not promote the extra
shape seed from this trial. The experiment did not exercise mixed
epoch acceptance, global curvature, multiple patches or a full
compiler/CRT/sanitizer delivery matrix.

The two limiting faces are already present, with the same vertex
positions, before smoothing. The 6.33-degree TRI ties a side-0
contour point, whose adjacent chords are 1.00032 and 0.50010,
to a 0.12500 edge shared with a QUAD at depth 4. The 25.34-degree
QUAD uses a 1.01716 side-1 contour edge and a 0.25817 opposing
edge. Its edge midpoints lie on or within depth-4 leaves. This is
evidence of length contrast at the native cap, with no guarantee
that subdividing or changing one span corrects either face.

Next align a bounded physical-to-discrete conversion that checks
actual child arc lengths against local requests before regeneration,
using residual-only as the control. Include a count budget and
measure both shared limiting regions and all final shape scores.
Keep the original split operation, quadtree cap, mixed selection
and smoothing. Current accepted mixed epochs: zero.
