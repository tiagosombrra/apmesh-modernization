# M4 research — native Quadtree two-patch physical candidate meshes (2026-11-11)

**Status:** implementation submitted for exact-head native CI, **not yet
qualified**. This is an isolated research candidate; no production mesh or
scientifically approved 1993 mode is claimed.

## Original source and reuse, without numerical substitution

1. Execute the actual existing C++ 19-leaf `Quadtree` source through
   `quad_m4_native_tree_export`, preserving the original **53 UV vertices /
   42 QUAD** produced by the native exporter under both explicitly
   unapproved `vertex_mean` and `area_centroid` rules.
2. Reuse the already-qualified Python M5 UV research exterior algorithms
   without alteration. Their exact-rational Lawson candidate closes the UV
   unit-square domain with **36 TRI**, **69 UV vertices**, **20 QUAD/TRI
   interior edges** and 16 outer-domain edges. This is **not** the
   insertion/contraction procedure from the original 1993 article.
3. Execute the separate production-backed `quad_m4_pairwise_boundary_probe`
   to generate **actual indexed `.bp` model fixtures** and recheck two
   positive models with one shared curve, plus three negative incidences.
4. New `quad_m4_pairwise_physical_sampler` reads the verified native
   UV identities and calls **real** `PatchReader::ReaderFilePatches`
   and `PatchBezier::Parameterize / Qu / Qv` for **two distinct patches**
   per model. It returns only sample CSV. Its negative guards verify
   69 ordered/unique/finite UV coordinates, model patch type, **exactly
   seven curves with one shared patch-pair boundary**, derivative/Jacobian
   orientation and mode-specific curve direction.
5. New independent Python test `test_m4_pairwise_physical_candidates.py`
   compares **138 samples** (69 per patch) against an independently
   evaluated analytic cubic surface golden, then exports **one physical
   OBJ per patch** with the unchanged 42 QUAD + 36 TRI face IDs.

These tools operate on **two temporary analytic test surfaces**, with
shared cubic Bézier boundary and a shallow out-of-plane bend. One is
aligned in U/V, and the other reverses **both U and V** for its second
patch, preserving the positive chart orientation. These two modes are
not 1993 templates or a generalized arbitrary CAD importer.

## Independent seam and topology qualification

Each of four candidates (two chart models × two centroid rules) has
69 independent patch-local nodes and 78 local polygonal faces. An
independent test checks:

- Unmodified native UV vertex identities and **42 QUAD / 36 TRI**
  connectivity, with **120 positively oriented physical subtriangles**
  per patch (two for each QUAD, one for each TRI).
- Finite XYZ, Qu/Qv, cross-derivative magnitude, positive sample Jacobian
  and agreement with the explicit analytic Bézier polynomial.
- Exactly **four interpatch physical seam edges** with opposing directed
  face boundaries and **five pairwise-identical seam coordinate sites**.
  The virtual merged-node count is **133 = 69×2−5**. **No real node
  welding or shared element ownership is performed.**
- At least **seven** negative model/UV input rejections and **12**
  independent physical CSV/OBJ/cracked-boundary mutation rejections
  across the four output combinations.

The standalone candidate keeps its own `quad_m4_pairwise_physical_sampler`
C++ executable in the test target. It is not linked into the production
`ap_mesh` executable, `GeneratorAdaptive`, `Adapter` or any production
`SubMesh`.

## Gate and reproducibility

Register root CTest `quad.m4.pairwise_native_physical_candidates` and
publish an exact-commit, 14-day `quad-m4-pairwise-physical-<sha>` artifact
with two per-patch OBJ files for each of four combinations, source CSV,
physical CSV and a JSON manifest. Required: **83/83 root CTest**, **527/527
Python tooling**, seven M3 CLI invalid-mode negatives, standalone native
QUAD Linux GCC/Windows MSVC checks and strict frozen Eistute/Book TRI
comparison at the candidate head, with a second check after research merge.
No number is claimed passed until actual CI logs confirm it.

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure --no-tests=error
python3 -m unittest discover -s tests/tooling -p 'test_*.py'
```

## Explicit non-claims and next scientific blockers

This **does not** generate a conforming multi-patch mesh for Eistute, Book,
Ribbed Bracket, Pneu, the 32-patch Utah Teapot or an untracked Bolha model.
It **does not** share actual `NodeAdaptive` objects across patches, create a
global owning `SubMesh`, accept/roll back adaptive attempts, prove global
Jacobian bounds, implement historical 1993 Delaunay insertion and contour
contraction, approve either interior-point rule, or enable production QUAD
and all-QUAD. For this controlled fixture only, an upward world-normal
check is admissible; Eistute's strongly rotating sampled normals exclude
reuse of that check as a universal policy.

**Next gate after the merged-source CI passes:** export true per-patch
Bezier samples for all 4 Eistute / 28 Book / 13 Ribbed Bracket patches
with an explicitly sheet-aware incidence graph. Reject ambiguous high-valence
node welding; test boundary synchronization, chart orientation,
degenerate/near-degenerate patch regions, and lifecycle rollback before
claiming even a research full-model mesh. A separate `PatchHermite`
adapter is still required for Pneu.
