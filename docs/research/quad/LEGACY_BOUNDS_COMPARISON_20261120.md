# Legacy factor bounds on the mixed article-front case

20 November 2026, Fortaleza. One configuration-only comparison requested after the [boundary generation audit](BOUNDARY_GENERATION_AUDIT_20261120.md). The comparison keeps the original adaptive source workflow and the article-front reconstruction. It examines how growth on the curved side and straight sides relates to the transition and interior. The user approves neighboring influence in both directions as a design objective, with different refinement levels where appropriate. This run varies shared bounds and cannot isolate either direction.

The same qualified MSVC Debug application image serves both profiles. The fixed `1.5` archive came from PR240 source `51d51f6423abd0208b250f0bbb0291364852cab1`. Executable and build-cache hashes match the original receipt. The candidate config removes `PATCH_FACTOR_MIN=1.5` and `PATCH_FACTOR_MAX=1.5`, so the parser uses `0.80–1.12`. Only the output location and that bound pair differ. The run exits zero in 81.18 seconds under the existing 180-second limit and publishes a complete archive. Application success and TRI source acceptance are recorded separately.

| Step | Mixed nodes, fixed → legacy | Contour segments, fixed → legacy | Source TRI curvature error, fixed → legacy | Legacy TRI outcome |
| --- | ---: | ---: | ---: | --- |
| 0 | 5 → 5 | 4 → 4 | 0.314848 → 0.314848 | Initial |
| 1 | 33 → 165 | 8 → 20 | 0.139436 → 0.125829 | Accepted |
| 2 | 281 → 953 | 10 → 112 | 0.0538754 → 0.382516 | Rejected, global error increased |
| 3 | 689 → 953 | 14 → 112 | 0.0303172 → 0.382516 | Rejected, global error increased |

The legacy candidate publishes the Step 1 mixed mesh with 138 QUAD and 32 TRI, bound to the last accepted TRI source attempt. It retains both rejected reconstructions, each with 858 QUAD and 76 TRI. Steps 2 and 3 have identical parsed XYZ, UV and connectivity. The source error increases from the last accepted `0.125829` to `0.382516` on each rejected candidate. These are the original TRI curvature-error values. The mixed global curvature error remains unavailable and mixed accepted adaptive epochs remain zero.

## Growth and quality of the transition

At legacy Step 1, the curved side gains eight segments and each straight side has four. At Step 2, the curved side reaches 64 segments and each straight side reaches 16. The Step 2 curve-only pass has 17 points on the curved side and five on each straight side. The surface-informed pass produces 65 and 17 points, respectively, and the final-budget observation preserves those lists. Therefore the largest point-count jump occurs in the surface-informed pass in this run. The original curve factors are `0.80` then `0.84`, and the domain factors are `0.80` then `0.88`. Native tree leaves grow from 46 to 256. This preserves differential refinement across sides while increasing the total growth sharply.

| Mixed quality measure | Step 1 fixed → legacy, both accepted source | Step 2 fixed → legacy, legacy source rejected |
| --- | ---: | ---: |
| Worst physical angle on a face using a contour edge | 31.55° → 23.67° | 15.64° → 13.66° |
| Worst physical angle on a face touching contour by vertices only | 37.62° → 22.92° | 9.59° → 38.34° |
| Worst physical edge ratio on faces touching contour by vertices only | 1.62 → 2.54 | 5.71 → 1.61 |
| Median size ratio between a vertex-only face and its interior neighbor | 1.59 → 1.80 | 2.64 → 1.47 |

The last line uses adjacent faces sharing one edge. Each face size is its median physical edge length. Ratios are descriptive and are compared over 8 and 26 pairs in Step 1, and 39 and 42 pairs in Step 2 for fixed and legacy profiles, respectively. The legacy Step 2 shows more gradual sizes at that interface. Its worst contour-edge angle still worsens. The released Step 1 has worse minima in both contour groups than the fixed profile. Greater density alone yields neither a consistent quality gain nor a usable accepted history here.

## Existing neighbor influence and next action

The source already uses two distinct connections. `AdaptCurveBySurface` consults analytical surface curvature and stored discrete curvature of the endpoint nodes before subdividing the curve, then `BinTree::Restrict` regulates the curve partition. `AdaptDomain` seeds its front with that partition, calculates target sizes from the preceding TRI faces and uses `SmoothDomainTargetSizes` to spread size influence across neighboring faces. The mixed mode uses the selected contour and native tree. These mechanisms show how information can travel from the surface to the curve and from the curve to the subsequent domain. They do not establish that the distribution on every mixed-front interface is well graded.

Close the shared bound comparison and keep fixed `1.5` as the retained reference for this model. Move the next diagnosis to the Step 1 → 2 surface-informed jump. For each source interval, trace the endpoint discrete curvature, analytical midpoint curvature, original target length, emitted subdivisions and adjacent native target size. Start from the accepted Step 1 context and bind the trace to the already measured rejected Step 2. Use that evidence to propose a local coordination change with the existing domain and curve restrictions. Preserve the graded interior and assess local growth around corners and along neighboring sides separately. Scientific alignment precedes any changed sizing, new controller or feedback law.

The [numeric receipt](evidence/LEGACY_BOUNDS_COMPARISON_20261120.json) records source/binary/configuration identities, input and output hashes, twelve contour source checks across six adapted stages, oriented pre/post smoothing connectivity and fixed contour, 96 curve-pass records and regional physical quality. The last accepted mixed output matches its archived Step 1 OBJ byte for byte. The reference inputs remain identical. The single native model run and the archive audit ran this session. No rebuild, fresh baseline CTest campaign, hosted rerun, integration or new acceptance rule is attributed to this documentation checkpoint. Existing draft PR243 remains separate.
