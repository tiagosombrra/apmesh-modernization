# S40-F0 — Source-native edge frontier after S3.Y (original CAD)

**Checkpoint 2026-11-18.** Evidence tier: original industrial STEP graph **actually parsed** and independently cross-checked against S3.X; this is **not** a BP, trimmed native BRep, C++ or mesh generation checkpoint.

## Immutable input and real audit

The original upstream `cgg-bern/hex-me-if-you-can` `original/i25o_s40.step` was retrieved at revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`. Its **entire 216,438-byte content** was evaluated; the original SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b` was independently recomputed in the current checkpoint. This repository contains no copy of the original CAD bytes or private Bézier coordinates.

The previous S3.Y 156-patch child is the last **native-sampled bounded research baseline**, representing **22 of 43 original STEP faces** with 1,665 global controls. Its immutable private BP SHA-256 is `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`. **No new patches were created or admitted** here.

The parsed original STEP has **3753 entities**, **43 ADVANCED_FACE**, **117 distinct EDGE_CURVE**, and **77 VERTEX_POINT** objects. All 117 original edges have exactly **two distinct original face owners**. Consequently S40 remains a **manifold geometric benchmark**, not a true non-manifold source-positive.

The original S3.X per-face metadata was independently cross-checked: **21/21 remaining face records match** their STEP support, individual wire counts and 3D master curve histograms. The new atlas frontier excludes source face `#3044`, admitted in S3.Y.

### Remaining 21 original STEP faces

There are **12 planar**, **6 cylindrical**, **2 nonrational B-spline** and **1 rational B-spline** source faces pending. **15** share at least one original `EDGE_CURVE` with the represented atlas, and **6** are two original edge hops away.

| Original face | Original support | Original wire lengths | Shared source edges with atlas | Min edge hops |
| --- | --- | --- | ---: | ---: |
| `#556` | Rational B-spline | 8 | 1 | 1 |
| `#807` | B-spline | 4 | 1 | 1 |
| `#859` | Plane | 4 | 2 | 1 |
| `#1279` | Plane | 6 | 3 | 1 |
| `#1386` | Plane | 6 | 3 | 1 |
| `#1493` | B-spline | 4 | 1 | 1 |
| `#1827` | Plane | 6 | 6 | 1 |
| `#1907` | Plane | 6 | 6 | 1 |
| `#2243` | Plane | 2+3 | 5 | 1 |
| `#2469` | Plane | 4 | 0 | 2 |
| `#2545` | Plane | 5+6 | 6 | 1 |
| `#3134` | Plane | 4 | 0 | 2 |
| `#3183` | Cylinder | 4 | 0 | 2 |
| `#3237` | Cylinder | 4 | 0 | 2 |
| `#3269` | Plane | 5 | 1 | 1 |
| `#3319` | Cylinder | 4 | 0 | 2 |
| `#3402` | Cylinder | 4 | 1 | 1 |
| `#3485` | Plane | 5 | 1 | 1 |
| `#3535` | Plane | 13 | 1 | 1 |
| `#3683` | Cylinder | 4 | 0 | 2 |
| `#3710` | Cylinder | 4 | 1 | 1 |

## Revised source-driven implementation priorities

**Priority P1: original #1279 and #1386.** Each has **one six-edge outer wire**, with **four LINE and two CIRCLE source edges**. The three already represented source edges are all LINE, allowing canonical existing indexed straight sides to be inherited. Three other edges (two circles and one line) need source-identified canonical curved-side construction and a conforming future join. In a four-sided Bézier atlas, these are polygon-partition candidates, **not one-patch faces**. Exact segment counts cannot be assumed until the original S3.Y BP is recovered.

- **ADVANCED_FACE #1279:** `#1139` LINE (already represented #1105); `#1284` LINE (already represented #3737); `#1307` CIRCLE (pending #3710); `#1336` CIRCLE (pending #3683); `#1365` LINE (pending #3485); `#1002` LINE (already represented #912). 
- **ADVANCED_FACE #1386:** `#1259` LINE (already represented #1230); `#1080` LINE (already represented #912); `#1392` LINE (pending #3269); `#1415` CIRCLE (pending #3319); `#1444` CIRCLE (pending #3402); `#1473` LINE (already represented #3737). 

**Priority P1-repair: original #1827 and #1907.** Their six original source edges are already connected to represented faces, but the previous three-face S3.Y construction produced **18 native-trim OUT boundary samples per face**. They remain blocked until two-sided shared circular-edge correction passes strict original native plane/cylinder trim membership and both radial gates; do not accept the rejected 160-patch candidate.

**Priority P2: #3269 and #3485.** Both have one **five-LINE** source wire and one source-edge connection to the existing atlas. This odd boundary-segment parity requires a planned boundary split propagated to its neighbor or a source-canonical conforming subdivision; a naive all-quad closure with five unsplit sides is not admissible. They share new original-source edges with #1386 and #1279 respectively, so P1 improves their future atlas connectivity.

**Not an easy one-quad target: #859.** Four original source edges include **two original B_SPLINE_CURVE_WITH_KNOTS**, one CIRCLE and one LINE; only two edges currently touch the atlas. Its curve approximations and future-canonical joins need a separate plan.

**Special trim cases: #2243 and #2545.** Their original STEP face-bound wire lengths are **2+3** and **5+6**, respectively. A graph with more than one wire must preserve the original trimmed-domain topology explicitly; it cannot be flattened to a simple six-sided polygon even though #2243 has five represented source-edge neighbors and #2545 has six.

The remaining cylindrical / rational / B-spline and two-hop faces are not falsely labeled ready for a planar solver. See the linked machine-readable receipt for every original source `EDGE_CURVE`, its 3D master curve and the independently identified neighbor face. No coordinate-based welding is permitted.

## Gated next operations

1. Recover S3.W private BP/manifest and the exact S3.Y child or deterministically reconstruct its byte-locked state; do not overwrite the 156-patch accepted reference.
2. Implement #1279/#1386 source edge-to-indexed-BP mapping using the established S3.Y independent native curve matcher, preserve the four original source edges' curve types and all six edge owners, and choose a conforming quad partition with inherited controls on represented sides.
3. Audit actual original STEP BRep trim `IN/ON`, feature curve deviation within the predeclared `0.001 mm` pilot, outward Jacobians, no introduced holes/overlaps, existing S3.W repaired splines and original hole #218; reject source/native ambiguities.
4. Only after passing those gates append new source faces to the atlas, version the private BP SHA/manifest and run directed regressions. Keep production TRI/QUAD, full C++ regression, external 3+-sheet original and complete 43/43 coverage as independent unsatisfied gates.

**Validation disposition:** original STEP topology and full 21-face source-graph classification **PASS**, original-to-previous S3.X record comparison **21/21 PASS**; **no private BP available**, therefore `NATIVE_BP_CONVERSION=NOT_RUN`, `NEW_FACES_ADMITTED=0`. The 156-patch research baseline and draft PR #225 are not promoted or merged.
