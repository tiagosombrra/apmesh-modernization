# S40-F27 — Original APMesh TRI execution on an authentic private Thingi10K STL-derived domain

**Date:** 2026-11-23. **Branch:** `research/benchmark-corpus-reverse-patches` / PR #225 (**Draft**). **Scope:** native original C++ initial TRI generation and independent physical/topological audit for a single real original-derived patch model. This stage **does not** admit a scientific QuadWild-vs-APMesh pair, certify global native connectivity, or authorize third-party data redistribution.

## Provenance: actual code and actual geometry, kept separate

- **Source input:** real Thingi10K **#293137 Bunny LowPoly**, an original **292-triangle** binary STL from the immutable public mirror archive, ZIP Git blob SHA-1 `359c26b16664e9ba8d2415ca065a85bd27504d5f`, decompressed STL SHA-256 `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`. This is a **Badia literature** case, not a case with verified original QuadWild author output. Upstream asset-specific permissions remain unverified.
- **Candidate four-sided APMesh domain:** the actual original STL was deterministically partitioned into three four-sided bilinear patches per triangle and degree-elevated to **876 bicubic Bézier patches**, **7,886 indexed controls**, and **1,752 shared four-control boundaries**. Its private `.bp` is **538,482 bytes**, SHA-256 `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0`. This reproduces a *piecewise-flat STL surface*, not authored CAD curves, smooth interpatch continuity or a general surface reconstruction algorithm.
- **Original C++ generator:** [code-only GitHub Actions build/run 45164751761](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45164751761), source commit `56d793bfe611b7352d9cd4f8dc6f5e025f5b84b0`, workflow `.github/workflows/research-f27-private-original-tri-cli.yml`: successfully built the **unchanged original `ap_mesh_engine` and `src/main.cpp`** into a static Linux executable. It compiled against the full source checkout in GitHub Actions **without obtaining, processing or publishing the third-party source/derived geometry**. The downloaded code-only binary SHA-256 was checked locally against `9ee068d7c0809476d37b77fb8d8bef4cbede21db5efe68ed2a3b13343b5b401f` (ELF 64-bit, statically linked).
- **All model-specific executions** happened in a private isolated directory outside the Git repository, never in public CI. No original STL, original ZIP, derived `.bp`, native OBJ, high-precision snapshot, or original vertex XYZ has been added to Git or the public ZIP delivery.

## Frozen experimental settings, acceptance definition, and two original executions

The independent Python driver `probes/thingi10k_f27_native_tri_evidence.py` pins **both input hashes**, the original C++ binary hash, and the 20 configuration settings. Only the private absolute `INPUT_MODEL` and private `OUTPUT_PREFIX` vary between runs. The profile is **serial** (`NUM_PROCESSES=1`, `NUM_THREADS=1`, MPI/OpenMP disabled), `ADAPTIVE_MODE=research_debug`, intensity `0.02`, maximum steps `2`, curve sampling bounds `3..16`, quadtree depths `2`, and `ENABLE_HYBRID_RECONSTRUCTION=0`. `WRITE_MODE=h` refers to the legacy *mesh + quality export choice*, **not** an admission of QUAD/hybrid output. Resource limits per native process: **2 GiB virtual address space**, **180 CPU seconds**, **150 s elapsed timeout**, **64 MiB per output file**, no core dumps. Each run uses a fresh output directory and a strict zero-exit process receipt.

Two new, independently launched original native CLI processes completed with **exit code 0**, **wall times ~0.3738525 s and ~0.3724603 s**, on the exact pinned private BP. The earlier preliminary two processes (~0.419 s each) also exited 0; their independent artifacts agree with the final checked repeat. Native output for the final runs includes:

- `bunny_passo_0_malha_0.obj`: **3,504 native TRI faces**; SHA-256 `145b40c2f542a9d1d18bcda6eccc01c8861be83d247418af96fa18b4c860c325`.
- `bunny_passo_0_incidences.json`: 876 patch records, actual complete source-curve identities, full-precision node and triangle UV/XYZ; SHA-256 `76c0c3eb7c0bd257b2d0ec97d151d0e6d99fa9fa88fe2bc06d17f8e1007e431a`.
- `bunny_passo_0_acceptance_accepted.log`: stage **0 accepted=1**, SHA-256 `1f241c0b6d1b05adcb0607f705054ca588071242d24ac4b2e7482730c3a119e4`.
- `bunny_n.process__metrics_rank_-1.csv`: one stage, 3,504 TRI, SHA-256 `8d969920240b043a2fe5195b14c231e29dd76784e6f055b37d186bd4a90d6c14`.

**All four native artifacts are byte-identical between the two final runs.** The checker also reconciles every full-precision native snapshot node and face with the actual six-significant-digit exported OBJ; fabricated/cross-run output cannot pass the source-preserving gate merely because it contains plausible triangle counts.

The APMesh initial stage reports **zero curvature-derived global error** on these piecewise-planar patches and stops immediately at stage 0. The zero error **is not** a bidirectional geometric error certification or evidence of adequate treatment of sharp transitions between original STL facets: the interior of each bilinear patch is planar.

## Independent topological census: native indexed OBJ versus exact-XYZ diagnostic

