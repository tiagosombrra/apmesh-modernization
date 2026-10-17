# Local quality automation

## Purpose and current limits

These commands automate repeatable checks; they do not certify the full
application. Stages 1 and 2 are integrated and closed for their measured scope.
Stage 3 slices 1-7 are integrated with qualified node and UV targets.
The integrated CTest passes 17/17 with zero skips and 74 Python controls,
including real invalid inputs, orientation, metric schema, independent verifier
negative controls, architecture freshness and actual analyzer scope controls.
Exact Eistute/Book repetition and shared-incidence regression pass. Earlier
orientation/schema/lint failures are repaired and retained as historical
evidence in `evidence/STAGE1_CLOSURE.md`. They are not current failing gates.
Selected lint scopes pass unchanged diagnostic rules; legacy warning/style debt,
full-application memory qualification and broad portability remain open.


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

Slice 2 adds `tests/uv_memory` and required CTest application.uv_lifetime,
compiling 14 actual production units. `tools/qualify_uv_lifetime.py` requires
the original 26 ASan/Debug CRT cases, including invalid access/leak controls,
pending-template cleanup, ordered ownership transfer, midpoint aliases and
allocation-denied teardown/transfer preparation. The same runner fails the
pinned original. The bounded results do not qualify arbitrary allocation failure,
every template pattern or the full application. Commands and exact-head closure
requirements: [UV lifetime evidence](evidence/STAGE3_UV_LIFETIME.md).

Slice 3 extends the same runner to 35 cases and adds required CTest
application.uv_primitive_contracts (12 total CTest entries). It measures every
observed allocation ordinal in Edge construction, both Face constructors,
default front construction and Edge/Face setVertices. Failed replacement must
preserve endpoints, cache identity/geometry and scalar state. Endpoint-alias
replacement and normal geometry are separate ASan/CRT controls. The pinned
original fails; candidate, exact-head and implementation-main results are recorded in
[primitive allocation evidence](evidence/STAGE3_UV_ALLOCATION.md). This bounded
scope leaves template/Boundary registration, other setters and full-application
allocation failure qualification open.

```sh
python tools/quality.py docs
```

Doxygen is configured to report undocumented APIs and fail on warnings. Doxygen 1.18.0 is installed, but the initial documentation gate fails on
undocumented members. Complete API coverage and generated-page review remain
stage 8; a config file or installed tool is not generated-documentation validation.

## Pending registration qualification

Slice 4 extends the same runner to 49 cases and normal CTest to 14 entries.
Eight new sweeps deny 1,361 measured allocations in Boundary registration,
quality temporaries and prepared template creation. Missing-cell-context
queries throw std::logic_error; owned-cell numerical criteria are unchanged.
Selected lint covers six production units. The Boundary null-curve fixture
permits retry; failed templates are qualified for destruction only. See
[evidence](evidence/STAGE3_UV_REGISTRATION.md) for instruments and limits.

## Primary references reviewed 2026-10-15

- https://clang.llvm.org/docs/ClangFormatStyleOptions.html - repository style file.
- https://clang.llvm.org/extra/clang-tidy/ - compilation database and diagnostics.
- https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines - RAII, ownership,
  resource safety, interfaces and separation of responsibilities.
- https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html - shared presets.
- https://cmake.org/cmake/help/latest/manual/ctest.1.html - test discovery/execution.
- https://clang.llvm.org/docs/AddressSanitizer.html - instrumentation and limits.
- https://www.doxygen.nl/manual/config.html - API extraction and warning controls.

These are engineering references, not a proof that legacy code follows them.

## Tree construction qualification (#20)

Slice 5 introduced required application.uv_tree_contracts: 15 CTest tests at that boundary,
74 Python controls, 56 UV instrument cases and seven previous node cases.
Five independently calibrated CRT sweeps inject 3,470 allocation failures,
covering root, uniform subdivision, edge/old-face generation and real neighbor
refinement. Full original/candidate success traces and allocation counts must
match. Failed-tree destruction is qualified; retries and observer consumption
are not. See `evidence/STAGE3_UV_TREE.md` and ADR-0006.

## Angle-helper borrowed endpoints (#23)

Slice 6 adds required application.uv_angle_contracts: 16 CTest tests,
74 Python controls, 68 UV instrument cases and seven previous node cases.
Ten calibrated CRT sweeps deny 252 allocations through four endpoint-match
branches and the nonadjacent branch with empty/populated adjacency. They require
caller ownership/state, receiver cache/scalar state and successful query reuse
after every caught failure. ASan/CRT normal traces and successful allocation
counts match the original; the original fails all ten new sweeps. Prior 56
instrument controls remain required. See evidence/STAGE3_ANGLE_HELPER.md and
ADR-0007 for exact commands, diagnostic history and limits.

Doxygen 1.18.0 is now installed locally. The submitted initial documentation
run fails on undocumented APIs; this remains a stage-8 failure inventory, not
a documentation pass. Warning enforcement is unchanged.

## Parametric midpoint replacement (#26)

Slice 7 adds required application.uv_parametric_contracts: 17 CTest
entries, 74 Python controls, 81 UV instrument cases and seven previous node
cases. Eleven normal variants cover four sides/both directions, interior
fallback and null-curve no-op; ten CRT sweeps deny 30 allocations and require
unchanged cache identity/geometry and length, caller state and successful retry.
Normal success traces and successful allocation counts match the original.
Actual curve position/gradient, signed arc and midpoint have independent
analytic controls. Their three measured operation scopes observe zero
allocations; this is explicitly unmeasured curve-internal failure coverage.
See evidence/STAGE3_PARAMETRIC_MIDPOINT.md and ADR-0008 for commands and limits.
