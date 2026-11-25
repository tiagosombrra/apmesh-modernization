# CurvaBezier operation 81 and its inherited template edge

2026-11-25 Fortaleza. [Machine-readable evidence](evidence/CURVABEZIER_OP81_TEMPLATE_EDGE_20261125.json).

## Native archive diagnosis

The read-only analysis binds the certified CurvaBezier output from
[PR 277](https://github.com/tiagosombrra/apmesh-modernization/pull/277),
head `9aabc278e78d72d72f2e3790fc160874634ff690`. Its four hosted checks
passed, including native Linux and Windows and original TRI equivalence.

The only interior TRI below both diagnostic floors shares its short edge
with seed QUAD 204. The seed belongs to level-4 leaf 161. Its west edge
abuts the level-3 leaf 154, which touches the outer curve and receives no
template. The short segment spans v = 0.8125 to 0.84375 at u = 0.125.
Its birth length is 0.05985 model units. The edge is present in all 81
archived front states from the initial front to the closure. An independent
search found no shape-eligible QUAD for that edge at any such state and
no TRI with a better minimum angle at birth than the one actually chosen
(10.57 degrees). At the actual closure all globally valid apices were
already local. Changing the window or visiting this edge sooner would
need a different upstream front to have better options.

## Local reconnection check

At fixed positions, consider connected cavities of up to five generated
faces whose simple outer polygon contains all their original nodes.
Preserve seed edges, the cavity boundary and TRI/QUAD counts. Require
validity both before and after smoothing at the retained positions.
There were 21 such cavities and 31 nonidentity reconnections that also
preserved the counts by region. None reached both interior TRI floors.
The best two-face reconnection produces an 18.72 degree interior TRI after
smoothing and a TRI shape score of 0.44078. The floors in this diagnostic
are 26.57 degrees and 0.69295. A diagonal flip can move a smaller 8.27
degree TRI into the contour-vertex group, where the lower regional floor
would hide it. This is not an observed quality improvement.

## Projected quadtree adjustment

The parent box [0.125, 0.75, 0.25, 0.875] has four existing level-4
children with seed templates. Grouping them into their level-3 parent
would retain edge-wise 2:1 balance and preserve positive clearance from
the analytic contour. No active size request lies in the parent or the
four neighbor cells whose side masks change. Using the existing template
catalog, the projected parent uses T1 and its west side has two template
edges instead of four. The one covering the offending interval would
grow from 0.05985 to 0.11782 model units. The ratio of median birth TRI edge
length to that side changes from 2.78 to 1.41. The native tree would have
223 rather than 226 leaves and the regrouped parent would carry 4 seed
QUADs in place of 16. This is a projection of the seed partition. It does
not establish the quality or error of the subsequent native mesh.

Await alignment on one opt-in native CurvaBezier trial with the grouping
applied after the established requests and before template dispatch.
Retain the 16 certified contour samples and all current screening,
smoothing and diagnostic floors. Compare the full typed output and all
regional minima, error, growth, and the exact predecessor binding.
The read-only investigation changes no thresholds or native output.
Mixed admission, mixed ownership reentry and global mixed curvature
remain open. Accepted mixed epochs: zero.
