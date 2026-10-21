# ADR 0031: automatic curvature samples

Status: implemented; exact-head/main qualification pending.

Replace overwritten heap allocations with automatic PointAdaptive values and
pass them directly to the actual PointAdaptive curvature API. Use a fixed
25-entry automatic scratch buffer for the at-most-25 populated entries. Preserve
historical sample thresholds, order, arithmetic, fallback and requested-count
denominator, including between-level/out-of-range semantics. Translate the touched
early diagnostic; do not introduce a sample validation or scientific policy.

Require actual ASan/CRT controls, zero-allocation and exception observations,
independent numerical token mutations, GCC original/repaired scalar traces and
full exact-head/main regression before integration. Retain original leaks and
failed probe preflights; the original MSVC VLA adapter is explicit. Other helpers,
arbitrary callbacks/cache rollback and full-process/parallel remain unqualified.
See [cause, measurements and limits](../evidence/STAGE3_CURVATURE_SAMPLE.md).
