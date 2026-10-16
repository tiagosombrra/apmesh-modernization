# Technique-preserving APMesh modernization

The imported implementation remains the historical algorithm. API migration
and full Doxygen coverage are pending; an undocumented declaration is not a
verified ownership or numerical contract.

## Ownership and observers

Document the unique owner, borrowed references, invalidation on replacement,
copying versus transfer, rollback and error-path cleanup for each API.
Shared geometry does not imply shared ownership.

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
