# First complete serial MSVC/ASan observation

Observed main: `c44f1860916ac10f914a3a179354535b4dc55ce6` (PR #135), tree
`a2dc3d3b79d446ed84c416a94070ee61938943c3`.
Classification: engineering-only bounded instrument/application observation.
Production, formulas/order, inputs, fixtures and scientific policies are unchanged.
The [compact evidence](stage3/serial_asan_sp02/summary.json) records exact commands,
source/control/runtime identities and results. This is the first P3 checkpoint,
not complete W-ASAN inventory qualification or Stage 3 closure.

## Full target and instrument

The existing complete ap_mesh target compiled with MSVC 14.44.35207 x64, C++17,
RelWithDebInfo and /fsanitize=address. MPI/OpenMP/LTO and BUILD_TESTING were off.
All 73 original production translation units are present. Actual MSBuild command
tracking records 73 compilation groups, each with the ASan flag; no native unit
is excluded or replaced with an extracted helper. The linker reports LNK4300,
disabling incremental linking for ASan metadata; the full build returns zero.

```powershell
cmake -S . -B build/p3-msvc-asan-sp02/application -G "Visual Studio 17 2022" -A x64 -DCMAKE_CXX_STANDARD=17 -DBUILD_TESTING=OFF -DAP_MESH_USE_MPI=OFF -DAP_MESH_USE_OPENMP=OFF -DAP_MESH_ENABLE_LTO=OFF -DCMAKE_CXX_FLAGS=/fsanitize=address
cmake --build build/p3-msvc-asan-sp02/application --target ap_mesh --config RelWithDebInfo --parallel 2
```

Artifact: `build/p3-msvc-asan-sp02/application/bin/RelWithDebInfo/ap_mesh.exe`.
SHA-256: `cc1b16974c5ecf334afe61f3a4aba144a7faab09544b4d3696facdbda49c827a`.
This is a separate profile with iterator level 0; P1's checked Debug executable
and its iterator level 2 remain unchanged. No Debug check is disabled to obtain
this observation. Compiler/runtime default files, including the existing default
ignore list, are identified; no new suppression or tolerance is introduced.

Both the application and standalone controls import the qualified toolchain's
clang_rt.asan_dynamic-x86_64.dll. Its directory is first on the recorded child
PATH; ASAN_OPTIONS is halt_on_error=1. Exact DLL/tool hashes are in the summary.

Two controls compiled with the same toolchain, configuration, standard, runtime
and ASan flag. The valid control observes unpoisoned live storage, reads the
expected value, deletes its array, observes poisoned retired storage and exits
zero with its completion marker. The deliberately invalid control performs the
same deletion and then an actual read in a separately compiled ReadCell function.
It exits 1 with heap-use-after-free, including allocation, free and read stacks.
That expected invalid result demonstrates detection; it is not application failure.

The exact compiled control sources are retained as source snapshots in the JSON
evidence and local controls directory. They can be restored into a standalone
CMake source directory and built with the recorded configure/build commands.
No production CLI mode, central CTest target or scientific fixture is added.

## One natural SP-02 execution

The existing boundary_orientation_case.run_control is called once with name
aligned, reverse=false, sheets=2 and all remaining defaults. It produces the
same existing input hash as P1/P2. Its real child command is ap_mesh --config
followed by the newly owned aligned/article.conf path. Native numerical selection
and policies run without failure or acceptance injection. No alternative cases,
fixture changes, retries or parameter searches are executed.

The process returns zero. Independent physical/parametric metrics, analytic
mapping and boundary verification pass: initial accepted step 0, two patches,
eight triangles, seven curve groups and one positive shared-boundary incidence
comparison. Max curve error and shared gap are zero in this case. Stderr is empty
and no ASan diagnostic is observed through the actual process/owner teardown.

There is no rejected step or adaptive retry in this initial-only witness. One
clean ASan execution does not prove absence of leaks, arbitrary ownership safety,
same-process reuse, full adaptive history/rollback or the other SP cases. CRT,
LSan/UBSan, terminal observer portability and parallel qualification remain open.
The three bounded/seven partial-open closure dispositions do not change.

## Delivery and next bounded execution

Preserve the one native observation at its actual revision. Documentation delivery
requires unchanged non-documentation source/input bytes, exact application/control/
runtime/report identities, replayed compilation groups and positive comparison
counts, P1/P2 seals, whitespace/inventory/contracts and staged/remote checks.
Run the existing 74 CTest entries with zero failures/skips and 380 nested Python
controls on exact documentation head and main. Reuse this ASan evidence by identity;
do not rerun SP-02 or rebuild the unchanged instrumented target for documentation.
No large scientific or instrument campaign is part of this delivery regression.

Local build/p3-msvc-asan-sp02 retains logs, actual compiler commands, binaries,
PDBs, source snapshots, controls, the single process and all independent outputs.
The delivery PR/local seal bind documentation revisions to this measured source.

Next: continue P3's fixed production inventory, SP-01 and SP-03..08, with the
qualified unchanged ASan artifact. Stop expansion at the first unexpected failure,
retain/classify it and repair a demonstrated supported defect in a bounded item.
SP-09/10 still require full-caller observer portability before MSVC measurement.
Stage 3 and the complete P3 instrument inventory remain open.
