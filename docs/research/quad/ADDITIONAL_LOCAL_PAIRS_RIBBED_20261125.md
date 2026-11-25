# Transfer of additional local pairs to Ribbed Bracket

2026-11-25 Fortaleza. [Draft PR 275](https://github.com/tiagosombrra/apmesh-modernization/pull/275)
head `779ac3437a7ab7099dda3d26c8deb478892dc922`.
[Machine-readable receipt](evidence/ADDITIONAL_LOCAL_PAIRS_RIBBED_20261125.json).

## Scope and controls

Run the same opt-in advancing-front flag used on CurvaBezier on original
Ribbed Bracket patch 12 in isolation, Step 2. The reference is the exact-image
portable archive for the existing both-seed requests. The experimental input
plan differs by the `additional_pairs` line alone. The Windows MSVC x64
Debug C++17 image, analytic patch, ordered requests, original TRI, mixed
predecessor and source tree match by hash or direct comparison. Both arms
deliver the same 22 ordered contour segments and original curve records,
the same 133 ordered leaves, the same seed QUADs and the same 623 nodes.
No relative tolerance or shape limit was recalibrated. The measurement
covers a second development geometry with a different existing request
profile from the selective CurvaBezier comparison.

The native candidate stages in 56 seconds in the directed runner, with
zero accepted mixed epochs. Independent replay checks all 100 candidate
operations and rejects a forged score. The first change is operation 1.
Replacement QUADs appear at operations 1, 3 and 60. The reference has 98
operations. Three successful fallback replacements still lead to two more
faces overall because the altered front changes subsequent construction.

## Physical outcomes

| Metric | Control | Additional pairs |
| --- | ---: | ---: |
| Final TRI / QUAD / total | 74 / 574 / 648 | 78 / 572 / 650 |
| Minimum contour-vertex TRI angle at birth | 6.33 degrees | 0.29 degrees |
| Minimum contour-vertex TRI angle after smoothing | 6.33 degrees | 6.33 degrees |
| Minimum interior TRI angle after smoothing | 18.37 degrees | 10.90 degrees |
| Minimum interior TRI shape after smoothing | 0.43305 | 0.24380 |
| Minimum interior QUAD angle after smoothing | 26.71 degrees | 27.04 degrees |
| Final global surface deviation RMS | 0.01736884 | 0.02353321 |
| Final maximum sampled surface deviation | 0.10749591 | 0.11580974 |
| Largest final adjacent size ratio | 5.66626 | 5.66626 |

The RMS is weighted by source surface area over the same 2,304 UV sites,
in model length units. It increases 35.49 percent. The 24 by 24 report and
the physical TRI and QUAD metrics for all regions and both stages are in
the receipt. The same unguarded smoothing control rejects at face 562 in
both arms. All five guarded passes complete. The unadopted predecessor
quality profile blocks both outputs on face growth, interior TRI angle and
shape, and interior QUAD shape.

## Where the change comes from

The new 0.29 degree TRI is created at operation 29. Its edge from vertex
197 to 622 is part of the replacement QUAD produced at operation 1. This
TRI is absent from the original topology. Guarded smoothing raises its
individual minimum angle to 22.81 degrees, so a different TRI determines
the final regional minimum. The lower interior TRI minimum after smoothing
and the larger sampled error remain.

The first replacement QUAD has S = 1.156, an 83.09 degree minimum physical
angle, and a birth scaled corner Jacobian of 0.9652. The 126 comparison sites
inside its final footprint account for 91.22 percent of the net increase
in weighted squared error. On five identical sites in each prospective
footprint, all four eligible QUADs at this operation produce larger
geometric RMS than the completed original birth mesh. Selecting only by
QUAD shape misses this error. The four alternatives are assessed offline.

An additional offline control compares each replacement QUAD with its two
constituent triangles, on identical sites. In Ribbed operation 3, the QUAD
has lower local RMS than those two triangles, while increasing local RMS
against the completed original mesh. The two constituents cannot serve as
an equivalent proxy for keeping the original front decision. CurvaBezier
operation 13 improves local birth RMS in its own footprint, despite the
small increase in final whole-chart RMS. These comparisons introduce no
generator rule or threshold.

## Closure and next action

The transfer falsifies a consistent quality benefit for the tested
minimum-S fallback. Keep it experimental and retain the original front
as the control. Before any broader promotion or reserved case, align a
prospective test that uses the existing relative surface deviation and
physical size information on the local front. Compare its predicted
viability against the archived footprints and existing transition shape
controls before changing native selection. Both development cases informed
this study. Shared curves, mixed reentry, global curvature error, and two
admitted mixed epochs remain open.

The native run and independent readbacks are recorded with exact commands
and inputs. One local analysis attempt failed on a UTF-8 byte order mark.
The next found the two OBJ exports use different face ordering. The final
check verifies exact node coordinates and an orientation-preserving
multiset of face cycles, alongside the full operation order from the native
trace. The native application was run once for the variant. No production
source, acceptance logic, or default TRI configuration changed in this
transfer. Hosted PR checks are recorded on the exact source head in the
receipt. This documentation checkpoint closes the bounded experiment.
