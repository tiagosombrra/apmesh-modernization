# S40 — Original-source pending 21-face acceptance register (post S3.Y)

**Date:** 18 November 2026. **Reference:** original industrial S40 STEP, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`; S3.Y selected BP SHA-256 `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`. Research branch only; PR #225 remains draft.

## Snapshot, not a completed industrial atlas

Selected S3.Y has **156 indexed bicubic Bézier patches**, **1,665 declared controls**, **264 two-sided indexed seams**, **96 open sides**, **22/43 original STEP faces**. Only face **#3044** was newly admitted in S3.Y after native trim/geometry checks. Thus **21 of the 43 original source faces remain unrepresented**. No TRI/QUAD APMesh mesh, full original CAD completion, production C++ regression or genuine original non-manifold positive is established.

This register is reconstructed from the SHA-pinned **S3.X original-source census (22 pending before S3.Y)**, explicitly removing the admitted S3.Y face **#3044**. The **source support and source boundary counts remain valid**. Historical adjacency counts (S3.X) are labeled stale after #3044; they MUST NOT be used as refreshed S3.Y source-native connectivity without reimporting original STEP and recomputing incidence.

| Type of still-unrepresented source support | Faces |
| --- | ---: |
| PLANE | **12** |
| CYLINDRICAL_SURFACE | **6** |
| Non-rational B_SPLINE_SURFACE_WITH_KNOTS | **2** |
| COMPLEX_RATIONAL_B_SPLINE_SURFACE | **1** |
| **Total** | **21** |

## Ordered scientific gates (not guaranteed acceptance)

| Priority | Original STEP `ADVANCED_FACE` | Known native-source obstacle | Required gate |
| --- | --- | --- | --- |
| **P0 — retry current block** | **#1827**, **#1907** | Six source boundary edges each; four circular edges and two straight edges; each had 18 strict native `OUT` boundary samples in the rejected joint S3.Y candidate | Run source-canonical shared-control S3.Z trials, audit BOTH incident faces and all old affected cylinder patches; never accept based on synthetic unit tests |
| **P1 — next independent region** | **#859** | Four planar source edges; two incident source edges were already represented in the pre-S3.Y S3.X census | Recompute current edge ownership and indexed BP-side mapping; check convexity/trim and admit only with exact shared integer controls |
| **P1 — circular planar regions** | **#1279**, **#1386** | Six source edges each, two circle edges; three historical directly incident represented source edges each | Preserve original circular curves; quadrangulate all existing subdivisions without hanging boundary nodes |
| **P2 — dependency resolution** | **#2469**, **#3134** | Four planar edges, zero direct neighbors in old S3.X census | Recompute post-S3.Y adjacency; consider only after qualifying bordering regions |
| **P2 — odd parity** | **#3269**, **#3485** | Five source boundary edges each | Need source-compliant boundary split or Steiner strategy; no five-side boundary admits a pure conforming all-quad disk without a boundary subdivision |
| **P3 — complex planar** | **#3535**, **#2243**, **#2545** | 13-edge source wire (#3535) or original inner wires/holes (#2243, #2545) | Preserve original holes and non-intersecting inner wires; verify native trim inclusion and avoid filled holes |
| **P3 — curved support** | **#3402**, **#3710**, **#3183**, **#3237**, **#3319**, **#3683** | Original cylindrical supports, some two source-edge hops away from the prior atlas | Native parametric trim constraints, original curve budget and interval-aware radial support verification |
| **P4 — higher-order supports** | **#807**, **#1493**, **#556** | Two B-spline supports and one rational B-spline support | Surface degree/knots/weights audit, controlled approximation, source-edge identity and two-sided native trim checks |

## S3.Z.4 runnable gate

The S3.Z.4 package from this checkpoint adds `s3zd_original_s40_runner.py`, which explicitly retrieves the byte-pinned original STEP when requested (outside Git), checks private S3.W BP and manifest, checks the S3.Y source-backed builder, and calls the eight fixed-budget trial candidates. Native-trial output is blocked without the exact inputs and never auto-admits faces. The local hermetic unit suite was **102/102 PASS, no failures**, including **19 new executor tests**.

The actual S40 native trial remains **NOT RUN** in this runtime: authorized original STEP and private S3.W BP/manifest were missing, and raw GitHub retrieval from the isolated container failed. The source-only code and the Python test evidence do not replace the original CAD.

The code package is delivered to the researcher privately in the conversation; **this specific GitHub commit records the register and S3.Z.4 orchestration only**. Until script contents are committed, use the package's verified local Python files, not a hypothetical remote code path.

## Next verifiable actions

1. Supply the exact authorized original STEP and original S3.W BP/manifest to a configured private research workspace (or run the opt-in pinned download where external internet is enabled).
2. Re-run the S3.Z.4 native trial and independently audit all its candidate control changes. **Keep the previous 156-patch S3.Y child unchanged** until an independent selected-patch receipt passes.
3. Progress to the independent planar `#859`, `#1279`, `#1386` if S3.Z remains blocked; never conflate priority ranking with geometric admission.
4. After future complete **43/43** source-face representation, require watertight indexed seams, original hole preservation, full source-native BRep coverage, scientific approximation tolerances and accepted APMesh TRI/QUAD run before claiming a complete research model.

**Scientific disposition:** The measured industrial S40 is **PARTIAL (22/43)**; S3.Z.4 is a tested execution gate, not a new geometric admission.
