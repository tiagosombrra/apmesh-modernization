# Technique-preserving APMesh modernization

The imported implementation remains the historical algorithm. API migration
and full Doxygen coverage are pending; an undocumented declaration is not a
verified ownership or numerical contract.

## Ownership and observers

Document the unique owner, borrowed references, invalidation on replacement,
copying versus transfer, rollback and error-path cleanup for each API.
Shared geometry does not imply shared ownership.

Completed Bezier retirement (C26/ADR-0033) requires current borrowed curves to
outlive the entire patch destructor. Destruction removes every observer equal
to the patch address from those curves, preserving other pointer values in
order without allocating or deleting patches. Vector capacity and iterators
are not preserved contracts. Arbitrary curve replacement, copied observer lists
and foreign publications remain outside this boundary.

Geometry owns its curves and patches exclusively. Destruction and populated
move assignment retire old patches before their borrowed curves; incoming
objects keep their addresses and self move preserves the graph. Borrowing from
another Geometry's retiring destination owners is invalid; foreign observers
are not automatically rebound. Actual qualification status and remaining scope
are in [the observer evidence](evidence/STAGE3_BEZIER_OBSERVERS.md).

Serial input (C27/ADR-0034) returns a new list of unique control-only PatchBezier
owners from LoaderBezierPatchFile. Each result is independent. ReaderFilePatches
retains those controls while interning coordinates and consumes a separate unique
reconstructed patch through Geometry::InsertPatch. Partial parse results release
on failure; Geometry can retain an already committed prefix on later failure.
No external raw-result/binary compatibility or complete-reader rollback/retry is
claimed. Three badbit masks propagate resource errors before partial row indexing;
normal validation, EOF/failbit, control/ID order, interning tolerance and directions
are preserved. Other loaders retain separate contracts and pending coverage.
See [the serial boundary evidence](evidence/STAGE3_SERIAL_READER.md).

## Numerical contracts

State domain, coordinate system, units, orientation, degeneracy, finite-value
preconditions, tolerance meaning and failure behavior. Do not conflate a
numerical roundoff budget with geometric discretization error.

## Topology contracts

Distinguish parameter-domain and physical meshes. Boundary identity and
orientation must remain explicit for every incident patch. Treat curvature
at a non-manifold junction by sheet/incidence, with declared coverage.

## Scientific behavior

Document the article algorithm step and any defect repair that changes its
result. New estimators, generators and stopping criteria are research changes.
