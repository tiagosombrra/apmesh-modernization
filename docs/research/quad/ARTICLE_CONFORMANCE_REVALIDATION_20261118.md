# Revalidation against the 1993 procedure and existing controls

Date: 2026-11-18. Source candidate b3d2fbc, draft PR240; canonical entry f1094d1.
Classification: read-only source/paper/decision audit and planning correction.
[Evidence, source anchors and flag consumers](evidence/ARTICLE_CONFORMANCE_REVALIDATION_20261118.json).
No generator, acceptance policy, scientific threshold, native test or mesh changed.

The user rejects invented balancing adjustments and requests the planned 1993
QUAD/TRI technique as an increment to the existing original algorithm, using
existing effective flags. This supersedes the previous priority to implement a
new local boundary/interior feedback controller. Retain its measured mismatch
as evidence; the proposed controller is outside the current execution scope.

## Primary-source scope

Directly inspect complete printed pp287-290 of the seven-page SIBGRAPI1993 scan,
SHA-256 `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`.
Native Poppler renders pp287-288 successfully; pp289-290 are checked against the
retained render and verified original PDF hash. No scan is redistributed.

The paper starts with an already discretized contour. It describes quadtree
construction, one-level neighbor grading, removal of interior cells too close
to the contour, maximum interior size restriction, templates, mixed contraction
and smoothing. It does not prescribe the newly proposed adaptive coupling law.
The inherited curve/surface adaptive pipeline is the deliberate original-code
increment; it is not claimed as part of the paper's planar algorithm.

## Findings that prevent a complete conformance claim

**PAPER-01 - contour-clearance reclassification is missing.** Printed p288
reclassifies an interior cell as contour when its distance to a contour edge is
less than0.2 times that edge's length. The purpose is to avoid poor transition
elements. Current `QuadtreeCell::inBoundary` and `CaptureLeafPolygons` classify
by missing side neighbors; the research path contains no equivalent edge-
distance clearance stage. This is an inherited selection difference, not a
failure of the new TRI/QUAD choice-before-commit loop itself.

Replay actual source leaf boxes and identify which leaves supplied native QUAD.
For every original finite UV contour interval, measure minimum rectangle-to-
segment distance against0.2 of its length. Also check cell-center distance as
a separate control, since the prose does not specify an executable distance
formula. Both interpretations yield the same witnesses in this fixture:

| Source stage | Used native interior leaves | Leaves inside the paper clearance band |
| --- | ---: | ---: |
| 1 | 4 | 0 |
| 2 | 44 | 0 |
| 3 | 175 | 25 |

All stage3 offending intervals are on the straight sides. Their UV interval
length is0.5, clearance target0.1, and closest used native cell distance0.0625.
This demonstrates a missing documented stage and a relevant witness. No cells
were removed or mesh regenerated here; improved quality after a repair is not
claimed. UV is the current planar chart, not a physical curved-distance identity.

**PAPER-02 - mixed smoothing is omitted.** Printed p290 averages adjacent-element
vertex coordinates for interior nodes, fixes original contour nodes and repeats
four or five times. The current mixed result explicitly reports smoothing=none.
`ArticleMixedFront::Run` and subsequent typed physical construction have no mixed
smoothing pass. The original TRI still calls improveMesh. Its smoothing flags
can affect source TRI and replay inputs indirectly, but do not directly smooth
the final mixed graph. Existing TRI quality passes/blend and5..7 runtime clamp
are not automatically the exact printed smoother.

**PAPER-03 - centroid identity remains unresolved.** The paper specifies a
polygon centroid; current PointRule uses vertex arithmetic mean. This equals
the area centroid for some shapes but differs for asymmetric polygons. Existing
M1 experiments contain both rules. Retain the explicit vertex-mean experimental
label and unfinished historical numeric oracle; do not silently adopt another
formula or certify the current one as the paper's exact numeric interpretation.

**PLAN-01 - the prior proposed remedy was premature.** Actual size mismatch and
poor boundary angles are real, but they do not establish that a new feedback
controller is needed before completing these existing article stages. Withdraw
that implementation priority. Preserve the old audit as observed evidence and
the old controller text as an unadopted proposal, with this explicit correction.

## Steps consistent with the audited scope

- Original curve/surface partitions and shared endpoint identities are replayed.
- Native topology checks one-level/2:1 neighbor grading. The actual largest native
  interior cell is no larger than the largest boundary cell in all three stages.
- Six native pattern families and midpoint subdivision are retained; this is
  separate from the still-experimental numeric center rule.
- Existing-node maximum-angle search, quadtree neighborhoods and second expansion,
  two prospective alternatives, planar S<=1.5, TRI fallback, polygonal front
  updates and termination are implemented in the audited core sequence.
- Default TRI and prior source outputs retain their measured exact-head gates.

Minimum-S choice and stable source-ID/side exact ties are explicit deterministic
implementation choices where the article does not prescribe tie handling. UV
selection plus curved XYZ lifting is an explicit extension, not planar numerical
identity. These distinctions must remain visible in code and delivery claims.

## Existing flags: accepted is not the same as effective

| Existing control | Actual current effect and limitation |
| --- | --- |
| PATCH_FACTOR_MIN/MAX | Affect source curve/domain factor bounds. Both are1.5 in this case; final curve factor is fixed by that clamp. Do not confuse this adaptive factor with the paper's quadtree percentage. |
| CURVE_FACTOR_SENSITIVITY and curve-factor policy | Feed the existing factor calculation. Sensitivity cannot change the final clamped factor while both bounds remain1.5. |
| CURVE_POINT_MIN/MAX/BUDGET_MODE | Count rebuild requires both budget-driven adaptation and point-budget mode. Legacy defaults have budget-driven0; changing the minimum alone does not force extra curve points. |
| SMOOTHING_LAPLACIAN_NUMBER/FACTOR and AFT_LOCAL_POSTPROCESS_* | Reach the original source TRI. The new mixed output has no corresponding pass, so these are not direct final-mesh smoothing controls. |
| QUADTREE_FACE_QUALITY_THRESHOLD, LOW_QUALITY_H_FACTOR and existing depth controls | Affect source-tree paths subject to native policies. They do not implement the missing0.2 clearance stage. |
| USE_TEMPLATE | Original TRI consumes it; research Generate structurally constructs template reference/interior regardless. Do not present a general template-off mixed path as implemented. |

No flag sweep is executed here. Any bounded existing-flag trial must record its
effective values, actual consumer, changed source partitions/tree, boundary
quality and cost. Do not use a setting that has no active consumer or substitute
a new threshold for a missing article stage. Changing adaptive mode activates
multiple policies and is not an isolated single-factor experiment.

## Revised next action and evidence limits

Keep PR240 draft/unmerged. The next implementation item is the documented
contour-clearance classification in the opt-in research path, with a retained
failing witness, coherent source/template/front interfaces and original TRI
preserved. Then complete/qualify mixed smoothing and its effective control
contract, and dispose the M1 center/oracle ambiguity explicitly. Existing flags
are available for bounded source discretization trials; no new balancing law
or full R3 controller is authorized by this audit.

Existing85 local tests and hosted44271951483 four successful jobs still qualify
their exact b3d2fbc implementation scope, not these omitted paper stages. The
current replay tests verify implemented selection/shape/front behavior but do
not require the clearance band or a smoothed mixed result. No native suite was
rerun; input hashes/source anchors and read-only witnesses are recorded. Retain
local WSL publication failures, independent-review and exact integration gates,
full historical M1/M5/R3/M7, continuous validity and memory/documentation limits.
