# Mixed-front transition and element shape

20 November 2026, Fortaleza. Source investigation and a bounded research
experiment for the native `curva_bezier` fixed-`1.5` history. Curve adaptation,
templates, centroid, the TRI source acceptance policy and the separate mixed
curvature work retain their existing scope.

## What happens at the interface

The [numeric receipt](evidence/MIXED_TRANSITION_SHAPE_20261120.json) binds the
original Step 2/3 MSVC archive by SHA-256. It compares unchanged contour UV/XYZ
and face connectivity before smoothing, all five passes and publication.
Faces are matched by vertex set because export order can differ. Shape is
recomputed from physical coordinates with the existing independent reporting
function. All ratios below are descriptive.

| Witness | Initial minimum angle | First pass | Fifth pass |
| --- | ---: | ---: | ---: |
| Step 2 contour QUAD with lowest first-pass corner Jacobian | 25.85° | 16.24° | 15.64° |
| Step 3 TRI from front commit 106 | 1.42° | 5.70° | 6.99° |
| Step 3 TRI from front commit 48 | 6.95° | 2.59° | 1.87° |

Commit 106 connects the fixed straight-side midpoint `(0, 0.5)` in UV to the
exposed seed edge `(0.125, 0.125)–(0.125, 0.15625)`. The edge measures
`0.03125` in UV and `0.04731` in XYZ. The two links to the contour point
measure `0.66953` and `0.71364` in XYZ. The shape of this face was determined
by the available geometry: after commit 73 the unfilled pocket contains that
one contour vertex and four collinear seed-interface vertices, with no other
active vertex within its closure. Each of its three exposed seed edges must
remain in a conforming partition. Every possible four-vertex polygon has a
degenerate corner or zero area, leaving the three observed triangles. The
alternate QUAD at commit 106 has a zero signed UV corner cross product.
Commit 14 creates one side of the pocket. Commit 73 creates the other, with
legacy UV triangle radius ratio `0.03671` and physical/UV quantities kept
separate in the receipt. Changing the final TRI/QUAD pairing would leave
the constrained closure unchanged.

The different commit-48 TRI shares another short exposed template edge.
The contour corner `(1, 1)` stays fixed while the other two vertices move
about `0.0553` and `0.0589` in UV. At Step 2 the two contour-edge QUADs'
lowest corner scaled Jacobian goes `0.394 -> 0.158 -> 0.224`, while the
vertex-only TRI minimum angle improves `4.82° -> 9.59°`. These are regional
minima. They can belong to different faces at different stages.

## Existing controls and literature

The native triangular AFT uses `Face::quality()`, a planar
`2 * inradius / circumradius` score, and reports values below `0.05` as
degenerate-shape observations. Its local postprocessing tries a UV position,
tests the adjacent triangles, and restores the old position when the score
fails to improve. The runtime `AFT_LOCAL_POSTPROCESS_*` settings control
that legacy path. The mixed article route calls `ArticleMixedFront::Run`
and `SmoothMixedUv` separately. Its five simultaneous mean updates validate
convexity, orientation and overlap. They can reduce element shape metrics.

