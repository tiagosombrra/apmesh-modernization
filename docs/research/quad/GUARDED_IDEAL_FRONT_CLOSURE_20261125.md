# Guard the ideal point with a paired front closure

[Draft PR 283](https://github.com/tiagosombrra/apmesh-modernization/pull/283)
at `45718e0b3c3e231754e7a250332cac568ab7dc2e` tests the same scientific
proposal on CurvaBezier and Ribbed Bracket. It extends the
[unit-width experiment](LEGACY_IDEAL_FRONT_POINT_20261125.md) by trying
one, one half, one quarter and one eighth of the same native leaf width.
The first TRI has the same eligibility conditions.

For each eligible placement, clone the current ordered front and drain
it twice using the existing TRI/QUAD selection. One closure uses the
original apex and one uses the proposed vertex. Both previews disable
further insertions. Cancel identical oriented faces and compare the
remaining region against the corresponding reference. Require the same
directed patch boundary, valid nonoverlapping facets, and no deterioration
of the minimum physical angle or shape per element family and location
(contour edge, contour vertex, interior). Use the frozen safety floor for
a new family or location. The shape scores are the TRI mean-ratio and the
QUAD minimum scaled corner Jacobian. The numerical tolerance is the
relative 1e-12 convention of the existing smoothing comparison. The first
eligible closure is committed. Each later insertion repeats the comparison.

The native research plan uses `guarded_ideal_closure` with a point cap and
the existing TRI and QUAD angle and shape floors. The point caps are 50
and 31, as in the original trial. The existing contour, request trace,
grouped native leaves, templates, smoothing, growth budget and admission
are fixed for the paired comparison. No separate configuration was fitted
to either model.

| Model and arm | New points | Faces | Final transition TRI below floor | Minimum final transition TRI angle | Area-weighted geometric RMS (48 × 48) |
| --- | ---: | ---: | ---: | ---: | ---: |
| CurvaBezier control | 0 | 704 | 37 | 3.15° | 0.007765 |
| CurvaBezier full width | 2 | 707 | 27 | 1.85° | 0.007882 |
| CurvaBezier guarded | 3 | 710 | 37 | 3.15° | 0.007760 |
| Ribbed Bracket control | 0 | 538 | 14 | 8.06° | 0.017874 |
| Ribbed Bracket full width | 0 | 538 | 14 | 8.06° | 0.017874 |
| Ribbed Bracket guarded | 3 | 544 | 12 | 8.76° | 0.017869 |

The first TRI met its floor for 58 CurvaBezier and 28 Ribbed proposals.
Whole-closure checks refused 55 and 25 of them, respectively. No
unit-width proposal was retained. CurvaBezier's interior TRI minimum
stays at 12.07°, compared with 3.42° with the full-width rule. Ribbed's
minimum transition TRI angle at birth moves from 8.06° to 8.62°.
The guarded candidates keep 17 and 23 contour segments, stay within the
growth budget and improve sampled geometric error against their bound
mixed predecessors. Both remain blocked on shape. Zero mixed adaptive
epochs were accepted.

## Remaining geometric constraint

CurvaBezier's limiting final TRI is already 3.15° at birth, and one edge
joins a seed QUAD. Ribbed's limiting final TRI is 8.62° at birth, and one
edge joins a QUAD created by the advancing front. The two TRI neighbors of
each limiting face provide no valid single diagonal flip. Enumerating all
triangulations of each corresponding three-TRI polygon, with the same
sites and directed boundary, gives one valid triangulation per model,
identical to the observed topology. This is a bounded fixed-vertex
obstruction; it does not imply that a wider mixed region cannot improve.

Next compare a wider mixed region before its closure, with certified
contour and seed-QUAD boundaries held fixed. Align the limited change to
front order before implementing it. Use the same choices on both models
and retain the physical profile as the acceptance check. The shared curve,
owner reentry, reserved validation, accepted epochs and global mixed
curvature error remain open.

## Checkpoint audit

- MSVC 19.44 x64 C++17 Debug built `ap_mesh` and
  `quad_real_boundary_source_contracts`. See the
  [native receipts](evidence/GUARDED_IDEAL_FRONT_CLOSURE_20261125.json).
- Two bound guarded runs staged candidates. The control without insertion
  and the previous unit-width option each reproduced nine artifacts
  byte for byte. An independent Python audit verified the six introduced
  sites, the frozen native inputs and all three comparable mesh arms.
- The direct three-stage article audit exercised rollback and 19 rejected
  forgeries. The original-curve contracts exercised six captures, 54
  source refusals, six certified splits, six unchanged cases and 24
  certificate refusals. Ten progressive controls passed.
- The validation-session adapter still reports unavailable tools and a
  missing local baseline. No native sanitizer qualification or independent
  approval was obtained. [Hosted checks for PR 283](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45704856431)
  were in progress at the checkpoint.
