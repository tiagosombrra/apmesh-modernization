# Curved-boundary behavior diagnosis - 2026-11-15

Inspected exact feature 79828fcbfc1c4aa20d84576e58f1a3ef8fe2592a and retained
native artifacts. This is a diagnosis, not a numerical change or new native run.

## Confirmed findings

ModelCurvaBezier curve 0 has controls (1,-1,0), (0.5,-0.5,0), (0.5,0.5,0),
(1,1,0). Its analytic midpoint is (0.625,0,0), distance 0.375 from its initial
endpoint chord at (1,0,0). The curved source exists; endpoint-only sampling
hides that shape.

The example selects adaptive_stable and two steps. Generator enables both
point and element budgets for this mode. AdaptCurve invokes the original
curve and surface passes, but RefineCurveSamples then invokes
RebuildCurveWithTarget under the active point budget. That final operation
can replace/discard proposed samples to enforce its target count.

| Source step | Actual points per curve, endpoints included | Total boundary intervals | Outcome |
| --- | --- | --- | --- |
| 0 | 2 on each side | 4 | Initial TRI reference |
| 1 | 2 on each side | 4 | Accepted, unchanged four TRI |
| 2 | 4 on each side | 12 | Rejected, 28 candidate TRI |

Retained curve CSVs show final targets 2 then 4. Step-2 targets before
consistency are 8/7/7/7, clamped to 4/4/4/4. Twelve is the total over four
sides: the curved side has only three straight mesh segments. The acceptance
log records growth factor 7, error improvement 0.456174 and score -2.85629.
The reference rejected this candidate under its existing criterion.

RunRealBoundaryPatch finishes the TRI reference first, selects the last
locally selected source with a complete global outcome (including rejection),
then generates mixed QUAD/AFT once. It does not adapt curves from its own
previous mixed mesh. Blender displays this one export, not a progressive
mixed sequence. Existing point/parameter/ID equality and interval/tree tests
do not prove approximation between boundary sites or mixed convergence.

Exported curve-0 parameters: 0, 0.378067746758461, 0.621932253241539, 1.
A 10,001-point analytic Bezier sampling gives maximum nearest distance to
those three segments 0.06280875228120662 near t=0.1846, in source units.
This is a sampled diagnostic, not a continuous bound or an acceptance threshold.
Intermediate counts/parameters immediately after the curve and surface passes,
before budget rebuilding, have NOT been measured. The code proves the rebuild
path; final CSV alone does not prove which intermediate points were removed.
Do not infer a curvature-formula defect from these observations alone.

## Disposition

PR238 is draft: the bounded bridge retains its compiler/contract/CI evidence,
but the expected coarse-to-fine mixed behavior remains unimplemented and the
candidate is not ready to integrate for that functional objective.

One active item: localize and correct this curve/control-flow discrepancy.
Next code action is to record step/attempt identity and parameters/counts after
each original pass and the budget rebuild, retaining initial/subsequent states
and real acceptance/stop reasons. Correct the proven cause before changing
controls. The mixed successor must be driven by its actual prior accepted
mixed state, with retained ownership/history/publication and approved mixed
curvature/error/selection gates. No density knob, tolerance, acceptance,
stopping policy, formula or default TRI is changed here. Mixed epochs stay zero.

Evidence: retained step-1 accepted/step-2 rejected curve CSVs, acceptance log,
source-contract stdout, reference steps 0/1/2 OBJ and exact mixed OBJ. Read code,
recounted face-edge incidence and evaluated the pinned Bezier formula. No new
compiler, CTest, sanitizer, Doxygen or scientific campaign was executed.
