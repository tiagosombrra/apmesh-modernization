# S40-F28 — Source-topology-aware seam reconciliation and STL crease retention

**Research date:** 2026-11-23. **Repository:** `tiagosombrra/apmesh-modernization`. **Research branch:** `research/benchmark-corpus-reverse-patches`; PR #225 remains **DRAFT**. No `main` changes, releases, scientific-model admission, rights clearance, nor QUAD generation.

## Decision and provenance

The F27 immutable, original APMesh C++ CLI (built in [code-only CI run 45164751761](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45164751761)) **actually generated** stage-0 TRI on the private, genuine #293137 Thingi10K-model-derived patch input. Two original native processes exited 0 and were byte identical for the original OBJ, incidence snapshot, acceptance log, and metrics CSV. This F28 work **does not reimplement or modify the mesher**. It treats the F27 original OBJ as immutable and constructs a **different, explicitly derived, private OBJ** in a new directory.

The source dataset is the original mirror `larsbrubaker/Thingi10K-meshes-2` at immutable ref `ab50a098405dc2dfcf882e87dab3811b5ea8ce92`, `meshes/293137.stl.zip`, whose Git blob is `359c26b16664e9ba8d2415ca065a85bd27504d5f` and decompressed STL SHA-256 is `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`. The F21/F22 source-topology-preserving piecewise-planar, degree-elevated `.bp` has SHA-256 `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0`, 7,886 controls and 876 patches. The native F27 OBJ is SHA-256 `145b40c2f542a9d1d18bcda6eccc01c8861be83d247418af96fa18b4c860c325`. It has six-significant-figure exported XYZ and unique node IDs per patch, not native welded global connectivity. The native incidence snapshot contains the original, higher-precision node positions, UV coordinates and four curve IDs per patch.

## Why coordinate-only welding is not the method

A global “equality-of-XYZ” rule can erroneously connect unrelated source sheets that touch or share coincident positions. It also loses the provenance needed to decide whether a high-dihedral ridge is supposed to remain sharp. This stage requires both **(1) an original closed, opposite-oriented native shared `CurveAdaptive` pair** and **(2) identical provenance from the pinned source STL topology** for every vertex union. The original #293137 STL was already checked to be an oriented closed genus-0 triangle surface; no assumption about other STLs is made.

For each input source triangle `t = (a,b,c)`, the F21 construction creates three quadrilaterals `(a,m_ab,g,m_ca)`, `(b,m_bc,g,m_ab)`, and `(c,m_ca,g,m_bc)` where `g` is the facet centroid. In the F27 initial TRI stage each patch has four parametric corner nodes and one interior node. F28 labels each corner by either the original STL vertex, the unordered **source-edge endpoints** (edge midpoint), or the **facet ID** (centroid); patch interiors are tagged by **unique patch ID**. Identities are checked against the actual F27 snapshot UV records, source coordinates, and the 16 Bézier controls of every patch.

For each shared native curve, a union-find structure merges **only** the two corresponding labeled endpoints on its two incident patches. Controls must match in opposite contour order and full-precision evaluations must agree componentwise within a fixed **1e-11 source-unit audit tolerance** (not a mesher or smoothing tolerance). The *measured* maximum source-corner evaluation difference is `8.881784197001252e-16`, native seam endpoint difference `1.5543122344752192e-15`, and opposite shared-control difference **zero**. Exported six-significant-figure XYZ must match **exactly** for every merge. Distinct source labels at the same full-precision or rounded position, unpaired/multiply paired curves, reversed winding, missing UV records and nonconforming corners are rejected rather than repaired. This is not a general mesh-welding tool.

No original `v` line is changed: the derived file selects the earliest original textual coordinate for each authorized union and rewrites **only the `f` vertex indices**. It retains native TRI face order and face orientation. Every original geometric triangle's exported coordinates and `2r/R` quality are bitwise equal under the established one-to-one face remap. All original mesh geometry and the 4,380→1,754 private remapping table remain **local**, not public.

## Observed actual-native result and separately derived result

| Measurement | Original APMesh F27 OBJ | Private F28 stitched derivative |
|---|---:|---:|
| OBJ vertices | 4,380 | 1,754 |
| TRI faces | 3,504 | 3,504 |
| Indexed edges | 7,008 | 5,256 |
| Indexed components | 876 | 1 |
| Indexed free edges | 3,504 | 0 |
| Euler characteristic | 876 | 2 |
| Vertex-link singularities | 0 | 0 |
| High-incidence edges | 0 | 0 |
| Winding conflicts | 0 | 0 |

- Original APMesh source-matched, opposite-C0 shared curves: **1,752**.
- Curve and source-entity-authorized native vertex-index unions: **2,626**.
- Unique derived source entities, including **876 unique patch-interior nodes**: **1,754**.
- Detected cross-entity false aliases at exported XYZ precision: **zero** for this pinned input. The negative synthetic corpus includes *two geometrically coincident but topologically disconnected closed tetrahedra*; F28 refuses global welding of those sheets.
- Derived private OBJ SHA-256: **`b93995d1319e702649574044b2167fa01fe90644b1e5e02a295f3b47cdfdc46b`**, 98,801 bytes. Generated identically from both verified original-native F27 runs. No original/native/derived OBJ or private index mapping has been committed or added to any distributed ZIP.
- The stage-0 3,504 TRI face qualities are **unchanged**: minimum `2r/R = 0.0003074899137272615`, mean `0.5942111212551515`; **602/3,504 (17.1803652968%)** are below 0.30. Topological repair does **not** cure poor triangle shapes.

