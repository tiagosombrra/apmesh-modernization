# M4 — Native hybrid research geometry on the built-in curved APMesh model (2026-11-11)

**Status: integrated and feature CI-qualified research experiment (PR #204).** This is a
bounded research implementation. It does not enable production QUAD, adopt a
historical interior-point formula, reproduce the original 1993 Delaunay and
contour-contraction procedure, or qualify imported CAD/multipatch boundaries.

## Source of the geometry and connectivity

1. Root research target `quad_m4_native_tree_export` reuses the existing
   `tree_visual_export.cpp`, `TreeFixture` and the C++ production Quadtree
   implementation linked through `ap_mesh_engine`. It produces both native
   42-QUAD/53-vertex unmodified source OBJs and source leaf classification.
2. The existing `test_m5_exterior_interface.py` consumes that C++ output and
   generates the bounded 60-TRI exterior fan interface.
3. The existing `test_m5_constrained_delaunay.py` independently builds the
   36 experimental locally Delaunay triangles using exact-rational local
   Lawson flips. Both candidate centroid modes retain the 69-UV-vertex mixed
   mesh and one 20-edge QUAD/TRI seam.
4. New `quad_m4_physical_model_lift` parses only the admitted M5 research OBJ
   group order and vertex/face inventory, rejects invalid UV and signed area,
   instantiates actual `Models3d::ModelCurvaBezier(&geometry)`, borrows its
   `PatchBezier`, and evaluates `Parameterize`, `Qu`, `Qv` serially.
   It writes one 3D OBJ and one typed derivative sample CSV per candidate mode,
   preserving all 69 IDs, all 42 native four-node QUAD and all 36 research TRI
   faces. It creates no new physical `ElementAdaptive` or `SubMesh`.

## Independent acceptance oracle and deliberately negative inputs

`test_m4_real_model_hybrid.py` uses 16 **explicitly pinned production-model
control points** and an independent bicubic Bernstein basis/derivatives;
it does not trust `PatchBezier` or the emitted differential CSV to compute its
expected coordinates. It checks exact source provenance using pinned native
C++-produced file SHA-256 in the M5 manifest, unchanged face indices and
orientation, 69 unique physical vertex identities, 120 oriented subtriangles,
tangent/Jacobian orientation and positivity, all 20 mixed seam edges, all 16
outer edges attached to model parametric boundaries, normal alignment, maximum
edge-midpoint faceting error and boundary-chord approximation error.

Each of the two explicitly **unapproved** centroid alternatives must pass 11
independent negative controls: wrong mapped XYZ, inverted TRI, corrupt
connectivity, false derivative, changed golden control net, bad source checksum,
out-of-domain/nonfinite UV, out-of-bounds OBJ face ID, reversed QUAD and invalid
source group identity. This tests rejection, not an alleged production safety
policy.

## Exact admission commands

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure --no-tests=error
python3 -m unittest discover -s tests/tooling -p 'test_*.py'
python3 tests/quad/test_m3_dispatch.py build/local-serial/bin/ap_mesh
```

The new root CTest is `quad.m4.real_builtin_model_hybrid`. A qualifying serial
profile should pass **80/80 CTest**, **527/527 Python tooling**, the seven CLI
negative controls, native standalone **13/13** GCC and MSVC QUAD CTest and the
frozen Eistute 5/Book 4 strict OBJ/acceptance/boundary equivalence. The existing
`quad-research-validation.yml` retains a bounded 14-day artifact containing
both physical OBJ witnesses, the derivative CSVs and their manifest.

The expected result is a **research physical OBJ on a single built-in curved
Bezier example**, not verified behavior on an imported CAD surface or arbitrary
physical boundary. The next scientific gates remain owned four-node physical
elements, historical 1993 contour contraction/point insertion, approved
interior-point policy, shared multipatch curves, adaptation reentry and the
separate selectable all-QUAD extension. `main` and the default TRI pipeline
must remain unchanged.

## Exact feature qualification and integration

- [PR #204](https://github.com/tiagosombrra/apmesh-modernization/pull/204) merged on scientific `quad-templates` as `da61e09d157698210faa674bfa911332f574c7ad` after exact feature `ac4eb3b464297962d7bc68376b97112c4523a8b5` passed all four [Actions #42993951256](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42993951256) jobs.
- Root 80/80 CTest, Python 527/527, CLI negatives 7/7, independent research QUAD GCC/MSVC suites and strict Eistute/Book frozen TRI equivalence passed. Both centroid witnesses produced 3D OBJ/CSV research artifacts; the bounded [artifact #13842634340](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42993951256/artifacts/13842634340) was uploaded successfully. No claimed actual imported CAD or physical `ElementAdaptive`.
- Post-merge exact-commit [Actions #42994999161](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42994999161) was in progress at this checkpoint; see [evidence receipt](evidence/M4_BUILTIN_MODEL_PHYSICAL_HYBRID_20261111.json) and canonical [STATE.md](STATE.md) for later final status.
