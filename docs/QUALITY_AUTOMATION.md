# Local quality automation

## Purpose and current limits

These commands automate repeatable checks; they do not certify the full
application. The integrated bootstrap registers tooling controls and an archived-artifact
check. Application ownership, accepted-state generation and sanitizer qualification
remain open. The legacy warnings/style debt is not declared resolved.

The stage 1 draft also registers real executable invalid-input controls and
positive shipped-model grammar controls. Its independent generation verifier
has negative controls for rejected targets, invalid geometry, altered counts,
missing evidence, absent incidence coverage and numerical report drift.
The prior numerical reduction-order repair passes exact Eistute/Book repetition.
The incidence follow-up checks every sheet against source controls and actual
triangles. Full CTest now contains seven tests: five pass and two required gates
fail (`application.boundary_orientation`, `application.metric_schema`). The
failures expose pre-existing reversed geometry and CSV label/value defects;
they are not skipped or marked expected failures. 65 Python controls pass.
Selected exporter clang-tidy fails on 18 inherited header/Eigen diagnostics;
the checks were not weakened. Keep the draft unmerged. See
`evidence/STAGE1_INCIDENCE_AUDIT.md` for commands, evidence and next repairs.


Requirements: Python >=3.10, Git, CMake >=3.21 and Ninja for presets. The imported
code still targets C++17. GCC/Clang/MSVC qualification and C++23 migration are
stage 4. LLVM format/tidy and Doxygen are development tools, not runtime libs.
Record actual versions in each validation report; formatter-version changes
require a separate reviewed formatting change.

```sh
python tools/quality.py doctor
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial
python tools/quality.py test
```

Use a terminal with the intended compiler, Ninja and LLVM tools on PATH.
On Windows, an MSYS2 UCRT64 GCC terminal is one qualified bootstrap path; do
not silently switch compilers in an existing build directory.

## Whitespace and formatting

EditorConfig defines spaces, UTF-8 and LF, with batch-file line endings handled
by editors. The whitespace command is for selected supported first-party text
files. It preserves Markdown hard breaks, rejects binary content and normalizes
selected text to LF. Do not select historical batch files for that operation.

```sh
python tools/quality.py whitespace tools/quality.py docs/PROJECT_STATE.md
python tools/quality.py whitespace --fix tools/quality.py
python tools/quality.py format src/data/mesh/sub_mesh.cpp
python tools/quality.py format --fix src/data/mesh/sub_mesh.cpp
python tools/quality.py format --base main
```

Without --fix, files are never rewritten. Explicit missing/outside/vendor inputs,
empty selections, missing tools and command failures fail the check. Changed
selection covers tracked working-tree differences against --base; untracked
files must be selected explicitly or staged. The hook checks INDEX bytes so
unstaged fixes cannot conceal a bad staged version.

clang-format uses a repository file, preserves include order and avoids comment
reflow to reduce the initial diff. Adoption is batch-wise; the whole historical
tree is not reformatted during bootstrap.

## Static analysis

```sh
python tools/quality.py tidy src/data/mesh/sub_mesh.cpp --build build/local-serial
```

Select compiled translation units. Headers are analyzed through consumers.
The command requires a nonempty first-party compilation database and applies
clang-analyzer, selected bugprone, modernize and performance checks. Diagnostics
fail the selected scope. No --fix mode exists for tidy; ownership, overrides,
renames, noexcept, const and container changes require reviewed evidence.
Do not use automatic global fixes or add NOLINT merely to silence findings.

The vendor header exclusion also applies to lexical include/../../libs paths
that otherwise match the first-party header filter. Checks and warnings-as-errors
remain unchanged. Required CTest tooling.tidy_header_scope invokes the actual
analyzer with a vendor positive control and first-party header/source negative
controls. Missing clang-tidy or lost first-party diagnostics fails the test.
LLVM 22.1.8 is qualified; other versions must support ExcludeHeaderFilterRegex.
Selected exporter lint coverage is not a full legacy lint-clean claim.


## Architecture inventory freshness

```sh
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

The deterministic lexical inventory covers every first-party production C++
file and hashes the CMake inputs. Eight positive/negative controls, including
retained-inventory freshness, run through normal tooling CTest. The source
anchor checker establishes traceability only; ownership conclusions require
human code review and dynamic safety requires qualified instruments. Conditional
includes are potential dependencies, not active-preprocessor or runtime proof.
Regenerate explicitly without --check only after reviewing actual source changes.

## Optional local pre-commit hook

```sh
git config core.hooksPath .githooks
```

The opt-in hook checks supported staged first-party text and clang-format for
staged C++. It never modifies files, installs packages or calls a network service.
It is a fast guard, not a substitute for build, tests or scientific regression.

## Architecture and numerical rules

Prefer RAII, explicit ownership, const-correct interfaces, value types and narrow
responsibilities. Use unique_ptr for exclusive dynamic ownership and borrowed
references/pointers for observers with documented lifetime. Avoid speculative
shared_ptr, global mutable configuration, unchecked indexing, C-style casts,
VLAs and duplicated formulas with different undocumented conventions.

Do not infer topological identity from floating-point proximity. Do not change
tolerances, accumulation order, solver policy or enable fast-math under the label
of formatting. Benchmark only after clock qualification and compare equivalent
accepted results. A lint pass does not validate numerical stability or topology.

## Memory and documentation

After portability repairs, qualify GCC/Clang ASan+UBSan, Linux LSan and platform
equivalents, including negative controls and repeated rejection/rebuild paths.
Windows ASan alone does not establish Linux leak coverage. Never claim memory
safety beyond the cases and instruments run.

Stage 3 adds a standalone physical node/submesh/triangle target under
`tests/memory`, also registered in normal CTest as application.node_lifetime.
MSVC ASan and separate Debug CRT builds are qualified by
`tools/qualify_node_lifetime.py`, including deliberately invalid controls. The
runner rejects absent diagnostics and nonzero valid-case exits. Commands and
scope limits: [node lifetime evidence](evidence/STAGE3_NODE_LIFETIME.md).

```sh
python tools/quality.py docs
```

Doxygen is configured to report undocumented APIs and fail on warnings. Full
documentation generation is pending until a Doxygen-equipped environment and
API coverage are available; a config file is not generated documentation.

## Primary references reviewed 2026-10-15

- https://clang.llvm.org/docs/ClangFormatStyleOptions.html — repository style file.
- https://clang.llvm.org/extra/clang-tidy/ — compilation database and diagnostics.
- https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines — RAII, ownership,
  resource safety, interfaces and separation of responsibilities.
- https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html — shared presets.
- https://cmake.org/cmake/help/latest/manual/ctest.1.html — test discovery/execution.
- https://clang.llvm.org/docs/AddressSanitizer.html — instrumentation and limits.
- https://www.doxygen.nl/manual/config.html — API extraction and warning controls.

These are engineering references, not a proof that legacy code follows them.