## Sharp STL feature preservation

The original STL has **438 manifold edges**, including **205** with an inter-facet normal angle ≥30° (a dihedral proxy; angle/units are geometric, not semantic CAD-feature labels). Each source edge is split into two boundary segments by its original midpoint. The test enumerates all **876** reconstructed source-edge segments in the derived TRI graph and verifies that their two adjacent native facets correspond exactly to the two original STL incident facets (never faces from a different source edge). The **410** segments belonging to the **205 sharp ≥30° edges** are retained. Using the native full-precision incidence snapshot and source STL, the largest deviation of a native face normal from its original parent face is `1.4787793334710982e-06°`, and the largest deviation between a segment's observed dihedral and the source dihedral is `2.191182651989365e-11°`. **No smoothing and no newly computed vertex positions** are used in the exported artifact. These bounds do not prove that every downstream import/export preserves the same face normals.

## Independent library corroboration, export precision and explicit limitations

An optional independent Python **Trimesh 4.11.1** pass, operating only on the authorized **private** files, confirms:

| Property | Original source STL TRI | Original APMesh OBJ | F28 derived OBJ |
|---|---:|---:|---:|
| `is_watertight` | true | false | true |
| `is_winding_consistent` | true | true | true |
| Connected bodies | 1 | 876 | 1 |
| Euler characteristic | 2 | 876 | 2 |
| Reported surface area (source/export coordinates) | 29,490.715496607303 | 29,490.723809947594 | 29,490.723809947594 |
| Reported signed volume (source/export coordinates) | 273,280.0337419664 | 273,280.0637890109 | 273,280.0637890109 |

The OBJ export uses ~six significant figures, so its area/volume are not numerically identical to **full-precision** native triangles or the original STL: relative source-vs-OBJ differences are `2.8189686656833297e-07` in area and `1.0994965162950229e-07` in volume. The native and derived OBJs have **identical** area and volume because no geometry was altered. F27's much smaller original-surface/full-precision native area residual (`~3.64e-12` squared source units) is a **different precision comparison**, not a contradiction.

**Not proved:** global absence of surface self-intersections (topological closure alone cannot prove that), recovery of original CAD surfaces, C1 continuity, anisotropic/high-quality remeshing, error or performance improvement, independent third-party redistribution rights, a matched literature-output pair, or any original APMesh QUAD generation. This stitched OBJ is a new research derivative, **not** the original accepted APMesh output. Never replace or edit original accepted model outputs, S40 reference, or the `main` branch.

## Reproduction (local; user-provided authorized private paths)

The standard-library-only main audit uses [F27's preceding original TRI audit script](probes/thingi10k_f27_native_tri_evidence.py) from the same revision and [F28's seam source](probes/thingi10k_f28_topology_aware_stitch.py):

```bash
python3 -m unittest discover -s docs/research/nonmanifold-benchmark/probes \
  -p test_thingi10k_f28_topology_aware_stitch.py -v

python3 docs/research/nonmanifold-benchmark/probes/thingi10k_f28_topology_aware_stitch.py \
  --source-zip PRIVATE/293137.stl.zip \
  --private-bp PRIVATE/293137_piecewise_linear_candidate.bp \
  --first-native-run PRIVATE/native-attempt-1 \
  --second-native-run PRIVATE/native-attempt-2 \
  --private-derived-output PRIVATE/new-stitched-obj-directory \
  --receipt PRIVATE_OR_REPORT_OUTPUT/new-f28-coordinate-free-receipt.json

# Optional independent verification; requires locally installed numpy and trimesh.
python3 docs/research/nonmanifold-benchmark/probes/thingi10k_f28_optional_trimesh_crosscheck.py \
  --source-zip PRIVATE/293137.stl.zip \
  --native-obj PRIVATE/native-attempt-1/bunny_passo_0_malha_0.obj \
  --derived-obj PRIVATE/new-stitched-obj-directory/293137_derived_source_seam_stitched.obj \
  --receipt PRIVATE_OR_REPORT_OUTPUT/new-f28-trimesh-receipt.json
```

This stage's **47/47 hermetic tests** use only an original synthetic tetrahedral surface; they enforce source-entity-specific joins, valid curve incidence, exact exported XYZ on merged nodes, guards against false co-located disconnected bodies, native face order, seam tolerances, source crease edges, source shape/quality invariance and refusal to overwrite existing private results. The optional Trimesh cross-check is **private-runtime only**, not a GitHub Actions CI requirement. The code-only CI must not access or upload the protected geometry. Public receipts are restricted to hashes/counts/numeric aggregate results. Retain the original F27 source/native OBJ hashes, never publish actual private files inadvertently.

## F29 follow-up

Only after F28, independently evaluate whether the original APMesh has a truly native supported QUAD output path for this exact domain. Keep the author-QUAD-reference/permissions gate separate. Do not classify the derived F28 TRI stitch as a QUAD mesh, a certified artifact for other STL topologies, or a fair QuadWild/Badia comparison. Any future connected native export requires separate production contract and downstream regression qualification.
