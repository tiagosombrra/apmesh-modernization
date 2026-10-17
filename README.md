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
- [Initial audit](docs/audit/INITIAL_AUDIT.md): observed defects and limitations.
- [Published package README](docs/PUBLISHED_README.md): unchanged historical usage.

## Build and check locally

Use Python >=3.10, CMake >=3.21, Ninja and a C++17-capable compiler. Put the
intended toolchain on PATH. GCC/MinGW is qualified for this bootstrap; MSVC
still has historical variable-length-array blockers. See the evidence report.

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial
python tools/quality.py doctor
```

The local suite has nine required tooling, input, geometry, orientation and
report-semantics tests. clang-tidy is required for its real header-scope controls;
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
Stage 3 is in progress with five qualified ownership/lifecycle slices.
The latest guards root and midpoint construction across 3,470 injected
allocation failures. CTest 15/15, UV 56/56, node 7/7 and strict Eistute/Book
regressions pass before and after integration. See
[the latest closure](docs/evidence/STAGE3_UV_TREE_CLOSURE.md).
Full-application memory and parallel qualification remain open.

## Repository policy

All new first-party code and documentation are English. Historical names and
interfaces migrate in reviewed batches. Production serial code will ultimately
depend only on the C++ standard library; Eigen is still present in this import.
No paid Actions or hosted workflows are configured. Checks run locally and
compact evidence is retained in Git. Read AGENTS.md before making changes.

The original license, citation and third-party notices are retained. Historical
artifacts, failed runs and unmeasured coverage must remain distinguishable from
successful validation. Existing source and experimental repositories are separate.
