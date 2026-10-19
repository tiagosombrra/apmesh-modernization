# ADR-0020: consume pending SubMesh ownership before insertion

Status: accepted design; exact delivery qualification pending.

MeshAdaptive documents ownership transfer of raw SubMesh arguments. Wrapping the
pointer only after vector growth leaves it ownerless if growth throws. Returning
early for a negative position also abandons that consumed argument. Pinned actual
production units reproduce both defects with real physical graphs.

Construct a local unique_ptr at entry to each raw insertion, then move it into
the vector after successful growth. A negative position consumes and destroys
the argument while preserving existing slots. Preserve successful identity,
ordering, replacement and sparse/null semantics; no new retry or rollback policy.
Successful replacement invalidates observers of the old graph, as before.

Require unique, exclusively deletable actual SubMesh arguments and nonthrowing
destructors. Re-adopting an owned alias is invalid. SubMesh has a nonvirtual
destructor; test destruction through its actual owned polymorphic nodes and
triangles instead of deleting derived SubMesh instances through a base pointer.

Classification: behavior-changing resource-lifetime defect repair. Formulas,
floating-point order and generation/acceptance/stopping policies are unchanged.
SubMesh raw element adoption and whole-process/parallel memory remain separate.
See [root cause and evidence](../evidence/STAGE3_MESH_ADOPTION.md).
