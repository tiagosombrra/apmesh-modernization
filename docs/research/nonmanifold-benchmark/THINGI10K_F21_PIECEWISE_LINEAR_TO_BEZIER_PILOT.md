# S40-F21 — Original #293137 STL to four-sided bicubic candidate: exact piecewise-linear construction

**Research date:** 2026-11-23. **Branch:** `research/benchmark-corpus-reverse-patches`, PR #225 DRAFT. **Not a qualified native APMesh run, accepted CAD reconstruction, or published QUAD comparison.**

## Real source provenance and independently observed geometry

The pinned public Thingi10K mirror file is `larsbrubaker/Thingi10K-meshes-2@ab50a098405dc2dfcf882e87dab3811b5ea8ce92`, `meshes/293137.stl.zip`. The GitHub connector returned the ZIP as base64 with **Git blob SHA-1 `359c26b16664e9ba8d2415ca065a85bd27504d5f`**, size **7,073 bytes**. In an isolated JavaScript audit, the original ZIP's single DEFLATE member `293137.stl` was decoded to **14,684 bytes**. The binary STL header and its actual 292 triangle records were read, with exact-coordinate vertex reconstruction. The resulting original mesh contained **V=148, E=438, F=292**, all 438 edges with exactly two consistently oriented incident triangles, and `χ=148−438+292=2` / combinatorial genus 0. This agrees with prior F16/F17 byte-pinned audits (which previously computed the decompressed raw STL SHA-256 `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`). This isolated F21 JS audit **did not independently recompute the STL SHA-256**; it relies on the pinned original ZIP blob and earlier F16 hash for attribution. Original author upload identity and per-model rights remain **not independently cleared**.

The actual source's bounding box in **undocumented STL coordinate units** is `[-23.889854431152344, -41.42763137817383, 5.253882884979248]` to `[84.23294067382812, 45.19732666015625, 112.51364135742188]`. The finite original-facet dihedral proxy at a threshold of 30 degrees flags **205 of 438** source edges; this is **not** author-provided CAD feature semantics.

## Four-sided decomposition (piecewise linear, not CAD smoothing)

For each oriented input triangle `(A,B,C)`, create the three edge midpoints `M_AB, M_BC, M_CA` from **canonically indexed original edge endpoints**, and the original facet centroid `G=(A+B+C)/3`. Replace the triangle by three oriented quads:

- `(A,M_AB,G,M_CA)`
- `(B,M_BC,G,M_AB)`
- `(C,M_CA,G,M_BC)`

Each new convex planar quadrilateral has a bilinear parameterization. A tensor-product **bicubic Bézier representation of the same bilinear map** is obtained by exact degree elevation: the sixteen controls are the bilinear expression at `(i/3,j/3)`, for `i,j=0…3`, with four corner and boundary controls constructed using a *canonical edge-oriented cubic line control net* to ensure **bit-for-bit identical** reversed seam controls across all incident quads. The `.bp` record order matches the 16-point column-major `p00,p10,p20,p30,p01,…,p33` format used by the APMesh indexed Bézier input reader.

Because the construction partitions each original triangle into three quads in its plane, the geometry agrees with the original piecewise-flat STL surface **as a set in exact arithmetic**. In floating arithmetic a nonzero residual is expected. No smoothing is introduced and C1 regularity across original STL triangle edges is **not claimed**. The three-patch-per-triangle construction is deliberately inefficient; it is a source-domain *feasibility and connectivity control*, not a production-quality quadrangulation.

## Actual input geometry audit (original ZIP decoded through GitHub)

| Property | F21 result |
|---|---:|
| Original raw STL triangle faces | 292 |
| Original exact XYZ vertices | 148 |
| Original triangle edges | 438 |
| Bicubic bilinear patch candidates | **876** |
| New quadrilateral corner vertices | **878** |
| New quadrilateral sides/edges | **1,752** |
| Quadrilateral surface Euler | **2** |
| All shared edges have exactly two oppositely directed faces | **YES** |
| All shared 4-control boundary curves identical after reversal | **YES** |
| Unique indexed BP control XYZ candidates | **7,886** |
| Distinct control pairs subject to the reader's per-coordinate `1e−7` merge tolerance | **0 observed** |
| Min/Max normalized *corner* Jacobian | **0.0833333333333323 / 0.25000000000000006** |
| Largest sampled bicubic-vs-bilinear point discrepancy (STL units) | **2.95110562224397e−14** |

