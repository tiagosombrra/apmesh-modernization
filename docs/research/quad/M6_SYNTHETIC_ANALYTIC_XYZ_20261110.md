# M6 — Synthetic analytic UV→XYZ embedding on real C++ QUAD output (2026-11-10)

**Status: bounded research geometry test.** This is not a curved physical APMesh
model, historical Delaunay point insertion, 1993 contour contraction, a
production hybrid mode, or a completed all-QUAD extension.

## What is actually executed

The existing 19-leaf C++ quadtree writes 42 four-node UV QUAD (53 source
vertices). The already qualified M5 Python exterior algorithm adds 36 locally
Delaunay UV TRI, producing a conforming 69-vertex, 20-edge shared seam mixed disk.
This test consumes its actual native-origin OBJ and immutable OBJ/manifest
provenance; it does not regenerate or substitute the C++ interior.

For a reproducible geometric bridge, vertices are embedded on the **synthetic
analytic graph**:

\[
\mathbf{X}(u,v;k)=(u,v,k\,u(1-u)v(1-v)), \quad k\in\{0,1.6,-1.6\}.
\]

No APMesh CAD/curved-model adapter API is invoked. The domain boundary remains
z=0, and the signed analytic tangent normal is proportional to
\((-h_u,-h_v,1)\). Every face is audited through its oriented triangular
decomposition (84 from the 42 QUAD + 36 from the 36 TRI, 120 subtriangles).
Their cross products must have positive analytic tangent-normal projection,
normal alignment >0.98 and nonzero projected area. The map must preserve
the 69 UV vertex IDs, the 42/36 element topology and the **20-edge QUAD/TRI seam**
exactly. Edge-midpoint height deviation from the analytic surface is reported
as a **faceting approximation error**, not falsely claimed to be zero.

Eight malformed controls reject invalid curvature, nonfinite coordinates,
nonzero original UV height, coordinate collision, reversed TRI winding and
a reversed spatial map. Both explicitly selected, still-unapproved vertex
mean and area-centroid policies run, and the two curved 3D OBJ witnesses are
uploaded as a bounded GitHub Actions artifact.

## CI and local reproduction

\`\`\`bash
cmake -S tests/quad -B build/quad-ci-linux -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAP_MESH_QUAD_WITH_TREE=ON
cmake --build build/quad-ci-linux --parallel 2
ctest --test-dir build/quad-ci-linux --output-on-failure --no-tests=error
# Inspect build/quad-ci-linux/real_tree_visual/analytic_surface_research_* files.
\`\`\`

The native QUAD CTest count is expected to increase from 12 to 13 on Linux
GCC and Windows MSVC. The root TRI 78, Python tooling 527, CLI seven
negative cases and Eistute/Book 5/4 strict parity remain mandatory.

## Open scientific gates

1. Reproduce the 1993 exterior Delaunay insertion and curve-aware boundary
   contraction from primary sources, **with adviser approval**; the current
   Lawson research mesh is not historical reproduction.
2. Verify the actual APMesh model boundary curves and UV→XYZ / normal APIs,
   then test curved **physical** QUAD/TRI ownership, conformity and quality
   on a model with an independent golden geometry reference.
3. Decide the numerical historical centroid with Bento/Creto and explicitly
   record allowable concavity, degeneracy and tolerances.
4. Only after historical hybrid validation, develop a selectable all-QUAD
   boundary extension with distinct scientific tests.

Modernization \`main\` and the existing serial TRI behavior remain unchanged.

## Qualification receipt and actual APMesh geometry entrypoints

- Reviewed research PR [#202](https://github.com/tiagosombrra/apmesh-modernization/pull/202), exact candidate `e0e0d86ca4bad419425337ea7676b1c2a9ec3490`, merge `b48526ab22f7190679cd37c61a12005687666c5f` with matching tested tree. Main unchanged.
- [CI #42941827778](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42941827778) **SUCCESS**: GCC/MSVC QUAD 13/13 each, TRI 78, Python 527, CLI denials 7 and Eistute/Book nine states with exact byte-OBJ/acceptance/boundary parity. Native artifact #13821515576 provided XYZ witness OBJs and manifest. Post-merge [#42942777929](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42942777929) was `in_progress` when checkpointed; verify its exact merged SHA.
- In the actual application geometry, `include/data/patch/patch_bezier.h` exposes **`PatchBezier::Parameterize(double u,double v)`** returning a `PointAdaptive`, plus `Qu(u,v)`/`Qv(u,v)` and higher derivatives. The next isolated research prototype must obtain a **live owned/borrowed patch reference**, preserve patch and curve ownership contracts, independently check XYZ/normal and physical shared boundary identity, and reject invalid domain/degenerate Jacobian before any physical QUAD publication.
- **No real PatchBezier was called in this PR**. The analytic surface above is purely a reproducible geometric intermediate. The 1993 historical Delaunay/contour contraction, centroid rule and all-QUAD remain unapproved/not implemented.
