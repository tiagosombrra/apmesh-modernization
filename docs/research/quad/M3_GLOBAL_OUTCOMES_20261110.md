# M3-6b — bounded global TRI outcome observations

**Status:** code candidate pending GitHub Actions and independent review. No physical QUAD generation.

A research-only caller installs hooks via `GeneratorAdaptive::SetResearchUvCapture`, which now allocates one per-generator `GlobalOutcomeLog` with a fixed capacity of 128 value-only events. Normal TRI calls do not allocate this log. Every event inherits the `OuterAttemptIdentity` session namespace, monotonic epoch and global retry from M3-6a.

The four distinct `GlobalOutcomeKind` values mark different facts:
- `ElementBudgetRejectedCandidate` is recorded after an element-budget evaluation rejects a candidate and before the outer retry `continue`.
- `GrowthRejectedCandidate` is recorded after excessive element-growth evaluation and before its `continue`.
- `AcceptedStepCommitted` is recorded **after** the real serial `AcceptedMeshScope::Commit()`.
- `RejectedStepRestored` is recorded **after** both rejected geometry and curve states have been restored.

The first two are *evaluations*, not global commit/rollback claims. The latter two confirm completed transitions in the serial generator; they are not equivalent to an accepted QUAD mesh. No observer callbacks, file writes or memory allocations occur in any of these critical paths. `Record` is `noexcept`. `GetResearchGlobalOutcomeLog()` exposes the chronological prefix as const values and `truncated()` signals lost events; consumers must not claim completeness after overflow.

Native QUAD contracts test overflow, ordering, immutable scope values, reset and all four event kinds. A full research-hook-enabled `GeneratorAdaptive::Execute` test that forces budget, acceptance and rollback is **not included** here and remains a separate M3-6c qualification requirement. MPI/OpenMP runtime correctness and complete sanitizers remain unverified. TRI default and experimental `quad_uv` fail-closed selection are unchanged.

**Required tests:** Linux GCC and Windows MSVC QUAD 4/4 native CTest, root TRI 76/76 CTest, Python tooling 527/527, seven CLI denials, conditional OMP syntax and frozen Eistute/Book five/four-state OBJ/acceptance/boundary parity. No merge before exact-head green CI.
