# ADR-0022: remove partial observer publication on triangle construction failure

Status: accepted; exact published-head and implementation-main gates pass through PR #64.

The parameterized TriangleAdaptive constructor publishes this in three node
lists before construction completes. If a later list allocation throws, the
triangle destructor is not called and earlier registrations remain expired.
Actual pinned units reproduce one/two extra live list nodes despite zero
retained blocks after final node destruction.

Keep original vertex registration and cached-geometry evaluation order. On a
C++ construction exception, remove matching this observers from the three live
nodes without allocating, then rethrow. A narrow NodeAdaptive observer-removal
method erases pointer entries without owning/deleting the element. Repeated
vertices are handled by removal of all matching entries; existing list nodes,
order, null markers and scalar fields are preserved. No full-state snapshots.

Require three live non-null nodes, valid existing adjacency, a fresh triangle
address without pre-existing registrations, and nonthrowing cleanup. Degenerate
repeated-node fixtures qualify lifecycle behavior, not geometric validity.

Classification: behavior-changing exception-consistency defect repair, preserving
success and numerical policies. Ordinary triangle destruction still does not
unregister observers; successful-construction deletion/adoption failure,
ReplaceNode/copy/move, mesh destruction/move ordering and whole-process/parallel
qualification remain separate. The component probe constructs a fresh triangle
after exact restoration; no CLI retry policy is introduced.
See [evidence and limits](../evidence/STAGE3_TRIANGLE_CONSTRUCTION.md).
