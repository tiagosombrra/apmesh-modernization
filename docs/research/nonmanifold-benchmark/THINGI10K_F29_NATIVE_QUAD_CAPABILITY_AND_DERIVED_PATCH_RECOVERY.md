# S40-F29 — Original APMesh QUAD capability boundary and private, derived QUAD recovery

**Date:** 2026-11-23. **Repository:** `tiagosombrra/apmesh-modernization`. **Research branch:** `research/benchmark-corpus-reverse-patches`; **PR:** #225 (Draft). **Classification:** capability audit + experimental external surface reconstruction; **not a native QUAD-generator implementation, new CAD surface, or admitted science benchmark**.

## Executive conclusion

The audited original C++ serial/default APMesh pipeline remains **triangular**. Its domain *quadtree* is a spatial refinement structure, **not** an output QUAD mesh. Native `WRITE_MODE=q` selects **quality reports**, not quadrilateral faces; `WRITE_MODE=h` writes a triangular OBJ plus quality reports. The existing physical type is `TriangleAdaptive`, the temporary front `Face` owns exactly three vertices, and the exported OBJ uses `TriangleAdaptive` node 1/2/3. No original C++ `GeneratorQuad`/native QUAD output was executed or established. These statements apply to the exact audited source, **not** every possible future or other-branch module.

A **different, private derived artifact** was constructed after F27 generated actual 3,504 native triangles and F28 joined their seams by genuine source identities. Every original F21/F22 four-sided control patch produced exactly four triangles meeting at one interior center. Removing **only that center** and recovering the four original patch boundary vertices produces **876 four-node planar convex QUAD** (3 recovered QUAD per original 292 STL triangles). This precisely inverts the hand-authored-for-research STL-to-patch construction. It is **not an independently optimized quadrilateral mesher** and provides no new CAD/freeform surface recovery. None of the earlier S40 native and frozen sources were altered.

## Source-pinned original C++ capability

| Audited original file | Git blob SHA-1 | Relevant native contract |
|---|---|---|
| `include/data/triangle_adaptive.h` | `9bfcff6bd128d62374daf39b47a7b5255b1416a6` | `TriangleAdaptive` is the physical element |
| `include/crab_mesh/aft/face.h` | `c615cd59c555152a43daad7d999b8caa3bf6da65` | Temporary advancing-front `Face` has `Vertex *v[3]` |
| `src/generator/generator_adaptive.cpp` | `60400e9c532ae80c8605a9e833ac4dfd70bfcb73` | TRI writer and distinct `m/q/h` reporting modes |
| `src/input_output/write_obj_file.cpp` | `453416ed67f9bbc985e26ebea3a18c39da168807` | Legacy physical writer enumerates exactly three triangle nodes |
| `include/input_output/input_validation.h` | `bc7988e862383f2f264f9d3a2a7691fe5c028592` | Config accepts `WRITE_MODE=q` as a reporting mode |

**Runtime negative control:** The **unchanged**, original static C++ executable from [F27 Actions run 45164751761](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45164751761) (binary SHA-256 `9ee068d7c0809476d37b77fb8d8bef4cbede21db5efe68ed2a3b13343b5b401f`) ran a **public-domain-generated synthetic one-patch control** with its original CLI profile changing only `WRITE_MODE=h` to `WRITE_MODE=q`. It **exited 0**, produced **one quality log, one metrics CSV, one acceptance log** and **zero OBJ files**. Original stage 0 was accepted. This is an execution-based *negative* QUAD capability gate, not an attempt to rebrand `q` as quadrilaterals. Its source-derived config and temporary logs stay private; only aggregate receipt was published.

## Exact private source and prior evidence

- Original Thingi10K #293137 binary STL SHA-256 `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`, **292 TRI**.
- Independent F21/F22 indexed Bezier `.bp` SHA-256 `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0`, **876 control patches**. It is a planar degree-elevated source-derived construction, not original CAD.
- F27 **actual original APMesh C++ TRI** OBJ SHA-256 `145b40c2f542a9d1d18bcda6eccc01c8861be83d247418af96fa18b4c860c325`: **4,380 vertices/3,504 faces** before seam reconstruction, **876 index-disconnected patch components**.
- F28 **separate source-aware stitched TRI** OBJ SHA-256 `b93995d1319e702649574044b2167fa01fe90644b1e5e02a295f3b47cdfdc46b`: **1,754 vertices/3,504 triangles**, one connected closed orientable surface. Original F27 OBJ immutable.

For each of the two independently verified actual native F27 runs, F29 re-executes the complete F28 source-aware audit (source STL, `.bp`, original OBJ, 876 native curve identities and source-normal/provenance checks), byte-verifies the unmodified F28 stitched OBJ and requires **four precisely oriented TRI per source patch**, four distinct boundary corners, and a unique disposable interior node. The derived QUAD OBJ is created in a separate mode-0700 private directory; an existing private file or evidence receipt cannot be overwritten.

## Actual recovered QUAD, with explicit limitations

