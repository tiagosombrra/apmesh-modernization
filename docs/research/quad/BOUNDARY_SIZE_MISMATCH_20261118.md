# Straight-boundary size mismatch in the actual mixed output

Later same-day correction: the user rejects a new balancing law. The
[direct article/source audit](ARTICLE_CONFORMANCE_REVALIDATION_20261118.md)
identifies missing documented contour-clearance and mixed-smoothing stages.
The measurements below remain valid; the proposed new-controller follow-up is
withdrawn from the execution queue. Use the latest STATE/roadmap for next work.

Date: 2026-11-18. Read-only audit of candidate b3d2fbc, draft PR240.
Canonical entry894a71a; no source, acceptance policy, native test or mesh changes.
[Per-interval physical measurements](evidence/BOUNDARY_SIZE_MISMATCH_20261118.json).

## Observed cause

All three geometrically straight source curves retain three points/two intervals
at all three adapted stages. Each physical interval has length1.0 in this model.
The original curve pass emits parameters0/1; the surface pass restores0/0.5/1;
the final budget retains those three. The curved side grows3->5->9 points.
The straight partitions are not trimmed by the mixed contraction: the source
curve/surface workflow produces them, and the mixed path preserves them exactly.

For each actual one-owner boundary edge, find its incident mixed face and the
nearest native interior QUAD layer through shared-edge face adjacency. Measure
that layer's physical vertex extent projected onto the boundary chord tangent.
Compare the boundary chord with the median width of that nearest native layer.
All values below use XYZ lengths, not a raw UV/XYZ comparison or global counts.

| Stage | Points on each straight curve | Straight interval/native tangential width | Minimum physical corner angle of a straight-boundary incident face |
| --- | ---: | ---: | ---: |
| 1 | 3 | 3.74-4.26 | 38.46 degrees |
| 2 | 3 | 7.32-7.68 | 20.83 degrees |
| 3 | 3 | 13.26-15.35 | 8.11 degrees |

Stage3 straight-boundary TRI have normalized quality about0.223-0.226 (one is
equilateral), boundary base1.0 and physical altitude about0.10. The curved side
has boundary/native tangential width ratios3.07-3.79 at the same stage. Interior
refinement progresses without compatible straight-side tangential refinement;
the transition must connect long boundary bases to much shorter interior edges.
These measurements demonstrate a local size mismatch and degrading incident
shape, not just a rendering defect. They do not isolate every source of poor
quality: ordering, available candidates, UV-to-XYZ distortion and no mixed
smoothing can also affect the result. No global uniform-density target follows.

## Existing feedback and the missing link

`Adapter::AdaptCurveBySurface` already compares analytical surface curvature with
discrete nodal curvature from the original TRI state. It is incorrect to say
that surface contribution is entirely absent. However, it does not consume the
actual mixed candidate's boundary-face quality and nearby native QUAD size.
The research mixed output still has zero accepted mixed adaptive epochs.

`ComputeCurveAdaptationFactor` combines patch factors/error weights rather than
local actual mixed interval quality. `ComputeCurveDomainBalance` returns neutral1
when target_patch_h is unavailable; that is not measured proof of compatibility.
Several structural responses are stable-mode-only, while this case is legacy.
The new front uses existing nodes and preserves source intervals, so it cannot
subdivide a long boundary edge on its own. QUAD shape rejection can retain a
topologically valid slender TRI; current validity gates do not prove balanced size.

## Concrete quality follow-up

Retain PR240 review and exact integration requirements as the one active item.
This finding becomes an explicit quality limitation in that review. The next
functional generation package should implement opt-in boundary/transition size
coupling before the full R3 mixed-error controller; local quality feedback need
not wait for the entire adaptive estimator/accepted-state milestone.

1. Attribute actual mixed face quality and nearby directional physical sizes to
   each original curve interval, preserving source/patch/generation identities.
2. Where a geometrically justified interior is too fine for the boundary and
   transition quality is poor, request local curve size compatible with both
   geometric error and neighboring mesh needs. Straight intervals can require
   extra points for element quality even with exact geometric representation.
3. Feed requests to the original analytical curve discretizer and synchronize
   shared curves. Rebuild affected native quadtree/templates and mixed fronts;
   do not edit final OBJ faces or introduce disconnected boundary subdivisions.
4. If fine interior size is not justified by geometry/accuracy, damp that local
   interior request instead. Grade neighboring sizes and bound per-step changes
   to avoid indiscriminate flat-region refinement, oscillation and node explosion.
5. Compare boundary angles, quality, size ratios, source error and node cost on
   the same case, including accepted/rejected choices and rollback. A topology
   pass alone does not demonstrate this quality improvement.

These are scoped scientific-policy proposals, not adopted numerical rules.
Ratio/quality thresholds, grading, growth limits and hysteresis still require
explicit scientific alignment. No arbitrary ratio or new default is selected.
Retain original TRI, current qualified candidate outputs and negative evidence.
