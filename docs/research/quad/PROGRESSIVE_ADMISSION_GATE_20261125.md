# Opt-in progressive assessment of staged mixed feedback

2026-11-25 Fortaleza. [Draft PR 279](https://github.com/tiagosombrra/apmesh-modernization/pull/279)
at `f6ae34715db2c2a9ec98988e468122bf8803f0bf`.
[Machine-readable evidence](evidence/PROGRESSIVE_ADMISSION_GATE_20261125.json).

## Delivered behavior

The researcher chose progression by stages. The single-patch runner now
accepts `--progressive-profile` and enables native boundary certification
for that run. It records an eligible, blocked, or no-action result before
any owner publication. The archive command can repeat the assessment:

```text
python tools/quad_progressive_admission.py --archive <native-run-dir> --profile <profile.json>
```

The assessment binds original TRI, mixed predecessor and native source
tree by SHA-256 before reading the candidate. It checks the candidate
digest, exact replay of the predecessor, native outcome, ordered curve
site placement and certificate contents, and the original analytic
surface. It independently evaluates the common 24 × 24 and 48 × 48
grids, with the existing physical angle, TRI shape and scaled corner
Jacobian. The metadata checks use a trusted portable runner receipt and
verify correspondence to the artifacts.

The JSON requires all safety floors and separate regional targets for TRI
and QUAD, positive minimum relative RMS gain, per-attempt growth limit,
absolute face budget, and geometric stopping targets in model units.
A below-target group may advance if its minimum, count and fraction below
the target do not worsen and all safety floors are met. A newly populated
group must meet its targets. Geometric RMS must meet the gain on both
grids and neither sampled maximum may increase. The report records
whether the evaluated candidate meets both geometric and shape targets.
It also records the largest realized adjacent size ratio. The evaluator
does not own the native mesh or publish an accepted state. Its decision is
a prerequisite for the future native owner transaction.

The scoped delta from PR 278 is five Python and workflow paths. C++ source
and build configuration are byte-identical to that base. The draft
targets the canonical research branch for exact-head CI.
The implementation introduces no numerical default.

## Validation

- All 36 local Python checks pass on the delivered source tree. This includes
  10 progressive controls and the established regional quality, geometric
  reporting and relative feedback tests.
- A fresh CurvaBezier Step 3 run with the opt-in flag uses the exact
  MSVC x64 Debug C++17 image from PR 278. Its original TRI, mixed
  predecessor, source tree, requests, 779-face candidate and certificate
  match the retained native run. The report marks it eligible under a
  deliberately permissive fixture profile, with zero committed epochs.
- Reassessment of the two certified development archives exercises both
  the built-in and indexed Bézier surfaces. The same assessor reports
  no action on the archived zero-request Ribbed run.
- Six detached binding mutations are refused. With an illustrative
  5° TRI safety floor and the previous 10.42% diagnostic growth bound,
  CurvaBezier is blocked by the transition TRI safety floor and Ribbed
  by face growth. These values exercise distinct paths and are not adopted
  as a scientific profile.
- The first archive invocation interpreted cached metadata in a contour
  record as XYZ coordinates and rejected it. Parsing only the documented
  XYZ fields resolves the issue. The validation session planner lacked
  its local baseline receipt. The directed tests and exact retained
  native image supplied the bounded evidence.

[Exact-head hosted run 45671619225](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45671619225)
had four jobs in progress at checkpoint. Independent review and integration
remain pending.

## Next gate

Prepare one numerical profile for alignment, using intended element
quality and cost requirements independent of individual development
results. Evaluate it on the two development cases before reserving
geometries. Integrate the approved decision with a native owner transaction
that retains the exact predecessor on failure and feeds the next iteration
from the accepted mixed state. Establish cross-patch conformity and two
successive accepted epochs before transfer claims. No mixed epoch has been
committed. Global mixed-curvature error remains open.
