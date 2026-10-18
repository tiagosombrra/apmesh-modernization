# Stage 3 slice 9: initialized curve copy parameters

Issue #32. Entry main 8088c0b487c74cd27f215465fe364f717b78a80f, complete tree
45a4aa671f2dbf689860205c189e3d0c1244305a (961 blobs). Remote audit found 22
branches, no open PRs/issues, check/status contexts or Actions before the sole
active item opened. Complete entry working bytes match Git. All 460 original
production/header/vendor blobs are extracted and verified against entry Git.
The historical repository is untouched. This is a copy-state defect repair,
not a scientific proposal.

## Entry and original failures

Fresh previous curve 19/19, UV 81/81 and node 7/7 entry controls pass. Serial
comparison reuses the qualified slice-8 implementation-main
587c91923b48d7f55414df720d29bcb1d2dacc11 outputs; all 510 qualified inputs are
unchanged on entry documentation-main 8088c0b, whose exact CTest and complete
checkout gates already pass. No second fresh entry model campaign is claimed.

The original loses the populated parameter sequence in parametric, Bezier and
Hermite pointer-taking copies, in forward and reverse sample order, under both
instruments: 12 normal cases fail. Each reports
`copied parameter sequence preserves sampled-point pairing and order`.
Six populated CRT denial scopes also fail their successful calibration copy
contract before injecting any failure. Their original populated denial coverage
is unmeasured, not failed or passing memory qualification. Twelve other original
case outcomes are as expected, including deliberately invalid controls.

The new probe compiles nine actual curve/point/patch/numerical units. Derived
sources are added only to the new target; the previous collection target remains
seven units. Existing target compiler/sanitizer/link options are applied equally
without changing their values. No replacement numerical implementation or
alternative generator is introduced.

## Repair and measured contract

One production constructor initializer copies parameters_ under standard-list
RAII; its header records initialized/non-null source and borrowed-object limits.
Public function types and class layout are unchanged. Point/patch containers
retain borrowed identities; parameter values and all container nodes are copied
independently. The source is unchanged on normal copy, copy mutation/destruction
and every propagated allocation failure. Copies preserve ID/length, endpoint/
control IDs and XYZ, tangents, coefficient/basis/initial scratch matrices and
sample/patch identity/order. Independent parameter/point/patch container mutation
is checked; both curve destruction orders retain caller-owned objects until
their actual owners destroy each once (five samples, two patches per fixture).

Empty sequences are explicit controls. Forward/reversed cases each traverse five
actual copied parameter/sample pairs and check physical correspondence. For
x(t)=0.3t+0.6t^2+0.1t^3, five position/derivative samples and both signed arc
directions are checked against scalar formulas using existing 1e-12 bounds.
The parametric evaluator is initialized through public coefficients; actual
Bezier controls [0,0.1,0.4,1] and Hermite endpoints/tangents [0,1]/[0.3,1.8]
produce the same independent cubic. All 18 original/repaired normal numerical
traces match; empty-sequence full traces match. Populated copy state intentionally
gains the missing parameters. No tolerance or numerical expression is changed.

| Scope per type | Original allocation count | Repaired count | Denial coverage |
| --- | ---: | ---: | --- |
| Empty sampled sequence | 7 | 7 | All measured ordinals in both versions |
| Forward five-sample sequence | 12 | 17 | Original stops at calibration; all repaired ordinals |
| Reversed five-sample sequence | 12 | 17 | Original stops at calibration; all repaired ordinals |

The nine independently calibrated sweeps deny 123 repaired ordinals, exactly
once each, requiring unchanged source values/nodes/objects and complete retry.
Five additional populated-copy parameter nodes are intentional resource changes;
counts are observations, not portable constants. The previous collection runner
also independently recalibrates its two-parameter copy (nine to 11 allocations).
No zero-denial sweep is accepted. Constructor measurements exclude fixture setup,
contract checks and numeric evaluation. Valid CRT cases retain zero normal
blocks/bytes; actual allocation denial, ASan UAF and CRT leak controls must respond.

