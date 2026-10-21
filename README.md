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
Stage 3 remains open with thirty-two qualified ownership/lifecycle slices.
The latest retires completed Bezier observers and preserves dependent Geometry
teardown/move order (PR #86). Exact-head and completed post-merge qualification
retain CTest 45/45, 74 Python controls, 28 memory batteries/2874 expected outcomes,
1040 scalar sequences and exact repeated Eistute/Book accepted/rejected traces on
the same 598 protected inputs. A terminal main API timeout is retained; a separate
explicit continuation completes the remote audit without repeating local tests.
See [the bounded closure audit](docs/evidence/STAGE3_BEZIER_OBSERVERS.md).
The next single audit covers successful caller adoption and remaining loader/
Model/copy roots. Other lifecycle roots, cache/metadata/acceptance rollback and
full-process/parallel memory remain open; stages 4-11 are pending.

## Repository policy

All new first-party code and documentation are English. Historical names and
interfaces migrate in reviewed batches. Production serial code will ultimately
depend only on the C++ standard library; Eigen is still present in this import.
No paid Actions or hosted workflows are configured. Checks run locally and
compact evidence is retained in Git. Read AGENTS.md before making changes.

The original license, citation and third-party notices are retained. Historical
artifacts, failed runs and unmeasured coverage must remain distinguishable from
successful validation. Existing source and experimental repositories are separate.
