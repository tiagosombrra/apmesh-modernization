# S3.M — Native source-trim inventory and real CAD visualization

**Date:** 2026-11-16. **Scope:** independent, research-only S40 original geometry. This is neither a C++ production change nor an APMesh TRI/QUAD generation result.

## Provenance and admission

Original STEP: `cgg-bern/hex-me-if-you-can`, immutable revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, original raw SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.

The original source bytes were reconstructed locally after an externally transferred text envelope was normalized; the SHA-256 was verified before using CadQuery/Open CASCADE. No upstream STEP bytes, derivative meshes, or derived BP control coordinates are committed to the public repository. The private interactive HTML and GLB visualizers are **tessellations of the original CAD**, for human inspection only, not meshes generated or accepted by APMesh.

S3.L already admitted 9 exact planar source faces and four simple cylindrical source faces (`#2882`, `#2936`, `#2990`, `#3127`) as a **25-patch partial** Bézier atlas, not a closed original shell. S3.M analyzes the remaining four *direct first-ring complex* cylinders without promoting them into BP patches.

## Recomputed original STEP ↔ native BRep trimming

Original source identities were checked with the existing independently verifiable S3.E/S3.F correspondence gates, not inferred solely from face-index order. Each native face was confirmed cylindrical. Original wire-edge count and native wire-edge count are equal per face. The native `BRepTools.OuterWire` was used to distinguish outer and inner loops when present.

| Original `ADVANCED_FACE` | Native face index | Source wires | Original edge types | Native trim result | Decision |
|---|---:|---:|---|---|---|
| `#218` | 1 | 8 + 4 | 5 lines, 5 circles, 2 B-splines | 1 outer loop, **1 inner loop** | Blocked: hole + spline boundaries |
| `#1519` | 12 | 8 | 4 lines, 2 circles, 2 B-splines | Single subdivided outer loop | Blocked: spline boundaries |
| `#1986` | 17 | 8 | **4 lines, 4 circles** | Single subdivided outer loop | **Next controlled split-edge candidate**; not yet admitted |
| `#2457` | 22 | 9 | 4 lines, 2 circles, 3 B-splines | Single subdivided outer loop | Blocked: spline boundaries |

All cylinder-side original PCURVE records for `#1986` are `LINE`; the other three include B-spline PCURVEs. This is why **`#1986` should be decomposed first**, preserving original `EDGE_CURVE` identities for split boundaries. Do not treat it as a four-edge rectangle or silently sew separate source features by coordinate proximity.

The full first-party machine-readable inventory is kept privately with the visualizer package. A **nongeometric** summary accompanies the repository work. No new patches or TRI/QUAD meshes were generated in S3.M.

## Test evidence

Nine new directed tests passed locally against the original byte-pinned S40: hash checks, correct native face census, 1 confirmed inner loop on `#218`, explicit spline rejection, exact analytic boundaries on `#1986`, negative forged-source and mismatched BRep controls. The previous S3.L full research suite had 179 passing tests; the attempt to rerun the entire enlarged suite exceeded the execution limit at an expensive existing S3.L test. **Do not record 188/188 as passing on this evidence.** No C++ production regression was run.

## Visual model outputs

Private, offline interactive Plotly viewers present the complete original M5 and S40 STEP tessellations, the admitted M5/S40 BP partial reconstructions, and on S40 a distinct red overlay for complex faces `#218`, `#1519`, `#1986` and `#2457`. GLB viewer meshes and a side-by-side PNG were also produced. Use the HTML's button group to switch views. All original native shape semantics remain in the source STEP, not in GLB.

## S3.N proposed gate

1. On original S40 `ADVANCED_FACE #1986`, reconstruct oriented original source `PCURVE` polygon with all 8 LINE segments, including the four split source circles in 3D. Obtain an unambiguous no-hole rectangular partition from original UV edge intersections, and explicitly attribute each generated internal seam separately from original `EDGE_CURVE` identities.
2. Require unique original↔native boundary matches and exact shared global Bézier control indices with neighboring previously admitted patches, then independently audit native trimmed-face membership and predeclared geometric distances. No artificial rectangle fill or post hoc tolerance relaxation.
3. Only then investigate spline trim loops of `#1519/#2457` and the confirmed inner loop of `#218`. Never remove or ignore the hole.
4. Keep full-model acceptance, genuine original 3+-sheet non-manifold evidence, APMesh TRI/QUAD execution, advisor criteria and protected main merges separate, unresolved gates.

**PR #225 remains draft; no changes to `main`.**