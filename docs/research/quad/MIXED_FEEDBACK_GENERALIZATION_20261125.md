# Generalization gate for mixed adaptive feedback

2026-11-25 Fortaleza. Scope is the opt-in Bézier TRI/QUAD research path in
[issue 221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).
Historical TRI provides the control. Native curve sampling, balanced
quadtree, templates and the 1993-style mixed front provide reconstruction.
The feedback size field, admission and stopping are research extensions.

## What transfers today

The retained CurvaBezier and Ribbed Bracket patch 12 runs both improve
sampled geometric RMS and the worst transition TRI. Each also creates one
corner QUAD worse than its predecessor's boundary-QUAD minimum. The runs
used distinct experimental drivers. Both geometries have already informed
development. Their results establish feasibility and expose failure modes.
[Native comparison](MIXED_FEEDBACK_ADMISSION_SHARED_SOURCE_20261125.md).

The current native feedback driver requires the recovered CurvaBezier
grouping branch and the first accepted Step 3 attempt. Its size calculator
refers directly to the built-in CurvaBezier analytic evaluator. The live
real-boundary entry also admits one patch. These are executable scope
limits, even though the underlying reconstruction primitives are reusable.

A read-only diagnostic supplied each archived predecessor's own evaluator
to the same current size calculation. With the original formulas and pilot
parameters, it reproduced 13 face and ten curve requests for CurvaBezier,
and 17 face and eight curve requests for Ribbed Bracket. These are sizing
results. Native transfer through one common entry is still pending.

The same diagnostic ran a conforming unit plane with two TRI, one QUAD
and six boundary intervals. At every indicator sample, the geometric
residual was exactly zero. The current two-seed rule still proposed three
face and two curve requests, because it halves the target of the largest
residual of each type without a minimum signal check. This bounds the
claim of geometry-driven refinement. On a genuinely flat case, adjacent
finer regions or element quality could independently justify refinement.
Those reasons need distinct witnesses.
[Diagnostic receipt](evidence/MIXED_FEEDBACK_GENERALIZATION_20261125.json).

## Revised order of work

1. **One native entry independent of model and step.** Take the original
   Bézier evaluator, typed predecessor, its original curve samples, and
   its captured quadtree from the same attempt. Join them using explicit
   provenance. Build curve and leaf requests through the same code path
   regardless of file name, patch index, step number or previous manual
   grouping. Preserve the original binary split and native front. Use
   CurvaBezier and Ribbed to verify that the same executable consumes
   their source state, reports actual splits, and retains it on rejection.
   This is a portability test using the existing pilot.
2. **Align and freeze the candidate rule before reserved runs.** Develop
   one physical size field evaluated from explicit geometric and quality
   evidence, with graded changes between adjacent faces and curve intervals
   in both directions. Specify when to do nothing, when a flat region
   legitimately receives a smaller size from its neighbor, and what to do
   when the boundary split or quadtree cap cannot realize a request.
   Verify the achieved physical sizes and shape after native reconstruction.
   Grading of mesh size fields has a published basis. The present ratio 1.35,
   three passes and worst-face seeds are pilot settings. A mesh size field
   does not itself certify the realized mesh quality.
   [Borouchaki, Hecht and Frey (1998)](https://www.ljll.fr/~frey/publications/ijnme4398.pdf).
   Record an explicitly aligned stopping/admission rule, length units and
   tolerances, growth budget, tie order and required improvement. Keep
   geometric deviation and the pending global mixed-curvature estimator
   distinct.
3. **Test transfer on a registered corpus.** Keep CurvaBezier and Ribbed in
   development. Before running the frozen mixed policy, reserve actual
   Bézier inputs in the existing catalog covering different curvature and
   transitions, with selection by input geometry and source identity.
   Include controls for an exactly flat acceptable mesh, a curved-to-flat
   transition and a conforming shared curve. Record any rejected geometry,
   cap saturation, no action and failed reconstruction. Use the same
   policy parameters and executable for the reserved cases. A case used
   to improve the rule returns to development. Use fresh reserved geometry
   for the next transfer claim.
4. **Measure improvement at comparable cost and execute real ancestry.**
   Use original TRI, mixed input and mixed feedback output with comparable
   face budgets or report error versus face count. Use the same sampled
   analytic points per geometry. Record RMS and maximum distance, TRI
   shape and QUAD scaled corner Jacobian and angles by region, adjacency
   size ratios, growth, conforming incidence, unmet requests and rollback.
   A lower aggregate error alone is insufficient to certify local mesh
   quality. Execute two distinct accepted states driven by the previous
   mixed state under the frozen policy as required by issue 221. Report
   the domain and geometry coverage of any conclusion.

For the shared-curve case, capture native curve samples independently of
patch-local corner IDs. The known equal-XYZ corner rejection must be
resolved before native two-patch transfer. Qualify both sides' provenance,
winding and rollback on the shared pair. Report single-patch and two-patch
coverage explicitly. High-valence welding, all-QUAD and anisotropic
extension retain their existing scope.

## Current decision

The active implementation item is the model-independent single-patch
entry with verified source/mesh/tree provenance. Use the flat control
as a negative scientific control for the current indicator trigger, and
retain the curved pair as the next boundary ownership gate. The studies
above adopt no new numerical thresholds or scientific acceptance. No new
native meshes ran in this audit. Accepted mixed epochs remain zero.