| Property | Unmodified native indexed OBJ | Diagnostic after exact-coordinate welding (not native output) |
|---|---:|---:|
| Vertices | **4,380** | **1,754** |
| Triangular faces | 3,504 | 3,504 |
| Unique edges | 7,008 | 5,256 |
| Connected components | **876** | **1** |
| Free/boundary edges | **3,504** | **0** |
| Edges incident to exactly two faces | 3,504 | 5,256 |
| Nonmanifold (>2) edge incidences | 0 | 0 |
| Oriented-edge winding conflicts | 0 | 0 |
| Closed-cycle vertex links | 876 | 1,754 |
| Open-path vertex links | 3,504 | 0 |
| Singular/disconnected vertex links | 0 | 0 |
| Euler characteristic | **876** | **2** |

The original indexed OBJ consists of **876 disconnected topological disks**, one per patch, with **2,626 duplicate vertex indices** located at exactly equal *exported XYZ* coordinates. The production exporter `GeneratorAdaptive::WriteMesh` in `src/generator/generator_adaptive.cpp` deduplicates by **node ID**, not by shared XYZ, and the initial submesh assembly preserves separate boundary node IDs. The raw OBJ therefore **cannot be represented as a closed connected manifold for genus/benchmark purposes without an explicit, independently justified assembly operation**.

A strictly **exact exported-coordinate** (no epsilon, no smoothing or geometry changes) diagnostic maps equal OBJ vertices to a single index and obtains **one closed, connected, consistently oriented combinatorial surface**, all vertex links single cycles, **Euler χ=2, conditional genus 0**. This is a *verification of potential spatial stitchability for this case*, **not evidence that native APMesh produced a stitched global OBJ**. For other surfaces with self-contact, exact coordinate welding might incorrectly merge independent sheets; no general stitching fix is admitted by this control.

## Geometry and numerical quality

Full-precision incidence triangles were assigned to their source triangle via the documented **three-patches-per-original-facet** construction; all **12 generated triangles per source facet** were independently checked for source-plane distance, barycentric containment and normal orientation:

- Original STL facet area sum: **29,490.71549660732** squared *unknown STL units*.
- Native full-precision TRI area: **29,490.715496607325**; absolute total difference: **3.64e-12** squared STL units.
- Maximum local relative source-facet area difference **1.13e-15**, point-to-source-triangle-plane distance **1.82e-14** STL units, barycentric outside violation **6.13e-14**, and **zero** inverted faces in the original source-facet normals.

These are precise checks **against the given faceted STL**, not against an independently available original CAD surface. OBJ coordinates are rounded to six significant digits; quality metrics below are independently recomputed **from the actual exported OBJ**, compared with the native CSV and acceptance log using the existing export-specific tolerances:

| TRI quality (scaled 2r/R) | Original 292-facet STL | Original APMesh stage-0 3,504-facet OBJ |
|---|---:|---:|
| Minimum | 0.00250092 | **0.00030749** |
| Arithmetic mean | 0.717143 | **0.594211** |
| Triangles below 0.30 | 22 / 292 | **602 / 3,504** |
| Percentage below 0.30 | 7.53% | **17.18%** |

The source and output have **different resolutions and different face partitions**. This descriptive change is *not* a controlled improvement/degradation causal claim about mesh algorithms. It does demonstrate that **native stage acceptance alone does not ensure acceptable global triangle quality**.

## Evidence automation and preservation

The source-only independent checker and its **47/47 hermetic synthetic/negative Python tests PASS locally**. Controls reject malformed source hashes, altered private `.bp`, incomplete/contradictory acceptance and metric evidence, nonfinite/invalid OBJ, duplicated or nonmanifold facets, inconsistent native snapshot positions, source-geometry deviation, mismatched native repeat outputs, modified run configuration, nonzero process exit, and modified binary/standard output hashes. The checker **does not** assume that Euler equality proves a manifold: it explicitly checks edge degree, winding, components and vertex-link structure before interpreting the conditional genus.

Reproduce on a *permitted local workstation holding the exact original source and private BP*:

```bash
python -m unittest -v test_thingi10k_f27_native_tri_evidence
python thingi10k_f27_native_tri_evidence.py \
  --source-zip /private/293137.stl.zip \
  --bp /private/293137_piecewise_linear_candidate.bp \
  --binary /private/apmesh_f27_original_static_cli \
  --replay-root /private/new-f27-replay-root \
  --receipt /private/new-f27-numeric-receipt.json
```

The replay root and numeric receipt must not exist beforehand. The checker and unit tests are published; only **aggregate numeric/hash evidence**, the compiled code provenance and the script are retained in the research branch. The native binary is a temporary GitHub Actions **code-only** artifact (short retention). Original binaries from the F26 native Geometry probe are not interchangeable with the F27 mesher executable.

## Boundary of scientific claims and F28

**Measured:** the unchanged original C++ TRI generator successfully generated, logged, accepted and exported a real candidate 3,504-face **initial** surface from the actual pinned #293137 STL-derived patch domain, with complete repeatable evidence and full-precision/source geometric checks. This removes the previous *generator-not-run* blocker for one original model, but does **not** establish a canonical CAD-based APMesh comparison to the Badia/QuadWild papers.

**Still not admitted:** globally stitched native OBJ, scientifically fair method/input equivalence, dataset author-output pair, per-asset reuse rights, C1 smooth CAD patch domain, high-quality TRI, QUAD/QUAD-dominant meshing, experimental repeatability across hardware/toolchains or validated speedup.

**Recommended F28:** build a separate **non-destructive, explicit-ID-consistent seam/vertex correspondence export control** and audit it against the unmodified native OBJ and full-precision incidence snapshot. Retain original artifacts, fail closed on self-contact/near-duplicate collisions, add low-quality distribution and sharp-feature checks, and isolate any postprocessing runtime from native APMesh runtime. Do not silently weld production nodes or retrofit the existing accepted S40 cases.
