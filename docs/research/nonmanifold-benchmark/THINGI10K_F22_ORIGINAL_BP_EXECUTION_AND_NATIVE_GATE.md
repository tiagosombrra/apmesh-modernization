# S40-F22 — Original #293137 ZIP → private BP: executed; native APMesh meshing remains blocked

**Execution date:** 2026-11-23. **Research branch:** `research/benchmark-corpus-reverse-patches` (PR #225 DRAFT). **Scientific stage:** original-source representation constructed and independently inspected; **not native APMesh TRI/QUAD mesh admission**.

## Original source acquisition and integrity

A byte-for-byte private working copy of `larsbrubaker/Thingi10K-meshes-2@ab50a098405dc2dfcf882e87dab3811b5ea8ce92`, path `meshes/293137.stl.zip`, was obtained through the connected GitHub repository source, not the article's mesh output archive. The archive was verified by **Git blob SHA-1 `359c26b16664e9ba8d2415ca065a85bd27504d5f`**, exact ZIP size **7,073 bytes**, unique `293137.stl` member, archive CRC32 and **decompressed binary STL SHA-256 `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`** (14,684 bytes). This reproduces F16/F17 identity with independently recomputed SHA-256 in this stage.

**Do not redistribute original ZIP/STL or derived BP geometry.** The rights of the individual author and correspondence to the original author upload are not independently established. This source comes from the Badia cohort, **not a case with a published matching QuadWild output**.

## Actual Python execution against original bytes

The previously committed F21 generator was **actually executed** with the original #293137 ZIP on a private Linux workspace. Python 3.13, in the existing isolated work area. Its verified indexed BP output was **538,482 bytes**, SHA-256 **`6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0`**. The private receipt and BP were not added to Git.

- Original input graph: **292 triangles**, **148 exact XYZ vertices**, **438 two-face edges**, `χ=2`, combinatorial genus 0; 205 edges exceed the **30° normal-dihedral proxy** (not authoritative CAD feature classification).
- Candidate domain: **876 bicubic patches**, **7,886 unique control coordinates**, **878 patch-corner vertices**, **1,752 paired patch edges**, `χ=2`, zero unmatched or multi-owner seams, zero near-distinct-point collisions within the C++ reader's `1e-7` component tolerance in the F21 generator.
- **Three actual-input repeat generations** gave byte-identical BP SHA-256 (individual times **0.240276 / 0.157532 / 0.165256 seconds**, local Python wall-clock only). They are not APMesh generator measurements.
- **30/30** previous F21 synthetic Python tests re-executed, passing.

## Independent generated-BP validation

The new standard-library-only F22 verifier rereads the private ZIP and private `.bp` independently of the F21 generator. It checks the source Git/SHA identity, each original triangle against the three corresponding patch corner quadruples, every degree-elevated 16-point control net, exact 4-control reversed shared sides, positive normalized *four-corner* Jacobians, original triangle/quad area, and the 876/878/1752 Euler graph. On actual bytes:

| Item | Measured output |
|---|---:|
| Source total triangle area (unknown squared source units) | 29490.71549660732 |
| Candidate total quad area | 29490.71549660732 |
| Maximum three-quads-versus-one-triangle area error | 2.842170943040401e-14 |
| Maximum source-corner deviation | 0.0 |
| Maximum bicubic-control versus bilinear elevation deviation | 2.0097183471152322e-14 source units |
| Minimum/maximum normalized corner Jacobian | 0.0833333333333323 / 0.25000000000000006 |
| Exactly paired, reversed cubic C0 seams | 1,752 / 1,752 |

These numbers are finite-precision controls, not a certified continuous Hausdorff bound, smooth CAD surface, genus proof for an unseen APMesh output or published QuadWild benchmark. The representation is piecewise-flat and usually not C1 across original STL edges.

A separately compiled **independent C++17 BP reader/edge checker** (GCC 14.2.0, `-std=c++17 -O2`) also processed the *actual generated BP* and confirmed **7,886 controls, 876 patches, 1,752 paired seams**. Its own grammar and boundary checks are independent probes, **not the original APMesh C++ reader**. The additional `thingi10k_f22_native_header_integration.cpp` explicitly includes the *real* APMesh `include/input_output/input_validation.h` and provides a command to check the original input validation function **once the complete repository checkout is available**; it was **not compiled/executed in this isolated environment**.

## Native reader scaling risk identified without executing it

The real `src/input_output/control_patch_reader.cpp` calls `FindControlPoint(vectorControlPoints, p[i])` for each of the **14,016 indexed controls**. `FindControlPoint` receives its vector by **const reference** and scans sequential IDs, so the observed code does **not** imply copying all 7,886 input points on each lookup. For this pinned BP, summing the ordinal positions of all indices yields **51,714,078 potential ID comparisons** in this linear-lookup path. This is a static cost model, **not measured runtime**, not evidence of an actual performance problem, and not a justification to change the production loader before obtaining a genuine native trace.

## Hermetic regressions and reproducibility

- The F22 Python/C++ synthetic suite contains **18 directed tests** of valid tetrahedral input, invalid hashes/files/indices/NaN records, orphan seams, changed controls, wrong arity and missing source. **18/18 PASS** on the local compiler-enabled workstation; the F21 30 original synthetic tests also passed.
- Real byte checks and the independent BP validator's JSON output were executed **separately** on the actual original source; these tests are **not** counted as another synthetically constructed benchmark.
- Raw ZIP/STL, private BP, private receipts with local paths and compiled binaries are intentionally **not** added to the research branch. Only scripts, tests, hash/count-only evidence and this report are versioned.

### Reproduction on an authorized workstation

Run from `docs/research/nonmanifold-benchmark/probes` in the **full checkout** (private source paths are examples):

```bash
python -m unittest -v test_thingi10k_f21_piecewise_linear_bezier test_thingi10k_f22_original_bp_audit
python thingi10k_f21_piecewise_linear_bezier.py \
  --source-zip /private/Thingi10K/293137.stl.zip \
  --private-output-bp /private/apmesh-f22/293137_piecewise_linear_candidate.bp \
  --private-receipt /private/apmesh-f22/293137_candidate_receipt.json
python thingi10k_f22_original_bp_audit.py \
  --source-zip /private/Thingi10K/293137.stl.zip \
  --candidate-bp /private/apmesh-f22/293137_piecewise_linear_candidate.bp \
  --receipt /private/apmesh-f22/f22_independent_original_bp_audit.json

g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  thingi10k_f22_independent_cpp_bp_probe.cpp -o /private/apmesh-f22/f22_cpp_probe
/private/apmesh-f22/f22_cpp_probe /private/apmesh-f22/293137_piecewise_linear_candidate.bp

# This step requires the original APMesh header from the repository checkout:
g++ -std=c++17 -O2 -I../../../../include \
  thingi10k_f22_native_header_integration.cpp -o /private/apmesh-f22/f22_original_header_probe
/private/apmesh-f22/f22_original_header_probe /private/apmesh-f22/293137_piecewise_linear_candidate.bp
```

Do **not** call the last command a full original `PatchReader::ReaderFilePatches` test: it calls **only the actual inline input-validator function** and not `Geometry::VerifyCurveGeometry`, `InsertPatch`, the AFT generator or the QUAD generator.

## State and next non-negotiable gates

- F22 original ZIP and STL byte integrity: **PASS**.
- F21 real original → private candidate BP generation and deterministic repetition: **PASS**.
- F22 independent Python and independently compiled C++ BP grammar/seams: **PASS**.
- Original production C++ input validator: **NOT RUN** (full checkout unavailable in local sandbox).
- Original `ReaderFilePatches` geometry construction and shared curve identities: **NOT RUN**.
- Actual APMesh accepted TRI output: **NOT RUN**.
- Actual APMesh supported QUAD mode: **NOT RUN**.
- Per-object license/derivative publication authority: **NOT CLEARED**.
- Comparable QuadWild input/output source pair: **NOT AVAILABLE FOR THIS BADIA CASE**.
- Main merge, new S40 source face/patch admission, scientific method comparison: **NONE**.

**F23:** run exact-head production native `input_validation.h` then actual `ReaderFilePatches` with a bounded 876-patch observer; inspect real shared curve identity, memory and runtime; only then attempt supported APMesh TRI with accepted-state evidence, while preserving the research PR Draft and production baselines.
