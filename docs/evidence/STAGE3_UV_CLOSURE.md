# Stage 3 slice 2 integration closure

Issue #11; implementation PR #12. This closes the registered UV template and
endpoint-teardown slice. The full memory/lifecycle stage 3 remains open.

## Authority and exact revisions

- Entry main: `0f2473622800907e2d15e1d5ab6216caedb36797`, tree
  `ddde9c8a1ebb930c2890b0cc098ec698beb1cf1c`, 685 blobs.
- Qualified published head: `a5fb2cd0d7ebbe6dc10f98689f4d6caa60419c0c`.
- Integrated main: `5bfcadaaa2172c297448c9870c0f468feeae8f4a`.
- Both have tree `306907d63f893767736bddfd995cf313f1bfcf8f`, 706 blobs.
- All 43 changed/new files and all retained blobs were independently compared
  with the intended Git blob map before publication. The two remote-only
  immutable publication binaries are preserved. No deletions occurred.
- Remote main, branches, open PRs/issues, check runs and statuses were audited.
  There was no concurrent work; only issue #11 was active. Configured remote
  checks/statuses and Actions runs were zero; local required gates provide the
  results below. No hosted workflow was added.

## Explicit closure audit

Reviewed five AFT implementations, seven associated headers and the Windows
definitions header, the standalone probe, strict runner, CTest registration,
22 contracts/83 anchors, inventory, ADR-0003, state, plan and failure inventory.
Only demonstrated lifetime defects, minimal instrumentation prerequisites and
reviewed nullable/override diagnostics changed production behavior. Template
selection, numerical formulas/order/thresholds, boundary partitions, front/
smoothing, adaptation/acceptance/stopping policies, inputs, vendor and existing
independent scientific verifiers are preserved. Changed production ranges and
the new probe pass formatting; no lint configuration or oracle was weakened.

The pinned original's same 26-case runner remains failed. It demonstrates
61,584-byte post-template failure/exception retention, 68,464-byte abandoned
tree retention, midpoint-alias invalid access and allocation-dependent teardown.
The repaired cases pass with one owner, ordered address-preserving handoff,
zero teardown allocations and source ownership retained across three measured
observer-preparation allocation failures. Original diagnostic excerpts, initial
invalid fixture setup and compiler/lint failures remain evidence.

## Exact-head and post-merge regression

Both complete campaigns passed independently:

| Gate | Published head | Integrated main |
| --- | --- | --- |
| CTest, zero skipped | 11/11 | 11/11 |
| Python controls | 74 | 74 |
| UV ASan / separate Debug CRT | 26/26 | 26/26 |
| Previous physical node boundary | 7/7 | 7/7 |
| Selected five production-unit clang-tidy | Pass | Pass |
| Inventory freshness, 122 files / five CMake inputs | Pass | Pass |
| Two same-command runs per article model | Exact | Exact |
| Strict entry and previous-slice continuity | Exact | Exact |
| Named CSV fields | 189 matching | 189 matching |

All nine attempted article states retain positive shared-incidence coverage and
zero measured position gap. Both models accept steps 0/1; final accepted meshes
remain Eistute **1,168** and Book **4,256** triangles. OBJ, acceptance/CSV and
incidence comparison are exact. Application SHA-256:
`6cbb57bbfed033ebf5b8b11a359a628fbf92b1d1273fab357ca94511f026a8e8`.
Build checks retain all four instrumented executable identities.

Reports include commands, input/executable/source identities and log hashes:
[exact head](stage3/uv/head_qualification.json),
[post-merge](stage3/uv/postmerge_qualification.json),
[original failure](stage3/uv/original_failed_qualification.json),
[source audit](stage3/uv/source_identities.json). Commands/toolchain and detailed
case observations: [implementation evidence](STAGE3_UV_LIFETIME.md).

This follow-up changes documentation/evidence only and preserves every qualified
production, development-tool, test, build, model, configuration and vendor blob.
Its published-head and final-main CTest/inventory/delta audits are recorded on
the closure PR and issue #11 after execution. A documentation-only delta does
not replace the complete implementation-head and post-merge campaigns above.

## Remaining boundary and next step

Measured memory coverage is isolated Windows ASan plus separate Debug CRT,
including deliberately invalid controls. It is not Linux LSan/UBSan or a
full-application leak-free result. The square reaches template types 1 and 4;
other patterns remain unqualified. Repetitions construct fresh front objects.

Next qualify allocation failure before UV object registration and constructor/
setter replacement. Adapter temporary ownership, curve sample/initialization
ownership, rollback, same-front execute reuse, mate/root sharing, generic node
adjacency/cache mutation, full-process leaks, parallel modes, every internal
retry and Decor Shelf remain open. Stages 0-2 are closed for measured scope;
stage 3 is in progress with two closed slices; stages 4-11 remain pending.
