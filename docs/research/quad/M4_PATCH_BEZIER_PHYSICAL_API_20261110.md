# M4 preliminary — production PatchBezier geometric API probe (2026-11-10)

**Status: integrated isolated physical API probe; exact-head PR qualification passed.** The test calls
the *real* C++ production `PatchBezier` constructor, `Parameterize(u,v)`,
`Qu(u,v)` and `Qv(u,v)` in a standalone serial root CTest. Its 16
Bernstein control points describe a deterministic mathematical test patch,
**not** an actual imported Eistute/Book CAD model. No physical QUAD object
is allocated or published.

## Geometric independent reference

The degree-(3,3) control net uses
`P_ij=(i/3,j/3,k*a_i*a_j)`, with `a=(0,1/3,1/3,0)`,
for `k={0,+1.6,-1.6}`. Polynomial degree elevation independently implies:

```text
X(u,v)=(u,v,k*u*(1-u)*v*(1-v))
Qu=(1,0,k*(1-2u)*v*(1-v))
Qv=(0,1,k*u*(1-u)*(1-2v))
```

The test compares all coordinates and partial derivatives at 81 specified UV
samples per curvature (243 in total), evaluates positive oriented Jacobian,
checks the zero-height outer boundary and disallows non-finite/out-of-domain UV.
Two invalid geometric control nets are intentionally rejected: a collapsed
surface and a reversed u-axis. The rejection guard belongs **only** to this
research adapter; production `PatchBezier` does not validate those inputs.

## Ownership and noninterference

Four `CurveAdaptiveParametricBezier` instances are owned by
`unique_ptr` members and outlive the `PatchBezier` which borrows them.
This matches the existing observer lifetime contract and avoids using
the 16-point constructor whose fresh curves require explicit adoption.
Evaluations are serialized because the current `Parameterize`/`Qu`/`Qv`
mutate internal matrices. No calls alter application code, TRI control flags,
curve sampling, mesh publication, geometry loaders or scientific presets.

This is a **bounded physical API precondition** only. The actual 69-vertex
C++ QUAD + M5 research TRI interface has not been evaluated using this patch;
neither actual curved model boundaries nor patch-to-patch shared controls
have been admitted. The historical 1993 Delaunay insertion, contour contraction
and centroid policy still require separate scientific qualification.

## Required execution

```bash
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure --no-tests=error
```

The named new test is `quad.patch_bezier.physical_api`. [PR #203](https://github.com/tiagosombrra/apmesh-modernization/pull/203) integrated at merge `6dcffdc0a96a69bd3bd0a1ebc9b434ea607eba20`, after exact feature `956127fdaef8535cb8ae995cae14f50099b306b5` passed four-job [CI #42990407284](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42990407284). An initial failure [#42944985482](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42944985482) was the stale root CMake SHA-256 in `docs/architecture/source_inventory.json`; the one-hash-only fix was validated and no numerical acceptance threshold was changed. Post-merge CI [#42991513759](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42991513759) was in progress when this documentation was prepared.

The bounded next gate is [native hybrid geometry on a built-in model](M4_REAL_MODEL_HYBRID_DESIGN_20261111.md). This adds one
research-only test to the previously recorded 78 root CTest cases, so a
qualifying all-pass run should report 79 cases; all 527 Python controls,
seven CLI denials and Eistute/Book strict TRI reference equivalence remain
mandatory. No passing outcome should be claimed until the exact-head CI is read.

## Next gate

Connect the already qualified native QUAD/M5 TRI 69-UV-vertex mesh to an actual
owned or borrowed `PatchBezier` instance, preserve the single seam's IDs
through physical lifting and verify face normals/orientation and CAD boundary
agreement independently. Then repeat with **loaded actual curved geometry**;
controlled control grids are insufficient for the physical model criterion.