**Interpretation:** This is a geometry/math-stage positive. The minimum Jacobian refers to the **local normalized bilinear corner derivative relative to its parent triangle**, not a global scaled Jacobian quality score of an actual mesh. The discrepancy was sampled at three interior parameter pairs per patch, not a certified continuous Hausdorff-distance bound; exact-arithmetic set preservation follows from the construction proof, not the sample alone. The zero near-control count is specific to the enumerated candidate controls for this pinned input and does not guarantee correct C++ runtime curve grouping.

## Executable Python reproducer and its independently tested scope

- [`probes/thingi10k_f21_piecewise_linear_bezier.py`](probes/thingi10k_f21_piecewise_linear_bezier.py): pure-Python script, explicit source Git-blob and decompressed STL SHA-256 pin, strict one-member ZIP check, exact XYZ connectivity, fail-closed degeneracy/topology rejection, 3F index-quad degree elevation, canonical shared cubic edge nets, Euler/edge incidence checks, bicubic De Casteljau samples, normalized corner Jacobian, legacy APMesh `1e−7` intern tolerance guard, optional private `.bp` and JSON receipt, no overwrite and partial-output cleanup.
- [`probes/test_thingi10k_f21_piecewise_linear_bezier.py`](probes/test_thingi10k_f21_piecewise_linear_bezier.py): **30/30 synthetic hermetic tests PASS** on 2026-11-23. Tests include zipped STL identity, tampering, wrong member paths, source orientation, open/duplicate/degenerate/NaN input, tetrahedral genus-0, toroidal genus-1, triangulated cube, exact boundary continuity, numerical degree elevation, Jacobian, legacy merge risk and local private-publication semantics.
- [`evidence/thingi10k/thingi10k_f21_293137_original_geometry_audit.json`](evidence/thingi10k/thingi10k_f21_293137_original_geometry_audit.json): numerical **actual original-byte** F21 audit receipt. This receipt records the JS source of the numerical observations and explicitly denies scientific mesh admission.

The Python implementation and its 30 tests ran on synthetic STL fixtures locally. Because the original GitHub ZIP was delivered to the isolated connector but **not mounted as a local original file** on the test workstation, the new Python CLI **was not executed on the real #293137 ZIP in this round**; no original-model `.bp` was written or committed. The independent JS computation analyzed the original geometry directly, including all 876 candidate nets and 1,752 paired seam edges. Do not conflate these execution pathways.

### Reproduction against the authorized original ZIP on a research workstation

Download the exact pinned archive only where authorized for private analysis, then run:

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_thingi10k_f21_piecewise_linear_bezier
python thingi10k_f21_piecewise_linear_bezier.py \
  --source-zip /private/Thingi10K/293137.stl.zip \
  --private-output-bp /private/apmesh-f21/293137_piecewise_linear_candidate.bp \
  --private-receipt /private/apmesh-f21/293137_candidate_receipt.json
```

Only publish hash/count receipts in Git. Do **not** commit, redistribute or call the generated `.bp` an approved mesh without original per-asset rights review. The script must **stop** if the pinned source bytes, closed incidence, source topology, internal seam or legacy control-merge check fail. Private `.bp` output is a candidate source domain, not an APMesh-generated QUAD mesh.

## Admission boundary and next task

- Original source geometry topology: **verified by independent original-byte F21 JS** and earlier F16/F17 audits.
- Reproducible mathematical construction: **YES** for a piecewise-flat input, with a separate synthetic Python test suite.
- Private actual-source BP file from the new Python reproducer: **NOT EXECUTED**.
- Native APMesh C++ `.bp` reader, canonical curves, accepted TRI and supported QUAD generator: **NOT EXECUTED**.
- Continuous geometric distance certificate beyond construction theorem: **NOT EXECUTED**.
- Original asset license/rights: **NOT CLEARED**.
- Comparability with QuadWild published outputs: **NOT DEMONSTRATED** (this #293137 Badia source has no published QuadWild QUAD output pair).
- New accepted S40 source faces, patches or scientific comparison: **ZERO**.

**F22** should use the byte-pinned private output to run the original C++ BP reader in a sandbox, inspect actual curve/patch graph and its `1e−7` interning effect, then measure real native TRI output and (if supported) QUAD separately. Keep the PR DRAFT, main and earlier 156-patch/22-source-face S40 baseline unchanged.