## Candidate campaign and reproduction

Candidate CTest 19/19, zero skips and 74 Python controls, new copy 30/30, previous
curve 19/19, UV 81/81 and node 7/7 pass. Read-only selected lint covers the changed
parametric implementation and its compiled configurations under unchanged rules.
The complete new probe and changed constructor/header ranges are explicitly
formatted. Inventory remains 123 C++ files (57 units, 66 headers), six CMake
inputs, 22 contracts and 99 anchors; the known six-header cycle remains.

Native Windows GCC 16.1.0 serial C++17 Release, MPI/OpenMP/LTO off and static
MinGW runtime; LLVM 22.1.8. Narrow instruments use separate MSVC 19.44.35229.0
ASan RelWithDebInfo and Debug CRT builds. Compiler/preset records and flags are
retained. Relevant interfaces:

```text
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <fresh-phase>/ctest.xml
cmake -S tests/curve_memory -B build/c9a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_CURVE_ASAN=ON
cmake --build build/c9a --config RelWithDebInfo --target curve_copy_probe --parallel 2
cmake -S tests/curve_memory -B build/c9d -G "Visual Studio 17 2022" -A x64
cmake --build build/c9d --config Debug --target curve_copy_probe --parallel 2
python tools/qualify_curve_copy.py --asan build/c9a/RelWithDebInfo/curve_copy_probe.exe --crt build/c9d/Debug/curve_copy_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/copy
python tools/quality.py tidy src/data/curve/curve_adaptive_parametric.cpp --build build/windows-gcc17
clang-format --dry-run --Werror tests/curve_memory/copy_probe.cpp
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Original c9oa/c9od use identical final probe/options and AP_MESH_CURVE_SOURCE_ROOT
set to the verified snapshot. Previous UV/collection instruments are rebuilt
against the changed base constructor/header; previous node inputs are unchanged.
Two repetitions per Eistute/Book use the established repeat_generation.repeat
interface with its unchanged 300-second bound, strict boundary verification and
independent CSV audit. All nine attempted states, positive shared-incidence
coverage, zero measured position gap, acceptance/rejection and 189 named CSV
fields match entry. Accepted steps stay 0/1, rejected Eistute 2/3/4 and Book 2/3
remain visible; last accepted triangles remain 1,168/4,256.

## Failure/coverage inventory and remaining gates

Reports, original failure/normal traces, the verified snapshot map and actual
toolchains are retained in stage3/curve_copy/. Deliberate-negative raw diagnostic
logs remain byte-for-byte local with hashes in original_raw_log_inventory.json;
they are not normalized or described as current tracked raw files. Large current
instrument and verbose CTest/JUnit logs remain local with hashes. Exact published-
head and implementation-main complete campaigns remain required before closure.
No hosted checks or paid Actions are configured.

CloneCurveForPatch/DisableSharedCurveSynchronization is reviewed statically,
without enabling/changing that scientific policy or claiming its integration
qualified. Post-copy publication, implicit copy/assignment, inconsistent/null/
uninitialized input, other constructors/mutations, shared ownership, initialization/
rollback, general observers and full-process/parallel/LSan/UBSan remain open.
Scoped CRT retention is not full-process leak freedom. Full stage 3 stays open;
stages 0-2 stay closed and stages 4-11 stay pending. Doxygen 1.18.0 undocumented-
API debt stays stage 8. Code/tests/contracts/docs/scientific scope and known
failures/coverage must be explicitly audited before this work item closes.

Candidate input identity: `f9336d27b8b18636ca0393026cd285ade7a4334ccaf52b8b5329611ca392aef2`.
Application SHA-256: `5ce368fb7c0993d1cdf09a8e853631d20df61c2783a0c309197ee3a9b0881626`.
