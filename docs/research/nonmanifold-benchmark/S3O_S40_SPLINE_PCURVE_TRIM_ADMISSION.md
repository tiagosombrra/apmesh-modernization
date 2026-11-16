# S3.O — Original S40 `ADVANCED_FACE #1519`: B-spline PCURVE-native partial Bézier admission

**Date:** 2026-11-16. **Research classification:** isolated geometric proposal in `research/benchmark-corpus-reverse-patches`, draft PR #225. This is not a production refactor, a complete source CAD conversion, or an APMesh TRI/QUAD meshing result.

## Pinned external source and source-native mapping

- Original upstream repository: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
- Original STEP: `original/i25o_s40.step`. Its byte-level SHA-256 was checked before import: `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Native Open CASCADE: 43 source/native faces; uniquely certified target native `TopoDS_Face` index 12, cylindrical radius **16 mm**, original `CYLINDRICAL_SURFACE #137`, one outer wire, no hole, eight original source edges and eight distinct native boundary edges.
- The eight frozen original `EDGE_CURVE` identities in loop order: `#1523` (circle), `#1548` (line), `#85` (3D B-spline), `#1570` (line), `#1593` (circle), `#1616` (line), `#1644` (3D B-spline), `#1753` (line).
- Original `#85` and `#1644` each use a monotone 47-control, degree-3 cylinder `PCURVE`, at constant axial parameter. The short circular edges `#1523` and `#1593` are represented by degree-1 B-spline `PCURVE` lines in original STEP; the four generators have `LINE` PCURVEs.
- The original source 3D B-spline is not asserted to coincide *exactly* with the analytic cylinder: the separately sampled radial deviation of a native boundary curve from its support can reach about **8.6e-6 mm**. The native boundary curves are therefore audited separately from the radial-support error.

## Geometric insight and conservative partition

Despite the source 3D B-spline complexity, the original cylinder `PCURVE` geometry describes a single orthogonal, stepped UV domain:

- Original angular U breakpoints (rad): `[3.141592653568, 3.459416357509, 5.965361603261, 6.28318530718]`.
- Original axial V breakpoints (mm): `[-16.49999999996, -10.49999999998, 16.500000000031]`.
- One upper band across U, plus one lower central tab; no inner loop is inserted or ignored.
- Verified source polygon parametric area: approximately **99.85867312202046 rad·mm**, equal to the sum of disjoint source-anchored rectangles within `1e-8`.

The original S3.N 43-patch BP is reverified by SHA and recomputed from its frozen canonical registry before extension. The selected **seven central angular sectors** produce **16 source-anchored cubic Bézier patches** (nine upper, seven lower), with **21 new internal indexed seams**. Four original generator edges use their original `VERTEX_POINT` and `EDGE_CURVE`-based canonical control identities. The eight previously assigned integer control indices on original generator edges `#1548` and `#1570` are **reused exactly**, without coordinate welding. All newly generated internal seams also share integer indices on both sides.

### Admitted pilot configuration and numeric evidence

| Gate | Direct original native result |
| --- | ---: |
| Previous S40 BP | 43 patches, 511 controls |
| S3.O addition | **16 patches** on `#1519` |
| Combined indexed partial BP | **59 patches, 681 distinct controls** |
| Represented original STEP faces | **15 of 43**; 28 still excluded |
| Exact indexed internal seams added | **21** |
| Reused original planar shared generator edges | `#1548`, `#1570` |
| Unique source/native boundary identities | **8 of 8** |
| Sampled original native boundary points | **198**, including both original 3D B-splines |
| Original native B-spline `#85` sampled boundary points | 63 |
| Original native B-spline `#1644` sampled boundary points | 81 |
| Native UV samples on S3.O patches | **1,296 interior IN; 704 boundary IN/ON** |
| Maximum sampled original native boundary deviation | **0.0006828948238988339 mm** |
| Maximum sampled native cylinder projection deviation | **0.0006828967915523848 mm** |
| Guarded numeric Bernstein radial-support upper | **0.0006828979518292894 mm** |
| Predeclared *experimental* geometric budget | **0.001 mm** |
| Six central sectors | **REJECTED** by radial enclosure |
| Seven central sectors | **PASS** within bounded gates |

The source 3D B-spline edges are evaluated through their **actual** Open CASCADE `BRepAdaptor_Curve` objects and their independently recovered `BRepAdaptor_Curve2d` parameterization, rather than replacing them with ideal circular edges. Monotone PCURVE parameters are inverted numerically per sample. Every original boundary entity has the correct number of indexed subsegments; absent, duplicate, ambiguous, altered, or unsupported edge identities fail closed.

## Scientific limitations

- Bernstein convex-hull subdivision is evaluated in floating point with a fixed heuristic guard; it is not directed-rounding interval certification.
- UV membership, 3D B-spline edge distances and cylinder projection are sampled, not global continuous Hausdorff equivalence results.
- The original **43-face S40 source shell remains incomplete**: 15 original source faces currently have research BP representations, while 28 remain excluded, notably complex face `#2457` and the hole-bearing `#218`.
- No genuine external 3+-incident original non-manifold positive has been established; S40 is still a manifold control.
- No accepted APMesh TRI/QUAD result or production C++ regression is claimed. No merge to `main` is authorized from this bounded scientific evidence.
- The original third-party STEP file, private BP controls and derived CAD tessellation/GLB are **not committed publicly**, pending redistribution-rights review. The user-visible research ZIP is private and excludes the original STEP bytes.

## Independent directed validation and reproducibility

The S3.O unit tests include original source SHA, original source/native interface IDs, source spline degrees and monotonicity, source polygon/rectangle area, inherited global control identity, new internal seams, original 3D boundary distances, native UV membership, fixed numeric budget, and adversarial modified-source/manifest/BP/ambiguous-edge controls.

- **S3.O only:** 17/17 directed tests PASS.
- **S3.M + S3.N + S3.O:** 45/45 directed tests PASS, with byte-frozen original S40 available. The entire older research suite was not rerun for this delivery; do not claim an expanded all-suite result.

Run from `code/`, after supplying the original STEP from an authorized local source and the *private* S3.N baseline BP/manifest:

```bash
export APMESH_ORIGINAL_CAD_DIR=/path/to/originals
export APMESH_MAMBO_SOURCE_DIR=/path/to/originals
python -m unittest -q test_s3m_s40_complex_trim_inventory test_s3n_s40_orthogonal_trim test_s3o_s40_spline_trim
python s3o_s40_spline_trim.py \
  --source-step /path/to/originals/i25o_s40.step \
  --baseline-bp /private/s3n/private_bp/s40_step1986.partial.bp \
  --baseline-manifest /private/s3n/private_bp/s40_step1986_manifest.json \
  --middle-sectors 7 --budget-mm 0.001 \
  --output-dir /private/s3o-output
```

**Next bounded step S3.P:** audit `#2457` source spline PCURVEs and original/native BRep trim graph; only then attempt a compatible partial BP extension. Treat `#218`'s true inner loop as a distinct hole-preserving task, not a trivial rectangle fill. Continue independent, explicit production/QUAD/non-manifold positive gates.
