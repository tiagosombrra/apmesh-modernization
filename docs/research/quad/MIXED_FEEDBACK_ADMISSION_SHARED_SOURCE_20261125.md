# Mixed feedback admission comparisons and shared curve capture

2026-11-25 Fortaleza. Experimental follow-up to [issue 221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).
[Machine-readable observations](evidence/MIXED_FEEDBACK_ADMISSION_SHARED_SOURCE_20261125.json).

## Comparable measurements from archived native meshes

Reevaluate the three typed OBJ files on each source surface with the same
24 by 24 and 48 by 48 UV samples. The controls are the original TRI from
the corresponding accepted TRI step and each guarded experiment's own
mixed input. The existing evaluator checks geometry against the source,
oriented incidence, chart coverage and connected disk topology. RMS is
the square root of the area-weighted mean squared distance, in the
model's length units.

| Model and step | Original TRI faces / RMS | Mixed input faces / RMS | Residual successor faces / RMS | RMS reduction from mixed input |
| --- | ---: | ---: | ---: | ---: |
| CurvaBezier 3 | 430 / 0.009566 | 725 / 0.009712 | 852 / 0.002968 | 69.4% |
| Ribbed Bracket 12, step 2 | 278 / 0.024733 | 547 / 0.027488 | 648 / 0.017369 | 36.8% |

These are the retained [CurvaBezier](FEEDBACK_SEARCH_AND_CURVES_20261125.md)
and [Ribbed residual-only](RIBBED_PREFRONT_SHAPE_TARGET_20261123.md)
native candidates. No new remesh was run for this numerical comparison.
The source and successor OBJ hashes match their recorded experiments.
Each row uses its own analytic surface and an identical set of sites across
the three arms. The successor reduces maximum sampled distance as well as
RMS in each row. Face growth from the mixed input is 17.5% and 18.5%.
The worst size contrast across adjacent faces improves in both models.

| Regional angle in degrees | CurvaBezier input to successor | Ribbed input to successor |
| --- | ---: | ---: |
| Minimum TRI, contour vertex only | 1.87 to 4.10 | 3.79 to 6.33 |
| Minimum TRI, contour edge | 9.15 to 14.98 | 13.90 to 25.40 |
| Minimum QUAD, contour edge | 18.92 to 18.57 | 26.18 to 25.34 |
| Median minimum QUAD angle, contour edge | 20.63 to 32.39 | 26.52 to 31.86 |

The lower QUAD minimum matters because the experiment creates new contour
faces. The more favorable median does not remove the limiting elements.
Exactly one new contour-edge QUAD lies below its preceding minimum on each
model (one of 12 and one of 14). In both cases it touches a chart corner
and has zero UV area overlap with the former worst contour QUAD. Ribbed also adds interior TRI and lowers their minimum angle from
26.57 to 18.37 degrees. A regional rule requiring every minimum to be
nondecreasing would reject both candidates. A rule based on global
deviation alone would miss the local deterioration. These are empirical
tradeoffs for deciding admission. No tolerance, growth budget or rule was
adopted. Global curvature and mixed adaptive acceptance are open.

## Original shared curve source

[Draft PR 270](https://github.com/tiagosombrra/apmesh-modernization/pull/270)
head `dc6025e8f676bb6d6a850fd78a992d5a87ff7fbf` adds the opt-in native
`quad_real_boundary_source_contracts --shared-source <config>` witness.
It checks the actual `PatchReader` shared curve object and observes the
original TRI generator's native boundary capture on each patch. It joins
captures to their local selection, selected domain and same original
accepted outer attempt only when both sources reach that point. The
existing default contract path is preserved.

- **Ribbed patches 2 and 8** are a reindexed excerpt of the original model,
  with both exact control nets. They share the two-owner curve identified
  in the earlier size-contrast audit. The original TRI run stops at step 0
  with eight elements and zero estimated error. The witness exits 1 due
  to absent later source captures. There is no mixed seam comparison.
- **Curved aligned pair** comes from the existing M4 indexed Bézier test.
  The native source witness reaches domain generation and exits 1 at the
  second patch's capture. The original adjacent curve samples disagree
  in source ID at corners 0 and 3 (21/12 and 26/14). At all four corners the componentwise
  XYZ differences are exactly zero. The original capture invariant
  rejects the different IDs. No mixed boundary split or mesh is produced.
- **Uninstrumented TRI**, using the same curved pair and fixed-1.5 profile,
  exits zero and accepts steps 0 through 3. Independent face-incidence
  inspection verifies matching XYZ and opposite traversals across 1, 4,
  16 and 64 seam edges. Both endpoints have differing IDs at step 0.
  At steps 1 through 3 the low endpoint retains different IDs (12/21,
  47/74 and 431/524). No other site differs in ID at these later steps.
  The failure of the all-ID equality assertion is retained alongside
  the successful XYZ and orientation checks.

The capture and the accepted TRI output both show why physical seam
conformity cannot be inferred from patch-local corner IDs. Further
work must retain each original curve record and the actual TRI contour
owner ID as distinct provenance. Identify the native source and
patch-local contour explicitly, qualify that representation against
the curved positive control and forged IDs or displaced positions,
then exercise one original shared subdivision on both sides before
claiming mixed seam feedback. Keep scientific admission open until
growth and regional shape policy are aligned.

## Validation

Exact local MSVC x64 Debug C++17 builds the diagnostic target. Its default
run passes six original source captures (three reversed) and 54 negative
controls. The two opt-in failures above are expected measured blocks
on the final executable. The earlier prefixes and uninstrumented
positive TRI result are recorded by hash. The validation session planner
was unavailable because the local baseline receipt was absent. The bounded
native commands used the established compiler profile directly.
At checkpoint the exact draft head had 1 successful, 3 pending and 0 other hosted jobs. Independent review,
mixed shared-curve construction, native multipatch memory/rollback
qualification and accepted mixed epochs remain pending.
