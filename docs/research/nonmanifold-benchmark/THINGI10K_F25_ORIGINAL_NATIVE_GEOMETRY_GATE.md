# S40-F25 — Original APMesh `ReaderFilePatches`/`Geometry` native integration gate

**Date:** 2026-11-23. **Scope:** research-only, PR #225 (`research/benchmark-corpus-reverse-patches`), not a production modification or scientific benchmark admission.

## What is now implemented

- `probes/thingi10k_f25_native_geometry_probe.cpp` links against the repository's **actual** `ap_mesh_engine` C++17 static library. It calls `PatchReader::ReaderFilePatches` with a `.bp` file and inspects the resulting `Geometry`, `PatchCoons`/`PatchBezier` and `CurveAdaptive` instances through the original public methods.
- It checks every patch contains precisely four non-null curve references, that all stored curves appear in patches, that each curve's actual patch-observer list is a bijection with its patch incidences, and that expected boundary/shared curve counts and `4*patches` incidence totals match. Any unexpected non-manifold or orphan curve, foreign observer, duplicate curve use in one patch or incomplete output **fails closed**.
- It records load time, observer-inspection time and **Linux** process peak RSS (`getrusage(RUSAGE_SELF).ru_maxrss`, KiB) without logging control coordinates. It does **not** invoke the TRI/QUAD mesher.
- `probes/thingi10k_f25_native_geometry_runner.py` runs the original CMake `ap_mesh_engine` target with MPI, OpenMP and LTO explicitly disabled for one bounded serial comparison. Original CMake and seven relevant C++ implementation files are pinned to their Git object SHA-1 from the audited research branch. Both a standalone 1-patch and an adjacent 2-patch synthetic `.bp` case are generated without third-party data. Each is run twice in a fresh process, with timeout, virtual-memory and CPU caps. Only exact machine-checked JSON results can qualify.
- Optional **private** mode accepts an existing original-source-derived BP only when its exact F22 SHA-256 matches `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0` (538,482 bytes, 7,886 controls, 876 patches). The required native result is **876 patches / 1,752 shared curves / zero boundary curves**, twice. This input is **never committed or sent to CI**.
- `probes/test_thingi10k_f25_native_geometry_runner.py` contains 30 local **Python contract tests**. A passing Python test is **not** a production C++ pass.

## Native executable build and run (when a full checkout is available)

From the full `apmesh-modernization` source root:

```bash
python3 -m unittest -v \
  docs/research/nonmanifold-benchmark/probes/test_thingi10k_f25_native_geometry_runner.py

python3 docs/research/nonmanifold-benchmark/probes/thingi10k_f25_native_geometry_runner.py \
  --root . \
  --receipt /tmp/apmesh-f25-synthetic.json
```

For the already-generated **private** #293137 candidate, add this flag to the second command (do not commit the file or the resulting derivative):

```bash
  --private-bp /private/path/293137_piecewise_linear_candidate.bp
```

Outputs are numeric hashes/counts/time/RSS only; there are no geometry coordinates or source mesh bytes in the reporter output. The result is only positive when the original linked `ReaderFilePatches` and real `Geometry` actually ran, returned expected counts, and passed observer checks. The first synthetic fixture expects `(patches=1, curves=4, boundary=4, shared=0)`; the second `(patches=2, curves=7, boundary=6, shared=1)`; private #293137 expects `(876,1752,0,1752)`.

## CI boundary

An isolated Ubuntu GitHub Actions workflow `research-f25-native-geometry-smoke.yml` attempts the **original engine** on **only the two synthetic fixtures**, without accessing third-party assets or private BP. A passing workflow proves the original loader and Geometry on those synthetic fixtures. It does **not** prove the real #293137 path. Check the actual workflow job and logs before marking this gate passed; adding the YAML file is not evidence of its execution.

## Current permissions and scientific scope

The original Thingi10K #293137 STL asset's per-object redistribution/derivation permissions have not been independently cleared. Previous stages verified and privately generated the source-derived BP, but this stage does not publish or transmit it. The F25 native integration is **not** an original B-Rep CAD reconstruction, a matching input to QuadWild, a topology preserving smoothing claim, or a completed TRI/QUAD benchmark.

### Known limits and risks

- The repository cannot currently be cloned from this isolated runtime because DNS lookup of github.com fails. An incomplete checkout cannot be substituted for `ap_mesh_engine`.
- `ReaderFilePatches` performs linear control interning and `Geometry::VerifyCurveGeometry` performs linear sequential curve matching. F24 estimated 51,714,078 linear ID comparisons and approximately 3,069,504 curve-candidate inspections on #293137, but those are static operation counts, **not measured time**.
- If full native tests expose a performance or curve-observer defect, capture an exact failing trace and propose a separate targeted fix; do **not** silently change the APMesh production code or original patch data to satisfy this research gate.
- No original model, STL/ZIP, third-party material, private BP, native generated mesh or existing S40 benchmark is changed. PR #225 remains Draft; `main` is not modified, and no tag/release is created.

## Next stage

Run the native private BP gate in an authorized **full original checkout**, check actual curve identity and peak RSS, then attempt a separate accepted TRI run through the **actual** APMesh generator with independently captured mesh, quality and patch/curve incidence; only then investigate supported QUAD modes and fair-reference comparability.
