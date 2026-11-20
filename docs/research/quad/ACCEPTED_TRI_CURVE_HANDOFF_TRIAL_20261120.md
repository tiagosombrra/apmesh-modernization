# Accepted TRI curvature handoff trial and final mixed quality

20 November 2026, Fortaleza. The researcher approved one opt-in replay after the [surface-curve provenance trace](SURFACE_CURVE_SPACING_QUALITY_TRACE_20261120.md). The MSVC C++17 trial uses a separate local build and changes the data consumed by the Step 2 surface pass for the single Bézier patch. The native analytical channel selection, sizing formulas, neighbor restriction, mixed front and acceptance are the existing implementations. The trial reads signed discrete values from the accepted TRI contour by identity and exact position. At new parameters, it linearly interpolates both channels between the two enclosing accepted sites on the same side. The instrumentation and trial were retained locally as experimental source and are outside the tracked application tree.

The native trial exited zero in 42.31 seconds under the existing 180-second limit. An independent audit verifies all 24 exact side incidences and all eight interpolated sites, the effective values actually consumed in 28 intervals, and equality of all four Step 0/1 OBJ files to the legacy control. The publication matches its accepted Step 1 archive exactly. The scientific outcome is negative for this candidate. The correctly wired data do not produce a better accepted mixed history.

| Step 2 measurement | Legacy control | Accepted TRI handoff |
| --- | ---: | ---: |
| Curved-side points after surface pass | 65 | 65 |
| Straight-side points after surface pass | 17 / 17 / 17 | 18 / 17 / 17 |
| Contour intervals | 112 | 113 |
| Mixed nodes | 953 | 954 |
| Original TRI curvature error | 0.382516 | 0.381381 |
| Original TRI decision | Rejected | Rejected |

All 28 requested length ratios change from the uniform `0.296985` of the previous run. They range from `0.257–0.398` on the curved side in the trial, yet the curve still emits 65 points. The three straight sides change their requests as well, and only side 1 emits one extra point. The counts are complete before the neighbor restriction in both cases. The existing binary subdivision therefore absorbs most of the continuous size changes in this fixture. This observation does not show that the same ratios always yield the same partition. The TRI accepted Step 1 error is still `0.125829`. Steps 2 and 3 in the trial are rejected for increased global error. The publication remains the same accepted mixed Step 1 mesh with 165 nodes, 138 QUAD and 32 TRI.

## Physical shape and the remaining target

Across the two rejected Step 2 mixed candidates, the worst contour TRI stays at `13.66°` with a minimum triangle quality of `0.385`. The worst contour QUAD stays at `38.43°` with minimum corner scaled Jacobian `0.389`. The vertex-only TRI minimum stays at `38.34°`. The audit retains the per-type and per-region observables and both phases of smoothing. The angles and corner Jacobians assess physical shape. The ratio of longest to shortest edge also detects elongation even where angles look reasonable.

The retained *accepted-source* fixed `1.5` snapshots give a separate clue. At Step 2, the worst QUAD touching a contour edge has minimum angle `23.28°` and corner Jacobian `0.394` before smoothing. After the first pass the corresponding regional minima become `16.24°` and `0.158`. After all five passes they are `15.64°` and `0.224`. Over the same sequence, the vertex-only TRI angle improves from `4.82°` to `9.59°`. At Step 3, its worst vertex-only TRI starts at `1.42°` before smoothing and finishes at `1.87°`. Replaying the existing frames therefore identifies both a shape problem already present when the mixed transition is built and a separate smoothing tradeoff. The regional minima need not belong to the same face at each pass.

The Step 3 worst pre-smoothing triangle is face 730 in the archived commit OBJ, created at advancing-front commit 106. It connects the straight-side midpoint `(0, 0.5)` to an exposed template edge from `(0.125, 0.125)` to `(0.125, 0.15625)` in UV. Its physical longest-to-shortest edge ratio is `15.08`. The front records two ineligible QUAD alternatives. After smoothing, the worst angle belongs to face 672 near the `(1, 1)` corner, created at commit 48. These are distinct witnesses.

Close this handoff experiment and retain the negative result. The next bounded step is to trace the two front commits against the neighboring native sizes and prepare a local transition proposal around the template interface with the original contour retained. Scientific alignment precedes changing that geometry or choosing a local sizing rule. Keep the legacy TRI source and use the final physical shape after smoothing as a decision input. Candidate evidence must include minimum/maximum angles, edge ratios, TRI `q`, QUAD corner `J`, region tails, growth and source acceptance. No new acceptance limits are established here.

The [evidence](evidence/ACCEPTED_TRI_CURVE_HANDOFF_TRIAL_20261120.json) includes hashes, commands, interval mapping, native lineage and all quality summaries. This session includes local configuration/build and native observations. It does not qualify any application change or a new baseline CTest/CI revision. The mixed global error is still unavailable, and accepted mixed adaptive epochs remain zero.