| Invariant / property | Observed real #293137 derived F29 |
|---|---:|
| Private QUAD OBJ SHA-256 | `e2687802ec3314178a973282a33ffd86d71ee8aaa87eed3d4976b266000cf548` |
| Private QUAD OBJ bytes | **38,834** |
| Original created Bezier patches / derived quads | **876 / 876** |
| Vertex coordinates in derived OBJ | **878 original F28 positions; none added or changed** |
| Discarded patch-center nodes | **876** |
| Derived edges, face count | **1,752 edges / 876 quadrilaterals** |
| Connected components / free edges | **1 / 0** |
| Invalid winding / edge nonmanifold / vertex-link singularities | **0 / 0 / 0** |
| Euler characteristic / genus under established closed orientable assumptions | **2 / 0** |
| Reflex or inverted QUAD corners | **0** |
| Source STL edges preserved as two QUAD segments | **438 / 438 (876 segments)** |
| Source edges with dihedral ≥30° preserved | **205 / 205 (410 segments)** |
| Source facet crossings, geometric smoothing, new coordinates | **0 / 0 / 0** |
| Total full-precision source area vs derived QUAD | **29,490.715496607303 / 29,490.715496607303** squared source units |
| Max full-precision relative QUAD-to-four-original-TRI patch area error | **1.55×10⁻¹⁵** |
| Max full-precision planar corner deviation | **5.89×10⁻¹⁵** source units |

**QUAD-specific quality must not be mixed with TRI `2r/R`:** minimum corner angle **1.1053°**, maximum **178.8252°**, minimum scaled Jacobian at the four corners **0.01929** (dimensionless), mean of per-quad minimum scaled Jacobians **0.59806**, **159/876 (18.15%)** quads with a minimum corner angle below 30°, **11/876 (1.26%)** below 10° and **160/876 (18.26%)** with a maximum corner angle above 150°. All corners are locally convex at full precision, but **many faces have poor shape**. No smoothing, reparameterization, pairing heuristic, topology relocation, optimization or performance superiority is claimed.

**Independent Trimesh v4.11.1 check:** the separate private derived QUAD OBJ has 878 vertices, **876 four-index faces in the original OBJ**; Trimesh internally triangulates these into 1,752 triangles for inspection. It reports **watertight, winding consistent, positive volume, Euler 2, one component**, while the prior F28 TRI remains watertight with one component. Trimesh area/volume computed on six-digit rounded OBJ coordinates differ slightly from the prior F28 TRI because it retriangulates potentially noncoplanar *rounded* quads via a different diagonal. These rounded-export differences are **not** an original-CAD surface discrepancy and do not affect the high-precision source area identity. No global self-intersection test or per-object redistribution permission is established.

## Reproducibility and admission boundary

- The private recovered QUAD OBJ was regenerated **twice** from the two native F27 runs in swapped order, byte-identically (SHA-256 pinned above); it is **not** stored in GitHub nor included in the downloadable research package.
- **49/49** directed synthetic/negative unit tests passed locally, covering missing/reversed native patch fans, duplicate centers and corners, incorrect topology/winding, nonplanarity, concavity, original node/tag preservation and write/overwrite refusal. The original code-only F27/F28 47-test gates remain independent checks.
- The code-only GitHub CI verifies the actual pinned C++ source contracts and runs the three distinct test suites **without** any third-party source mesh or derivative model data.
- Public artifacts: source-only capability/QUAD recovery tool, tests, optional Trimesh diagnostic tool, numeric receipts and this report. No original STL/ZIP, private `.bp`, native F27 OBJ or F28/F29 derived OBJ, full native snapshots or coordinate maps are in the PR or release ZIP.
- **Not scientific benchmark admission:** no native QUAD generator, comparison to QuadWild's source/output pairs, author-CAD freeform quality, rights grant or external mesh quality advantage. Retain S40 original 156 CAD patch baseline unchanged. F29 does **not** substitute the user’s separate QUAD meshing research line or implement native adaptation.

## Reproduction commands (authorized private local copy)

From the full checkout, with private source/provenance data copied **outside the repository**, run:

```bash
python3 docs/research/nonmanifold-benchmark/probes/thingi10k_f29_quad_capability_and_recovery.py --source-root .
python3 -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_thingi10k_f29_quad_capability_and_recovery.py' -v
python3 docs/research/nonmanifold-benchmark/probes/thingi10k_f29_quad_capability_and_recovery.py \
  --source-zip PRIVATE/293137.stl.zip \
  --private-bp PRIVATE/293137_piecewise_linear_candidate.bp \
  --native-run-1 PRIVATE/f27/first-native-run \
  --native-run-2 PRIVATE/f27/second-native-run \
  --f28-private-stitched-obj PRIVATE/f28/293137_derived_source_seam_stitched.obj \
  --private-output-dir PRIVATE/f29/new-quad-output \
  --public-receipt PRIVATE/new-sanitized-receipt.json
```

The last command validates **actual original TRI-generation outputs**, then writes a **different QUAD derived OBJ** to the specified private directory. It deliberately cannot create a QUAD mesh through the original CLI.

**Next F30 gate:** separately scope native QUAD meshing as a new scientific algorithmic proposal requiring advisors' alignment; investigate quality optimization with pinned trade-offs to feature edges, 876 original partition quads, distortion and Jacobi thresholds. A native QUAD claim requires **actual native output and acceptance evidence** from a dedicated native QUAD implementation, not this export-conversion prototype.
