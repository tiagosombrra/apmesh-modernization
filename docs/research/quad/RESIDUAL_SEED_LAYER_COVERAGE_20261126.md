# Residual coverage of the one-layer transition repair

The [automatic repair trial](AUTO_SEED_LAYER_TRIAL_20261126.md)
left both staged meshes below the full-mesh quality profile. This audit
maps every remaining physical safety-floor violation to its native birth
face and checks whether the existing bounded search could repair it.
It starts from the two staged successors at
[PR 295](https://github.com/tiagosombrra/apmesh-modernization/pull/295)
and holds the first repaired region fixed throughout.

## Observed coverage

| Measurement | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Residual faces below a physical safety floor | 31 | 11 |
| TRI sharing a contour vertex only | 26 | 10 |
| QUAD using a contour edge | 4 | 0 |
| Interior TRI | 1 | 1 |
| Already below a floor at birth in the advancing front | 31 | 11 |
| Targets with an individually feasible first witness | 25 | 10 |
| No joint witness in the permitted search | 5 | 1 |
| Retention-trial limit reached | 1 | 0 |
| Individually feasible first witnesses that reduce QUAD count | 25 | 9 |
| Vertex-disjoint first witnesses in severity order | 8 | 5 |
| Residual failures covered by those disjoint witnesses | 13 | 6 |
| Face count after the disjoint witness estimate | 729 → 729 | 542 → 546 |
| QUAD count after the disjoint witness estimate | 644 → 626 | 480 → 470 |

The individual witness search uses the same angle, shape, request
and total face limits as PR 295, with the same limits per target.
It examines 1,923 patches in CurvaBezier and 107 in Ribbed Bracket
when repeated target-patch visits are included. Every successful
witness is checked for directed boundary, coverage area, interior
and exterior non-overlap, protected sites, size requests, local
shape and budget. The actual staged geometry, node IDs, source
curve and native birth ordering match their bound archives.

A feasible alternative for one face can overlap another repair.
The severity-ordered subset above uses the first witnesses and
requires their vertex sets to be disjoint. Its arithmetic gives
one compatible topology estimate. A broader search or a different
choice of witnesses could cover additional failures. This audit
does not compose or stage a batch and does not measure its global
acceptance or geometric error. The two original admissions are
still blocked. Zero mixed epochs are accepted.

All residual failures originate in advancing-front faces that
missed a floor before smoothing. For the four CurvaBezier QUAD
failures, the recorded initial TRI passes the physical floors on
its own, while the archived direct QUAD alternatives provide no
passing substitute for the chosen face. The tested traces for
the remaining TRI also yield no recorded passing alternate
QUAD. The first-TRI observation concerns one face and does not
establish whether the remaining front can close with acceptable
shape after taking that alternative.

## Verification and scientific decision

The four [exact-head PR checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45799331940)
completed successfully, including the frozen TRI comparison and
the hosted Windows native step that invokes the direct article
rollback test. The prior local Windows staging rename failure
remains in its original record. This audit runs only Python
archive measurements. It adds no generation or acceptance rule
and performs no new native candidate run.
[Per-face receipts and search limits](evidence/RESIDUAL_SEED_LAYER_COVERAGE_20261126.json).

The first-feasible rule often spends QUAD to repair local shape.
Compare it against minimizing QUAD loss among eligible witnesses
for the same target and with the same search limits. Use one
replay per development model and preserve the local and global
checks. Await scientific alignment before changing selection
or running multiple repairs. Use the birth witness findings to
guide the advancing-front follow-up.
