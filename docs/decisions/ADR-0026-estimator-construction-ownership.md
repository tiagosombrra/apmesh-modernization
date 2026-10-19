# ADR-0026: isolate estimator construction ownership

InitialMeshEstimate returned a SubMesh already adopted by an unreachable Mesh;
caller re-adoption duplicated ownership while roots/source temporaries leaked.
Return one unique physical mesh owner from BuildInitialEstimateSubMesh. Pending
source samples and triangles stay locally owned; first successful curve insertion
transfers the sample to the existing collective lifetime. Only complete construction
publishes the patch observer. The raw compatibility method explicitly releases
ownership; callers must rebind that observer before destroying the mesh.

Bound parameter induction by an integer ceiling that cannot truncate positive
32-bit degree sequences, retaining floating endpoint tests and repeated additions.
Reject nonpositive degrees before patch access. This fixes the actual unbounded
induction/precondition issue; it does not suppress diagnostics or recompute coordinates.
Full object-bit comparisons of actual extracted headers and a rejected recomputation
control establish the measured scalar sequence boundary.

Classification: behavior-changing resource-lifetime and invalid-input defect repair.
Preserve formulas, UV/element order, historical center-ID timing and scientific
adaptation/acceptance/stopping. Caller roots/lifetime and general complete-mesh
validity remain subsequent work. See [evidence and closure inventory](../evidence/STAGE3_ESTIMATE_MESH.md).
