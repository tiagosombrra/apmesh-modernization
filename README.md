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

The CTest suite currently checks tooling controls and the archived Eistute
artifact. It does not yet establish accepted-state scientific regression or
full memory safety. Commands fail on empty test discovery. Doxygen, full lint,
sanitizer campaigns, C++23 migration and Eigen replacement remain planned work.

## Repository policy

All new first-party code and documentation are English. Historical names and
interfaces migrate in reviewed batches. Production serial code will ultimately
depend only on the C++ standard library; Eigen is still present in this import.
No paid Actions or hosted workflows are configured. Checks run locally and
compact evidence is retained in Git. Read AGENTS.md before making changes.

The original license, citation and third-party notices are retained. Historical
artifacts, failed runs and unmeasured coverage must remain distinguishable from
successful validation. Existing source and experimental repositories are separate.
