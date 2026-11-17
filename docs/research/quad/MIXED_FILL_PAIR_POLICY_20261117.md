# Experimental mixed-fill pairing policy - 2026-11-17

Classification: research policy decision, supported by read-only observations.
The research owner explicitly delegates the metric/limit/ordering choices in the
current conversation. This resolves the earlier pending technical questionnaire
for this opt-in experiment; it does not assert formal advisor sign-off, literal
1993 reproduction, production adoption or an optimal global meshing algorithm.
No numerical selection is activated by this documentation checkpoint.

## Decision for the next implementation

Use policy `physical_angle_pair_v1` in a separate explicit research selector.

1. Retain the historical starting angular limit: S <= 1.5, where
   S = 1 + max_i(abs(beta_i - 90 degrees)) / 90 degrees. A square has S = 1.
   In a valid convex planar QUAD the limit permits corner angles from45 to135
   degrees. This is an angular criterion, not a complete error/quality measure.
2. Calculate beta_i from the two physical XYZ corner chord vectors. The mesh
   approximates a physical surface, and raw UV angle distortion depends on its
   parameterization. Keep S_UV as a comparison diagnostic, not the physical
   quality gate. Applying the planar rule to nonplanar XYZ corners is an explicit
   curved-surface research extension, not a source-certified1993 choice.
3. Require an admissible oriented four-node union in UV. Preserve the existing
   four corner determinant threshold1e-14, source/seam/manifold contracts and
   existing physical validity predicates before scoring/ranking. Retain the
   source-normal signed corner scaled-Jacobian and split-normal checks without
   changing their tolerances. They do not certify continuous bilinear validity.
4. Among currently admissible alternatives in the original live-front operation,
   minimize S_XYZ. On exact equality, minimize physical longest/shortest edge
   ratio, then preserve original frontier alternative order, then use stable
   source face/node IDs. No weighted sum, tie epsilon, new aspect-ratio cutoff
   or new refinement factor is introduced. The edge ratio only resolves exact
   angular ties; it does not bound every accepted element's elongation.
5. If no admissible pair exists, retain the valid TRI. Consume each source TRI
   at most once. Do not force QUAD count or apply a completed-mesh greedy matcher
   as a substitute for the intended in-front procedure.

The shape score is locally best only with respect to the declared ordering and
currently available alternatives. It does not optimize the full mesh, global
error, node count or future frontier. Monitor physical edge ratio, warpage,
sampled geometry error, coverage and failed candidates alongside angular shape.
No new threshold for these diagnostics is inferred from this decision.

## Evidence from the actual archived candidates

Source: feature7fc988d30b27f08f620a68e4804ce453270774bd, draft PR238.
Read existing MSVC Debug histories original-default, original-coarse and
bounded-coarse, adapted steps1-3. Include accepted and rejected TRI reference
states; do not present them as accepted mixed epochs. Nine stage observations
contain seven distinct XYZ/UV/connectivity geometries after deduplication.

| Observation | Count |
| --- | ---: |
| Topological candidate observations across those seven geometries | 760 |
| Fail existing UV convexity/orientation predicate | 410 |
| Fail existing physical corner/split predicate | 180 |
| Pass validity plus S_UV <= 1.5 | 244 |
| Pass validity plus S_XYZ <= 1.5 | 138 |
| Pass UV angular policy but fail XYZ angular policy | 108 |
| Pass XYZ angular policy but fail UV angular policy | 2 |

Invalid counters overlap. The138 eligible observations overlap/conflict and
are not138 selected elements. There is no statistical independence claim for
these760 observations or evidence that accepting more pairs is better.

Among61 base-TRI observations with multiple alternatives passing both angular
policies, score-space ranking differs in15. That diagnostic uses source face IDs
for score ties; it does not exercise the full future rank or live-front ordering.

Three analytic controls complement the actual data: a unit square has S=1;
a sheared physical parallelogram with square UV has S_XYZ=1.7048327646991335;
the inverse parameterization example has the same distorted S_UV but a physical
square with S_XYZ=1. These demonstrate why a parameter-space angle is not an
intrinsic physical shape score. They do not establish a global convergence rate.

[Portable observation and source/input hashes](evidence/MIXED_FILL_PAIR_POLICY_20261117.json).
Local analyzer command: `python build/quad-pair-policy-20261117/compare.py`.
Raw OBJ/CSV inputs and the analyzer remain local build artifacts, so the report
is not a self-contained rerun package. Source-scoped generation and independent
OBJ readers remain available at the pinned feature revision.

## Implementation and acceptance boundary

Next: implement this policy during the original frontier operation, with distinct
AFT-pair provenance and reversible two-TRI/one-QUAD physical owner publication.
Keep native-template origins separate. Preserve source nodes, curve sharing,
frontier ordering, oriented seam, coverage, manifold incidence and valid TRI
fallback. Log all alternatives, rejection reasons, chosen score/tie keys and
rollback; publish no selected face until the owner transaction succeeds.

Validate square/skewed/curved and reparameterization witnesses, positive and
rejected pairs, competing alternatives, exact ties, foreign IDs/generations,
nonconvex/degenerate inputs, duplicate consumption and nonempty rollback.
Compare actual source histories and independent UV/XYZ topology/quality/error;
run change-relevant native profiles, sanitizer checks and frozen TRI/exact-head
regression before qualifying or integrating the implementation.

This session ran read-only diagnostics, three analytic controls, count/hash
assertions and documentation checks. No new source build, full baseline rerun,
native sanitizer run, CI run, mesh generation or Blender display occurred.
Prior85/85 and hosted4/4 remain evidence only for exact source7fc988d, whose
selection is still not_evaluated. No lower geometry error or better final mesh
has been demonstrated for this future selector.

M1 polygon-center identity, M5 historical scope, R3/M7 mixed accepted feedback,
Doxygen/full CRT, independent review and integration remain open. Local sizing
balance follows qualified mixed filling and actual mixed error/feedback; neither
that controller nor its thresholds are decided here.
