# S3.L — Original S40 second-ring planar/cylinder indexed BP gate

**Date:** 2026-11-16. **Classification:** isolated scientific research on native original CAD, not production modernization, a whole-model surface atlas, or TRI/QUAD meshing.

## Source and fixed acceptance scope

- **Pinned STEP**: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, original file `original/i25o_s40.step`, raw SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. An actual byte-identical source was imported through CadQuery/Open CASCADE; original STEP bytes are not committed or redistributed.
- **Predeclared experimental geometry budget**: `0.001 mm`. This is not a final advisor-approved model-quality tolerance.
- **New source consistency check**: maximum `1e-8 rad` between the directed 3D original circular-edge sweep and the oriented generator-PCURVE endpoint span. This is **not** a widening of the geometric approximation budget. Its purpose is to detect inconsistent 3D/2D trimming parameters while using the actual source PCURVE endpoints to construct the domain. If this gate fails, the face is excluded.
- Only four original S40 cylindrical faces are eligible under the bounded **one four-edge wire / exactly two straight axial generators / two original circle arcs** policy: `ADVANCED_FACE #2882`, `#2936`, `#2990`, `#3127`, with native face indices 26, 27, 28, 31 respectively. Their 3D radius is 9 mm and axial extent is 10 mm. All four have one original planar-candidate generator anchor; the other original generator is shared with another admitted cylindrical face.
- Original **first-ring complex cylinders** `#218`, `#1519`, `#1986`, and `#2457` remain explicitly excluded. Their trims include multiple wires, 8/9-edge loops, curve splits and B-spline edges. **No arbitrary UV-rectangle fill or geometric proximity welding is used to bypass these restrictions.**

## Why a new S3.L algorithm is necessary

The S3.I original joint constructor required **two planar-anchored generators for every cylindrical face**, which applies to the original M5 pilot but rejects these S40 second-ring faces. S3.L generalizes the canonical control-index registry to one-planar-anchor cylinders, while demanding native original edge identity for all represented inter-face seams. It does not change S3.I, production C++ code, or Stage 3/QUAD.

The first strict S3.J check on `#3127` exposed a floating source-parameter disagreement: the 3D `CIRCLE` sweep and generator-PCURVE span differ by `6.56590337655e-10 rad`. The unaligned last angular control exceeded the strict wedge inequality by approximately `5.91e-9 mm`. Rather than simply increasing the geometric budget or suppressing the test, S3.L computes the source 2D endpoint span and **independently checks** its winding/closure against the 3D STEP circle. The largest observed original 3D/2D closure discrepancy is `6.56590337655e-10 rad`, below the explicit separate `1e-8 rad` source-consistency gate. The canonical original 3D generator endpoint controls remain unchanged. A deliberately forged source discrepancy of `1e-5 rad` is rejected.

## Original native S40 measured result

| Measure | Observed |
|---|---:|
| Original source faces | 43 |
| Exact planar source quad faces | 9 |
| Bounded admitted cylindrical source faces | 4 |
| Other original source faces unrepresented | 30 |
| Cubic Bézier patches (9 planar + 4 × 4 cylindrical) | **25** |
| Unique indexed global control points | **320** |
| Two-sided original source `EDGE_CURVE` seams retained | **8** |
| Shared global original feature control IDs | **32** |
| Author-derived angular seams internal to cylinder faces | 12 |
| Sampled original native cylinder UV interior points | **1,296** |
| Sampled original native cylinder UV boundary points | **704** |
| Maximum sampled native cylinder projection distance | **0.0005559481871054107 mm** |
| Maximum guarded float Bernstein radial support bound | **0.0005559491871095784 mm** |
| Maximum sampled native planar face distance | **5.028317966014237e-10 mm** |
| Fixed experimental distance budget | **0.001 mm** |
| Independently rechecked source-native topology and UV sample result | **PASS within declared scope** |

Global original source-edge seam identities are preserved at edges `#1161`, `#1210` (planar–planar); `#2810`, `#2861`, `#3022`, `#3104` (planar–cylinder); and **`#2916` between source cylindrical faces `#2882/#3127` and `#2970` between `#2936/#2990`**. Every such pair uses exactly the same four canonical global BP control IDs, and the same native `TopoDS_Edge` identity was verified via original endpoint coordinates plus native `IsSame` matching. Numeric coordinate matching is used only to identify a **unique** source edge on each native face, not to join distinct edges by proximity.

The four cylindrical faces have a 90° nominal angular range. Two-sector and three-sector controls do **not** meet the 0.001-mm pilot budget; four-sector controls do. The actual BP was assembled with four angular patches per cylinder and checked against native trimmed UV classification, an independent geometric point oracle and the Bernstein radial-polynomial enclosure. Recomputed BP/manifest identity is enforced. Adversarial tests reject changed source hash, altered BP even with a recomputed digest, altered source seam IDs, post-hoc enlarged budgets, incorrect 3D/2D winding and insufficient subdivision. The full research Python test suite is separate from production CTest.

## Reproduce without including upstream STEP bytes in Git

From the repository root with CadQuery 2.8.0, OCP 7.9.3.1 and NumPy available, place the byte-verified STEP outside the repository:

```sh
export APMESH_MAMBO_SOURCE_DIR=/external/mambo/sources
python docs/research/nonmanifold-benchmark/probes/s3l_s40_partial_cylinder_atlas.py \
  --source-step "$APMESH_MAMBO_SOURCE_DIR/i25o_s40.step" \
  --sectors 4 --budget-mm 0.001 --output build/research-s3l/s40-private
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes \
  -p 'test_s3l_*.py' -v
```

Outputs are `s40_second_ring.partial.bp`, `s40_second_ring_manifest.json`, and `s40_second_ring_native_audit.json`. These source-derived BP/manifest files belong in **private** scientific evidence until redistribution rights are reviewed; commit only summarized non-geometric receipts, scripts, tests and documentation.

## Unclosed gates and S3.M priorities

- Four complex-trim S40 source-adjacent cylindrical faces `#218/#1519/#1986/#2457` must be partitioned by **original source PCURVE and curve topology** first, with controlled B-spline edge decomposition, split-edge identity and trim-hole treatment. No generalized four-sided native BP claim is made for them.
- The four newly admitted cylinders are not a complete contiguous model shell: source S40 retains **30 unrepresented faces**. All missing boundary interfaces must be explicitly represented before any accepted full-model APMesh mesh.
- Even on admitted cylinders, native trim membership and distance are **sampled**; Bernstein radial enclosure uses floating-point arithmetic with a heuristic numerical guard, **not directed-rounding formal interval proof** or a continuous trimmed Hausdorff certificate.
- Genuine original 3+-incident external non-manifold model, independent geometry quality/anisotropy comparisons, TRI/QUAD APMesh generator runs, complete production C++/CTest scientific regression, advisor acceptance criteria and PR merge remain OPEN.
- Research PR #225 remains draft and is not merged to `main`.
