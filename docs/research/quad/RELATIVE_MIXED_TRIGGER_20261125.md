# Relative geometric trigger for native mixed feedback

2026-11-25 Fortaleza. [Draft PR 272](https://github.com/tiagosombrra/apmesh-modernization/pull/272)
head `7d17c5d368b179e903665ba1658637c2a6c76d42`.
[Machine-readable receipt](evidence/RELATIVE_MIXED_TRIGGER_20261125.json).

## Aligned experiment

The researcher selected relative geometric deviation as the first
refinement signal and requested shape assessment after reconstruction.
The opt-in `--relative-tolerance` divides the existing maximum sampled
distance per face by its median physical edge length. It selects at
most one seed of each element type whose score strictly exceeds that
tolerance, using the existing face order for ties. The earlier seed
reduction and size propagation remain fixed. The original native curve
split, capped quadtree, mixed front and smoothing comparison are reused.
A finite nonnegative tolerance is required by the option. The existing
default pilot is preserved.

The exact plane generates no relative requests at test tolerance zero.
The unfiltered control gives three face and two curve requests. A
synthetic curved-to-flat transition shows that an active curved TRI
can still cause a size request on its flat QUAD neighbor. Rescaling
that fixture by eight preserves the selected sites and scales the
physical targets by eight. Invalid negative and nonfinite tolerances
are rejected. These are sizing tests.

## Native validation

The zero-tolerance test reproduces both prior [portable successors](PORTABLE_MIXED_FEEDBACK_20261125.md)
and all face and curve requests byte for byte on the same C++ application
image. An explicit high cutoff of 1 yields no action on the native
Ribbed source. The replay preserves the identical TRI, mixed predecessor
and tree files, and has no successor plan or archive. The separately
supplied forged tree still fails before reconstruction on the positive
Ribbed arm.

The two development inputs have four distinct per-type maxima. A
read-only replay evaluates the intervals induced by those breakpoints,
without fitting a tolerance or using reserved geometry. For one directed
native sensitivity control, set the tolerance to the earlier measured
maximum QUAD score on CurvaBezier (0.034341894205194436). By the strict
comparison, only CurvaBezier's TRI seed can initiate requests at that
boundary. The requests go from 11 face and seven curve requests to seven
face and two curve requests. Apply the same native reconstruction once.
The absolute threshold value is specific to the control.

| CurvaBezier | Mixed input | Both seeds, test tolerance 0 | TRI seed only, sensitivity control |
| --- | ---: | ---: | ---: |
| Faces | 732 | 796 | 780 |
| Curve segments | 14 | 21 | 16 |
| Native quadtree leaves | 223 | 229 | 226 |
| Geometric RMS at 2,304 common UV sites | 0.011915 | 0.008071 | 0.009073 |
| Maximum sampled geometric distance | 0.049974 | 0.044192 | 0.044192 |
| Minimum physical TRI angle | 1.42 degrees | 2.47 degrees | 2.27 degrees |
| Minimum contour-edge QUAD angle | 19.44 degrees | 18.57 degrees | 19.44 degrees |
| Maximum adjacent face size ratio | 12.24 | 8.66 | 8.93 |

The sensitivity run reduces RMS by 23.8% at 6.6% face growth and preserves
the original boundary QUAD minimum. Interior QUAD minimum falls from
64.41 to 50.86 degrees, compared with 27.63 degrees in the both-seed arm.
The minimum TRI angle directly adjoining a contour edge is unchanged.
It retains a smaller RMS gain than
the two-seed case and has 16 fewer faces and five fewer boundary segments.
The unguarded arm rejects face 668 at pass one. The guarded arm stages a
valid successor after five passes. The selective outcome is a development
observation. A common fixed tolerance still needs a calibration and
reserved-case validation plan with regional quality and resource guards.

## Evidence and remaining gate

The local directed portable suite, 33 Python controls and the additional
native threshold observations use the exact source and unchanged C++
image. The first selective command failed argument parsing before any
native invocation. Keep this prefix alongside the successful replay
using the recorded tolerance literal. Exact head run 45585487055 has 1 successful, 3 pending and 0 other hosted jobs at checkpoint. Independent review is pending.

No decision adopts a tolerance, growth budget, scientific acceptance
policy or global mixed curvature operator. The next decision specifies
the development calibration and intended guards before applying a frozen
policy to reserved cases. The native predecessor reentry, two accepted
mixed epochs and conforming shared-curve adaptation remain open.
