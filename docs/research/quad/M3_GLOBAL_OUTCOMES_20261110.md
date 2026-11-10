# M3-6b — bounded global TRI outcome observations

**Status:** merged to research `quad-templates` via PR #192. Exact-head pre-merge CI passed; post-merge run #42821767939 separately tracked. No physical QUAD generation.

A research-only caller installs hooks via `GeneratorAdaptive::SetResearchUvCapture`, which now allocates one per-generator `GlobalOutcomeLog` with a fixed capacity of 128 value-only events. Normal TRI calls do not allocate this log. Every event inherits the `OuterAttemptIdentity` session namespace, monotonic epoch and global retry from M3-6a.

The four distinct `GlobalOutcomeKind` values mark different facts:
- `ElementBudgetRejectedCandidate` is recorded after an element-budget evaluation rejects a candidate and before the outer retry `continue`.
- `GrowthRejectedCandidate` is recorded after excessive element-growth evaluation and before its `continue`.
- `AcceptedStepCommitted` is recorded **after** the real serial `AcceptedMeshScope::Commit()`.
- `RejectedStepRestored` is recorded **after** both rejected geometry and curve states have been restored.

The first two are *evaluations*, not global commit/rollback claims. The latter two confirm completed transitions in the serial generator; they are not equivalent to an accepted QUAD mesh. No observer callbacks, file writes or memory allocations occur in any of these critical paths. `Record` is `noexcept`. `GetResearchGlobalOutcomeLog()` exposes the chronological prefix as const values and `truncated()` signals lost events; consumers must not claim completeness after overflow.

Native QUAD contracts test overflow, ordering, immutable scope values, reset and all four event kinds. A full research-hook-enabled `GeneratorAdaptive::Execute` test that forces budget, acceptance and rollback is **not included** here and remains a separate M3-6c qualification requirement. MPI/OpenMP runtime correctness and complete sanitizers remain unverified. TRI default and experimental `quad_uv` fail-closed selection are unchanged.

**Required tests:** Linux GCC and Windows MSVC QUAD 4/4 native CTest, root TRI 76/76 CTest, Python tooling 527/527, seven CLI denials, conditional OMP syntax and frozen Eistute/Book five/four-state OBJ/acceptance/boundary parity. No merge before exact-head green CI.

## Audited integration receipt

[PR #192](https://github.com/tiagosombrra/apmesh-modernization/pull/192) merged at `584fe2a2959b268908bc2d9feff8888658a47d62`. [Exact-head CI #42816180344](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42816180344) passed 4/4 jobs (QUAD Linux/MSVC 4/4 each; TRI 76/76 CTest, Python 527/527, Eistute/Book 5/4 scientific parity); [postmerge #42821767939](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42821767939) in_progress at checkpoint. The event API is NOT yet runtime-qualified by a full hook-enabled GeneratorAdaptive run: that is M3-6c.
