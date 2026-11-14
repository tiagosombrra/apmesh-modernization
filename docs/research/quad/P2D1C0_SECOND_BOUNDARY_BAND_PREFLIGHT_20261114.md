# P2d-1c0 — second native-boundary candidate: independent dyadic preflight

Date: 2026-11-14. Parent: integrated [PR #231](https://github.com/tiagosombrra/apmesh-modernization/pull/231), exact original source candidate `1efb13b6a6fb46fca77deba81aa405db5bff90d5`, research merge `4b7f485a0df2c5108dbd822f337d2e38bba2947a`.
Scientific requirement: [R3/M7 issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Grounded input and narrow falsifiable question

The first physical controlled patch is **69 nodes / 42 QUAD / 36 original AFT TRI**. The first connected real native Quadtree/AFT candidate is **93 nodes / 62 QUAD / 44 AFT TRI**, source-specific experimental fixed16 policy, only **staged and unaccepted**. The independent PR #231 64×64 same-site original Bernstein source oracle reports reduction in max error `0.06564122093160714 -> 0.05160741345747398`, RMS UV `0.017295203854736017 -> 0.012518000838243337` and source Jacobian-weighted RMS `0.015981265663966727 -> 0.011810324643012932`. All are finite-grid diagnostics; **no accepted adaptive epoch** exists.

The **new maximum AFT-TRI residual of that staged physical candidate** is triangle face #103 near UV **(0.8,0.1)**. In its *level-2 source cell* coordinates, this is **(3,0)** — a different physical-error target from the first-boundary band (original source cell #6 near UV (0.2,0.1)). We must not blindly repeat the previous three-cell pattern or claim a new iteration from a fresh original template.

A research-only independent 8×8 dyadic surrogate enumerates adding the *actual UV grid cell coordinates* to the previously qualified source set `{(1,1),(0,0),(1,0),(0,1)}`. No speculative native `QuadtreeCell::getId` identities are assigned to these grid coordinates. All results are topology **preflight**, not actual source C++ Quadtree/AFT tests.

## Independent bounded predictions

| Additional level-2 source cells beyond P2d-1b1 | 8×8 eligible QUAD tiles | Predicted leaves | Source QUAD UV area | Four-neighbor/vertex UV disk |
| --- | ---: | ---: | ---: | --- |
| None (physical band already staged, not accepted) | 21/64 | 28 | 32.8125% | YES |
| (3,0) only — selected new source error | 22/64 | 31 | 34.375% | **NO: disconnected and diagonal vertex touch** |
| (3,0) plus west (2,0) | 24/64 | 34 | 37.5% | YES, **surrogate only** |
| (3,0) plus north (3,1) | 24/64 | 34 | 37.5% | YES, **surrogate only** |
| (3,0), west (2,0), north (3,1) | 26/64 | 37 | 40.625% | YES, **surrogate only** |

The area predictions count *eligible* dyadic grid tiles, not actual native emitted QUAD count or accepted physical faceted area. The surrogate performs three independent necessary UV disk checks: edge/four-neighbor connectedness, no enclosed complement holes and rejection of diagonal-only two-cell vertex links. Actual native balancing may introduce extra changes; neither source cell IDs, AFT front closure nor mapped four-corner physical Jacobians are implied.

**Decision insight:** two distinct two-cell choices have the same predicted area and smaller leaf count than the three-cell option. Therefore an algorithm that always selects three leaves is not demonstrably complexity-efficient. The two- vs three-cell options require real native C++ Quadtree/AFT physical construction and independent same-site error/quality comparison before selecting an acceptance strategy. Record failed variants and leave any previous owner intact.

## Execution / test limits

- Source-only Python: `research/quad/p2d_next_band_dyadic.py`.
- Six isolated positive/negative tests: `python tests/quad/test_p2d_next_band_dyadic.py -v`; locally executed **6/6 PASS** in an independent Python environment. Exact-feature GitHub CI and production/native C++ tests were **not executed** for this source commit at this checkpoint.
- Test controls reject original-only island, diagonal nonmanifold vertex touch, duplicate/already-refined/out-of-range cells and nonfinite/noninterior UV sites.
- Next bounded native milestone **P2d-1c1**: use the **real staged physical candidate #229/#231's current second worst-AFT residual** as the selection input, carry forward the **previously refined native tree** rather than rebuilding the initial P1 tree, evaluate west, north, and both native neighbors. Run actual `refineAccordingToNeighbors`, `CaptureLeafPolygons`, `EmitLeafQuads`, original native AFT and independent Bernstein physical OBJ/source/quality controls per candidate. Reject malformed physical fronts and preserve original owner/outputs. Do not count a proposal or staged OBJ as a second accepted epoch.
- **R3/M7 remains OPEN:** scientifically defined error/quality/complexity policy, fully owned `MixedEpoch` candidate transaction, prior-accepted-mesh-driven history and at least two accepted distinct adapted epochs remain missing. Initial fixed16 sampling is not production `Adapter::AdaptCurve` or historical 1993 method; no global Eistute/Book nonmanifold sheet/weld approval, all-QUAD or anisotropy.
