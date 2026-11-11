# M4 next gate — native QUAD/TRI to a real APMesh Bezier model (2026-11-11)

**Status: experimental built-in model implementation delivered through [PR #204](https://github.com/tiagosombrra/apmesh-modernization/pull/204); full physical elements and CAD admission remain pending.** This is the bounded next
engineering experiment after the merged M4 physical API gate. Scientific
approval of the 1993 historical exterior method and centroid remains open.

## Verified inputs and identified production API

- The native C++ 19-leaf Quadtree fixture emits exactly **42 UV QUAD**, and
  the M5 research-only constrained local Lawson stage emits **36 exterior TRI**:
  **69 UV vertices, 20 shared QUAD/TRI seam edges and 16 outer edges**.
  The two explicitly unapproved centroid witnesses must stay separate.
- `Models3d::ModelCurvaBezier(Geometry*)` in
  `src/input_output/models_3d.cpp` creates an actual
  production-owned curved `PatchBezier` with four Geometry-owned curves.
  This is an embedded example model with fixed control points, **not an external
  imported CAD or Eistute/Book model**.
- `Geometry::GetPatch(0)` provides a borrowed `Patch*`, which must be
  dynamically checked as `PatchBezier*` and retained only while the owning
  `Geometry` lives. Its `Parameterize`, `Qu` and `Qv` APIs mutate
  scratch matrices; use serial evaluation only.
- The root serial `quad.patch_bezier.physical_api` CTest, integrated in
  PR #203, already checks the actual `PatchBezier` API against an independently
  derived 16-control-point polynomial witness. It does not consume the
  69-vertex mesh or use `Models3d`.

## Minimal implementation proposal

1. Build a research-only root C++ exporter using the existing
   `tests/quad/tree_visual_export.cpp`, `research/quad/quadtree_quad.cpp`,
   `research/quad/uv_mesh.cpp` and experimental point-selector target, linked
   to `ap_mesh_engine` only in a serial test configuration. Do not
   duplicate or substitute its real C++ tree output.
2. Invoke the preexisting independent Python exterior scripts on the actual
   generated C++ artifact to materialize the two identical-topology M5 local
   Lawson UV meshes. Verify the source OBJ and its manifest before lifting.
3. In a separate research-only C++ executable, instantiate
   `Geometry` and `Models3d::ModelCurvaBezier`; borrow its `PatchBezier`,
   validate every finite UV in `[0,1]^2`, and obtain XYZ/Qu/Qv at each
   existing vertex ID. Export mixed 3D OBJ preserving all original face
   indices and QUAD/TRI group membership. Never publish a production mesh.
4. An independent Python auditor reconstructs the loaded model's 16 pinned
   source control points, evaluates the Bernstein bicubic basis and both
   tangents independently, then checks XYZ error, tangent-normal orientation,
   nonzero subtriangle physical area, faceting error, **120** oriented
   subtriangles, exactly **20** unchanged interface edges, **16** outer edges
   on the four model boundary curves, and unchanged 69/42/36 inventory.
5. Require malformed controls: nonfinite/out-of-range coordinates, source OBJ
   checksum/provenance mismatch, duplicate/missing vertices, inverted face,
   collapsed normal/Jacobian, broken seam and incorrect expected control net.
   Preserve the two numerical centroid hypotheses without choosing one.

## Validation / admission

- New tests must be opt-in research/serial. Mainline `ap_mesh`, `src/`,
  `include/`, production configuration, existing TRI geometry/outputs and
  scientific acceptance/rollback remain untouched.
- Qualify the full required root CTest (expected **80** after exactly one
  addition), **527** Python controls, seven CLI negatives, native GCC/MSVC
  QUAD **13/13** each, strict frozen five Eistute/four Book scientific
  states and a sampled physical audit with independent reference.
- A passing example-model lift is **not** validation of arbitrary imported
  curved geometry, nonconvex CAD patches, multipatch shared-curve
  synchronization or 1993 Delaunay plus contour contraction.
- Integration only by reviewed PR into `quad-templates`, after the
  exact-head qualification and independent post-merge check. No scientific
  deployment and no default QUAD selector.

## Further scientific blockers

Historic T1–T6 interior-point coordinates and admissible degeneracy/tolerances,
actual 1993 Delaunay insertion / contour contraction, CAD boundary fidelity,
four-node physical-element lifecycle, multipatch shared-curve sync, global
adaptation acceptance and the separate all-QUAD mode remain unapproved or pending.
