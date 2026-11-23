# Native trials of automatic template grouping on the two sides of a Ribbed contour vertex

Recorded 2026-11-23 Fortaleza. The researcher authorizes execution
of the experiments needed to resolve the defect. Apply the
[archived selector](MIXED_TEMPLATE_GROUP_SELECTOR_20261123.md) on the
measured minimum-angle TRI before smoothing. Each reconstruction
takes just one new selected parent. The
[receipt](evidence/RIBBED_AUTOMATIC_TEMPLATE_GROUP_TRIALS_20261123.json)
binds both applications, source/selector images, meshes and comparisons.

The Python selector runs against the actual preceding geometry and
writes a single new parent plus its four native child identities to
the isolated native replay. The native app verifies those cells,
replays the copied tree, and builds the existing templates, mixed
front and smoothing. The originally tested manual coarsening is
part of every comparator. The second application also keeps the
first automatic grouping. The selector has not been integrated
into the ordinary or production application.

## First automatic grouping

The measured 6.86298-degree TRI chooses parent 62 with children
66 through 69. Native build and application exits are zero in
7.61 s and 40.45 s. The tree changes from 130 to 127 leaves
and replaces that block's four 0.12501 facing edges with two
0.25001 edges. The local template block contains 11 instead of
16 seed QUADs. The TRI footprint is wholly covered by QUAD
before smoothing (one QUAD, 43.44-degree physical minimum)
and after smoothing (two QUADs, same local minimum). The
global TRI minimum barely changes.

The next 6.86759-degree TRI already existed, with identical
UV and XYZ, immediately next to the removed one and at the
same contour vertex (0.5, 1). Its exposed side belongs to
another parent. A read-only analysis of both parents together
preserves 2:1, finds no pending smaller-size request in the
affected boxes, and predicts both sides' longer edges. The
rule can therefore address the remaining side with one further
grouping, using the measured first candidate as its control.

## Second automatic grouping and combined result

The selector reruns against the first candidate and chooses parent
71 with children 74 through 77. Build and application exit zero
in 7.74 s and 34.67 s. Exactly the selected four leaf records
give way to their parent, leaving 124 leaves. The adjacent
previously grouped parent switches template as expected after
losing the finer neighbor. Its curve-facing scale stays enlarged.
The old 6.86759-degree TRI footprint is wholly QUAD (one at
birth and two overlapping after smoothing, minimum 43.51 degrees).
The global worst TRI moves elsewhere. Its final angle improves
to 7.03754 degrees.

| Final measure | One manual group, starting control | Plus first automatic group | Plus second automatic group |
| --- | ---: | ---: | ---: |
| Curve segments | 23 | 23 | 23 |
| Nodes | 612 | 598 | 584 |
| TRI | 73 | 73 | 73 |
| QUAD | 563 | 549 | 535 |
| Worst TRI angle at birth (degrees) | 6.86298 | 6.86759 | 6.86982 |
| Worst final TRI angle (degrees) | 6.86298 | 6.86759 | 7.03754 |
| Worst final QUAD angle (degrees) | 26.26014 | 26.26014 | 26.26014 |
| Largest final neighboring size ratio | 5.51243 | 5.51243 | 5.28167 |
| Area-weighted XYZ RMS, same 576 UV sites | 0.01722016 | 0.01720131 | 0.01719460 |
| Maximum sampled XYZ deviation | 0.10278112 | 0.10278112 | 0.10278112 |

Validate both complete native front histories (96 and 95
transactions), template area centers, grouped leaf inventories,
2:1, five original and five guarded smoothing passes per
candidate, and typed output mapping. Both have the same
physical size requests, explicitly capped requests and
23 original-contour identities and positions as the reference.
All five ordinary prefix meshes and the guarded Step 2
predecessor match the retained archive.

## Disposition and next step

These cases resolve the two thin TRI at the one contour vertex
in the Ribbed archive and reduce the mesh by 28 faces.
Other parts of the same model still contain small TRI angles.
The second case illustrates why a single worst-face statistic
can hide a group of similarly bad elements at the same curve
vertex. Retain both observed positive results, the earlier
Bezier unchanged-edge and protected-size controls, and this
single-model scope.

Next prepare the reusable experimental selection and bounded
rollback around the whole local transition, with a reported
shape and geometric error comparison to the previous mesh.
Validate another curved/flat geometry for a positive native
run and a fine-resolution negative. Keep the historical
TRI and existing scientific acceptance unchanged until the
mixed acceptance/error rule is aligned. No approved mixed
adaptive epoch or mixed-global curvature is claimed.
