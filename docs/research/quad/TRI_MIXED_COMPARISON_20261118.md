# TRI and prospective mixed-front comparison

Date: 2026-11-18. Source candidate b3d2fbc, draft PR240; canonical entry660d0ad.
This is a read-only comparison of already generated artifacts, not a new native
generation, benchmark, acceptance policy, implementation or closure qualification.
[Measured evidence](evidence/TRI_MIXED_COMPARISON_20261118.json).

## Algorithmic differences

Both paths use the original analytic Bezier source, original curve adaptation,
native quadtree and original source TRI generation/adaptation history. The TRI
path fills the interior with triangular templates, then advances triangular
elements using its geometry phase and conditional topology phase. Its geometry
phase may construct ideal vertices; execute also calls improveMesh.

The mixed candidate subdivides intermediate interior polygons using canonical
side midpoints and experimental vertex-mean centers. In the remaining domain,
the new contraction uses existing contour nodes, native leaf neighborhoods and
maximum included angle. It considers neighboring triangles on the best triangle's
two other sides, evaluates possible QUAD unions using planar S<=1.5, then commits
one TRI or QUAD and the corresponding active-contour toggles. It retains TRI
when no acceptable QUAD is available. Selection precedes front mutation.

The earlier mixed prototype advanced TRI first and paired committed triangles.
That prototype, the unpaired QUAD-interior/TRI-exterior output, the original pure
TRI output and the new prospective mixed front are distinct comparisons.

Mixed choice uses planar UV coordinates; output vertices map to the actual XYZ
surface and retain source boundary identity. UV shape does not certify optimal
physical shape on a curved surface. The current mixed candidate has no smoothing
and no accepted mixed adaptive epochs. Curve/interior balance remains pending.

## Actual generated counts

| Stage | Pure TRI nodes | Pure TRI elements | Mixed nodes | Mixed QUAD | Mixed TRI | Mixed total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 17 | 24 | 33 | 24 | 8 | 32 |
| 2 | 78 | 144 | 281 | 249 | 52 | 301 |
| 3 | 223 | 430 | 797 | 738 | 102 | 840 |

At stage3, mixed output uses about3.57 times the nodes and1.95 times the elements.
The native midpoint/center subdivision changes density; QUAD generation is not
an equal-node conversion of the TRI output. Front QUAD counts are8/7/14, with
16/242/724 native interior QUAD. The 797-node mixed result does not improve the
previous unpaired mixed layout's node count. No runtime/cost benefit is measured.

## Same-site geometric error

Evaluate all576 centers of a24x24 UV grid against the independent Bernstein
surface, using linear TRI interpolation or four-node QUAD interpolation and the
source Jacobian as an area weight. Values below are RMS distances in the original
model units, not percentages of model size or the adaptive log's error metric.

| Stage | Pure TRI area-weighted RMS | Mixed area-weighted RMS | Relative RMS reduction |
| --- | ---: | ---: | ---: |
| 1 | 0.0264873587 | 0.0236686151 | 10.6418% |
| 2 | 0.0146519966 | 0.0117035994 | 20.1228% |
| 3 | 0.0093103124 | 0.0072621020 | 21.9994% |

This is a descriptive comparison of different node layouts, densities and
smoothing paths, not controlled isolation of the effect of QUAD shape. Stage1
maximum sampled distance actually rises0.0899217->0.0909421 despite lower RMS.
No continuous bound, finite-element solution accuracy, universal superiority or
equal-cost efficiency claim follows from these measurements.

The previously reported1.1217%/0.1323%/0.3667% RMS increases compare the new mixed
front to the unpaired QUAD-interior/TRI-exterior layout, not to pure TRI. Those
negative results remain valid. Different comparison references must stay named.

The existing mixed-region checker intentionally rejects pure TRI. Preserve that
first rejected attempt and its contract unchanged. A separate TRI-only linear
interpolation calculation covers all576 same sites per stage; evidence records
input hashes, method, script hash and limitations. No native tests are rerun.

## Current next action

Original candidate evidence remains85 local tests and4 successful hosted jobs on
exact b3d2fbc. This comparison adds no code qualification. PR240 remains draft:
independent review, explicit local WSL publication-failure disposition and exact
research-integration/post-merge gates precede R3 feedback and local balancing.
