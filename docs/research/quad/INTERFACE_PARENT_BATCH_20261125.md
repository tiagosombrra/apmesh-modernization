# A common protected template batch meets the face budget on both models

2026-11-25 Fortaleza. [Draft PR 280](https://github.com/tiagosombrra/apmesh-modernization/pull/280)
at `3e01614c6e0559cc001bbed00984957dab3c12b5`.
[Machine-readable evidence](evidence/INTERFACE_PARENT_BATCH_20261125.json).

## Scope and selection

Start from the [two coordinated native controls](COORDINATED_TRANSITION_SIZING_20261125.md)
and their certified 17- and 23-segment contours. Scan the whole
contour-vertex transition in each mesh at birth. For each TRI below the
frozen safety floors, look for a short shared seed edge. Project the
immediate parent of its template leaf. Require an interior parent,
four leaf children, positive contour clearance, protected requests,
2:1 side balance, and a longer replacement edge below the longer incident
physical contour chord. Match the existing rule on both models. Among
eligible disjoint parents, consider first the ones covering the most
affected TRI, then larger physical size mismatch, then tree coordinates.
Verify the combined leaf set again. These are selection rules for the
directed development comparison.

The projection selects two more parents on CurvaBezier and five more on
Ribbed, in addition to their earlier protected parent. The individual
projections cover 12 and seven TRI from the input interface. Many other
parents touch the contour and fall outside the existing grouping scope.

The native application now accepts more than one `group_feedback_parent`
directive. It validates disjoint interiors, checks requests against
the original realized leaves before modifying the tree, and applies
all groupings in one tree reconstruction. It retains the original
single-parent receipt and writes the parent list when there are several.
The scoped delta from PR 279 is the experimental application translation
unit. The original planning metric, templates, AFT, smoothing and
[progressive profile](profiles/progressive_admission_development_v1.json)
are reused.

## Native results

| Measurement, coordinated control → batch | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Leaves | 223 → 217 | 130 → 115 |
| Elements | 782 → 749 | 635 → 559 |
| Growth relative to the mixed predecessor | 6.83% → 2.32% | 16.09% → 2.19% |
| Minimum transition TRI angle | 2.47° → 3.15° | 6.86° → 8.04° |
| Transition TRI below safety | 47 → 41 | 19 → 14 |
| Minimum interior TRI angle | 7.89° → 7.89° | 18.37° → 18.37° |
| Largest adjacent physical size ratio | 8.66 → 7.63 | 5.51 → 4.46 |
| Area-weighted RMS at 2,304 common sites | 0.00818118 → 0.00768472 | 0.01734660 → 0.01732366 |
| Maximum sampled deviation at 2,304 common sites | 0.04419218 → 0.04382005 | 0.10748411 → 0.10748411 |

Both cases stage, fit the 10% growth limit and retain byte-identical
predecessor source attachments, contour certificates and request traces.
The exact leaf differences match the projections. The frozen profile
still blocks both candidates on regional shape. Shape is now the
remaining admission gate in these results.

Of the 41 remaining sub-floor TRI in CurvaBezier, 25 share a template
edge whose immediate parent touches the contour. All 14 in Ribbed have
this relationship. The current interior grouping directive excludes these
parents. CurvaBezier's absolute worst TRI has an interior supporting
parent. Both constraints need to be visible in the next sizing proposal.
A single additional interior group cannot address the shared remaining
blocker.

## Verification and next action

The existing MSVC x64 Debug C++17 configuration builds the changed
translation unit. Scope retains the existing compiler warnings. The
first staged check could not locate its formatter. With the configured
tool available it identified a formatting difference. Applying
clang-format on the changed file and rerunning the staged checker passed.

Directed native checks include both batches, byte-exact compatibility
on seven files for a one-parent plan, rejection of one duplicate parent,
and rejection of a disjoint parent containing a protected request.
The refusal controls preserve their original source and publish no
candidate. Native boundary contracts pass six captures with 54
negative controls, six certified splits and six unchanged cases with
24 refinement refusals. Ten local progressive assessment checks pass.
The validation plan wrapper lacks its local baseline receipt.

[Exact-head hosted run 45682472818](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45682472818)
has four jobs in progress at checkpoint. Independent approval remains
open. No merge, mixed epoch acceptance or reserved-model validation.

Next project a common contour-adjacent template handoff under the
existing clearance and active request rules. Measure it first on the
25 and 14 identified TRI and test the resulting full meshes against
the same growth and shape profile. The next acceptance milestone is
one native mixed successor whose shape also passes the profile.
