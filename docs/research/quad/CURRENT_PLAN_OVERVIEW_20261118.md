# Current QUAD plan at a glance

Updated2026-11-18 against the verified canonical plan and exact source11dcaa7,
draft PR240. This reading guide summarizes the existing approved sequence;
it does not introduce a new scientific rule, milestone or authorization.

## Objective

Extend the original mesher with the1993 mixed TRI/QUAD procedure, using real
original curve discretization and native quadtree/templates/front machinery.
Preserve default TRI, original policies, reproducible error/quality observations
and explicit separation between a static mixed output and mixed adaptive closure.

## What is already delivered

| Capability | Current status | Important boundary |
| --- | --- | --- |
| Original analytical curves feeding actual application output | Implemented; earlier bounded integration completed through PR238 | The adaptation still uses the original TRI state |
| Native interior templates and source polygons | Implemented; six-family catalog and actual mixed usage available | Historical numeric center identity remains unresolved |
| Prospective mixed advancing front | Implemented on draft PR240; chooses TRI/QUAD before one contour update | Static output exists; complete paper conformance is not claimed |
| Real curved-model output at steps0-3 | Regenerated and archived; current final output689 nodes,630 QUAD,102 TRI | These are outputs driven by TRI source histories, not accepted mixed adaptive epochs |
| Contour-clearance classification | Implemented in11dcaa7; exactly25 former violations removed | Boundary angle improves, but geometry error and worst edge ratio worsen |
| Per-step geometry errors and element quality | Exported to Markdown/CSV/JSON and displayed in Blender | Original global curvature error is TRI-only; mixed RMS is a different diagnostic |
| Explained Blender presentation | Delivered with six scenes, eight meshes,18 panels, real usage maps and FAQ | It shows the previous9ca6deb output; current clearance results are in the new numerical archive |

The latest source11dcaa7 has exact local85/85 and four successful hosted
checks, reverified remotely. Passing those scopes does not cover the missing
paper stages, full historical oracle, general geometry or full adaptive closure.
PR240 remains draft/unmerged. The modernization main branch stays separate.

## What prevents calling the technique complete

1. **Mixed smoothing:** current final mixed graph has no smoothing pass. Existing
   TRI smoothing flags do not directly smooth that graph.
2. **Historical center identity:** vertex arithmetic mean remains experimental;
   it is not generally the area centroid. Do not silently change the formula.
3. **Mixed global curvature error and adaptation:** the equivalent error on the
   actual mixed graph is unavailable; accepted mixed adaptive epochs remain0.
   Lower sampled RMS does not establish mixed adaptive convergence.
4. **Review/integration:** independent review, the retained adversarial-fixture
   enum diagnostic, local filesystem failures and exact research-merge gates
   remain necessary.

## The single execution sequence

1. **Implemented:** documented contour-clearance classification in the opt-in
   candidate, with retained witness/default TRI and exact checks. Review its
   tradeoffs and additional adversarial-fixture analysis finding.
2. **Next:** clarify and complete the paper's mixed smoothing/effective-control contract and
   explicitly resolve the historical center interpretation within its scientific
   alignment requirements. Preserve formulas rather than invent new balancing.
3. **Validate that correction:** regenerate the real histories, compare original
   TRI versus mixed geometry/quality under stated conditions, retain bad results
   and negative controls, update Blender and complete change-relevant tests.
4. **Qualify and integrate the bounded static package:** independent review,
   local-failure disposition, exact candidate remote/local gates, then research
   integration and exact post-merge verification. No automatic main integration.
5. **Later adaptive package:** connect actual mixed-state/error observations and
   retained histories, then the scientifically aligned estimator/acceptance and
   local boundary-transition/interior feedback work. Full M1/M5/R3/M7 and broader
   original gates remain open; no new controller is adopted by this summary.

The previously proposed new balancing controller and broad global-factor sweeps
are not the current next action. Preserve measured size mismatch as evidence.
Artifact polish and repeated audits are not default successors to this summary.

## Where to read

- [STATE](STATE.md): current active item, evidence and exact next action.
- [Implementation roadmap](IMPLEMENTATION_ROADMAP.md): full milestones and
  acceptance gates; dated historical queues do not override its current queue.
- [Article conformance findings](ARTICLE_CONFORMANCE_REVALIDATION_20261118.md).
- [Error/quality reporting](GENERATION_RESULT_METRICS_20261118.md).
- [Explained presentation](EXPLAINED_BLENDER_PRESENTATION_20261118.md).

Repository roles: canonical decisions/checkpoints are on `quad-templates`;
current executable changes remain on the source branch of PR240
(`research/quad-article-mixed-front-20261118`,11dcaa7). A documentation checkpoint
is not a new algorithm delivery. The earlier overview was documentation-only; the subsequent clearance repair
changes source and regenerates the real case. See its pinned report and evidence.
