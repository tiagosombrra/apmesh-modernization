# APMesh Modernization

Private engineering modernization of the published adaptive non-manifold patch
meshing implementation. The scientific technique is preserved while ownership,
portability, architecture, duplication, English APIs and reproducibility improve.
Scientific extensions require separate proposals aligned with the advisors.

## Start here

- [Project state](docs/PROJECT_STATE.md): completed, active and next work.
- [Full modernization plan](docs/MODERNIZATION_PLAN.md): stages 0–11 and gates.
- [Source provenance](docs/PROVENANCE.md): exact published baseline and import.
- [Local quality commands](docs/QUALITY_AUTOMATION.md): formatting, lint and tests.
- [Stage 3 closure inventory](docs/architecture/STAGE3_CLOSURE_INVENTORY.md): finite remaining lifecycle obligations and required observations.
- [Initial audit](docs/audit/INITIAL_AUDIT.md): observed defects and limitations.
- [Published package README](docs/PUBLISHED_README.md): unchanged historical usage.

## Build and check locally

Use Python >=3.10, CMake >=3.21, Ninja and a C++17-capable compiler. Put the
intended toolchain on PATH. GCC/MinGW is qualified for this bootstrap; MSVC
still has historical variable-length-array blockers. See the evidence report.
The quality guide also gives an explicit Windows configuration equivalent to
the qualified local preset, without requiring ignored machine-specific files.

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial
python tools/quality.py doctor
```

The local suite includes required tooling, input, geometry, orientation,
report-semantics and lifecycle tests; integrated baseline counts are recorded
below and active qualification is recorded in PROJECT_STATE.md.
clang-tidy is required for its real header-scope controls;
LLVM 22.1.8 is the qualified version. Commands fail on empty discovery or missing
tools. Full memory safety, legacy lint cleanup, Doxygen, C++23 and Eigen removal
remain later work.

## Stage 1 completed

Strict Eistute/Book repetition and independent accepted-state/boundary validation
pass. Actual reversed curved/non-manifold generation and named CSV semantics
now pass their previously failing gates. Pointer-order smoothing, reversed
incidences, corner arcs and CSV labels are explicitly classified defect repairs.
Raw prior-version failures remain stored; strict minimally corrected reference
comparisons pass without relaxed tolerances. See
[the repair and regression evidence](docs/evidence/STAGE1_ORIENTATION_REPAIR.md).

PR #3 is integrated. Exact-head and post-merge validation pass; see
[the closure record](docs/evidence/STAGE1_CLOSURE.md). Stage 2's mesh/architecture
inventory follows the same regression gates.

## Stage 2 architecture inventory completed

[The source-backed architecture map](docs/architecture/MESH_ARCHITECTURE.md)
covers every production C++ header/unit, domain/identity conversions and lifecycle
contracts. [The follow-up sequence](docs/architecture/REFACTOR_SEQUENCE.md) keeps
physical/UV meshes distinct and prioritizes qualified ownership work before
consolidation. The candidate adds development tooling and eight controls;
production sources and scientific outputs remain exact. PR #6 is integrated,
and exact-head/post-merge checks pass. See [the closure record](docs/evidence/STAGE2_CLOSURE.md).
Stage 3 remains open with thirty-three qualified ownership/lifecycle slices.
The latest owns serial parsed-control results and pending parse/reconstructed
patches and propagates resource failures before consuming partial rows (PR #89).
Exact implementation head/main gates pass: 47/47 CTest, 74 Python controls,
29 memory batteries/3005 expected outcomes, 1040 retained scalar sequences and
exact twice-repeated Eistute/Book accepted/rejected traces on the same 603 inputs.
The new 131 outcomes cover sixteen complete sweeps/2731 actual denials and eight
GCC/sixteen MSVC live pairs; original 72 failed outcomes and partial sweeps remain
retained. See [the bounded closure audit](docs/evidence/STAGE3_SERIAL_READER.md).
The Model audit reproduces original copy/rvalue ownership aliases and failed-append
retention; see [the evidence](docs/evidence/STAGE3_MODEL_ROOT_AUDIT.md).
The next single repair is slice 34, Model mesh adoption and copy/move intent.
Other loaders, cache/metadata/acceptance rollback and full-process/parallel memory
remain open; stages 4-11 are pending.

## Repository policy

All new first-party code and documentation are English. Historical names and
interfaces migrate in reviewed batches. Production serial code will ultimately
depend only on the C++ standard library; Eigen is still present in this import.
No paid Actions or hosted workflows are configured. Checks run locally and
compact evidence is retained in Git. Read AGENTS.md before making changes.

The original license, citation and third-party notices are retained. Historical
artifacts, failed runs and unmeasured coverage must remain distinguishable from
successful validation. Existing source and experimental repositories are separate.
