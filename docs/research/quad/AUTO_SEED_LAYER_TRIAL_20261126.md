# Automatically select one post-smoothing transition repair

[Draft PR 295](https://github.com/tiagosombrra/apmesh-modernization/pull/295)
at `442644df44dfede19318f49832ab8fbbd65c370b` adds an opt-in planner
for the [native post-smoothing repair](POST_SMOOTH_SEED_LAYER_TRIAL_20261126.md).
The planner ranks faces below the frozen angle or shape floor by
their minimum ratio to the two floors, then by native face ordinal.
It grows edge-connected front groups and searches subsets of the
first template layer along their edges. It returns the first eligible
replacement and tries retaining all enclosed sites before removing
any. Limits are six front faces, six directly adjacent template
faces, 14 sites in a patch, 1,024 patches, 1,024 retention trials and
25,000 search states. Exhaustion creates a refusal receipt. A mesh
without below-floor faces creates a no-action receipt.

Run `python tools/quad_auto_seed_layer.py --archive <native-control>
--profile <progressive-profile> --output <new-directory>` on a
bound single-patch control with its original source, plan,
native birth trace and guarded smoothing frames. The output plan
is an input to the current C++ experimental route. The native
engine checks the birth witness, certified curve, physical size
requests, local shape and face cap. The planner does not edit the
control, change the default TRI route or publish an accepted mesh.

## Native matched comparison

| Measurement | CurvaBezier control to automatic | Ribbed Bracket control to automatic |
| --- | ---: | ---: |
| Failed-face rank selected | 1 | 1 |
| Minimum angle inside the repair | 3.25° → 17.07° | 11.91° → 16.44° |
| Minimum angle in the whole mesh | 3.25° → 3.78° | 11.91° → 11.97° |
| Total faces | 731 → 729 | 541 → 542 |
| QUAD faces | 648 → 644 | 483 → 480 |
| TRI below a safety floor | 31 → 27 | 12 → 11 |
| QUAD below a safety floor | 4 → 4 | 0 → 0 |
| Area-weighted RMS on the same 48 × 48 grid | 0.006621758 → 0.006623564 | 0.020102640 → 0.020102451 |
| Maximum sampled geometric deviation | 0.043991119 → 0.043991119 | 0.107484106 → 0.107484106 |

Both searches select the highest-ranked failure with no supplied
case name or face number. They examine 53 and four unique patches.
Both replacements happen to contain only TRI. The search accepts
the first locally eligible option and provides a weaker local
minimum on Ribbed than the earlier manually selected 23.64°.
It preserves 723 and 537 exterior faces, respectively, and keeps
all 697 and 525 retained coordinates and physical node IDs exactly.
Three and one enclosed sites retire. The 19 and 26 ordered curve
sites remain identical, and no previously met physical size
request becomes unmet. All original pass frames match, including
the guarded final mesh before replacement.

The full profiles still reject both meshes with the same sets of
blockers as their controls. RMS here is the root mean square of
sampled positional deviations, weighted by analytic surface area.
It changes by +0.02727 percent and −0.00094 percent, respectively.
The global mixed-curvature error remains open. These are two
development models and zero accepted mixed adaptive epochs.

## Validation and next action

Both native successors stage using identical archived-source inputs
and the unchanged MSVC 19.44 x64 C++17 Debug engine from PR 294.
The published selector reproduces both plan hashes. The eight
synthetic selection controls, 15 progressive controls, six size
controls and native curve contracts pass. The new direct article
invocation stops before rollback with Windows access denied on the
rename from its relative staging path. The failed logs are retained.
PR 294 has a passing direct rollback receipt for the same executable
using an absolute output path. The local validation adapter reports
unavailable required tools and a missing iteration baseline.
Full qualification and independent review remain open.
[PR 295 exact-head checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45799331940).
[Measured results and control inventory](evidence/AUTO_SEED_LAYER_TRIAL_20261126.json).

Map the remaining safety-floor violations by origin and region,
and estimate how many still have a feasible one-layer neighborhood
under the frozen budgets. Use those results to scope any proposed
multi-region repair or change to candidate ranking before running it.
Shared curves, owner reentry, two consecutive accepted mixed epochs
and reserved cases are still required.
