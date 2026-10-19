# ADR-0027: own temporary triangle-count graphs

CalculateNumbersTriangle discarded its raw SubMesh after reading a scalar count,
leaking the physical graph and retaining patch/curve publications. Deleting that
mesh alone would leave a dangling patch observer. A general Geometry sample owner
would also delete preexisting borrowed samples, so its semantics cannot replace
the required selective boundary.

Delegate to CountEstimateTriangles. Own the physical mesh with unique_ptr and use
a private nonallocating scope to restore the preceding patch observer and reclaim
only fresh samples published into the four initially empty curve lists. Preserve
preexisting sample/parameter/adjacency list-node identity. Clear all owned aliases
before each sample deletion. Retire the scoped graph before destroying independent
copied physical nodes. No shared ownership or application metadata rollback.

Classification: behavior-changing resource-lifetime defect repair. Returned counts,
builder formulas/order and scientific policies are unchanged. Actual-helper memory,
live-state, full allocation sweeps and scalar-count comparisons qualify this
boundary; area/error callers, arbitrary callbacks, evaluator scratch, geometric
validity of lifecycle fixtures and full-process/parallel memory remain separate.
See [evidence and closure inventory](../evidence/STAGE3_TRIANGLE_COUNT.md).
