# Stage 0 bootstrap validation

Date: 2026-10-16 UTC / 2026-10-15 America/Fortaleza.
Baseline import: `cbfb863fb014e798289d824e158f67922036a5e3`.

## Changes and exact scope

The remote import has the exact publication tree
`1b7618d5a04e4d8d8a82a252f85b58757437408b`, all 513 blobs included.
Local compilation uses the earlier 511-blob text/source copy. The omitted local
PDF/PNG are preserved by their original remote tree entries.
All original src/, include/, libs/, configs/, input_models/ and reference/ files
remain byte-identical. Existing files changed only: README.md, .gitignore and
CMakeLists.txt (the latter appends CTest tooling registration). No repair from
the earlier six-file candidate patch is applied.

Validation input hashes are recorded in validation_inputs.json. Recompute and
compare them against the reviewed revision before relying on these results.

## Toolchain

- Windows native x64; MSYS2 UCRT64 GCC 16.1.0.
- CMake/CTest 4.4.0; Ninja 1.13.2.
- Python 3.14.6; clang-format and clang-tidy LLVM 22.1.8.
- Release; C++17 retained; MPI, OpenMP and LTO OFF.
- Doxygen unavailable in this environment.

## Executed results

| Check | Outcome | Limit |
|---|---|---|
| cmake --preset local-serial | PASS | GCC qualification only |
| cmake --build --preset local-serial --parallel 2 | PASS | 285 historical compiler warning diagnostics remain |
| Python unittest discovery | PASS: 18 tests | Tooling/compatibility controls, not application ownership |
| ctest --preset local-serial | PASS: 2/2 | One suite of 18 controls plus one archived-artifact check |
| Archived Eistute reference | PASS: 7,184 triangles | Does not assert that regenerated stage 4 is accepted |
| Real formatter controls | PASS: 5 expected outcomes | Bad format fails without writes, explicit fix passes, empty/outside selection fails |
| clang-tidy on src/data/mesh/sub_mesh.cpp | PASS: one TU | Does not establish full-project analyzer coverage |
| clang-format on unchanged sub_mesh.cpp | FAIL, preserved as legacy debt | The formatter is working; no global reformat applied |
| Real Book compatibility report with compared_groups=0 | FAIL as required | Measures missing coverage, not mesh incompatibility |
| Doxygen command | BLOCKED: missing tool, nonzero exit | No generated-page or API completeness claim |

The first tooling run failed on sandbox-provided temporary-directory access.
Tests were corrected to use owned temporary directories inside the workspace;
all 18 controls and CTest passed afterward. No assertions were relaxed.
Optional hook tests cover spaces in filenames and partially staged content:
clean working-tree bytes cannot conceal dirty index bytes, and unstaged debt
cannot invalidate a clean staged version.

## Remote checks and publication policy

At the pre-publication audit, main had only initialization commit
`b6dc4a010ba9d7ec7d1002fc15664a7deaac86b0`, with no concurrent PRs or Actions
runs. Branch-protection inspection returned 403 for the integration; rulesets
returned 403 requiring GitHub Pro or public visibility. No claim of server-side
enforcement is made. No hosted workflow or paid Action was created.
GitHub reports a combined status of pending with zero statuses when no checks
are installed; this must not be represented as green remote CI.
This bootstrap uses explicit local checks for its limited scope and is reviewed
through a PR. Later scientific/memory deliveries need their own stronger gates.

## Remaining qualification

Application generation with accepted-state comparison, invalid-input repairs,
full sanitizer campaign, MSVC/Clang portability, full-project lint, English API
migration, Eigen removal, CRABMesh unification, Doxygen rendering and performance
qualification are open stages. No full application leak-free claim is made.
