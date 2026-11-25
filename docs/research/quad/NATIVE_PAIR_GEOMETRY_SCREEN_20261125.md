# Native geometry screen for supplemental QUAD pairs

2026-11-25 Fortaleza. [Draft PR 276](https://github.com/tiagosombrra/apmesh-modernization/pull/276)
head `6b4d5b6d3371ce945b82393f7311d4be44ea9499`.
[Machine-readable receipt](evidence/NATIVE_PAIR_GEOMETRY_SCREEN_20261125.json).

## Implementation

The approved `0.045` development ceiling is explicit in the optional
single-patch plan. The screen evaluates the five existing bilinear
surface-deviation samples for each shape-eligible extra pair and uses the
physical length of its active edge as the denominator. It bypasses an
extra pair when the edge length is unavailable or the relative deviation
exceeds the ceiling. Lowest S with the existing tie order selects among
surviving pairs. Other choices follow the existing front rule. The trial
uses CurvaBezier Step 3 with the established selective requests and
Ribbed Bracket patch 12 Step 2 with its established both-seed requests.

The initial native attempts returned staged rejections. The existing
whole-mesh surface measure requires both TRI and QUAD populations. The
implementation now shares the interpolation and five-site stencil with a
single-QUAD entry, keeping the whole-mesh population contract. The native
residual tests compare both entries on a curved witness and test zero
deviation on a plane. The initial compilation request also named the
standalone residual fixture in the root build. The fixture runs from its
own CMake project. The first boundary-contract invocation omitted its
existing config argument. The corrected invocation passes the originals.

The screen trace records the limit, ordered prospective polygons, S and
relative deviation. The independent checks recompute candidate geometry
from the analytic patch, verify eligible pair coverage and confirm the
winner or original TRI fallback. Negative, duplicate and unbound limits
are rejected at native plan parsing before proposal publication.

## Native result and limits

Both development meshes stage with the approved ceiling. Original TRI,
mixed predecessor, source binding, requests, realized leaves, native curve
records and final contours reproduce. CurvaBezier keeps its operation 13
replacement and reproduces the previous additional-pair OBJ byte for byte.
Ribbed retains TRI at operations 1 and 3 and first changes operation 61.
There are ten distinct ineligible QUADs across those two early operations,
recorded as twenty ordered apex/companion measurements. One replacement
passes in each model. The independent replay rejects a forged omission.

| Case and final metric | Original | Unfiltered pairs | Filtered pairs |
| --- | ---: | ---: | ---: |
| CurvaBezier interior TRI minimum angle, degrees | 8.04 | 14.36 | 14.36 |
| CurvaBezier interior QUAD minimum angle, degrees | 50.86 | 44.57 | 44.57 |
| CurvaBezier sampled geometric RMS | 0.009073249 | 0.009079035 | 0.009079035 |
| CurvaBezier faces | 780 | 779 | 779 |
| Ribbed transition TRI minimum angle at birth, degrees | 6.33 | 0.29 | 6.33 |
| Ribbed final interior TRI minimum angle, degrees | 18.37 | 10.90 | 18.37 |
| Ribbed sampled geometric RMS | 0.017368839 | 0.023533214 | 0.017364849 |
| Ribbed faces | 648 | 650 | 648 |

The RMS compares 2,304 identical UV sites with the analytic surface and
weights by analytic area. Both cases retain the original sampled maximum
deviation and largest adjacent physical size ratio. Ribbed's final regional
angle and shape minima reproduce the original control. CurvaBezier still
has a 2.27 degree TRI that touches the contour only at a vertex. Its
interior QUAD angle tradeoff also remains. The previous unadopted
predecessor-derived control still blocks both candidates. The test therefore
removes the transfer regression in these cases while leaving the mixed
admission rule and accepted adaptive ancestry open.

## Validation and next work

The final PR revision changes only the verifier after the initial feature
commit. The initial hosted Linux run stopped because its Python test
compared request tuples in memory with arrays read from JSON. The corrected
test compares both live ordered request records in memory. The receipt
preserves the first run and the current hosted check snapshot. Locally,
the corrected verifier checks the retained exact-image native files
without rerunning their generation. The native ordinary regression, the
boundary source captures and 54 negative controls, the standalone
residual contract and 39 focused Python tests pass.

The next functional gate is independent review of the scoped source
change, followed by aligning a mixed candidate admission rule before
using held-out geometries or claiming accepted adaptive reentry. The
0.045 threshold is a development option. Zero accepted mixed epochs,
shared curve qualification and global mixed curvature remain open.
