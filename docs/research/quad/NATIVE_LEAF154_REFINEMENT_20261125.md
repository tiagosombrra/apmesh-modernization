# Native CurvaBezier refinement on the coarse side of the transition

2026-11-25 Fortaleza. CurvaBezier Step 3 development experiment.
[Machine-readable evidence](evidence/NATIVE_LEAF154_REFINEMENT_20261125.json).

## Paired experiment

The [operation 74 diagnosis](CURVABEZIER_OP74_SIZE_TRANSITION_20261125.md)
projected template coverage when the coarse leaf beside the limiting seed
edge is refined. The approved comparison augments the **ungrouped**
screened successor plan by exactly one tracked request:

```text
face 636 0.09375 0.796875 0.05916342422101073
```

Face 636 is the zero-based predecessor face and the coordinates are in UV.
The last value is the requested physical size in model units. The bound
predecessor, original curve and face requests, 0.045 pair geometry screen,
guarded smoothing and quality diagnostic are reused. The [prior native
grouping](NATIVE_OP81_PARENT_GROUPING_20261125.md) stays a separate arm. Its
protected neighbor check would refuse this request.

The MSVC x64 Debug C++17 image is from [draft PR 278](https://github.com/tiagosombrra/apmesh-modernization/pull/278)
at `e93205007b8f937b72d7b612694cbc8091c637dc`. From the isolated trial
directory the process used `ap_mesh.exe --config successor.conf` with
`APMESH_QUAD_FEEDBACK_PLAN=successor.plan` and a 180-second limit. The
directed run exited zero in 55.79 seconds including the driver. The engine
staged the mixed candidate and the three predecessor artifacts retained
their hashes. The certificate is byte-identical to the control. The same
two native splits take the original contour from 14 to 16 segments, in
the same order and positions. The added request is actionable. Relative
to the ungrouped staged control, leaf 154 alone is replaced by children
302 through 305, bringing the tree from 226 to 229 leaves. The two inner
children each contribute four template QUADs. The children on the contour
contribute none.

## Quality and error

| Final metric | Ungrouped control | Coarse-side refinement |
| --- | ---: | ---: |
| Nodes | 737 | 745 |
| TRI / QUAD | 102 / 677 | 106 / 683 |
| Interior TRI count | 2 | 0 |
| Interior TRI minimum angle | 14.36° | Absent |
| Interior QUAD minimum angle | 44.57° | 58.40° |
| Interior QUAD minimum scaled corner Jacobian | 0.69133 | 0.85165 |
| Contour-edge TRI minimum angle | 10.37° | 10.37° |
| Contour-edge QUAD minimum angle | 19.44° | 19.44° |
| Contour-vertex TRI minimum angle | 2.27° | 2.27° |
| Largest adjacent physical size ratio | 8.93 | 8.93 |
| Area-weighted geometric RMS, model units | 0.009079035 | 0.009014565 |
| Maximum sampled geometric deviation, model units | 0.044192185 | 0.044192185 |

The TRI classified as interior disappear before smoothing. Of the faces
touching the contour, five additional TRI touch it only at a vertex,
one additional TRI shares an edge, and one fewer QUAD shares an edge.
The RMS is the square root of the area-weighted mean of squared distances
to the analytic surface samples. The RMS reduction is 0.71 percent on
2,304 common UV sites. The 576-site comparison also shows a reduction.
The face increase is 1.28 percent versus the reconstructed control. The
existing diagnostic compares growth to the 732-face mixed predecessor and
records 7.79 percent, below its 10.42 percent limit. It reports no veto.
Interior TRI angle and shape are marked absent in both the predecessor
and candidate. The remaining populated regions meet the configured floors.
The worst angle and adjacent size ratio still identify unresolved transition
quality, even though the configured diagnostic has no veto.

## Evidence status and next action

The first local comparison script stopped when it used a list-valued
leaf box as a dictionary key. The corrected comparison uses the same
native artifacts and completed. The native mesh was generated once.
The four checks on the exact PR 278 head pass in
[run 45653182415](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45653182415).
Their scope is the executable revision. This directed trial adds no source
change and is covered by the local native receipt and paired measurements.

The candidate is staged. The diagnostic profile has yet to be adopted for
admission. There are zero accepted mixed epochs. This trial covers one
development geometry and leaves global mixed-curvature error unmeasured.
Prepare a prospective admission and stopping contract using both development
cases, with explicit regional quality, absent classes, geometric error,
growth and rejection rules. Review and align it before choosing a frozen
profile for the reserved cases. Keep shared-curve conformity and two
successive accepted mixed states as required gates.
