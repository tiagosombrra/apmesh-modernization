# ADR-0018: explicit serial curve-sample lifetime

Status: accepted; exact published-head and implementation-main gates pass through PR #56.

Curve lists observe collectively shared samples. Generator's late manual cleanup
does not execute when generation/reporting throws, and its unordered_set can
itself fail allocation. The CLI reports that exception and terminates; it does
not recover and reuse partially updated Generator metadata.

Give the current published graph one serial scope owner, installed before
initialization. Preserve explicit release at the previous normal cleanup point,
and release automatically during exceptional unwinding after inner guards. Clear
all aliases before each deletion without allocating. Geometry must outlive this
owner; sample objects must have no competing control-point or physical-mesh owner.
Qualified inner operations leave surviving objects reachable in current lists.

This is resource release, not metadata rollback or a new retry/acceptance policy.
Unpublished allocations and constructor failures need separate local ownership
repairs. Parallel and full-process qualification remain separate. Teardown order,
allocation behavior and worst-case quadratic alias scanning change; numerical
formulas and policy remain unchanged. Evidence and limits:
[serial sample lifetime](../evidence/STAGE3_CURVE_SAMPLE_LIFETIME.md).
