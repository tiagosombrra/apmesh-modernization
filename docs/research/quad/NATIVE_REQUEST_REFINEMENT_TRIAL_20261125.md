# Compare native contour and follow-up leaf splits at physical requests

The approved comparison follows the [archived front-choice replay](FRONT_SIZE_OPTIONS_REPLAY_20261125.md).
[Draft PR 291](https://github.com/tiagosombrra/apmesh-modernization/pull/291)
at `4d6db5f2a6459fafa3d2322199cb1670d03b88dc` permits one explicitly selected existing face request
to subdivide its containing leaf a second time. The plan requires a
certified successor and a unique face request. The original split and
balance run first. The second split requires exactly the next
level after the original split and room under the original cap.
It uses native subdivision, checks the direct three-leaf increase,
then restores native 2:1 balance. The curve comparison uses the
existing certified arc operation. Neither arm changes the generators'
selection, smoothing, shape, error or growth criteria. The directive
is opt-in and does not change the default TRI path.

## Matched native comparison

| Measurement | CurvaBezier control → arc | Ribbed Bracket control → leaf |
| --- | ---: | ---: |
| Final faces / fixed cap | 731 → 731 / 805 | 533 → 540 / 601 |
| Certified contour segments | 18 → 19 | 26 → 26 |
| Final size at targeted sites | 0.13681 → 0.13140 | 0.95097 → 0.19437 |
| Requested size | 0.07104 and 0.07243 | 0.38298 |
| Minimum final angle at targeted sites | 22.33° → 18.96° | 17.21° → 86.93° |
| Requests met after smoothing | 4/7 → 4/7 | 8/17 → 10/17 |
| Transition TRI below a safety floor | 30 → 30 | 10 → 13 |
| Worst transition TRI angle | 3.25° → 3.25° | 11.97° → 11.97° |
| Area-weighted geometric RMS, 48 × 48 | 0.0066262 → 0.0066218 | 0.0203525 → 0.0201073 |
| Maximum geometric deviation, 48 × 48 | 0.0439911 → 0.0439911 | 0.1074841 → 0.1074841 |

The CurvaBezier trial splits original interval 0 using a certified
native point at UV (0.06443863201639033, 0). Arc lengths measured
independently on the same analytical surface are 0.27381 before
and 0.13687 plus 0.13695 after subdivision. The original archived
samples and all previously generated coordinates are retained. Four
control-trial inserted IDs advance by one because the native routine
assigns new IDs in original interval order. The control and trial
trees and geometric requests match byte for byte. Both targeted
requests still exceed their size limit before and after smoothing.
The local QUAD's angle is worse at birth; the face stays in the same
shape through smoothing.

Ribbed leaf 150 at UV (0.75, 0, 0.875, 0.125) is replaced by its four
level-4 children. The realized tree gains three leaves (109 to 112)
after template grouping. The original curve certificate is identical.
Two QUAD cover request 478 at birth, both below 0.192 model unit and
with angles of at least 89.52°. One QUAD covers it after smoothing,
at 0.19437 and 86.93°. Request 486 also meets its size after smoothing.
The targeted replacement creates new template-support edges around the
refined leaf. Three additional transition TRI and one new interior TRI
are below the 15° safety floor. All four are already below the floor
before smoothing. The three new transition bases are each about 0.125
unit beside about 0.500-unit certified arcs. One such arc touches the
contour vertices used by all three. Both staged native meshes remain
blocked under the unchanged progressive profile.

## Validation and next action

Both no-option controls reproduce eight archived artifacts per model
byte for byte. The new mode refuses duplicate selection, an unknown
request, a leaf already capped at input and a leaf with no available
level after the initial split. Every archived source is byte-bound.
Independent checks cover the actual site-incident sizes, two error
sampling grids and the edge-adjacent 2:1 leaf pairs. Original-curve
contracts, 15 progressive checks, six sizing checks and the native
article rollback regression pass on the measured MSVC C++17 Debug tree.
The first ad hoc source-contract invocation omitted the required
configuration and stopped before boundary captures. The separate
workflow-configured invocation verifies all six captures and 54
source refusals plus the certification controls. The central validation
adapter could not resolve its full tools or iteration baseline.
Full stage qualification and review remain pending.
[Hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45741703224).
[Commands, witnesses and hashes](evidence/NATIVE_REQUEST_REFINEMENT_TRIAL_20261125.json).

Next project a coordinated contour and seed pair using the physical
edge/arc grading already used by the size-field work. Start with the
new Ribbed transition strip and the CurvaBezier corner. Bind an
affordable native action to both exposed seed edges and certified arcs
before aligning another numerical rule. Retain the locally effective
Ribbed comparison as evidence. No accepted mixed epoch, shared-curve
validation, owner reentry, reserved-case coverage or global mixed
curvature norm follows from these single-patch runs.