[Canann, Tristano and Staten (1998)](https://citeseerx.ist.psu.edu/document?doi=83b460eaa8a47fc9d79fe0b2b8af755eda6affea&repid=rep1&type=pdf)
provide a precedent for constrained smoothing on TRI, QUAD and mixed meshes.
[Knupp (2001)](https://doi.org/10.1137/S1064827500371499) treats shape,
orientation and length ratios in a Jacobian-based framework. For this patch,
the signed corner Jacobian is paired with edge ratios: a long rectangle can
retain right angles and a strong scaled corner Jacobian. The final comparison
reports angle extrema, shape tails and neighboring size ratios by region,
together with counts and sampled geometric error. These metrics have different
interpretations from the TRI source's global curvature error.

## Approved experiment

The researcher prioritizes generation of the transition over the separate
quality-constrained smoothing experiment. For one opt-in fixed-`1.5` run,
postpone a base edge when the prospective choice is a TRI with one original
contour vertex, an opposite edge from the exposed seed interface, and legacy
UV radius ratio below `0.05`. Try the next active edge with the existing
TRI selection and QUAD eligibility. After an unproductive full rotation,
commit the earliest deferred valid TRI. This preserves the vertex set and
the per-base choices, with a changed order at the marked transition. The
scientific scope is one locally compiled and isolated application, compared
with the archived control. Keep the current five-pass smoothing for both.

A separate proposed experiment would protect incident TRI area scores,
QUAD corner Jacobians and QUAD edge ratios during UV smoothing while preserving
the fixed curve. It is deferred by the researcher. The source-history,
scoped curvature estimators and mixed global curvature acceptance remain
separate.

## Run result and disposition

MSVC `19.44.35229.0`, Windows x64, Debug C++17, MPI/OpenMP/LTO disabled.
The isolated C++ change is based on `c93a383e2775d33eb8a7e5f28cbc410e3d98593d`.
Configuration and build exit zero in 4.22 and 215.88 seconds. One application
invocation exits zero in 22.08 seconds under the retained 180-second bound.
The three comparison scripts bind original and candidate OBJ/trace hashes in
the receipt. An independent source-boundary audit checks all 32 contour edges
in Steps 1–3 and rejects nine corruptions of the final candidate. All four
original TRI OBJ files match byte for byte, as do both Step 0 mesh files; all
manifest source acceptance, epoch, retry and lineage fields match. Original
contour identities/positions, native leaves, centroid, seed and clearance
records match exactly through Steps 1–3.

| Observation | Step 1 | Step 2 | Step 3 |
| --- | ---: | ---: | ---: |
| Deferred prospective TRI choices | 0 | 0 | 221 |
| Full rotations requiring the first deferred valid TRI | 0 | 0 | 15 |
| Original and trial final nodes / QUAD / TRI | 33 / 24 / 8 | 281 / 249 / 52 | 689 / 630 / 102 |
| Final worst physical angle, in both | 31.55° | 9.59° | 1.87° |
| Original and trial area-weighted sampled XYZ RMS | 0.022169 | 0.012897 | 0.009542 |

Step 3 first changes a committed polygon at operation 32. The pocket-closing
TRI moves from operation 73 to 105 and the `1.42°` TRI moves from 106 to 104.
All three final pairs have exactly the same XYZ/UV arrays, cyclic oriented
face multisets and smoothing trace. Steps 1 and 2 mixed exports also match
bytes. Step 3 export order and cyclic starting corners differ. Shape scores,
size-gradation and sampled error agree for each before/after comparison.
The Step 3 final contour QUAD minimum corner Jacobian is `0.32013`, and the
median neighboring size ratio for the vertex-only transition is `1.44270`
in both. This is a negative result for the bounded ordering change. It stays
local, with no promotion to the research branch or PR243.

**Next:** prepare a single scientifically aligned change to the local spacing
before the mixed front is seeded, centered on the long original straight-side
intervals and adjacent template edges. Start with the existing curve
subdivision and quadtree size measurements in the neighborhood of the exposed
edge `[13, 349]`. Quantify the extra nodes and score quality through all five
smoothing passes. Retain both the short-edge pocket and the fixed-corner
smoothing regression as separate comparisons. Seek alignment before selecting
a new spacing rule. Keep the smoothing guard queued after transition work.

**Closure scope:** C++/configuration changes are confined to the isolated
local trial. The canonical checkpoint adds documentation and numeric evidence.
The trial exercised its deferral and full-rotation release in the real case.
Other models, configurations, allocation failures and broader native/compiler
validation were outside this run. Full CTest, frozen TRI corpus qualification
and new hosted checks were not run for this checkpoint. Mixed global curvature
error remains unavailable; mixed adaptive epochs remain zero.
