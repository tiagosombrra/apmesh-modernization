# M1 — primary-source integrity, Figure 7 review and numerical centroid decision

**Review date:** 2026-11-10. **Scope:** scientific primary-source verification and research-only shape comparison. **Adviser approval:** not yet recorded.

## Primary source independently retrieved and verified

A new authenticated live read of the user's personal Google Drive original `1993_Bento_SIBGRAPI_Combinacao_das_Tecnicas_Templates_Quadrilaterais.pdf`, [Drive source](https://drive.google.com/file/d/1dYBOU5Q-pFRBlmFXB3iWqQaPFdd2ClzA/view), yielded **5,439,448 bytes**, **seven A4 scanned pages** and verified SHA-256 `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`. This exactly matches the pre-existing local-paper metadata in `evidence/M1_FIGURE7_TRANSCRIPTION_20261108.json`. The prior statement that the Drive bytes were unverified is superseded **for this exact file**, not for arbitrary copies.

At PDF page 4 / printed page **288**, an independent visual inspection of **Figure 7** found six left-to-right lower-row intermediate polygon patterns consistent with the repo's proposed CCW polygon cycles, including the central three-edge junction in column 2, N/W transition in column 3, W/E horizontal split in column 4, W-to-S oblique segment with **no O center in column 5**, and the complete four-way split in column 6. The paper does **not print T1..T6 labels**: the mapping `T1,T2,T4,T3,T5,T6` is the current repository classifier's internal convention, not a historical caption. This is **assistant visual source corroboration**, not adviser sign-off of the reconstruction.

The accompanying paragraph describes edge midpoints, then an inserted point at the **polygon centroid** linked to those midpoints, citing Baehmann (1987). The original does not give the centroid's numerical equation, implementation tolerance, accepted nonconvex cases or numerical failure behavior. On page 291 it cites Baehmann et al., *Robust, Geometrically Based, Automatic Two-Dimensional Mesh Generation*, IJNME 24, 1043–1078 (1987); publisher record: [DOI 10.1002/nme.1620240603](https://doi.org/10.1002/nme.1620240603). **The referenced 1987 full text has not been examined**, so no undocumented implementation rule is imported.

## Interpretation of polygon centroid

In standard planar geometry, the centroid of a **filled polygonal region** is its signed-area centroid, unlike the arithmetic mean of vertices. Thus signed-area centroid is the stronger **mathematical interpretation of the 1993 wording**, but the wording alone is not proof of the original software's formula. The two existing research-only point witnesses remain independently selectable; neither becomes an approved scientific rule or a production default.

Independent rational golden points already checked:
- T2 `ABOW`: arithmetic mean `(3/8,1/4)`; signed-area centroid `(7/18,2/9)`.
- T5 `WSND`: arithmetic mean `(1/4,5/8)`; signed-area centroid `(5/18,11/18)`.

## Quantitative experiment: normalized Figure 7 templates, not curved physical meshes

[Reproducible analysis](../../../tests/quad/test_m1_point_rule_quality.py) uses exact rational proposed coordinates, constructs the same conceptual four-corner witnesses for both rules, and measures the **smallest signed normalized corner Jacobian** (corner sine) of each generated QUAD. The experiment checks eight D4 symmetries per six patterns per two rules (**96 comparisons**), independent golden values and metric invariance. It complements, but does not replace, independent topology/UV tests.

| Proposed class | Theoretical quads | Worst corner sine, both rules | Mean element-worst sine, vertex mean | Mean element-worst sine, area centroid |
| --- | ---: | ---: | ---: | ---: |
| T1 | 4 | 1.000000 | 1.000000 | 1.000000 |
| T2 | 11 | 0.600000 | 0.765486 | 0.753073 |
| T4 | 12 | 0.707107 | 0.867178 | 0.855799 |
| T3 | 8 | 1.000000 | 1.000000 | 1.000000 |
| T5 | 11 | 0.600000 | 0.837935 | 0.831728 |
| T6 | 16 | 1.000000 | 1.000000 | 1.000000 |

These data give **no winner by the worst-corner metric** on the six normalized configurations, because the minima are identical for both rules. The arithmetic mean slightly increases the mean of individual element worst-corner sines in T2, T4 and T5; this by itself cannot determine the historical algorithm or performance in curved/physical and adaptive meshes. The metric is an angle-based local proxy, **not a complete finite-element scaled Jacobian/signed area or a numerical error convergence study**.

## Explicit next adviser decision

1. Confirm the graph-by-graph Figure 7 reading and the internal source-class mapping, without claiming the paper itself labels T1..T6.
2. Decide whether the 1993 reference to a polygon centroid should be operationalized as **signed-area centroid**, or whether independent reading of Baehmann et al. (1987) or source code supports another formula.
3. State admissible source geometry, tolerance scaling, strict-CCW/convexity, nonfinite/degenerate and boundary treatment.
4. Separate the historical reproduction decision from an optional second experiment comparing mesh quality, improvement strategies and element distortion after UV→XYZ mapping.

**Decision status:** historical scan identity and lower-row Figure 7 correspondence verified for this exact file; numerical formula selection and adviser acceptance remain **OPEN**. No production QUAD, patch ownership, boundary or 3D output is authorized.
