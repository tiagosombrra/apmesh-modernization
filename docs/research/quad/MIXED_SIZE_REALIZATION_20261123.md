# Requested and realized spacing in the mixed feedback pilot

Recorded 2026-11-23 Fortaleza. Read-only audit of the actual Step 2
mixed predecessor and the [valid guarded successor](MIXED_SMOOTHING_PILOT_COMPARISON_20261123.md).
Both already exist in the capped pilot archive. This closes the bounded
size-realization measurement and prepares a reusable sizing contract.
The [receipt](evidence/MIXED_SIZE_REALIZATION_20261123.json) records
every original interval, all 17 face requests, the exact sample sites,
shape and sizing measurements, and the input hashes.

## How the sizes were paired

Trace the original boundary intervals by source identity and match split
children by the archived binary midpoint. Measure their native physical
arc lengths in model units, independently check against analytic Bezier
arc length, and use physical median edge length for each incident
TRI or QUAD. Arc lengths and chords are stored separately.

For each face request, locate its original residual sample in the
predecessor, in the reconstruction before smoothing and in the final
mesh. Compare physical median edge lengths at the same UV location.
Verify original leaf bins using the retained tree, face sizes using
the original feedback definition, and all 39 recorded updates by
replaying propagation on the typed old incidence reconstructed from
OBJ connectivity. The UV widths in the receipt reconstruct what the
recorded one-level tree operation requests from the original bins.
The archived candidate mesh provides the physical emitted sizes.
At each of the 17 sites there is one containing face in each frame.

## Where the size mismatch appears

| Observation | Result |
| --- | --- |
| Curve conversion | 8 of 10 old intervals divided. Five of those eight still exceed the request. The other three are 0.69 to 0.93 times the request. |
| Largest remaining curve difference | On side 3, request 0.19489 and longer child 0.50001, or 2.57 times the request. One division covers half of the original interval even when it needs a much smaller target. |
| Face conversion | 7 of 17 requested sites have a final face above the request. All seven received a leaf edit, and all seven exceed the request before smoothing as well. |
| Saturated sites | Both requests blocked at depth 4 have emitted faces within the requested physical size. Capped leaf 58 stays separate from the observed face size. |
| Unnecessarily fine output relative to a request | At face request 241 the result is 0.05822 for a target of 0.12979. At request 300 the result is 0.28370 for a target of 0.18435. |
| Three propagation passes | 22 face-to-face, 8 face-to-curve, 9 curve-to-curve reductions, zero curve-to-face reductions. In the active old graph, 4 of 50 final target pairs exceed 1.35, with maximum 1.70. |

A cut of one level in UV has variable physical effects once templates
and front faces are emitted. Requests 255 and 300 share leaf 49 and
land in the same final face, yet their two requests differ. Even a
saturated leaf can realize a smaller face through neighboring edits
and reconstruction. Treating either a leaf edit or a blocked edit
as evidence about the output would misclassify this case.

The 95th percentile of the ratio between adjacent face sizes improves
from 2.53 in the predecessor to 2.13 before smoothing and 1.90 after
it. The median ratio between each contour arc and its incident face
size rises from 1.70 to 1.76. The sampling populations change from
10 to 18 contour intervals and 571 to 753 shared face edges. These
observations do not establish a mesh-wide grading limit. The limiting
5.09-degree TRI touches the contour at one vertex and shares an
edge with a face 4.10 times different in size. No logged request
site maps to that TRI. A criterion based only on attainment at
sample sites misses this measured transition problem.

## Requirements for the next sizing proposal

A reusable implementation should keep the target in physical units
and attribute it to a typed curve interval or patch region. Preserve
the original binary curve subdivision, native quadtree balance,
templates and mixed advancing front. Separate three observations:
the requested size, the discrete action that fits limits and the
resulting physical sizes next to the curve and across shared edges.
Derive changes from requests and local neighbors, with no model
coordinates or case-specific exceptions. Where two patches share a
curve, any later implementation must retain one synchronized
partition and test the behavior from both sides.

Use the current case as one control. A future proposal needs evidence
from a second curved-to-flat configuration and a shared-curve case
before adoption. Compare effects on final TRI/QUAD shape, physical
gradation, error at common sites and node/face growth. A numerical rule
for choosing legal binary depths and mapping a physical request to
quadtree actions remains to be aligned. The audit does not prescribe
a new maximum depth, propagation limit, face acceptance or error.

## Validation scope

One read-only Python audit, no native rerun. The first quadrature
resolution missed convergence and the second audit attempt shadowed a
path while writing evidence. The final audit uses 1024 and 2048 panels
and completes the same tolerance check, interval sum, identities,
site lookup, request replay and artifact hash checks. The earlier
failures and corrected script are identified in the receipt.
No source or configuration changes. Zero accepted mixed epochs.
Global mixed curvature, cross-model qualification and the full
native matrix remain open.
