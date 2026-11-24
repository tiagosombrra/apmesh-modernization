# QUAD research plan at a glance

Updated 2026-11-24. The immediate research question is whether a mixed mesh
can identify a poor curve-to-template transition, change the local native
mesh size, and generate a better successor while preserving fine geometric
detail elsewhere. The deliverable is an opt-in application run with inspectable
meshes and a decision for each attempt. The default adaptive TRI run supplies
the reference. The planar mixed method of 1993 supplies the template and front
construction. Feedback from the physical mixed mesh on a curved surface is the
research extension. See the [article audit](ARTICLE_CONFORMANCE_REVALIDATION_20261118.md).

## What the evidence supports

| Finding | Consequence for the plan |
| --- | --- |
| The [integrated generator](PR240_RESEARCH_INTEGRATION_20261119.md) discretizes original curves and emits physical TRI and QUAD using native templates and a mixed advancing front. The [histories](MIXED_HISTORY_OBSERVATIONS_20261119.md) bind each mesh to a TRI-driven source attempt. | Reuse this entry, the existing acceptance traces, and the original TRI control. A mixed file at Step 2 does not establish mixed feedback. |
| [Changing global limits](LEGACY_BOUNDS_COMPARISON_20261120.md) reached 112 boundary segments and rejected attempts. [Passing measured curvature to the curve](ACCEPTED_TRI_CURVE_HANDOFF_TRIAL_20261120.md) changed size requests without repairing the accepted history. [Deferring an edge](MIXED_TRANSITION_SHAPE_20261120.md) retained the critical faces. | Stop rerunning these variants unless a new observation distinguishes a specific cause. Record requested size, realized arc and incident face sizes so saturation and poor shape remain distinguishable. |
| The [two automatic Ribbed selections](RIBBED_AUTOMATIC_TEMPLATE_GROUP_TRIALS_20261123.md) ran through separate native executions after an earlier manual grouping. With 23 fixed segments, the [paired comparison](TRANSITION_REGIONAL_COMPARISON_AUDIT_20261124.md) found the regional minimum angle rose from 6.86 to 43.44 degrees and the patch-wide TRI minimum from 6.86 to 7.04. Faces fell from 636 to 608. The single arc split improved regional RMS but worsened regional minimum angle. | Treat Ribbed as development data. Freeze the comparison region from the predecessor before looking at the successor. Report whole-patch damage as well as regional benefit. A single good angle or a lower sampled error cannot decide the trade-off. |
| The [Bezier selector replay](MIXED_TEMPLATE_GROUP_SELECTOR_20261123.md) preserved the same T6 edge and returned no action. The archived positive Bezier comparison used a manually chosen layout. [Shared-curve measurements](MIXED_SIZING_CROSS_CASE_20261123.md) found a physical neighbor ratio as high as 5.84 on matched seams. | A second independent native case and a protected fine-size control are still needed. Treat two-patch synchronization and grading as a subsequent scope with its own evidence. |
| The [curvature candidate](MIXED_QUADRATIC_JET_CANDIDATE_20261119.md) has sparse and one-sided boundary limitations. PR 243 covers its diagnostic, PR 247 the feedback adjacency and PR 263 the paired reporter. | None of these three draft branches implements an accepted adaptive history. Report original TRI global curvature error when available, mixed geometric RMS/max in model units, and mixed global curvature as unavailable until qualified. |

## Execution order and decisions

| Order | Work product | Evidence that permits moving on |
| --- | --- | --- |
| **1. Measured locally. Reversible native trial** | From one nonempty Ribbed predecessor, invoke the existing selection and native reconstruction in the experimental application. Derive requests and the region from that mesh, retain source hash, patch, curve intervals, affected leaves, tree limits and candidate hash. Reuse the existing real-boundary owner and OBJ rollback rehearsal. | One valid staged mesh, a forced rejection or publication fault that preserves the previous owner, ordered observers, epoch and OBJ bytes, and a recorded no-action case. The operator can reproduce the comparison without supplying a parent ID or choosing a region after the result. Engineering trials increment no scientific epoch. |
| **2. Active. Freeze the scientific decision before testing transfer** | With the advisers, specify how TRI shape, QUAD corner Jacobian, gradation, geometric deviation and growth enter admission, including units, tolerance, grid sensitivity, ties, and a case where shape and error disagree. Bind the rule and the covered region to the run configuration. Specify what curvature evidence is required for the claim. | The rule can decide the archived positive, reversed and trade-off examples, or explicitly abstain. Preserve source-curve identity when testing grouping; a change to the partition is a separate treatment. No thresholds are adopted by this plan. |
| **3. Test transfer once with a frozen rule** | Register a second native curved-to-flat patch and control, refinement limits, predecessor-derived region and sampling sites before inspecting output. Include a fine-resolution veto and an unchanged-edge/no-action case. Use the original TRI run, static mixed mesh and feedback-enabled mixed candidate for distinct comparisons. | Record valid, rejected, saturated and no-action outcomes. A no-op supports a veto; a positive transfer claim requires an actual native improvement on the second geometry. If transfer fails, report the limiting mechanism and revise the hypothesis before another run. |
| **4. Demonstrate an adaptive history** | Apply the aligned policy to the previous accepted mixed mesh twice, through the same entry. Archive each attempted mesh, original curve parameters, typed topology, parent/child identity, metrics, reason and rollback. | [Issue 221](https://github.com/tiagosombrra/apmesh-modernization/issues/221) requires two distinct accepted mixed-driven epochs with prior-state influence, a source-compatible estimator, native validity and ownership checks, frozen TRI parity, exact-revision regression and independent verification. Report any shorter history at its measured length. |

The [reversible native trial](REVERSIBLE_TRANSITION_TRIAL_20261124.md) covers
staging, injected rejection and the selector veto on the retained Ribbed patch.
Portability and broader ownership/publication qualification remain pending.

Compare geometry on identical analytic UV sites with area weighting. Report physical
TRI and QUAD shape by contour-edge, contour-vertex-only and interior faces, before
and after smoothing. Record node and face counts by type. For the TRI/mixed research
comparison use the same model, analytical reference and comparable element budget,
or report the error versus size for each run and identify unmatched budgets. An
accepted TRI step supplies a baseline only. Timing or budget differences must be
visible before drawing an efficiency conclusion.

One active implementation item is sufficient. Reopen smoothing or sizing only when
a reproducible failure identifies that operation. The global curvature estimator is
a prerequisite for claiming the corresponding global error and the full scientific
milestone; the reversible trial can proceed now. Shared two-patch grading follows
the single-patch demonstration. High-valence welding, all-QUAD and anisotropy
retain their separate scope. Use Blender for the accepted/rejected mesh sequence
and analytic reference once that sequence exists.

The [current state](STATE.md) names the active item and the
[roadmap](IMPLEMENTATION_ROADMAP.md) retains historical obligations. The
[previous reading guide](https://github.com/tiagosombrra/apmesh-modernization/blob/ce33b5e7b2743ff5e32495e4271dbd885d9da30f/docs/research/quad/CURRENT_PLAN_OVERVIEW_20261118.md)
preserves the earlier package inventory and visual artifacts.
