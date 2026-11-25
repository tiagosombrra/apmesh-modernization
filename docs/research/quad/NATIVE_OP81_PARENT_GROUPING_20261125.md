# Native CurvaBezier parent grouping after feedback

2026-11-25 Fortaleza. [Draft PR 278](https://github.com/tiagosombrra/apmesh-modernization/pull/278),
head `e93205007b8f937b72d7b612694cbc8091c637dc`.
[Machine-readable evidence](evidence/NATIVE_OP81_PARENT_GROUPING_20261125.json).

## Scope and source binding

One approved CurvaBezier Step 3 comparison uses the existing selective
requests, certified contour, geometric pair screen, and guarded smoother.
The trial groups parent [0.125, 0.75, 0.25, 0.875] after native feedback
refinement and before template dispatch. An explicit experimental plan
directive protects requests in the affected region, checks 2:1 balance,
and replays the native tree in its ordered identities. It reuses the
grouping primitive of the earlier two-block trial.

The same MSVC x64 Debug C++17 image regenerates the control, grouped
candidate, and refusal control. The ungrouped output reproduces the PR 277
mesh and front trace byte for byte. The grouped arm retains the exact
source binding, all measured request records, and the 16-site contour and
certificate. Only the four specified leaves (158 through 161) are replaced
by their parent. The tree has 226 leaves after refinement and 223 after
grouping. The old west-side seed partition of four edges becomes two. The
edge covering the prior limit grows from 0.05985 to 0.11782 model units.
An injected request inside the selected parent rejects before publishing
a candidate and keeps the source artifact unchanged.

## Measured native outcome

| Metric | Control | Grouped |
| --- | ---: | ---: |
| Nodes | 737 | 713 |
| Elements | 779 | 754 |
| Minimum final interior TRI angle, degrees | 14.36 | 18.16 |
| Minimum final interior TRI shape | 0.37719 | 0.49691 |
| Minimum final interior QUAD angle, degrees | 44.57 | 48.47 |
| Minimum final contour-vertex TRI angle, degrees | 2.27 | 2.27 |
| Global sampled geometric RMS, model units | 0.009079035 | 0.008987707 |
| Maximum sampled geometric deviation, model units | 0.044192185 | 0.044187868 |

The geometric comparison uses both 24 by 24 and 48 by 48 identical UV
sites per arm; the table uses the area-weighted RMS on the denser grid.
RMS is about 1.01 percent lower. The largest adjacent physical size ratio
is unchanged. The old operation 81 TRI is absent. The new limiting
interior TRI is formed at operation 74 on a different seed edge of length
0.05382. Its best admissible birth angle at that chosen base is 17.09
degrees. Guarded smoothing reaches 18.16 degrees. This edge belongs to
leaf 148. Its parent touches the outer contour and is outside the current
interior grouping scope. The existing diagnostic
still blocks on interior TRI angle and shape. CurvaBezier remains a
development case. No numerical admission floor or construction policy was
adopted by this comparison.

## Checks and next action

Local exact-image source contracts pass with the original 54 negative
boundary controls and 24 refinement refusals. The legacy two-block
selection and recovery pass. The combined legacy suite exited at the
forced refusal arm and removed the temporary native logs. The direct
forced refusal and protected-neighbor controls pass on the same image
with retained artifacts. The first build did not compile the deduced one-element
array; the explicit array type resolves it. The prior diagnosis was
published to `quad-templates` after creating a temporary remote reference
to allow the fast-forward, and the five files were verified on the remote.
Hosted checks on the new draft are recorded as observed.

Keep this trial and its remaining veto. Next examine the physical size
field across the boundary-adjacent transition around leaf 148, whose
parent lies outside the tested interior grouping scope. Mixed ownership
reentry, global mixed curvature and
accepted mixed epochs remain open.
