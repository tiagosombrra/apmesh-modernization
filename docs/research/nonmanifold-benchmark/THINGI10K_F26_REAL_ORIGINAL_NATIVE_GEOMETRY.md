# S40-F26 — Original APMesh `Geometry` execution on the private authentic #293137 BP

**Execution date:** 2026-11-23. **Research branch:** `research/benchmark-corpus-reverse-patches`. **PR:** #225 (**DRAFT**). **Status:** **original C++ Geometry and shared-curve identities actually executed on the real data-derived 876-patch model**; **TRI/QUAD meshing NOT run**, no scientific author-output/reference-pair admission and no asset-specific redistribution permission established.

## Scientific scope and original-input provenance

The selected Thingi10K **#293137 Bunny LowPoly** STL is a 292-triangle, genus-zero source (148 exact-coordinate vertices, 438 paired edges). The 7,073-byte original mirror ZIP is pinned to Git blob SHA-1 `359c26b16664e9ba8d2415ca065a85bd27504d5f`; the 14,684-byte uncompressed binary STL was previously SHA-256 verified as `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a`.

F21/F22 generated a **piecewise-planar, bilinear-to-bicubic degree-elevated domain** via three four-sided patches for every input triangle. The resulting private original-derived `.bp` is **538,482 bytes**, SHA-256 `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0`, with **7,886 indexed controls and 876 patches**. It preserves the piecewise-triangle surface up to documented numerical budgets; it does not recover author CAD, original Bézier freeform features or interpatch C1 continuity.

## Removing the full-checkout/network blocker without redistributing source geometry

The isolated local runtime has no GitHub DNS access. Instead, the **full source** was checked out within [GitHub Actions workflow F26](../../../.github/workflows/research-f26-private-native-replay-tool.yml) at commit `73e46748c294af0f390a907a11445645e279fc12`. It checked the original pinned CMake/reader/curve/geometry source Git blobs, configured an `ap_mesh_engine` CMake Release build without OpenMP/MPI/LTO, and linked the already-tested F25 C++ native-Geometry probe statically (`-static -static-libgcc -static-libstdc++`). The standalone executable proved against two *synthetic* fixtures in CI before uploading a **binary-only** ZIP. The workflow received no STL or derived original-model `.bp`.

- [Authoritative F26 build/run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45163373559) — **success**.
- GitHub Actions artifact ID **14812772005**, `apmesh-f26-static-native-geometry-offline-replay`; retention **1 day**. This transient artifact contains **only** the static original-engine-linked native probe, SHA256SUMS and provenance.txt, not original mesh assets.
- Verified local native probe binary: **ELF x86_64, statically linked**; SHA-256 **`6a83395ab509e698a28f7822441b265ee9640a7258096c0b1717aa05b02e6a63`**, identical to SHA256SUMS in the GitHub artifact.
- Original private BP was verified locally *before and after* execution, never transferred to the GitHub runner, and never copied into the repository or the public research package.

## Real native execution — two independently spawned processes

The exact C++ `PatchReader::ReaderFilePatches` was executed inside the linked original engine. The linked 
`Geometry` class and `CurveAdaptive`/`PatchBezier` types were verified using the original F25 C++ probe, including patch curve pointers, observer identity, source-matched four-control sequences, stored direction flags, and the total incidence partition. Memory and timing are measured from the original native process, not extrapolated from the Python preview or synthetic C++ tests.

| Observable | First process | Second process |
|---|---:|---:|
| Patches materialized | 876 | 876 |
| Distinct native curves | 1,752 | 1,752 |
| Shared native curves, exactly two patch observers each | 1,752 | 1,752 |
| Free/border curves | 0 | 0 |
| Nonmanifold curves (3+ observers) | 0 | 0 |
| Source-matched boundary-control sides | 3,504 | 3,504 |
| Boundary sides with reverse *storage* orientation | 0 | 0 |
| Independently parsed BP (ms) | 7.68450 | 7.66392 |
| **Original native Geometry load (ms)** | **286.062** | **288.406** |
| Native source-to-Geometry identity check (ms) | 1.23476 | 1.29310 |
| End-to-end subprocess wall (ms) | 299.667 | 302.671 |
| Linux process peak RSS (KiB) | 80,780 | 80,780 |

