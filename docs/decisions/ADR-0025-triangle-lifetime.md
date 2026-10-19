# ADR-0025: unregister completed triangles before borrowed vertices expire

Status: accepted; full exact-head and implementation-main gates pass.

Construction registers this in three node lists, but the completed destructor
left those addresses behind. Actual-unit post-delete traversal reproduces ASan
UAF despite zero final CRT retention. Remove matching this observers from each
non-null current vertex without allocating or deleting nodes/elements. Repeated
vertices and the all-null default object are safe; virtual/base destruction also
cleans a completed base after a controlled derived constructor failure.

Require live borrowed nodes through destruction. Qualified SubMesh destruction/
move ordering supplies this for its own physical graph. Stable noncopyable identity
and first-match ReplaceNode registration remain unchanged. General foreign copied
observer lists, arbitrary protected mutation and invalid external lifetimes are
not repaired. Strengthen the previous terminal-adoption oracle to require the exact
live observer prefix; retain its historical negative evidence and independently
pair current-entry sources with the same fresh-adoption probe.

Classification: behavior-changing observer-lifetime defect repair. Formulas,
evaluation order, caches/UVs, numerical policies and CLI retry behavior do not
change. Component fresh construction/adoption after exact cleanup does not establish
full process recovery, metadata rollback or consumed-object reuse. See [evidence
and closure inventory](../evidence/STAGE3_TRIANGLE_LIFETIME.md).
