# ADR 0033: completed Bezier observer retirement

Status: accepted for a bounded defect repair; exact-revision qualification is
recorded in the linked evidence, not inferred from this decision.

A completed PatchBezier removes every observer equal to its own address from
each current nonnull borrowed curve during destruction. Preserve all other
pointer values in order, including duplicate foreign observers and null markers.
Removal does not allocate, dereference or delete patches. Vector capacity and
iterator stability are not restoration guarantees. Borrowed curves must outlive
the patch, including its destructor; arbitrary ReplaceCurve publications and
copied observer lists are outside this boundary.

Geometry already declares patches after curves, so reverse member destruction
retires patches first. Default memberwise move assignment instead releases the
old curves before old patches. Replace it with a temporary moved-in Geometry and
nonallocating member swaps; the temporary retires the complete old graph in
destruction order. Self move is an explicit no-op. Incoming objects keep their
addresses; foreign observers are not rebound. Cross-Geometry borrowing of the
destination's retiring owners is invalid.

Require actual positive and deliberately broken ASan/CRT controls, exact unrelated
observer preservation, populated destruction/move/self-move, allocation-denied
teardown, original/repaired live numerical traces, preservation mutations and
the complete prior regression. This changes destruction/failure behavior without
changing formulas, numerical order or adaptive policies. Hermite retirement,
successful fresh-curve caller adoption, full orchestration rollback and whole-
process/parallel/LSan/UBSan remain separate.

See [bounded evidence](../evidence/STAGE3_BEZIER_OBSERVERS.md) and
[stage 3 closure inventory](../architecture/STAGE3_CLOSURE_INVENTORY.md).
