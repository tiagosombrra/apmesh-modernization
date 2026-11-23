# S40-F23 — Exact original APMesh C++ validator on the real #293137 BP

**Date:** 2026-11-23. **Research branch:** `research/benchmark-corpus-reverse-patches`, Draft PR #225. **Disposition:** original production **BP input grammar accepted**; full Geometry/curve/AFT TRI/QUAD generation **not executed**. No production or original CAD model source was changed.

## Frozen input and code provenance

The private BP candidate generated in F22 from the previously authenticated original Thingi10K #293137 ZIP was independently rehashed before execution:

| Evidence | Frozen value |
|---|---|
| Original mirror ZIP Git blob SHA-1, F22 | `359c26b16664e9ba8d2415ca065a85bd27504d5f` |
| Original STL SHA-256, independently recomputed in F22 | `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a` |
| Actual F22 private candidate BP | **538,482 bytes**, **7,886 indexed controls**, **876 bicubic patch records** |
| Actual private candidate BP SHA-256, checked in F23 | `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0` |
| Original APMesh `include/input_output/input_validation.h` Git blob SHA-1 | `bc7988e862383f2f264f9d3a2a7691fe5c028592` (7,679 bytes) |
| Existing F22 native C++ wrapper Git blob SHA-1 | `b8bb3be6d1d28a3500a05c620c0be4bfef6b0989` (588 bytes) |

**Important:** The complete original checkout could not be cloned into this isolated container: its direct network path to GitHub has DNS resolution disabled, while the repository connector can securely supply individual UTF-8 source files but not a repository archive. Instead, the exact **original inline production header**, independently validated against its Git blob SHA-1, was placed alongside the existing F22 wrapper in a restricted partial source tree. The build executed this exact-header original `apmesh::io::ValidateBezierPatchInput`, not a rewritten lookalike validator. `src/input_output/control_patch_reader.cpp` and `src/input_output/patch_reader.cpp` were inspected through the connected GitHub source but **not** compiled/linked in F23.

## Actual native observations

- Compiler: GCC 14.2.0, C++17, `-O2 -Wall -Wextra -pedantic`, on Linux x86_64.
- The pinned production header compiled without a code modification or diagnostic failure.
- The actual 538,482-byte private BP was accepted by the original C++ header on **three distinct native process executions**, each with exit code 0 and the exact stdout `apmesh-original-bp-header-validation-pass`.
- Observed per-run Python-subprocess wall-clock: **0.016085 / 0.014777 / 0.014101 seconds**. These measure only the short-lived validation process, **not mesh generation or native loader throughput**. Each run had a 6-second timeout and a 256 MiB virtual-address-space cap.
- Separate GCC C++17 `-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer` executable accepted the original candidate input under LeakSanitizer/ASan/UBSan environment settings. This sanitizer result covers the **header-only input-validator path**, not the full mesher.
- **32/32 hermetic native integration tests PASS** on the original header, covering positive grammar controls and missing/empty input, malformed records, nonfinite coordinates, invalid/overflow indices, unexpected tails and strict Git-blob/handoff identity. The positive degenerate-geometry grammar test is intentionally accepted; this demonstrates why the **input grammar validator cannot certify geometry**.

## New durable artifacts

- `probes/thingi10k_f23_original_native_input_gate.py`: reproducible, pinned-header/wrapper and pinned-private-BP native C++17 compile/execute tool. It verifies SHA-256 and sizes, compiles from the real repository headers, caps validation execution time/address space, repeats executions and writes a new receipt without overwriting existing data. **POSIX/Linux research harness**; this is not a Windows/MSVC portability claim.
- `probes/test_thingi10k_f23_native_input_gate.py`: 32 tests that compile and execute the **original** F22 C++ wrapper against the pinned original header; require the full checkout for default paths or `APMESH_F23_REPO_ROOT` for an exact-header partial staging tree.
- `evidence/thingi10k/thingi10k_f23_original_native_input_receipt.json`: count-/hash-/execution-only evidence without source STL, private derived BP, or file locations. The receipt must not be presented as a complete engine observation.

Reproduce from the full research checkout, inside `docs/research/nonmanifold-benchmark/probes`, using a separately obtained **rights-authorized private** BP candidate with the pinned SHA-256:

```bash
python -m unittest -v test_thingi10k_f23_native_input_gate
python thingi10k_f23_original_native_input_gate.py \
  --repo-root /path/to/apmesh-modernization \
  --private-bp /private/293137_piecewise_linear_candidate.bp \
  --output /private/thingi10k_f23_native_receipt.json
```

The script rejects changed input/source hashes, missing records and attempts to overwrite a prior receipt. It does **not** bypass the independent F22 geometric/seam check; keep both results when qualifying the same private BP candidate.

## Gate matrix and next stage

| Gate | F23 result |
|---|---|
| F21 original source topology and conservative subdivision | Previous PASS; not reinterpreted |
| F22 private BP generation and independent geometry/seam audit | Previous PASS, pinned by hash |
| **Original production C++ `ValidateBezierPatchInput` on real BP** | **PASS, 3/3 native runs** |
| Native header sanitizer run | **PASS, header path only** |
| Original `ReaderFilePatches` and Geometry construction | **NOT RUN** |
| Real native shared curve identity, orientation and memory observations | **NOT RUN** |
| Accepted APMesh AFT TRI and supported QUAD output | **NOT RUN** |
| Authorized per-model source/derivative redistribution | **NOT CLEARED** |
| QuadWild paper pair matched to this Badia source | **NOT APPLICABLE/NOT ESTABLISHED** |
| Scientific benchmark / S40 baseline admission | **ZERO** |

**F24 next:** once the complete checkout is available in a compiler-enabled workspace with private BP access, construct a *bounded* engine-linked `ReaderFilePatches` probe and capture the **actual** `Geometry::GetNumberPatches`, `Geometry::GetNumberCurves`, exact curve incidence identities, orientation and maximum resident memory under timeout. Independently validate any accepted mesh, if one is produced. Do not infer the curve count or claim full source conversion from the mathematical 1,752 patch edges. Preserve original `M5/S40/S27/M3`, Book/Eistute/Decor Shelf/Tsh249 and all frozen stage baselines. Keep the PR Draft; no merge or release.
