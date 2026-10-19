# ADR-0024: stable triangle identity and list-node observer replacement

Status: accepted; full exact-head and implementation-main gates pass.

Node adjacency identifies a triangle by address. Implicit value copying changes
identity without publishing it; move expressions had used the copy operation.
Explicitly delete all four copy/move special members. Ownership wrappers and mesh
containers remain movable because their triangle object addresses are stable.
Current production lexical searches find no direct value-copy/move or ReplaceNode
consumer; unobserved external/conditional callers may need adaptation.

Preserve ReplaceNode first-match n1/n2/n3 selection. Transfer one existing physical
observer list node to the destination tail with splice before committing the
vertex pointer. This preserves repeated-vertex multiplicity and other list nodes
without allocation. Same/absent vertices are no-ops. Matched null destination or
missing/default registration reject before mutation; live non-null matched nodes
and a valid registration are required. Diagnostic exception storage is outside
the valid-operation zero-allocation claim.

Classification: behavior-changing observer-consistency defect repair and explicit
identity API tightening. Preserve triangle/node scalar state, ID/UV and all cached
geometry; no recomputation, formula/evaluation-order or numerical-policy change.
Cache validity after coordinate-changing replacement remains unqualified. Ordinary
triangle destruction is unchanged; completed-triangle observer removal and failed
adoption graph reuse require a separate actual-unit and model regression audit.
See [evidence and closure inventory](../evidence/STAGE3_TRIANGLE_OBSERVER.md).
