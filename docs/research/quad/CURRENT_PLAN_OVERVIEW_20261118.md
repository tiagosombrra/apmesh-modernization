# Current QUAD plan at a glance

Updated2026-11-19 against the verified canonical plan and exact research merge
7ccd8d7/PR242 diagonal experiment,5fe2e6f/PR241 reporting and51d51f6/PR240
generator. This reading guide summarizes the existing approved sequence;
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
| Native interior templates and source polygons | Implemented; six-family catalog and actual mixed usage available | Area-centroid UV policy adopted/tested; historical numeric identity remains unproven |
| Prospective mixed advancing front | Integrated in PR240; chooses TRI/QUAD before one contour update | Static output exists; complete paper conformance is not claimed |
| Real curved-model output at steps0-3 | Regenerated and archived; current final output689 nodes,630 QUAD,102 TRI | These are outputs driven by TRI source histories, not accepted mixed adaptive epochs |
| Contour-clearance classification | Implemented in11dcaa7; exactly25 former violations removed | Boundary angle improves, but geometry error and worst edge ratio worsen |
| Per-step geometry errors and element quality | Exported to Markdown/CSV/JSON and displayed in Blender | Original global curvature error is TRI-only; mixed RMS is a different diagnostic |
| Source-history error/quality binding | Integrated PR241: full stage identity, accepted/rejected source lineage, hashes and changes versus previous accepted source | Original TRI errors on rejected attempts are reported; no mixed estimator or adaptive acceptance |
| Both-diagonal Gaussian sensitivity | Adopted and measured in PR242;22 real observations/three native profiles | Sign flips and differing distribution results; no diagonal/global estimator/adaptive policy selected |
| Mixed smoothing | Implemented: UV, distinct incident other vertices, five simultaneous passes, fixed contour | Angle gains coexist with worse QUAD J/stage2 RMS/stage3 boundary angle |
| Current Blender presentation | New four-scene file: eight outputs,18 pass states, mean/area comparison and previous template reference | New four-scene area-centroid file adds six actual mean/area comparison meshes; retained catalog is labeled previous mean reference |

[PR240 is integrated and qualified](PR240_RESEARCH_INTEGRATION_20261119.md) at
51d51f6: independent ownership/scientific reviews, exact post-merge85/85 baseline,
native20/20, actual three-profile histories and four successful hosted checks
(including527 Python/frozen TRI). Source/config/image identities are preserved.
The modernization main branch stays separate. No full-stage closure follows.

## What prevents calling the technique complete

1. **Historical smoothing identity:** adopted UV/distinct/five-pass smoothing is implemented and tested; numeric identity with the historical planar method is not proven.
2. **Historical center identity:** area centroid in UV is now explicitly adopted and tested for the experiment; the original software equation remains unproven.
3. **Mixed global curvature error and adaptation:** the equivalent error on the
   actual mixed graph is unavailable; accepted mixed adaptive epochs remain0.
   Lower sampled RMS does not establish mixed adaptive convergence.
4. **Coverage limits:** static review/integration is complete. The raw additional enum-analysis exit1, old DrvFS route, full CRT/allocation/atomic-publication coverage and independent exact front-tie coverage remain explicitly limited.

## The single execution sequence

1. **Implemented:** documented contour-clearance classification in the opt-in
   candidate, with retained witness/default TRI and exact checks. Review its
   tradeoffs and additional adversarial-fixture analysis finding.
2. **Smoothing and center disposition implemented/tested:** the user adopts area centroid in UV. Actual histories and negative controls pass; small Step2 benefits and a small QUAD-J loss remain. No repeated selection question for the settled experiment.
3. **Executed for clearance/smoothing:** real histories regenerated, before/after quality/error exported, all15 passes/negative controls retained, new Blender opened and change-relevant tests passed. Current area-centroid comparison is delivered in its own exact-source evidence.
4. **Complete:** bounded static review, retained-finding disposition, research integration and exact post-merge verification at51d51f6. Main remains separate.
5. **Complete:** source-history reporting prerequisite in PR241/5fe2e6f; actual accepted/rejected/retry observations remain associated with the correct previous accepted source.
6. **Complete:** approved both-diagonal Gaussian comparison in PR242/7ccd8d7; same-node sign flips and nonuniform stage results are retained.
7. **Prepared, not adopted:** [mixed Gaussian/mean operator contract](MIXED_CURVATURE_OPERATOR_CONTRACT_20261119.md). Explicit adoption/revision of the bounded quadratic-jet candidate is next; legacy mean scaling/global aggregation questions stay separate. Full M1/M5/R3/M7 and broader gates remain open.

The previously proposed new balancing controller and broad global-factor sweeps
are not the current next action. Preserve measured size mismatch as evidence.
Artifact polish and repeated audits are not default successors to this summary.

## Where to read

- [STATE](STATE.md): current active item, evidence and exact next action.
- [Implementation roadmap](IMPLEMENTATION_ROADMAP.md): full milestones and
  acceptance gates; dated historical queues do not override its current queue.
- [Article conformance findings](ARTICLE_CONFORMANCE_REVALIDATION_20261118.md).
- [Error/quality reporting](GENERATION_RESULT_METRICS_20261118.md).
- [Current source-history bindings](MIXED_HISTORY_OBSERVATIONS_20261119.md).
- [Measured both-diagonal comparison](DIAGONAL_CURVATURE_COMPARISON_20261119.md).
- [Pending mixed K/H scientific contract](MIXED_CURVATURE_OPERATOR_CONTRACT_20261119.md).
- [Explained presentation](EXPLAINED_BLENDER_PRESENTATION_20261118.md).

Repository roles: canonical current code and decisions/checkpoints are on
`quad-templates`. PR240/51d51f6 integrates the static generator package;
PR241/5fe2e6f integrates reporting bindings; PR242/7ccd8d7 integrates the
read-only diagonal experiment. Their source branches preserve the qualified
candidates. A later documentation checkpoint does not establish another
exact-revision native/scientific execution.

Current [mixed smoothing delivery](MIXED_UV_SMOOTHING_20261118.md) preserves all tradeoffs and exact validation identities.

The [area-centroid implementation and comparison](AREA_CENTROID_DELIVERY_20261118.md)
settles the experimental center choice. Static review and finding disposition
are complete in the [PR240 integration record](PR240_RESEARCH_INTEGRATION_20261119.md).

The earlier [review-readiness checkpoint](PR240_REVIEW_READINESS_20261118.md)
retains its pre-review status and Linux-filesystem qualification evidence.
Old DrvFS failures and raw enum analysis remain visible; their scoped disposition
is recorded by the later integration. The adopted curvature comparison is
complete. The mixed Gaussian/mean contract is now prepared; explicit scientific adoption
or revision is pending, as described in STATE.
