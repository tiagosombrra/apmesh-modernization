# Audit of the regional transition validation plan

Recorded 2026-11-24 Fortaleza. Verify remote main, the canonical
research branch and the open research PRs before execution. The mixed
feedback adjacency PR 247 has four successful checks at its recorded
head. The curvature candidate PR 243 remains independent. Neither
certifies the grouping trial or mixed acceptance.

## Finding

The [Ribbed comparisons](RIBBED_AUTOMATIC_TEMPLATE_GROUP_TRIALS_20261123.md)
remove two thin faces and show modest patch-wide improvements. A global
minimum can simply move to a different region. A count of faces touching
the same vertex also changes under reconstruction and smoothing. Use a
fixed UV polygon through every comparison: measure all faces with positive
area overlap there and sample geometric deviation at identical UV sites,
weighted by the analytic surface area. Report the same measurements for
the whole patch. Record physical TRI angle and shape, QUAD angle and
scaled corner Jacobian, neighbor size ratios and exact directed contour
edges. The directed UV cycle comparison is separate from the native
curve-source identity evidence retained in previous trials.

## What was delivered and measured

[Draft PR 263](https://github.com/tiagosombrra/apmesh-modernization/pull/263)
adds a read-only comparator and extends the existing reporting interpolation
to accept fixed source sites. The old global reports match numerically
exactly on eight retained native TRI and mixed meshes. Four new tests and
17 reporting regressions pass on exact remote head 00cac043. The six
paired observations reproduce and the real Ribbed CLI report matches the
programmatic replay. The [receipt](evidence/TRANSITION_REGIONAL_COMPARISON_AUDIT_20261124.json)
binds the output metrics, mesh hashes and commands. Hosted checks on the
draft are independent and are recorded as pending if still running.

| Retained comparison | Regional sites | Minimum regional angle (deg) | Regional area-weighted XYZ RMS | Curve partition |
| --- | ---: | ---: | ---: | --- |
| Ribbed, first automatic group, final | 288 | 6.86298 to 6.86759 | 0.025402 to 0.024574 | Equal |
| Ribbed, both groups, before smoothing | 288 | 6.86298 to 43.44078 | 0.025402 to 0.024213 | Equal |
| Ribbed, both groups, after smoothing | 288 | 6.86298 to 43.44078 | 0.025402 to 0.023821 | Equal |
| Ribbed, reversed regression control | 288 | 43.44078 to 6.86298 | 0.023821 to 0.025402 | Equal |
| Ribbed, single arc split trade-off, final | 364 | 25.33562 to 25.11119 | 0.018735 to 0.005817 | Different |
| Built-in curved Bezier, archived two-block layout, final | 84 | 3.79507 to 8.24212 | 0.015072 to 0.014507 | Equal |

The Ribbed two-group regional maximum also drops, from 0.035168 to
0.034656 in model units. The Bezier change leaves the global minimum
angle unchanged at 1.86988 degrees. A lower RMS can coexist with a
worse regional angle, as seen in the arc split. Its changed contour
makes this case a diagnostic trade-off witness. No common acceptance
decision is implicit in the table. Coverage means observed sampled
geometric deviation and positive overlap; it is not a continuous error
bound or an independent native geometry-qualification matrix.

## Reordered work and scope

1. Review the comparator and attach the fixed-region measurements
   to the next opt-in candidate construction. Record both that region
   and whole-mesh shape/error from the same previous mesh.
2. Add a reversible candidate transaction, preserving the reference
   before any tentative reconstruction. Exercise retention on
   rejected geometry and success on a valid comparison through the
   existing opt-in entry. Align the exact shape/error trade-off rule
   before it can choose the published experimental mesh.
3. Use a fresh second geometry with a curve-to-interior transition
   and a protected fine-resolution control for native qualification.
   The archived Bezier result shows geometry transfer for the
   measurement tool and a previous manually selected layout. It
   does not qualify the automatic selector on a second model.
4. Treat mixed global curvature error and two accepted mixed-driven
   epochs as wider research gates. Keep them separate from regional
   diagnostics, the existing original TRI acceptance and comparison
   against the common analytic sampling grid.

This session changes only read-only reporting tools and evidence.
No new native reconstruction or automatic rollback was executed.
No scientific threshold is chosen. Mixed adaptive epochs accepted: zero.
