# Portable terminal observer candidate: qualification stopped

Classification: engineering-only test instrumentation candidate. Entry main is
`4cdeb15393487871542909bef065074bbad158b4` (PR #138). Production sources, public
interfaces, fixtures, configurations and scientific policies remain unchanged.
This candidate is unqualified; it is retained for draft review, not integration.

## Bounded implementation

The existing SP-09/10 observer uses GNU linker wrapping. The standalone
tests/terminal_observer target prepares a reversible test copy of Adapter:
its two `avanco.execute(mesh_old)` calls route through a test function. The test
function calls the unchanged typed fixture's BeforeExecute with the actual AFT
context; a selected false result returns false, otherwise the actual native
execute method is called once. No AFT body, mesh formula, selection policy,
accepted/rejected decision or stopping criterion is edited.

The original typed_domain_failure_fixture.h remains intact. A generated copy
changes only its allocation-observer include to a small portable test interface.
The payload, propagation, library owner/observer/sample assertions and unwind
control bodies are byte-identical. Both generated copies reverse exactly to
their original bytes. The preparer rejects missing/extra call sites, already
intercepted source and dependency drift; its four Python tests pass.

The probe embeds the actual CLI main body under a test-only function name and
compiles every production unit, with the generated Adapter replacing its original
unit. Seventy-four compiler groups represent the 73 production units plus the
separate allocation observer/control unit. All groups carry MSVC /fsanitize=address
under C++17 RelWithDebInfo. The ordinary global new/delete test replacements
provide actual allocation denial; they are not production allocators or full
allocator/leak accounting. Aligned/runtime allocation paths are not generalized.

## Build and controls

Configure with the following command, then build the terminal_observer_probe
target using RelWithDebInfo and --parallel 2:

```text
cmake -S tests/terminal_observer -B <build> -G "Visual Studio 17 2022" -A x64 -DCMAKE_CXX_STANDARD=17 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DCMAKE_CXX_FLAGS=/fsanitize=address
cmake --build <build> --target terminal_observer_probe --config RelWithDebInfo --parallel 2
```

Compiler/runtime identities match the preserved profile. The candidate builds
once successfully; no rebuild follows the native failure. Its SHA-256 is
`20b7132e2deb53969593de69558fea3638095b388395f1aa605ca4f137cf5218`.
With ASAN_OPTIONS=halt_on_error=1, each prerequisite has a ten-second cap:

| Prerequisite | Observed result |
| --- | --- |
| --instrument-release | Returns zero after an actual independent allocation/read/release. |
| --instrument-uaf | Expected nonzero result; ASan reports heap-use-after-free in TerminalControlRead after the real release. This is deliberate instrument detection. |
| --observer-contracts | Returns zero; selected live AFT interception, excluded contexts, disabled selector and independent real allocation denial pass. |
| --typed-domain-contracts | Returns one: all nine payload/identity/nonallocating-propagation rows pass, then the actual unwind-allocation control fails. Required completion markers are absent. |

The first unexpected diagnostic is:
`Typed domain failure: native allocation during unwinding was not denied`.
The unchanged assertion combines detection/catch and allocation counters; their
individual values were not emitted. Allocation elision, MSVC exception-runtime
semantics or another cause is not established. This does not demonstrate a
production defect. The nine preceding rows are partial evidence, not a passing
type-contract or observer qualification.

## Stop and remaining contexts

The campaign stops immediately at that failed prerequisite. Zero directed CLI or
library contexts execute; all five remain unrun: SP-09 Book patch 0, Eistute
patches 0/1, and SP-10 Book patch 0/Eistute patch 1, each at step 2 with its fixed
attempt oracle and 300-second cap. No context, instrument control or native
campaign is repeated after the failure. No assertion, timeout or fixture changes.

Two preparation-driver refusals precede compilation/native execution: an initial
identity check used the preceding delivery's entry documentation rather than its
integrated staged hashes, and a literal MSBuild tlog directory missed its
abbreviated name. Their records and bounded corrections are preserved; neither
is relabeled as a successful gate or native context observation.

The [compact record](stage3/serial_asan_terminal/summary.json) and local
build/p3-msvc-asan-terminal manifest retain source/tool hashes, preparation proof,
compiler commands, executable/PDB identity, four control processes and raw logs.
Prior SP-01..08 evidence and all 66 article input files remain intact.

Qualification is a failing required gate. Integration, exact-delivery regression
and Stage 3 closure are blocked. No full CTest or scientific campaign is repeated
to substitute for this failure. Draft review may check source identity,
whitespace, contracts/inventory and the already observed preparer tests, without
claiming native qualification. The next bounded task is to repair and requalify
the demonstrated unwind-allocation control, retaining actual allocation coverage
and unchanged terminal oracles before measuring the five fixed contexts.
