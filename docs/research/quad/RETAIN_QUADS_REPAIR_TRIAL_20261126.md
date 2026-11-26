# Rank eligible transition repairs by retained quadrilaterals

[Draft PR 296](https://github.com/tiagosombrra/apmesh-modernization/pull/296)
at `7f131022b6f6d9b7c3c184241a0bf7ec742e5b7c` adds the opt-in
`--retain-quads` option to `tools/quad_auto_seed_layer.py`.
The default still returns the first feasible repair. The comparison
fixes that target and searches eligible replacements with the same
limits. It ranks by net QUAD loss, then by the number of faces in
the replacement, then by the minimum relative physical quality
margin. Exact ties keep the first encountered witness. The original
witness stays available when the search reaches a bound. Native
topology, curve, shape, size, and total face checks still apply.

## Matched results

The CurvaBezier ranked search inspected 422 patches and hit the
original limit of 1,024 retention trials. Across three eligible
witnesses, its best-ranked plan was identical to the first-feasible
plan. The verified archival native result therefore applies to both
choices. It preserves 644 QUAD and 729 total faces with a local
minimum angle of 17.07 degrees. The bounded result leaves open
whether a better witness exists outside the measured prefix.

The Ribbed Bracket search inspected 745 patches and recorded
9,553 eligible witnesses within the bounds. Both choices replace the
same four native faces and retire the same enclosed site. The first
repair creates five TRI. The ranked repair creates one TRI and
two QUAD. Its single native replay confirms the following.

| Measurement | Untouched staged control | First feasible | QUAD retention |
| --- | ---: | ---: | ---: |
| Minimum angle in the same repair region | 11.91° | 16.44° | 24.69° |
| Minimum angle in the entire mesh | 11.91° | 11.97° | 11.97° |
| Total faces | 541 | 542 | 540 |
| QUAD faces | 483 | 480 | 482 |
| TRI below a safety floor | 12 | 11 | 11 |
| Area-weighted RMS on the same 48 × 48 grid | 0.020102640 | 0.020102451 | 0.020102545 |
| Maximum sampled geometric deviation | 0.107484106 | 0.107484106 | 0.107484106 |

The 26 ordered curve sites, 525 retained node IDs and coordinates,
537 exterior faces, original smoothing frames, and all 11 previously
met size requests match. The ranked candidate has the same full-profile
blockers as the first-feasible candidate. Both development models
still have zero accepted mixed epochs.

## Validation and next action

The 10 selector, 15 progressive, and six sizing controls pass.
Both default plans reproduce the exact earlier bytes. The two
ranked plan receipts reproduce on the delivery tree, including
the CurvaBezier fallback. The Ribbed candidate runs with the
existing MSVC 19.44 x64 C++17 Debug executable. No native source
changed and this round stages only the changed Ribbed candidate.
The local validation adapter reports unavailable tools and a missing
baseline. Prior rollback evidence retains its original scope. Full
qualification and independent review remain open.
[Exact evidence](evidence/RETAIN_QUADS_REPAIR_TRIAL_20261126.json).
[Exact-head CI](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45804722207).

The local Ribbed improvement and the CurvaBezier fallback support
retaining the optional comparison as evidence. The
[birth-face audit](RESIDUAL_SEED_LAYER_COVERAGE_20261126.md) points to
the next scientific decision. Compare the current advance with an
opt-in choice that tests the existing initial TRI when the eligible
QUAD fails the existing physical floors and the TRI passes. Use the
same contour, article UV limit, and full-mesh guards. Align this
choice before implementation, then check whether the downstream
front trades the first improvement for later poor faces.
