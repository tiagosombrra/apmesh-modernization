> Pre-integration checkpoint. STAGE1_CLOSURE.md records the subsequent exact-head
> audit, integration and successful post-merge regression.

# Stage 1 closure candidate: orientation and report repairs

Date: 2026-10-16 UTC. Work item: issue #2 / PR #3.
Base: `28494333d6223de309770c233cbc1d10ea1371a3`.
Historical failing evidence in STAGE1_INCIDENCE_AUDIT.md is retained unchanged.
This report supersedes its current-status conclusions, not its observations.

## Defects and contracts

Shared-curve storage has one canonical direction. Each Bezier patch incidence
now records whether its local increasing side parameter opposes that direction.
The reader resolves all four controls, checking exact direction first and then
the existing curve-match policy. It does not introduce a new welding tolerance.
Both patch constructors preserve the input control net; copying a patch preserves
its direction flags. The initial mesh and adaptive reconstruction map stored
points to local UV consistently, including sides traversed clockwise by the front.

Physical midpoint bisection and arc integration receive increasing canonical
limits. Reversed incidences complement the limits and map the midpoint back.
The integration, solver, tolerances, refinement, smoothing and acceptance formulas
are unchanged. The outgoing side of a boundary vertex supplies the completed
edge's curve: the old implementation used the newly appended vertex's next side
at a corner. An independent analytic control distinguishes the correct normalized
length 0.6875 from the old next-curve result 0.875.

CSV repair moves only the adaptation_relaxation header label to its actual row
position, after budget_driver_mode. Row serialization order is unchanged.
The independent semantic checker still compares 21 named fields to analysis logs
with no numerical tolerance. Neither that oracle nor strict regression was relaxed.

These are behavior-changing defect repairs, not scientific proposals or claims
of unchanged output against the defective implementation. The prior pointer-order
repair remains separately documented in STAGE1_SMOOTHING_ORDER.md.

## Independent and executable controls

- All 14 real generation controls pass: four original planar controls, plus
  aligned and reversed asymmetric curved cases on each of the four patch sides,
  with two and three incident sheets. Their 44 exported attempted states have
  actual shared-boundary coverage. Adaptive cases exercise refinement, accepted
  and rejected states, repeated reconstruction after rejection and retry count 1.
  The forced three-sheet side-2 case must observe both retry and rejection.
- The C++ probe checks all 16 constructor direction combinations against an
  analytic surface, direction preservation by copy, eight physical side/direction
  combinations against an independently inverted monotone cubic, and the corner
  curve control. Test-only precision settings do not change application settings.
- 65 Python positive/negative checker and tooling controls pass, as do 23 actual
  invalid-input controls. Prior invalid geometry, shifted CSV and failed numerical
  comparisons remain preserved; a historical rejected target still cannot stand
  in for an accepted mesh.
- Full CTest: **9 passed, 0 failed, 0 skipped**. No WILL_FAIL or skip hides a gate.

Retry coverage records the final exported attempt for each outer step and named
retry counters. It does not observe every transient inner-retry mesh or establish
memory safety across these paths. The legacy runtime definitions are temporarily
reused by the C++ probe; independent library extraction remains stage 6 work.

## Article regression and explicit output changes

| Observation | Eistute | Book |
| --- | --- | --- |
| Attempted states per execution | 5 | 4 |
| Accepted steps | 0, 1 | 0, 1 |
| Rejected steps | 2, 3, 4 | 2, 3 |
| Last accepted triangles before repairs | 1,168 | 4,418 |
| Last accepted triangles after repairs | 1,168 | 4,256 |
| Identical executable/configuration/command repetition | PASS | PASS |
| Strict comparison to minimally corrected reference | PASS | PASS |
| Named CSV fields checked per execution | 105 | 84 |

Raw comparison to the preceding candidate deliberately remains FAILED: 62
Eistute differences from corrected CSV labels; 287 Book differences including
the corner-curve geometry repair. Eistute OBJ bytes are unchanged. Both models
retain their accepted/rejected step sequence. These failures are not relabelled
as successful strict regressions.

The controlled reference starts at the stated base and applies only two minimal
fixes: CSV labels and the completed edge's preceding curve. Its exact patch and
build/restoration identities are retained in stage1/orientation/. It contains no
new patch-incidence direction logic. Both reference repetitions pass exactly.
Candidate/reference comparison then requires identical OBJ hashes, every CSV
and acceptance field, source model/config identities, incidence fields and
snapshot hashes for all nine attempted states. Both models pass, isolating the
orientation implementation from the separately proved defect repairs.

Every article state checks all 16 Eistute / 112 Book sides, including rejected
candidates. The non-manifold shared groups have 4 / 28 sheets and 3 / 27
comparisons per state; measured shared-position gaps are zero. All four candidate
repetitions pass the semantic CSV audit. Existing independent evaluator/export
roundoff budgets are unchanged; strict numerical comparisons remain exact.

## Static analysis, formatting and scope

The selected exporter clang-tidy gate now passes. Nine inherited first-party
override findings were repaired by explicit override declarations. The remaining
vendor findings arose because lexical include paths such as include/../../libs
matched the first-party header filter. Explicit vendor-header exclusion repairs
that scope, consistent with quality.py's existing vendor policy. No check is
disabled, warnings-as-errors remains enabled and vendored Eigen is unchanged.
Three real analyzer controls prove vendor exclusion and required failures for
equivalent first-party header and source diagnostics. Missing clang-tidy fails.
The qualified analyzer is clang-tidy 22.1.8.

Changed C++ ranges in 15 existing files and both complete new C++ files pass
clang-format checks. This is incremental adoption, not a full legacy formatting
or lint-clean claim. Compiler warning debt remains visible. A transient local
executor interruption was followed by a resumed build and complete successful
CTest run; interrupted invocations are not qualification evidence.

## Reproduction and closure requirements

Qualification uses native Windows UCRT64 GCC 16.1.0, C++17 serial Release,
MPI/OpenMP/LTO OFF, CMake/CTest 4.4.0 and LLVM tools 22.1.8.

```sh
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure
python tools/quality.py tidy src/input_output/incidence_snapshot.cpp --build build/local-serial
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh --model eistute --output build/new-eistute-repeat --report eistute-repeat.json
python tools/audit_metric_schema.py build/new-eistute-repeat/repetition-1 --report eistute-schema.json
python tools/verify_generation.py build/new-eistute-repeat/repetition-1 --require-boundary-coverage --report eistute-generation.json
```

Use .exe on Windows; repeat for Book and the second repetition. Fresh output
directories are mandatory. Apply controlled_reference.patch to the stated base
in a separate checkout to reproduce the minimal reference, then run the same
repetition and strict comparison commands with --baseline. No golden report or
defective raw reference is silently replaced.

Prepublication local gates pass. Integration still requires exact published-head
source/tree verification and repeated gates, a remote concurrency/check audit,
and post-merge validation on main. Main must not advance on a failing gate.
Stage 2 starts only after that closure. Sanitizers, full ownership repair,
parallel qualification, Eigen removal, C++23, Decor Shelf generation, Doxygen
review and performance qualification remain later-stage work. No paid Actions
or hosted workflow was introduced. Evidence includes source, input and executable
hashes, raw failures, controlled comparisons, generation coverage and logs.
