# Local boundary-transition-interior coupling proposal - 2026-11-16

Sequencing updated2026-11-17: retain this proposal after completion of the
integrated mixed-fill capability and actual mixed accepted-state/error feedback.
The [current implementation realignment](MIXED_FILL_REALIGNMENT_20261117.md)
supersedes its former position as the immediate next controller. This changes
delivery order, not scientific approval or any proposed numerical threshold.

Status: scientific proposal requested by the user after inspecting the generated
mesh. No new numerical policy, formula, threshold or implementation is adopted.
Baseline source remains d59a513a04ea8c9573e006789641f4adbeecedee in draft PR238;
its factor-bound repair and evidence are preserved, not presented as a complete
balancing controller. Advisor alignment remains required for scientific changes.

## Problem and current source findings

The corrected coarse run has curved-side points3/5/9 and mixed nodes33/281/797.
Three straight sides retain3 points each. The boundary grows, but interior growth
can outpace the support needed for a good transition. More interior elements do
not guarantee better boundary fidelity or triangle/QUAD shape. Counts in one
and two dimensions cannot by themselves measure local mesh-size compatibility.

GeneratorAdaptive::ComputeCurveAdaptationFactor combines patch factors and
patch error/efficiency weights. It does not consume local quality of the actual
mixed boundary-adjacent elements. Several density/spacing/structural responses
in GeneratorAdaptive::AdaptDomain are guarded by current_policy_.stable_mode;
the current explicit original-curvature case uses legacy. Adapter structural
fallback is likewise guarded by IsAdaptiveStableMode.

Adapter::ComputeCurveDomainBalance returns1 when target_patch_h is not positive.
In the corrected legacy trace, curve_domain_balance is1 at all three steps;
that neutral return is not a measurement proving balanced discretization.
The existing regional coupling indicator is computed from TRI FaceList region
quality, not from actual typed mixed faces. The source sequence is still
TRI-driven; mixed_adaptive_epochs=0. These are source/log observations, not a new
native experiment or proof that every undesirable element comes from the curve.

## Proposed behavior for review

Use local coupled target sizes, rather than one global scalar that forces the
whole boundary and domain to have equal density. Keep the original real-curve
discretizer, quadtree/templates and original exterior AFT. The proposal supplies
reviewable sizing requests and feedback; it does not substitute a generator.

1. Geometry determines initial local size requests on curve intervals and surface
   regions. Preserve high-curvature fidelity; retain coarser sizes where geometry
   and neighboring mesh requirements allow. Compare lengths in a consistent
   physical metric, or transform through the local surface Jacobian when using
   UV; never compare raw physical curve length to an unconverted UV size.
2. For each original boundary interval, inspect its actual incident mixed faces
   and adjacent transition/interior neighborhoods. Record local boundary length,
   nearby element scale, curve approximation error, element quality and size
   changes across neighboring layers. No global point-count ratio stands in for
   this adjacency information. Mark missing/invalid observations as unavailable,
   rather than treating a neutral numeric default as a successful balance check.
3. If boundary spacing is too coarse for a geometrically justified neighboring
   interior and causes poor transition elements, request refinement only on the
   implicated original curve intervals. Rediscretize analytically and synchronize
   shared curves before rebuilding the affected quadtree/templates and AFT.
   A geometrically straight interval may still need points for compatibility;
   refinement must not propagate from an unrelated distant curved region.
4. If the interior is finer than geometry/accuracy requires, damp that local
   interior request instead of automatically adding boundary points. Poor quality
   alone must also trigger a cause check: AFT layout, template transition or a
   geometric defect may require repair rather than extra curve refinement.
5. Grade sizes across boundary, transition and interior, with bounded changes per
   adaptation and hysteresis to avoid alternating over-refinement/coarsening.
   Local curvature and required accuracy can legitimately justify a fine interior
   behind a straight boundary; the transition must accommodate it smoothly.
   Do not impose uniform density or globally refine flat regions.

The feedback must come from the actual generated QUAD/TRI candidate and be
associated with the correct source interval, patch and generation identity.
Candidate feedback and diagnostics do not by themselves accept or publish a
mixed state. Preserve accepted ownership, rollback and rejected traces until
scientifically approved mixed selection/commit rules are available.

## Decisions and finite validation

Define the physical size comparison and adjacency neighborhood, curve/surface
error targets, TRI/QUAD quality criteria, allowable spatial size gradient and
per-step change, hysteresis and a finite retry/stop rule. Separate geometric,
curvature and cost objectives. No universal numeric ratio, fixed factor1.5,
weighting formula or new stopping/acceptance rule is authorized by this proposal.
These scientific choices require explicit advisor alignment under AGENTS.md.

The next concrete implementation slice is a source-interval-linked diagnostic
and request contract for actual mixed faces, using existing exports and controls
first. Activate new numerical feedback only after the scientific choices above
are aligned. Reuse existing parity evidence where source/data are unchanged.
Change-relevant validation must then include the existing curved patch across
all steps, a flat/low-curvature control, a localized-curvature control and shared
curve synchronization. Include missing-measurement, coarse-boundary/poor-transition,
wrong generation identity and rollback/rejected-history negative controls.
Report same-site physical error, regional quality, local size compatibility and
nodes/elements per step. Fewer nodes or a global mean alone is not a pass; retain
exact-head native/regression and independent review gates before integration.

No new native build, generation, test, CI, Blender scene or scientific acceptance
was performed in this planning session. Existing d59a513 qualification remains
its own bounded scope. PR238 review, Doxygen, broader CRT and R3/M7 remain open.
