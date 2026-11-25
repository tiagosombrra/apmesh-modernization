# Portable native mixed feedback on two original Bézier sources

2026-11-25 Fortaleza. [Draft PR 271](https://github.com/tiagosombrra/apmesh-modernization/pull/271)
head `e470cbe2ccc249bb6b3ea39fcd1915e3066d941b`.
[Machine-readable measurements](evidence/PORTABLE_MIXED_FEEDBACK_20261125.json).

## Executable scope

One experimental runner consumes the source geometry and an explicitly
requested accepted TRI step. It runs the original curve and domain
workflow, locates the matching accepted source attempt and builds a typed
mixed predecessor with the retained guarded smoothing arm. It computes
the existing geometric sizing pilot with the actual source evaluator.
The second native invocation replays and compares the original TRI and
mixed OBJ bytes and the native tree cell and order binding before applying
requests. Typed source curves in the OBJ keep the original parameters,
IDs and coordinates. The replay verifies retention of the original TRI
owner; the native feedback transaction also verifies the mixed predecessor
while staging the successor.

The same MSVC x64 Debug C++17 binary runs CurvaBezier at accepted Step 3
and the original indexed control net of Ribbed Bracket patch 12 at accepted
Step 2. This path requires one Bézier patch. The CurvaBezier predecessor
in this run is the ordinary area-centroid mixed reconstruction with
guarded smoothing. Its earlier PR 269 grouped predecessor is a distinct
experiment. Ribbed produces exactly the same UV, XYZ and oriented face
connectivity as the earlier isolated native Ribbed experiment, for both
the mixed predecessor and successor.

| Native measurement | CurvaBezier | Ribbed Bracket patch 12 |
| --- | ---: | ---: |
| Original curve segments | 14 to 21 | 14 to 22 |
| Native leaf count | 223 to 229 | 112 to 133 |
| Direct leaf edits | 2 | 7 |
| Face requests capped / total | 6 / 11 | 1 / 17 |
| Mixed face count | 732 to 796 | 547 to 648 |
| Geometric RMS, common 48 by 48 UV samples | 0.011915 to 0.008071 | 0.027488 to 0.017369 |
| Geometric RMS reduction versus mixed source | 32.3% | 36.8% |
| Maximum sampled geometric distance | 0.049974 to 0.044192 | 0.125618 to 0.107496 |
| Minimum physical TRI angle | 1.42 to 2.47 degrees | 3.79 to 6.33 degrees |
| Minimum contour-edge QUAD angle | 19.44 to 18.57 degrees | 26.18 to 25.34 degrees |
| Maximum adjacent face size ratio | 12.24 to 8.66 | 6.19 to 5.67 |

Area-weighted RMS describes physical deviation from the analytic surface
on the same grid, in model length units. The original TRI controls on this
grid use 430 and 278 faces, with RMS 0.009566 and 0.024733 respectively.
Their smaller budgets preclude an efficiency conclusion. The mixed
successors grow by 8.7% and 18.5% relative to their own mixed inputs.
Guarded smoothing completes five valid passes on each successor. The
unguarded controls reject at pass one (faces 680 and 562), preserving
the actual failed alternatives. The worse QUAD shape at the contour
continues to matter for an admission rule.

The new meshes independently supply 12 face and eight curve requests for
CurvaBezier and 14 face and five curve requests for Ribbed. The new requests
were recorded without a subsequent invocation. The run preserves the
previous pilot and uses no new tolerance, scientific admission or stopping
decision. No mixed epoch is accepted.

Replay of the measured physical arc sizes finds that six of the seven
CurvaBezier intervals and five of eight Ribbed intervals still have a child
above the requested size after the bounded single split. The largest
child-to-target ratio is 3.79 and 1.63 respectively. No additional splits ran.

A separate read-only check divides the existing face residual by its median
physical edge length. Scaling the same inputs by 0.001 and 1000 changes
the measured ratios by at most 2.4e-15 in these checks. The unit plane has
exact zero indicator on the original scale. These measurements inform
the next experiment. No trigger or tolerance is adopted.

## Qualification and remaining work

Both development cases stage from the same image and original source path.
A forged tree binding on Ribbed is rejected before entering the native
feedback calculation, with no published successor and identical predecessor
witnesses. Original and reversed source contracts pass six captures and
54 negative controls. The validation adapter could not plan the iteration
because the local baseline receipt was absent. The bounded native gates
use the established local MSVC profile directly. The legacy grouping and rejection suite, the
portable two-model native suite, and 30 reporting and recovery tests pass. Test commands, hashes,
outcomes, source bindings and paired metrics are in the receipt.
The exact hosted head has 1 successful, 3 pending and 0 other jobs
in [run 45583661335](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45583661335). Independent review is pending.

The portability gate is measured for the two development cases. Align a
geometry-driven size trigger, no-action behavior, regional quality and
growth before applying a rule on reserved Bézier geometries. Preserve the
flat zero-residual negative. Define the shared-curve provenance contract
and qualify actual two-patch synchronized refinement. For a subsequent
adaptive generation, retain and reenter from the previous mixed candidate's
native curve and tree after approved admission. The current path recreates
its first mixed input from a TRI step. Global mixed curvature and the
two-accepted-epoch milestone remain open.
