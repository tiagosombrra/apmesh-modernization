# Stage a native transition replacement across one template layer

The approved native trial follows the [local projection](SEED_LAYER_TRANSITION_PROJECTION_20261126.md).
[Draft PR 293](https://github.com/tiagosombrra/apmesh-modernization/pull/293)
at `d0fd3bf1f0f39bf8b7b257814f8511ebde4b1e8b` adds the opt-in `replace_seed_layer` directive in
the certified mixed feedback experiment. Its input binds every
removed face and its UV sites to the freshly regenerated front.
Require both front and template faces. Each template must share a
directed edge with the affected front. Replacement faces use
existing sites and preserve the directed cavity boundary.
Check the article QUAD shape rule, all protected requests incident
to the old cavity and the fixed candidate face budget.

The value-level topology compacts unused vertices before any
physical owners or observers are created. Every retired vertex
is enclosed, has no unaffected face and is neither a curve site
nor an inserted protected interior point. Preserve physical node
IDs for all retained vertices, relative order within the existing
face partitions and directed exterior face connectivity. Element
ordinals remain derived from the new array as in the standard
export. Verify full disk incidence, nonoverlap and original
curve identity. Run the existing guarded native smoothing and
remeasure local shape and protected sizes before staging.
The archived pre-replacement frame and retirement map are retained
separately from the new topology. The usual front-operation view
is defined for the unmodified front, so the replacement arm
publishes its actual birth and smoothed frames instead.

## Matched experiment

| Measurement | CurvaBezier control → trial | Ribbed Bracket control → trial |
| --- | ---: | ---: |
| Faces / progressive cap | 731 → 729 / 805 | 541 → 540 / 601 |
| Retired enclosed interface sites | 3 | 1 |
| Lowest angle in selected cavity before smoothing | 2.53° → 15.86° | 11.91° → 25.96° |
| Lowest angle in selected cavity after smoothing | 3.25° → 15.86° | 11.91° → 25.96° |
| Lowest physical angle in whole final mesh | 3.25° → 3.78° | 11.91° → 11.97° |
| Area-weighted geometric RMS at 48 × 48 | 0.00662176 → 0.00691570 | 0.02010264 → 0.02010224 |
| Maximum geometric deviation at 48 × 48 | 0.04399112 → 0.04418787 | 0.10748411 → 0.10748411 |

The rehearsals replace exactly the planned topology in both cases.
Every pre-existing feasible size request stays feasible. Ribbed
request 503, at target 0.33409, measures 0.18923 on the control
and 0.19454 after replacement and smoothing. Its protected interior
point is retained. The matched curve certificates, requests and
native grouping remain byte-identical.

All exterior node coordinates match at birth. The same smoother
runs on different adjacency, so 13 exterior vertices in CurvaBezier
and 11 in Ribbed finish at different positions from the controls.
Their maximum physical differences are 0.04590 and 0.02841,
respectively. This differs from the earlier read-only stitch on frozen
archived coordinates. Both new meshes are staged for research and
both remain blocked by the whole-mesh progressive shape profile.
No accepted mixed adaptive epoch.

## CurvaBezier smoothing diagnosis

The birth RMS changes from 0.00700036 to 0.00700340. Across five
guarded passes the RMS falls to 0.00662176 in the control and
0.00691570 with the replacement. Relative to the smoothed control
the latter is approximately 4.4 percent higher. At identical
48 × 48 sites, approximately 98.7 percent of the net increase in
area-weighted squared deviation occurs outside the original UV
cavity. This partition is by sample position in the birth cavity;
it is not proof that a single node causes the full difference.
The unguarded smoothing arm rejects CurvaBezier pass 1 on a
collapsed or inverted QUAD. The native guarded arm completes all
five passes and supplies the staged output.

Alignment requested for one matched comparison applying the same
guarded replacement after the native smoothing of the unchanged
connectivity. Preserve exterior positions and recheck the local
shape, physical sizes, geometric deviation and full face budget.
This deliberately proposes a changed experimental order. A native
comparison is required before selecting it. Shared curves,
owner reentry, reserved models and the global mixed-curvature
norm remain open.

## Validation and closure

Both no-option controls reproduce eight archived files bit for bit.
Negative arms refuse a foreign UV site, a changed directed
boundary, a tighter face budget and an invalid face arity.
The first Python runner invocation stopped before the engine on
a face-ordinal packing error. The corrected harness preserves that
failure and runs both complete comparisons once. Native source
contracts, 15 progressive tests, six sizing tests and the direct
three-stage article and rollback regression pass. The primary
validation adapter could not resolve its local tools or baseline.
Full closure and independent review remain pending.
[Hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45795875797).
[Native witnesses, commands and hashes](evidence/NATIVE_SEED_LAYER_TRIAL_20261126.json).
