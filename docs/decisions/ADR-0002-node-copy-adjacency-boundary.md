# ADR-0002: independent physical node copies exclude foreign adjacency

Status: accepted engineering defect repair, stage 3 slice 1 (#8, PR #9).

## Context

SetNoh has always copied its argument into SubMesh ownership. Initial-mesh
callers depend on independent copies while originals can remain shared curve
samples. Its grouped header comment incorrectly promised adoption. General
NodeAdaptive copy duplicates observer adjacency, so destroying an original
triangle left a reproducible dangling pointer in the copied mesh node.

## Decision

Keep SetNoh's scalar-copy and null-ignore behavior. Preserve ID, XYZ and all four
curvature fields; clear the new owned node's foreign element observers. Local
TriangleAdaptive construction registers local adjacency in its existing order.
Document AddNoh(unique_ptr) transfer and SetElement raw adoption separately.

Do not change general NodeAdaptive copy/assignment or TriangleAdaptive value
snapshots in this slice: those uses require separate semantic review. Do not
replace copying with raw adoption, which would alter curve-sample ownership and
pointer lifetimes. Do not introduce shared_ptr to mask ambiguous ownership.

## Consequences and evidence

The original expired-triangle control fails under ASan; the repaired boundary
passes 200 valid rebuild/move/replacement/teardown iterations under ASan and
Debug CRT. Deliberate UAF, double-free and leak controls remain detected. Exact
Eistute/Book article regression is preserved. This is a demonstrated API lifetime
repair with no observed scientific output change; full mesh destruction,
mutation, rollback and sample ownership remain separate work.

See [closure audit](../evidence/STAGE3_SLICE1_CLOSURE.md) for SHAs and qualified
scope. No scientific technique or advisor-approved policy was revised.