The zero count of reversed *stored* sides is not a claim that all adjacent face boundary traversals have identical orientation. The F25 native probe validates storage-versus-input side direction; the earlier F21/F22 global patch-topology audit separately verified opposite oriented **topological** incidences.

The measurements are point observations on the one private runtime and two process starts: **not performance distributions, algorithmic complexity proofs, or a fair external benchmark**.

## Tests and fail-closed conditions

- The GitHub Actions original-engine executable passed both synthetic native C++ fixtures in the build runner, with source hashes pinned; its full-source `Geometry` execution then passed the private **876-patch** candidate locally twice.
- The F26 private-replay Python harness supplies **20 hermetic regression/negative tests**, executed locally (**20/20 PASS**), covering source-data integrity prerequisites and rejection of unproven/out-of-scope native results.
- The private replay rejects incorrect BP or binary SHA-256, modified size/counts, missing/duplicate C++ JSON fields, nonfinite times, mismatched 876/1,752/3,504 invariants, incorrect curve incidence, nonzero exit, unexpected diagnostic text, different stored control orientations across runs, excessive resources and accidental report overwrite. The local private BP never enters normal source control or CI.

Reproduce on a **rights-authorized** Linux host, using an exact GitHub Actions F26 static binary artifact and the already verified privately generated F22 `.bp`:

```bash
python -m unittest -v test_thingi10k_f26_private_original_geometry
python thingi10k_f26_private_original_geometry.py \
  --native-executable /private/apmesh_f26_original_native_geometry_probe \
  --private-bp /private/293137_piecewise_linear_candidate.bp \
  --native-sha256 6a83395ab509e698a28f7822441b265ee9640a7258096c0b1717aa05b02e6a63 \
  --report /private/f26_original_native_evidence.json
```

Retain only hashes/counts/times in the versioned [machine-readable report](evidence/thingi10k/thingi10k_f26_real_original_native_geometry_receipt.json). Do not commit or distribute raw third-party ZIP/STL or the resulting original-model `.bp` without explicit rights clearance.

## Uncrossed scientific and software gates

1. **No TRI / QUAD generation:** the executed binary loads and inspects Geometry; it does not call the APMesh AFT/QUAD generator. No accepted mesh faces, output vertex coordinates, step logs, quality metrics or comparisons can be reported from this gate.
2. **Input non-equivalence:** original Thingi10K triangulated source is not a four-sided CAD patch domain. The 876-patch domain is an auxiliary reconstruction; comparisons against QuadWild require method-equivalent input and preprocessing declarations.
3. **Surface regularity:** C0-compatible seams and strictly positive sampled corner Jacobian from F21 are not a global proof of C1 smoothness, local nondegeneracy in the whole parameter square, inverse-parameterization convergence or successful APMesh triangulation.
4. **Permissions:** a public Git mirror does not confer individual asset rights; original Thingiverse author/upload identity and rights remain unverified. Only code and numerical summaries may be published under present research policy.
5. **S40 baseline:** do not modify original MAMBO CAD inputs, M5/S40/S27/M3, Book/Eistute/Decor Shelf, Tsh249 or previously accepted face/patch denominators. The candidate remains outside the scientifically admitted set.

**Next stage S40-F27:** compile a *bounded original APMesh generator executable* in a clean full-source runner and transfer only the executable. Execute locally with the private F22 model and a pinned sandbox configuration; inspect actual acceptance/rejection, resource budget, generated output/incidence and independent geometry/quality metrics, without altering production source or asserting success before an accepted actual result. For QUAD, examine supported mode independently after TRI.
