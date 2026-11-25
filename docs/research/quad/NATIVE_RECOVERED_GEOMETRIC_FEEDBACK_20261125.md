# Native geometric feedback from a recovered mixed mesh

Recorded 2026-11-25 Fortaleza. [Commands, traces and numeric receipt](evidence/NATIVE_RECOVERED_GEOMETRIC_FEEDBACK_20261125.json).

[Draft PR 268](https://github.com/tiagosombrra/apmesh-modernization/pull/268)
adds a bounded feedback trial to the CurvaBezier runner. It reads the recorded
mixed predecessor, recovered OBJ and fronts, recomputes the sizing requests
using the approved residual and gradation code, and verifies that the trial
reproduces their bytes before attributing either candidate to them. The 14
original contour segments are held fixed for this tree-only comparison.

Both source meshes produce the same 13 requests. With the captured depth cap
of four, eight requests are saturated. The five remaining requests identify
three unique level-three leaves. Each is split once and the existing native
balance runs. Both arms replace the same three leaf boxes with the same 12
children. The reference tree changes from 223 to 232 leaves and the recovered
tree from 217 to 226. Both detached TRI/QUAD candidates pass native geometric and typed incidence
checks. The previous OBJ and typed owner remain authoritative.

| Final result | Mixed predecessor | Its successor | Recovered mixed mesh | Its successor |
| --- | ---: | ---: | ---: | ---: |
| Nodes / faces | 689 / 732 | 689 / 732 | 683 / 725 | 683 / 725 |
| Minimum TRI angle | 1.870 deg | 1.463 deg | 1.870 deg | 1.463 deg |
| Minimum QUAD angle | 12.171 deg | 9.527 deg | 12.171 deg | 9.527 deg |
| Full-patch geometric RMS, grid 24 | 0.0095417 | 0.0100386 | 0.0094863 | 0.0099859 |
| Full-patch geometric RMS, grid 48 | 0.0097646 | 0.0102325 | 0.0097117 | 0.0101821 |

Both the sampled maximum and RMS increase on both grids. These are
geometric deviations in model units. There is no mixed curvature aggregate
or scientific acceptance decision for this pilot. Keep both negative
results and the original mesh.

## Source of the first regression

The refinement preserves every ordered seed QUAD cycle and the original
front vertices. The mixed advancing front first diverges at transaction 9
for both arms, on the same base from UV (1, 0) to (1, 0.5). The original
apex at (0.875, 0.25) is still active and passes the geometric validity
check. On the finer leaf partition the first viable search neighborhood
has 12 candidates instead of 16 and excludes that apex. The search
selects (0.875, 0.125), with a lower UV apex score (116.57 vs 126.87 degrees).
The successor of the recovered mesh already has a global minimum TRI angle
of 1.184 degrees before smoothing, from 2.272 on the recovered predecessor.
The first divergent vertex is measured separately from the globally worst
face after smoothing. The quadtree alters the spatial search even though
the contour and seed mesh are identical.

## Verification and next experiment

Exact MSVC C++17 build and runner suite pass, including the matched native
case, selection recovery, the forced rejection and the protected-size veto.
Independent checks replay the 108 and 106 front transactions and all five
smoothing passes per candidate. They reject nine forged boundary cases per
candidate. The source contracts cover 54 negatives, and 30 reporting and
recovery tests pass. The default validation adapter lacks a local baseline
receipt; the existing working MSVC profile was used directly.
Hosted validation had 0 successful, 4 pending and 0 failed jobs at checkpoint.

Seek explicit alignment for one causal replay of the spatial search. Use the
predecessor boxes for candidate lookup only when the measured seed vertices,
seed QUAD cycles and curve are identical. Keep the three native tree edits,
validity checks and triangle/QUAD scoring. Compare the transaction sequence,
the physical mesh and the same metrics. If the geometry reproduces the
predecessor, treat this as a search-only effect for this run. Qualifying a
general rule for advancing an adaptive epoch remains open.
Accepted mixed adaptive epochs: zero.
