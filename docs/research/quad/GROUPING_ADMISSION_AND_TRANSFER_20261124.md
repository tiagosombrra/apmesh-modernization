# Conservative grouping decision and native CurvaBezier control

Recorded 2026-11-24 Fortaleza. [Protocol, commands and numeric receipt](evidence/GROUPING_ADMISSION_AND_TRANSFER_20261124.json).
The researcher authorizes the conservative comparison for this bounded grouping
experiment. Freeze the measurements and second-model configuration before running
the native control.

## Evaluation

The evaluator in [draft PR 264](https://github.com/tiagosombrra/apmesh-modernization/pull/264)
reads paired results from the [fixed-region comparator](TRANSITION_REGIONAL_COMPARISON_AUDIT_20261124.md)
on grid sizes 24 and 48. Both reports must use the same input mesh pair,
predecessor-defined region and analytic source. The comparison uses the final
smoothed meshes, with before-smoothing results kept for diagnosis.

Require exact directed contour equality for grouping and a strictly larger
minimum physical angle among all faces overlapping the region. The region may
change from TRI to QUAD. Across the complete patch, the minimum TRI angle and
TRI shape score, and minimum QUAD angle and scaled corner Jacobian, cannot
decrease. Both node and face counts are bounded by their predecessor values.
The maximum adjacent size ratio cannot grow in the region or the full patch.
At both sampling densities, sampled maximum deviation and area-weighted RMS are
compared in the region and the full patch. Agreement on increasing deviation
vetoes eligibility. Disagreement on the direction of any geometric metric
returns inconclusive unless a separate veto applies. Floating-point equality
uses a relative allowance of 64 binary64 epsilons for arithmetic roundoff,
without a model-scale or mesh-quality tolerance. An angle tie lacks the
regional improvement required here. Each arm contains a single tested candidate;
ranking multiple eligible candidates is outside this protocol.

The native validity, curve-source trace and protected requested size checks
precede this evaluation. The evaluator uses existing reports and does not
publish a candidate. Sampled geometry is in model units and supplies no
continuous bound or global mixed curvature measure.

| Comparison | Offline disposition | Evidence |
| --- | --- | --- |
| Ribbed staged single group and archived two groups | Eligible | Better regional angle, size ratio and sampled deviation with unchanged contour. |
| Ribbed two-group comparison reversed | Reject | Worse regional angle, grading, sampled error and counts. |
| Ribbed split arc | Reject | Regional error decreases, but the angle worsens, the contour changes and counts rise. |
| Injected opposite RMS directions | Inconclusive | Synthetic sampling disagreement without a separate veto. |
| Ribbed injected finer request | No action from the selector | The requested resolution protects the proposed group. |
| CurvaBezier archived two groups chosen manually | Eligible | Better regional angle and grading with lower sampled error on both grids. The global minimum angle is unchanged. |

The admitted comparison status is eligibility for this experiment. The
Ribbed native candidate from the prior session was explicitly rejected
to exercise preservation of its predecessor. No adaptive epoch is accepted.

## Native reproduction on the second geometry

Regenerate the original CurvaBezier histories with the retained MSVC C++17
native application and original curves, templates and mixed front. The run
exits zero after 20.95 seconds. All eight TRI and mixed Step 0 through Step 3
OBJ files and the Step 3 front trace match the prior archives byte for byte.
The final original-flow mixed output has 689 nodes, 630 QUAD and 102 TRI
with 14 original curve segments.

Run the existing primary grouping selector on the freshly exported Step 3
front. The limiting unsmoothed TRI is 1.418 degrees. Its short template edge
is 0.047312 model units. Grouping its four siblings would retain the same
edge in T6, with a projected size ratio of 14.151 before and after. The
selector chooses no action, so no successor reaches the comparison rule.
This is renewed native evidence for a previously known transfer failure.
The selector operates on fresh output outside the executable. The run
provides no new positive automatic transfer.

Compare the archived manually selected two-block alternative separately.
It raises the regional minimum from 3.795 to 8.242 degrees and reduces the
maximum regional size ratio from 5.400 to 4.863. The full-patch minimum
remains 1.870 degrees. The additional block borders the first on the
contour side and changes the template constraint. This supports a narrow
follow-up hypothesis: test an adjacent block only when it forces the old
short side to remain. Obtain alignment for how the neighboring block is
chosen and preserve the fine-size veto, contour and 2:1 constraints.
No search for alternative faces or groups was performed in the native control.

## Validation and remaining gates

Five focused evaluator tests pass on remote PR 264 head `e1775f38`.
The exact tool reproduces all five real comparison dispositions from the
preregistered evaluator. The commit's initial EOF whitespace finding was
corrected before publishing. Hosted PR checks were in progress at review
snapshot. The default validation adapter lacked its required tools and local
baseline receipt. The native negative uses a previously qualified compiler
image, with its recorded compiler identity. No sanitizer, multipatch
or new native candidate acceptance was exercised. The draft is outside the
generation path, and accepted mixed epochs remain zero.
