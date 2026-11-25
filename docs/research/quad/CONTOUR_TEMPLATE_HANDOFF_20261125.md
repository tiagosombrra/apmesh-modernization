# Protected contour-side template handoff in the mixed generator

2026-11-25 Fortaleza. [Draft PR 281](https://github.com/tiagosombrra/apmesh-modernization/pull/281)
at `acb12e6ba97f3cfeecbc0bde7e57102b56932818`.
[Native evidence](evidence/CONTOUR_TEMPLATE_HANDOFF_20261125.json).

## Combined techniques

Keep the certified binary curve divisions and the [protected interior
batch](INTERFACE_PARENT_BATCH_20261125.md). For each sub-floor transition
TRI that uses a template edge, consider the immediate tree parent if it
touches the contour. Admit a trial parent only with four leaf children,
disjoint interiors, unchanged 2:1 side balance and protection of active
requests in the parent and neighboring leaves. Rank the available parents
by the number of affected TRI and then their UV coordinates for consistent
ties. Project the seed faces using the existing historical templates and
the same clearance policy.

The trial selects five contour parents in CurvaBezier and one in Ribbed.
The native plan adds `group_feedback_contour_parent` records. The old
interior directive still rejects contour parents. The new directive
requires a contour-touching parent. It uses the existing batch tree
operation. The usual template dispatch excludes contour-touching leaves,
so the normal advancing front receives that region. Curves, template
formulas, clearance factor, front selection, smoothing and admission
profile keep their existing implementation.

## Measured outcome

The native source binding, certificate and active request trace match
the preceding batch. The actual replacement parents and counts of seed
QUADs match the projection. Every added contour parent is absent from
the seed QUAD region. The original certified contours have 17 and 23
segments, respectively.

| Prior batch → contour-side handoff | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Tree leaves | 217 → 202 | 115 → 112 |
| Seed QUADs | 645 → 607 | 470 → 455 |
| Final faces | 749 → 704 | 559 → 538 |
| Growth relative to the mixed predecessor | 2.32% → -3.83% | 2.19% → -1.65% |
| Minimum TRI angle in transferred transition regions | 5.65° → 7.75° | 8.04° → 13.57° |
| TRI below the safety floors in transferred transition regions | 8 → 3 | 4 → 1 |
| Minimum TRI angle across the full transition | 3.15° → 3.15° | 8.04° → 8.06° |
| TRI below the safety floors across the full transition | 41 → 37 | 14 → 14 |
| Minimum interior TRI angle | 7.89° → 12.07° | 18.37° → 18.56° |
| Area-weighted RMS at 2,304 common sites | 0.00768472 → 0.00776493 | 0.01732366 → 0.01787416 |
| Maximum sampled deviation at 2,304 common sites | 0.04382005 → 0.04399112 | 0.10748411 → 0.10748411 |

The transferred-area rows count transition TRI with positive UV area
inside one or more selected parents. They count each face once and
allow a different face population after reconstruction. Separate birth
and final measurements are retained in the evidence. The 48-grid RMS
increases by 1.04% and 3.18% versus the preceding batches. Both final
results still reduce geometric RMS by more than 34% against their
actual mixed predecessors and remain below the fixed growth limit.
The unchanged progressive profile blocks both on regional shape.

At the two worst remaining transition faces, independently replay the
actual front and test all active vertices at the chosen base. Of 31
active vertices in CurvaBezier operation 77 and five in Ribbed operation
82, exactly one apex produces a valid TRI in each case. Neither triangle
meets the physical safety floors. This covers the recorded states and
bases. It explains why trying a different visible TRI apex at those
operations cannot repair these two witnesses.

## Verification and next step

Exact MSVC x64 Debug C++17 builds both targets. The prior interior-only
Ribbed plan reproduces seven artifacts byte for byte. Three refusal
controls exercise a contour box given to the interior directive, an
interior box given to the contour directive and a protected contour
parent. All preserve their source and publish no candidate. Ten local
progressive checks and the six native boundary captures pass, with
54 original negative controls and 24 certification refusals. The
local validation plan wrapper lacks its baseline receipt.

[PR 280 exact-head checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45682472818)
all pass. [PR 281 exact-head run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45688349735)
is in progress at checkpoint. Independent approval, accepted mixed
owner reentry, shared curves and reserved-model qualification are open.

Next compare how the front could obtain quality-compliant physical
candidates before these narrow closures. The aligned profile leaves
101 faces of integer budget on CurvaBezier and 63 on Ribbed. Use the
observed space before closure to formulate a bounded interior-point
proposal on the analytic surface with certified contour and existing
validity checks. Align its placement rule before native implementation.
No accepted mixed epoch.
