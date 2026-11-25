# Native TRI/QUAD successor with original curve subdivision

2026-11-25 Fortaleza. Experimental continuation of issue 221.
[Draft PR 269](https://github.com/tiagosombrra/apmesh-modernization/pull/269)
head `219183c7767bf4a1319ee8142db13595a5fd7fe7`, parent `7fea06303d7788c3648eb62a230911adafcc8f12`.
[Machine-readable receipt](evidence/FEEDBACK_SEARCH_AND_CURVES_20261125.json).

## What ran

The input was the recovered native mixed CurvaBezier Step 3. Its typed OBJ
hash is `2579c96ac0945cec621b091eef65ab8a6cd48a3dedd104db8d351f00323bc4f6`.
Its 14 original segments participate in the existing geometric feedback with
half-size seeds, three neighbor passes and the physical size ratio 1.35.
Eight of 13 face requests saturate at the source depth cap of four. Three
direct edits take the balanced native tree from 217 to 226 leaves.

1. The search-only arm kept the refined tree and looked up vertices using
   the predecessor boxes, conditioned on the exact ordered seed and curve
   geometry. The seed faces, all 106 front transactions, smoothing trace,
   UV/XYZ positions and connectivity match the predecessor exactly. This
   isolates the search regression documented in PR 268 for this fixed input.
2. The coupled arm used the refined tree and the ten requested one-level
   binary curve splits. The native original arclength midpoint routine added
   four samples on side 0 and two on each other side. Every predecessor sample
   retains its side, parameter, ID and coordinates. The contour has 24
   segments, with their vertices evaluated on the original Bezier curves.
   Standard smoothing rejects at pass one when face 727 collapses or inverts
   in UV. The rejected arm publishes no staged candidate.
3. From the same initial valid mesh, the previously exercised Ribbed quality
   guard accepts five UV passes. Each pass computes simultaneous targets,
   then visits nodes in deterministic order and tries the full displacement,
   one half, one quarter and one eighth. The fixed contour and existing
   geometric validity checks apply. The native comparison retains pass zero,
   the rejected control, four more guarded frames plus the final state, and
   the attempted-movement counts. The typed staged candidate is
   `d886e75bebfcdf96b6999c61bed3ee6ea8183923de1f6990112e08a9a05c6d90`.

The original source depth limit and default TRI path are preserved. The two
lookup settings and the guarded smoothing arm are scoped to the experiment.
The OBJ source header describes the original capture. Subsequent native leaf
edits are reported in the candidate's separate tree and request receipts.

## Measurements

Geometric deviation is the distance from the mesh interpolant to the
analytical surface at identical UV sample sites. RMS is the square root of the
area-weighted mean of squared distances, in the model's length units. The
sampled maximum uses the same sites. Mixed curvature error and adaptive
admission still need their own qualification.

| Quantity | Recovered input | Successor before smoothing | Guarded successor |
| --- | ---: | ---: | ---: |
| Nodes | 683 | 813 | 813 |
| TRI / QUAD | 100 / 625 | 104 / 748 | 104 / 748 |
| Contour segments | 14 | 24 | 24 |
| Geometric RMS, grid 24 | 0.00948629 | 0.00295536 | 0.00286938 |
| Geometric RMS, grid 48 | 0.00971171 | 0.00304726 | 0.00296791 |
| Maximum sampled distance, grid 48 | 0.04296836 | 0.01937644 | 0.01889585 |
| Minimum TRI angle, degrees | 1.87 | 4.10 | 4.10 |
| Minimum QUAD angle, degrees | 12.17 | 18.57 | 18.57 |
| Maximum size ratio across shared edges | 4.94 | 4.59 | 4.53 |

The final area-weighted geometric RMS drops 69.4% on the finer grid.
The mesh has 17.5% more faces and 19.0% more nodes. Its worst TRI touches the
contour at a single vertex and still measures 4.10 degrees. Among elements
with a contour edge, the minimum TRI angle improves from 9.15 to 14.98
degrees. The corresponding minimum QUAD angle falls from 18.92 to 18.57
degrees. The comparisons by incidence retain counts and medians as well as
the minimum, since the number of boundary elements changes.

Recomputing the approved sizing diagnostic from the staged mixed geometry
yields 21 face and 6 curve requests, compared with 13 and 10 from the input.
None of the face requests retains both the same UV site and the same size.
These new requests are measured and have yet to be applied.

## Validation and next action

Local MSVC x64 Debug C++17 compiled the QUAD application. The directed runner
suite on the final source passed the selection, rejection, recovery, fine
size veto and both original tree-only feedback arms. The source contracts
passed six captures, three reversed captures and 54 negative controls.
Python reporting and recovery checks passed. The same-site comparison checks
analytic surface membership, oriented edge incidence, unit-chart area and
disk incidence. The observed unguarded native rejection is retained.
See the receipt for command invocations, image hashes and exit results.
Draft review and hosted validation are tracked on the exact PR head.

The completed milestone is a valid mixed successor generated from its mixed
predecessor's residual and able to supply a different next set of requests.
There are zero accepted mixed adaptive epochs. Next, establish the scoped
experimental admission rule for a changed contour. Use the measured element
growth, contour-edge QUAD tradeoff and remaining transition TRI as the test
cases for that rule. Then exercise the same generation on a second real
transition and a shared patch edge, with the preserved TRI control, before
claiming repeatable adaptive improvement. The global mixed curvature error
remains open.
