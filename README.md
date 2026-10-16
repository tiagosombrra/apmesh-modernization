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

The initial integrated CTest suite checks tooling controls and the archived Eistute
artifact. It does not yet establish accepted-state scientific regression or
full memory safety. Commands fail on empty test discovery. Doxygen, full lint,
sanitizer campaigns, C++23 migration and Eigen replacement remain planned work.

## Stage 1 candidate (not integrated)

This draft additionally checks real invalid CLI/model/configuration inputs and
the three valid shipped model grammars. The independent generation checker
selects the last accepted state, cross-checks candidate OBJ/CSV/log evidence and
recomputes exported geometry. It does not substitute a rejected target artifact
for an accepted result.

```sh
python tools/verify_generation.py build/candidate/eistute --baseline build/baseline/eistute --report comparison.json
python tools/repeat_generation.py --exe build/baseline/bin/ap_mesh --model eistute --output build/repeat-eistute --report repeat.json
```

The Eistute repeatability defect was traced to pointer-ordered Laplacian sums.
The draft now orders those sums by unique logical edge ID. Strict repetitions
and controlled reference comparisons pass for Eistute and Book without relaxing
tolerances. This is an explicit behavior-changing defect repair; the original
reference's numerical differences remain recorded. See
[the follow-up evidence](docs/evidence/STAGE1_SMOOTHING_ORDER.md).
Per-incidence export/checking now passes for all nine Eistute/Book attempted
states. The closure audit exposed two pre-existing defects: actual reversed
incidences generate degenerate geometry, and CSV control fields are mislabelled.
Both are required failing CTests; current CTest status is 5/7, with no skips.
Keep the delivery draft. See [the incidence audit](docs/evidence/STAGE1_INCIDENCE_AUDIT.md).

## Repository policy

All new first-party code and documentation are English. Historical names and
interfaces migrate in reviewed batches. Production serial code will ultimately
depend only on the C++ standard library; Eigen is still present in this import.
No paid Actions or hosted workflows are configured. Checks run locally and
compact evidence is retained in Git. Read AGENTS.md before making changes.

The original license, citation and third-party notices are retained. Historical
artifacts, failed runs and unmeasured coverage must remain distinguishable from
successful validation. Existing source and experimental repositories are separate.
