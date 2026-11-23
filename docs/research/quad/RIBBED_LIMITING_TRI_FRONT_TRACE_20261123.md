# Ribbed limiting TRI front trace and template interface

Recorded 2026-11-23 Fortaleza. The researcher requests the
diagnostic following the [single child arc split](RIBBED_SINGLE_QUAD_EDGE_SPLIT_20261123.md).
The isolated MSVC Debug C++17 application adds the front-history
export only. Build takes 10.55 s and the one application exits zero
in 42.70 s within 180 s. The predecessor, five ordinary prefix OBJs,
all request/leaf records, smoothing frames and typed mixed outputs
match the prior run byte for byte. The [receipt](evidence/RIBBED_LIMITING_TRI_FRONT_TRACE_20261123.json)
retains source/image/trace hashes, selected and rejected candidates,
and independent observations.

## What the front had available

Independent replay checks all 99 commits: 24 mixed QUAD selections
and 75 TRI, with 71 observed QUAD-union rejections. The front creates
the limiting TRI at operation 27. Its oriented base is the short
template edge from UV (0.4375, 0.125) to (0.40625, 0.125).
There are 112 active vertices across the full front and three
geometrically valid third vertices for this base:

| Vertex UV | Opposite angle in UV | Physical minimum angle of the TRI |
| --- | ---: | ---: |
| (0.625, 0.0625) | 2.49 deg | 3.99 deg |
| (0.625, 0.09375) | 1.33 deg | 2.52 deg |
| (0.500091552734375, 0) | 10.30 deg | 6.33 deg |

The actual choice is also the best of these by physical minimum
angle. One prospective side has no valid next TRI; the other
selects a union with an invalid UV corner. Considering every
geometrically valid secondary vertex gives two convex unions with
S about 1.80 and 1.89, outside the existing 1.5 criterion.

Exhaustively check that short base in each of the first 27
archived front states, including the original state and the target
operation. Considering all geometrically valid active vertices
regardless of search radius gives no higher physical minimum TRI
angle and no eligible two-TRI union for that base. The front
component containing the base has 14 vertices after operation 4.
Its three valid third vertices then stay unchanged up to the
target operation. This bounds the finding to a fixed base and
observed history; different earlier connectivity is unmeasured.

## Native template scale and next decision

The short edge belongs to a seed QUAD in depth-4 leaf
[0.375, 0.4375] x [0.125, 0.1875]. All four native QUADs of this
leaf match the T1 quarter-square subdivision. Its parent has four
depth-4 leaf children (native IDs 26 through 29). Independent
layout calculation groups those siblings into their level-3
parent [0.375, 0.5] x [0.125, 0.25] with 2:1 balance across
every leaf edge. It predicts existing T2 (only east side split),
11 instead of 16 QUADs inside the block, and two contour-facing
edges of about 0.25000 model units instead of four of about
0.12500. Counts are local to the inspected block. Neighboring
template changes and actual post-front quality remain unmeasured.
The curve retains its 23 original samples in this proposed test.

The bounded coarsening of a derived tree requires scientific
alignment. It would preserve the accepted source, native curve,
existing templates, mixed selection, depth cap and smoothing.
Measure the original TRI region and whole-mesh shape before and
after smoothing, geometric deviation and mesh growth. Record any
loss of accuracy or other shape regression. The diagnostic result
does not adopt a coarsening rule. No new scientific reconstruction,
accepted mixed epoch, mixed-global curvature or delivery
qualification follows from this trace.
