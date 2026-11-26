# Compare the native seed-layer replacement after smoothing

This is the approved order comparison for the
[native one-layer experiment](NATIVE_SEED_LAYER_TRIAL_20261126.md).
[Draft PR 294](https://github.com/tiagosombrra/apmesh-modernization/pull/294)
at `b78c6c6d62f1c63a255e65b7818d3032b3a74b00` adds `replace_seed_layer_after_smoothing`
to the existing opt-in plan. It binds the same per-face and
per-vertex witnesses on the original front, runs the existing
guarded smoothing on its original connectivity, then applies the
specified replacement at the smoothed coordinates. It checks
requests incident to the original and current cavity, preserves
the original directed boundary, and evaluates the new faces with
the existing UV article rule, physical size and shape tests.
All retained UV and XYZ values and node IDs match the smoothed
control exactly. No new position or smoothing pass is introduced
by the replacement. The original analytic curve, size-request
inputs and default TRI path retain their original contracts.

## Results

| Result | CurvaBezier control / early / late | Ribbed control / early / late |
| --- | ---: | ---: |
| Final faces | 731 / 729 / 729 | 541 / 540 / 540 |
| Minimum angle in the replaced region | 3.25° / 15.86° / 16.28° | 11.91° / 25.96° / 23.64° |
| Minimum angle in the full mesh | 3.25° / 3.78° / 3.78° | 11.91° / 11.97° / 11.97° |
| Area-weighted RMS at 48 × 48 | 0.006621758 / 0.006915701 / 0.006622043 | 0.020102640 / 0.020102241 / 0.020102170 |
| Maximum deviation at 48 × 48 | 0.04399112 / 0.04418787 / 0.04399112 | 0.10748411 / 0.10748411 / 0.10748411 |

CurvaBezier's late RMS is about 0.0043 percent above the fixed
control, versus 4.4 percent with the early replacement. The
remaining difference is limited to the changed interpolation.
The late Ribbed mesh preserves the improvement in request 503.
Its final size stays at the control value 0.18923 for target
0.33409. No formerly met size request is lost in either mesh.

Independent checks match the full pre-replacement smooth frames
to the archived control, verify 697 retained CurvaBezier and 525
retained Ribbed vertices, and check every preserved physical node
ID and directed exterior face. Three and one enclosed interface
sites retire. Post-replacement faces meet their local physical
floors. Both whole meshes remain blocked by the frozen admission
profile. CurvaBezier still has 26 contour-vertex TRI, four
contour-edge QUAD and one interior TRI below a safety floor.
Ribbed still has ten contour-vertex TRI and one interior TRI
below a floor. Zero mixed adaptive epochs are accepted.

## Validation and next action

Both early replacement controls reproduce six archived files
each. The late paths reproduce the original five guarded pass
frames, birth frame, guarded final frame and pass journal.
Negative controls refuse a foreign birth site after the
original smooth, a changed directed boundary, an exceeded face
budget and an invalid face arity. Source binding and the direct
three-stage article rollback pass. The 15 progressive tests
and six sizing tests pass on the measured tree. The primary
validation adapter has unavailable local tools and no iteration
baseline. Full-stage qualification and independent review
remain open. [Hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45797258631).
[Exact native receipts and measurements](evidence/POST_SMOOTH_SEED_LAYER_TRIAL_20261126.json).

The approved replacements still use explicit witnessed regions.
Alignment is pending on a bounded automatic cavity selection
trial. Rank faces below the frozen physical floors by their
relative shape deficit, evaluate the first adjacent template
layer, and compare up to one feasible replacement per candidate
on both development models. Retain the curve, sizes, geometry
and growth checks. Shared curves, owner reentry, reserved cases
and the global mixed-curvature error remain open.
