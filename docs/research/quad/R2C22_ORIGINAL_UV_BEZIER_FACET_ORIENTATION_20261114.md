# R2c-22 — Original source UV / Bezier differential facet orientation

Status: candidate, exact-head native CI has not yet been measured.
R2c-21 on source 5ed7fdd (Actions #43532150635) completed all four hosted jobs successfully,
with 32/32 original Eistute+Book indexed detached charts and 7/7 negative controls.

Research-only native test stage now exports the real physical element's per-vertex UV,
the original PatchBezier::Parameterize() XYZ, and the native Qu x Qv differential
normal at each original TRI / triangulated QUAD facet UV centroid.
The independent Python checker cross-links OBJ physical indices, source model identities,
UV signed triangle area, physical XYZ, source Bezier point samples, facet centroid,
strictly positive physical facet vs original differential-normal dot, complete
patch and facet coverage, and five synthetic negative controls.

These originals are detached candidate MeshAdaptive patches from the research test
Quadtree/AFT, not production GeneratorAdaptive::AdaptDomain accepted meshes.
Qu and Qv values are evaluated by original source C++ methods: Python independently
verifies their relation to the indexed physical mesh; it does NOT independently
reconstruct the Bezier control net, prove continuous Jacobian signs, reject global
self-intersections, or authorize model-global sheet pairing/welding.
Eistute valence 4 and Book valence 28 still need model-SHA-bound advisor decisions.

Reproduction: python3 tools/verify_r2c22_original_patch_uv_bezier_orientation.py
  --directory build/local-serial/r2c10_original_detached_meshes
  --output build/local-serial/r2c22_original_uv_bezier_orientation

Do not merge or enable quad_uv before native exact-source gates and scientific review.
