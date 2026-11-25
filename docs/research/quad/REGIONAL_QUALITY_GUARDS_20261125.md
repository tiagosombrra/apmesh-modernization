# Regional quality floor and face budget study

2026-11-25 Fortaleza. [Draft PR 273](https://github.com/tiagosombrra/apmesh-modernization/pull/273)
head `c06f69feaa8da7eed0b427a32f60b41d3d86b84c`.
[Machine-readable receipt](evidence/REGIONAL_QUALITY_GUARDS_20261125.json).

## Executable assessment

The research evaluator reads a staged single-patch predecessor/candidate
pair and an explicit profile. It uses the already measured minimum physical
angle and shape score in each of six groups (TRI or QUAD with a contour
edge, with only a contour vertex, or in the interior). TRI uses the
existing triangle shape score. QUAD uses the existing minimum scaled
corner Jacobian. The operator supplies all twelve floors and the face
growth fraction.

For a group present in both meshes, a minimum must reach its floor or
strictly improve from a predecessor minimum already below that floor.
A new class has to meet the floors as there is no predecessor minimum.
A class absent in the candidate is recorded. Both metrics and counts
below the floors remain visible. The read-only result covers these
configured guards. It also reproduces geometric deviation on 24 by 24
and 48 by 48 common UV samples. It performs no epoch decision, stopping,
publishing, or mutation of the source archives.

## Profile controls on the four archived meshes

The [common relative calibration](COMMON_RELATIVE_CALIBRATION_20261125.md)
supplies the same four native candidates. Two controls exercise the
reporting path with one budget equal to the measured selective Ribbed
growth of 57/547 (10.4205 percent), the minimum common budget that could
include both selective archives by face count alone.

- **Permissive control.** Floors zero isolate the budget branch because
  physical validity is already checked by the mesh evaluator.
- **Predecessor-derived control.** For each type, region and metric,
  use the lower observed minimum across the two nonempty predecessor
  groups. When both are absent, use the same permissive test floor.
  This is an explicit test profile for development.

| Guard result | CurvaBezier both | CurvaBezier selective | Ribbed both | Ribbed selective |
| --- | --- | --- | --- | --- |
| Permissive control | Passes | Passes | Face growth blocks | Passes |
| Predecessor-derived control | Blocks | Blocks | Blocks | Blocks |

The predecessor-derived profile blocks both selective candidates on
interior TRI angle and shape. It also blocks selective Ribbed on
interior QUAD shape. CurvaBezier creates an interior TRI class absent
from its predecessor. Any common floor greater than 8.04047 degrees or
0.22575 in interior TRI shape blocks that CurvaBezier successor. These
numbers describe the available candidates under the prototype. They
are not proposed quality requirements.

## Limiting interior TRI

The two CurvaBezier candidates have the identical limiting interior TRI
in UV and XYZ. In the selective run, the pre-smoothing frame already
contains the face at 6.36773 degrees. It reaches 8.04047 after guarded
smoothing. The three edges measure 0.05797, 0.22812 and 0.17748 in physical
units. The adjacent QUAD across the shortest edge has a median physical
edge length of 0.05822, versus 0.17748 for the TRI. The measured poor
element predates smoothing and survives both seed regimes, so changing
the tolerance between those regimes cannot remove this face.

Next trace its native creation and the size change from the adjacent
QUAD, using the same inputs, before proposing a reconstruction change
or freezing quality thresholds. Keep the Ribbed archive as the other
development control. Evaluate angle and shape by region and report
over-limit size requests and the eligible budget. Own mixed successor
reentry, shared-curve feedback and the global mixed curvature definition
remain open.

## Validation

Six directed controls and 39 focused Python checks pass. Eight
read-only CLI assessments match the archived native geometric reports,
using both common grids. A corrupted model-surface witness is refused
by the directed test. The limiting TRI study binds both stages and
both seed cases. The C++ generator and native image are unchanged.
No new native run, held-out geometry, adopted tolerance, regional
floor, growth budget, or accepted mixed epoch belongs to this study.

[Exact hosted run 45610316100](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45610316100) has 0 successful, 4 pending and 0 other jobs at checkpoint. Independent review is pending.
