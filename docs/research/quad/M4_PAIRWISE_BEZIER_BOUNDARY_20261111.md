# M4 research — production Bezier pairwise boundary admission (2026-11-11)

**Status:** feature branch candidate; native exact-head CI and code review pending.
**Classification:** engineering-only research probe. This is not a model-wide QUAD/TRI
mesh, historical 1993 hybrid implementation, production element publication, or a
general patch welding algorithm.

## Actual production interface

`tests/quad/patch_reader_pairwise_probe.cpp` writes five indexed bicubic `.bp`
fixtures into a build-local directory and loads each through the production
`PatchReader::ReaderFilePatches(Geometry*, filename)`. The loader and Geometry
own the patches and curves; this research executable does not retain pointers
after their owner is destroyed.

Two positive cases have two actual `PatchBezier` instances, seven Geometry-owned
boundary curves, **exactly one two-owner seam** and six one-owner curves:

- **Aligned:** the first patch's right UV side and the second patch's left side
  share the same CurveAdaptive identity and a common increasing-v direction.
- **Reparameterized:** the second patch reverses **both** local U and V,
  preserving positive physical orientation, while its right UV boundary shares
  the first patch's right boundary in the **opposite** parameter direction.
  The loader's `IsCurveReversed` observation must preserve this incidence.

Each admitted case checks 9x9 points on both patches against independent
analytic XYZ, Qu and Qv polynomials and validates 17 mapped seam positions
and tangent directions. No world-positive normal policy is inferred for real
curved CAD: the fixed +Z golden applies only to this explicit analytic fixture.

Three mandatory rejected cases:

1. One displaced interior seam control point breaks real shared-curve identity.
2. Reversing only V leaves a coincident curve but reverses the patch Jacobian;
   matching coordinates alone must not grant geometric admission.
3. A third sheet shares the curve, producing a valence >=3 junction. A
   two-owner admission must fail rather than silently weld all sheets.

The test deliberately does not create `NodeAdaptive`, `SubMesh`,
`QuadrilateralAdaptive`, OBJ meshes or global identities. The high-valence
cases in Eistute (4) and Book (28) must have an explicit per-sheet policy.
This probe does **not** alter `src/`, `include/`, `main`, TRI defaults or
scientific oracle baselines.

## Qualification

New root serial CTest: `quad.m4.pairwise_bezier_boundary`. Expect the existing
81 root tests plus this test (82 total), 527 tooling Python tests, seven CLI
invalid-mode rejections, native Linux GCC/Windows MSVC QUAD controls and strict
Eistute/Book frozen TRI equivalence on the exact feature head. A PR cannot be
merged while any required gate is unmeasured or failing.

The GitHub-hosted native CTest is executable evidence, not a local sanitizer,
MSVC checked-CRT or complete scientific multi-patch qualification. The research
output files are build-local and are not input model assets.

## Next bounded experiment

After exact-head and post-merge CI pass, export per-patch QUAD/TRI candidate
UV-to-XYZ witnesses from the real C++ source Quadtree for the two-patch
surface, independently compare seam discretization and global shared-node
identity, then test explicitly chosen sheet-aware behavior on Eistute's
4-way and Book's 28-way curve junctions. A distinct Hermite adapter remains
necessary for `ModelPneu`.
